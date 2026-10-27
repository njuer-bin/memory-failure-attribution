# Pre-registration changelog

Append-only. Any change to a frozen item in `docs/PROTOCOL_FREEZE.md`, any change
to an analysis plan after seeing its outcome, or any re-scoping of a claim must
be recorded here **before** the affected run or analysis. Each entry states what
changed, why, and which analyses it invalidates or re-labels.

## Template

```
## YYYY-MM-DD — <short title>
- Item: <frozen item or plan>
- Old: <what was pre-registered>
- New: <what it becomes>
- Reason: <why, stated before seeing the outcome where applicable>
- Affected analyses: <artifact paths, label versions>
- Decision impact: <none / re-label / invalidate / re-scope>
```

## Entries

## 2026-10-26 — Adopt the CCF-B decision plan and freeze the protocol
- Item: governing plan and frozen configuration.
- Old: phase plan in `docs/PUBLICATION_ROADMAP.md`; no formal freeze.
- New: `docs/CCF_B_DECISION_PLAN_2026-10-26.md` is the governing plan;
  `docs/PROTOCOL_FREEZE.md` freezes commit `b8b1f6e`, model config, datasets,
  evaluation and annotation protocols, and headline artifacts.
- Reason: adversarial review (`docs/reviews/2026-10-26-direction-kill-argument.md`)
  found the current framing not CCF-B viable as-is; the plan replaces
  paper-polishing with falsifiable decision gates.
- Affected analyses: all headline numbers must now state their label version
  (auto / abstention-corrected / human-gated); E0 levels are not quoted.
- Decision impact: none on stored results; re-scope of claims pending gates A–D.

## 2026-10-26 — Stage B conditions frozen: A1 and A3 first, A2 deferred
- Item: Stage B architecture-ablation conditions.
- Old: design listed A1/A2/A3 plus A2a/A2b wide-context variants.
- New: freeze **A1** (`semantic_rawwrite`, removes the formation bottleneck)
  and **A3** (`verbatim_hybrid`, removes the retrieval bottleneck) at n=100,
  `context_chars=6000`, `candidate_k=20`, `top_k=10`. **A2a/A2b** (summary vs
  raw sessions at a wide context budget) are deferred until A1/A3 report,
  because summary baseline ingest costs ~1,900 LLM calls.
- Reason: A1/A3 need no LLM ingestion and test the two stages with the largest
  measured losses; run the cheap decisive pair first.
- Affected analyses: `results/systems_ablation_n100_a3/`,
  `results/systems_ablation_n100_a1/`.
- Decision impact: none on stored results; the gate-B rule is unchanged
  (≥2 systems move their dominant-stage share ≥20 points with Holm-significant
  within-system Stuart–Maxwell).

## 2026-10-27 — Gate B verdict and claim re-scope (route decision)
- Item: the Stage B decision gate and the paper's phenomenon claim.
- Old: gate B passes only if ≥2 of 3 systems move their dominant-stage share
  ≥20 points with Holm-significant within-system Stuart–Maxwell; on a pass the
  project would continue the CCF-B phenomenon paper.
- New: gate B is **partial** — A1 (semantic vs semantic_rawwrite, n=100) moves
  the stage significantly (SM χ²=19.75, df=6, p=0.00307; F1 share 0.13→0.00,
  F4 0.12→0.24; accuracy 0.500 vs 0.430, p=0.392) but the largest share move is
  13 points; A3 moves 14 points at p=0.066. Neither condition meets the 20-point
  bar, so 0 of 2 evaluated conditions pass. The claimed phenomenon is **re-scoped
  from a universal failure fingerprint to architecture-conditional stage
  localisation**, and the route switches to the analysis/resource paper.
- Reason: the pre-registered rule is applied as written; the bar is not lowered
  after seeing the result. Two protocol facts are recorded with the verdict:
  (i) with A2 deferred, only 2 of the 3 systems were evaluable, so the rule
  could not return a pass; (ii) the F1 share was 13% of rows, so eliminating
  formation failure can move that share by at most 13 points.
- Affected analyses: `results/analysis_ablation_a1_n100.json`,
  `results/analysis_ablation_a3_n100.json`, `results/decision_gate_b.json`,
  `results/route_decision_2026-10-27.json`. Claims C1–C3 are unchanged; C4 is
  new; the universal-fingerprint claim is retracted; the actionable-diagnosis
  claim was already null.
- Decision impact: re-scope (claims and paper route). No stored result is
  invalidated; no criterion is changed.
