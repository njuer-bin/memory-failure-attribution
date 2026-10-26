# Stage annotation protocol — round 5 (blind, two annotators)

Status: protocol draft, 2026-10-26. Governed by
`docs/CCF_B_DECISION_PLAN_2026-10-26.md` (Stage A). This is the measurement
gate that must clear **Cohen's κ ≥ 0.70** before the Stage-C intervention or
any paper-grade stage claim.

## What is being annotated

Two tasks on the LoCoMo n=100 fingerprint questions
(`results/systems_locomo_n200_fixedgate/`, `limit: 100`):

1. **Fact-level evidence audit.** For each reference answer, the atomic facts
   are pre-authored (round-3 format, `README_round3.md`). The annotator marks
   each fact present / absent / uncertain in the listed gold evidence. This
   validates the E0/gate input.
2. **Stage attribution.** For each (question, system) pair, the annotator marks
   the first lifecycle stage at which the gold evidence needed for the
   reference answer is no longer present:
   `formation | storage | evolution | retrieval | rerank | context | none | E0 | uncertain`.

Task 2 is the new one; it is not a restatement of the automatic label. The
annotator sees the actual memory items at each stage and decides presence
independently.

## Materials and prerequisite

The stored comparison rows contain stage `found/missing` ids but **not item
texts**, so a trace dump must be generated before annotation:

- `semantic` and `verbatim`: re-run locally; no LLM ingestion.
- `summary`: requires the session summaries. Options, in order of preference:
  (a) re-ingest with the answer model (~19 calls/question ≈ 1,900 calls,
  ≈3 h at current latency); (b) use raw session text as a **diagnostic
  proxy** and label it as such; (c) restrict Task 2 to semantic+verbatim
  first, and add summary after (a). Do not silently substitute the proxy for
  a system result.

Each row in the dump shows, per stage: the question, reference answer, gold
evidence text, and up to K item previews (id + first 300 chars) that the
system held at that stage. System identity is anonymised as A/B/C; the
automatic failure label and gate status are hidden.

## Blinding and independence

- Two annotators, independent; do not open the hidden key or each other's sheet.
- Row order shuffled; system labels A/B/C fixed per row but not explained.
- A third adjudication pass resolves disagreements; ties go to `uncertain`
  (not to the automatic label).
- Every `no`/`uncertain` in Task 1 and every stage choice other than `none` in
  Task 2 gets a one-line note citing the missing item or the stage where it
  disappeared.

## Fields and workbook

`round5_stage_attribution.csv` (one row per question × system):

| field | content |
|---|---|
| row_id | opaque id |
| system_blind | A / B / C |
| question / reference_answer / gold_evidence | as in the run |
| stage_formation / storage / evolution / retrieval / rerank / context | item previews (K=5, 300 chars) |
| annotated_first_loss_stage | formation / storage / evolution / retrieval / rerank / context / none / E0 / uncertain |
| confidence | high / medium / low |
| notes | required unless stage = none |

`round5_fact_audit.csv` (one row per fact): reuses the round-3 schema, extended
to all 100 LoCoMo questions.

## Scoring and acceptance

- Task 1: fact-level Cohen's κ (yes/no co-decided), agreement, uncertain share.
- Task 2: Cohen's κ on the 9-way stage label; **confusion matrix** vs the
  automatic label (reported, not used for acceptance); uncertain share.
- Acceptance: **κ ≥ 0.70 on both tasks**; no acceptance on the basis of the
  automatic-label confusion alone.
- Pilot: 20 rows first. If pilot κ < 0.70, revise the task shape (e.g. show
  fewer stages at a time, or split "which stage first loses gold" from
  "does the final context contain gold"), not just the wording; re-pilot.

## What this gate decides

- Pass → Stage B (architecture ablation) and, later, Stage C intervention may
  use human-confirmed stage labels.
- Fail → do not run Stage C on automatic labels; either re-pilot the task or
  narrow the paper to measurement contributions that do not require stage
  labels (oracle ladder, gate/judge audit).

## Cost and coordination

- Annotation time: 100 questions × 3 systems = 300 stage rows plus ~200–300
  fact rows; estimate 6–10 hours per annotator across two sittings.
- Trace-dump API cost depends on the summary option; semantic+verbatim alone
  cost no API.
- This protocol needs the user to recruit two annotators; the package
  generator and key are produced only after the trace-dump decision, so the
  workbook annotators see contains real item previews rather than placeholder
  ids.
