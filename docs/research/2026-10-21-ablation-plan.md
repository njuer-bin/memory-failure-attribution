# P2 ablation plan (2026-10-21)

Source: independent reviewer `kimi-k3` (opencode zen gateway, temperature 0,
streaming; raw output in
`docs/research/2026-10-21-ablation-review-kimi-k3.md`). The skill's default
Codex/GPT backend is not installed on this host; `gpt-6-luna` and
`gpt-5.6-luna` reject both Anthropic- and OpenAI-style calls with
`ModelProtocolUnsupported`, so the strongest protocol-compatible model was
used. Treat this as an external review, not the exact skill default.

## Reviewer's three blunt questions

1. Is the `agnostic` gain just self-check? If so, the lifecycle instrument adds
   nothing beyond generic verification.
2. Does targeting beat arbitrary repair? C2 is already dead: `path` routing
   reads gold (`path_target` calls `gold_ids`), so it was oracle-advantaged and
   *still* tied with `first_loss` (p=1.0).
3. Are the flips real? Every contrast rests on 7–19 discordant pairs, with
   cross-model judge kappa ≈ 0.03. Measurement, not ablation, is the binding
   constraint.

## Prioritised ablations

| ID | Ablation | What it tests | Priority |
|---|---|---|---|
| A1 | Placebo re-answer (second identical fresh baseline) | Nondeterminism / regression-to-mean floor | 1 |
| A2 | write-through only, all attributable failures | Does gold-free formation repair carry the bundle? | 1 |
| A3 | self-check only, all attributable failures | Is agnostic just verification? | 1 |
| A4 | wide context only (top_k 20, cap 8) | Context-assembly component | 1 |
| A5 | Mismatched routing (rotate labels) | Causal value of stage targeting (thesis test) | 1 |
| A6 | Oracle routing (gold first-loss stage) | Label noise vs routing null | 1 |
| A7 | Broadcast agnostic to all 200, shared store | ITT effect, harm on fresh-correct, E0 control, store pollution | 2 |
| A8 | Sham self-check (shuffled evidence) | Grounding vs second-chance effect | 2 |
| A9 | Sham context (random distractors) | Perturbation/length artifact | 2 |
| A10 | retrieval only (top_k 20, cap 3) | 2×2 factorial cell | 2 |
| A11 | cap only (top_k 10, cap 8) | Missing factorial cell | 2 |
| A12 | Pairs: WT+SC, WT+CX, CX+SC | Interaction structure (gated on singles) | 2 (gated) |
| A13 | Fresh-label routing (re-diagnose on fresh baseline) | Sensitivity to 18%/3% stale labels | 3 |
| A14 | Write-through threshold 0.45/0.65 + offline histogram | Robustness of 0.55 | 3 |
| A15 | Self-check on 50 fresh-correct questions | Verification harm rate | 5 (subsumed by A7) |

## Non-ablation fixes the reviewer calls non-negotiable

- Human audit of every discordant pair in primary contrasts (~120–180 grades).
- Frontier-model re-judge of discordants; recompute McNemar after the audit.
- Pre-register the primary family (`agnostic` vs baseline per benchmark);
  Holm-correct the rest and label them exploratory. Under Holm, p=0.0574,
  0.0225, 0.0156 do not survive.
- Report intention-to-treat: +50 pts on 34 questions ≈ +8.5 pts on 200;
  +29.5 on 44 ≈ +6.5 on 200.
- Disclose that `path` routing reads gold; scope deployment claims accordingly.
- Free checks: stale-label harm decomposition, flip provenance
  (judge vs deterministic floor), answer-length/style confound, EVAL rows as a
  negative control, per-arm unscored-question reasons.

## Feasibility review (Claude)

- API cost is small (≈5k–7k answer/judge calls, tens of dollars). Wall-clock is
  the binding constraint on this host: ≈7–20 s/question plus ingestion, and
  the box has repeatedly killed runs under memory pressure. Runs must stay
  resumable and be launched when ≥3 GB is free.
- A1/A2/A3/A4/A5/A10/A11 need new arms in `experiments/run_interventions.py`
  (mostly config-only routing changes). A7 needs a shared-store mode. A6 needs
  oracle stage labels from the baseline comparison rows. A8/A9 need sham
  context builders. A12 is gated. A14's offline histogram is free.
- Phase 0 (no API) should run before any new arm: it can reverse flips in a
  borderline contrast and would change the verdict.
- Recommended gate: A1 first on LoCoMo. If the placebo's discordant count is
  the same order as the arm effects, stop and fix measurement before spending
  on A2–A6.

## Run order

Phase 0 (free analyses) → A1 both benchmarks → A2/A3/A4 → A5/A6 → A7 →
conditional A8/A9/A10/A11/A13/A14.
