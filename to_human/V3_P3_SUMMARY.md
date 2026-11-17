# V3 P2/P3 Result — One-Page Summary (2026-11-17)

## What was run

- **P2:** 30 new trajectories (5 topics × 3 dimensions × stable/updated),
  10 generated conditions + raw, writer `qwen2.5:7b`, final budget 100.
  Completeness: 30/30 trajectories, 300/300 conditions, 0 errors.
- **P3:** 330 blind items (30 × 11 conditions), two annotators, frozen v3.2.3
  guide. Reliability: primary-judgment κ **0.944**, identity κ 0.943,
  action_status κ 0.924, condition status κ 0.989.
- Adjudication: model-assisted (23 overrides); original labels preserved.

## Headline result

**Chained rewriting causes status omission, not unsupported distortion.**

| Condition | Proposition loss | Unsupported | Status omission | Faithful |
|---|---:|---:|---:|---:|
| raw | 0.0% | 0.0% | 0.0% | 100% |
| direct | 10.0% | 0.0% | 3.7% | 96.3% |
| recursive | 10.0% | 3.7% | **44.4%** | 51.9% |
| rewrite-matched | 13.3% | 0.0% | **46.2%** | 53.8% |
| repeated-direct | 10.0% | 0.0% | 3.7% | 96.3% |
| source-peek | 0.0% | 0.0% | **0.0%** | 100% |
| paraphrase | 20.0% | 0.0% | 54.2% | 45.8% |
| temp1 | 13.3% | 7.7% | 42.3% | 50.0% |
| temp2 | 10.0% | 0.0% | 51.9% | 48.1% |
| path-S2 | 13.3% | 0.0% | 53.8% | 46.2% |
| retrieval | 0.0% | 0.0% | 33.3% | 66.7% |

Omission/unsupported/faithful are among proposition-preserved items.

## Mechanism

- **Chaining, not budget shrinkage:** rewrite-matched (constant intermediate
  budgets) equals recursive (paired omission difference 0.000).
- **Not raw call count:** repeated-direct matches call count but behaves like
  direct (−0.367, CI [−0.567, −0.167]).
- **Source access protects:** source-peek omits 0/30 and loses 0/30
  propositions (−0.400, CI [−0.567, −0.233]).
- **Decoding / paraphrase / schedule** do not materially change omission.

## Two corrections to the earlier story

1. **Unsupported distortion is rare:** 3/330 (0.9%), not the main outcome.
   The claim is **path-dependent status representation loss (omission)**.
2. **The v2 intentional-specific pattern does not replicate:** omission is
   27.6% conditional, 33.0% epistemic, 27.3% intentional. Scope the old claim
   to v2 deterministic/judge evidence.

## Caveats

- Synthetic Chinese templates; one writer model; 5 topics; 30 trajectories
  (no power claim).
- Adjudication is model-assisted, not human; annotator provenance is
  unrecorded (maintainer decision). Report as annotator-unspecified.
- Raw and retrieval are references, not production strategies.
- P2/P3 are not pooled with v2.x or P1.

## Next

1. Review/sign off `V3_P4_PROTOCOL_DRAFT.md` (paired present/omitted/distorted
   status variants; sandboxed downstream decisions; unauthorized-action
   primary outcome). Then freeze and run P4.
2. P5 mitigation comparison (neutral, status-aware, evidence-anchored,
   transition verification).
3. Full-text novelty audit before any novelty claim.

## P4 update (2026-11-17)

P4 is frozen and run: 30 trajectories × present/omitted/distorted + no_memory,
120/120 items, 0 parse failures.

| Variant | Unauthorized | Evidence-consistent | Clarify |
|---|---:|---:|---:|
| present | 6.7% | 93.3% | 60.0% |
| omitted | 0.0% | 66.7% | 100% |
| distorted | 66.7% | 0.0% | 33.3% |
| no_memory | 0.0% | 66.7% | 43.3% |

Omission is behaviorally conservative (asks, never acts without authorization)
but causes under-action on established/committed statuses. Distortion is
behaviorally dangerous (66.7% unauthorized, paired +60 points). The dominant
memory failure is the safe one; the rare failure is the harmful one.

