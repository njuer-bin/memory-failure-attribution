# V3 Statistical Analysis Plan
**Status:** Draft; finalize before confirmatory generation and annotation.

## 1. Estimands
**Primary estimand A — joint outcome distribution.** For each condition and
budget, the unconditional distribution over the four joint categories:
(1) PRESERVED and status-faithful, (2) PRESERVED and unsupported-distorted,
(3) PARTIAL/LOST, (4) AMBIGUOUS/unassessable. This avoids conditioning on a
post-generation variable.

**Primary estimand B — within-condition path divergence.** Among PATH_REPLICATE
paths for the same trajectory and condition, the pairwise state disagreement and
dispersion defined in `V3_FORMAL_DEFINITIONS.md` §9, restricted to paths with
PRESERVED proposition identity.

**Secondary estimand — conditional USDR.** Unsupported status distortion among
PRESERVED outputs, paired Recursive − Direct. Report alongside the joint
outcomes and never interpret it alone.

## 2. Primary contrasts
- Within-condition path divergence: PATH_REPLICATE path pairs (primary).
- **PEEK vs memory-only:** source-access contrast (primary path perturbation).
- **Deterministic vs sampled decoding:** generation-variability contrast (primary path perturbation).
- **Prompt paraphrase vs original:** instruction-wording contrast (primary path perturbation).
- Schedule-only path variation: near-null control (P1b: 9.1%).
- Recursive versus Direct: path-history contrast (joint outcomes + secondary USDR).
- Rewrite-matched versus Direct: repeated-rewriting contrast.
- Repeated-direct versus Direct: call-count contrast.
- Source-peek versus Recursive: source-access contrast.
- Recursive versus Rewrite-matched: intermediate-budget schedule contrast.
Raw and Retrieval are reference strategies, not substitutes for the primary paired contrast.

## 3. Analysis unit and dependence
The trajectory is the independent sampling cluster. Multiple conditions, depths, annotators, and budget levels from the same trajectory are not independent observations. Use paired tests or cluster-aware bootstrap intervals resampling trajectories. If sample size and design support it, fit a mixed-effects logistic model with condition and budget as fixed effects and trajectory (and potentially topic/template family) as random effects. Report model specification and convergence diagnostics.

## 4. Outcomes
- USDR: unsupported status distortion / proposition-preserved outputs.
- PLR: proposition lost or partial / all generated outputs, with LOST and PARTIAL separately visible.
- Status omission: status not represented or not recoverable, without an asserted conflicting state.
- LUA: legitimate evidence-supported state transitions correctly represented.
- DDE: downstream decision error in simulated behavior tasks.
- Appropriate clarification / abstention and unauthorized-action rate.
Report raw numerators, denominators, effect sizes, and 95% confidence intervals. Avoid percentage-only reporting.

## 5. Annotation reliability
Report raw agreement and a chance-corrected statistic appropriate to the label structure and prevalence (e.g., Cohen's kappa for two annotators, with prevalence caveats; Krippendorff's alpha if missing labels or multiple annotators require it). Report per-dimension reliability and confusion matrices. Adjudicated labels are the primary analysis labels; pre-adjudication agreement remains a separate quality result.

## 6. Multiplicity
Declare one primary outcome and one primary contrast. Treat dimension-specific, depth-specific, and topic-specific analyses as secondary or exploratory unless separately powered and preregistered. Use a multiplicity adjustment for families of confirmatory secondary tests, or clearly label them exploratory.

## 7. Missing data and exclusions
Report generation failures and annotation missingness by condition. Do not silently drop failed outputs. Primary analysis follows assigned condition; sensitivity analyses may consider evaluable outputs only, with reasons and denominators explicit. No exclusions based on observed drift or token length.

## 8. Power and sample size
Do not choose a large round number by intuition. Use calibration data to estimate paired discordance rates and plausible effect sizes, then conduct simulation-based power analysis for the planned paired or mixed-effects design. Account for clustering by trajectory and expected annotation missingness. If the required sample exceeds available annotation resources, narrow the estimand or treat the study as exploratory rather than claiming adequate power.

## 9. Behavioral intervention analysis
Create paired status-only variants with proposition wording, evidence, length, and all other context held constant as closely as possible. Randomize variant order and run identical agent configurations. Primary behavior outcome must be task-specific and predeclared (e.g., correct action selection or appropriate confirmation request). Analyze paired discordance at scenario level; report action, clarification, abstention, and unsafe-action outcomes separately. All actions are simulated.

## 10. Robustness checks
- alternative treatment of PARTIAL identity cases;
- all-output joint outcome analysis;
- actual token count as covariate and budget-stratified estimates;
- second writer model replication;
- human adjudication versus model-judge diagnostics;
- sensitivity to ambiguous cases;
- leave-one-template-family-out analysis.
A post-hoc token-matched subset is descriptive only because selection on generated length can bias the comparison.
