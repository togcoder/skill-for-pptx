#!/usr/bin/env python3
"""Compound motion engine for existing PowerPoint objects (T023 / T024).

Four layers:

1. Keyframe tracks -> native effects.  A track animates one existing object
   through keyframes (position, scale, rotation, opacity, color, visibility).
   Each changed property between keyframes becomes a native PowerPoint effect
   (custom motion path, Grow/Shrink, Spin, Transparency, Color, entrance/exit)
   with an exact delay.  When ``poly_path=True`` or intermediate keyframes mark
   ``via=True``, consecutive position segments compile into a single
   multi-segment ``p:animMotion`` path.  State is carried across clicks.

2. Group-aware virtual rigging & secondary follow-through (T024).  Shapes that
   visually contain separate text labels, icons, or badges automatically carry
   those followers along in unison (translating, scaling, rotating, dimming and
   hiding together) without mutating the slide's ``p:spTree`` group hierarchy.
   When ``follow_through_ms > 0`` is specified, attached followers lag behind
   their carrier by staggered millisecond offsets (overlapping action / inertia).

3. Choreography recipes -> tracks.  spotlight, release, assemble, disperse,
   cycle, swap, travel, zoom-focus, orbit, orbit-3d, wave, explode-layers and
   cascade-flow use the objects' authored geometry.  Optional ``auto_avoid=True``
   bends trajectories into cubic Bezier arcs when a straight path would collide
   with an intermediate obstacle.

4. Simulation & continuous collision checks.  Evaluates any effect list at any
   time ``t``; checks both stable end-states and mid-flight trajectories.
"""
import copy
import math

try:
    from . import pptx_animator as anim
except ImportError:
    import pptx_animator as anim

PROPS=("pos","scale","rot","opacity","color","visible")
ENTER_DEFAULT=("fade",400)
EXIT_DEFAULT=("fade-out",400)


# ---------------------------------------------------------------------------
# Object state & virtual rigging


def authored(obj):
    g=obj["geometry"]
    return {"cx":g["x"]+g["w"]/2,"cy":g["y"]+g["h"]/2,"w":g["w"],"h":g["h"]}


def text_block(obj,aspect=16/9):
    """Estimated box (x0,y0,x1,y1) of the visible text lines inside a text
    shape, as slide fractions. Assumes a 7.5 in slide height, default insets
    and an average glyph width; returns the shape box when the vertical
    anchor is unknown (placeholders inherit it)."""
    g=obj.get("geometry")
    if not g:
        return None
    full=(g["x"],g["y"],g["x"]+g["w"],g["y"]+g["h"])
    if obj.get("filled"):
        return full  # a filled shape is seen as a whole box
    anchor=obj.get("text_anchor") or (None if obj.get("placeholder") else "t")
    paras=[p.get("text","") for p in (obj.get("paragraphs") or [])] or (obj.get("text") or "").split("\n")
    if anchor not in ("t","ctr","b") or not any(paras):
        return full
    size=float(obj.get("max_font_pt") or 18)
    hp,wp=540.0,540.0*aspect
    width=max(size,g["w"]*wp-14.4)
    lines=sum(max(1,math.ceil(len(t)*size*0.55/width)) for t in paras)
    block=min(g["h"],(lines*size*1.2)/hp)
    inset=3.6/hp
    y0={"t":g["y"]+inset,"ctr":g["y"]+(g["h"]-block)/2,"b":g["y"]+g["h"]-inset-block}[anchor]
    y0=max(g["y"],min(y0,g["y"]+g["h"]-block))
    return (g["x"],y0,g["x"]+g["w"],y0+block)


def fresh_state(visible=True):
    return {"dx":0.0,"dy":0.0,"scale":1.0,"rot":0.0,"opacity":1.0,"visible":visible,"alpha":1.0,"text_frac":1.0,
            "color":None}


def initial_states(objects,effect_groups):
    """Object states before the first click: an object whose first visibility
    change is an entrance starts hidden."""
    first={}
    for group in effect_groups:
        for eff in group:
            if eff.get("paragraph") is not None:
                continue
            cls="entr" if eff["preset"]=="counter" else anim.PRESETS.get(eff["preset"],("",))[0]
            if cls in ("entr","exit"):
                first.setdefault(eff["spid"],cls)
    return {o["id"]:fresh_state(first.get(o["id"])!="entr") for o in objects}


def _area(o):
    g=o.get("geometry")
    return g["w"]*g["h"] if g else 0.0


def _contains_center(outer,inner,margin=0.005):
    g=outer.get("geometry")
    ig=inner.get("geometry")
    if not g or not ig:
        return False
    cx,cy=ig["x"]+ig["w"]/2,ig["y"]+ig["h"]/2
    return (g["x"]-margin<=cx<=g["x"]+g["w"]+margin
            and g["y"]-margin<=cy<=g["y"]+g["h"]+margin)


def detect_virtual_rigs(objects,transitive=True):
    """Return {carrier_id: [follower_obj, ...]} for separate labels/icons/badges
    sitting inside a larger carrier shape on the same slide.

    When ``transitive=True`` (default), if carrier A contains sub-panel B which
    contains label C, A's rig list includes both B and C (sorted by area
    descending) so moving A carries the entire multi-part assembly.
    """
    if not objects:
        return {}
    with_geom=[o for o in objects if o.get("geometry") and not (o.get("name") or "").startswith(("__counter_", "!!"))]
    carriers=[o for o in with_geom if o.get("kind")=="shape" and 0.0015<_area(o)<0.22]
    direct={}
    for child in with_geom:
        if child.get("kind")=="chart":
            continue
        ca=_area(child)
        enclosing=[c for c in carriers if c["id"]!=child["id"]
                   and ca<0.88*_area(c) and _contains_center(c,child)]
        if enclosing:
            best=min(enclosing,key=_area)
            direct.setdefault(best["id"],[]).append(child)
    if not transitive:
        return direct
    rigs={}
    for cid in list(direct):
        collected=[]
        queue=list(direct.get(cid,[]))
        seen={cid}
        while queue:
            cur=queue.pop(0)
            if cur["id"] in seen:
                continue
            seen.add(cur["id"])
            collected.append(cur)
            queue.extend(direct.get(cur["id"],[]))
        collected.sort(key=_area,reverse=True)
        rigs[cid]=collected
    return rigs


def _rig_pairs(objects):
    """Set of (id1, id2) pairs belonging to the same virtual rig (carrier + followers)."""
    rigs=detect_virtual_rigs(objects,transitive=True)
    pairs=set()
    for cid,followers in rigs.items():
        fids=[f["id"] for f in followers]
        for fid in fids:
            pairs.add((cid,fid))
            pairs.add((fid,cid))
            for other in fids:
                if fid!=other:
                    pairs.add((fid,other))
    return pairs


# ---------------------------------------------------------------------------
# Scheduling + simulation


def schedule(effects):
    """[(start_ms, end_ms, effect)] for one click group (block-relative delays)."""
    blocks,_=anim.plan_blocks(effects)
    out=[]
    for begin,effs in blocks:
        for e in effs:
            start=begin+e.get("delay_ms",0)
            dur=e["duration_ms"] if e["preset"]=="counter" else anim.effective_duration(e)
            out.append((start,start+dur,e))
    return out


def group_duration(effects):
    return max((end for _,end,_ in schedule(effects)),default=0)


def _ease(p,eff):
    if eff.get("auto_reverse"):
        p=1-abs(2*p-1)
    rep=eff.get("repeat")
    if isinstance(rep,(int,float)) and rep>1 and p<1.0:
        p=(p*rep)%1.0
    a=eff.get("accel",0.5 if eff["preset"]=="path" else 0)
    d=eff.get("decel",0.5 if eff["preset"]=="path" else 0)
    if a or d:
        q=p*p*(3-2*p)
    else:
        q=p
    if eff.get("bounce_end") and q>0.75:
        b=float(eff["bounce_end"])
        u=(q-0.75)/0.25
        q=1.0-abs(math.sin(u*math.pi*2))*(1-u)*0.18*b
    return q


def _bezier(p0,c1,c2,p1,t):
    u=1-t
    return (u**3*p0[0]+3*u*u*t*c1[0]+3*u*t*t*c2[0]+t**3*p1[0],
            u**3*p0[1]+3*u*u*t*c1[1]+3*u*t*t*c2[1]+t**3*p1[1])


def path_polyline(eff):
    """Anchored offsets along the path, densely sampled."""
    if eff.get("anchored"):
        segs=eff["anchored"]
        pts=[(segs[0]["x"],segs[0]["y"])]
        for seg in segs[1:]:
            p0=pts[-1]
            p1=(seg["x"],seg["y"])
            if "c1" in seg:
                c1=(seg["c1"]["x"],seg["c1"]["y"])
                c2=(seg["c2"]["x"],seg["c2"]["y"])
                pts.extend(_bezier(p0,c1,c2,p1,i/16) for i in range(1,17))
            else:
                pts.append(p1)
        return pts,True
    pts=eff["points"]
    return [(p["x"]-pts[0]["x"],p["y"]-pts[0]["y"]) for p in pts],False


