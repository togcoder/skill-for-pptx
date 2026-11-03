import { writeFileSync } from "node:fs";
import * as k from "../../kit/iso-kit.mjs";
import { productSvg } from "../../kit/product-svg.mjs";

const W = 820, H = 900;
const CAB = { x: -150, y: -125, w: 300, d: 250, r: 6 };
const P = k.fitProjection(
  [...k.boxCorners(CAB, -10, 430), [160, 130, 430], [-160, -130, 430]],
  W, H, { pad: 40, azimuth: 310, elevation: 14 },
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
.qm-red .iso-fill{fill:#B03A2E}.qm-red .iso-top{fill:#E87A6A}.qm-red .iso-edge{stroke:#7A1F1A !important}
</style>`);

out.push(`<path class="iso-halo" d="${k.haloOf(CAB, -10, 20, P)}"/>`);
for (const [x, y] of k.corners(CAB, 24)) {
  out.push(M(k.cylinder(x, y, 10, -8, 8, P, 24), "wood", { tone: "lo" }));
}
out.push(M(k.slabOf(CAB, 0, 420, P, 8, 1.5), "wood", { tone: "mid" }));
out.push(L(k.planOutline(k.insetPlan(CAB, 6), 420, P, 8), { tone: "lo" }));

// grain on the visible right side, kept faint: the cabinet is read by
// silhouette, port and terminal plate, not by a plank pattern.
for (let i = 0; i < 4; i++) {
  const y = -90 + i * 60;
  out.push(`<path d="${k.segment([150, y, 8], [150, y, 412], P)}" fill="none" stroke="#2A2A2A" stroke-width=".8" opacity=".55"/>`);
}

// rear port
out.push(`<path d="${k.sideRing([0, -131, 320], 62, "y", P, 48)}" fill="#050607" stroke="#000" stroke-width="1"/>`);
out.push(`<path d="${k.sideRing([0, -131, 320], 58, "y", P, 48)}" fill="none" stroke="#3A3E44" stroke-width="1.2"/>`);
out.push(`<path d="${k.sideRing([0, -131, 320], 52, "y", P, 48)}" fill="#0A0C0E" stroke="#141618" stroke-width="1"/>`);
out.push(`<path d="${k.sideRing([0, -131, 320], 38, "y", P, 48)}" fill="#000" stroke="#2E3238" stroke-width="0.8"/>`);
out.push(`<path d="${k.sideRing([0, -131, 320], 18, "y", P)}" fill="#050607" stroke="#1A1C1E" stroke-width="0.6"/>`);

// label plate
out.push(M(k.slabOf({ x: -62, y: -133, w: 124, d: 5, r: 5 }, 218, 48, P, 4, 0.6), "baffle", { tone: "mid" }));
const [gx, gy] = at([0, -134, 252]);
out.push(`<text x="${gx}" y="${gy}" font-family="Segoe Script, Brush Script MT, cursive" font-size="17" fill="#D9D9D9" text-anchor="middle">Gale</text>`);
const [sx, sy] = at([0, -134, 234]);
out.push(`<text x="${sx}" y="${sy}" font-family="Arial" font-size="8" font-weight="bold" fill="#E8E8E8" text-anchor="middle" letter-spacing="1">SILVER MONITOR</text>`);

// terminal plate
out.push(M(k.slabOf({ x: -68, y: -134, w: 136, d: 6, r: 5 }, 112, 92, P, 4, 0.6), "baffle", { tone: "mid" }));
out.push(M(k.slabOf({ x: -56, y: -138, w: 112, d: 3, r: 3 }, 122, 72, P, 3, 0.4), "wood", { tone: "lo" }));
for (const [x, z, mat] of [[-32, 170, "red"], [32, 170, "red"], [-32, 140, "wood"], [32, 140, "wood"]]) {
  out.push(`<path d="${k.sideRing([x, -139, z], 9, "y", P)}" fill="${mat === "red" ? "#B03A2E" : "#050607"}" stroke="#2E3238" stroke-width="0.8"/>`);
  out.push(`<path d="${k.sideRing([x, -139, z], 4, "y", P)}" fill="${mat === "red" ? "#E87A6A" : "#3A3E44"}"/>`);
}
// barcode strip
out.push(M(k.slabOf({ x: -50, y: -137, w: 100, d: 2, r: 1 }, 104, 8, P, 2, 0.3), "baffle", { tone: "hi" }));
for (let i = 0; i < 18; i++) {
  const x = -46 + i * 5;
  out.push(L(k.segment([x, -138, 105], [x, -138, 111], P), { tone: "lo" }));
}

// base contact: the halo carries the shadow; a bottom outline reads as a
// hidden wireframe edge on a black cabinet.

const svg = productSvg({
  width: W,
  height: H,
  label:
    "Gale Silver Monitor bookshelf speaker, rear three-quarter product illustration with bass port, label and terminal plate.",
  title: "Gale Silver Monitor speaker (rear)",
  desc: "Part-based isometric SVG drawn in object coordinates with the MIT-licensed Anatomy kit. Flat four-tone solids, painter order, no raster and no trace.",
  body: out,
});
const outPath = process.argv[2] || "gale-speaker-rear.svg";
writeFileSync(outPath, svg);
console.log("wrote", outPath, svg.length, "paths", (svg.match(/<path/g) || []).length, "P", P);
