#!/usr/bin/env python3
"""Compound motion engine for existing PowerPoint objects (T023).

Three layers:

1. Keyframe tracks -> native effects.  A track animates one existing object
   through keyframes (position, scale, rotation, opacity, visibility).  Each
   changed property between two keyframes becomes one native PowerPoint
   effect (custom motion path, Grow/Shrink, Spin, Transparency, entrance/exit)
   with an exact delay, so many objects can move concurrently inside one
   presenter click.  State (offset, scale, rotation, opacity, visibility) is
   carried across clicks so chained paths stay continuous.

2. Choreography recipes -> tracks.  spotlight, release, assemble, disperse,
   cycle, swap, travel and zoom-focus use the objects' authored geometry, so
   an AI can ask for "walk the cycle" instead of computing coordinates.

3. Simulation.  The same semantics evaluate any effect list at any time; the
   preview renderer and the verifier use it to draw frames and find
   occlusion/out-of-bounds problems.

Native semantics assumed (hypotheses until PowerPoint playback, see T006
"anchored-hold" matrix): motion paths are offsets from the authored layout
position and hold their end; Grow/Shrink ``by`` compounds on the current size;
Spin compounds; Transparency holds until another Transparency on the object.
"""
import math

try:
    from . import pptx_animator as anim
except ImportError:
    import pptx_animator as anim

PROPS=("pos","scale","rot","opacity","visible")
ENTER_DEFAULT=("fade",400)
EXIT_DEFAULT=("fade-out",400)


# ---------------------------------------------------------------------------
# Object state


def authored(obj):
    g=obj["geometry"]
    return {"cx":g["x"]+g["w"]/2,"cy":g["y"]+g["h"]/2,"w":g["w"],"h":g["h"]}


def fresh_state(visible=True):
    return {"dx":0.0,"dy":0.0,"scale":1.0,"rot":0.0,"opacity":1.0,"visible":visible,"alpha":1.0}


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
    a=eff.get("accel",0.5 if eff["preset"]=="path" else 0)
    d=eff.get("decel",0.5 if eff["preset"]=="path" else 0)
    if a or d:
        return p*p*(3-2*p)
    return p


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
    target=p*total
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
    elif preset=="dim":
        target=eff.get("opacity",0.35)
        state["opacity"]=base["opacity"]+(target-base["opacity"])*min(1.0,p*4)


def state_at(states,effects,t):
    """States after running one click group's effects up to time t."""
    out={k:dict(v) for k,v in states.items()}
    hidden_paras=set()
    for start,end,eff in sorted(schedule(effects),key=lambda x:x[0]):
        if t<start or eff["spid"] not in out:
            continue
        dur=max(1,end-start)
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