def _along(pts,p):
    lengths=[math.dist(a,b) for a,b in zip(pts,pts[1:])]
    total=sum(lengths)
    if total==0:
        return pts[-1]
    target=max(0.0,min(1.0,p))*total
    for (a,b),length in zip(zip(pts,pts[1:]),lengths):
        if target<=length and length>0:
            f=target/length
            return (a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f)
        target-=length
    return pts[-1]


def apply_effect(state,eff,p,base):
    """Mutate ``state`` for effect progress p (0..1). ``base`` is the state
    captured when the effect started."""
    preset=eff["preset"]
    if preset=="counter":
        state["visible"]=True
        return
    cls=anim.PRESETS[preset][0]
    if eff.get("paragraph") is not None or eff.get("chart") is not None:
        if cls=="entr" and eff.get("chart") is not None:
            state["visible"]=True
        return
    q=_ease(p,eff)
    if cls=="entr" and eff.get("iterate"):
        # Typewriter / word-by-word: units arrive one after another.
        state["visible"]=True
        state["alpha"]=1.0
        state["text_frac"]=1.0 if p>=1 else max(0.0,p)
        return
    if cls=="entr":
        state["visible"]=True
        state["alpha"]=1.0 if preset in ("appear",) else min(1.0,p if p>0 else 0.0)
        if preset=="float-in":
            state["dy"]=base["dy"]+0.1*(1-q)
        if preset=="zoom":
            state["scale"]=base["scale"]*max(0.01,q)
        if p>=1:
            state["alpha"]=1.0
            if preset=="float-in":
                state["dy"]=base["dy"]
            if preset=="zoom":
                state["scale"]=base["scale"]
    elif cls=="exit":
        state["alpha"]=1-p if preset!="disappear" else 0.0
        if p>=1 or preset=="disappear":
            state["visible"]=False
            state["alpha"]=1.0
    elif cls=="path" and preset in anim.LIBRARY:
        # PowerPoint preset paths are relative to where the object is now.
        pts,_=path_polyline({"anchored":parse_path(anim.LIBRARY[preset]["template"].find(".//p:animMotion",anim.NS).get("path"))})
        x,y=_along(pts,q)
        state["dx"],state["dy"]=base["dx"]+x,base["dy"]+y
    elif preset=="path":
        pts,anchored=path_polyline(eff)
        x,y=_along(pts,q)
        if anchored:
            state["dx"],state["dy"]=x,y
        else:
            state["dx"],state["dy"]=base["dx"]+x,base["dy"]+y
    elif preset=="grow":
        state["scale"]=base["scale"]*(1+(eff["ratio"]-1)*q)
    elif preset=="pulse":
        tri=1-abs(2*p-1)
        state["scale"]=base["scale"]*(1+(eff.get("scale",1.08)-1)*tri)
    elif preset=="spin":
        state["rot"]=base["rot"]+eff.get("by_deg",360)*q
    elif preset=="teeter":
        deg=eff.get("by_deg",2.0)
        state["rot"]=base["rot"]+deg*math.sin(p*math.pi*4)*(1 if p<1 else 0)
    elif preset=="color":
        if p>=0.5:
            state["color"]=anim.norm_hex(eff.get("color","#E06C4F"))
    elif preset=="dim":
        target=eff.get("opacity",0.35)
        state["opacity"]=base["opacity"]+(target-base["opacity"])*min(1.0,p*4)


def loop_progress(eff,elapsed):
    """Progress of a looping effect; at rest (0) once it is over or at t=inf."""
    loop=eff["loop"]
    dur=max(1,eff["duration_ms"])
    cycle=anim.loop_cycle(eff)
    repeat=loop.get("repeat","indefinite")
    if elapsed==float("inf") or (type(repeat) is int and elapsed>=repeat*cycle):
        return 0.0 if loop.get("auto_reverse") or repeat in ("indefinite","until-next-click") else 1.0
    phase=(elapsed%cycle)/dur
    return 2-phase if phase>1 else phase


def state_at(states,effects,t):
    """States after running one click group's effects up to time t.
    Ambient loops are shown moving inside t and at rest at t=inf."""
    out={k:dict(v) for k,v in states.items()}
    for start,end,eff in sorted(schedule(effects),key=lambda x:x[0]):
        if t<start or eff["spid"] not in out:
            continue
        dur=max(1,end-start)
        if eff.get("loop"):
            p=loop_progress(eff,t-start)
            st=out[eff["spid"]]
            base=dict(st)
            if eff["preset"]=="spin" and not eff["loop"].get("auto_reverse"):
                base_eff=dict(eff)
                apply_effect(st,base_eff,p,base)
            else:
                apply_effect(st,eff,p,base)
            continue
        p=1.0 if t>=end else (t-start)/dur
        st=out[eff["spid"]]
        base=dict(st)
        apply_effect(st,eff,p,base)
    return out


def advance(states,effects):
    return state_at(states,effects,float("inf"))


# ---------------------------------------------------------------------------
# Keyframe tracks -> effects


def _resolve_point(kf,obj,objects_by_token,current):
    """Return anchored offset (dx,dy) for a keyframe's position, or None."""
    a=authored(obj)
    if "to" in kf:
        other=objects_by_token.get(kf["to"])
        if other is None:
            raise ValueError(f"keyframe target {kf['to']!r} not found")
        b=authored(other)
        return (b["cx"]-a["cx"]+kf.get("dx",0.0),b["cy"]-a["cy"]+kf.get("dy",0.0))
    if "x" in kf or "y" in kf:
        return (kf.get("x",a["cx"]+current[0])-a["cx"],kf.get("y",a["cy"]+current[1])-a["cy"])
    if "dx" in kf or "dy" in kf:
        return (kf.get("dx",current[0]),kf.get("dy",current[1]))
    return None


def _arc_controls(p0,p1,curve):
    """Cubic controls bulging by ``curve`` × chord length; positive bulges to the
    left of the travel direction as seen on screen (rightward motion arcs up)."""
    mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    vx,vy=p1[0]-p0[0],p1[1]-p0[1]
    nx,ny=vy,-vx  # screen-left of the travel direction (slide y grows downward)
    bx,by=mx+nx*curve,my+ny*curve
    c1=(p0[0]+(bx-p0[0])*2/3,p0[1]+(by-p0[1])*2/3)
    c2=(p1[0]+(bx-p1[0])*2/3,p1[1]+(by-p1[1])*2/3)
    return c1,c2


EASE={"linear":(0,0),"smooth":(0.5,0.5),"in":(0.6,0),"out":(0,0.6)}
# T029: design-system easing roles fitted to PowerPoint accel/decel (motion_tokens.py).
try:
    from . import motion_tokens as _mt
except ImportError:
    import motion_tokens as _mt
EASE.update({role:_mt.ease(role) for role in _mt.ROLES})


