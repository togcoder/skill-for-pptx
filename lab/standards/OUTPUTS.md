# Where files go

| File | Place | Committed? |
|---|---|---|
| Verification decks, documents, sheets, SVGs, PDFs made by a task | `experiments/<ID>-…/artifacts/` | yes, if small (< 5 MB each) and synthetic |
| Previews, renders, contact sheets | `experiments/<ID>-…/preview/` | yes, if small |
| Inputs and specs of a task | `experiments/<ID>-…/inputs/` | yes |
| Reusable example specs | `examples/<domain>/` | yes |
| Scratch, intermediate builds, large renders, videos | `workspace/` | **no** (git-ignored) |
| Reference media from outside (templates, decks, fonts) | `local-media/` | **no** |
| Legacy E001–T006 decks | `output/` | frozen: add nothing |

**Never write output files to the repository root**, even when asked to "make
a test slide". Put them in the current task's `artifacts/`. Without a task,
use `workspace/`.

`python3 lab/tools/check_layout.py` fails on new root entries, on office or
media files at the root, and on new files in `output/`.
