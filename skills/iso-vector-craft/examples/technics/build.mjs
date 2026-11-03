import { writeFileSync } from "node:fs";
import * as k from "../../kit/iso-kit.mjs";
import { tubePieces, tubeSvg } from "../../kit/tube.mjs";
import { productSvg } from "../../kit/product-svg.mjs";

const W = 980, H = 900;
const PLINTH = { x: -225, y: -180, w: 450, d: 360, r: 12 };
const PLATTER = [-45, 0];
const ARM = [150, -120];
const DECK = 54;
const P = k.fitProjection(
  [...k.boxCorners(PLINTH, -12, DECK), [PLATTER[0] + 166, 0, 84],
   [205, -165, 104], [225, 180, 60]],
  W, H, { pad: 42, azimuth: 130, elevation: 24 },
);
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const M = (paths, mat, style = {}) => k.solidSvg(paths, { ...style, className: `qm-${mat}` });
const L = (d, style) => k.lineSvg(d, style);
const D = (pts, style) => k.dotsSvg(pts, style);

const out = [];
const parts = [];
let section = null;
const part = (name) => { section = []; parts.push([name, section]); };
const emit = (item) => section.push(item);
part("document");
out.push(`<style>
.qm-silver .iso-fill{fill:#B8B5AC}.qm-silver .iso-shade[data-shade="0"]{fill:#7A7770}.qm-silver .iso-shade[data-shade="1"]{fill:#A8A59C}.qm-silver .iso-shade[data-shade="2"]{fill:#C9C6BC}.qm-silver .iso-shade[data-shade="3"]{fill:#D8D5CC}.qm-silver .iso-top{fill:#E8E6DE}.qm-silver .iso-edge{stroke:#5E5B54 !important}
.qm-dark .iso-fill{fill:#151719}.qm-dark .iso-shade[data-shade="0"]{fill:#08090B}.qm-dark .iso-shade[data-shade="1"]{fill:#0E1012}.qm-dark .iso-shade[data-shade="2"]{fill:#151719}.qm-dark .iso-shade[data-shade="3"]{fill:#23262A}.qm-dark .iso-top{fill:#2E3238}.qm-dark .iso-edge{stroke:#000 !important}
.qm-record .iso-fill{fill:#08090B}.qm-record .iso-top{fill:#0A0C0E}.qm-record .iso-edge{stroke:#000 !important}
.qm-label .iso-fill{fill:#F2EBDC}.qm-label .iso-top{fill:#FBF7EA}.qm-label .iso-edge{stroke:#8E8B82 !important}
.qm-tube-steel .tb-body{fill:#B8B5AC;stroke:none}.qm-tube-steel .tb-shine{fill:#F5F3EA}.qm-tube-steel .tb-shade{fill:#6E6B64}.qm-tube-steel .tb-edge{stroke:#5E5B54;fill:none}.qm-tube-steel .tb-ring{stroke:#8E8B82;fill:none}
.qm-tube-dark .tb-body{fill:#151719;stroke:none}.qm-tube-dark .tb-shine{fill:#2E3238}.qm-tube-dark .tb-shade{fill:#08090B}.qm-tube-dark .tb-edge{stroke:#000;fill:none}.qm-tube-dark .tb-ring{stroke:#3A3E44;fill:none}
</style>`);

part("halo");
emit(`<path class="iso-halo" d="${k.haloOf(PLINTH, -12, 30, P)}"/>`);
part("feet");
for (const [x, y] of k.corners(PLINTH, 38)) {
  emit(M(k.cylinder(x, y, 24, -12, 12, P, 32), "dark", { tone: "lo" }));
  emit(M(k.cylinder(x, y, 17, 0, 3, P, 32), "silver", { tone: "mid" }));
  emit(L(k.ring(x, y, 22, -6, P, 24), { tone: "mid" }));
}
part("plinth");
// low plinth: rubber base + thin silver body + chamfer
emit(M(k.slabOf(PLINTH, 0, 18, P, 8, 1.2), "dark", { tone: "lo" }));
emit(M(k.slabOf(PLINTH, 18, 32, P, 8, 1.4), "silver", { tone: "mid" }));
emit(M(k.slabOf(k.insetPlan(PLINTH, 4), 50, 4, P, 6, 0.8), "silver", { tone: "hi" }));
emit(L(k.planOutline(PLINTH, 18, P, 8), { tone: "lo" }));
emit(L(k.planOutline(k.insetPlan(PLINTH, 4), 50, P, 6), { tone: "hi" }));

