# T057 commands (Windows, PowerShell / Git Bash)

```bash
python -m unittest discover -s tests            # 461 OK, 4 skipped
python scripts/slide_forge.py build examples/pptx/forge/vi_chuyen_doi_so.json -o $W/vi.pptx
DC=/d/artcraft/DeckCraft/deckcraft-cli.exe      # 0.13.1
$DC render $W/vi.pptx --all $W/dcr              # 9 × 1920×1080
$DC convert $W/vi.pptx $W/vi_rt.pptx            # round trip; count p:anim/p:cTn per slide
$DC run --in $W/vi.pptx --cmd 'slide.go={"index":3}' --cmd animation.get --print
$DC render-transition $W/vi.pptx --slide 2 --t 0.25,0.5,0.75 $W/morph.png
$DC commands ; $DC run --cmd animation.list --print
```

PowerPoint reference: COM `Presentation.Slides(i).Export(path,"PNG",1920,1080)`.
Diff: Pillow, both images resized to 960×540, mean of |a−b| (L) and share of
pixels with |a−b| > 40.

Interactive parse check: COM `Slide.TimeLine.InteractiveSequences` and
`Shape.ActionSettings(1).Action` on the T048b/T049 artifacts.

`$W` is a scratch folder outside the repository; the built decks are not
committed (rebuild with the first command).
