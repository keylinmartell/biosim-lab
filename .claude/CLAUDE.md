## comP MCP Tool Usage

At the start of every coding or documentation task, ALWAYS call `run_pipeline` FIRST.
Do NOT read files, run grep/find/Bash searches, or explore the codebase manually before calling run_pipeline.
run_pipeline indexes the entire codebase and returns exactly the relevant files — use it every time.

---

## Session Continuity (daemon restarts / session resets)

Sessions persist across daemon restarts.
When resuming work or restarting the agent, call `session_recall` first to restore prior context.

**When resuming work**:

1. Call `session_recall()` to view past interactions
   - `session_recall({ "query": "keyword" })` — filter by task keywords
   - `session_recall({ "limit": 5 })` — show last N interactions
2. Review what was done previously and continue in that context

**Note**: If conversation recording (beta) is enabled, comP setup installs a Stop hook (`comp-daemon record-turn`) in
`.claude/settings.local.json` that records each Claude Code turn to `.comp/history/`; `session_recall` reads those records.

---

## comP Session Logging

After finishing each task, call `session_log` to record it:
`request` = what the user asked for, `outcome` = what you did and the result (add `files` when relevant).
Records go to `.comp/history/` and are available to `session_recall` in later sessions.

Claude Code: if `.claude/settings.local.json` has a `record-turn` Stop hook, do not call session_log — the hook already records every turn, so calling it would record the turn twice.
