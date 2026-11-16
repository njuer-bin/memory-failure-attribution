# v2.4 Neutral-Writer Human Annotation Result (2026-11-16)

**Set:** `results/status_drift_v2_pilot/v24_full_neutral/annotation/`
**Items:** 120 per annotator (Raw / Direct D5 / Recursive D5 / Rewrite-matched D5).
**Annotators:** A and B, independent.
**Run:** `v24_full_neutral` (neutral writer, qwen2.5:7b writer/judge,
rewrite-matched, token logging).

## 1. Completion and agreement

- A: 120 rows, 0 missing, 0 invalid.
- B: 120 rows, 0 missing, 0 invalid.

| Field | Raw agreement | Cohen's kappa |
|---|---:|---:|
| proposition_identity | 0.858 | 0.366 |
| polarity | 0.908 | 0.702 |
| epistemic_status | 0.875 | 0.765 |
| intention_status | 1.000 | 1.000 |
| action_status | 0.967 | 0.927 |
| condition_status | 0.983 | 0.967 |
| unsupported_status_change | 0.900 | 0.764 |

The primary label has 12 disagreements, mostly `UNCLEAR` vs `NO` when one
annotator considers the proposition PARTIAL. The drift-rate conclusion is
reported with both individual and bounded (conservative/liberal) estimates.

## 2. Primary metric — Unsupported Status Drift Rate

| Condition | A (YES / preserved) | B (YES / preserved) |
|---|---:|---:|
| Raw | 0 / 30 = 0.0% | 0 / 30 = 0.0% |
| Direct D5 | 0 / 30 = 0.0% | 0 / 27 = 0.0% |
| Recursive D5 | 4 / 26 = 15.4% | 3 / 19 = 15.8% |
| Rewrite-matched D5 | 5 / 28 = 17.9% | 5 / 21 = 23.8% |
| **Overall** | 9 / 114 = 7.9% | 8 / 97 = 8.2% |

Bounded estimates across the 12 disagreements:

- **Conservative** (YES only if both annotators say YES): 7/97 = **7.2%**.
- **Liberal** (YES if either annotator says YES): 10/114 = **8.8%**.
- Recursive D5: 3/19 = 15.8% conservative, 4/26 = 15.4% liberal.
- Rewrite-matched D5: 4/21 = 19.0% conservative, 6/28 = 21.4% liberal.
- Raw and Direct D5: 0 in every estimate.

By dimension:

| Dimension | A | B |
|---|---:|---:|
| epistemic | 0/40 = 0.0% | 0/35 = 0.0% |
| intentional | 9/35 = 25.7% | 7/32 = 21.9% |
| conditional | 0/39 = 0.0% | 1/30 = 3.3% |

## 3. Comparison with the status-aware writer

Human-annotated unsupported drift, same protocol:

| Condition | neutral | status-aware |
|---|---:|---:|
| Overall | 7.2–8.8% | 4.2–4.3% |
| Recursive D5 | 15.4–15.8% | 6.9–7.4% |
| Rewrite-matched D5 | 19.0–21.4% | 10.0–10.7% |
| Intentional (all) | 21.9–25.7% | 7.5–7.9% |
| Epistemic (all) | 0.0% | 5.0% |
| Conditional (all) | 0.0–3.3% | 0.0% |

The neutral writer roughly doubles the human-annotated drift overall, and more
than doubles it at chained D5 and in the intentional dimension.

## 4. Disagreements (12)

Patterns:

- `UNCLEAR` vs `NO` when one annotator marks the proposition `PARTIAL`
  (e.g., conditional_00_U / conditional_04_U recursive D5, epistemic_00_S
  recursive D5, intentional_04_S recursive/rewrite D5).
- `YES` vs `UNCLEAR` on intentional_03_U recursive/rewrite D5: one annotator
  treats `推进计划` as commitment weakening (YES), the other as a PARTIAL
  proposition (UNCLEAR).
- One `UNCLEAR` vs `YES` on conditional_01_U rewrite D5: the memory states both
  the received scholarship and a not-satisfied condition.

These disagreements change the estimated rate by at most ~1.6 percentage points
and do not change the direction or the neutral > status-aware ordering.

## 5. Interpretation

- **Human labels confirm the neutral-writer chaining effect.** Raw and Direct D5
  have zero drift; Recursive D5 and Rewrite-matched D5 have 15–21%; the
  intentional dimension carries most cases (22–26%).
- **Status-aware mitigation is human-confirmed.** It roughly halves the drift at
  every chained condition.
- **Token mismatch remains a caveat.** Chained memories are ~25% shorter in
  tokens (16.1 vs 21.4 at D5), so a matched-token-budget follow-up is required
  before a causal recursion claim.
- The 12 disagreements should be adjudicated for a single final table; the
  bounded estimates are robust enough to support the qualitative conclusion.

## 6. Next

1. Adjudicate the 12 primary-label disagreements.
2. Build a matched-token-budget experiment (target the same final writer token
   count across direct/recursive/rewrite).
3. Compare human drift rates at matched token budgets before causal wording.
