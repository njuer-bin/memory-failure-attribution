> **QUARANTINED — unauthorized model.** Generated with `kimi-k3` before the
> user restricted the project to `DeepSeek-v4.1-flash`. Exploratory only; do
> not cite or fold into any paper claim without explicit approval.

## 0. Blunt framing

Three questions decide whether this paper survives review, and none are answered yet:

1. **Is the agnostic gain just self-check?** If yes, your lifecycle instrument is a diagnostic ornament on a generic verification bump, and C1–C3 collapse.
2. **Does targeting beat a coin flip over repairs?** C2 is already dead — and path's "context contains all gold items" test reads gold, so it was oracle-advantaged and *still* failed (p=1.0). Say this loudly; don't spend compute resurrecting it.
3. **Are the flips real?** Every contrast rests on 7–19 discordant pairs (I verified: LME agnostic = 17/0, LCM agnostic = 16/3, first-vs-agnostic = 11/3, path-vs-agnostic = 11/2). With cross-model judge κ≈0.03, two misjudged flips reverse every borderline claim. That is a measurement problem — no ablation fixes it.

## 1. Prioritised ablations

| ID | Ablation | What it tests | Expected signature if component matters | Pri |
|---|---|---|---|---|
| A1 | **Placebo re-answer (B2)**: second identical fresh baseline | Nondeterminism/RTM floor under temp-0 provider noise | B2-vs-B1 net ≈ 0 with symmetric discordants (~10% of subset); all arm effects should clear B2's noise envelope. If placebo shows net gains on the stored-failure subset, subset selection is doing the work | 1 |
| A2 | **write-through-only** on all attributable failures | Does the gold-free formation repair carry the bundle? | LME: captures ≥ ~70% of agnostic net flips (31/34 labels are formation). Note: first_loss on LME already ≈ this arm, so marginal info is on non-formation questions | 1 |
| A3 | **self-check-only** on all attributable failures | Whether generic verification explains agnostic | If A3 ≈ agnostic on both benchmarks: rewrite C3 as "verification, not memory repair." Also expect the highest correct→wrong harm rate here | 1 |
| A4 | **wide-context-only (top_k 20, cap 8)** | Context-assembly component | On LCM (path composition: 30 retrieval / 21 context) should capture the plurality of flips; modest on LME | 1 |
| A5 | **Mismatched routing**: rotate labels (F1→F4→F5→F6→F1), same repair budget | Causal value of stage targeting — the paper's thesis | If targeting matters: matched fix-rate ≫ mismatched, diagonal dominance in the label×repair fix matrix. If mismatched ≈ matched: labels are a "something is wrong" flag, nothing more. Weak on LME (label distribution degenerate); decisive on LCM | 1 |
| A6 | **Oracle routing**: route by gold first-loss stage from the oracle ladder | Separates "labels are noisy" from "routing is worthless" | Oracle ≈ first_loss → labels are accurate, routing itself is null → C3 strengthened. Oracle ≫ first_loss → instrument's labels are the bottleneck → diagnostic-value claim weakened | 1 |
| A7 | **Broadcast**: agnostic on all 200, shared mutated store | Four readouts in one run: ITT effect; harm on fresh-correct; E0 negative control (~0 net expected; gains ⇒ E0 mislabels or second-chance effects); cross-question store pollution from write-through | If broadcast-ITT ≈ targeted-ITT with ≤1–2% harm: routing is pointless end-to-end. If harm is large: routing *protects* correct answers — complicates C3 | 2 |
| A8 | **Sham self-check**: verification call with shuffled/no evidence, matched compute | Evidence-grounding of the verification gain | Sham ≈ placebo and real > sham → grounding matters. Sham ≈ real → self-check is a second-chance effect; reframe | 2 |
| A9 | **Sham context**: widen with random distractor chunks, same token budget | Whether perturbation/length per se helps (judge style bias probe) | Sham ≤ placebo noise. If sham helps: escalate to judge audit immediately | 2 |
| A10 | **retrieval-only (20, cap 3)** | Completes 2×2 with B1 (10,3), A4 (20,8), A11 | If rank cutoff binds: (20,3) > (10,3) | 2 |
| A11 | **cap-only (10, cap 8)** | The missing cell — is the type cap the binding constraint? | If cap binds: (10,8) ≈ (20,8) and top_k is irrelevant | 2 |
| A12 | **Pairs**: WT+SC, WT+CX, CX+SC | Interaction structure | Run **only if** Σsingles ≠ agnostic. Complementarity story (WT creates, CX surfaces, SC uses) predicts pairs > singles, agnostic ≥ pairs | 2 (gated) |
| A13 | **Fresh-label routing**: re-diagnose on B1's failures, route on fresh labels | Sensitivity to the 18%/3% label staleness | If stale labels drive the LCM losses: fresh-label routing keeps gains, losses → ~0 | 3 |
| A14 | **Threshold sweep**: write-through-only at 0.45/0.65 (LME only) + free offline similarity histogram at 5 thresholds | Robustness of 0.55; bloat/coverage trade | Flat → report robustness. Monotone → 0.55 was tuned-lucky; disclose provenance | 3 |
| A15 | SC on 50 fresh-correct questions | Verification harm rate | Skip if A7 runs (subsumed by its harm readout) | 5 |

