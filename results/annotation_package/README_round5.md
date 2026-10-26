# Round 5 — blind stage attribution (pilot)

For each row you see one question, its reference answer, the gold evidence, and
the memory items a system held at six lifecycle stages (previews, truncated).
Mark the **first stage at which the gold evidence needed for the reference
answer is no longer present**. Use only this row.

- `formation` / `storage` / `evolution` previews are the items most textually
  related to the gold evidence (not the full store).
- `retrieval` / `rerank` / `context` previews are the system's own ordered
  context at that stage.
- Mark `none` when every stage still contains the needed evidence.
- Mark `E0` when the gold evidence itself does not establish the reference
  answer (the question is unanswerable from the benchmark evidence).
- Mark `uncertain` when the previews are insufficient to decide; add a note.

System identity is hidden (A/B). Do not open the key. Two annotators work
independently; disagreements are adjudicated blind. Every non-`none` choice
needs a one-line note naming the absent evidence or the stage where it vanished.

Pilot acceptance: Cohen's kappa >= 0.70 on the stage label. If the pilot falls
short, the task shape is revised before the full 100 questions.
