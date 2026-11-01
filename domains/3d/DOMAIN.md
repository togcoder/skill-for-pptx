# Domain: 3d (3D Solid Modeling & PBR Rendering)

## Scope
Parametric 3D solid modeling (CSG, B-Rep, STEP), lighting setups, and physically-based rendering (glTF 2.0 PBR, LightCraft snapshots) using SolidCraft and LightCraft.

## Thesis
Realistic 3D CAD models and professional product renders require:
1. Grounding and metric scale: $1.0\text{ unit} = 1.0\text{ mm}$ for product assemblies, right-handed Y-up orientation for glTF with pivot at bottom center ($\min(Y) = 0.0$).
2. The No-Sharp-Edge Law: Physical parts always possess micro-bevels ($R = 0.2 - 0.5\text{ mm}$) to capture specular catchlights.
3. Concentric wall thickness preservation: $R_{\text{in}} = \max(0.5\text{ mm}, R_{\text{out}} - T)$.
4. Geometric camera framing: True Isometric ($45^\circ$ azimuth, $\arctan(1/\sqrt{2}) \approx 35.264^\circ$ elevation, 70–78% framing fill) and Product Hero ($50-85\text{ mm}$ perspective without barrel distortion).
5. Calibrated 3-Point Studio Lighting: Key light (1.00 intensity, 5500K), Fill light (2:1 ratio for technical clarity, 4:1 for dramatic product hero), Rim light (0.8–1.5 intensity for subject-background separation).
6. Strict PBR albedo and metalness rules: Dielectric ($M=0.0$, IOR $1.50$) vs Conductor ($M=1.0$), with a total ban on ambiguous metalness $M \in [0.2, 0.8]$.

## Native canon and sources
- ISO 10303: Standard for the Exchange of Product model data (STEP).
- Khronos glTF 2.0 PBR Metallic-Roughness Specification.
- `knowledge/3d_solid_canon.json`: formal machine-readable specification.

## Owners and reviewers
- Author: Antigravity + Argon (Gemini 4).
- Peer reviewers: Claude, OpenCode.

## Code (canonical / experimental)
| Module | Status | Tests |
|---|---|---|
| `scripts/multi_domain_canons.py` | Canonical (T042): Micro-bevel, concentric fillet, isometric elevation, 3-point lighting, PBR validator | `tests/test_multi_domain_canons.py` |
| `scripts/solidcraft_bridge.py` | Experimental (T042): SolidCraft headless CLI runner | `tests/test_multi_domain_canons.py` |

## Data
- `knowledge/3d_solid_canon.json`: Metric coordinate system, micro-bevel formula, lighting geometry, PBR albedo ranges.

## Evidence ladder
| Rung | Tool | Meaning |
|---|---|---|
| 0 | Python test suite | Mathematical formulas and token validation |
| 1 | `solidcraft-cli.exe eval` | Geometry, volume, surface area, and manifold validity |
| 3 | `solidcraft-cli.exe snapshot` | Headless CPU/GPU rasterized PNG snapshot |
| 4 | `solidcraft-cli.exe render` / LightCraft | Ray-traced / PBR image synthesis |
| 5 | CAD software (FreeCAD, Fusion 360) | STEP/B-Rep geometric interchange verification |

## State (2026-11-01)
- 3D design canon defined in `knowledge/3d_solid_canon.json`.
- Parametric calculations and PBR validators implemented in `scripts/multi_domain_canons.py`.
- SolidCraft native bridge implemented in `scripts/solidcraft_bridge.py` connecting to `D:\artcraft\SolidCraft\solidcraft-cli.exe`.
