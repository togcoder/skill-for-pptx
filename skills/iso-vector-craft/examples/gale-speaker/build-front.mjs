import { writeFileSync } from "node:fs";
import * as k from "../../kit/iso-kit.mjs";
import { productSvg } from "../../kit/product-svg.mjs";

const W = 820, H = 900;
const CAB = { x: -150, y: -125, w: 300, d: 250, r: 6 };
const BAFFLE = { x: -140, y: 125, w: 280, d: 5, r: 8 };
const TW = [0, 310], WF = [0, 140];
const P = k.fitProjection(
  [...k.boxCorners(CAB, -10, 430), [160, 130, 430], [-160, -130, 430]],
  W, H, { pad: 40, azimuth: 130, elevation: 14 },
);
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const M = (paths, mat, style = {}) => k.solidSvg(paths, { ...style, className: `qm-${mat}` });
const L = (d, style) => k.lineSvg(d, style);
const D = (pts, style) => k.dotsSvg(pts, style);

const out = [];
out.push(`<style>
.qm-wood .iso-fill{fill:#151515}.qm-wood .iso-shade[data-shade="0"]{fill:#090909}.qm-wood .iso-shade[data-shade="1"]{fill:#111111}.qm-wood .iso-shade[data-shade="2"]{fill:#1A1A1A}.qm-wood .iso-shade[data-shade="3"]{fill:#242424}.qm-wood .iso-top{fill:#2A2A2A}.qm-wood .iso-edge{stroke:#000 !important}.qm-wood .iso-crease{stroke:#333 !important}
.qm-baffle .iso-fill{fill:#1A1C1E}.qm-baffle .iso-shade[data-shade="0"]{fill:#0A0C0E}.qm-baffle .iso-shade[data-shade="1"]{fill:#141618}.qm-baffle .iso-shade[data-shade="2"]{fill:#1A1C1E}.qm-baffle .iso-shade[data-shade="3"]{fill:#24272B}.qm-baffle .iso-top{fill:#2E3238}.qm-baffle .iso-edge{stroke:#000 !important}
.qm-gold .iso-fill{fill:#B08A2E}.qm-gold .iso-top{fill:#D9B24A}.qm-gold .iso-edge{stroke:#7A5A18 !important}
</style>`);

out.push(`<path class="iso-halo" d="${k.haloOf(CAB, -10, 20, P)}"/>`);
for (const [x, y] of k.corners(CAB, 24)) {
  out.push(M(k.cylinder(x, y, 10, -8, 8, P, 24), "wood", { tone: "lo" }));
}
out.push(M(k.slabOf(CAB, 0, 420, P, 8, 1.5), "wood", { tone: "mid" }));
out.push(L(k.planOutline(k.insetPlan(CAB, 6), 420, P, 8), { tone: "lo" }));
out.push(M(k.slabOf(BAFFLE, 10, 400, P, 8, 1), "baffle", { tone: "mid" }));
out.push(L(k.planOutline(k.insetPlan(BAFFLE, 5), 410, P, 8), { tone: "faint" }));

// wood grain on the visible side, kept faint: a black cabinet is read by
// silhouette and drivers, not by a plank pattern.
for (let i = 0; i < 4; i++) {
  const y = -90 + i * 60;
  out.push(`<path d="${k.segment([-150, y, 8], [-150, y, 412], P)}" fill="none" stroke="#2A2A2A" stroke-width=".8" opacity=".55"/>`);
}

function driver(cx, cz, rOuter, rCone, rInner, rCap, label) {
  const g = [];
  g.push(`<path d="${k.sideRing([cx, 131, cz], rOuter, "y", P, 48)}" fill="#1A1C1E" stroke="#000" stroke-width="1"/>`);
  g.push(`<path d="${k.sideRing([cx, 131, cz], rOuter - 3, "y", P, 48)}" fill="none" stroke="#3A3E44" stroke-width="1.2"/>`);
  g.push(`<path d="${k.sideRing([cx, 131, cz], rCone, "y", P, 48)}" fill="#2E3238" stroke="#0A0C0E" stroke-width="1"/>`);
  g.push(`<path d="${k.sideRing([cx, 131, cz], rCone - 8, "y", P, 48)}" fill="#23262A" stroke="#141618" stroke-width="0.8"/>`);
  g.push(`<path d="${k.sideRing([cx, 131, cz], rInner, "y", P, 48)}" fill="#1A1C1E" stroke="#3A3E44" stroke-width="0.8"/>`);
  g.push(`<path d="${k.sideRing([cx, 131, cz], rCap, "y", P, 48)}" fill="#0A0C0E" stroke="#000" stroke-width="0.8"/>`);
  g.push(`<path d="${k.sideRing([cx, 131, cz], rCap * 0.55, "y", P, 48)}" fill="#2E3238" stroke="#3A3E44" stroke-width="0.6"/>`);
  const screws = [];
  for (let i = 0; i < 4; i++) {
    const a = Math.PI / 4 + i * Math.PI / 2;
    screws.push(at([cx + Math.cos(a) * (rOuter - 8), 132, cz + Math.sin(a) * (rOuter - 8)]));
  }
  g.push(D(screws, { size: 1.5, tone: "mid" }));
  return `<g data-driver="${label}">${g.join("")}</g>`;
}

out.push(driver(TW[0], TW[1], 60, 38, 22, 12, "tweeter"));
out.push(driver(WF[0], WF[1], 92, 72, 48, 20, "woofer"));

// logo
const [lx, ly] = at([0, 132, 382]);
out.push(`<text x="${lx}" y="${ly}" font-family="Segoe Script, Brush Script MT, cursive" font-size="22" fill="#C9A227" text-anchor="middle">Gale</text>`);

// corner mounting holes
for (const [x, z] of [[-122, 42], [122, 42], [-122, 382], [122, 382]]) {
  out.push(`<path d="${k.sideRing([x, 131, z], 11, "y", P)}" fill="#050607" stroke="#2E3238" stroke-width="1"/>`);
  out.push(`<path d="${k.sideRing([x, 131, z], 7, "y", P)}" fill="#000" stroke="#3A3E44" stroke-width="0.6"/>`);
}

// base shadow / feet
// base contact: the halo carries the shadow; a bottom outline reads as a
// hidden wireframe edge on a black cabinet.

const svg = productSvg({
  width: W,
  height: H,
  label:
    "Gale Silver Monitor bookshelf speaker, front three-quarter product illustration with tweeter, woofer, mounting holes and cabinet.",
  title: "Gale Silver Monitor speaker (front)",
  desc: "Part-based isometric SVG drawn in object coordinates with the MIT-licensed Anatomy kit. Flat four-tone solids, painter order, no raster and no trace.",
  body: out,
});
const outPath = process.argv[2] || "gale-speaker-front.svg";
writeFileSync(outPath, svg);
console.log("wrote", outPath, svg.length, "paths", (svg.match(/<path/g) || []).length, "P", P);