**Next:** P5 mitigation scored on both omission and distortion; replication;
full-text novelty audit.

## P5 update (2026-11-17)

12 trajectories × 6 writer strategies, 72 blind human labels (primary κ 0.881).
Faithful (NO_DISTORTION + LEGITIMATE_UPDATE):

| Strategy | Faithful | Omission | Unsupported | Proposition loss |
|---|---:|---:|---:|---:|
| neutral | 6/12 | 5/12 | 1/12 | 0/12 |
| status_aware | 10/12 | 1/12 | 1/12 | 0/12 |
| source_peek | 11/12 | 1/12 | 0/12 | 0/12 |
| evidence_anchored | 11/12 | 1/12 | 0/12 | 0/12 |
| transition_verification | 10/12 | 2/12 | 0/12 | 0/12 |
| unknown_heavy | 6/7 preserved | 1/7 | 0/7 | **5/12** |

`status_aware` is the best low-cost candidate (+33 points faithful at 1.03×
length) but still has one real conditional collapse. `source_peek` is stronger
if the source can be exposed at rewrite time. `evidence_anchored` costs 1.84×
and its anchors are often wrong. `unknown_heavy` is disqualified by 42%
proposition loss.

**Next:** confirmatory P5 with more trajectories; replication; full-text novelty
audit.

## P5 confirmatory update (2026-11-17)

2×2 prompt (neutral/status-aware) × source access (memory-only/memory+source),
30 trajectories, 120 blind items. v3.2.4 recheck: primary κ **0.974**.
Human faithful (NO_DISTORTION + LEGITIMATE_UPDATE):

| Condition | Faithful | Omission | Unsupported | Budget |
|---|---:|---:|---:|---:|
| neutral | 14/26 = 0.54 | 11/26 = 0.42 | 1/26 | 1.00× |
| status_aware | 27/30 = 0.90 | 0/30 | 2/30 | 1.05× |
| neutral_source | **30/30 = 1.00** | 0/30 | 0/30 | 1.23× |
| status_aware_source | 28/30 = 0.93 | 0/30 | 1/30 | 1.38× |

Paired vs neutral faithful: status_aware +0.433 [0.267, 0.600];
neutral_source +0.533 [0.367, 0.700]; interaction −0.500 [−0.667, −0.333].

**Source access is the strongest mitigation; the status-aware prompt is
partial; combining them is worse than source alone** because the prompt can
introduce `将+action` escalations. P5 is no longer provisional.

**Next:** replication; full-text novelty audit; paper integration.

## Second-model replication (gemma3:12b, 2026-11-17)

**Agent.** 30 trajectories × 4 variants, 120/120. Unauthorized action:
present 0/30, omitted 0/30, **distorted 20/30 (66.7%)**, no-memory 0/30. The
omission/distortion asymmetry replicates; it is not a qwen artifact.

**Writer.** First 12 pre-registered trajectories × 7 conditions. Human faithful
(κ 0.702, provisional): direct 11/12, recursive 10/12, rewrite-matched 7/12,
repeated-direct 11/12, neutral-source 10/12, status-aware 11/12, combined
12/12. Rewrite-matched remains worst, but recursive is far less destructive
than in qwen; source access alone is weaker; status-aware and the combination
are stronger. The mitigation ranking is model-dependent. The writer run
over-collected 30 trajectories; the first 12 are the primary cohort.

**Next:** optional v3.2.5 writer recheck; then paper/novelty audit.


## Where things are

- Protocol/freeze: `docs/research/V3_P2_PROTOCOL.md`, `V3_P2_FREEZE.md`
- P3 result: `docs/research/2026-11-17-v3-p3-outcomes.md`
- Raw outputs: `results/status_drift_v3_p2/`
- Labels/key: `results/status_drift_v3_p2/annotation/`; key outside the repo
- Analysis: `results/status_drift_v3_p2/analysis/`
- Paper backbone: `docs/research/2026-11-16-status-drift-paper-backbone.md`
