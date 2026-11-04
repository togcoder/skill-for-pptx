# Decisions that bind every agent

These are decided, not proposals. Only the lead and the owner change them. An
agent who disagrees writes the case in its REPORT and asks the owner in
`research/feedback/questions.md`. It does not work around a decision in code.

`python lab/tools/coord.py claim …` prints the decisions that apply to the
capability you claim. `lab/capabilities.json` links each capability to its
decisions.

| ID | Decision | Why (evidence) | Since |
|---|---|---|---|
| D001 | **The owner's eye is the measure of quality.** Critic scores, narrative scores and "overall" are technical checks, not evidence that a deck is better. "Better" needs the owner's A/B vote (T071). | T068/T069b decks score 4.99 / narrative 5.00 with empty cards, a clipped title and scaffold text (`experiments/T070-…/preview/critic-499-vs-eye.jpg`). | T070 |
| D002 | **One owner per file, one canonical implementation per capability.** Every script is registered in `lab/capabilities.json`. A second implementation of a registered capability needs the lead's decision before it is written; otherwise extend the canonical module. | Three `interactiveSeq` writers (fixed T061); two style systems (T043 `theme_engine`, T067 VisualStyle/1); two script systems (`motion_script`, `deck_director`); 27 of 103 scripts were in no domain card. | T083 |
| D003 | **Script first.** A new deck is built only after its script has been read and approved as text: by the owner, or by a model from a stronger family than the builder. | The owner: motion thinking is driven by the script. A script read after building costs a full rebuild. | T078 |
| D004 | **One script format.** It is the Markdown of `motion_script.py` (`## Slide`, `[click]`) plus a `claim:` line per scene, as T067 proposed. `direction.json` is compiled from it, not hand-written. `scaffold` emits empty slots with guiding questions, never prose. | T068 ignored T067's proposal and started a second format. `scaffold_direction()` writes filler such as "hành động quyết liệt là chìa khóa đạt kết quả vượt bậc", which shipped in the T069b proof deck. | T078 |
| D005 | **Never invent content.** Missing figures, steps or labels are a coded error back to the author, never "100%", "Bước hoàn thiện" or "Chỉ số 1". | `deck_director.compile_direction` fills those values. | T070 |
| D006 | **Single writer for lab-wide documents.** Only the lead writes `HANDOFF.md`, `docs/ROADMAP.md`, `docs/SCRIPT_TRACK.md`, this file and `lab/capabilities.json`. Agents report through their INDEX row, REPORT, CHANGELOG entry and PR description. `coord.py board` shows the live state. | Each agent rewrote HANDOFF with its own priorities. After T069 the HANDOFF planned a "T070" that collided with the lead's T070. | T083 |
| D007 | **Start every task with `coord.py claim`.** It reserves the ID against `main` and every open branch, creates your branch and a separate worktree, and prints your briefing. Never edit the shared checkout. | Duplicate IDs T042, T043, T047, T048, T049, T069a/b. An agent's uncommitted edit sat in the owner's checkout while other agents worked there. | T083 |
| D008 | **Builder and critic come from different model families** (Claude / Gemini / DeepSeek). Merges into `main` are done by the lead or the owner, after CI and the review. | Gemini built and Gemini reviewed T068/T069b. A single agent built T058–T065 with no outside review. | T057, T070 |