def compile_track(track,obj,objects_by_token,state,beat_id):
    """Compile one track into effects (delays relative to the beat start).

    state: the object's state at the beat start; it is not mutated here.
    Keyframe keys: t (ms, required), position via x/y | dx/dy | to (+curve,
    +controls, +via), scale, rotate (deg, absolute vs authored), opacity,
    color (#RRGGBB), visible (+enter/exit preset, enter_ms), ease
    (linear|smooth|in|out), repeat, auto_reverse, bounce_end.
    When ``track.get("poly_path")`` is True or an intermediate keyframe sets
    ``via=True``, consecutive position segments merge into one multi-segment
    ``p:animMotion`` path.
    """
    kfs=sorted(track["keyframes"],key=lambda k:k["t"])
    if not kfs:
        raise ValueError(f"track for {obj['name']!r} has no keyframes")
    if any(type(k.get("t")) not in (int,float) or k["t"]<0 for k in kfs):
        raise ValueError(f"track for {obj['name']!r}: keyframe t must be >=0")
    effects=[]
    spid=obj["id"]
    if not obj.get("geometry"):
        raise ValueError(f"{obj['name']!r} has no resolvable geometry for motion")
    cur_pos=(state["dx"],state["dy"])
    pos_time=None
    cur_scale=state["scale"]
    scale_time=None
    cur_rot=state["rot"]
    rot_time=None
    visible=state["visible"]
    cur_opacity=state["opacity"]
    cur_color=state.get("color")
    poly_mode=bool(track.get("poly_path"))
    pending_poly=None
    n=[0]

    def eff(preset,start,dur,**kw):
        n[0]+=1
        e={"preset":preset,"spid":spid,"trigger":"with","delay_ms":int(round(start)),
           "duration_ms":int(round(max(0,dur))),"beat":f"{beat_id}:{spid}:{n[0]}"}
        for mod in ("repeat","auto_reverse","bounce_end"):
            if mod in track and mod not in kw:
                kw[mod]=track[mod]
        # T032: Argon's repeat/auto_reverse keyframe modifiers -> the one loop model.
        rep,rev=kw.pop("repeat",None),kw.pop("auto_reverse",None)
        if rep is not None or rev:
            e["loop"]={"repeat":rep if rep in ("indefinite","until-next-click") else max(1,int(round(rep or 1))),
                       "auto_reverse":bool(rev)}
        e.update({k:v for k,v in kw.items() if v is not None})
        effects.append(e)
        return e

    def flush_poly():
        nonlocal pending_poly
        if pending_poly is not None:
            eff("path",pending_poly["start"],pending_poly["end"]-pending_poly["start"],
                anchored=pending_poly["segments"],accel=pending_poly["ease"][0],decel=pending_poly["ease"][1],
                repeat=pending_poly.get("repeat"),auto_reverse=pending_poly.get("auto_reverse"),
                bounce_end=pending_poly.get("bounce_end"))
            pending_poly=None

    for kf in kfs:
        t=kf["t"]
        ease=EASE.get(kf.get("ease","standard"))  # T029: Carbon standard instead of symmetric
        if ease is None:
            raise ValueError(f"unknown ease {kf.get('ease')!r}")
        entering=kf.get("visible") is True and not visible
        if entering:
            flush_poly()
            preset,ms=kf.get("enter",ENTER_DEFAULT[0]),kf.get("enter_ms",ENTER_DEFAULT[1])
            if preset not in anim.ENTRANCES:
                raise ValueError(f"enter preset {preset!r} is not an entrance")
            eff(preset,t,ms)
            visible=True
        target=_resolve_point(kf,obj,objects_by_token,cur_pos)
        if target is None and pos_time is None:
            pos_time=t
        if "scale" not in kf and scale_time is None:
            scale_time=t
        if "rotate" not in kf and rot_time is None:
            rot_time=t
        if target is not None:
            jump=kf.get("jump") or (pos_time is None and entering)
            if math.dist(target,cur_pos)>1e-9:
                if jump:
                    flush_poly()
                    if visible and not entering:
                        eff("path",t,1,anchored=[{"x":cur_pos[0],"y":cur_pos[1]},{"x":target[0],"y":target[1]}])
                else:
                    seg_start=pos_time if pos_time is not None else 0
                    if t<=seg_start:
                        raise ValueError(f"{obj['name']!r}: position keyframe at t={t} needs time to move (use jump)")
                    vx,vy=target[0]-cur_pos[0],target[1]-cur_pos[1]
                    span=t-seg_start
                    if kf.get("anticipate"):
                        # Secondary: a small wind-up against the direction of travel.
                        a=float(kf["anticipate"])
                        back=(cur_pos[0]-vx*a,cur_pos[1]-vy*a)
                        lead=int(span*0.2)
                        eff("path",seg_start,lead,anchored=[{"x":cur_pos[0],"y":cur_pos[1]},{"x":back[0],"y":back[1]}],
                            accel=0.0,decel=0.6)
                        cur_pos=back
                        seg_start+=lead
                        span-=lead
                    final=target
                    if kf.get("overshoot"):
                        o=float(kf["overshoot"])
                        target=(final[0]+vx*o,final[1]+vy*o)
                    main=int(span*0.8) if kf.get("overshoot") else span
                    seg={"x":target[0],"y":target[1]}
                    if kf.get("curve"):
                        c1,c2=_arc_controls(cur_pos,target,kf["curve"])
                        seg["c1"]={"x":c1[0],"y":c1[1]}
                        seg["c2"]={"x":c2[0],"y":c2[1]}
                    elif "controls" in kf:
                        seg["c1"],seg["c2"]=kf["controls"]
                    if poly_mode or pending_poly is not None or kf.get("via"):
                        if pending_poly is None:
                            pending_poly={"start":seg_start,"end":t,"segments":[{"x":cur_pos[0],"y":cur_pos[1]},seg],
                                          "ease":ease,"repeat":kf.get("repeat"),"auto_reverse":kf.get("auto_reverse"),
                                          "bounce_end":kf.get("bounce_end")}
                        else:
                            pending_poly["segments"].append(seg)
                            pending_poly["end"]=t
                            pending_poly["ease"]=ease
                            for mod in ("repeat","auto_reverse","bounce_end"):
                                if mod in kf:
                                    pending_poly[mod]=kf[mod]
                        if not poly_mode and not kf.get("via"):
                            flush_poly()
                    else:
                        eff("path",seg_start,main,anchored=[{"x":cur_pos[0],"y":cur_pos[1]},seg],
                            accel=ease[0],decel=ease[1],repeat=kf.get("repeat"),
                            auto_reverse=kf.get("auto_reverse"),bounce_end=kf.get("bounce_end"))
                        if kf.get("overshoot"):
                            # Follow-through: settle back from the overshoot.
                            eff("path",seg_start+main,span-main,anchored=[{"x":target[0],"y":target[1]},
                                                                           {"x":final[0],"y":final[1]}],accel=0.3,decel=0.7)
                            target=final
            cur_pos=target
            pos_time=t
        if "scale" in kf:
            new=float(kf["scale"])
            if new<=0:
                raise ValueError("scale must be positive")
            seg_start=scale_time if scale_time is not None else 0
            if abs(new-cur_scale)>1e-9:
                eff("grow",seg_start,max(1,t-seg_start),ratio=new/cur_scale,accel=ease[0],decel=ease[1],
                    repeat=kf.get("repeat"),auto_reverse=kf.get("auto_reverse"),bounce_end=kf.get("bounce_end"))
                cur_scale=new
            scale_time=t
        if "rotate" in kf:
            new=float(kf["rotate"])
            seg_start=rot_time if rot_time is not None else 0
            if abs(new-cur_rot)>1e-9:
                eff("spin",seg_start,max(1,t-seg_start),by_deg=new-cur_rot,accel=ease[0],decel=ease[1],
                    repeat=kf.get("repeat"),auto_reverse=kf.get("auto_reverse"))
                cur_rot=new
            rot_time=t
        if "color" in kf:
            hx=anim.norm_hex(kf["color"])
            if hx!=cur_color:
                eff("color",t,kf.get("color_ms",400),color=hx,repeat=kf.get("repeat"),auto_reverse=kf.get("auto_reverse"))
                cur_color=hx
        if "opacity" in kf:
            value=float(kf["opacity"])
            if not 0<=value<=1:
                raise ValueError("opacity must be within 0..1")
            if abs(value-cur_opacity)>1e-9:
                eff("dim",t,kf.get("opacity_ms",400),opacity=value)
                cur_opacity=value
        if kf.get("visible") is False and visible:
            flush_poly()
            preset,ms=kf.get("exit",EXIT_DEFAULT[0]),kf.get("exit_ms",EXIT_DEFAULT[1])
            if preset not in anim.EXITS:
                raise ValueError(f"exit preset {preset!r} is not an exit")
            eff(preset,t,ms)
            visible=False
    flush_poly()
    return effects


def expand_rig_tracks(built_tracks,objects,states,objects_by_token,follow_through_ms=0):
    """Expand carrier tracks with synchronized follower tracks for any attached
    child shapes/labels not already explicitly targeted in ``built_tracks``.

    When ``follow_through_ms > 0``, each follower ``fi`` adds a phase lag
    ``(fi + 1) * follow_through_ms`` to its keyframes, producing realistic
    overlapping action / secondary motion inertia.
    """
    if not objects:
        return built_tracks
    rigs=detect_virtual_rigs(objects,transitive=True)
    if not rigs:
        return built_tracks
    explicit={tr["target"]["id"] for tr in built_tracks if isinstance(tr.get("target"),dict)}
    out=[]
    for tr in built_tracks:
        out.append(tr)
        carrier=tr.get("target")
        if not isinstance(carrier,dict) or carrier["id"] not in rigs:
            continue
        followers=[f for f in rigs[carrier["id"]] if f["id"] not in explicit]
        if not followers:
            continue
        ft_ms=int(tr.get("follow_through_ms",follow_through_ms) or 0)
        if "pulse_at" in tr:
            for fi,f in enumerate(followers):
                out.append({"target":f,"pulse_at":tr["pulse_at"]+(fi+1)*ft_ms})
            continue
        if "color_at" in tr:
            continue
        ac=authored(carrier)
        cs0=states.get(carrier["id"],fresh_state())
        for fi,f in enumerate(followers):
            lag=(fi+1)*ft_ms
            af=authored(f)
            ox,oy=af["cx"]-ac["cx"],af["cy"]-ac["cy"]
            fs0=states.get(f["id"],fresh_state())
            cur_c_pos=(cs0["dx"],cs0["dy"])
            cur_c_scale=cs0["scale"]
            cur_c_rot=cs0["rot"]
            fkfs=[]
            sorted_kfs=sorted(tr["keyframes"],key=lambda k:k["t"])
            for ki,kf in enumerate(sorted_kfs):
                t_val=kf["t"]+lag
                fk={"t":t_val}
                pos=_resolve_point(kf,carrier,objects_by_token,cur_c_pos)
                has_pos=pos is not None
                if has_pos:
                    cur_c_pos=pos
                if "scale" in kf:
                    cur_c_scale=float(kf["scale"])
                    fk["scale"]=cur_c_scale
                if "rotate" in kf:
                    cur_c_rot=float(kf["rotate"])
                    fk["rotate"]=cur_c_rot
                if has_pos or "scale" in kf or "rotate" in kf:
                    rad=math.radians(cur_c_rot)
                    rx=cur_c_scale*(ox*math.cos(rad)-oy*math.sin(rad))
                    ry=cur_c_scale*(ox*math.sin(rad)+oy*math.cos(rad))
                    shift_x,shift_y=rx-ox,ry-oy
                    fk["dx"]=cur_c_pos[0]+shift_x
                    fk["dy"]=cur_c_pos[1]+shift_y
                    if "curve" in kf:
                        fk["curve"]=kf["curve"]
                    elif "controls" in kf:
                        c1,c2=kf["controls"]
                        fk["controls"]=[{"x":c1["x"]+shift_x,"y":c1["y"]+shift_y},
                                        {"x":c2["x"]+shift_x,"y":c2["y"]+shift_y}]
                for k in ("jump","via","opacity","opacity_ms","visible",
                          "enter","enter_ms","exit","exit_ms","ease","repeat","auto_reverse","bounce_end"):
                    if k in kf:
                        fk[k]=kf[k]
                if len(kf)==1 and kf["t"]>0 and (fs0["dx"] or fs0["dy"]):
                    fk.setdefault("dx",0.0)
                    fk.setdefault("dy",0.0)
                fkfs.append(fk)
            ftr={"target":f,"keyframes":fkfs}
            for mod in ("poly_path","repeat","auto_reverse","bounce_end"):
                if mod in tr:
                    ftr[mod]=tr[mod]
            out.append(ftr)
    return out


