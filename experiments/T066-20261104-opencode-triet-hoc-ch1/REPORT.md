# T066 [pptx] — Triết học Mác – Lênin, Chương 1: a native red editorial deck

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max).
- **Date:** 2026-11-04. **Base:** `main` @ `be03d63`. **Branch:**
  `work/T066-opencode-triet-hoc-ch1`.
- **Request:** a “best possible” deck for **Chapter 1 of Marxist-Leninist
  philosophy**, with complex motion, a vivid red tone, and images taken from the
  internet with their backgrounds removed.
- **Status:** complete as an experimental deck; review requested. No product
  path was changed.

## Frame

- **Question.** Can the lab produce a native, editable, art-directed deck for a
  real university chapter — not a template demo — with a coherent red identity,
  cut-out historical portraits, and motion that carries the argument?
- **Hypothesis.** A 10-slide deck built from native shapes, four type roles,
  three cut-out assets and a continuous Morph thread can look like an editorial
  product, not a generic AI deck, while remaining editable in PowerPoint.
- **Falsifiers.**
  - the deck reads as a template with text dropped in;
  - the motion is decorative and obscures the content;
  - the portraits are raw internet images with visible backgrounds;
  - the red palette fails contrast or becomes monotonous;
  - the file cannot be opened/rendered by PowerPoint;
  - the content misstates the textbook chapter.

## Frozen input

- **Request/date:** 2026-11-04, owner’s desktop session.
- **Content source:** *Giáo trình Triết học Mác – Lênin*, Bộ Giáo dục và Đào tạo,
  Chapter 1 — *Khái luận về triết học và triết học Mác – Lênin*. The deck is a
  summary, not a verbatim copy.
- **Quotation:** C. Mác, *Luận cương về Phoiơbắc* (1845).
- **Images (Wikimedia Commons, downloaded 2026-11-04):**
  - Karl Marx, `Karl Marx 001.jpg`, Public Domain;
  - Friedrich Engels, `Friedrich Engels (1891) contrast.jpg`, Public Domain;
  - V. I. Lenin, `Lenin in 1920 (cropped).jpg`, Public Domain;
  - Epidauros philosopher bust, `Epidauros Philosopher bust NAMA 582 Athens
    Greece.jpg`, CC0.
  Full URLs and modifications: `inputs/SOURCES.md`.
- **Environment:** Windows 11, PowerPoint 16.0 build 17932, Python 3.13,
  python-pptx, Pillow, `rembg` 2.0.86 (U2Net), lxml.
- **Not available:** a human review of every slide; a second PowerPoint build;
  a measured projector/room; a complete proofread against the printed textbook.

## Method

```powershell
# 1. download the four raw images into inputs/raw/ (URLs in inputs/raw/README.md)
python experiments/T066-20261104-opencode-triet-hoc-ch1/inputs/01_cutout.py
python experiments/T066-20261104-opencode-triet-hoc-ch1/inputs/02_prepare_assets.py

# 2. build the native deck (10 slides, 144 effects, 9 Morph transitions)
python experiments/T066-20261104-opencode-triet-hoc-ch1/inputs/build_deck.py

# 3. render with PowerPoint: PNG 1920×1080 + PDF
powershell -File experiments/T066-20261104-opencode-triet-hoc-ch1/inputs/render.ps1 `
  -Pptx experiments/.../artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx `
  -OutDir experiments/.../preview

python scripts/design_critic.py `
  experiments/T066-.../artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx `
  -o artifacts/critic.json

# 4. render motion with PowerPoint CreateVideo
python scripts/slide_forge.py render `
  experiments/T066-.../artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx `
  -d preview/motion --seconds 6
```

1. **Art direction.** Vivid crimson `#C1121F`, deep red `#7A0C14`, cream
   `#F7F1E8`, ink `#1A0508`, gold `#E8B04B` (small text uses `#FFD98A` for
   contrast). Palatino Linotype display, Arial body; Vietnamese coverage checked
   with fontTools: 89 non-ASCII characters, 0 missing glyphs in either family.
2. **Images are assets, not backgrounds.** `rembg` removed the background, a
   two-stop duotone mapped the archive image into the palette, and a circular
   mask (or a full bust silhouette for the Plato image) made the cut-outs sit in
   the layout. The raw photographs are not embedded.
3. **Native geometry.** Every panel, rule, circle, arrow, timeline and label is
   a PowerPoint shape. The deck uses no raster underlay, no traced photo and no
   template.
4. **Motion.** `pptx_animator.apply_timeline` writes native `p:timing` with
   click groups, `with`/`after` chains, wipes, zooms, floats, a pulse and a
   wipe timeline. `add_morph_transition` puts a 1.5 s Morph on slides 2–10. The
   gold thread and dot (`!!thread`, `!!dot`) are named on every slide so Morph
   carries the eye between sections; `!!bg` carries the background.
5. **Verification.** PowerPoint COM reads 10 slides, 144 main-sequence effects
   and 9 Morph transitions. The deck exports 10 PNGs and a 10-page PDF. A
   74-second `CreateVideo` render proves the click sequence plays; the 14-second
   teaser keeps the preview inside the 2 MB cap.

