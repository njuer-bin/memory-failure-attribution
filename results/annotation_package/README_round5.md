# Round 5 — blind stage attribution (v2 pilot)

For each row you see one question, its reference answer, the gold evidence with
its session dates, and the memory items a system held at each lifecycle stage.
Mark the **first stage at which the gold evidence needed for the reference
answer is no longer present**.

## Labels (8 classes; `evolution` is not measured and is excluded)

`formation | storage | retrieval | rerank | context | none | E0 | uncertain`

- `none`: every measured stage still contains the needed evidence.
- `E0`: the gold evidence itself does not establish the reference answer
  (use the dates shown in `gold_evidence_dates` to resolve relative time).
- `uncertain`: the previews are insufficient to decide; add a note.

## What the previews mean

- `retrieval`: the system's full top-20 candidates (N shown in the header).
- `rerank` / `context`: the system's full top-10 (N shown in the header).
- `formation` / `storage`: two views of the stored items — the first 10 in
  session order and the top 10 by overlap with the gold evidence, with the
  total count in the header. **Operational rule: if the gold evidence does not
  appear in either view, treat the stage as missing.** This is a defined
  criterion, not a claim that the full store lacks it; say so in the analysis.
- `evolution` is excluded because it is unmeasured in both systems (empty for
  verbatim, constant for semantic). Do not use it as a label.

For verbatim rows the retrieval/rerank/context previews are the same ranking at
different cutoffs (20 / 10 / 10); that is a property of the system, not a
package error.

## Procedure

Two annotators, independent and blind; system identity is A/B and the key is
hidden. Use only the row. Do not open the key. Every non-`none` choice needs a
one-line note naming the absent evidence or the stage where it vanished.

Pilot acceptance: Cohen's kappa >= 0.70 on the 8-class stage label (also report
kappa on the classes actually used). If the pilot falls short, revise the task
shape before the full 100 questions.
