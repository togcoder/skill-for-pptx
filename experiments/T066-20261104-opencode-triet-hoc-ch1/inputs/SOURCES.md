# Sources and licences — T066

## Content

- **Giáo trình Triết học Mác – Lênin**, Bộ Giáo dục và Đào tạo (Vietnamese
  university textbook), Chapter 1: *Khái luận về triết học và triết học Mác –
  Lênin*. The deck summarises the chapter's structure; it is not a verbatim
  reproduction.
- C. Mác, *Luận cương về Phoiơbắc* (1845), for the closing quotation.
- Standard dates used for the timeline: 1848 (*Tuyên ngôn của Đảng Cộng sản*),
  1867 (*Tư bản*, quyển I), 1917 (Cách mạng Tháng Mười Nga).
- The "three components" and "two sides of the basic question" follow the
  textbook's chapter structure; wording is the author's summary.

## Images

All images were downloaded from Wikimedia Commons on 2026-11-04, then
processed locally (background removed with `rembg` U2Net, duotone, circular
mask). The raw files stay in `workspace/`, not in the repository.

| File used | Source | Author / credit | Licence | Changes |
|---|---|---|---|---|
| `marx-circle.png` | [Karl Marx 001.jpg](https://commons.wikimedia.org/wiki/File:Karl_Marx_001.jpg) | Wikimedia Commons | Public domain | background removed, duotone, circular mask |
| `engels-circle.png` | [Friedrich Engels (1891) contrast.jpg](https://commons.wikimedia.org/wiki/File:Friedrich_Engels_(1891)_contrast.jpg) | Wikimedia Commons | Public domain | background removed, duotone, circular mask |
| `lenin-circle.png` | [Lenin in 1920 (cropped).jpg](https://commons.wikimedia.org/wiki/File:Lenin_in_1920_(cropped).jpg) | Wikimedia Commons | Public domain | background removed, duotone, circular mask |
| `plato-full.png` | [Epidauros Philosopher bust NAMA 582 Athens Greece.jpg](https://commons.wikimedia.org/wiki/File:Epidauros_Philosopher_bust_NAMA_582_Athens_Greece.jpg) | Wikimedia Commons | CC0 | background removed, duotone |

The images are historical/archival material; the duotone treatment is a design
choice, not a claim about the original colours. The bust is identified as an
Epidauros philosopher type, not as a portrait of Plato; the slide caption says
"tượng triết gia Hy Lạp" to avoid a false identification.

## Fonts and tools

- Display: **Palatino Linotype** (system font; all 89 non-ASCII characters used
  in the deck are present).
- Body: **Arial** (system font; all 89 non-ASCII characters used in the deck are
  present).
- Build: Python 3.13, `python-pptx`, `lxml`, Pillow; `rembg` 2.0.86 (U2Net).
- Motion: `scripts/pptx_animator.py` (native `p:timing`, Morph transition).
- Render/verify: Microsoft PowerPoint 16.0 build 17932 (COM), PDF export,
  `CreateVideo`, `scripts/design_critic.py`.
- The deck uses no raster underlay, no traced photograph, no stock template.
