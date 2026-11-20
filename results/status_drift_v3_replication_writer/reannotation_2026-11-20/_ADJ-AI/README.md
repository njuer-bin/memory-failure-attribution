# Archived AI-adjudicated run (not human)

These files are the first merge of the n=30 re-annotation, in which all 125
disputed items were filled with `adjudicator = ADJ-AI`. They are preserved for
audit only and **must not be described as human adjudication**.

- `adjudication_sheet_ADJ-AI.csv` — the filled sheet as returned.
- `adjudication_ADJ-AI.csv` — merged 210-row labels.
- `condition_table_ADJ-AI.csv`, `summary_ADJ-AI.json` — resulting summaries.

Observed at review: 30 primary-judgment disputes were all but one resolved to
annotator B's label; `STATUS_OMISSION` fell from 20 (old n=30 labels) to 5;
15 old omission items became `NO_DISTORTION`; 18 `EPISTEMIC` items received
`POSSIBLE` from a memory that only contains `考虑/打算` (an INTENTIONAL cue, not
an epistemic cue). A human adjudicator is redoing the 125 disputes in
`../adjudication_sheet.csv`.
