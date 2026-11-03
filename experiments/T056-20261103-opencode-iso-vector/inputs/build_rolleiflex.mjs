import { writeFileSync } from "node:fs";
import * as k from "../../../skills/iso-vector-craft/kit/iso-kit.mjs";
import { productSvg } from "../../../skills/iso-vector-craft/kit/product-svg.mjs";

const W = 820, H = 900;
const BODY = { x: -75, y: -60, w: 150, d: 120, r: 8 };
const P = k.fitProjection(
  [...k.boxCorners(BODY, -8, 235), [90, 70, 235], [-90, -70, 235]],
  W, H, { pad: 40, azimuth: 60, elevation: 22 },
);
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const M = (paths, mat, style = {}) => k.solidSvg(paths, { ...style, className: `qm-${mat}` });
const L = (d, style) => k.lineSvg(d, style);
const D = (pts, style) => k.dotsSvg(pts, style);

const out = [];
out.push(`<style>
.qm-leather .iso-fill{fill:#151515}.qm-leather .iso-shade[data-shade="0"]{fill:#090909}.qm-leather .iso-shade[data-shade="1"]{fill:#111111}.qm-leather .iso-shade[data-shade="2"]{fill:#1A1A1A}.qm-leather .iso-shade[data-shade="3"]{fill:#242424}.qm-leather .iso-top{fill:#2A2A2A}.qm-leather .iso-edge{stroke:#000 !important}.qm-leather .iso-crease{stroke:#333 !important}
.qm-chrome .iso-fill{fill:#B8B5AC}.qm-chrome .iso-shade[data-shade="0"]{fill:#7A7770}.qm-chrome .iso-shade[data-shade="1"]{fill:#A8A59C}.qm-chrome .iso-shade[data-shade="2"]{fill:#C9C6BC}.qm-chrome .iso-shade[data-shade="3"]{fill:#D8D5CC}.qm-chrome .iso-top{fill:#E8E6DE}.qm-chrome .iso-edge{stroke:#5E5B54 !important}
</style>`);

out.push(`<path class="iso-halo" d="${k.haloOf(BODY, -8, 18, P)}"/>`);
for (const [x, y] of k.corners(BODY, 18)) {
  out.push(M(k.cylinder(x, y, 6, -6, 6, P, 20), "chrome", { tone: "lo" }));
}
out.push(M(k.slabOf(BODY, 0, 190, P, 8, 1.4), "leather", { tone: "mid" }));
out.push(M(k.slabOf({ x: -66, y: 60, w: 132, d: 4, r: 6 }, 8, 174, P, 6, 0.8), "leather", { tone: "hi" }));

// chrome trim around the front panel
for (const [x, z, w, h] of [[-68, 6, 136, 4], [-68, 182, 136, 4], [-68, 6, 4, 180], [64, 6, 4, 180]]) {
  out.push(M(k.slabOf({ x, y: 63, w, d: 3, r: 1 }, z, h, P, 2, 0.4), "chrome", { tone: "hi" }));
}

// folded hood
out.push(M(k.slabOf({ x: -62, y: -52, w: 124, d: 112, r: 5 }, 190, 14, P, 6, 1), "leather", { tone: "mid" }));
out.push(M(k.slabOf({ x: -66, y: -56, w: 132, d: 120, r: 4 }, 204, 7, P, 6, 0.8), "leather", { tone: "hi" }));
out.push(M(k.slabOf({ x: -64, y: 60, w: 128, d: 3, r: 2 }, 190, 4, P, 2, 0.3), "chrome", { tone: "hi" }));
out.push(L(k.sideSeam({ x: -62, y: -52, w: 124, d: 112, r: 5 }, 204, P, 6), { tone: "lo" }));
out.push(L(k.planOutline(k.insetPlan({ x: -66, y: -56, w: 132, d: 120, r: 4 }, 5), 211, P, 6), { tone: "hi" }));

// nameplate
out.push(M(k.slabOf({ x: -42, y: 60, w: 84, d: 3, r: 2 }, 196, 11, P, 3, 0.4), "chrome", { tone: "hi" }));
const [nx, ny] = at([0, 63, 202]);
out.push(`<text x="${nx}" y="${ny}" font-family="Arial Narrow, Arial" font-size="9" font-weight="bold" fill="#1A1A1A" text-anchor="middle" letter-spacing="1.3">ROLLEIFLEX</text>`);

