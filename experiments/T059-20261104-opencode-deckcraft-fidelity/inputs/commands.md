# T059 commands (Windows 11, PowerShell)

Environment measured on 2026-11-04:

| Item | Value |
|---|---|
| OS | Windows 11 x64 |
| Python | 3.13.5 (Anaconda) |
| python-pptx | 1.0.2 |
| Pillow | 13.0.0 |
| numpy | 2.2.6 |
| pywin32 | installed (COM) |
| Microsoft PowerPoint | 16.0, build 17932 (COM, desktop) |
| DeckCraft CLI | 0.13.1, `D:\artcraft\DeckCraft\deckcraft-cli.exe` |
| ffmpeg / ffprobe | 8.1.1 essentials |

Set `PYTHONUTF8=1` in the shell: this host's default code page is cp1258 and
several existing tests read files without an explicit encoding.

```powershell
$env:PYTHONUTF8 = "1"
$DC = "D:\artcraft\DeckCraft\deckcraft-cli.exe"
$EXP = "experiments/T059-20261104-opencode-deckcraft-fidelity"
$W = "workspace"
```

## 1. Frozen decks

```powershell
New-Item -ItemType Directory -Force $W/decks | Out-Null
Get-ChildItem examples/pptx/forge/*.json | ForEach-Object {
  python scripts/slide_forge.py build $_.FullName -o "$W/decks/$($_.BaseName).pptx"
}
Copy-Item experiments/T028-20261008-claude-morph-studio/output/T028_report_pro.pptx $W/decks/
Copy-Item experiments/T028-20261008-claude-morph-studio/output/T028_showcase_pro.pptx $W/decks/
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/build_kind_probe.py  # synthetic per-kind probe
```

Deck hashes are in `inputs/deck_hashes.txt`.

## 2. Static matrix, object kinds, critic parity

```powershell
python scripts/deckcraft_fidelity.py static `
  --decks $W/decks `
  --out $EXP/artifacts `
  --work $W/t059
```

The tool renders with PowerPoint `Slide.Export(1920x1080)` and with
`deckcraft-cli render --all --scale 2`, resizes both to 960x540, and diffs the
maximum channel difference. It writes `fidelity.csv`,
`fidelity_objects.csv`, `critic_parity.csv`, `critic_frames.csv`, one 3-up JPEG
per slide in `artifacts/diffs/`, and a contact sheet per deck in
`artifacts/static/`.

The probe is merged separately:

```powershell
python scripts/deckcraft_fidelity.py static --decks $W/decks/kind_probe.pptx `
  --out $W/probe_out2 --work $W/kind_probe_work2
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/merge_probe.py
```

## 3. Morph frames

The harness copies deck N-1 and N, strips slide 1's timing and incoming
transition, records a 1080p `CreateVideo` at 30 fps, detects the first changed
frame, and samples t = 0.25/0.5/0.75 of the transition duration from the XML
(`p14:dur`, 1500 ms for the Forge decks). DeckCraft frames come from:

```powershell
$DC render-transition <deck.pptx> --slide <N-1> --t 0.25,0.5,0.75 out.png
```

Batches used:

```powershell
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/vi_chuyen_doi_so.pptx --slides 2,3,4,5,6,7,8,9 --work $W/morph --out $W/morph_out/vi_chuyen_doi_so --pp-static $W/t059/pp/vi_chuyen_doi_so
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/coffee_report_photos.pptx --slides 3,5,10 --work $W/morph --out $W/morph_out/coffee_report_photos --pp-static $W/t059/pp/coffee_report_photos
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/coffee_office_dynamic.pptx --slides 4 --work $W/morph --out $W/morph_out/coffee_office_dynamic --pp-static $W/t059/pp/coffee_office_dynamic
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/coffee_report.pptx --slides 4 --work $W/morph --out $W/morph_out/coffee_report --pp-static $W/t059/pp/coffee_report
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/vi_brand_seed.pptx --slides 3 --work $W/morph --out $W/morph_out/vi_brand_seed --pp-static $W/t059/pp/vi_brand_seed
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/T028_report_pro.pptx --slides 2,4,6 --work $W/morph --out $W/morph_out/T028_report_pro --pp-static $W/t059/pp/T028_report_pro
python scripts/deckcraft_fidelity.py morph-batch --pptx $W/decks/T028_showcase_pro.pptx --slides 2,7,10 --work $W/morph --out $W/morph_out/T028_showcase_pro --pp-static $W/t059/pp/T028_showcase_pro

python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/aggregate_morph.py
```

If PowerPoint returns `RPC server is unavailable` after a long COM session,
rerun the single slide with `morph --slide N`; the video encoding is
deterministic (a same-file control gives 0.0 diff).

## 4. Round trip

```powershell
foreach ($d in @('vi_chuyen_doi_so','vi_brand_seed','coffee_report',
                 'coffee_report_photos','coffee_office_dynamic',
                 'T028_report_pro','T028_showcase_pro')) {
  python scripts/deckcraft_fidelity.py roundtrip `
    --pptx "$W/decks/$d.pptx" --out "$W/rt_out/$d" --work $W/rt
}
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/aggregate_rt.py
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/rt_media.py
```

`roundtrip` calls `deckcraft-cli convert IN OUT.pptx`, compares the timing
inventory (effects, props, children, transition, `p:cTn`, `p:cond`,
`p:graphicEl`), asks PowerPoint for `TimeLine.MainSequence` effect and behavior
counts on both files, and writes `roundtrip*.csv`.

Static end-state check of the round-tripped deck (PowerPoint export only):

```powershell
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/rt_static.py
```

## 5. Animation playback (original vs round trip)

A one-slide deck with a leading blank slide is recorded twice, so the target
slide's click effects auto-advance. Frames are aligned on target appearance and
compared by index; a same-file control gives 0.0, proving the capture is
deterministic.

```powershell
python scripts/deckcraft_fidelity.py animation --original $W/decks/vi_chuyen_doi_so.pptx --roundtrip $W/rt/vi_chuyen_doi_so-roundtrip.pptx --slide 7 --work $W/anim --out $W/anim_out/vi7
python scripts/deckcraft_fidelity.py animation --original $W/decks/coffee_office_dynamic.pptx --roundtrip $W/rt/coffee_office_dynamic-roundtrip.pptx --slide 3 --work $W/anim --out $W/anim_out/coffee3
python scripts/deckcraft_fidelity.py animation --original $W/decks/coffee_office_dynamic.pptx --roundtrip $W/rt/coffee_office_dynamic-roundtrip.pptx --slide 4 --work $W/anim --out $W/anim_out/coffee4
python scripts/deckcraft_fidelity.py animation --original $W/decks/coffee_report.pptx --roundtrip $W/rt/coffee_report-roundtrip.pptx --slide 7 --work $W/anim --out $W/anim_out/coffee_report7
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/control_video.py        # same-file control; expect 0.0
python experiments/T059-20261104-opencode-deckcraft-fidelity/scripts/merge_anim.py
```

## 6. Tests

```powershell
python -m unittest tests.test_deckcraft_fidelity -v
python -m unittest discover -s tests -v
python lab/tools/check_layout.py
```

## Scratch

Everything under `workspace/` is git-ignored: built decks, PowerPoint exports,
DeckCraft exports, videos, extracted frames. Only `artifacts/` (CSV + JPEG) and
`inputs/` are committed.