## Content map

| # | Slide | Content job | Motion |
|---|---|---|---|
| 1 | Cover | Chapter title, three portraits, the “01” field | title/rule/portraits build; thread draws |
| 2 | Triết học là gì? | textbook definition; three functions; Plato bust | definition, three labels, bust float |
| 3 | Vật chất hay ý thức? | basic question; two sides (bản thể luận / nhận thức luận) | cards wipe up/down; question zoom |
| 4 | Biện chứng hay siêu hình? | dialectics vs metaphysics | circular arrow, cards, straight-line comparison |
| 5 | Điều kiện ra đời | economic-social, natural science, thought; 1848 | three cards, timeline |
| 6 | Ba bộ phận | philosophy, political economy, scientific socialism | three blocks, connectors, note |
| 7 | Một dòng chảy | Marx/Engels/Lenin, 1848/1867/1917 | portraits, dates, timeline |
| 8 | Đối tượng & chức năng | worldview, method, social function, science | four tiles build |
| 9 | Luận cương | “cải tạo thế giới” quotation | quote mark, three lines, author |
| 10 | Mang theo | three takeaways, closing question, credits | takeaways, closing zoom |

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| Native deck, 10 slides | PowerPoint 16.0 opens read-only; `Slides.Count=10`; no repair | 4 |
| Complex motion | COM: **144** main-sequence effects; `Morph` entry effect **3954** on slides 2–10, 1.5 s | 4 |
| Render fidelity | 10 PNGs at 1920×1080; PDF **10 pages**, 513 KB | 5 |
| Motion playback | `CreateVideo` render **74 s**; 14 s teaser at 960×540 | 5 |
| Design critic | overall **4.03**; design 2.98, motion **4.99**, rhythm 4.48, coherence 3.67 | 1–3 |
| Vietnamese glyphs | 89 non-ASCII characters used; Palatino/Arial cmap missing **0** | 1 |
| Image processing | backgrounds removed, duotone, circular mask; raw files not embedded | 1 |
| File size | PPTX **2,016,432 bytes**; PDF 513,186; teaser 195,267 | 1 |
| Human review | **not reached** | — |

Artifacts:
- `artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx` — final deck.
- `preview/T066-Triet-hoc-Mac-Lenin-Chuong-1.pdf` — 10-page PDF.
- `preview/slide-01.png` … `slide-10.png` — 1920×1080 renders.
- `preview/motion-teaser.mp4` — 14 s, 960×540.
- `preview/motion/` — CreateVideo strips + sequence JSON.
- `inputs/build_deck.py`, `inputs/assets/`, `inputs/SOURCES.md`.
- `artifacts/critic.json`, `artifacts/SHA256SUMS.txt`.

## Negative results and limitations

1. **Critic flags type density.** The deck uses 21 distinct type sizes; the
   design-system band is 3–6. The editorial layout intentionally uses display,
   section, body, label and micro-caption roles, but the critic is right that a
   stricter six-size scale would be more coherent. It also flags 10–12 pt body
   text in cards and 8–9 pt captions; at 1920 px these are readable, but in a
   large room the body should be raised. This is the first thing to fix in a
   second pass.
2. **Cut-out artefacts.** The Engels portrait has a residual shoulder/bow at the
   bottom of its circle; the Marx portrait has a chair edge hidden by the crop.
   The circle masks hide most of it. A manual alpha cleanup would make a cleaner
   print asset.
3. **The Plato bust is generic.** The caption says “tượng triết gia Hy Lạp”, not
   “Plato”, because the museum object is an Epidauros philosopher type. A
   specialist may object to using it as an illustration of Plato.
4. **Content is a summary.** The definitions and the three-component scheme are
   accurate to the textbook’s chapter structure, but the deck does not carry the
   full argument or citations for every claim. It needs a subject-matter
   proofread before a real class.
5. **Morph is global.** All slides use a 1.5 s Morph; some transitions may feel
   slow, and the thread moves across long distances. Per-slide durations are a
   next pass.
6. **No interactive triggers.** The deck is linear click-build, not a branching
   or trigger-driven experience. The T058 harness was not applied because the
   deck has no `interactiveSeq`.
7. **Rung 6 missing.** PowerPoint rendered and played the deck, but no human
   reviewed every slide and every click in the room. The owner’s eye test is the
   next gate.
8. **No audio.** The deck has speaker notes but no narration or soundtrack.

## Next

1. **Human review** on a projector; record which slides are too dense and which
   transitions are too slow.
2. **Type pass:** six sizes, body ≥18 pt where possible, captions ≥10–12 pt;
   re-run the critic and the PDF.
3. **Content proofread** against the printed textbook; add a small “nguồn”
   slide or footnote for the definitions and dates.
4. **Image cleanup:** manual alpha refinement for Engels/Marx; decide whether
   the Plato bust stays.
5. **Optional variants:** a 4:3 classroom cut, a handout-only PDF, and a
   voice-over version.

## Review response

Pending. This is an experimental deck; the first review should check the
content against the textbook and the motion against the room, not only the
critic score.
