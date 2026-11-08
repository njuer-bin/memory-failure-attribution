Run one bounded, evidence-driven research cycle.

1. Follow the start-of-run recovery and safety rules in `CLAUDE.md`.
2. Inspect git status and branch. Do not overwrite uncommitted changes.
3. Read the charter, current state, backlog, decision log, stop conditions, protocol, related-work matrix, and research log.
4. Select exactly one highest-value unblocked task. Prefer reducing uncertainty over writing more code.
5. Use the relevant specialist subagents:
   - literature-scout for papers/artifacts;
   - experiment-designer for design and confounds;
   - skeptical-reviewer for claims and novelty;
   - statistics-auditor for sample and analysis.
6. Independently verify important claims against primary sources or executable artifacts.
7. Perform the bounded task. Do not start expensive experiments or change the core question without explicit approval.
8. Update the durable state files and append a dated research-log entry.
9. Inspect the diff, validate changed JSON/YAML/scripts where possible, run relevant tests, and commit only verified changes to `research/memory-filtering-protocol`.
10. Report actual work, sources, files, commit, validation, limitations, next task, and any human decision required.

If blocked, document the blocker and work on the next independent low-risk task. Do not manufacture progress.