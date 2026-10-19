# Publication roadmap — CCF-B

Created 2026-10-19. Daily work still resumes from `docs/STATUS.md`; this doc is
the route to the submission only.

## Thesis

> When an LLM agent with long-term memory answers wrongly, the failure is
> decomposable into lifecycle stages (Formation→Storage→Retrieval→Context→
> Reasoning), and measuring where it starts first changes what should be fixed.

Current evidence: canonical LongMemEval n=50 (`oracle_experiments_n50_final`)
under the frozen protocol, plus the instrument-refinement rescore
(`_orderrefuted`) after the deterministic ordering refutation.

## Contribution slots (paper needs ≥2 of these to be CCF-B viable)

1. **Instrument** (done, draft-stage): unified failure-attribution protocol
   (F1–F6, E0, EVAL, RC) with a measured judge-reliability floor.
   Self-consistency kappa 1.0, cross-model raw-judge kappa ≈ 0.03 → the paper
   has a defensible statement about WHY deterministic floors are required.
2. **Cross-benchmark evidence** (P0) — LoCoMo n=50 first, then scale.
3. **Sample-scale** (P1) — n=200 per benchmark so McNemar/bootstrap can
   separate conditions. At n=50 everything was non-significant.
4. **Intervention** (P2) — at least one targeted fix showing that repairing
   the *measured* first-loss stage lowers the failure rate vs stage-agnostic
   baselines (ablated with `aris-ablation-planner`).

## Phase plan

### P0 — this week: generalization + novelty + venue deadline

- [ ] End-to-end LoCoMo n=50:
  `G:/aconda/python.exe -u -m experiments.run_oracle_experiments --dataset locomo_refined_public --limit 50 --out-dir results/oracle_experiments_locomo_n50`
- [ ] Read per-question failures; check the 8 former E0 cases did not silently
  change population (research-log discipline: rerun before claims).
- [ ] `aris-novelty-check` + `aris-prior-art-search` on the framing
  "lifecycle-stage failure attribution for LLM memory agents".
- [ ] Confirm submission deadlines for CIKM / COLING / ECIR / NLPCC this year
  (web search; do not plan from memory) and pick the target + backup.
- [ ] Commit the LoCoMo run + updated STATUS.md; push.

**Gate to enter P1:** LoCoMo produces a non-degenerate attribution
distribution (no single bucket > 80%) AND novelty search finds ≤ 1 direct
prior. If novelty fails, fork the narrative (see "Kill-switch narratives").

### P1 — weeks 2–3: statistical power

- [ ] LongMemEval n=200 (oracle benchmark, qwen2.5:7b, memory-safe batches;
  ~30–40 min per 50 records measured at n=50 latency).
- [ ] LoCoMo n=200.
- [ ] Paired McNemar + bootstrap per condition pair; report effect sizes, not
  only p-values.
- [ ] `aris-experiment-plan` for the run queue; `aris-analyze-results` after
  each batch.
- [ ] `aris-citation-audit` pass on the lit section draft.

**Gate to enter P2:** at least one pairwise contrast significant at α=0.05
with bootstrap CI excluding 0. If nothing separates even at n=200, the honest
paper is the instrument paper (contribution 1 + the reliability study), and
the venue choice changes (COLING resource track or NLPCC fits that better).

### P2 — weeks 3–5: intervention

- F6-dominated residual → repair candidates: deterministic temporal floor
  (already built for ordering questions), answer-time self-check prompt,
  or retrieval-time expansion of the formation-failure items.
- F1 dominant under real memory → repair candidates: ingestion-time
  summaries, provenance-carrying memory write, or query-time re-write.
- [ ] Controlled ablation: with-repair vs without-repair on the same
  question set, same judge/floor instrumentation.
- [ ] `aris-ablation-planner` + `aris-experiment-audit` before any number is
  quoted in the draft.

**Gate to enter P3:** intervention shows ≥ 5-point accuracy gain on the
repaired stage's failure set with CI excluding 0.

### P3 — weeks 5–6: manuscript

- [ ] Outline + claim extraction: `aris-paper-plan`, `aris-claims-drafting`,
  `aris-result-to-claim`.
- [ ] Full draft: `aris-paper-write` / `research-paper-writing`.
- [ ] Figures: `aris-paper-figure` + `academic-plotting` + `dataviz`.
- [ ] Internal review: `rigor-reviewer`, then 2–3 loops of
  `aris-auto-review-loop`; kill remaining contradictions with `aris-kill-argument`.
- [ ] `/security-review`-style integrity pass: `aris-integrity-forensics` +
  `aris-paper-claim-audit` (every number tied to a rerun artifact path).

### P4 — week 7: submission

- [ ] `aris-paper-compile` for camera-ready format; LaTeX repo synced with
  `aris-overleaf-sync`.
- [ ] Submit target; if rejected or risky deadline, `aris-resubmit-pipeline`
  to the backup venue.

## Kill-switch narratives (pre-registered)

- **Intervention fails but instrument holds:** resource/analysis paper about
  the attribution protocol + judge-reliability methodology. Venue: COLING /
  NLPCC (more accepting of resource-and-analysis).
- **No pairwise separation at n=200:** report under a positive framing —
  "memory agent failures are statistically dominated by formation, and
  post-formation repairs cannot recover them" — if and only if the n=200
  evidence shows exactly that.
- **Heavy prior-art collision:** pivot to the UNRESOLVED part of the
  lifecycle (only the stages the prior work left unwired), re-run novelty
  before any drafting.

## Non-negotiable rules (carried from the lab diary)

1. Every number that enters the paper must be traceable to a rerun artifact
   path committed next to it; unit tests never constitute a conclusion.
2. Contaminated runs are negative results; they are archived with a
   corrigendum, never silently replaced.
3. Judge-based numbers are paper-usable only with the deterministic floor in
   place and the kappa value reported alongside.
