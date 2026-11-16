# v2.4 Full Pilot — Run and Annotation Set (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PILOT_PROTOCOL.md` (v2.4)
**Run:** design v3, 30 trajectories, qwen2.5:7b writer and judge,
`--rewrite-matched`, seed 42.
**Fingerprint:** `1ca412a6ea85289266d331ab56277271e1ae4c0a6c965dea3e744e0dce524fed`
**Output:** `results/status_drift_v2_pilot/v24_full/`

## 1. Pipeline checks

- 30/30 trajectories completed; **0 errors**.
- 0 invalid/parse-error predictions and 0 missing predictions in every condition.
- Every condition has a memory, judge output, Unicode/byte size, topic-mention
  flag, and condition-marker diagnostic.
- `run_config.json` contains the canonical fingerprint; rewrite-matched is on.
- Topic-mention rate 100% (lexical diagnostic only).

## 2. Provisional judge metrics (do not interpret as the result)

| Condition | valid | accuracy | condition heuristic |
|---|---:|---:|---:|
| raw | 30 | 0.833 | 0.5 |
| direct D1/D2/D3/D5 | 30 | 0.733 / 0.667 / 0.767 / 0.667 | 1.0 / 0.9 / 0.9 / 0.9 |
| recursive D1/D2/D3/D5 | 30 | 0.767 / 0.767 / 0.767 / 0.733 | 1.0 / 1.0 / 1.0 / 0.9 |
| rewrite-matched D1/D2/D3/D5 | 30 | 0.733 / 0.733 / 0.733 / 0.700 | 1.0 / 1.0 / 1.0 / 1.0 |

Paired error-rate differences (recursive minus direct):
`D1 -0.033, D2 -0.100, D3 0.000, D5 -0.067`.

Recursive minus rewrite-matched is `-0.033` at every depth; rewrite-matched
minus direct is between `-0.067` and `+0.033`.

**These judge metrics do not show a recursion penalty.** They are dominated by
the uncalibrated judge: the raw conditional condition-marker heuristic is only
0.5 because the judge inverts `条件尚未满足` to `CONDITION_SATISFIED`, and
explicit confirmations with trailing qualifiers (`确认…未购`, `确认…未确定时间`)
are downgraded to `POSSIBLE`. The same model writes and judges. Per the v2.4
protocol, `cpsd_judge_provisional` and these accuracies are exploratory, not
confirmatory.

## 3. Annotation set (primary measurement)

Generated with `experiments/make_annotation_set.py`:

- **120 items per annotator**: 30 trajectories × Raw / Direct D5 / Recursive D5 /
  Rewrite-matched D5.
- Balanced gold statuses: 20 each of POSSIBLE, CERTAIN, CONSIDERING, COMMITTED,
  CONDITION_ACTIVE, CONDITION_SATISFIED.
- Files:
  - `annotation/annotation_items.csv` — one row per item, with memory and
    dialogue text.
  - `annotation/annotator_A.csv`, `annotation/annotator_B.csv` — template rows
    with blank label fields, one per annotator.
  - `annotation/prevalence.json` — item count and gold-status counts.

Each annotator reads the full dialogue, the target proposition, and the specific
memory, then labels proposition identity, polarity, the applicable status,
action status, condition status, evidence turns, and unsupported status change.
Agreement is computed per field before adjudication.

## 4. Gate status

- Pipeline gate: **PASS** (complete, no unreported errors, fingerprint, sizes,
  interpretable labels).
- Phenomenon gate: **PENDING** human annotation. The LLM-judge metrics cannot
  establish or refute unsupported status drift.

## 5. Next

1. Two annotators independently label all 120 items per annotator.
2. Compute raw agreement and Cohen's kappa per field; adjudicate disagreements.
3. Compute the primary Unsupported Status Drift Rate from human labels,
   conditioned on proposition identity PRESERVED.
4. Add token-level usage logging and a genuinely matched final-budget
   experiment before any causal recursion claim.