part("platter");
// platter shadow + chamfered platter
emit(`<path d="${k.ring(PLATTER[0], PLATTER[1], 173, DECK, P, 96)}" fill="#000" opacity=".16" style="filter:blur(5px)"/>`);
emit(M(k.cylinder(PLATTER[0], PLATTER[1], 165, DECK, 24, P, 96, 1.2), "silver", { tone: "hi" }));
emit(M(k.cylinder(PLATTER[0], PLATTER[1], 158, DECK + 24, DECK + 26 - (DECK + 24), P, 96, 0.5), "silver", { tone: "hi" }));
emit(L(k.ring(PLATTER[0], PLATTER[1], 158, DECK + 26, P, 96), { tone: "mid" }));
emit(L(k.ring(PLATTER[0], PLATTER[1], 160, DECK + 26, P, 96), { tone: "hi" }));
emit(L(k.ring(PLATTER[0], PLATTER[1], 156, DECK + 26, P, 96), { tone: "lo" }));

part("record");
// record + deadwax + label
emit(M(k.cylinder(PLATTER[0], PLATTER[1], 150, DECK + 26, 4, P, 96, 0.6), "record", { tone: "mid" }));
for (const r of [68, 78, 88, 98, 108, 118, 128, 138, 144]) {
  emit(L(k.ring(PLATTER[0], PLATTER[1], r, DECK + 30, P, 96), { tone: "faint" }));
}
emit(L(k.ring(PLATTER[0], PLATTER[1], 150, DECK + 30, P, 96), { tone: "mid" }));
emit(L(k.ring(PLATTER[0], PLATTER[1], 146, DECK + 30, P, 96), { tone: "lo" }));
emit(M(k.cylinder(PLATTER[0], PLATTER[1], 50, DECK + 30, 2, P, 64, 0.4), "label", { tone: "hi" }));
emit(`<path d="${k.ring(PLATTER[0], PLATTER[1], 40, DECK + 31, P, 64)}" fill="none" stroke="#2A2118" stroke-width="0.5" opacity=".5"/>`);
emit(k.faceTextSvg(k.topMatrix([PLATTER[0], PLATTER[1]], DECK + 31, P, "x"), "Technics", { size: 5, tone: "lo", anchor: "middle" }));
emit(M(k.cylinder(PLATTER[0], PLATTER[1], 3, DECK + 30, 18, P, 24, 0.4), "silver", { tone: "hi" }));

part("tonearm-mount");
// tonearm well Ø96 + bearing
emit(M(k.cylinder(ARM[0], ARM[1], 48, DECK, 3, P, 64, 0.6), "dark", { tone: "lo" }));
emit(M(k.cylinder(ARM[0], ARM[1], 40, DECK + 3, 3, P, 56, 0.5), "silver", { tone: "mid" }));
emit(M(k.cylinder(ARM[0], ARM[1], 18, DECK + 6, 18, P, 32, 0.6), "dark", { tone: "lo" }));
emit(L(k.ring(ARM[0], ARM[1], 18, DECK + 20, P, 32), { tone: "hi" }));
emit(M(k.cylinder(ARM[0], ARM[1], 10, DECK + 24, 4, P, 24, 0.4), "silver", { tone: "hi" }));
emit(M(k.cylinder(ARM[0], ARM[1], 7, DECK + 28, 3, P, 20, 0.3), "dark", { tone: "lo" }));

part("tonearm");
// Far (upper-right) gimbal plate and its axle cap come first: they are behind
// the arm. The near plate and its cap are drawn after the arm.
emit(M(k.slabOf({ x: ARM[0] + 16, y: ARM[1] - 10, w: 4, d: 20, r: 1 }, DECK + 18, 18, P, 2, 0.4), "silver", { tone: "hi" }));
const axle = tubePieces([[ARM[0] - 20, ARM[1], DECK + 34], [ARM[0] + 20, ARM[1], DECK + 34]], 3.5, P, { maxLength: 40, spacing: 4 });
emit(`<g class="qm-tube-steel">${axle.map((p) => tubeSvg(p, { tone: "hi" })).join("")}</g>`);
emit(`<path d="${k.sideRing([ARM[0] + 20, ARM[1], DECK + 34], 6, "x", P)}" fill="#C9C6BC" stroke="#5E5B54" stroke-width="0.5"/>`);

