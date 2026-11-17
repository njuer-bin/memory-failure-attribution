# Status Drift Pilot — Paper Backbone (2026-11-16; V3 update 2026-11-17)

Working synthesis of committed results. Not a paper draft; a narrative skeleton
with the evidence attached. Sections 1–8 summarize the v2.x exploratory pilots.
The **V3 confirmatory update** at the end supersedes the headline claim.

## Working title (V3)

**Path-Dependent Status Loss in Chained Conversational Memory Compression:
Status Is Omitted Before the Proposition Is Lost**

## Abstract (V3 working)

Long-term LLM agents repeatedly compress conversational memory. We ask whether
this changes the epistemic, intentional, or conditional **status** attached to a
proposition, even when the proposition survives. In a frozen paired study
(30 new trajectories, 10 transformation conditions plus raw, 330 blind human
labels), chained rewriting causes **status omission** in 44–54% of
proposition-preserved memories, while unsupported status distortion is rare
(3/330, 0.9%). One-shot compression and repeated independent compression omit
status in only 3.7%, and chained rewriting with source access omits it in 0%.
A rewrite-matched control (constant intermediate budgets) equals recursive
rewriting, isolating chaining from budget shrinkage; repeated-direct matches
call count without chaining and behaves like direct. Proposition loss is
10–20% in chained conditions and does not explain the omission contrast. The
supported claim is therefore **path-dependent status representation loss**, not
a strong unsupported-distortion effect.

## Contributions (V3)

1. **A blind, calibrated diagnostic** separating proposition identity, status
   omission, and unsupported status distortion; primary-judgment κ 0.944 on 330
   confirmatory items.
2. **A mechanism**: chained rewriting, not intermediate budget shrinkage or raw
   call count, drives status omission (rewrite-matched = recursive;
   repeated-direct = direct).
3. **A protective factor**: source access during rewriting eliminates omission
   (0/30) and proposition loss (0/30).
4. **A reframing**: the dominant path effect is status omission, not
   unsupported distortion. The v2 intentional-specific cue-loss pattern does
   **not** replicate in V3 blind human labels; omission is dimension-general.
5. **Frozen artifacts**: protocol, ontology, annotation guide, SAP, runner, and
   raw outputs are versioned and hashed before generation.

## v2 exploratory evidence (retained; not pooled with V3)

The following v2.x results motivated V3 and remain exploratory. They used
deterministic cue metrics and model judges; they are not confirmatory.

## Method

- Synthetic Chinese multi-turn trajectories, 3 dimensions (epistemic,
  intentional, conditional), 10 topics, crossed stable/updated design.
- Conditions: raw, direct compression, recursive chain, rewrite-matched chain.
- Writers: neutral, status-aware, commitment-aware.
- Measures: deterministic proposition retention, deterministic status-cue state
  (MATCH / MIXED / OPPOSITE / ABSENT), judge labels (qwen2.5:7b, gemma3:12b,
  mistral:7b), manual adjudication.

## Headline numbers

### 30-trajectory run (design v3, five topics)

| Metric | neutral | status-aware |
|---|---:|---:|
| Inter-judge agreement | 0.904 | 0.952 |
| Both-judge-correct | 221/270 | 256/270 |
| Both-judge-wrong | 23 | 1 |
| Three-judge all-wrong | 23 | 1 |
| Proposition omission | 3/270 | 0/270 |

### Rewrite-matched control (neutral, 30 trajectories)

Both-correct by depth D1/D2/D3/D5:

- direct: 29 / 28 / 28 / 27
- recursive: 29 / 20 / 17 / 16
- rewrite-matched: 29 / 19 / 17 / 15

Recursive ≈ rewrite-matched; both far below direct. Chaining is the mechanism.

### 10-topic expansion (60 trajectories, cue-only)

Updated cases, ABSENT by depth:

| Condition | neutral | status-aware |
|---|---|---|
| direct D1–D5 | 0 / 3 / 1 / 3 (of 20) | 0 / 0 / 0 / 0 |
| recursive D1–D5 | 0 / 9 / 11 / 11 (of 20) | 0 / 2 / 5 / 7 |

Dimension split at intentional vs epistemic recursive D5:

- neutral: 9/10 vs 2/10
- status-aware: 5/10 vs 2/10

### Commitment-aware ceiling (20 intentional trajectories)

Strong/weak/none commitment cues at D5:

- neutral: 1 / 1 / 8
- status-aware: 5 / 5 / 0
- commitment-aware: **10 / 0 / 0**

Judge confirmation: qwen and gemma agree **180/180**; all **40/40** updated
D3/D5 items are judged COMMITTED, and stable CONSIDERING cases remain correct.

### Human annotation (v2.4)

**Status-aware** (single manual annotator A; the B file is gold-derived and is
not used):

- overall 5/119 = 4.2%; Raw 0/30; Direct D5 0/30; Recursive D5 2/29 = 6.9%;
  Rewrite-matched D5 3/30 = 10.0%; intentional 3/40 = 7.5%; epistemic 5.0%;
  conditional 0%.

**Neutral** (two independent manual annotators):

- overall 6.7–7.9% (A 9/114, B 7/105); Raw 0/30; Direct D5 0/30;
  Recursive D5 13.6–15.4%; Rewrite-matched D5 16.7–17.9%;
  intentional 21.9–25.7%; epistemic and conditional 0%;
- primary-label agreement raw 0.942, Cohen's kappa 0.849.

The neutral writer roughly doubles the human-annotated drift.

## Figures (planned)

