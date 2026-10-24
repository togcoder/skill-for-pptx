# Cross-Slide Morph Choreography, Pre-Staging Playbook & Pacing Architecture

## 1. Why Passive Auto-Morph Fails (Red-Team Diagnostics)
1. **Unstaged Ghosting (X-Ray Fade-In)**: Multi-part assemblies (`Walker1:*`, `Engine1:*`) without a pre-staged twin on Slide $k-1$ cross-dissolve in place (`alpha = 0 -> 1`), exposing overlapping internal joints.
2. **Flat Disappearance (In-Place Fade-Out)**: Outgoing background objects without a post-staged twin on Slide $k$ fade out flatly in place while foreground elements pan.
3. **Uniform Linear Velocity**: Identical travel distances across a single transition `dur_ms` cause robotic simultaneous arrival.
4. **Custom Geometry Winding & Multi-Hole Fallback**: Per official Microsoft Morph rules, PowerPoint cannot geometrically morph a shape with more than one hole, and requires identical clockwise vertex winding and aligned starting vertices.

## 2. The 6 Pro Morph Playbook Techniques (`stage_cross_slide_morph_twins`)
1. **Off-Canvas Pre-Staging (`pre_stage` mode: `"off-left" | "off-right" | "off-top" | "off-bottom"`)**
2. **Velocity Staggering via Off-Canvas Distance (`stagger_dist`, `stagger_parts: true`)**
3. **Portal-Seed Expansion (`pre_stage` mode: `"portal-seed"`, `portal: "!!hero-orb"`, `scale: 0.08..0.15`, `alpha: 0.02`)**
4. **Telescopic Stack Unfolding (`pre_stage` mode: `"telescopic-stack"`, `portal: "!!node-3"`)**
5. **Off-Canvas Camera Sweep Post-Staging (`post_stage` mode: `"off-left" | "off-bottom"`)**
6. **Corner-Badge Context Mini-Map (`post_stage` mode: `"corner-badge"`, `scale: 0.20`, `alpha: 0.42`)**