// Counterweight sits behind the pivot; paint it before the arm so the arm
// enters it instead of being covered by it.
const cwPts = [[ARM[0] + 16, ARM[1] - 16, DECK + 34], [ARM[0] + 48, ARM[1] - 32, DECK + 34]];
const cw = tubePieces(cwPts, 14, P, { maxLength: 12, spacing: 2.5 });
emit(`<g class="qm-tube-dark">${cw.map((p) => tubeSvg(p, { tone: "hi" })).join("")}</g>`);
const cwCap = tubePieces([[ARM[0] + 48, ARM[1] - 32, DECK + 34], [ARM[0] + 54, ARM[1] - 35, DECK + 34]], 14, P, { maxLength: 8, spacing: 2 });
emit(`<g class="qm-tube-steel">${cwCap.map((p) => tubeSvg(p, { tone: "hi" })).join("")}</g>`);

// S-shaped arm + stepped collars. The first point is the pivot, so moving ARM
// moves the whole arm; the other points are the product's S-curve.
const armPts = [[ARM[0], ARM[1], DECK + 34], [ARM[0] - 28, ARM[1] + 38, DECK + 35], [ARM[0] - 58, ARM[1] + 98, DECK + 37], [ARM[0] - 88, ARM[1] + 158, DECK + 37], [ARM[0] - 110, ARM[1] + 202, DECK + 34]];
const armPieces = tubePieces(armPts, 4, P, { maxLength: 18, spacing: 2.4 });
emit(`<g class="qm-tube-steel">${armPieces.map((p) => tubeSvg(p, { tone: "hi" })).join("")}</g>`);
const collar1 = tubePieces([[ARM[0] - 8, ARM[1] + 10, DECK + 34], [ARM[0] - 22, ARM[1] + 26, DECK + 35]], 7, P, { maxLength: 16, spacing: 2.2 });
emit(`<g class="qm-tube-steel">${collar1.map((p) => tubeSvg(p, { tone: "hi" })).join("")}</g>`);
const collar2 = tubePieces([[ARM[0] - 90, ARM[1] + 164, DECK + 36], [ARM[0] - 100, ARM[1] + 188, DECK + 35]], 6, P, { maxLength: 10, spacing: 2 });
emit(`<g class="qm-tube-steel">${collar2.map((p) => tubeSvg(p, { tone: "hi" })).join("")}</g>`);

// Near (lower-left) gimbal plate after the arm, with its cap on top.
emit(M(k.slabOf({ x: ARM[0] - 20, y: ARM[1] - 10, w: 4, d: 20, r: 1 }, DECK + 18, 18, P, 2, 0.4), "silver", { tone: "hi" }));
emit(`<path d="${k.sideRing([ARM[0] - 20, ARM[1], DECK + 34], 6, "x", P)}" fill="#151719" stroke="#5E5B54" stroke-width="0.5"/>`);

