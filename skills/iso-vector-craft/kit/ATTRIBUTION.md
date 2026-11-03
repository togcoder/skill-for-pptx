# Attribution — Anatomy kit

The files in this folder are vendored from **Anatomy**:

- Source: <https://github.com/wheresryan22/anatomy>
- Author: Ryan
- Licence: MIT (see `LICENSE` in this folder)
- Commit: `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`
  (2026-10-18, "Printable sheets: A4 and Letter PDFs from any figure (#126)")
- Vendored on: 2026-11-03

| File | Upstream path | Status |
|---|---|---|
| `iso-kit.mjs` | `kit/iso-kit.mjs` | unmodified |
| `tube.mjs` | `kit/tube.mjs` | unmodified |
| `lathe.mjs` | `kit/lathe.mjs` | unmodified |
| `iso.css` | `kit/iso.css` | unmodified |
| `LICENSE` | `LICENSE` | unmodified |

`product-svg.mjs` is **not** from Anatomy. It is this lab's export wrapper
(T056): it bakes the light palette into literal values, adds `<title>/<desc>`
and pins a real font family so the SVG survives editors and rasterisers that
do not resolve CSS custom properties.

The upstream `SKILL.md`, `references/` and examples are **not** vendored;
this skill documents only the subset used for product illustration. Read the
upstream docs for the full kit (WebGL, 3D turn, print sheets, audits).

Reference photos used to design the examples are cited in
`experiments/T056-20261103-opencode-iso-vector/REPORT.md` and are not
redistributed with this skill.
