# v2.4 Neutral-Writer Human Annotation Result (2026-11-16)

**Set:** `results/status_drift_v2_pilot/v24_full_neutral/annotation/`
**Items:** 120 per annotator (Raw / Direct D5 / Recursive D5 / Rewrite-matched D5).
**Annotators:** A and B, two independent manual annotations. (An earlier
gold-derived B was withdrawn and re-annotated manually; see the correction
note.)
**Run:** `v24_full_neutral` (neutral writer, qwen2.5:7b writer/judge,
rewrite-matched, token logging).

## 1. Completion and agreement

- A: 120 rows, 0 missing, 0 invalid.
- B: 120 rows, 0 missing, 0 invalid.

| Field | Raw agreement | Cohen's kappa |
|---|---:|---:|
| proposition_identity | 0.925 | 0.540 |
| polarity | 0.917 | 0.727 |
| epistemic_status | 1.000 | 1.000 |
| intention_status | 1.000 | 1.000 |
| action_status | 1.000 | 1.000 |
| condition_status | 1.000 | 1.000 |
| **unsupported_status_change** | **0.942** | **0.849** |

The primary drift label now has genuine inter-annotator reliability
(kappa 0.849).

## 2. Primary metric — Unsupported Status Drift Rate

| Condition | A (YES / preserved) | B (YES / preserved) |
|---|---:|---:|
| Raw | 0 / 30 = 0.0% | 0 / 30 = 0.0% |
| Direct D5 | 0 / 30 = 0.0% | 0 / 29 = 0.0% |
| Recursive D5 | 4 / 26 = 15.4% | 3 / 22 = 13.6% |
| Rewrite-matched D5 | 5 / 28 = 17.9% | 4 / 24 = 16.7% |
| **Overall** | 9 / 114 = 7.9% | 7 / 105 = 6.7% |

Bounded estimates:

- Conservative (YES only if both annotators say YES): 7/105 = **6.7%**.
- Liberal (YES if either says YES): 9/114 = **7.9%**.

By dimension:

| Dimension | A | B |
|---|---:|---:|
| epistemic | 0/40 = 0.0% | 0/39 = 0.0% |
| intentional | 9/35 = 25.7% | 7/32 = 21.9% |
| conditional | 0/39 = 0.0% | 0/34 = 0.0% |

## 3. Comparison with the status-aware writer

| Condition | neutral (two manual annotators) | status-aware (A-only) |
|---|---:|---:|
| Overall | 6.7–7.9% | 4.2% |
| Recursive D5 | 13.6–15.4% | 6.9% |
| Rewrite-matched D5 | 16.7–17.9% | 10.0% |
| Intentional (all) | 21.9–25.7% | 7.5% |
| Epistemic (all) | 0.0% | 5.0% |
| Conditional (all) | 0.0% | 0.0% |

The neutral writer roughly doubles the status-aware drift at chained depth and
in the intentional dimension. The neutral estimate now has two-annotator
reliability; the status-aware estimate still rests on one manual annotator
because its B file remains gold-derived.

## 4. Interpretation

- **Two-annotator reliability confirms the neutral chaining effect.** Raw and
  Direct D5 are zero; Recursive D5 is 13.6–15.4%; Rewrite-matched D5 is
  16.7–17.9%; intentional carries 21.9–25.7%.
- **Status-aware mitigation is directionally confirmed but its reliability
  statistics are pending** a manual re-annotation of the status-aware B file.
- The token mismatch (chained outputs ~25% shorter) remains a causal caveat and
  motivates a matched-token-budget follow-up.

## 5. Next

1. Manually re-annotate the status-aware B file to obtain two-annotator
   reliability for the mitigation condition.
2. Build a matched-token-budget experiment.
3. Compare human drift rates at matched token budgets before causal wording.
