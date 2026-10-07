#!/usr/bin/env python3
"""Validate an existing-deck motion-director plan against a deck inventory."""
import argparse
import json
from pathlib import Path
import math

try:
    from .data_motion_recipes import chart_motion_recipe, number_counter_recipe
except ImportError:
    from data_motion_recipes import chart_motion_recipe, number_counter_recipe

SCRIPT_SOURCES={"provided","speaker-notes","existing-timing","inferred","researched"}
TIMING={"on-click","with-previous","after-previous"}
PAUSE_AFTER={"presenter-explanation","await-next-reveal","slide-complete","none"}
COMPONENT_KINDS={"shape","text","connector","derived-visual"}
PROVENANCE={"none","derived-from-source","synthetic-nondata","user-provided"}
CHART_BUILDS={"as-whole","series","category","series-elements","category-elements"}
COUNTER_IMPLEMENTATIONS={"odometer-proxy","stepped-text"}
COUNTER_OPERATIONS={"kpi-highlight","hero-metric","number-counter","metric-highlight"}
GENERIC_OPERATIONS={"reveal","stagger-reveal","process-reveal","focus","emphasize","move","rotate"}
# Director v0.5 (T019): canonical PowerPoint presets, paragraph builds, exits,
# dimming and an automatic first group.
V05_OPERATIONS=GENERIC_OPERATIONS|{"text-build","exit","dim"}
V05_EFFECTS={"appear","fade","float-in","zoom","wipe-up","wipe-down","wipe-left","wipe-right",
             "disappear","fade-out","pulse","spin","dim","path"}


def _library_effect(name):
    """Any PowerPoint-authored preset from knowledge/powerpoint_presets.json ("ppt:<name>")."""
    if not str(name).startswith("ppt:"):
        return False
    lib=Path(__file__).resolve().parents[1]/"knowledge"/"powerpoint_presets.json"
    return lib.is_file() and name[4:] in {p["name"] for p in json.loads(lib.read_text(encoding="utf-8"))["presets"]}


CHOREOGRAPHY_RECIPES={"spotlight":(1,None),"release":(1,None),"assemble":(1,None),"disperse":(1,None),
                      "cycle":(3,None),"swap":(2,2),"travel":(2,None),"zoom-focus":(1,None),"ken-burns":(1,None),"float":(1,None),"tracks":(0,None)}
KEYFRAME_KEYS={"t","x","y","dx","dy","to","curve","controls","jump","scale","rotate","opacity","opacity_ms",
               "visible","enter","enter_ms","exit","exit_ms","ease"}


def _choreography_errors(beat,targets):
    errors=[]
    recipe=beat.get("recipe")
    if recipe not in CHOREOGRAPHY_RECIPES:
        return [f"unknown choreography recipe {recipe!r}"]
    low,high=CHOREOGRAPHY_RECIPES[recipe]
    n=len(targets) if isinstance(targets,list) else 0
    if n<low or (high is not None and n>high):
        errors.append(f"recipe {recipe} needs {low}{'' if high==low else '+' if high is None else f'..{high}'} targets, got {n}")
    params=beat.get("motion_parameters",{})
    if not isinstance(params,dict):
        errors.append("motion_parameters must be an object")
    if recipe=="tracks":
        tracks=beat.get("tracks")
        if not isinstance(tracks,list) or not tracks:
            errors.append("tracks recipe requires a nonempty tracks list")
        else:
            for tr in tracks:
                if not isinstance(tr,dict) or not isinstance(tr.get("target"),str):
                    errors.append("each track needs a target name")
                    continue
                if tr["target"] not in (targets or []):
                    errors.append(f"track target {tr['target']!r} must also be listed in targets")
                kfs=tr.get("keyframes")
                if not isinstance(kfs,list) or not kfs:
                    errors.append(f"track {tr['target']!r} needs keyframes")
                    continue
                for kf in kfs:
                    if not isinstance(kf,dict) or type(kf.get("t")) not in (int,float) or kf["t"]<0:
                        errors.append(f"track {tr['target']!r}: keyframe t must be a nonnegative number")
                        break
                    unknown=set(kf)-KEYFRAME_KEYS
                    if unknown:
                        errors.append(f"track {tr['target']!r}: unknown keyframe keys {sorted(unknown)}")
                        break
    return errors