## 2. Coverage assessment

**Objections answered by these ablations:**
- "The bundle is confounded" → A2–A4, A12
- "Targeting is unfalsified / any perturbation helps" → A5, A6, A7, and the A2-vs-first_loss contrast (repair-all vs repair-targeted for the dominant label)
- "Regression to the mean / temp-0 noise floor" → A1 (+ stored-vs-fresh stats in hand)
- "Self-check is just more test-time compute" → A3, A8 (compute-matched sham)
- "Hyperparameters tuned to the benchmark" → A10, A11, A14
- "No negative controls" → A7's E0 readout, A9
- "Deployment externalities" → A7's pollution readout

**Objections these ablations do NOT answer (statistics/measurement, not experiments):**
- **Judge validity.** Same model answers, verifies, and judges — triple self-dealing. κ≈0.03 cross-model with 0.71 raw agreement = chance-level beyond prevalence, and gemma3:12b is too weak to be the validating judge anyway. Fix: human audit of *every* discordant pair in primary contrasts (~120–180 grades, 1–2 person-days) + frontier-model re-judge; recompute McNemar post-audit. Non-negotiable.
- **Multiplicity.** ≥10 McNemars; p = 0.0574, 0.0225, 0.0156 do not survive Holm. Pre-register the primary family (agnostic vs B1, per benchmark); label the rest exploratory.
- **ITT reporting.** +50pts on 34 questions ≈ +8.5pts on 200; +29.5 on 44 ≈ +6.5 on 200. Free recompute; reviewers will do it for you otherwise.
- **Gold-dependence disclosure.** State exactly which routing decisions read gold (path's containment test; whether "attributable" is gold-derived). If attribution needs gold, scope C1/C3 to diagnostic settings.
- **Stale-label harm decomposition** (free): do the 3–4 LCM losses per arm land on the 9 stored-failure/fresh-correct questions? If yes, that's instrument staleness, not repair harm — different implication.
- **Flip provenance** (free): how many flips are floor-decided vs judge-decided? Watch the temporal-floor × provenance-timestamp interaction — write-through may be flipping floor decisions, not reasoning.
- **Judge style bias** (free): answer-length delta by arm vs flip direction.
- **Single answerer/provider/benchmark pair**: not ablatable; scope claims or fund a second-answerer study.
- Report why questions are unscored per arm (common-subset conditioning).

## 3. Unnecessary ablations

| Looks useful | Why it isn't |
|---|---|
| Full 7-cell factorial unconditionally | Gate on additivity; singles + agnostic may close the question |
| Fine top_k grid (12/16/24/32) | The 2×2 answers mechanism; finer grids are benchmark tuning |
| ≥3 fresh baselines / "seeds" at temp 0 | No seed lever exists; B2 suffices unless B1–B2 discordance ≈ arm effects |
| F2/F3 stage ablations | Zero routed targets in both compositions; no repair pathway; nothing to test |
| Random-label arm alongside A5 | Subsumed by rotation |
| Paraphrased vs verbatim write-through | Design exploration; no claim bears on it |
| Judge temperature/prompt sweeps | Self-consistency is already κ=1.0; the judge problem is bias, not variance |
| Re-ablating oracle-ladder rungs | Instrument validation, belongs to P1, not the intervention claims |
| 5-point online threshold sweep, both benchmarks | Offline histogram + 2 online points on LME suffice |

## 4. Suggested order (info per dollar)

- **Phase 0 (0 API, start day 1):** freeze one shared B1; human-audit existing discordants; ITT recompute; stale-label harm; flip provenance; length confound; gold-dependence disclosure. If audit reverses ≥2 flips in a borderline contrast, recompute before any new arm.
- **Phase 1 (~800 calls):** A1 placebo, both benchmarks. Gate: if placebo noise ≈ arm effects, stop and fix measurement.
- **Phase 2 (~770):** A2, A3, A4. Gate: one single ≈ agnostic → rewrite C3, skip A12; Σsingles ≈ agnostic → skip A12.
- **Phase 3 (~460):** A5, A6 — thesis-deciding.
- **Phase 4 (~1,200):** A7 broadcast (four readouts, one run).
- **Phase 5 (conditional, ~1,000):** A8/A9 (only if SC/CX carry weight), A10/A11, A14, A13.
- Frontier-judge re-score of discordants (~300 calls) slots into Phase 1.

Pre-register the decomposition hypotheses (e.g., "A3 captures <50% of agnostic net flips") before Phase 2 — you registered C2 and it failed; keep that discipline or the ablation program becomes HARKing fodder.

## 5. Estimated compute

Assumptions: T_LME = 60, T_LCM = 50 targeted attributable questions; E0 = 41/86; per targeted question A=1 answer, J=1 judge, V=1 verify; write-through and retrieval are embedding/store ops ≈ 0 LLM calls; A13 adds ~T judge calls for re-diagnosis.

| Ablation | LME | LCM |
|---|---|---|
| A1 placebo | 400 | 400 |
| A2 WT-only | 120 | 100 |
| A3 SC-only | 180 | 150 |
| A4 CX-only | 120 | 100 |
| A5 mismatched | 125 | 105 |
| A6 oracle | 125 | 105 |
| A7 broadcast (all 200) | 600 | 600 |
| A8 sham SC | 180 | 150 |
| A9 sham CX | 120 | 100 |
| A10/A11 factorial cells | 240 | 200 |
| A12 pairs ×3 (gated) | 450 | 375 |
| A13 fresh-label | 185 | 155 |
| A14 threshold (LME only) | 240 | 0 |

**P1 package (A1–A6): ≈2,030 calls.** Full program: ≈4,800–5,600 (+825 if A12 fires) + 300–1,600 judge re-scores → **≈5k–7k calls total**. At ~15k tokens/call ≈ 75–100M tokens → tens of dollars on flash-class pricing. The binding cost is the human audit (1–2 person-days), not API.

## 6. Threats to inference

| Threat | Consequence | Fix type | Fix |
|---|---|---|---|
| Selection on stored failures + regeneration (18%/3% stale labels) | Subset effects inflated; arms "lose" on already-fixed questions | Both | A1, A13 (ablation); stale-label harm breakdown (statistic, free) |
| Self-judge, cross-model κ≈0.03 | 2 misjudged flips reverse every borderline contrast | Measurement | Human audit of all discordants + frontier re-judge; post-audit McNemar. **No ablation substitutes** |
| Multiplicity (≥10 tests) | 0.0574/0.0225/0.0156 die under Holm | Statistic | Pre-registered primary family; Holm within families |
| Per-arm fresh baselines / run-order drift | Arm-vs-baseline confounded by time | Design | One frozen B1 for all arms; log timestamps; A1 bounds drift |
| Gold-dependent routing (path's containment test) | C2 was oracle-advantaged and failed — strengthens the negative; deployment claims need a gold-free labeler | Report | Disclose; A6 quantifies label quality; scope C1/C3 |
| Subset-vs-ITT | Headline +50pts is +8.5pts ITT | Statistic | Report both; free |
| Store pollution from write-through | Per-question regeneration hides cross-question harm | Ablation | A7 (shared-store readout) |
| Self-check compute confound | Agnostic gets two answer attempts | Ablation | A3, A8 (compute-matched sham) |
| Judge style/length bias toward verified answers | Flips may be judge artifacts | Statistic | Length-stratified flip analysis; blind re-judge with shuffled arm identity |
| Floor × repair interaction (temporal floor vs provenance timestamps) | Write-through may flip floor decisions, not reasoning | Statistic | Flip-provenance breakdown; free |
| EVAL-labeled questions in the 200s | Built-in negative control already in your data | Statistic | Read out repair effects on EVAL-labeled questions; free |
| One answerer, one provider, two benchmarks | External validity | Scope | Soften claims or fund a second-answerer study — not an ablation |