// lenses
function lens(cx, cz, r, glass, label) {
  const g = [];
  g.push(`<path d="${k.sideRing([cx, 66, cz], r + 4, "y", P, 48)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.8"/>`);
  g.push(`<path d="${k.sideRing([cx, 66, cz], r + 1, "y", P, 48)}" fill="#1A1C1E" stroke="#000" stroke-width="0.8"/>`);
  g.push(`<path d="${k.sideRing([cx, 66, cz], r - 2, "y", P, 48)}" fill="#2E3238" stroke="#5E5B54" stroke-width="0.6"/>`);
  g.push(`<path d="${k.sideRing([cx, 66, cz], glass, "y", P, 48)}" fill="#111A2A" stroke="#0A1020" stroke-width="0.8"/>`);
  g.push(`<path d="${k.sideRing([cx, 66, cz], glass * 0.55, "y", P, 48)}" fill="#1E3350" stroke="#0A1020" stroke-width="0.5"/>`);
  g.push(`<path d="${k.sideRing([cx, 66, cz], glass * 0.24, "y", P, 48)}" fill="#0A1020"/>`);
  return `<g data-lens="${label}">${g.join("")}</g>`;
}
out.push(lens(0, 145, 22, 15, "viewing"));
out.push(lens(0, 78, 21, 14, "taking"));
for (const [a, label] of [[0.3, "2.8"], [Math.PI / 2 + 0.3, "4"], [Math.PI + 0.3, "5.6"], [3 * Math.PI / 2 + 0.3, "8"]]) {
  const [sx, sy] = at([Math.cos(a) * 18, 67, 78 + Math.sin(a) * 18]);
  out.push(`<text x="${sx}" y="${sy}" font-family="Arial" font-size="2.6" fill="#C9C6BC" text-anchor="middle">${label}</text>`);
}
{
  const pts = [];
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2 + Math.PI / 6;
    pts.push(at([Math.cos(a) * 6, 67, 78 + Math.sin(a) * 6]));
  }
  out.push(`<polygon points="${pts.map(([x, y]) => `${x},${y}`).join(" ")}" fill="#050607" stroke="#3A3E44" stroke-width="0.5"/>`);
}
const [tx, ty] = at([0, 67, 111]);
out.push(`<text x="${tx}" y="${ty}" font-family="Arial" font-size="4.5" fill="#C9C6BC" text-anchor="middle" letter-spacing=".8">SYNCHRO-COMPUR</text>`);
const [fx, fy] = at([0, 67, 45]);
out.push(`<text x="${fx}" y="${fy}" font-family="Arial" font-size="3.4" fill="#8E8B82" text-anchor="middle" letter-spacing=".5">FRANKE &amp; HEIDECKE</text>`);
{
  const dots = [];
  for (let x = -55; x <= 55; x += 14) {
    for (let z = 22; z <= 172; z += 14) {
      if (Math.hypot(x, z - 145) < 34 || Math.hypot(x, z - 78) < 33) continue;
      dots.push(at([x, 65, z]));
    }
  }
  out.push(D(dots, { size: 0.28, tone: "faint" }));
}
// small front knobs
for (const [x, z, r] of [[-47, 112, 8], [47, 112, 8], [-50, 58, 6], [50, 58, 6]]) {
  out.push(`<path d="${k.sideRing([x, 67, z], r, "y", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.7"/>`);
  out.push(`<path d="${k.sideRing([x, 67, z], r * 0.55, "y", P)}" fill="#3A3E44"/>`);
}

// right-side crank and focus knob
out.push(`<path d="${k.sideRing([75, -2, 105], 17, "x", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.8"/>`);
out.push(`<path d="${k.sideRing([75, -2, 105], 12, "x", P)}" fill="#2E3238" stroke="#000" stroke-width="0.6"/>`);
out.push(M(k.slabOf({ x: 75, y: -7, w: 5, d: 12, r: 2 }, 98, 8, P, 2, 0.3), "chrome", { tone: "hi" }));
out.push(M(k.slabOf({ x: 75, y: -8, w: 8, d: 18, r: 2 }, 100, 6, P, 2, 0.3), "chrome", { tone: "hi" }));
out.push(`<path d="${k.sideRing([83, -2, 103], 7, "x", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.6"/>`);
for (const [y, z, w, h] of [[-50, 8, 100, 4], [-50, 176, 100, 4], [-50, 8, 4, 172], [46, 8, 4, 172]]) {
  out.push(M(k.slabOf({ x: 75, y, w: 3, d: w, r: 1 }, z, h, P, 2, 0.3), "chrome", { tone: "lo" }));
}
out.push(`<path d="${k.sideRing([75, 30, 62], 13, "x", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.7"/>`);
out.push(`<path d="${k.sideRing([75, 30, 62], 8, "x", P)}" fill="#3A3E44"/>`);
// strap lug
out.push(M(k.slabOf({ x: 75, y: -45, w: 5, d: 8, r: 2 }, 172, 8, P, 2, 0.3), "chrome", { tone: "hi" }));
out.push(`<path d="${k.sideRing([75, -30, 120], 14, "x", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.7"/>`);
out.push(`<path d="${k.sideRing([75, -30, 120], 10, "x", P)}" fill="#1A1C1E" stroke="#000" stroke-width="0.5"/>`);
out.push(`<path d="${k.sideRing([75, -30, 120], 4, "x", P)}" fill="#C9C6BC"/>`);
out.push(M(k.slabOf({ x: -48, y: 66, w: 6, d: 3, r: 1 }, 70, 10, P, 2, 0.3), "chrome", { tone: "hi" }));
out.push(`<path d="${k.sideRing([38, 67, 56], 5, "y", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.5"/>`);
out.push(`<path d="${k.sideRing([38, 67, 56], 2.5, "y", P)}" fill="#1A1C1E"/>`);
out.push(D([at([-35, 63, 202]), at([35, 63, 202])], { size: 1.1, tone: "mid" }));

// leather grain on the visible right side, kept faint: the camera is read by
// silhouette, lenses and the chrome trim, not by a plank pattern.
for (let i = 0; i < 3; i++) {
  const y = -30 + i * 45;
  out.push(`<path d="${k.segment([75, y, 12], [75, y, 180], P)}" fill="none" stroke="#2A2A2A" stroke-width=".8" opacity=".55"/>`);
}

// bottom plate: the halo carries the contact shadow.

const svg = productSvg({
  width: W,
  height: H,
  label:
    "Rolleiflex twin-lens reflex camera, three-quarter product illustration with folded hood, nameplate, viewing and taking lenses, side crank and focus knob.",
  title: "Rolleiflex TLR stress test",
  desc: "Hard-subject stress test for the iso-vector-craft method. Part-based isometric SVG with the MIT Anatomy kit; compound lens barrels and the folded hood remain simplified.",
  body: out,
});
const outPath = process.argv[2] || "rolleiflex-tlr.svg";
writeFileSync(outPath, svg);
console.log("wrote", outPath, svg.length, "paths", (svg.match(/<path/g) || []).length, "P", P);
