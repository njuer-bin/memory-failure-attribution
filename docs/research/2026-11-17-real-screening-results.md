# Real-Screening Results and Rubric Defects (2026-11-17)

Status: diagnostic only. **This is not a two-human reliability result.**
Annotator A records `role=human` (WMY). Annotator B records `role=model`
(YTB-directed WorkBuddy; the `model_assistance` field states that all 10
scoring columns were AI-produced with no independent human annotation). The
agreement below is useful for finding rubric defects, not for validating the
instrument.

Provenance note: B's returned file initially set `role=human` while its own
`model_assistance` field said full AI generation. The role was corrected to
`model` and the correction is preserved in
`screening_provenance_B.json`; approving model output is not independent human
annotation.

## 1. What was filled

- 50 items, 9 rating fields each; no blanks or invalid values.
- A: 46 status-bearing, 36 intentional, 5 epistemic, 5 conditional,
  2 mixed, 2 none.
- B: 43 status-bearing, 36 intentional, 3 epistemic, 6 conditional,
  1 mixed, 4 none.
- Both: all 50 have an explicit cue; 35 have a later-session mention.

## 2. Agreement

| Field | Raw | Cohen's kappa | Disagreements | Reading |
|---|---:|---:|---:|---|
| `status_bearing` | 0.920 | 0.606 | 4 | raw high, kappa dragged by prevalence; 4 boundary items |
| `dimension` | 0.920 | **0.826** | 4 | usable after anchor fixes |
| `proposition_clear` | 0.960 | 0.648 | 2 | boundary items only |
| `evidence_sufficient` | 0.820 | 0.535 | 9 | definition conflates two questions |
| `lexical_cue_present` | 1.000 | n/a | 0 | degenerate: every item has a cue |
| `lexical_labelable` | 0.660 | **0.226** | 17 | severe rubric defect |
| `semantic_labelable` | 0.960 | **0.730** | 2 | usable after anchor fixes |
| `update_present` | 0.840 | **0.170** | 8 | severe rubric defect |
| `difficulty_1_3` | 0.840 | 0.750 | 8 | usable |

The fields that Stage 2 depends on most — `lexical_labelable` and
`update_present` — are the two that fail. This is a rubric problem, not
annotator noise: the disagreements are one-directional and traceable to the
wording of the definitions.

## 3. Defect analysis

### D1. `lexical_labelable` is ambiguous (17 disagreements)

A read it as "a cue is present and a rule could fire"; B read it as "a
cue-based rule would assign the correct status type". The second reading is the
one Stage 2 needs.

Examples:

- RD-031 "I think I'll try out the FL Studio demo": cue `I think` maps to
  epistemic, but the semantic status is intentional. A=yes, B=no.
- RD-008 "I'll definitely check it out": cue `definitely` maps to epistemic,
  status is intentional. A=yes, B=no.
- RD-027 "I'll also pack ... just in case": cue `in case` maps to conditional,
  and the status is conditional; B still said no, so B was not uniformly
  applying the rule either.
- RD-026 "worried it'll break off if I don't get it fixed": cue `if` maps to
  conditional, status is conditional. A=no, B=yes.

The disagreement is not random. The field must be redefined as: **would the
cue-mapping rule assign the same status type as the semantic label?** If the
cue's canonical type differs, the answer is `no` even though
`lexical_cue_present=yes`. RD-027 shows that the rule also needs an explicit
backup-phrase entry.

### D2. `update_present` has no "later mention, no change" category (8 disagreements)

A marked 9 yes; B marked 1 yes. A counted a later re-mention as an update.
Examples: RD-032 guitar service, RD-037 car tune-up, RD-040 future event,
RD-042 bread recipe, RD-045 San Francisco trip, RD-047 dinner party.

The field needs three states:

- `yes`: a later session changes the status; quote the change.
- `no`: a later mention exists and the status is unchanged.
- `unknown`: no later mention is available.

Both annotators collapsed `no` into `unknown`, and A collapsed re-mention into
`yes`.

### D3. `evidence_sufficient` asks two questions at once (9 disagreements)

Examples: RD-004 "hope to treat you once I learn cooking" (A=yes, B=partial),
RD-007 "maybe get pets if not allergic" (A=partial, B=yes), RD-027 "pack
detergent just in case" (A=partial, B=yes).

Sometimes the disagreement is about whether the gold status is assignable;
sometimes about whether a later memory could be compared. The field must be
split or defined as both:

