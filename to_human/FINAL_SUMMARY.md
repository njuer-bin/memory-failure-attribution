# Status Drift — Final Summary (2026-11-17, V3)

> Supersedes the 2026-11-16 v2 summary, which is retained in git history.
> v2 exploratory results are not pooled with V3. Authoritative detail:
> `docs/research/2026-11-16-status-drift-paper-backbone.md` (V3 update).

## Question

When the same conversation passes through different memory transformation
histories, does the **status** attached to a proposition (epistemic /
intentional / conditional) survive — even when the proposition does — and do
status-only differences change downstream agent behavior?

## Answer

**Chained rewriting causes status omission, not unsupported distortion.** The
dominant path effect is that the writer drops the status while keeping the
proposition. Omission is behaviorally conservative; the rare distortion is
dangerous. Source access during rewriting removes the omission.

## Design

30 new trajectories (5 topics × 3 dimensions × stable/updated), 10 generated
transformation conditions + raw reference, `qwen2.5:7b` neutral writer, final
budget 100, seeds 42/43. Protocol, ontology, guide, SAP, and runner frozen and
hashed before generation (`V3_P2_FREEZE.md`). 330 blind human labels, two
independent annotators; model-assisted adjudication of 23 disagreements.

## Main result (330 adjudicated items)

Omission among proposition-preserved items:

| Condition | Proposition loss | Omission | Faithful |
|---|---:|---:|---:|
| raw | 0.000 | 0.000 | 1.000 |
| direct | 0.100 | 0.037 | 0.963 |
| recursive | 0.100 | 0.444 | 0.519 |
| rewrite_matched | 0.133 | 0.462 | 0.538 |
| repeated_direct | 0.100 | 0.037 | 0.963 |
| source_peek | 0.000 | 0.000 | 1.000 |
| para | 0.200 | 0.542 | 0.458 |
| temp1 | 0.133 | 0.423 | 0.500 |
| temp2 | 0.100 | 0.519 | 0.481 |
| path_s2 | 0.133 | 0.538 | 0.462 |
| retrieval | 0.000 | 0.333 | 0.667 |

Unsupported status distortion: 3/330 (0.9%); condition contrasts are
uninformative at that event count. Reliability: primary-judgment κ 0.944;
identity 0.943; action 0.924; expressed status 0.989; evidence 0.972.

Paired omission vs recursive: direct −0.367 [−0.567, −0.167]; repeated-direct
−0.367; source-peek −0.400 [−0.567, −0.233]; rewrite-matched 0.000
[−0.167, 0.167].

## Mechanism

Rewrite-matched equals recursive: holding intermediate budgets constant does
not help. Repeated-direct matches call count without chaining and behaves like
direct. So the cause is repeated re-editing of the writer's own output, not
budget shrinkage or raw call count. Source access eliminates it.

## Downstream behavior (P4)

Sandboxed agent sees present / omitted / distorted status with identical
proposition wording and chooses PROCEED / CONFIRM / ABSTAIN / OTHER.

| Variant | Unauthorized | Evidence-consistent |
|---|---:|---:|
| present | 6.7% | 93.3% |
| omitted | 0.0% | 66.7% |
| distorted | 66.7% | 0.0% |
| no_memory | 0.0% | 66.7% |

Paired vs present: omitted unauthorized −0.067 [−0.167, 0.000], evidence-
consistent −0.267 [−0.467, −0.067]; distorted unauthorized +0.600
[0.433, 0.767], evidence-consistent −0.933 [−1.000, −0.833]. The common
failure (omission) causes under-action; the rare failure (distortion) causes
unauthorized action. Keep the two outcomes separate — one "drift score" would
hide this.

## Mitigation (P5 confirmatory, v3.2.4 recheck κ 0.974)

30 trajectories × 2×2 prompt × source access, 120 items. Human faithful
(NO_DISTORTION + legitimate update): neutral 14/26 (0.54), status-aware
27/30 (0.90), neutral+source 30/30 (1.00), status-aware+source 28/30 (0.93).
Paired vs neutral: status-aware +0.433 [0.267, 0.600]; source +0.533
[0.367, 0.700]; interaction −0.500 [−0.667, −0.333]. Budget 1.05× / 1.23× /
1.38×, all below the 1.5× flag. Source access is the strongest mitigation; the
prompt is partial; the combination is non-additive and can introduce
`将 + action` escalations.

## Replication (gemma3:12b)

- **Agent (30 × 4 = 120):** distorted 20/30 unauthorized, present 0/30,
  omitted 0/30, no-memory 0/30. The omission/distortion asymmetry is not a
  qwen artifact.
- **Writer (12 pre-registered trajectories × 7 conditions, κ 0.834):**
  faithful direct 11/12, recursive 8/12, rewrite-matched 6/12,
  repeated-direct 11/12, neutral-source 10/12, status-aware 11/12,
  combined 12/12. The chain effect replicates in direction. The mitigation
  ranking is model-dependent: source access alone is weaker in gemma
  (0.83 vs qwen 1.00), while the prompt and combination are at or above qwen.

## Novelty (full-text audit of 14 papers)

Not novel: state tracking as a problem (StateMem), structured belief states
(ProgMem, BELIEFMEM), belief revision, recursive summarization and chained
rewriting harm (ABBEL, Supersede, ReSum), source access (LiveCtx), memory
state → action (STALE, MemTX, EAL-Bench), belief-change intervention (TWIST).

Defensible claim: the **status-specific, proposition-controlled
transformation-history diagnostic** — status tuple + paired rewriting
histories + proposition identity fixed + omission/distortion split + blind
human labels + status-only downstream intervention + second-model replication.
The ingredients are prior work; the combination and measurement target are the
contribution.

## Validity and caveats

- Synthetic Chinese templates; no natural-dialogue replication yet.
- 30 trajectories; no formal power claim; unsupported distortion underpowered.
- One primary writer and 12 replicated trajectories under the second writer.
- Annotator provenance unrecorded; adjudication is model-assisted.
- Behavioral tasks are sandboxed simulations.
- The v2 "intentional commitment cues are uniquely vulnerable" claim did not
  replicate in V3 blind human labels.

## Next

1. Write the paper from the backbone document using the audit's say/do-not-say
   list.
2. Optional: natural-dialogue replication, a third writer, and the full
   30-trajectory writer replication.
3. Optional: separate status-extractor prototype (the one-call 7B sidecar is
   blocked).
4. Before submission: check ABBEL/Supersede appendices for a
   proposition/status split.

## Where things are

- Narrative: `findings.md`; state: `research-state.yaml`
- Paper backbone: `docs/research/2026-11-16-status-drift-paper-backbone.md`
- Novelty audit: `docs/research/2026-11-17-novelty-audit.md`
- Protocols: `docs/research/V3_*_PROTOCOL.md`, `V3_*_FREEZE.md`
- Run notes: `docs/research/2026-11-17-*.md`
- Raw outputs: `results/status_drift_v3_*`, `results/status_drift_v2_pilot/`
- 46 experiment runs recorded in `research-state.yaml`