// anti-skate + cue lever, anchored to the arm base so moving ARM keeps the
// mechanism attached.
const AS = [ARM[0] - 22, ARM[1] + 16];
const CUE = [ARM[0] + 14, ARM[1] + 20];
emit(M(k.cylinder(AS[0], AS[1], 8, DECK + 6, 5, P, 20, 0.4), "dark", { tone: "lo" }));
for (let i = 0; i < 8; i++) {
  const a = (i / 8) * Math.PI * 2;
  emit(L(k.lineOnTop([AS[0] + Math.cos(a) * 8, AS[1] + Math.sin(a) * 8],
                         [AS[0] + Math.cos(a) * 11, AS[1] + Math.sin(a) * 11], DECK + 11, P),
               { tone: i % 2 === 0 ? "mid" : "lo" }));
}
emit(L(k.lineOnTop([AS[0], AS[1]], [AS[0] + Math.cos(-0.6) * 8, AS[1] + Math.sin(-0.6) * 8], DECK + 11, P), { tone: "hi" }));
emit(M(k.slabOf({ x: AS[0] - 6, y: AS[1] - 12, w: 4, d: 10, r: 1 }, DECK + 9, 3, P, 2, 0.3), "silver", { tone: "hi" }));
emit(M(k.cylinder(CUE[0], CUE[1], 4, DECK + 10, 4, P, 20, 0.3), "silver", { tone: "hi" }));
emit(M(k.slabOf({ x: CUE[0] - 2, y: CUE[1] + 2, w: 18, d: 4, r: 2 }, DECK + 14, 3, P, 2, 0.3), "silver", { tone: "hi" }));
emit(M(k.slabOf({ x: CUE[0] + 12, y: CUE[1], w: 6, d: 8, r: 2 }, DECK + 12, 2, P, 2, 0.3), "dark", { tone: "lo" }));
emit(M(k.cylinder(CUE[0] - 2, CUE[1] + 12, 3, DECK + 10, 8, P, 16, 0.3), "silver", { tone: "mid" }));

part("headshell");
// headshell + cartridge + finger lift. HS is the arm's end point, so moving
// the arm carries the cartridge with it.
const HS = [ARM[0] - 110, ARM[1] + 202];
emit(M(k.slabOf({ x: HS[0] - 18, y: HS[1] - 6, w: 34, d: 16, r: 4 }, DECK + 32, 8, P, 3, 0.5), "dark", { tone: "mid" }));
emit(M(k.slabOf({ x: HS[0] - 13, y: HS[1] - 2, w: 24, d: 10, r: 2 }, DECK + 28, 5, P, 2, 0.4), "dark", { tone: "lo" }));
emit(M(k.slabOf({ x: HS[0] + 13, y: HS[1] - 2, w: 10, d: 3, r: 1 }, DECK + 36, 2, P, 2, 0.3), "silver", { tone: "hi" }));
emit(`<path d="M${at([HS[0] - 5, HS[1] + 6, DECK + 28])[0]} ${at([HS[0] - 5, HS[1] + 6, DECK + 28])[1]} L${at([HS[0] - 5, HS[1] + 6, DECK + 25])[0]} ${at([HS[0] - 5, HS[1] + 6, DECK + 25])[1]}" stroke="#C9C6BC" stroke-width="0.8"/>`);
emit(D([at([HS[0] - 10, HS[1] - 2, DECK + 40]), at([HS[0] + 10, HS[1] - 2, DECK + 40])], { size: 1.1, tone: "mid" }));
emit(`<path d="M${at([HS[0] - 14, HS[1] + 2, DECK + 36])[0]} ${at([HS[0] - 14, HS[1] + 2, DECK + 36])[1]} L${at([HS[0] - 7, HS[1] + 5, DECK + 33])[0]} ${at([HS[0] - 7, HS[1] + 5, DECK + 33])[1]}" stroke="#C0392B" stroke-width="0.7"/>`);
emit(`<path d="M${at([HS[0] - 13, HS[1] + 2, DECK + 35])[0]} ${at([HS[0] - 13, HS[1] + 2, DECK + 35])[1]} L${at([HS[0] - 6, HS[1] + 5, DECK + 32])[0]} ${at([HS[0] - 6, HS[1] + 5, DECK + 32])[1]}" stroke="#2E6DA4" stroke-width="0.7"/>`);
emit(`<circle cx="${at([HS[0] - 5, HS[1] + 6, DECK + 25])[0]}" cy="${at([HS[0] - 5, HS[1] + 6, DECK + 25])[1]}" r="1.1" fill="#E8E6DE"/>`);

part("arm-rest");
// arm rest
emit(M(k.cylinder(103, 60, 3, DECK, 18, P, 16, 0.3), "silver", { tone: "mid" }));
emit(M(k.cylinder(115, 60, 3, DECK, 18, P, 16, 0.3), "silver", { tone: "mid" }));
emit(M(k.slabOf({ x: 100, y: 56, w: 18, d: 8, r: 3 }, DECK + 16, 4, P, 2, 0.3), "dark", { tone: "lo" }));

