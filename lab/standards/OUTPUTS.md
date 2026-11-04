# Where files go

| File | Place | Committed? |
|---|---|---|
| Verification decks, documents, sheets, SVGs, PDFs made by a task | `experiments/<ID>-…/artifacts/` | yes, if small (≤ 2 MB each, ≤ 10 MB per task) and synthetic |
| Previews, renders, contact sheets | `experiments/<ID>-…/preview/` | yes, if small |
| Inputs and specs of a task | `experiments/<ID>-…/inputs/` | yes |
| Reusable example specs | `examples/<domain>/` | yes |
| Scratch, intermediate builds, large renders, videos | `workspace/` | **no** (git-ignored) |
| Reference media from outside (templates, decks, fonts) | `local-media/` | **no** |
| Legacy E001–T006 decks | `output/` | frozen: add nothing |

**Never write output files to the repository root**, even when asked to "make
a test slide". Put them in the current task's `artifacts/`. Without a task,
use `workspace/`.

## Size cap (T065)

Committed artifacts: **2 MB per file, 10 MB per task.** A bigger asset stays
local: keep the source in git-ignored `local-media/` or `workspace/`, commit
its SHA-256 and the command that rebuilds it, and describe the result in the
REPORT. The cap is a **warning** in `check_layout.py` for one cycle, so the
current tree and in-flight branches are not broken while they are cleaned up.

Whether Git LFS replaces this rule is an **open owner decision** (T065): LFS
would let large decks live in the repository, but it needs per-clone setup and
a storage quota, and the lab's decks are synthetic inputs, not deliverables.
Until the owner decides, the cap stands and no LFS pointer is created.

`python3 lab/tools/check_layout.py` fails on new root entries, on office or
media files at the root, on new files in `output/`, on duplicate task IDs in
`research/tasks/INDEX.md`, and on Markdown that is not UTF-8, starts with a
BOM, carries C0/C1 control characters, or contains mojibake markers (`Ã`,
`â€`, `á»`, `Ä‘` outside an inline code span). A line that has to quote the
damage on purpose ends with `<!-- allow-mojibake -->`; nothing else is exempt.
It warns, without failing, on committed files over the size cap.
