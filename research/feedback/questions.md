# Questions from agents to the owner

Format and rules: `README.md` in this folder. Open items are printed by `lab/tools/coord.py`.

- [x] Q1 (claude, T083) Branch protection on `main` (require a PR and green CI before merge): may the lead turn it on? Every agent pushes with your GitHub account, so it cannot tell agents apart. It does stop direct pushes to `main`, which happened in T043/T047–T049. — answer (owner, 2026-11-04): **no.** Merges into `main` stay a convention: the lead or the owner merges, after CI (D008).
- [x] Q2 (claude, T083) Should agents also use GitHub Issues for two-way talk with you (one issue per task, notifications on your phone)? Or is this folder enough? — answer (owner, 2026-11-04): **no Issues.** The owner works directly with each agent. Agents talk to each other through the repository: `coord.py board` / `claim`, PR descriptions, this file and `lab/DECISIONS.md`.
- [x] Q3 (claude, T083) This machine has an MCP server `a12-hub` (task_claim, task_send, document_write, event_list) that fails to connect. Is it a coordination hub you want the agents to use? — answer (owner, 2026-11-04): **no, it is a dead project.** Removed from the user MCP config (`claude mcp remove a12-hub -s user`).
