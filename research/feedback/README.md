# Owner feedback ledger

The owner's comments are kept here, separate from new work. This avoids the
confusion of 2026-11-04, when feedback and new requests in one session pulled
agents in two directions (T070, P5).

- One file per review session: `<YYYY-MM-DD>-<topic>.md`.
- Each comment is one numbered item: `F1`, `F2`, … Use the owner's words, or a
  paraphrase marked as such.
- The lead turns items into briefs. A brief cites the items it addresses
  (`addresses: 2026-11-04-triet-hoc F2`).
- An item is closed only by the owner. Mark it `[x]` with the date and the
  evidence they looked at. Agents may mark an item `proposed-fix: <task>`;
  they never close one.
- New requests do not go in this folder. They become briefs in
  `docs/ROADMAP.md` / `research/tasks/INDEX.md`.

Format:

```markdown
# <topic> — <date>
Deck/artifact reviewed: <path or link>

- [ ] F1 "<owner's words>" — proposed-fix: T0xx
- [x] F2 "<owner's words>" — closed 2026-11-10 after bench round 3 (votes.jsonl #12)
```

## Questions to the owner

Agents ask, the owner answers, everyone reads: `questions.md`.

```markdown
- [ ] Q3 (opencode, T074) Should the Morph rulebook include 4:3 decks? — answer: …
```

The owner answers inline and ticks the item. `coord.py board` and `coord.py claim` print
every open item, so all agents see the same answer.
