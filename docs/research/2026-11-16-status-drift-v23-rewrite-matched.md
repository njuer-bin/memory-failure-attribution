# Rewrite-Matched Control — v2.3 Result (2026-11-16)

**Protocol:** `docs/STATUS_DRIFT_PROTOCOL_V2_3.md`
**Run:** design v3, neutral writer, 30 trajectories, `--rewrite-matched`, seed 42.
**Judges:** qwen2.5:7b and gemma3:12b.
**Status:** completed; gates passed.

## 1. Result

Inter-judge agreement: 350/390 = 0.897 (≥0.85).

Both-judge-correct and both-judge-wrong counts by condition:

| Condition | both correct | both wrong |
|---|---:|---:|
| raw | 30/30 | 0 |
| direct d1 / d2 / d3 / d5 | 29 / 28 / 28 / 27 | 0 / 0 / 0 / 1 |
| recursive d1 / d2 / d3 / d5 | 29 / 20 / 17 / 16 | 0 / 2 / 9 / 11 |
| rewrite-matched d1 / d2 / d3 / d5 | 29 / 19 / 17 / 15 | 0 / 3 / 9 / 11 |

Paired both-correct contrasts across d1/d2/d3/d5:

| Contrast | A both-correct | B both-correct | A-only | B-only |
|---|---:|---:|---:|---:|
| recursive vs rewrite-matched | 82 | 80 | 3 | 1 |
| rewrite-matched vs direct | 80 | 112 | 0 | 32 |
| recursive vs direct | 82 | 112 | 2 | 32 |

Deterministic proposition omission: 0–2/30 in every condition.
Deterministic condition omission (conditional, per depth):

- direct: 0/10 at every depth.
- recursive: 3/10 at D2, 4/10 at D3, 5/10 at D5.
- rewrite-matched: 4/10 at D2, 4/10 at D3, 4/10 at D5.

## 2. Interpretation

**The drift is caused by chained rewriting, not by shrinking intermediate
budgets.**

- Holding the intermediate budgets at 220 (`rewrite_matched`) produces the same
  degradation as the shrinking schedule (`recursive`): D3 17 vs 17 both-correct,
  D5 15 vs 16; paired A-only/B-only 3/1.
- Both chained conditions are far worse than a single compression to the same
  final budget (`direct`): D5 27 vs 15–16 both-correct; direct-only 32 versus
  0–2.
- Proposition omission stays at 0–2/30. The loss is status-specific (H3), not
  proposition forgetting.

So H2 is refined: **recursive compression adds drift because the writer
re-edits its own output, not because the budget shrinks.**

This is consistent with the v3 result and with the neutral-writer cue-loss
pattern (`确认`/`决定` disappearing at D3/D5).

## 3. Caveats

- The v2.3 writer run is a second neutral run. Its direct/recursive memories
  differ from the v3 run in 106/270 cells despite the same seed and prompts.
  Ollama is therefore **not fully deterministic** across processes. All
  statements above are within-run contrasts, which is the correct comparison.
- No status-aware rewrite-matched run yet; P10 is untested.
- Conditional remains the least reliable dimension; both chained conditions
  lose the condition status in 3–5/10 items.
- Assistant adjudication only; synthetic templates; n=30.

## 4. Next steps

1. Run the status-aware rewrite-matched control to test P10.
2. Manually adjudicate the new both-wrong items (mainly conditional and
   intentional) before external claims.
3. Add repeated-run variance (2–3 seeds) to quantify the nondeterminism and
   avoid treating single-run differences as effects.
