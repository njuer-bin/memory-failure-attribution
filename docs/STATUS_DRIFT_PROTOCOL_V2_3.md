# Status Drift Pilot — Protocol v2.3 (Rewrite-Matched Control)

**Status:** pre-registered; no v2.3 outputs exist yet.
**Branch:** `research/status-drift-v2-pilot`
**Scope:** adds a control condition to separate recursive dependency from
intermediate budget shrinkage. Dataset and prompts are unchanged.

## 1. Problem

The current design compares:

- `direct_d`: one compression from the full dialogue to budget `BUDGETS[d]`.
- `recursive_d`: `d` chained compressions with budgets
  `220 -> 180 -> 140 -> 120 -> 100`, judged at `d`.

`recursive_d` differs from `direct_d` in two ways:

1. it is **chained** (each step reads the previous memory), and
2. its **intermediate budgets shrink** (220, 180, 140, 120, 100).

The 30-run cannot say which factor produces the drift.

## 2. New condition

`rewrite_matched_d` keeps the chain and the number of calls but holds the
intermediate budgets at 220:

- `d=1`: one compression at 220 (identical to `direct_d1` and `recursive_d1`).
- `d=2`: `220 -> 180`.
- `d=3`: `220 -> 220 -> 140`.
- `d=5`: `220 -> 220 -> 220 -> 220 -> 100`.

The final budget equals `BUDGETS[d]`, and the number of chained writer calls
equals `d`, exactly as in `recursive_d`. Only the intermediate budgets differ.

## 3. What the contrasts mean

- `recursive_d - rewrite_matched_d`: effect of shrinking intermediate budgets
  with the chain held constant.
- `rewrite_matched_d - direct_d`: effect of chained dependency and additional
  calls with the final budget held constant.
- `recursive_d - direct_d`: the combined effect (the original contrast).

Call count is still confounded with chaining: any `d`-call chain is recursive.
The protocol reports this as a residual limitation, not a solved problem.

## 4. Pre-registered predictions

- **P8:** if the neutral-writer drift is driven mainly by intermediate budget
  shrinkage, `recursive_d` will be worse than `rewrite_matched_d`.
- **P9:** if it is driven mainly by chained dependency, `rewrite_matched_d`
  will show drift close to `recursive_d` and clearly worse than `direct_d`.
- **P10:** the status-aware writer will show little drift in
  `rewrite_matched_d`, matching its near-null `recursive_d` result.

## 5. Run plan

Run the neutral writer first (where the 30-run effect is), 30 trajectories,
seed 42, both judges. Run the status-aware writer second if the neutral result
is interpretable.

Command shape:

    --design v3 --limit 30 --writer-style neutral --rewrite-matched --skip-judge

Then judge with `qwen2.5:7b` and `gemma3:12b`.

## 6. Metrics

- Status accuracy by condition and depth.
- Deterministic proposition omission.
- Deterministic condition omission (conditional dimension).
- Both-judges-wrong candidates.
- Paired contrasts:
  - recursive minus rewrite-matched,
  - rewrite-matched minus direct,
  - recursive minus direct.
- Inter-judge agreement per condition.

Report raw counts and denominators. No significance tests.

## 7. Gates

Proceed to interpretation only if:

- inter-judge agreement ≥ 0.85 overall;
- deterministic proposition omission < 10%;
- all new both-judge errors are manually adjudicated;
- the three contrasts are reported with raw counts, not just rates.

## 8. Integrity

- v3 outputs remain unchanged; v2.3 writes to a separate directory.
- The new condition adds writer calls, not a new dataset.
- No claim about recursion until the rewrite-matched contrast is inspected.
