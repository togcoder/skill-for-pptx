// Export helper for the iso-vector-craft skill.
//
// Anatomy's `figureSvg` keeps its design tokens in CSS custom properties.
// Browsers resolve those, but several vector editors and rasterisers (resvg,
// older Illustrator imports, some CLI checkers) do not. A product illustration
// usually leaves the browser, so this wrapper bakes the light palette into
// literal values and adds a title/description. Geometry and shading stay
// identical; only `var(--anatomy-*)` references are replaced.

import { figureSvg } from "./iso-kit.mjs";

// Values copied from `kit/iso.css`, `.iso[data-theme="light"]` (MIT, Anatomy).
// Keep this table in one place: it is the export contract, not decoration.
export const LIGHT = {
  page: "#f2f2ef",
  card: "#fbfbfa",
  text: "#57575a",
  strong: "#18181a",
  muted: "#8c8c90",
  paper: "#fbfbfa",
  face: "#ffffff",
  top: "#ffffff",
  "shade-0": "#dcdcd9",
  "shade-1": "#e5e5e2",
  "shade-2": "#ededea",
  "shade-3": "#f4f4f1",
  "lit-top": "#ffffff",
  "lit-shade": "#eeeeeb",
  hi: "#26262a",
  mid: "#8a8a8f",
  lo: "#b4b4b8",
  faint: "#d4d4d6",
  lit: "#000000",
  halo: "#8a8a80",
  "halo-opacity": ".32",
  dot: "#3a3a3e",
  red: "#e5484d",
  green: "#30a46c",
  blue: "#3e63dd",
  weight: ".6px",
  ease: "cubic-bezier(.32,.72,0,1)",
  mono: "Arial",
  lift: "none",
};

const escapeXml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");

/**
 * Build a standalone, export-safe product SVG.
 *
 * @param {object} options
 * @param {number} options.width  viewBox width
 * @param {number} options.height viewBox height
 * @param {string} options.label  aria-label (what the drawing is)
 * @param {string} options.title  <title>, shown by editors and screen readers
 * @param {string} options.desc   <desc>, the method and the limits
 * @param {string|string[]} options.body  SVG fragments, back to front
 * @param {Record<string,string>} [options.palette] overrides for LIGHT
 * @returns {string} standalone SVG
 */
export function productSvg({ width, height, label, title, desc, body, palette = {} }) {
  const colors = { ...LIGHT, ...palette };
  let svg = figureSvg({ width, height, label, body, standalone: true });

  svg = svg.replace('data-theme="true"', 'data-theme="light"');
  for (const [name, value] of Object.entries(colors)) {
    svg = svg.replaceAll(`var(--anatomy-${name})`, value);
  }
  svg = svg
    .replace(
      "><style>",
      `><title>${escapeXml(title)}</title><desc>${escapeXml(desc)}</desc><style>`,
    )
    .replace(
      "</style>",
      ".iso-face-text{font-family:Arial,Helvetica,sans-serif}</style>",
    );
  return svg;
}
