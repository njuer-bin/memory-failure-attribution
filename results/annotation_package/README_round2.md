# Round 2 — evidence-sufficiency re-annotation (gate field only)

Round 1 of the evidence-sufficiency field failed in a specific way: one
annotator defaulted to "yes" (agreement 0.89, kappa 0.0 — never said "no"
except through "uncertain"), while the other said "no" 37× with concrete
reasons. Kappa 0 between annotators means the task was not operationalized
tightly enough. This round fixes the instructions and re-labels only the
`evidence_sufficient_yes_no_uncertain` field on the same 200 rows.

## What changed from round 1

The round-1 wording asked whether the evidence "contains enough information
to answer the question and justify the reference answer". That invites a
topical match: "the evidence mentions the café, so it is about the café
question" → yes. The correct decision rule is stricter and mechanical:

> Mark `yes` only if the reference answer is **derivable** from the listed
> evidence — i.e. every fact the reference asserts appears in the evidence
> (explicitly or by trivial arithmetic/date arithmetic). Otherwise `no`.
> Mark `uncertain` only when the evidence contains the needed facts but a
> relative time phrase cannot be resolved to a date (rule 3 of round 1).

Apply this test one fact at a time (a checklist, not a gestalt):

1. Underline every fact the reference answer asserts.
2. For each, search the evidence for a sentence stating it.
3. If ANY asserted fact has no matching sentence → `no`.
4. If all facts match but a date expression ("last Friday") is needed and
   the row carries no resolvable date → `uncertain` (+ note).
5. If all facts match and all dates resolve → `yes`.

## Worked examples (from round-1 disagreement rows)

All of these are `no` under the checklist:

- **locomo-006** "How long did it take Jon to open his studio?" / reference
  "five months". Evidence mentions losing a job and a grand opening
  "tomorrow" — no duration is stated. `no` (missing fact: the duration).
- **locomo-021** "What precautionary sign did Melanie see at the café?" /
  reference "a sign stating that someone is not being able to leave".
  Evidence mentions "thoughtful signs" but never says what any sign reads.
  `no` (missing fact: the sign's content).
- **locomo-038** "What pets does Melanie have?" / reference "two cats and a
  dog". Evidence names cats (Bailey, Oliver, Oscar) but never a dog.
  `no` (missing fact: the dog).
- **locomo-051** "What books has Melanie read?" / reference "Nothing is
  Impossible", "Charlotte's Web". Evidence mentions one unnamed book and
  "Charlotte's Web" — the second title is missing. `no`.
- **longmemeval-052** "Who became a parent first, Rachel or Alex?" /
  reference "Alex". Evidence says Rachel has twins "growing up so fast"
  and Alex adopted "in January" — no dates let you order the two events.
  `no` (missing fact: comparative dates).

These are `yes` under the checklist (for contrast):

- Any row where every named entity, number and date in the reference has a
  supporting sentence, even if the wording differs (paraphrase is fine).
- A row whose reference is "4 days" and whose evidence gives two event
  dates 4 days apart — derivable by trivial date arithmetic. `yes`.

These are `uncertain` under the checklist:

- A row where the facts all match but the reference asserts a specific
  date that only a relative phrase ("last Tuesday") supports, and no
  absolute date appears anywhere in the row. `uncertain` + note.
  (Do NOT mark `yes` here — that was the round-1 leniency failure.)

## Procedure

1. Same files, same rows: `annotations_annotator{1,2}.csv`. Only the
   `evidence_sufficient_yes_no_uncertain` column changes (round-1 answer
   correctness stays as adjudicated).
2. Work independently; do not look at round-1 evidence labels of the other
   annotator or at `key.csv`.
3. Every `no` requires one short note naming the FIRST missing fact.
   Every `uncertain` requires a note naming the unresolvable phrase.
   (Notes were the adjudication evidence in round 1 — keep them up.)
4. Adjudication: disagreements get the checklist applied fact-by-fact; the
   side whose note names a fact the other side cannot point to in the
   evidence wins. Ties go to `no` (the conservative label, because an
   insufficient gate is what the E0 metric needs to detect).
5. Scoring: `experiments/score_annotations.py` as before, but round 2 is
   judged primarily on **kappa for the gate field** — the round-1 value
   was 0.0 and the instrument is not usable until two independent
   annotators clear, say, kappa ≥ 0.6 on this field.
