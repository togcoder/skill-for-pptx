# T063 — frozen commands

Base: `ac5b45efb4e98359e1c68b13927db86696b35126` (`main`, after T058–T065 claims).
All commands run from the repository root with `PYTHONUTF8=1`.

## Build all example decks

```powershell
python -c "import json,sys; from pathlib import Path; sys.path.insert(0,'scripts'); import slide_forge as sf; [sf.build(json.loads(p.read_text(encoding='utf-8')), Path('workspace/final')/(p.stem+'.pptx')) for p in sorted(Path('examples/pptx/forge').glob('*.json'))]"
```

The static intermediate is written next to the output (`*.static.pptx`); it is
scratch and not committed.

## Critic (all examples)

```powershell
python -c "import sys,json; from pathlib import Path; sys.path.insert(0,'scripts'); import design_critic as dc; [Path('workspace/crit/after',p.stem+'.json').write_text(json.dumps(dc.critique(p),indent=1,ensure_ascii=False),encoding='utf-8') for p in Path('workspace/final').glob('*.pptx')]"
```

`artifacts/critic/before/` and `artifacts/critic/after/` hold the JSON and
markdown for all five decks, including the static intermediate decks
(`*.static`, which have MOT-STATIC by design).

## PowerPoint 16.0 export

The COM calls are in `scripts/powerpoint_render.ps1` for CreateVideo; PDF and
PNG were exported with the same COM object:

```powershell
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($pptx, -1, 0, 0)
$pres.Export($pdf, "PDF")
$pres.Slides.Item(3).Export($png, "PNG", 1280, 720)
$pres.Close(); $app.Quit()
```

PDF page 3 was rasterised with PyMuPDF 1.28:

```python
import fitz
fitz.open("artifacts/after/vi_chuyen_doi_so.pdf")[2].get_pixmap(dpi=120).save("artifacts/after/vi-pdf-slide3.png")
```

## Motion frames

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/powerpoint_render.ps1 `
  -Pptx workspace/final/vi_chuyen_doi_so.pptx `
  -OutDir workspace/evidence/after/pptrender -SecondsPerSlide 5

ffmpeg -ss 12.8 -t 7.2 -i workspace/evidence/after/pptrender/native_render.mp4 `
  -vf "fps=5,scale=640:-1" workspace/evidence/after/pptrender/frames/f%03d.png
ffmpeg -i workspace/evidence/after/pptrender/frames/f%03d.png `
  -vf "scale=320:-1,tile=6x6" -frames:v 1 preview/ppt-kpi-contact.png
```

The MP4 is 3.3 MB, above the 2 MB/file cap, so it stays local in
`workspace/`; the contact sheet, the cover frames and
`artifacts/native/native_sequence.json` are committed.

## DeckCraft (second reader, static end state only)

```powershell
D:\artcraft\DeckCraft\deckcraft-cli.exe render-transition `
  workspace/final/vi_chuyen_doi_so.pptx --slide 3 --t 0.5 `
  preview/morph-kpi-after.png
```

DeckCraft 0.13.1 reports `morph objects t=0.5` at 1920×1080. It renders the
outgoing slide's static end state, not PowerPoint's animated Morph; it is used
for the print/static stack only.

## Tests

```powershell
python -m unittest discover -s tests -v
python lab/tools/check_layout.py
```