- `yes`: gold status assignable **and** a later comparison is possible.
- `partial`: gold status assignable but comparison is weak.
- `no`: gold status not assignable.

### D4. Dimension anchors are missing for risk statements (4 disagreements)

- RD-005 "if I don't make changes soon, it can get worse": A=epistemic,
  B=none; semantically it is conditional.
- RD-026 "worried it'll break off if I don't get it fixed": A=epistemic,
  B=conditional; conditional is correct.
- RD-011 "I'll keep going ... definitely find those keys": self-encouragement,
  not a status; A=mixed, B=intentional; neither is `none`.
- RD-041 past bread evaluation: A=intentional, B=none; none is correct.

Add anchors: a risk statement with `if` is conditional; a past evaluation is
not a current status; self-encouragement is not a status.

### D5. Status-bearing boundary (4 disagreements)

- RD-001 "who knows if I'll ever get a pet": possibility; A=yes, B=ambiguous;
  yes is defensible.
- RD-005 conditional health risk: A=yes, B=no; yes.
- RD-024 "wondering if I can use bacteria from the old tank": A=yes,
  B=ambiguous; yes.
- RD-041 past evaluation: A=ambiguous, B=no; no.

Add these four as anchors. The prevalence of `yes` (46 vs 43) makes kappa
low even at 92% raw agreement; raw agreement must be reported with kappa.

## 4. Provisional gates

Evaluated on A and B separately; neither is a human-validated adjudication.

| Gate | Threshold | A | B | Verdict |
|---|---|---:|---:|---|
| Status-bearing yield | >= 35/50 | 46 | 43 | pass |
| Semantic labelability | >= 30/50 | 47 | 45 | pass |
| Dimension coverage | >= 8 per used dimension | intentional 36/36; conditional 5/6; epistemic 5/3 | | **conditional and epistemic fail** |
| Update opportunity | >= 25/50 later mention | 35 | 35 | pass |
| Downstream relevance | >= 10/50 clearly consequential | 4 (model diagnostic) | 4 | **fail** |

Verdict: the data support an **intentional-status** real-dialogue study.
Conditional needs targeted enrichment; epistemic is dropped (user decision).
P4.2 needs a curated high-stakes scenario bank.

## 5. Decisions recorded

1. **Epistemic:** dropped from the real-data confirmatory arm; retained in the
   frozen synthetic V3 arm as exploratory/confirmatory-by-design.
2. **Conditional:** targeted enrichment with pre-registered inclusion
   (condition state and action state both judgeable, and a consequence);
   report a natural-sample descriptive base rate separately; never call the
   enriched sample a natural distribution.
3. **P4.2:** curated scenario bank of 40-60 items across money, health,
   authorization, and commitments; proposition/evidence/task/length matched;
   only status varies; two human raters validate realism and manipulation
   before freezing.
4. **Annotators:** two independent humans are required. The current A/B pair
   does not meet this: A is human (WMY), B is YTB-directed model output. The
   screening result is therefore a human-versus-model rubric diagnostic, not
   human reliability.
5. **Sample size:** set after calibration plus a small real-data pilot; target
   a paired CI half-width of 0.10-0.12; planning target 150-200 usable
   propositions; reduce conditions before reducing items.
6. **Second domain:** use `longmemeval_s` (44-57 sessions) if the full split is
   available; the oracle variant (1-6 sessions) is not suitable for depth
   claims and is at most a construct check.

## 6. Next actions

1. Recruit a genuine second human annotator, or have YTB independently
   re-annotate the sheet—not approve the model output. Until then, no human
   reliability claim is possible. A's provenance is now recorded (WMY).
2. Revise the guide with D1-D5 (Stage 2 draft v2) and add the 17 lexical, 9
   evidence, 8 update, and 4 status anchors.
3. Re-calibrate on a **fresh** 60-item set from different conversations; do
   not reuse these 50 items for calibration.
4. Freeze the guide only after the gates pass.
5. In parallel, start the P4.2 scenario bank so it is ready when the fidelity
   instrument is frozen.

## 7. Artifacts

- Agreement: `results/status_drift_v3_real_audit/analysis/screening_agreement.json`
- Gate counts: `results/status_drift_v3_real_audit/analysis/screening_gate_counts.json`
- Labels: `screening_A.csv`, `screening_B.csv`
- Provenance: `screening_provenance_A.json` (blank), `screening_provenance_B.json` (model)
- Guide to revise: `V3_REAL_STAGE2_DRAFT.md`