# ---------------------------------------------------------------------------
# Recipes -> tracks


def _centroid(objs,states):
    pts=[(authored(o)["cx"]+states[o["id"]]["dx"],authored(o)["cy"]+states[o["id"]]["dy"]) for o in objs]
    return (sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))


def _pos(o,states):
    a=authored(o)
    s=states[o["id"]]
    return (a["cx"]+s["dx"],a["cy"]+s["dy"])


def _fit_scale(o,fill):
    a=authored(o)
    return max(1.0,min(fill/a["w"],fill/a["h"],3.0))


def _arc_step_keyframes(o,src,dst,cx,cy,t0,t1,via=False):
    a=authored(o)
    ang0=math.atan2(src[1]-cy,src[0]-cx)
    ang1=math.atan2(dst[1]-cy,dst[0]-cx)
    delta=(ang1-ang0+math.pi)%(2*math.pi)-math.pi
    r=(math.dist(src,(cx,cy))+math.dist(dst,(cx,cy)))/2
    kk=4/3*math.tan(delta/4)
    c1=(src[0]-kk*r*math.sin(ang0),src[1]+kk*r*math.cos(ang0))
    c2=(dst[0]+kk*r*math.sin(ang1),dst[1]-kk*r*math.cos(ang1))
    kf={"t":t1,"dx":dst[0]-a["cx"],"dy":dst[1]-a["cy"],
        "controls":[{"x":c1[0]-a["cx"],"y":c1[1]-a["cy"]},{"x":c2[0]-a["cx"],"y":c2[1]-a["cy"]}]}
    if via:
        kf["via"]=True
    return kf