1. Condition diagram: raw → direct / recursive / rewrite-matched.
2. Accuracy by depth for the three conditions, both writers.
3. Status-cue ABSENT by dimension and depth.
4. Judge-confusion / agreement heatmap.
5. Mitigation curve: neutral → status-aware → commitment-aware.

## Limitations

- Synthetic templates; one writer model; local judges.
- Human annotation exists for both writers, but the status-aware estimate uses
  one manual annotator; the neutral estimate has two-annotator reliability.
- Token budgets are not matched in the main runs; chained outputs are ~25%
  shorter. A token-band matched control (v2.9, band 14–18) is in progress.
- Neutral writer is not reliably deterministic at temperature 0; report ranges.
- Conditional remains the least reliable dimension (ontology/judge issues).
- Rewrite-matched controls call count but not intermediate content; call count
  and chaining are still entangled.
- The commitment-aware prompt is a ceiling intervention, not a deployment
  recommendation.
- The one-call structured sidecar is blocked with a 7B writer: it either drops
  the prose or copies the option strings. A reliable version needs a separate
  status extractor or a stronger model.

## Related work / novelty

- BELIEFMEM (2605.05583): probabilistic belief memory, LoCoMo/ALFWorld; not a
  measurement of status under chained compression.
- MemCoRe (2602.07885): compression-hierarchy evidence retrieval; not status
  preservation.
- PoS, MemTX, Memory as Belief, Agent-BRACE, TWIST: adjacent belief/state work;
  full-text comparison pending.
- Novelty claim: controlled status-cue diagnostic with a rewrite-matched
  mechanism control and a mitigation curve, not a new memory architecture.

## Open questions

1. Does the intentional-specific loss replicate on natural dialogue?
2. Can a **separate status extractor** (rather than a one-call prose+sidecar
   writer) achieve the commitment-aware result without templated prose? The
   one-call version is blocked at 7B.
3. Can a post-hoc checker repair weakened cues without the source?
4. Does the loss change downstream decisions (Stage B)?
5. What is the human-adjudicated error rate, and does it survive a genuine
   second annotator for the status-aware condition? (Neutral has two-annotator
   reliability; status-aware currently uses one manual annotator.)

## V3 confirmatory update (2026-11-17)

**Design.** 30 new trajectories (5 topics × 3 dimensions × stable/updated),
10 generated conditions plus raw, writer `qwen2.5:7b`, final budget 100,
seeds 42/43. Protocol and artifacts frozen in `V3_P2_FREEZE.md`;
labels in `results/status_drift_v3_p2/annotation/`; analysis in
`results/status_drift_v3_p2/analysis/`.

**Reliability.** 330 items, two annotators: primary-judgment raw 0.967 /
κ 0.944; identity 0.991 / 0.943; action_status 0.961 / 0.924;
expressed_status 0.991 / 0.989; evidence 0.988 / 0.972; dimension 1.000.
Adjudication is model-assisted (23 overrides); original labels are preserved.

**Outcome distribution (adjudicated).** NO_DISTORTION 182, STATUS_OMISSION 88,
PROPOSITION_LOSS 30, LEGITIMATE_UPDATE 27, UNSUPPORTED_STATUS_DISTORTION 3.
Identity: PRESERVED 300, PARTIAL 29, LOST 1.

**By condition (USDR and omission over PRESERVED).**

| Condition | PLR | USDR | Omission | Faithful |
|---|---:|---:|---:|---:|
| raw | 0.000 | 0.000 | 0.000 | 1.000 |
| direct | 0.100 | 0.000 | 0.037 | 0.963 |
| recursive | 0.100 | 0.037 | 0.444 | 0.519 |
| rewrite_matched | 0.133 | 0.000 | 0.462 | 0.538 |
| repeated_direct | 0.100 | 0.000 | 0.037 | 0.963 |
| source_peek | 0.000 | 0.000 | 0.000 | 1.000 |
| para | 0.200 | 0.000 | 0.542 | 0.458 |
| temp1 | 0.133 | 0.077 | 0.423 | 0.500 |
| temp2 | 0.100 | 0.000 | 0.519 | 0.481 |
| path_s2 | 0.133 | 0.000 | 0.538 | 0.462 |
| retrieval | 0.000 | 0.000 | 0.333 | 0.667 |

**Paired contrasts vs recursive (omission).** Direct −0.367
[−0.567, −0.167]; repeated-direct −0.367; source-peek −0.400
[−0.567, −0.233]; rewrite-matched 0.000 [−0.167, 0.167]. Temperature,
prompt paraphrase, and schedule-only point estimates are within 8 points and
their intervals cross zero. USDR has only 3 events; condition contrasts are
uninformative.

**Dimension result.** Omission among preserved is similar across dimensions
(conditional 27.6%, epistemic 33.0%, intentional 27.3%). The v2 claim that
intentional commitment is specifically vulnerable is **not replicated** in V3
blind human labels; it may reflect the deterministic cue metric or the v2
template family.

**Reframed claim.** Chained rewriting is associated with path-dependent
**status representation loss**, dominated by omission. Unsupported distortion
is a rare subtype (0.9%). The mechanism is re-editing the writer's own output:
rewrite-matched equals recursive, repeated-direct equals direct, and source
access removes the effect. Budget shrinkage and raw call count are not
sufficient explanations.

**Limitations added by V3.** Synthetic templates; one writer; 30 trajectories
(no power claim); model-assisted adjudication; annotator provenance unrecorded;
unsupported distortion underpowered; raw/retrieval are references.

**Next.** P4 status-only downstream intervention (correct / omitted / distorted
status, identical proposition wording), then P5 mitigation comparison, then the
full-text novelty audit. Do not claim novelty before that audit.
