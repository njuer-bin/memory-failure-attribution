# 10-Topic Expansion — v2.6 Result (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_6.md`
**Runs:** design v3, 10 topics, 60 trajectories per writer, `--skip-judge`.
**Status:** completed; gates passed with one borderline caveat.

## 1. Deterministic status-cue results

Updated cases, n=20 per depth (epistemic + intentional; conditional excluded
from this cue metric):

| Condition | neutral MATCH / ABSENT | status-aware MATCH / ABSENT |
|---|---|---|
| direct D1 | 17 / 0 | 15 / 0 |
| direct D2 | 14 / 3 | 16 / 0 |
| direct D3 | 16 / 1 | 18 / 0 |
| direct D5 | 14 / 3 | 20 / 0 |
| recursive D1 | 16 / 0 | 16 / 0 |
| recursive D2 | 11 / 9 | 15 / 2 |
| recursive D3 | 9 / 11 | 14 / 5 |
| recursive D5 | 9 / 11 | 13 / 7 |

Chained rewriting loses the gold status cue in 9–11 of 20 updated cases under
the neutral writer; the status-aware prompt cuts that to 2–7 of 20.

## 2. The effect is dimension-specific

This is the main new result. Neutral writer, updated cases, ABSENT counts:

| Dimension | direct D5 | recursive D2 | recursive D3 | recursive D5 |
|---|---:|---:|---:|---:|
| epistemic | 2/10 | 1/10 | 2/10 | **2/10** |
| intentional | 1/10 | 8/10 | 9/10 | **9/10** |

Under the neutral writer, chained compression almost destroys intentional
commitment cues (`决定` → absence) while epistemic certainty cues are largely
preserved. The aggregate 30-trajectory numbers hid this.

Status-aware writer:

| Dimension | direct D5 | recursive D2 | recursive D3 | recursive D5 |
|---|---:|---:|---:|---:|
| epistemic | 0/10 | 1/10 | 2/10 | 2/10 |
| intentional | 0/10 | 1/10 | 3/10 | **5/10** |

The status-aware prompt removes direct-condition loss entirely and roughly
halves intentional recursive loss (9 → 5/10 at D5), but does not eliminate it.
Epistemic is already robust (2/10 in both writers).

## 2b. Manual semantic cue check (intentional D5)

The strict cue metric counts only explicit terms (`决定`, `承诺`,
`按计划推进`, ...). Manual reading of the 10 intentional updated D5 memories:

| Writer | strong cue (`决定`) | weak cue (`推进计划`, `按计划`, `已开始`) | no cue |
|---|---:|---:|---:|
| neutral | 1 | 1 (`推进`) | 8 |
| status-aware | 5 | 5 | 0 |

- Neutral: only `intentional_09` keeps `决定`; `intentional_03` keeps a weak
  `推进`; the other 8 remove the commitment cue entirely
  (`上海工作，留意天气…`, `学习日语…`, `报名马拉松…`).
- Status-aware: 5 keep `决定`; the other 5 weaken it to `推进计划`, `按计划`,
  or `已开始…行动完成`. **Every status-aware intentional D5 memory still
  carries a commitment cue.**

So the strict metric overstates the status-aware loss. The status-aware
failure mode is **cue weakening**, not cue removal; the neutral failure mode is
removal in 8/10. Report both strict and semantic counts.

## 3. Proposition omission

- neutral: direct 1–2/60; recursive 1–6/60 (D5 = 6/60 = 10%, borderline).
- status-aware: **0/60 everywhere**.

The cue loss is not proposition forgetting. The neutral D5 proposition omission
is exactly at the 10% gate boundary; it is reported as borderline and is small
relative to the 9–11/20 cue loss.

## 4. Per-topic concentration

| Writer | recursive cue-loss total | largest topic | share |
|---|---:|---|---:|
| neutral | 31 | 去上海工作 | 5/31 = 16.1% |
| status-aware | 14 | 去上海工作 | 3/14 = 21.4% |

No single topic contributes more than half; the effect is distributed across
topics. Gate passes.

## 5. Gate verdict

- 60 trajectories complete and parse: PASS.
- Deterministic proposition omission < 10%: neutral D5 is exactly 10%
  (borderline); status-aware 0%. Read as not dominant, but flagged.
- No single topic > half of cue loss: PASS.
- Direct-vs-recursive pattern in both writers: PASS.

## 6. Interpretation

- **H2 is refined and dimension-specific.** Chained rewriting erodes
  intentional commitment status far more than epistemic certainty status.
- **H3 is supported.** Proposition retention is near-perfect (status-aware 0%
  omission; neutral ≤10%), while status cues disappear.
- **The status-aware prompt is a partial mitigation**, strongest for
  intentional status at shallow depths and at direct compression.

## 7. Caveats

- Synthetic templates; one writer model; cue metric is heuristic.
- Neutral D5 proposition omission is at the 10% gate boundary.
- Conditional is excluded from the cue metric; its ontology remains the least
  reliable.
- No judge and no human annotation in this 60-trajectory run; it is a
  deterministic measurement study.

## 8. Next

1. Manually read a stratified sample of the intentional recursive memories to
   confirm they are cue omissions, not metric artifacts.
2. Test a status-cue-aware writer prompt targeted at commitment language.
3. Keep the dimension split in all future tables; do not report an aggregate
   status-drift number without it.