def recipe_tracks(recipe,objs,states,params=None):
    """Return a list of tracks for a named recipe.

    objs: resolved target objects in order; states: current object states.
    """
    params=params or {}
    d=int(params.get("duration_ms",700))
    tracks=[]
    if recipe=="spotlight":
        focus,others=objs[0],objs[1:]
        scale=float(params.get("scale",1.15))
        toward=float(params.get("toward_center",0.0))
        fx,fy=_pos(focus,states)
        kf={"t":d,"scale":states[focus["id"]]["scale"]*scale}
        if toward:
            kf["x"]=fx+(0.5-fx)*toward
            kf["y"]=fy+(0.5-fy)*toward
        if params.get("color"):
            kf["color"]=params["color"]
        tracks.append({"target":focus,"keyframes":[{"t":0},kf]})
        if states[focus["id"]]["opacity"]<1:
            tracks[-1]["keyframes"][0]["opacity"]=1.0
        for o in others:
            if states[o["id"]]["visible"]:
                tracks.append({"target":o,"keyframes":[{"t":0,"opacity":float(params.get("dim",0.35))}]})
                if states[o["id"]]["scale"]>1.02:
                    tracks[-1]["keyframes"]+=[{"t":0,"scale":states[o["id"]]["scale"]},{"t":d,"scale":1.0}]
        halo=params.get("_halo_obj")
        if halo is not None:
            # Secondary layer: a soft halo glides behind the new focus.
            aspect=float(params.get("_aspect",16/9))
            fa,ha=authored(focus),authored(halo)
            want=max(fa["w"]*aspect,fa["h"])*scale*float(params.get("halo_size",1.6))
            have=max(ha["w"]*aspect,ha["h"])
            hs=states[halo["id"]]
            if hs["visible"]:
                kfs=[{"t":0},{"t":d,"to":focus["name"],"scale":want/have,"curve":float(params.get("halo_curve",0.15))}]
            else:
                kfs=[{"t":0,"to":focus["name"],"jump":True,"scale":want/have,"visible":True,"enter":"fade","enter_ms":d}]
            tracks.append({"target":halo,"keyframes":kfs})
    elif recipe=="release":
        for o in objs:
            s=states[o["id"]]
            kfs=[{"t":0}]
            end={"t":d}
            if s["dx"] or s["dy"]:
                end.update(dx=0.0,dy=0.0)
            if abs(s["scale"]-1)>1e-9:
                end["scale"]=1.0
            if abs(s["rot"])>1e-9:
                end["rotate"]=0.0
            if s["opacity"]<1:
                kfs[0]["opacity"]=1.0
            if not s["visible"]:
                kfs[0]["visible"]=True
                kfs[0]["enter"]=params.get("enter","fade")
            kfs.append(end)
            tracks.append({"target":o,"keyframes":kfs})
    elif recipe in ("assemble","disperse"):
        origin=params.get("from","center")
        stagger=int(params.get("stagger_ms",120))
        cx,cy=_centroid(objs,{o["id"]:fresh_state() for o in objs})
        for i,o in enumerate(objs):
            a=authored(o)
            if origin=="center":
                off=(cx-a["cx"],cy-a["cy"])
            elif origin=="slide-center":
                off=(0.5-a["cx"],0.5-a["cy"])
            elif origin in ("below","above","left","right"):
                dist=float(params.get("distance",0.25))
                off={"below":(0,dist),"above":(0,-dist),"left":(-dist,0),"right":(dist,0)}[origin]
            elif origin=="outward":
                vx,vy=a["cx"]-cx,a["cy"]-cy
                norm=math.hypot(vx,vy) or 1
                dist=float(params.get("distance",0.35))
                off=(vx/norm*dist,vy/norm*dist)
            else:
                raise ValueError(f"unknown assemble origin {origin!r}")
            t0=i*stagger
            if recipe=="assemble":
                end_kf={"t":t0+d,"dx":0.0,"dy":0.0,"ease":"out"}
                if params.get("bounce_end"):
                    end_kf["bounce_end"]=float(params["bounce_end"])
                tracks.append({"target":o,"keyframes":[
                    {"t":t0,"dx":off[0],"dy":off[1],"jump":True,"visible":True,"enter":params.get("enter","fade"),"enter_ms":min(d,500)},
                    end_kf]})
            else:
                tracks.append({"target":o,"keyframes":[
                    {"t":t0},
                    {"t":t0+d,"dx":off[0],"dy":off[1],"ease":"exit"},
                    {"t":max(t0,t0+d-min(d,400)),"visible":False,"exit":params.get("exit","fade-out"),"exit_ms":min(d,400)}]})
    elif recipe=="cycle":
        if len(objs)<3:
            raise ValueError("cycle needs at least three objects")
        steps=int(params.get("steps",1))
        direction=1 if params.get("direction","forward")=="forward" else -1
        poly=bool(params.get("poly_path",steps>1))
        cx,cy=_centroid(objs,states)
        positions=[_pos(o,states) for o in objs]
        n=len(objs)
        for i,o in enumerate(objs):
            kfs=[{"t":0}]
            for k in range(1,steps+1):
                src=positions[(i+direction*(k-1))%n]
                dst=positions[(i+direction*k)%n]
                kfs.append(_arc_step_keyframes(o,src,dst,cx,cy,(k-1)*d,k*d,via=(poly and k<steps)))
            tr={"target":o,"keyframes":kfs}
            if poly:
                tr["poly_path"]=True
            tracks.append(tr)
    elif recipe=="orbit":
        if len(objs)<2:
            raise ValueError("orbit needs at least two objects")
        around_first=bool(params.get("around_first",False))
        if around_first:
            hub,satellites=objs[0],objs[1:]
            cx,cy=_pos(hub,states)
        else:
            satellites=objs
            cx,cy=_centroid(satellites,states)
        angle_deg=float(params.get("angle_deg",360.0))
        direction=1 if params.get("direction","cw") in ("cw","forward") else -1
        total_rad=math.radians(angle_deg)*direction
        segs=max(1,int(math.ceil(abs(angle_deg)/90.0)))
        step_rad=total_rad/segs
        for o in satellites:
            a=authored(o)
            sx,sy=_pos(o,states)
            r=math.dist((sx,sy),(cx,cy))
            ang0=math.atan2(sy-cy,sx-cx)
            kfs=[{"t":0}]
            for k in range(1,segs+1):
                a0=ang0+(k-1)*step_rad
                a1=ang0+k*step_rad
                p0=(cx+r*math.cos(a0),cy+r*math.sin(a0))
                p1=(cx+r*math.cos(a1),cy+r*math.sin(a1))
                kk=4/3*math.tan(step_rad/4)
                c1=(p0[0]-kk*r*math.sin(a0),p0[1]+kk*r*math.cos(a0))
                c2=(p1[0]+kk*r*math.sin(a1),p1[1]-kk*r*math.cos(a1))
                kfs.append({"t":int(round(k*d/segs)),"dx":p1[0]-a["cx"],"dy":p1[1]-a["cy"],
                            "controls":[{"x":c1[0]-a["cx"],"y":c1[1]-a["cy"]},{"x":c2[0]-a["cx"],"y":c2[1]-a["cy"]}],
                            "via":k<segs})
            tr={"target":o,"keyframes":kfs,"poly_path":True}
            if params.get("repeat"):
                tr["repeat"]=params["repeat"]
            if params.get("auto_reverse"):
                tr["auto_reverse"]=bool(params["auto_reverse"])
            tracks.append(tr)
    elif recipe=="orbit-3d":
        if len(objs)<3:
            raise ValueError("orbit-3d needs at least three objects")
        around_first=bool(params.get("around_first",False))
        satellites=objs[1:] if around_first else objs
        if len(satellites)<3:
            raise ValueError("orbit-3d requires at least 3 orbiting satellites")
        cx,cy=_pos(objs[0],states) if around_first else _centroid(satellites,states)
        steps=int(params.get("steps",1))
        direction=1 if params.get("direction","cw") in ("cw","forward") else -1
        depth_scale=float(params.get("depth_scale",0.20))
        depth_dim=float(params.get("depth_dim",0.48))
        positions=[_pos(o,states) for o in satellites]
        n=len(satellites)
        for i,o in enumerate(satellites):
            a=authored(o)
            src=positions[i]
            dst=positions[(i+direction*steps)%n]
            ang0=math.atan2(src[1]-cy,src[0]-cx)
            ang1=math.atan2(dst[1]-cy,dst[0]-cx)
            # Elliptical arc control points preserving horizontal/vertical radii
            rx=max(0.08,max(abs(p[0]-cx) for p in positions))
            ry=max(0.05,max(abs(p[1]-cy) for p in positions))
            delta=(ang1-ang0+math.pi)%(2*math.pi)-math.pi
            kk=4/3*math.tan(delta/4)
            c1=(src[0]-kk*rx*math.sin(ang0),src[1]+kk*ry*math.cos(ang0))
            c2=(dst[0]+kk*rx*math.sin(ang1),dst[1]-kk*ry*math.cos(ang1))
            # Depth factor: sin(ang1) in [-1 (back/top), +1 (front/bottom)]
            depth=math.sin(ang1)
            target_scale=round(max(0.65,min(1.45,1.0+depth_scale*depth)),4)
            target_opacity=1.0 if depth>=-0.15 else round(depth_dim+(1.0-depth_dim)*(depth+1.0)/0.85,2)
            kf={"t":d,"dx":dst[0]-a["cx"],"dy":dst[1]-a["cy"],"scale":target_scale,
                "controls":[{"x":c1[0]-a["cx"],"y":c1[1]-a["cy"]},{"x":c2[0]-a["cx"],"y":c2[1]-a["cy"]}]}
            kfs=[{"t":0}]
            if abs(target_opacity-states[o["id"]]["opacity"])>0.05:
                kfs[0]["opacity"]=target_opacity
            kfs.append(kf)
            tracks.append({"target":o,"keyframes":kfs})
    elif recipe=="explode-layers":
        if len(objs)<2:
            raise ValueError("explode-layers needs at least two layers")
        axis=params.get("axis","iso")
        spread=float(params.get("spread",0.32))
        stagger=int(params.get("stagger_ms",90))
        bounce=float(params.get("bounce_end",0.30))
        scale=float(params.get("scale",1.0))
        n=len(objs)
        for i,o in enumerate(objs):
            s0=states[o["id"]]
            factor=(i-(n-1)/2)/max(1,n-1)
            delta=factor*spread
            if axis=="y":
                dx,dy=0.0,delta
            elif axis=="x":
                dx,dy=delta,0.0
            else:
                dx,dy=delta*0.42,delta
            t0=i*stagger
            end_kf={"t":t0+d,"dx":s0["dx"]+dx,"dy":s0["dy"]+dy,"ease":"out"}
            if bounce>0:
                end_kf["bounce_end"]=bounce
            if abs(scale-1.0)>1e-6:
                end_kf["scale"]=s0["scale"]*scale
            tracks.append({"target":o,"keyframes":[{"t":t0,"dx":s0["dx"],"dy":s0["dy"],"scale":s0["scale"]},end_kf]})
    elif recipe=="cascade-flow":
        if len(objs)<3:
            raise ValueError("cascade-flow needs at least 1 token and 2 stages")
        token_count=int(params.get("token_count",1))
        if not 1<=token_count<len(objs):
            raise ValueError("cascade-flow token_count must leave at least 1 stage")
        tokens,stages=objs[:token_count],objs[token_count:]
        stagger=int(params.get("stagger_ms",140))
        hop_ms=int(params.get("hop_ms",max(250,d//max(1,len(stages)))))
        base_arc=float(params.get("arc",0.18))
        stage_color=params.get("stage_color")
        offset_y=float(params.get("offset_y",-0.06))
        for ti,tok in enumerate(tokens):
            a=authored(tok)
            t0=ti*stagger
            spread_x=(ti-(token_count-1)/2)*float(params.get("token_spread_x",0.038))
            kfs=[{"t":t0,"dx":states[tok["id"]]["dx"],"dy":states[tok["id"]]["dy"]}]
            for si,st_obj in enumerate(stages):
                sx,sy=_pos(st_obj,states)
                sign=1 if (si+ti)%2==0 else -1
                kfs.append({
                    "t":t0+(si+1)*hop_ms,
                    "dx":sx+spread_x-a["cx"],
                    "dy":sy+offset_y-a["cy"],
                    "curve":base_arc*sign,
                    "via":si<len(stages)-1,
                })
            tracks.append({"target":tok,"poly_path":True,"keyframes":kfs})
        if params.get("pulse_stages",True):
            for si,st_obj in enumerate(stages):
                arr=(si+1)*hop_ms
                tracks.append({"target":st_obj,"pulse_at":arr})
                if stage_color:
                    tracks.append({"target":st_obj,"color_at":(arr,stage_color)})
    elif recipe=="wave":
        stagger=int(params.get("stagger_ms",120))
        amp=float(params.get("amplitude",0.05))
        scale=float(params.get("scale",1.10))
        for i,o in enumerate(objs):
            s0=states[o["id"]]
            t0=i*stagger
            half=max(100,d//2)
            tracks.append({"target":o,"poly_path":True,"keyframes":[
                {"t":t0,"dx":s0["dx"],"dy":s0["dy"],"scale":s0["scale"]},
                {"t":t0+half,"dx":s0["dx"],"dy":s0["dy"]-amp,"scale":s0["scale"]*scale,"via":True,"ease":"out"},
                {"t":t0+2*half,"dx":s0["dx"],"dy":s0["dy"],"scale":s0["scale"],"ease":"in"},
            ]})
    elif recipe=="swap":
        if len(objs)!=2:
            raise ValueError("swap needs exactly two objects")
        a,b=objs
        pa,pb=_pos(a,states),_pos(b,states)
        arc=float(params.get("arc",0.25))
        extra={k:float(params[k]) for k in ("overshoot","anticipate") if params.get(k)}
        tracks.append({"target":a,"keyframes":[{"t":0},{"t":d,"x":pb[0],"y":pb[1],"curve":arc,**extra}]})
        tracks.append({"target":b,"keyframes":[{"t":0},{"t":d,"x":pa[0],"y":pa[1],"curve":arc,**extra}]})
    elif recipe=="travel":
        token,stops=objs[0],objs[1:]
        if not stops:
            raise ValueError("travel needs a token and at least one stop")
        dwell=int(params.get("dwell_ms",250))
        poly=bool(params.get("poly_path",False))
        kfs=[{"t":0}]
        t=0
        for si,stop in enumerate(stops):
            sx,sy=_pos(stop,states)
            t+=d
            kf={"t":t,"x":sx+float(params.get("offset_x",0)),"y":sy+float(params.get("offset_y",0)),
                "curve":float(params.get("arc",0.0))}
            for key in ("overshoot","anticipate"):
                if params.get(key):
                    kf[key]=float(params[key])
            if poly and dwell==0 and si<len(stops)-1:
                kf["via"]=True
            kfs.append(kf)
            t+=dwell
        tr={"target":token,"keyframes":kfs}
        if poly and dwell==0:
            tr["poly_path"]=True
        tracks.append(tr)
        if params.get("pulse_stops",True):
            for i,stop in enumerate(stops):
                tracks.append({"target":stop,"pulse_at":(i+1)*d+i*dwell})
    elif recipe=="rise":
        # Text rises out of an invisible line: it starts under a mask painted
        # in the colour behind it and slides up past the mask's top edge.
        text=objs[0]
        mask=params.get("_mask_obj")
        a=authored(text)
        dist=float(params.get("distance",a["h"]*1.1+0.01))
        enter="appear"
        if mask is not None:
            # The mask's top edge is the line: the text starts with its first
            # line just below it and rises into place.
            tb=text_block(text,float(params.get("_aspect",16/9)))
            m=mask["geometry"]
            if "distance" not in params:
                dist=max(0.01,m["y"]-tb[1]+0.004)
            if m["h"]<(tb[3]-tb[1])+0.004:
                # Clipped to its container: rise as far as the mask reaches
                # and fade in, so nothing ever shows below the line.
                dist,enter=max(0.01,min(dist,m["h"]*0.95)),"fade"
        tracks.append({"target":text,"keyframes":[
            {"t":0,"dy":dist,"jump":True,"visible":True,"enter":enter,"enter_ms":int(d*0.8)},
            {"t":d,"dy":0.0,"ease":"enter"}]})
        if mask is not None:
            tracks.append({"target":mask,"keyframes":[
                {"t":0,"visible":True,"enter":"appear"},
                {"t":d+60,"visible":False,"exit":"disappear","exit_ms":0}]})
    elif recipe=="zoom-focus":
        focus,others=objs[0],objs[1:]
        fill=float(params.get("fill",0.6))
        scale=float(params.get("scale",_fit_scale(focus,fill)))
        tracks.append({"target":focus,"keyframes":[{"t":0},{"t":d,"x":float(params.get("x",0.5)),
                                                            "y":float(params.get("y",0.5)),"scale":scale}]})
        for o in others:
            if states[o["id"]]["visible"]:
                tracks.append({"target":o,"keyframes":[{"t":0,"visible":False,"exit":"fade-out","exit_ms":min(d,400)}]})
    elif recipe=="ken-burns":
        # Slow push-in with a gentle drift: a still picture keeps living while
        # the presenter talks. Neighbouring pictures drift in opposite directions.
        d=int(params.get("duration_ms",6000))
        scale=float(params.get("scale",1.06))
        drift=float(params.get("drift",0.015))
        for i,o in enumerate(objs):
            s=states[o["id"]]
            sign=-1 if i%2 else 1
            tracks.append({"target":o,"keyframes":[{"t":0},{"t":d,"scale":s["scale"]*scale,
                                                           "dx":s["dx"]+sign*drift,"dy":s["dy"]-0.6*drift,"ease":"linear"}]})
    else:
        raise ValueError(f"unknown recipe {recipe!r}")
    return tracks


RECIPES=("spotlight","release","assemble","disperse","cycle","swap","travel","zoom-focus","rise","ken-burns",
         "orbit","orbit-3d","wave","explode-layers","cascade-flow")
AMBIENT_RECIPES=("breathe","drift","spin-loop")
SECONDARY_RECIPES=("ripple",)


def ambient_effects(recipe,objs,states,beat_id,params):
    """Looping background motion (breathe, drift, spin-loop) and the ripple
    acknowledgement. Loops run until the slide ends (or next click)."""
    params=params or {}
    repeat=params.get("repeat","indefinite")
    effects=[]
    for i,o in enumerate(objs):
        st=states[o["id"]]
        delay=int(params.get("stagger_ms",300 if recipe!="ripple" else 120))*i
        base={"spid":o["id"],"trigger":"with","delay_ms":delay,"beat":f"{beat_id}:{o['id']}:{recipe}"}
        if recipe=="breathe":
            effects.append({**base,"preset":"grow","duration_ms":int(params.get("period_ms",3200))//2,
                            "ratio":float(params.get("scale",1.04)),"accel":0.5,"decel":0.5,
                            "loop":{"repeat":repeat,"auto_reverse":True}})
        elif recipe=="drift":
            amp=float(params.get("amplitude",0.015))*(1+0.5*(i%3))
            ang=float(params.get("angle_deg",-30))+i*70
            dx,dy=amp*math.cos(math.radians(ang)),amp*math.sin(math.radians(ang))
            effects.append({**base,"preset":"path","duration_ms":int(params.get("period_ms",9000))//2,
                            "anchored":[{"x":st["dx"],"y":st["dy"]},{"x":st["dx"]+dx,"y":st["dy"]+dy}],
                            "accel":0.5,"decel":0.5,"loop":{"repeat":repeat,"auto_reverse":True}})
        elif recipe=="spin-loop":
            effects.append({**base,"preset":"spin","duration_ms":int(params.get("period_ms",30000)),
                            "by_deg":float(params.get("by_deg",360)),"loop":{"repeat":repeat}})
        elif recipe=="ripple":
            effects.append({**base,"preset":"pulse","duration_ms":int(params.get("pulse_ms",180)),
                            "scale":float(params.get("scale",1.06))})
        else:
            raise ValueError(f"unknown ambient recipe {recipe!r}")
    return effects


def attach_followers(effects,attach,objects_by_token,states):
    """Copy a leader's movement onto followers (e.g. a separate label) so they
    stay together. Scaling the leader moves followers radially so their
    relative placement scales with it."""
    out=list(effects)
    for leader_tok,followers in (attach or {}).items():
        leader=objects_by_token.get(leader_tok)
        if leader is None:
            raise ValueError(f"attach: leader {leader_tok!r} not found")
        lead=[e for e in effects if e["spid"]==leader["id"]]
        for ftok in followers:
            f=objects_by_token.get(ftok)
            if f is None:
                raise ValueError(f"attach: follower {ftok!r} not found")
            ls,fs=states[leader["id"]],states[f["id"]]
            off=(fs["dx"]-ls["dx"],fs["dy"]-ls["dy"])
            la,fa=authored(leader),authored(f)
            rel=((fa["cx"]+fs["dx"])-(la["cx"]+ls["dx"]),(fa["cy"]+fs["dy"])-(la["cy"]+ls["dy"]))
            paths={(e["delay_ms"],e["duration_ms"]):e for e in lead if e["preset"]=="path"}
            copies=[]
            for e in lead:
                if e["preset"]=="spin":
                    continue
                c=dict(e,spid=f["id"],beat=e["beat"]+f":follow{f['id']}")
                if e["preset"]=="path":
                    c["anchored"]=[dict(p,x=p["x"]+off[0],y=p["y"]+off[1],
                                        **({"c1":{"x":p["c1"]["x"]+off[0],"y":p["c1"]["y"]+off[1]},
                                            "c2":{"x":p["c2"]["x"]+off[0],"y":p["c2"]["y"]+off[1]}} if "c1" in p else {}))
                                   for p in e["anchored"]]
                if e["preset"] in ("grow","pulse"):
                    ratio=e.get("ratio",e.get("scale",1.0))
                    shift=(rel[0]*(ratio-1),rel[1]*(ratio-1))
                    key=(e["delay_ms"],e["duration_ms"])
                    if e["preset"]=="grow" and key in paths:
                        paired=next(x for x in copies if x["preset"]=="path" and (x["delay_ms"],x["duration_ms"])==key)
                        last=paired["anchored"][-1]
                        last["x"]+=shift[0]
                        last["y"]+=shift[1]
                    elif e["preset"]=="grow" and (abs(shift[0])>1e-6 or abs(shift[1])>1e-6):
                        start=(fs["dx"],fs["dy"])
                        copies.append({"preset":"path","spid":f["id"],"trigger":"with","delay_ms":e["delay_ms"],
                                       "duration_ms":e["duration_ms"],"beat":c["beat"]+":shift",
                                       "anchored":[{"x":start[0],"y":start[1]},{"x":start[0]+shift[0],"y":start[1]+shift[1]}],
                                       "accel":e.get("accel",0),"decel":e.get("decel",0)})
                copies.append(c)
            out.extend(copies)
    out.sort(key=lambda e:e["delay_ms"])
    return out


def _compile_built_tracks(built,states,objects_by_token,beat_id):
    effects=[]
    for track in built:
        obj=track["target"]
        if "pulse_at" in track:
            effects.append({"preset":"pulse","spid":obj["id"],"trigger":"with","delay_ms":int(track["pulse_at"]),
                            "duration_ms":200,"scale":1.08,"beat":f"{beat_id}:{obj['id']}:pulse"})
            continue
        if "color_at" in track:
            t_ms,col=track["color_at"]
            effects.append({"preset":"color","spid":obj["id"],"trigger":"with","delay_ms":int(t_ms),
                            "duration_ms":350,"color":anim.norm_hex(col),"beat":f"{beat_id}:{obj['id']}:color"})
            continue
        effects.extend(compile_track(track,obj,objects_by_token,states[obj["id"]],beat_id))
    return effects


def resolve_trajectory_collisions(built,all_objects,states,objects_by_token,beat_id):
    """If a straight/low-arc trajectory collides mid-flight with another object,
    try curving the segment(s) with candidate arc bulges until clear."""
    if not all_objects:
        return built
    effs=_compile_built_tracks(built,states,objects_by_token,beat_id)
    base_trans=transient_warnings(all_objects,states,effs,"check")
    if not base_trans:
        return built
    candidates=(0.25,-0.25,0.38,-0.38,0.52,-0.52)
    best=built
    best_score=len(base_trans)
    for idx,tr in enumerate(built):
        if "keyframes" not in tr or len(tr["keyframes"])<2:
            continue
        for cand in candidates:
            trial=copy.deepcopy(best)
            changed=False
            for kf in trial[idx]["keyframes"][1:]:
                if any(k in kf for k in ("x","y","dx","dy","to")) and "controls" not in kf:
                    kf["curve"]=cand
                    changed=True
            if not changed:
                continue
            trial_effs=_compile_built_tracks(trial,states,objects_by_token,beat_id)
            end_st=advance(states,trial_effs)
            end_w=layout_warnings(all_objects,end_st,"end")
            tr_w=transient_warnings(all_objects,states,trial_effs,"check")
            score=len(tr_w)+2*len(end_w)
            if score<best_score:
                best=trial
                best_score=score
                if best_score==0:
                    return best
    return best


def compile_choreography(recipe,objs,states,objects_by_token,beat_id,params=None,tracks=None):
    """Return effects (delays relative to the beat start) for a recipe or raw
    tracks. ``objs`` are resolved objects; raw ``tracks`` use {"target": obj}."""
    params=params or {}
    if recipe=="float":  # T024 name for a vertical idle bob: drift straight up
        recipe,params="drift",{"angle_deg":-90,"amplitude":0.012,"period_ms":2600,**(params or {})}
    if recipe in AMBIENT_RECIPES+SECONDARY_RECIPES:
        return ambient_effects(recipe,objs,states,beat_id,params)
    if params.get("halo"):
        params=dict(params,_halo_obj=objects_by_token.get(params["halo"]))
        if params["_halo_obj"] is None:
            raise ValueError(f"halo {params['halo']!r} not found")
    if params.get("mask"):
        params=dict(params,_mask_obj=objects_by_token.get(params["mask"]))
        if params["_mask_obj"] is None:
            raise ValueError(f"mask {params['mask']!r} not found")
        m=bbox(params["_mask_obj"],fresh_state())
        for o in objects_by_token.values():
            if o is params["_mask_obj"] or o is objs[0] or not o.get("geometry") or not states.get(o["id"],{}).get("visible"):
                continue
            if (o.get("name") or "").startswith("__gen_"):
                continue
            ob=bbox(o,states[o["id"]])
            area=(ob[2]-ob[0])*(ob[3]-ob[1]) or 1
            if o.get("filled") and ob[0]<=m[0] and ob[1]<=m[1] and ob[2]>=m[2] and ob[3]>=m[3]:
                continue  # the container the mask is painted to match
            if _overlap(m,ob)>0.05*area:
                raise ValueError(f"rise mask would briefly cover {o['name']!r}; use another reveal or move the text")
    if recipe=="tracks":
        built=tracks
    else:
        built=recipe_tracks(recipe,objs,states,params)
    all_objects=list({id(o):o for o in objects_by_token.values() if isinstance(o,dict) and "id" in o}.values())
    if params.get("auto_avoid"):
        built=resolve_trajectory_collisions(built,all_objects,states,objects_by_token,beat_id)
    if params.get("rigging",True):
        ft_ms=int(params.get("follow_through_ms",0) or 0)
        built=expand_rig_tracks(built,all_objects,states,objects_by_token,follow_through_ms=ft_ms)
    effects=_compile_built_tracks(built,states,objects_by_token,beat_id)
    if not effects:
        raise ValueError(f"{recipe}: nothing changes from the current state")
    effects.sort(key=lambda e:e["delay_ms"])
    if params.get("attach"):
        effects=attach_followers(effects,params["attach"],objects_by_token,states)
    return effects


# ---------------------------------------------------------------------------
# Checks


PROP_OF={"path":"pos","grow":"scale","pulse":"scale","zoom":"scale","spin":"rot","dim":"opacity"}
for _name,_lib in anim.LIBRARY.items():
    _tags={b["tag"] for b in _lib["behaviours"]}
    PROP_OF[_name]=("pos" if "animMotion" in _tags else "scale" if "animScale" in _tags
                    else "rot" if "animRot" in _tags else None) if _lib["presetClass"] in ("path","emph") else None
PROP_OF.update({"teeter":"rot","color":"color"})


def conflicts(effects):
    """Overlapping animations of the same property on the same object."""
    found=[]
    spans={}
    for start,end,eff in schedule(effects):
        if eff.get("paragraph") is not None or eff.get("chart") is not None:
            continue
        prop=PROP_OF.get(eff["preset"])
        if prop is None or prop in ("opacity","color"):
            continue
        key=(eff["spid"],prop)
        if eff.get("loop"):
            end=float("inf")
        for s,e in spans.get(key,[]):
            if start<e and s<end:
                found.append(f"object {eff['spid']}: overlapping {prop} animations ({s}-{e} ms and {start}-{end} ms)")
        spans.setdefault(key,[]).append((start,end))
    return found


def bbox(obj,st):
    a=authored(obj)
    w,h=a["w"]*st["scale"],a["h"]*st["scale"]
    cx,cy=a["cx"]+st["dx"],a["cy"]+st["dy"]
    return (cx-w/2,cy-h/2,cx+w/2,cy+h/2)


def _overlap(b1,b2):
    w=min(b1[2],b2[2])-max(b1[0],b2[0])
    h=min(b1[3],b2[3])-max(b1[1],b2[1])
    return max(0,w)*max(0,h)


def layout_warnings(objects,states,label):
    """Out-of-slide and new-occlusion warnings for a stable state."""
    warn=[]
    rig_pairs=_rig_pairs(objects)
    vis=[o for o in objects if o.get("geometry") and states.get(o["id"],{}).get("visible")]
    for o in vis:
        b=bbox(o,states[o["id"]])
        a=bbox(o,fresh_state())
        if a[0]<0.005 or a[1]<0.005 or a[2]>0.995 or a[3]>0.995:
            continue  # authored at/past the edge (bleed, backdrop orb): the slide crops it by design
        if b[0]<-0.02 or b[1]<-0.02 or b[2]>1.02 or b[3]>1.02:
            warn.append(f"{label}: {o['name']!r} extends outside the slide")
    moved=[o for o in vis if any(abs(states[o["id"]][k]-v)>1e-6 for k,v in (("dx",0),("dy",0),("scale",1)))]
    for o in moved:
        bo=bbox(o,states[o["id"]])
        for other in vis:
            if other is o or (o["id"],other["id"]) in rig_pairs:
                continue
            if not other.get("text") and objects.index(other)<objects.index(o):
                continue  # passing over a text-free shape behind it (background decor) is fine
            bt=bbox(other,states[other["id"]])
            before=_overlap(bbox(o,fresh_state()),bbox(other,fresh_state()))
            now=_overlap(bo,bt)
            smaller=min((bo[2]-bo[0])*(bo[3]-bo[1]),(bt[2]-bt[0])*(bt[3]-bt[1])) or 1
            if now-before>0.15*smaller and states[other["id"]]["opacity"]>0.5 and states[o["id"]]["opacity"]>0.5:
                warn.append(f"{label}: {o['name']!r} now covers {other['name']!r}")
    return sorted(set(warn))


def transient_warnings(objects,start_states,effects,label,samples=(0.2,0.35,0.5,0.65,0.8)):
    """Sample intermediate instants of a click group to detect mid-motion
    collisions or occlusions that disappear by the end of the click."""
    dur=group_duration(effects)
    if dur<=1:
        return []
    rig_pairs=_rig_pairs(objects)
    end_states=advance(start_states,effects)
    moving_ids={e["spid"] for e in effects if e.get("preset") in ("path","grow")}
    if not moving_ids:
        return []
    warn=set()
    for frac in samples:
        t=dur*frac
        st=state_at(start_states,effects,t)
        vis=[o for o in objects if o.get("geometry") and st.get(o["id"],{}).get("visible")
             and st[o["id"]].get("opacity",1.0)>0.5 and st[o["id"]].get("alpha",1.0)>0.3]
        for o in vis:
            if o["id"] not in moving_ids:
                continue
            bo=bbox(o,st[o["id"]])
            if bo[0]<-0.05 or bo[1]<-0.05 or bo[2]>1.05 or bo[3]>1.05:
                warn.add(f"{label} (mid-motion): {o['name']!r} travels outside the slide")
            for other in vis:
                if other is o or (o["id"],other["id"]) in rig_pairs:
                    continue
                bt=bbox(other,st[other["id"]])
                smaller=min((bo[2]-bo[0])*(bo[3]-bo[1]),(bt[2]-bt[0])*(bt[3]-bt[1])) or 1
                start_ov=_overlap(bbox(o,start_states.get(o["id"],fresh_state())),
                                  bbox(other,start_states.get(other["id"],fresh_state())))
                end_ov=_overlap(bbox(o,end_states.get(o["id"],fresh_state())),
                                bbox(other,end_states.get(other["id"],fresh_state())))
                now_ov=_overlap(bo,bt)
                if now_ov-max(start_ov,end_ov)>0.22*smaller:
                    pair=tuple(sorted((o["name"],other["name"])))
                    warn.add(f"{label} (mid-motion): {pair[0]!r} passes over {pair[1]!r}")
    return sorted(warn)


# ---------------------------------------------------------------------------
# Reading timing XML back into effect dicts (any deck)

_ENTR_BY_ID={1:"appear",10:"fade",42:"float-in",53:"zoom",22:"wipe-up",21:"wheel",6:"circle",20:"wedge"}
_EXIT_BY_ID={1:"disappear",10:"fade-out"}
_PATH_TOKEN=__import__("re").compile(r"[MLCZE]|-?\d*\.?\d+(?:[eE]-?\d+)?")


def parse_path(path):
    """Parse an animMotion path into anchored segments (slide fractions)."""
    tokens=_PATH_TOKEN.findall(path or "")
    segs=[]
    i=0
    cmd=None
    while i<len(tokens):
        tok=tokens[i]
        if tok in "MLCZE":
            cmd=tok
            i+=1
            if tok in "ZE":
                continue
            continue
        if cmd in ("M","L"):
            x,y=float(tokens[i]),float(tokens[i+1])
            segs.append({"x":x,"y":y})
            i+=2
        elif cmd=="C":
            vals=[float(v) for v in tokens[i:i+6]]
            segs.append({"x":vals[4],"y":vals[5],"c1":{"x":vals[0],"y":vals[1]},"c2":{"x":vals[2],"y":vals[3]}})
            i+=6
        else:
            i+=1
    return segs


def effects_from_slide(root):
    """Click groups of effect dicts read from a slide's main sequence.

    Each group is a list whose first effect has trigger "click" and the rest
    "with"; delay_ms is the absolute start inside the group, so schedule()
    reproduces the authored timeline. Returns (groups, auto_flags).
    """
    P,NS=anim.P,anim.NS
    main=root.find(".//p:timing//p:cTn[@nodeType='mainSeq']",NS)
    groups=[]
    autos=[]
    if main is None:
        return groups,autos
    for gpar in main.findall("p:childTnLst/p:par",NS):
        gctn=gpar.find("p:cTn",NS)
        conds=gctn.findall("p:stCondLst/p:cond",NS)
        autos.append(any(c.get("evt")=="onBegin" for c in conds))
        effects=[]
        for bpar in gctn.findall("p:childTnLst/p:par",NS):
            bctn=bpar.find("p:cTn",NS)
            bdelay=_delay(bctn)
            for epar in bctn.findall("p:childTnLst/p:par",NS):
                ectn=epar.find("p:cTn",NS)
                eff=_effect_from_ctn(ectn)
                if eff is None:
                    continue
                eff["delay_ms"]=bdelay+_delay(ectn)
                effects.append(eff)
        effects.sort(key=lambda e:e["delay_ms"])
        for i,e in enumerate(effects):
            e["trigger"]="click" if i==0 else "with"
            if e.get("iterate"):
                e["iterate"]["units"]=text_units(root,e["spid"],e["iterate"]["by"],e.get("paragraph"))
        groups.append(effects)
    return groups,autos


def _delay(ctn):
    cond=ctn.find(f"{{{anim.P}}}stCondLst/{{{anim.P}}}cond")
    try:
        return int(cond.get("delay")) if cond is not None and cond.get("delay") not in (None,"indefinite") else 0
    except ValueError:
        return 0


def _read_modifiers(ctn,inner_ctn,eff):
    bounce=ctn.get(f"{{{anim.P14}}}bounceEnd")
    if bounce and bounce.isdigit():
        eff["bounce_end"]=int(bounce)/100000
    if inner_ctn is not None:
        rc=inner_ctn.get("repeatCount")
        if rc=="indefinite":
            eff["repeat"]="indefinite"
        elif rc and rc.isdigit() and int(rc)>1000:
            eff["repeat"]=int(rc)/1000
        if inner_ctn.get("autoRev")=="1" and eff.get("preset") not in ("pulse","teeter"):
            eff["auto_reverse"]=True


def _effect_from_ctn(ctn):
    NS=anim.NS
    cls=ctn.get("presetClass")
    try:
        pid=int(ctn.get("presetID") or -1)
    except ValueError:
        pid=-1
    tgt=ctn.find(".//p:spTgt",NS)
    if tgt is None:
        return None
    eff={"spid":tgt.get("spid")}
    pr=tgt.find("p:txEl/p:pRg",NS)
    if pr is not None:
        eff["paragraph"]=int(pr.get("st"))
    chart=tgt.find(f"p:graphicEl/{{{anim.A}}}chart",NS)
    if chart is not None:
        eff["chart"]=(chart.get("seriesIdx"),chart.get("categoryIdx"),chart.get("bldStep"))
    durs=[int(c.get("dur")) for c in ctn.iter(anim.q("cTn")) if c is not ctn and (c.get("dur") or "").isdigit()]
    eff["duration_ms"]=max([d for d in durs if d>1],default=1)
    motion=ctn.find(".//p:animMotion",NS)
    scale=ctn.find(".//p:animScale",NS)
    rot=ctn.find(".//p:animRot",NS)
    clr=ctn.find(".//p:animClr",NS)
    if cls=="entr" or (cls is None and ctn.find(".//p:animEffect[@transition='in']",NS) is not None):
        eff["preset"]=_ENTR_BY_ID.get(pid,"fade")
        if eff["preset"]=="appear":
            eff["duration_ms"]=0
    elif cls=="exit" or (cls is None and ctn.find(".//p:animEffect[@transition='out']",NS) is not None):
        eff["preset"]=_EXIT_BY_ID.get(pid,"fade-out")
        if eff["preset"]=="disappear":
            eff["duration_ms"]=0
    elif motion is not None:
        eff["preset"]="path"
        eff["anchored"]=parse_path(motion.get("path"))
        if len(eff["anchored"])<2:
            return None
        for key in ("accel","decel"):
            if ctn.get(key):
                eff[key]=int(ctn.get(key))/100000
        _read_modifiers(ctn,motion.find("p:cBhvr/p:cTn",NS),eff)
    elif scale is not None:
        by=scale.find("p:by",NS)
        inner=scale.find("p:cBhvr/p:cTn",NS)
        ratio=int(by.get("x"))/100000 if by is not None else 1.0
        if pid==6 and inner is not None and inner.get("autoRev")=="1" and not inner.get("repeatCount"):
            eff["preset"]="pulse"
            eff["scale"]=ratio
        else:
            eff["preset"]="grow"
            eff["ratio"]=ratio
            _read_modifiers(ctn,inner,eff)
    elif rot is not None:
        inner=rot.find("p:cBhvr/p:cTn",NS)
        if pid==32 and cls=="emph":  # PowerPoint Teeter (T032: was misread as 14 = Blast)
            eff["preset"]="teeter"
            eff["by_deg"]=abs(int(rot.get("by","0")))/60000
        else:
            eff["preset"]="spin"
            eff["by_deg"]=int(rot.get("by","0"))/60000
            _read_modifiers(ctn,inner,eff)
    elif clr is not None:
        srgb=clr.find(f".//{{{anim.A}}}srgbClr")
        eff["preset"]="color"
        eff["color"]="#"+(srgb.get("val") if srgb is not None else "E06C4F")
        _read_modifiers(ctn,clr.find("p:cBhvr/p:cTn",NS),eff)
    elif ctn.find(".//p:set/p:cBhvr/p:attrNameLst[p:attrName='style.opacity']",NS) is not None:
        val=ctn.find(".//p:set/p:to/p:strVal",NS)
        eff["preset"]="dim"
        eff["opacity"]=float(val.get("val")) if val is not None else 0.35
        eff["duration_ms"]=400
    else:
        return None
    it=ctn.find("p:iterate",NS)
    if it is not None:
        gap=it.find("p:tmAbs",NS)
        pct=it.find("p:tmPct",NS)
        eff["iterate"]={"by":"letter" if it.get("type")=="lt" else "word","units":1}
        if gap is not None:
            eff["iterate"]["gap_ms"]=int(gap.get("val"))
        elif pct is not None:
            eff["iterate"]["pct"]=int(pct.get("val"))/100000
    rc=ctn.get("repeatCount")
    if rc:
        until_click=ctn.find("p:endCondLst/p:cond[@evt='onNext']",NS) is not None
        repeat="until-next-click" if until_click else ("indefinite" if rc=="indefinite" else max(1,int(rc)//1000))
        eff["loop"]={"repeat":repeat,"auto_reverse":ctn.get("autoRev")=="1"}
    return eff



def text_units(root,spid,by,paragraph=None):
    """Number of letters (non-space) or words a by-word/letter effect animates."""
    node=anim.top_level_objects(root).get(spid)
    if node is None:
        return 1
    paras=node.findall("p:txBody/a:p",anim.NS)
    if paragraph is not None:
        paras=paras[paragraph:paragraph+1]
    text=" ".join("".join(t.text or "" for t in p.iter(f"{{{anim.A}}}t")) for p in paras)
    return max(1,len(text.split()) if by=="word" else len(text.replace(" ","")))