def compile_track(track,obj,objects_by_token,state,beat_id):
    """Compile one track into effects (delays relative to the beat start).

    state: the object's state at the beat start; it is not mutated here.
    Keyframe keys: t (ms, required), position via x/y | dx/dy | to (+curve),
    scale, rotate (deg, absolute vs authored), opacity, visible
    (+enter/exit preset, enter_ms), ease (linear|smooth|in|out).
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
    n=[0]

    def eff(preset,start,dur,**kw):
        n[0]+=1
        e={"preset":preset,"spid":spid,"trigger":"with","delay_ms":int(round(start)),
           "duration_ms":int(round(max(0,dur))),"beat":f"{beat_id}:{spid}:{n[0]}"}
        e.update(kw)
        effects.append(e)
        return e

    cur_opacity=state["opacity"]
    for kf in kfs:
        t=kf["t"]
        ease=EASE.get(kf.get("ease","smooth"))
        if ease is None:
            raise ValueError(f"unknown ease {kf.get('ease')!r}")
        entering=kf.get("visible") is True and not visible
        if entering:
            preset,ms=kf.get("enter",ENTER_DEFAULT[0]),kf.get("enter_ms",ENTER_DEFAULT[1])
            if preset not in anim.ENTRANCES:
                raise ValueError(f"enter preset {preset!r} is not an entrance")
            eff(preset,t,ms)
            visible=True
        target=_resolve_point(kf,obj,objects_by_token,cur_pos)
        if target is not None:
            jump=kf.get("jump") or (pos_time is None and entering)
            if math.dist(target,cur_pos)>1e-9:
                if jump:
                    if visible and not entering:
                        eff("path",t,1,anchored=[{"x":cur_pos[0],"y":cur_pos[1]},{"x":target[0],"y":target[1]}])
                else:
                    seg_start=pos_time if pos_time is not None else 0
                    if t<=seg_start:
                        raise ValueError(f"{obj['name']!r}: position keyframe at t={t} needs time to move (use jump)")
                    seg={"x":target[0],"y":target[1]}
                    if kf.get("curve"):
                        c1,c2=_arc_controls(cur_pos,target,kf["curve"])
                        seg["c1"]={"x":c1[0],"y":c1[1]}
                        seg["c2"]={"x":c2[0],"y":c2[1]}
                    elif "controls" in kf:
                        seg["c1"],seg["c2"]=kf["controls"]
                    eff("path",seg_start,t-seg_start,anchored=[{"x":cur_pos[0],"y":cur_pos[1]},seg],
                        accel=ease[0],decel=ease[1])
            cur_pos=target
            pos_time=t
        if "scale" in kf:
            new=float(kf["scale"])
            if new<=0:
                raise ValueError("scale must be positive")
            seg_start=scale_time if scale_time is not None else 0
            if abs(new-cur_scale)>1e-9:
                eff("grow",seg_start,max(1,t-seg_start),ratio=new/cur_scale,accel=ease[0],decel=ease[1])
                cur_scale=new
            scale_time=t
        if "rotate" in kf:
            new=float(kf["rotate"])
            seg_start=rot_time if rot_time is not None else 0
            if abs(new-cur_rot)>1e-9:
                eff("spin",seg_start,max(1,t-seg_start),by_deg=new-cur_rot,accel=ease[0],decel=ease[1])
                cur_rot=new
            rot_time=t
        if "opacity" in kf:
            value=float(kf["opacity"])
            if not 0<=value<=1:
                raise ValueError("opacity must be within 0..1")
            if abs(value-cur_opacity)>1e-9:
                eff("dim",t,kf.get("opacity_ms",400),opacity=value)
                cur_opacity=value
        if kf.get("visible") is False and visible:
            preset,ms=kf.get("exit",EXIT_DEFAULT[0]),kf.get("exit_ms",EXIT_DEFAULT[1])
            if preset not in anim.EXITS:
                raise ValueError(f"exit preset {preset!r} is not an exit")
            eff(preset,t,ms)
            visible=False
    return effects


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
        tracks.append({"target":focus,"keyframes":[{"t":0},kf]})
        if states[focus["id"]]["opacity"]<1:
            tracks[-1]["keyframes"][0]["opacity"]=1.0
        for o in others:
            if states[o["id"]]["visible"]:
                tracks.append({"target":o,"keyframes":[{"t":0,"opacity":float(params.get("dim",0.35))}]})
                if states[o["id"]]["scale"]!=1.0 or states[o["id"]]["dx"] or states[o["id"]]["dy"]:
                    tracks[-1]["keyframes"]+= [{"t":0,"dx":states[o["id"]]["dx"],"dy":states[o["id"]]["dy"],
                                                "scale":states[o["id"]]["scale"]},
                                               {"t":d,"dx":0,"dy":0,"scale":1.0}]
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
                tracks.append({"target":o,"keyframes":[
                    {"t":t0,"dx":off[0],"dy":off[1],"jump":True,"visible":True,"enter":params.get("enter","fade"),"enter_ms":min(d,500)},
                    {"t":t0+d,"dx":0.0,"dy":0.0,"ease":"out"}]})
            else:
                tracks.append({"target":o,"keyframes":[
                    {"t":t0},
                    {"t":t0+d,"dx":off[0],"dy":off[1],"ease":"in"},
                    {"t":t0+d,"visible":False,"exit":params.get("exit","fade-out"),"exit_ms":min(d,400)}]})
                # exit starts slightly before the move ends
                tracks[-1]["keyframes"][2]["t"]=max(t0,t0+d-min(d,400))
    elif recipe=="cycle":
        if len(objs)<3:
            raise ValueError("cycle needs at least three objects")
        steps=int(params.get("steps",1))
        direction=1 if params.get("direction","forward")=="forward" else -1
        cx,cy=_centroid(objs,states)
        positions=[_pos(o,states) for o in objs]
        n=len(objs)
        for i,o in enumerate(objs):
            a=authored(o)
            kfs=[{"t":0}]
            for k in range(1,steps+1):
                src=positions[(i+direction*(k-1))%n]
                dst=positions[(i+direction*k)%n]
                ang0=math.atan2(src[1]-cy,src[0]-cx)
                ang1=math.atan2(dst[1]-cy,dst[0]-cx)
                delta=(ang1-ang0+math.pi)%(2*math.pi)-math.pi
                r=(math.dist(src,(cx,cy))+math.dist(dst,(cx,cy)))/2
                kk=4/3*math.tan(delta/4)
                c1=(src[0]-kk*r*math.sin(ang0),src[1]+kk*r*math.cos(ang0))
                c2=(dst[0]+kk*r*math.sin(ang1),dst[1]-kk*r*math.cos(ang1))
                kfs.append({"t":k*d,"dx":dst[0]-a["cx"],"dy":dst[1]-a["cy"],
                            "controls":[{"x":c1[0]-a["cx"],"y":c1[1]-a["cy"]},{"x":c2[0]-a["cx"],"y":c2[1]-a["cy"]}]})
            tracks.append({"target":o,"keyframes":kfs})
    elif recipe=="swap":
        if len(objs)!=2:
            raise ValueError("swap needs exactly two objects")
        a,b=objs
        pa,pb=_pos(a,states),_pos(b,states)
        arc=float(params.get("arc",0.25))
        tracks.append({"target":a,"keyframes":[{"t":0},{"t":d,"x":pb[0],"y":pb[1],"curve":arc}]})
        tracks.append({"target":b,"keyframes":[{"t":0},{"t":d,"x":pa[0],"y":pa[1],"curve":arc}]})
    elif recipe=="travel":
        token,stops=objs[0],objs[1:]
        if not stops:
            raise ValueError("travel needs a token and at least one stop")
        dwell=int(params.get("dwell_ms",250))
        kfs=[{"t":0}]
        t=0
        for stop in stops:
            sx,sy=_pos(stop,states)
            t+=d
            kf={"t":t,"x":sx+float(params.get("offset_x",0)),"y":sy+float(params.get("offset_y",0)),
                "curve":float(params.get("arc",0.0))}
            kfs.append(kf)
            t+=dwell
        tracks.append({"target":token,"keyframes":kfs})
        if params.get("pulse_stops",True):
            for i,stop in enumerate(stops):
                tracks.append({"target":stop,"pulse_at":(i+1)*d+i*dwell})
    elif recipe=="zoom-focus":
        focus,others=objs[0],objs[1:]
        fill=float(params.get("fill",0.6))
        scale=float(params.get("scale",_fit_scale(focus,fill)))
        tracks.append({"target":focus,"keyframes":[{"t":0},{"t":d,"x":float(params.get("x",0.5)),
                                                           "y":float(params.get("y",0.5)),"scale":scale}]})
        for o in others:
            if states[o["id"]]["visible"]:
                tracks.append({"target":o,"keyframes":[{"t":0,"visible":False,"exit":"fade-out","exit_ms":min(d,400)}]})
    else:
        raise ValueError(f"unknown recipe {recipe!r}")
    return tracks


RECIPES=("spotlight","release","assemble","disperse","cycle","swap","travel","zoom-focus")


def compile_choreography(recipe,objs,states,objects_by_token,beat_id,params=None,tracks=None):
    """Return effects (delays relative to the beat start) for a recipe or raw
    tracks. ``objs`` are resolved objects; raw ``tracks`` use {"target": obj}."""
    if recipe=="tracks":
        built=tracks
    else:
        built=recipe_tracks(recipe,objs,states,params)
    effects=[]
    for track in built:
        obj=track["target"]
        if "pulse_at" in track:
            effects.append({"preset":"pulse","spid":obj["id"],"trigger":"with","delay_ms":int(track["pulse_at"]),
                            "duration_ms":200,"scale":1.08,"beat":f"{beat_id}:{obj['id']}:pulse"})
            continue
        effects.extend(compile_track(track,obj,objects_by_token,states[obj["id"]],beat_id))
    if not effects:
        raise ValueError(f"{recipe}: nothing changes from the current state")
    effects.sort(key=lambda e:e["delay_ms"])
    return effects


# ---------------------------------------------------------------------------
# Checks


PROP_OF={"path":"pos","grow":"scale","pulse":"scale","zoom":"scale","spin":"rot","dim":"opacity"}


def conflicts(effects):
    """Overlapping animations of the same property on the same object."""
    found=[]
    spans={}
    for start,end,eff in schedule(effects):
        if eff.get("paragraph") is not None or eff.get("chart") is not None:
            continue
        prop=PROP_OF.get(eff["preset"])
        if prop is None or prop=="opacity":
            continue
        key=(eff["spid"],prop)
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
    vis=[o for o in objects if o.get("geometry") and states.get(o["id"],{}).get("visible")]
    for o in vis:
        b=bbox(o,states[o["id"]])
        if b[0]<-0.02 or b[1]<-0.02 or b[2]>1.02 or b[3]>1.02:
            warn.append(f"{label}: {o['name']!r} extends outside the slide")
    moved=[o for o in vis if any(abs(states[o["id"]][k]-v)>1e-6 for k,v in (("dx",0),("dy",0),("scale",1)))]
    for o in moved:
        bo=bbox(o,states[o["id"]])
        for other in vis:
            if other is o:
                continue
            bt=bbox(other,states[other["id"]])
            before=_overlap(bbox(o,fresh_state()),bbox(other,fresh_state()))
            now=_overlap(bo,bt)
            smaller=min((bo[2]-bo[0])*(bo[3]-bo[1]),(bt[2]-bt[0])*(bt[3]-bt[1])) or 1
            if now-before>0.15*smaller and states[other["id"]]["opacity"]>0.5 and states[o["id"]]["opacity"]>0.5:
                warn.append(f"{label}: {o['name']!r} now covers {other['name']!r}")
    return sorted(set(warn))


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
        groups.append(effects)
    return groups,autos


def _delay(ctn):
    cond=ctn.find(f"{{{anim.P}}}stCondLst/{{{anim.P}}}cond")
    try:
        return int(cond.get("delay")) if cond is not None and cond.get("delay") not in (None,"indefinite") else 0
    except ValueError:
        return 0


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
    elif scale is not None:
        by=scale.find("p:by",NS)
        inner=scale.find("p:cBhvr/p:cTn",NS)
        ratio=int(by.get("x"))/100000 if by is not None else 1.0
        if inner is not None and inner.get("autoRev")=="1":
            eff["preset"]="pulse"
            eff["scale"]=ratio
        else:
            eff["preset"]="grow"
            eff["ratio"]=ratio
    elif rot is not None:
        eff["preset"]="spin"
        eff["by_deg"]=int(rot.get("by","0"))/60000
    elif ctn.find(".//p:set/p:cBhvr/p:attrNameLst[p:attrName='style.opacity']",NS) is not None:
        val=ctn.find(".//p:set/p:to/p:strVal",NS)
        eff["preset"]="dim"
        eff["opacity"]=float(val.get("val")) if val is not None else 0.35
        eff["duration_ms"]=400
    else:
        return None
    return eff
