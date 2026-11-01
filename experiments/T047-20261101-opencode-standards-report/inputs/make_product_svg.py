"""Generate a semi-flat 2.5D camera illustration (SVG) for T047.

A front three-quarter product view with an extruded side, a five-ring lens,
a viewfinder hump, a hot shoe, a shutter dial and a textured grip. The style is
controlled: one graphite family, one warm accent, thin machined edges, no
cartoon outlines. VectorCraft rasterises it; Pillow composites the cover.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1400, 1000
CX, CY = 700, 500


def rr(x, y, w, h, r, fill, stroke="#10141A", sw=2.4, opacity=1.0):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>')


def make_svg() -> str:
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    out.append("""<defs>
      <linearGradient id="front" x1="0" y1="0" x2="0.85" y2="1">
        <stop offset="0" stop-color="#3C4551"/><stop offset="0.55" stop-color="#2B323B"/>
        <stop offset="1" stop-color="#20262D"/>
      </linearGradient>
      <linearGradient id="top" x1="0" y1="0" x2="0.7" y2="1">
        <stop offset="0" stop-color="#56616F"/><stop offset="1" stop-color="#38404B"/>
      </linearGradient>
      <linearGradient id="barrel" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#4C5561"/><stop offset="0.55" stop-color="#252B33"/>
        <stop offset="1" stop-color="#14181E"/>
      </linearGradient>
      <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#8A94A1"/><stop offset="0.45" stop-color="#4A525D"/>
        <stop offset="1" stop-color="#252B33"/>
      </linearGradient>
      <radialGradient id="glass" cx="0.38" cy="0.32" r="0.75">
        <stop offset="0" stop-color="#2E75B6"/><stop offset="0.35" stop-color="#173E5F"/>
        <stop offset="0.75" stop-color="#0A1824"/><stop offset="1" stop-color="#050B11"/>
      </radialGradient>
      <linearGradient id="grip" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#1D2229"/><stop offset="1" stop-color="#2B323B"/>
      </linearGradient>
      <filter id="shadow" x="-30%" y="-30%" width="170%" height="170%">
        <feGaussianBlur stdDeviation="26"/>
      </filter>
      <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="4"/>
      </filter>
    </defs>""")

    # Floor shadow.
    out.append(f'<ellipse cx="{CX}" cy="830" rx="380" ry="56" fill="#080B0F" opacity="0.38" filter="url(#shadow)"/>')

    # Extruded side (offset back-right).
    out.append(rr(392, 286, 640, 424, 42, "#14191F", "#0B0E12", 2.4))
    # Top plate / body.
    out.append(rr(372, 300, 640, 390, 40, "url(#front)", "#0D1116", 2.6))
    out.append(rr(372, 292, 640, 78, 36, "url(#top)", "#0D1116", 2.4))
    out.append(rr(388, 308, 608, 14, 7, "#6A7482", "none", 0, 0.35))

    # Front panel inset (a subtle machined step).
    out.append(rr(398, 370, 590, 292, 22, "#2E353F", "#14191F", 1.6, 0.55))
    out.append(rr(404, 376, 578, 280, 18, "#2A313A", "none", 0, 0.45))

    # Viewfinder hump and hot shoe.
    out.append(rr(450, 206, 196, 100, 18, "#39424D", "#0D1116", 2.2))
    out.append(rr(466, 222, 164, 62, 10, "#151A20", "#0A0D11", 1.8))
    out.append(rr(480, 234, 136, 38, 6, "#0A0F15", "none", 0, 0.9))
    out.append(rr(500, 184, 96, 26, 6, "#2A3038", "#0B0E12", 1.6))
    out.append(rr(510, 190, 76, 8, 3, "#7E8996", "none", 0))
    out.append(rr(510, 204, 76, 4, 2, "#11161C", "none", 0))

    # Top dials.
    out.append(f'<circle cx="432" cy="262" r="48" fill="url(#barrel)" stroke="#0D1116" stroke-width="2.4"/>')
    out.append(f'<circle cx="432" cy="262" r="40" fill="#20262D" stroke="#0B0E12" stroke-width="1.6"/>')
    for i in range(24):
        import math
        a = 2 * math.pi * i / 24
        x1 = 432 + 44 * math.cos(a); y1 = 262 + 44 * math.sin(a)
        x2 = 432 + 50 * math.cos(a); y2 = 262 + 50 * math.sin(a)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#929CA9" stroke-width="2" opacity="0.45"/>')
    out.append(f'<circle cx="902" cy="252" r="31" fill="url(#barrel)" stroke="#0D1116" stroke-width="2.2"/>')
    out.append(f'<circle cx="902" cy="252" r="23" fill="#232A32" stroke="#0B0E12" stroke-width="1.4"/>')
    out.append(f'<circle cx="902" cy="252" r="10" fill="#C55A11" stroke="#7A3308" stroke-width="1.2"/>')

    # Grip on the right.
    out.append(rr(880, 356, 116, 288, 28, "url(#grip)", "#0F1318", 2.0))
    for i in range(9):
        y = 382 + i * 28
        out.append(f'<line x1="894" y1="{y}" x2="982" y2="{y}" stroke="#11151A" stroke-width="2.4" opacity="0.55"/>')
        out.append(f'<line x1="894" y1="{y+2}" x2="982" y2="{y+2}" stroke="#3A424D" stroke-width="1.0" opacity="0.30"/>')

    # Lens assembly (front view, concentric rings).
    lx, ly = 590, 508
    out.append(f'<circle cx="{lx}" cy="{ly+10}" r="166" fill="#0E1217" stroke="#080B0F" stroke-width="2"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="166" fill="url(#barrel)" stroke="#0C1015" stroke-width="2.4"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="151" fill="none" stroke="#6E7885" stroke-width="2" opacity="0.55"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="140" fill="#1A1F26" stroke="#0B0F14" stroke-width="2"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="132" fill="none" stroke="#2E75B6" stroke-width="5" opacity="0.9"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="120" fill="#20262E" stroke="#0B0F14" stroke-width="2"/>')
    # Knurled focus ring.
    for i in range(48):
        import math
        a = 2 * math.pi * i / 48
        x1 = lx + 142 * math.cos(a); y1 = ly + 142 * math.sin(a)
        x2 = lx + 151 * math.cos(a); y2 = ly + 151 * math.sin(a)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#0C1015" stroke-width="2.0" opacity="0.55"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="108" fill="url(#barrel)" stroke="#0B0F14" stroke-width="2"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="96" fill="#0D1218" stroke="#080B0F" stroke-width="1.6"/>')
    out.append(f'<circle cx="{lx}" cy="{ly}" r="86" fill="url(#glass)" stroke="#05090D" stroke-width="2"/>')
    # Glass reflections.
    out.append(f'<ellipse cx="{lx-28}" cy="{ly-30}" rx="30" ry="20" fill="#9DC3E6" opacity="0.32" filter="url(#soft)"/>')
    out.append(f'<ellipse cx="{lx+34}" cy="{ly+20}" rx="14" ry="9" fill="#D9E2F3" opacity="0.22" filter="url(#soft)"/>')
    out.append(f'<path d="M {lx-58} {ly+30} A 66 66 0 0 0 {lx+42} {ly+52}" fill="none" stroke="#2E75B6" stroke-width="3" opacity="0.45"/>')
    # Mount screws.
    import math
    for a in (0.4, 2.2, 4.0, 5.5):
        x = lx + 158 * math.cos(a); y = ly + 158 * math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#7E8996" stroke="#0B0E12" stroke-width="1"/>')

    # Brand plate and mark.
    out.append(rr(424, 610, 148, 42, 6, "#171C23", "#0B0E12", 1.4))
    out.append(f'<path d="M 444 640 L 456 618 L 468 640 Z" fill="#C55A11"/>')
    out.append(f'<path d="M 462 640 L 474 618 L 486 640 Z" fill="#E8EDF2" opacity="0.92"/>')
    out.append(f'<rect x="496" y="622" width="54" height="5" rx="2.5" fill="#8C96A3" opacity="0.6"/>')
    out.append(f'<rect x="496" y="632" width="34" height="4" rx="2" fill="#5B6470" opacity="0.7"/>')

    # AF lamp, screws, port flap, strap lug.
    out.append(f'<circle cx="824" cy="404" r="11" fill="#0B0F14" stroke="#39424D" stroke-width="3"/>')
    out.append(f'<circle cx="824" cy="404" r="4" fill="#C55A11" opacity="0.9"/>')
    for x, y in [(414, 366), (414, 654), (966, 366), (966, 654)]:
        out.append(f'<circle cx="{x}" cy="{y}" r="4.4" fill="#7E8996" stroke="#0B0E12" stroke-width="1"/>')
    out.append(rr(388, 430, 16, 82, 8, "#20262D", "#0B0E12", 1.2))
    out.append(rr(378, 342, 18, 28, 8, "#59616C", "#0B0E12", 1.2))
    out.append(f'<rect x="382" y="348" width="10" height="16" rx="5" fill="#14191F"/>')

    # Bottom accent line / tripod plate hint.
    out.append(f'<rect x="430" y="682" width="520" height="6" rx="3" fill="#0B0E12" opacity="0.8"/>')
    out.append(f'<rect x="650" y="690" width="120" height="8" rx="4" fill="#11161C" opacity="0.7"/>')

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    path = HERE / "camera.svg"
    path.write_text(make_svg(), encoding="utf-8")
    print(path)
