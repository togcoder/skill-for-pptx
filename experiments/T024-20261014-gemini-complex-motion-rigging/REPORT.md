# T024 — Deep Complex Motion Research, Transitive Multi-Part Rigging & 178-Shape Architectural Showcase

- **Task ID**: `T024`
- **Branch**: `work/T024-gemini-20261014`
- **Date**: `2026-10-14`
- **Agent**: `gemini`
- **PowerPoint Native Playback Verified**: `false` (OOXML schema + LibreOffice ODP import + 5/5 pixel-identical static render verified; native desktop PowerPoint playback remains unverified per `AGENTS.md`).

## 1. Why Simple Geometric Demos Were No Longer Enough
Earlier showcase decks used single-shape boxes (`1 card = 1 shape`). Real-world technical and architectural presentations have **multi-part composite widgets** (chassis card + header accent bar + vector icon + title + subtitle/spec text + metric badge), **3D spatial depth**, **layered hardware stacks**, and **concurrent packet streams**.

When a single-shape animation engine moves a card without transitive multi-part rigging and secondary follow-through inertia, either:
1. The sub-shapes get left behind (tearing the visual widget apart), or
2. Every sub-shape moves with rigid robotic lockstep (`0 ms` lag), lacking physical weight and overlapping action.

## 2. Core Engine Innovations Implemented (`scripts/motion_engine.py`, `scripts/pptx_animator.py`, `scripts/motion_director.py`, `scripts/validate_director_plan.py`)

1. **Transitive Multi-Part Virtual Rigging (`detect_virtual_rigs(objects, transitive=True)`) & Secondary Follow-Through Inertia (`follow_through_ms`)**:
   - Automatically binds multi-element visual assemblies (up to 6+ native shapes per pod/layer: chassis, header bar, geometric icon, title, spec text, status badge) without brittle `<p:grpSp>` flattening.
   - Caps carrier area (`0.0015 < area < 0.22`) so full-slide background panels never swallow an entire slide as a single rig.
   - Adds `follow_through_ms` in `expand_rig_tracks`: child shapes sorted by area/top-to-bottom lag the carrier by `(child_idx + 1) * follow_through_ms`, creating physical overlapping action (chassis moves first, header bar and icon follow `+22ms..+44ms`, text and badge settle `+66ms..+110ms` later) and propagating scale/opacity modulations to children.
2. **3D Perspective Elliptical Carousel (`orbit-3d` Recipe)**:
   - Revolves multi-part pods around a tilted 2.5D elliptical plane (`radius_x`, `radius_y`, `tilt_deg`) while dynamically modulating `scale` (`1.0 + depth_scale * sin(theta)`) and `opacity` (`depth_dim` in the back half, `1.0` in the foreground) at every step.
3. **Isometric & Vertical Multi-Strata Stack Disassembly (`explode-layers` Recipe)**:
   - Separates overlapping or tightly stacked multi-part architectural strata (Silicon Die, HBM3e Interposer, Tensor Core Mesh, KV-Cache Fabric, Compiler Runtime) along `"y"`, `"x"`, or `"iso"` (diagonal isometric) axes with `bounce_end` (`p14:bounceEnd`) and per-sub-shape `follow_through_ms` inertia, then optionally reassembles (`reassemble: true`).
4. **Concurrent Braided Packet Swarm & Synchronized Node Reactions (`cascade-flow` Recipe)**:
   - Launches `token_count` concurrent packets staggered by `stagger_ms` along multi-hop alternating cubic Bézier `poly_path` arcs through an arbitrary chain of stage nodes (`token_spread_x` horizontal fan-out so packets land side-by-side without overlapping).
   - Calculates exact per-hop arrival timestamps `(stage_idx + 1) * hop_ms` and injects synchronized `pulse` scale pops + `color` (`<p:animClr>`) flashes on each stage node at the exact millisecond each packet lands.
5. **Single-Element Multi-Segment `<p:animMotion>` (`poly_path` / `via`) & Auto-Arc Collision Avoidance (`resolve_trajectory_collisions`)**:
   - Emits a single `<p:animMotion path="M ... C ... L ...">` element per continuous movement sequence instead of conflicting consecutive `<p:animMotion>` tags.
   - Sweeps moving bounding boxes (`sample_scene_states` at 50ms intervals) against stationary obstacles and automatically bends linear trajectories into quadratic Bézier arcs (`auto_avoid: true`) around obstacles.
6. **Extended OOXML Native Primitives & Interactive Triggers**:
   - `<p:animClr>` (`color`), `<p:animRot>` (`teeter`), `repeatCount` (`repeat`), `autoRev` (`auto_reverse`), `p14:bounceEnd` (`bounce_end`), and `<p:interactiveSeq>` shape-click triggers (`trigger_shape` / `trigger_spid`).
   - Morph `empty_placeholders()` sanitizer (inspired by `mslides` Issue #4) and pure-Python `Pillow` storyboard/GIF renderer (`motion_preview.py`).

## 3. Bugs Caught & Fixed via Visual Inspection of Rendered Storyboards
1. **Spotlight Position Reset Bug (`motion_engine.py`)**: Previously, `spotlight` checked `if abs(st.dx) > 1e-4 or abs(st.dy) > 1e-4` on `others` and reset their `dx=0, dy=0` while dimming them. When applied after `orbit-3d` or `cycle`, all non-spotlighted pods snapped back to their original coordinates and collided with the spotlighted pod. Fixed so `spotlight` only dims opacity and resets enlarged scale (`st.scale > 1.02`) while preserving current `dx, dy` positions.
2. **Pure Anchor Keyframe Timestamp Initialization (`compile_track`)**: When `expand_rig_tracks` or `disperse` inserted a delayed anchor keyframe `{"t": t0}` (`t0 > 0`) before a movement keyframe `{"t": t1, "dx": ...}`, `pos_time` remained `None`, causing the compiled segment to start at `0ms` instead of `t0`. Fixed by initializing `pos_time`, `scale_time`, and `rot_time` on pure anchor keyframes.

## 4. 5-Slide, 178-Shape Showcase Verification & Hashes

Reproduce via:
```bash
python3 experiments/T024-20261014-gemini-complex-motion-rigging/build_t024_showcase.py
python3 -m unittest discover -s tests -v
```

| Artifact | Slide Count | Total Native Shapes | SHA-256 |
|---|---:|---:|---|
| `output/T024_complex_motion_source.pptx` | 5 | 178 | `6199128bb1712c0fad2d0d5de34d200bb73f8856f3695820be754d8e811ac81d` |
| `output/T024_complex_motion_directed.pptx` | 5 | 178 | `f6ee7775369601885f26c82d7ab8d6de05903b767551fc342dde65665c9a4cb9` |
| `output/T024_complex_motion_auto.pptx` | 5 | 178 | `1ff86ef67874ca0961461192ed296b73057d2faeac4ce42a8dddccc454ce927c` |

- **Static Render Identity (`render-identity-directed.json`)**: `identical_slides: 5/5` (`changed_pixels: 0` on all 5 slides).
- **LibreOffice ODP Cross-Check (`lo-crosscheck-directed.json`)**: `odp_convert_ok: true`, `slides_with_Extract_animations: 4` (Slide 4 uses `<p:transition><p159:morph option="byObject"/></p:transition>`).
- **Unit Test Suite (`unit-tests.txt`)**: `Ran 199 tests in 109.327s — OK` (`0` failures, `0` skipped).