part("controls");
// controls on the low deck
emit(M(k.cylinder(-160, 145, 22, DECK, 5, P, 40, 0.6), "silver", { tone: "hi" }));
emit(M(k.cylinder(-160, 145, 15, DECK + 5, 4, P, 32, 0.5), "dark", { tone: "lo" }));
emit(M(k.cylinder(-110, 152, 10, DECK, 5, P, 24, 0.4), "silver", { tone: "hi" }));
emit(M(k.cylinder(-80, 152, 10, DECK, 5, P, 24, 0.4), "silver", { tone: "hi" }));
emit(M(k.slabOf({ x: 80, y: 148, w: 100, d: 8, r: 3 }, DECK, 3, P, 2, 0.3), "dark", { tone: "lo" }));
emit(M(k.slabOf({ x: 116, y: 146, w: 14, d: 12, r: 3 }, DECK + 3, 5, P, 2, 0.4), "silver", { tone: "hi" }));
for (let i = 0; i <= 8; i++) {
  const x = 84 + i * 12;
  emit(L(k.lineOnTop([x, 140], [x, 145], DECK + 1, P), { tone: i % 4 === 0 ? "mid" : "lo" }));
}
for (const [x, label] of [[84, "-8"], [180, "+8"]]) {
  const [px, py] = at([x, 136, DECK + 1]);
  emit(`<text x="${px}" y="${py}" font-family="Arial" font-size="3.4" fill="#2E3238" text-anchor="middle">${label}</text>`);
}
for (const [x, label] of [[-110, "33"], [-80, "45"]]) {
  const [px, py] = at([x, 165, DECK + 1]);
  emit(`<text x="${px}" y="${py}" font-family="Arial" font-size="4" fill="#2E3238" text-anchor="middle">${label}</text>`);
}

part("target-light");
// pop-up target light (SL-1200 signature)
emit(M(k.cylinder(-120, 165, 6, DECK, 6, P, 24, 0.4), "silver", { tone: "hi" }));
emit(M(k.slabOf({ x: -123, y: 161, w: 6, d: 3, r: 1 }, DECK + 6, 2, P, 2, 0.3), "dark", { tone: "lo" }));
emit(`<circle cx="${at([-120, 165, DECK + 8])[0]}" cy="${at([-120, 165, DECK + 8])[1]}" r="2.2" fill="#E8D48A"/>`);

part("marks");
// logo on the front face, not on the deck: the start/stop button was occluding
// the brand mark when it sat at z = DECK + 1.
const [lx, ly] = at([PLINTH.x + 15, PLINTH.y + PLINTH.d + 1, 30]);
emit(`<text x="${lx}" y="${ly}" font-family="Arial" font-size="10" font-weight="bold" fill="#1A1C1E" text-anchor="start" letter-spacing="1">Technics</text>`);
const [mx, my] = at([PLINTH.x + 75, PLINTH.y + PLINTH.d + 1, 31]);
emit(`<text x="${mx}" y="${my}" font-family="Arial" font-size="4.6" fill="#2E3238" text-anchor="start" letter-spacing=".6">SL-1200MK2</text>`);
emit(D([at([PLINTH.x + 25, PLINTH.y + PLINTH.d - 20, DECK + 1]), at([PLINTH.x + PLINTH.w - 25, PLINTH.y + PLINTH.d - 20, DECK + 1])], { size: 1.4, tone: "lo" }));

const body =
  out.join("") +
  parts
    .filter(([, items]) => items.length)
    .map(([name, items]) => `<g data-part="${name}">${items.join("")}</g>`)
    .join("");
const svg = productSvg({
  width: W,
  height: H,
  label:
    "Technics SL-1200 direct-drive turntable, three-quarter product illustration: low plinth, chamfered platter, vinyl record with deadwax, gimbal tonearm, controls and target light.",
  title: "Technics SL-1200 product illustration",
  desc: "Part-based isometric SVG drawn in object coordinates with the MIT-licensed Anatomy kit. Flat four-tone solids, painter order, no raster and no trace.",
  body,
});
const outPath = process.argv[2] || "technics-sl1200.svg";
writeFileSync(outPath, svg);
console.log(
  "wrote", outPath, svg.length, "paths", (svg.match(/<path/g) || []).length,
  "parts", parts.filter(([, items]) => items.length).length, "P", P,
);