def _transition_errors(plan,inventory):
    errors=[]
    transitions=plan.get("transitions")
    if transitions is None:
        return errors
    if plan.get("version")!="0.6":
        return ["transitions require Director v0.6"]
    if not isinstance(transitions,list):
        return ["transitions must be a list"]
    count=len(inventory.get("slides",[]))
    seen=set()
    for tr in transitions:
        if not isinstance(tr,dict):
            errors.append("transition must be an object")
            continue
        slide=tr.get("slide")
        if type(slide) is not int or not 2<=slide<=count:
            errors.append(f"transition slide must be 2..{count}")
        elif slide in seen:
            errors.append(f"duplicate transition for slide {slide}")
        seen.add(slide)
        if tr.get("kind")!="morph":
            errors.append(f"transition kind {tr.get('kind')!r} unsupported (morph only)")
        if not isinstance(tr.get("reason"),str) or not tr["reason"].strip():
            errors.append(f"transition to slide {slide} needs a reason (which objects continue)")
        dur=tr.get("duration_ms",1500)
        if type(dur) is not int or not 300<=dur<=5000:
            errors.append(f"transition to slide {slide}: duration_ms must be 300..5000")
    return errors


def validate(plan,inventory):
    errors=[]
    if not isinstance(plan,dict):
        return ["plan must be an object"]
    required={"version","kind","source","user_instruction","script","preservation",
              "slides","target_slide_count","research_metadata"}
    errors += [f"missing field: {k}" for k in sorted(required-plan.keys())]
    if errors:
        return errors
    if plan["version"] not in ("0.1","0.2","0.3","0.4","0.5","0.6"):
        errors.append("version must be 0.1, 0.2, 0.3, 0.4, 0.5 or 0.6")
    if plan["kind"]!="existing-deck-motion-director":
        errors.append("kind must be existing-deck-motion-director")

    source=plan["source"]
    if not isinstance(source,dict):
        errors.append("source must be an object")
    else:
        if source.get("pptx_sha256")!=inventory.get("source_sha256"):
            errors.append("source.pptx_sha256 does not match inventory")
        if source.get("inventory_version")!=inventory.get("version"):
            errors.append("source.inventory_version does not match inventory")
        if source.get("source_slide_count")!=len(inventory.get("slides",[])):
            errors.append("source.source_slide_count does not match inventory")

    script=plan["script"]
    if not isinstance(script,dict):
        errors.append("script must be an object")
    else:
        if script.get("source") not in SCRIPT_SOURCES:
            errors.append("unsupported script.source")
        if not isinstance(script.get("summary"),str) or not script["summary"].strip():
            errors.append("script.summary must be nonempty")
        evidence=script.get("evidence")
        if not isinstance(evidence,list) or not evidence or any(not isinstance(x,str) or not x.strip() for x in evidence):
            errors.append("script.evidence must be a nonempty text list")
        beats=script.get("beats")
        if not isinstance(beats,list) or not beats:
            errors.append("script.beats must be nonempty")
        if script.get("source")=="researched":
            sources=plan.get("research_metadata",{}).get("sources")
            if not isinstance(sources,list) or not sources:
                errors.append("researched script requires research_metadata.sources")

    preservation=plan["preservation"]
    if not isinstance(preservation,dict):
        errors.append("preservation must be an object")
    else:
        for key in ("preserve_text_by_default","preserve_media_by_default",
                    "preserve_theme_by_default","preserve_slide_order_by_default"):
            if type(preservation.get(key)) is not bool:
                errors.append(f"preservation.{key} must be boolean")
        policy=preservation.get("slide_count_policy")
        if policy not in ("preserve","explicit-change"):
            errors.append("unsupported preservation.slide_count_policy")
        elif policy=="preserve" and plan["target_slide_count"]!=len(inventory.get("slides",[])):
            errors.append("target_slide_count must equal source when slide_count_policy=preserve")

    inv_slides={s["index"]:s for s in inventory.get("slides",[])}
    plans=plan["slides"]
    if not isinstance(plans,list) or not plans:
        if plan.get("version")=="0.6" and isinstance(plans,list) and plan.get("transitions"):
            return errors+_transition_errors(plan,inventory)  # transitions-only plan
        errors.append("slides must be nonempty")
        return errors

    seen=set()
    for slide in plans:
        if not isinstance(slide,dict):
            errors.append("slide plan must be an object")
            continue
        idx=slide.get("source_index")
        if idx in seen:
            errors.append(f"duplicate source_index: {idx}")
        seen.add(idx)
        inv=inv_slides.get(idx)
        if inv is None:
            errors.append(f"unknown source slide: {idx}")
            continue
        for key in ("role","objective"):
            if not isinstance(slide.get(key),str) or not slide[key].strip():
                errors.append(f"slide {idx}: {key} must be nonempty")

        components=slide.get("components")
        if not isinstance(components,list):
            errors.append(f"slide {idx}: components must be a list")
            components=[]
        component_ids=set()
        for comp in components:
            if not isinstance(comp,dict):
                errors.append(f"slide {idx}: component must be an object")
                continue
            cid=comp.get("id")
            if not isinstance(cid,str) or not cid:
                errors.append(f"slide {idx}: component id must be nonempty")
                continue
            if cid in component_ids:
                errors.append(f"slide {idx}: duplicate component id {cid}")
            component_ids.add(cid)
            if comp.get("native_kind") not in COMPONENT_KINDS:
                errors.append(f"slide {idx}: unsupported component kind {comp.get('native_kind')}")
            if comp.get("data_provenance") not in PROVENANCE:
                errors.append(f"slide {idx}: unsupported component provenance {comp.get('data_provenance')}")
            for key in ("role","rationale","style_basis"):
                if not isinstance(comp.get(key),str) or not comp[key].strip():
                    errors.append(f"slide {idx}: component {cid} missing {key}")
            rationale=(comp.get("rationale") or "").lower()
            if rationale.strip() in ("make it beautiful","make it impressive","đẹp hơn","ấn tượng hơn"):
                errors.append(f"slide {idx}: component {cid} has decorative-only rationale")

        source_targets=set()
        source_shape_by_token={}
        for shape in inv.get("shapes",[]):
            for value in (shape.get("name"),shape.get("forced_semantic_name"),shape.get("id")):
                if isinstance(value,str) and value:
                    source_targets.add(value)
                    source_shape_by_token[value]=shape

        beats=slide.get("beats")
        if not isinstance(beats,list) or not beats:
            errors.append(f"slide {idx}: beats must be nonempty")
            continue
        beat_ids=set()
        for beat in beats:
            if not isinstance(beat,dict):
                errors.append(f"slide {idx}: beat must be an object")
                continue
            bid=beat.get("id")
            if not isinstance(bid,str) or not bid:
                errors.append(f"slide {idx}: beat id must be nonempty")
            elif bid in beat_ids:
                errors.append(f"slide {idx}: duplicate beat id {bid}")
            else:
                beat_ids.add(bid)
            if not isinstance(beat.get("purpose"),str) or not beat["purpose"].strip():
                errors.append(f"slide {idx}: beat {bid} missing purpose")
            if not isinstance(beat.get("operation"),str) or not beat["operation"].strip():
                errors.append(f"slide {idx}: beat {bid} missing operation")
            if beat.get("same_slide") is not True:
                errors.append(f"slide {idx}: beat {bid} must stay on same slide in v0.1")
            if type(beat.get("reuse_existing")) is not bool:
                errors.append(f"slide {idx}: beat {bid} reuse_existing must be boolean")
            first_beat=beats and isinstance(beats[0],dict) and beat is beats[0]
            if plan["version"] in ("0.5","0.6") and first_beat and beat.get("timing_intent")=="on-slide-start":
                pass
            elif beat.get("timing_intent") not in TIMING:
                errors.append(f"slide {idx}: beat {bid} has unsupported timing_intent")
            targets=beat.get("targets")
            if not isinstance(targets,list) or not targets:
                errors.append(f"slide {idx}: beat {bid} targets must be nonempty")
            else:
                allowed=source_targets|component_ids
                missing=[target for target in targets if target not in allowed]
                if missing:
                    errors.append(f"slide {idx}: beat {bid} unknown targets {missing}")

            if plan["version"] in ("0.3","0.4","0.5","0.6") and isinstance(targets,list):
                source_shapes=[source_shape_by_token[t] for t in targets if t in source_shape_by_token]
                chart_shapes=[shape for shape in source_shapes if shape.get("kind")=="chart"]
                number_shapes=[
                    shape for shape in source_shapes
                    if (shape.get("data_semantics") or {}).get("standalone_number")
                ]
                data_motion=beat.get("data_motion")

                if chart_shapes and not isinstance(data_motion,dict) and beat.get("operation")!="choreography":
                    errors.append(f"slide {idx}: beat {bid} targeting chart requires data_motion")
                if beat.get("operation") in COUNTER_OPERATIONS and number_shapes and not isinstance(data_motion,dict):
                    errors.append(f"slide {idx}: beat {bid} highlighted standalone number requires counter data_motion")

                if isinstance(data_motion,dict):
                    kind=data_motion.get("kind")
                    rationale=data_motion.get("rationale")
                    if not isinstance(rationale,str) or not rationale.strip():
                        errors.append(f"slide {idx}: beat {bid} data_motion missing rationale")

                    if kind=="chart":
                        if len(chart_shapes)!=1:
                            errors.append(f"slide {idx}: beat {bid} chart data_motion requires exactly one chart target")
                        else:
                            summary=chart_shapes[0].get("chart_summary")
                            recommended=chart_motion_recipe(summary)
                            inventory_type=(summary or {}).get("primary_type")
                            if data_motion.get("chart_type")!=inventory_type:
                                errors.append(f"slide {idx}: beat {bid} chart_type does not match inventory")
                            build=data_motion.get("build")
                            if build not in CHART_BUILDS:
                                errors.append(f"slide {idx}: beat {bid} unsupported chart build {build}")
                            if type(data_motion.get("animate_background")) is not bool:
                                errors.append(f"slide {idx}: beat {bid} animate_background must be boolean")
                            if recommended:
                                recipe=data_motion.get("recipe")
                                expected_recipe=recommended["recipe"]
                                expected_build=recommended["preferred_build"]
                                override=data_motion.get("override_reason")
                                has_override=isinstance(override,str) and bool(override.strip())
                                normalized_build={
                                    "series-elements":"series-elements",
                                    "category-elements":"category-elements",
                                    "series":"series",
                                    "category":"category",
                                    "as-whole":"as-whole",
                                }.get(build)
                                if recipe!=expected_recipe and not has_override:
                                    errors.append(
                                        f"slide {idx}: beat {bid} chart recipe {recipe} differs from recommended {expected_recipe} without override_reason"
                                    )
                                if normalized_build!=expected_build and not has_override:
                                    errors.append(
                                        f"slide {idx}: beat {bid} chart build {build} differs from recommended {expected_build} without override_reason"
                                    )
                    elif kind=="number-counter":
                        if len(number_shapes)!=1:
                            errors.append(f"slide {idx}: beat {bid} number-counter requires exactly one standalone number target")
                        else:
                            semantics=(number_shapes[0].get("data_semantics") or {}).get("standalone_number")
                            recommended=number_counter_recipe(semantics)
                            if data_motion.get("implementation") not in COUNTER_IMPLEMENTATIONS:
                                errors.append(f"slide {idx}: beat {bid} unsupported counter implementation")
                            for key in ("from_value","to_value"):
                                if type(data_motion.get(key)) not in (int,float):
                                    errors.append(f"slide {idx}: beat {bid} counter {key} must be numeric")
                            if type(data_motion.get("duration_ms")) is not int or data_motion.get("duration_ms",0)<=0:
                                errors.append(f"slide {idx}: beat {bid} counter duration_ms must be positive integer")
                            if type(data_motion.get("steps")) is not int or data_motion.get("steps",0)<2:
                                errors.append(f"slide {idx}: beat {bid} counter steps must be integer >=2")
                            if recommended:
                                if abs(float(data_motion.get("to_value",0))-float(recommended["to_value"]))>1e-9:
                                    errors.append(f"slide {idx}: beat {bid} counter to_value does not match source number")
                                recipe=data_motion.get("recipe")
                                if recipe!=recommended["recipe"] and not (
                                    isinstance(data_motion.get("override_reason"),str)
                                    and data_motion["override_reason"].strip()
                                ):
                                    errors.append(
                                        f"slide {idx}: beat {bid} counter recipe {recipe} differs from source-direction recommendation"
                                    )
                    else:
                        errors.append(f"slide {idx}: beat {bid} unsupported data_motion kind {kind}")

                if plan["version"]=="0.6" and beat.get("operation")=="choreography":
                    errors.extend(f"slide {idx}: beat {bid} {e}" for e in _choreography_errors(beat,targets))
                elif plan["version"] in ("0.5","0.6") and not isinstance(data_motion,dict):
                    operation=beat.get("operation")
                    if operation not in V05_OPERATIONS:
                        errors.append(f"slide {idx}: beat {bid} unsupported v0.5 operation {operation}")
                    effect=beat.get("effect")
                    if effect is not None and effect not in V05_EFFECTS and not _library_effect(effect):
                        errors.append(f"slide {idx}: beat {bid} unsupported effect {effect}")
                    duration=beat.get("duration_ms")
                    if duration is not None and (type(duration) is not int or duration<0 or duration>10000):
                        errors.append(f"slide {idx}: beat {bid} duration_ms must be integer 0..10000")
                    if operation=="text-build":
                        if len(targets)!=1:
                            errors.append(f"slide {idx}: beat {bid} text-build requires exactly one target")
                        paras=beat.get("paragraphs")
                        if paras is not None and (
                            not isinstance(paras,list) or not paras
                            or any(type(p) is not int or p<0 for p in paras)
                        ):
                            errors.append(f"slide {idx}: beat {bid} paragraphs must be nonempty nonnegative integers")
                if plan["version"] in ("0.4","0.5","0.6") and not isinstance(data_motion,dict):
                    operation=beat.get("operation")
                    if operation in GENERIC_OPERATIONS|(V05_OPERATIONS if plan["version"] in ("0.5","0.6") else set()):
                        if chart_shapes:
                            errors.append(
                                f"slide {idx}: beat {bid} generic operation cannot target chart; use chart data_motion"
                            )
                        if operation in ("focus","emphasize","move","rotate") and len(targets)!=1:
                            errors.append(
                                f"slide {idx}: beat {bid} operation {operation} requires exactly one target"
                            )
                        params=beat.get("motion_parameters") or {}
                        if not isinstance(params,dict):
                            errors.append(f"slide {idx}: beat {bid} motion_parameters must be an object")
                        elif operation=="move":
                            points=params.get("points")
                            if not isinstance(points,list) or len(points)<2:
                                errors.append(f"slide {idx}: beat {bid} move requires motion_parameters.points")
                            else:
                                for point in points:
                                    if not isinstance(point,dict) or set(point)!={"x","y"}:
                                        errors.append(f"slide {idx}: beat {bid} invalid move point")
                                        break
                                    if any(
                                        type(point[k]) not in (int,float) or not math.isfinite(point[k])
                                        for k in ("x","y")
                                    ):
                                        errors.append(f"slide {idx}: beat {bid} nonfinite move point")
                                        break
                        elif operation=="rotate":
                            value=params.get("by_deg")
                            if type(value) not in (int,float) or not math.isfinite(value):
                                errors.append(f"slide {idx}: beat {bid} rotate requires finite motion_parameters.by_deg")

        if plan["version"] in ("0.2","0.3","0.4","0.5","0.6"):
            click_beats=slide.get("click_beats")
            if not isinstance(click_beats,list) or not click_beats:
                errors.append(f"slide {idx}: click_beats must be nonempty for v0.2")
            else:
                flattened=[]
                click_ids=set()
                beat_by_id={beat.get("id"):beat for beat in beats if isinstance(beat,dict)}
                for click_index,click in enumerate(click_beats):
                    if not isinstance(click,dict):
                        errors.append(f"slide {idx}: click beat must be an object")
                        continue
                    cid=click.get("id")
                    if not isinstance(cid,str) or not cid:
                        errors.append(f"slide {idx}: click beat id must be nonempty")
                    elif cid in click_ids:
                        errors.append(f"slide {idx}: duplicate click beat id {cid}")
                    else:
                        click_ids.add(cid)
                    for key in ("purpose","stable_state"):
                        if not isinstance(click.get(key),str) or not click[key].strip():
                            errors.append(f"slide {idx}: click beat {cid} missing {key}")
                    if click.get("pause_after") not in PAUSE_AFTER:
                        errors.append(f"slide {idx}: click beat {cid} has unsupported pause_after")
                    reason=click.get("boundary_reason")
                    if click_index>0 and (not isinstance(reason,str) or not reason.strip()):
                        errors.append(f"slide {idx}: click beat {cid} requires boundary_reason")
                    members=click.get("motion_beats")
                    if not isinstance(members,list) or not members:
                        errors.append(f"slide {idx}: click beat {cid} motion_beats must be nonempty")
                        continue
                    flattened.extend(members)
                    for member_index,member in enumerate(members):
                        beat=beat_by_id.get(member)
                        if beat is None:
                            errors.append(f"slide {idx}: click beat {cid} unknown motion beat {member}")
                            continue
                        intent=beat.get("timing_intent")
                        auto_start=(plan["version"] in ("0.5","0.6") and click_index==0 and member_index==0
                                    and intent=="on-slide-start")
                        if member_index==0 and intent!="on-click" and not auto_start:
                            errors.append(f"slide {idx}: click beat {cid} must start with on-click motion beat")
                        if member_index>0 and intent=="on-click":
                            errors.append(f"slide {idx}: click beat {cid} has nested on-click motion beat {member}")
                if flattened!=[beat.get("id") for beat in beats if isinstance(beat,dict)]:
                    errors.append(f"slide {idx}: click_beats must partition motion beats in order exactly once")

    errors.extend(_transition_errors(plan,inventory))
    if preservation.get("slide_count_policy")=="explicit-change":
        changes=plan.get("research_metadata",{}).get("slide_count_changes")
        if not isinstance(changes,list) or not changes:
            errors.append("explicit slide-count change requires research_metadata.slide_count_changes")
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan",type=Path)
    parser.add_argument("inventory",type=Path)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text(encoding="utf-8"))
    inventory=json.loads(args.inventory.read_text(encoding="utf-8"))
    errors=validate(plan,inventory)
    print(json.dumps({"valid":not errors,"errors":errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0


if __name__=="__main__":
    raise SystemExit(main())
