# Blind annotation package

Label each row in `annotations.csv` independently. Do not open `key.csv`.

## Fields

- `evidence_sufficient_yes_no_uncertain`: do the listed gold evidence snippets
  contain enough information to answer the question and justify the reference
  answer? Judge the evidence against the reference answer, not against the
  model answer.
- `answer_correct_yes_no_uncertain`: is `model_answer` correct given the
  reference answer? Accept paraphrases, dates written differently but
  equivalent, and units stated equivalently. Mark `uncertain` when the model
  answer is ambiguous (e.g. names both an old and a new value).
- `notes`: optional, one short line (why uncertain, what is missing).

## Rules

1. Use only the row's own question, reference answer, gold evidence and model
   answer. Do not consult the benchmark or any external source.
2. Evidence sufficiency and answer correctness are independent: an answer can
   be correct by luck while the evidence is insufficient, and vice versa.
3. Temporal wording ("yesterday", "last Saturday", "last week") must be
   resolved against the dates in the evidence when present. If no date makes
   the expression resolvable, mark uncertain and note it.
4. Two annotators label independently. A third pass adjudicates disagreements.
