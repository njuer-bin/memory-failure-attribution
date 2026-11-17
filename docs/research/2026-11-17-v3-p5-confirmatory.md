# V3 P5 Confirmatory Result (2026-11-17)

**Design:** 2×2 prompt (neutral / status-aware) × source access (memory-only /
memory + source), 30 P2 trajectories, 5-stage chain 220 → 180 → 140 → 120 → 100.
Frozen in `V3_P5_CONFIRMATORY_FREEZE.md`.
**Generation:** 120/120 conditions, 0 errors. Budget inflation: status_aware
1.05×, neutral_source 1.23×, status_aware_source 1.38×; all below the 1.5× flag.
**Human set:** 120 blind items, two annotators under v3.2.3; adjudication
model-assisted (29 overrides); original labels preserved.

## 1. Annotation reliability

| Field | Raw | Cohen's κ |
|---|---:|---:|
| proposition_identity | 0.958 | 0.528 |
| primary_dimension | 1.000 | 1.000 |
| status_expressed | 0.983 | 0.928 |
| expressed_status | 0.858 | 0.834 |
| action_status | 0.958 | 0.919 |
| evidence_support | 0.950 | 0.817 |
| **primary_judgment** | **0.900** | **0.689** |

Both files are schema-valid. Primary-judgment κ **0.689 is below the 0.80
calibration gate**; the identity κ is a prevalence artifact (112 vs 117
PRESERVED, raw 0.958). The disagreements are systematic rule boundaries, not
random noise:

- `驾照考试` for `考驾照`: nominalized action read as PARTIAL by one annotator;
- `将 + action` (`将开始健身`): read as COMMITTED vs CONSIDERING;
- contradictory cues (`确认未开网店`, `确认将开网店但不确定`): read as
  polarity/ambiguity vs established;
- `换工作中`, `不学游泳`: aspect/negative action states.

These are recorded in `annotation/adjudication.csv` and motivate v3.2.4. The
adjudicated labels are the primary analysis labels (SAP §5); the κ is a
quality caveat, not an exclusion.

## 2. Human outcomes

Faithful = `NO_DISTORTION` + `LEGITIMATE_UPDATE`; omission/unsupported/ambiguous
over PRESERVED; loss over all items.

| Condition | n | Faithful | Omission | Unsupported | Ambiguous | Loss |
|---|---:|---:|---:|---:|---:|---:|
| neutral | 30 | 14/27 = 0.52 | 12/27 = 0.44 | 1/27 = 0.04 | 0/27 | 3/30 = 0.10 |
| status_aware | 30 | 26/30 = 0.87 | 1/30 = 0.03 | 2/30 = 0.07 | 1/30 | 0/30 |
| neutral_source | 30 | **30/30 = 1.00** | 0/30 | 0/30 | 0/30 | 0/30 |
| status_aware_source | 30 | 28/30 = 0.93 | 0/30 | 1/30 | 1/30 | 0/30 |

## 3. Paired contrasts

Trajectory-level paired differences, cluster bootstrap 95% CI (10,000
resamples).

| Contrast | Faithful diff | Omission diff |
|---|---:|---:|
| status_aware vs neutral | +0.400 [0.233, 0.567] | −0.367 [−0.533, −0.200] |
| neutral_source vs neutral | **+0.533 [0.367, 0.700]** | **−0.400 [−0.567, −0.233]** |
| status_aware_source vs status_aware | +0.067 [0.000, 0.167] | −0.033 [−0.100, 0.000] |
| status_aware_source vs neutral_source | −0.067 [−0.167, 0.000] | 0.000 |
| status_aware_source vs neutral | +0.467 [0.300, 0.633] | −0.400 [−0.567, −0.233] |
| interaction (faithful) | **−0.467 [−0.633, −0.300]** | — |

## 4. Interpretation

1. **Source access is the strongest mitigation in this task family.** Neutral
   prompt with the original dialogue at rewrite time preserves status in 30/30
   items and never omits or distorts it. This is a near-ceiling result for the
   template design.
2. **The status-aware prompt alone is a partial mitigation.** It raises
   faithful status from 0.52 to 0.87 and cuts omission from 0.44 to 0.03, but
   introduces two conditional collapses (`将 + action` treated as committed) and
   one ambiguous item. It is not a complete fix.
3. **The two mitigations are not additive.** Adding status-aware to source
   access lowers faithful status from 30/30 to 28/30 (interaction −0.467) and
   adds one unsupported distortion. When the source is available, the prompt's
   future-action phrasing can create new escalations.
4. **Practical implication.** If the architecture can expose the original
   evidence at rewrite time, do that first. A status-aware prompt is a
   low-cost fallback when source access is impossible, not a substitute for it.
5. **Reliability caveat.** Primary κ 0.689 is below the calibration gate; the
   result is **provisional** until v3.2.4 is calibrated. The large source-access
   contrast (30/30 vs 14/27) is unlikely to be a labeling artifact, but the
   small combination differences (2 items) are not interpretable at this
   reliability.

## 5. Gate

- Completeness: PASS (30/30, 120/120).
- Budget: PASS (max 1.38× < 1.5×).
- Human reliability: **NOT MET** (primary κ 0.689 < 0.80).
- Effect: large for source access; partial for status-aware; negative
  interaction for the combination.

## 6. Next

1. Add v3.2.4 clarifications: nominalized predicates; `将 + action` =
   COMMITTED vs `计划/打算` = CONSIDERING; contradictory cues =
   AMBIGUOUS_UNASSESSABLE; aspect/negative action states.
2. Recheck the 29 adjudicated items under v3.2.4, or re-annotate all 120 if a
   clean reliability gate is required. Do not report the P5 confirmatory
   difference as definitive before that.
3. Update the paper: source access is the primary mitigation; status-aware is
   a partial fallback; the combination is not additive.
