# Real-Dialogue Feasibility Audit — Stage 1 Report (2026-11-17)

Status: automated screening complete; human screening pending. The model
diagnostic below is **not** human annotation and must not be reported as such.

## 1. What was done

Built a rule-based candidate generator
(`experiments/v3_real_feasibility_audit.py`) over LoCoMo-Refined public
conversations and LongMemEval oracle instances, then selected a balanced
50-item screening set. Human screening columns are blank in
`screening_A.csv` / `screening_B.csv`; the full protocol is in
`V3_REAL_DATA_AUDIT_PROTOCOL.md`.

## 2. Automated yield

| Dataset | Candidates | Conditional | Epistemic | Intentional |
|---|---:|---:|---:|---:|
| LoCoMo (10 conversations, 19 sessions each) | 140 | 10 | 46 | 84 |
| LongMemEval oracle (500 instances, 3 sessions each) | 1,995 | 21 | 935 | 1,039 |
| Total | 2,135 | 31 | 981 | 1,123 |

- Potential status change in a later session (change cue + topic overlap):
  269/2,135 (12.6%).
- Any later-session re-mention of the same topic: 725/2,135 (34.0%).
- Screening set: 50 items (LoCoMo 20, LongMemEval 30; marker dimensions
  conditional 13, epistemic 14, intentional 23; 36 unique sources).
- Of the 50, 35 have a later-session re-mention.

The generator over-generates: broad markers match opinions, advice, and
procedure. Precision is measured only by human screening.

## 3. Model diagnostic read (not human annotation)

Provenance: Claude Sonnet 4.6 read the target span plus adjacent turns for all
50 items on 2026-11-17. Stored in `diagnostic_read.csv`; summary in
`analysis/diagnostic_summary.json`. These ratings are a design aid and must be
replaced by two independent human annotations before any scientific claim.

| Field | Result |
|---|---|
| Status-bearing | yes 42, ambiguous 3, no 5 |
| Semantic dimension | intentional 32, conditional 8, mixed 3, epistemic 2, none 5 |
| Proposition clear | yes 43 |
| Evidence sufficient | yes 39, partial 6, no 5 |
| Lexically labelable | yes 43 |
| Semantically labelable | yes 42 |
| Consequential | yes 4, partial 29, no 17 |
| Difficulty | 1: 32, 2: 11, 3: 7 |

Semantically labelable by dimension: intentional 29, conditional 8, mixed 3,
epistemic 2.

## 4. Findings

**F1. Intentional status is the extractable phenomenon; epistemic status is
nearly absent.** The marker-based "epistemic" bucket (14 screening items)
dissolves on semantic reading into intentions and opinions: only 2 items are
genuine epistemic status propositions ("I think I got the price wrong",
uncertainty about seeding a tank). Most "I think / definitely" matches are
"I think I'll ..." plans or evaluative stances. A lexical cue metric would
count these as epistemic status when the status is actually intentional or
absent.

**F2. Conditional status is thin and mostly low-stakes.** Eight items are
semantically conditional, but they are dominated by backup plans ("just in
case"), preferences ("as long as it's safe"), and conditional repairs. Only a
few involve a condition whose satisfaction changes a consequential action.

**F3. Evidence availability is not the bottleneck.** 39/50 items have
sufficient original evidence to assign a gold status. The bottleneck is
identifying and typing the proposition, not finding the evidence.

**F4. Update opportunity exists, but explicit status change is rare.** 35/50
items are re-mentioned in a later session; only one item shows a clear
self-correction. LongMemEval oracle haystacks contain only three sessions, so
they offer little depth; LoCoMo's 19-session histories are the better base for
rewriting-depth and recovery experiments.

**F5. Decision-relevant propositions are scarce.** Only 4/50 items are clearly
consequential in the sense P4 needs (authorization, money, health, commitments
to others); 29 are partially relevant (trips, events, purchases); 17 are
low-stakes (books, recipes, chores). A P4.2 that samples real dialogue will be
underpowered; it needs curated high-stakes scenarios.

**F6. The lexical/semantic split is necessary, not cosmetic.** Every screening
item has an explicit cue by construction, yet 7 cannot support a lexical
fidelity metric and 8 cannot support a semantic one. More importantly, the
lexical cue type misassigns the semantic dimension in most epistemic matches.
Measuring only cue retention would answer "was the word kept?", not "was the
status kept?".

## 5. Gate evaluation (provisional, on the diagnostic read)

| Gate | Threshold | Diagnostic result | Verdict |
|---|---|---|---|
| Status-bearing yield | >= 35/50 | 42 | provisional pass |
| Semantic labelability | >= 30/50 | 42 | provisional pass |
| Dimension coverage | >= 8 per used dimension | intentional 32, conditional 8, epistemic 2 | **epistemic fails** |
| Update opportunity | >= 25/50 later mention | 35 | pass |
| Downstream relevance | >= 10/50 clearly consequential | 4 | **fails** |

Overall: the audit supports a real-dialogue study of **intentional** status,
with **conditional** as a secondary and deliberately enriched dimension. It
does not support transplanting the three-dimension V3 design unchanged, and it
does not support sampling P4.2 scenarios from these data.

## 6. Recommendation for Stage 2

1. **Primary dataset: LoCoMo**, because of its long multi-session histories.
   Use LongMemEval's knowledge-update subset as a second-domain check, not as
   the depth experiment.
2. **Dimensions: intentional first; conditional second; epistemic only with
   targeted elicitation** (e.g., explicit uncertainty about a fact that later
   resolves). Do not claim three-dimension coverage from marker sampling.
3. **Freeze the two metrics** (LSF and SSF) and the screening fields before any
   formal annotation. Two independent human annotators, blind to condition and
   gold; pre-registered adjudication; model assistance flagged.
4. **Curate P4.2 scenarios**: authorization, money, health, and commitments to
   others. Do not sample them from chat corpora and hope for consequence.
5. **Report the candidate-generator precision** from human labels. The 42/50
   diagnostic figure is an upper bound for the current rule, not a prevalence
   estimate.

## 7. Limitations

- Screening set is top-scored, not a random sample; no prevalence estimate.
- English-only dialogue; the V3 synthetic pilot was Chinese.
- The generator's marker lists are hand-built and were iterated on this sample;
  they need validation on held-out conversations.
- Only one model diagnostic read; no inter-annotator agreement yet.
- LoCoMo speakers are two named individuals in a public benchmark; identifying
  details were not used in coding.

## 8. Artifacts

- Generator: `experiments/v3_real_feasibility_audit.py`
- Protocol: `docs/research/V3_REAL_DATA_AUDIT_PROTOCOL.md`
- Candidates: `results/status_drift_v3_real_audit/candidates.csv`
- Screening sheets: `screening_50.csv`, `screening_A.csv`, `screening_B.csv`
- Diagnostic read: `diagnostic_read.csv`, `analysis/diagnostic_summary.json`
- Automated summary: `analysis/feasibility_summary.json`

## 9. Update after the 50-item screen (2026-11-17)

Both sheets are filled, but the pair is not two independent humans: B records
itself as a rubric-guided model and A's provenance is blank. Agreement and the
resulting rubric revisions are in `2026-11-17-real-screening-results.md`.
Dimension (kappa 0.826) and semantic labelability (0.730) are usable;
`lexical_labelable` (0.226) and `update_present` (0.170) fail and are being
redefined in `V3_REAL_STAGE2_DRAFT.md` v2. The provisional gate verdict is
unchanged: intentional is viable, conditional needs enrichment, epistemic is
dropped, and P4.2 needs curated high-stakes scenarios.
