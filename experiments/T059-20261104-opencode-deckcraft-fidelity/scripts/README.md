# T059 helper scripts

These are research scripts, not product code. Run them from the repository root
after `inputs/commands.md` has produced the `workspace/` renders.

| Script | Purpose |
|---|---|
| `build_kind_probe.py` | builds the synthetic per-kind deck (`workspace/decks/kind_probe.pptx`) |
| `merge_probe.py` | replaces the `kind_probe` rows in `artifacts/fidelity*.csv` |
| `aggregate_morph.py` | merges per-deck Morph runs into `morph*.csv` and strips |
| `aggregate_rt.py` | merges per-deck round trips into `roundtrip*.csv` |
| `rt_media.py` | shape/media inventory original vs round trip (`roundtrip_media.csv`) |
| `control_video.py` | same-file video control; must print 0.0 |
| `timewarp.py` | best-match frame offset for one animation slide |
| `make_tables.py` | prints the Markdown tables used in REPORT.md |
| `make_headline.py` | builds `artifacts/headline.jpg` |
| `write_hashes.py` | rewrites `inputs/deck_hashes.txt` |

The authoritative renderer/compare logic is `scripts/deckcraft_fidelity.py`
(marked EXPERIMENTAL). These helpers only aggregate or visualise its output.
