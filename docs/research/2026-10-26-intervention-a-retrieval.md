# Intervention (a) — targeted retrieval repair on the LoCoMo n=100 fingerprint

Status: pre-registered design, 2026-10-26. This is the P2 intervention required
by the CCF-B roadmap (contribution 4). The prior P2 arms (`first_loss` / `path`
/ `agnostic` on the oracle runs) produced gains that sat inside the A1 placebo
floor. This design changes the target to the stage the n=100 fingerprint shows
is both the largest and cleanly repairable.

## Evidence driving the choice (LoCoMo n=100, `results/systems_locomo_n200_fixedgate/`)

| system | first-loss stage counts | attributed failures | stage recall |
|---|---|---|---|
| semantic | formation 57, retrieval 22, context 3, none 17 | F1 18, F4 14, E0 21 | formation 0.473 |
| summary | context 46, rerank 30, formation 1, none 23 | F5 21, F4 10, E0 23 | context 0.258 |
| **verbatim** | **retrieval 80**, rerank 3, formation 1, none 16 | **F4 35**, E0 19 | **retrieval 0.197** |

Verbatim is the target because (i) the largest single failure mode is F4 (35
wrong answers), (ii) 80/100 questions lose gold at retrieval, so headroom is
large, and (iii) verbatim has no LLM ingestion, so re-running three arms costs
only answer + judge calls (~600 total, ≈1 h).

## Repair under test

Dense baseline ranking: `search` scores every stored turn by cosine against a
384-dim hash embedding, then takes `top_k=10` (candidate pool 20). The repair
replaces the ranking score with a deterministic hybrid:

```
score(item) = (1 - alpha) * cosine(question, item)
            + alpha      * lexical_overlap(question, item)
```

where `lexical_overlap` is the fraction of the question's content tokens
(lowercase alphanumerics, stopwords removed, length > 2) that occur in the item
text, and `alpha = 0.5` is fixed in advance (not tuned on outcomes). The item
budget (`candidate_k=20`, `top_k=10`, 6000 context chars) is unchanged, so any
gain is attributable to ranking, not to a larger context.

## Arms (same records, same answer model, judge and shared gate)

| arm | repair applied to | purpose |
|---|---|---|
| `placebo` | no-op; re-answer the F4 questions | provider/judge retest floor |
| `first_loss` | hybrid ranking on the 35 questions with baseline `F4_RETRIEVAL` | stage-targeted repair |
| `agnostic` | hybrid ranking on all 100 questions | stage-agnostic baseline |

Routing uses only the stored baseline diagnostic (never gold): `first_loss`
takes the questions whose stored attributed failure is `F4_RETRIEVAL`.

## Endpoints and pre-registered decision rule

Primary: paired accuracy on the 35 F4 questions, `first_loss` repaired vs
`placebo` (same questions; exact McNemar + paired bootstrap CI).

- **Success:** ≥6 net flips in favour of the repair on the F4 subset (the
  zero-loss McNemar threshold at n=35) **and** the bootstrap 95% CI excludes 0.
- **Stage-targeting claim:** `first_loss` gain exceeds `agnostic` gain on the F4
  subset, with the difference reported descriptively (not powered at n=35).
- **Null:** if the repair does not clear the placebo floor, report it as a null
  result — the same standard that killed the prior P2 arms.

Secondary: overall accuracy across all 100 questions; retrieval recall on the
F4 subset (must rise for the mechanism to be the intended one).

## Falsification / what would make us abandon this target

- Hybrid ranking does not raise retrieval recall on the F4 subset.
- The gain appears equally in `agnostic`, i.e. it is a generic re-ranking
  improvement rather than a stage-targeted repair.
- The placebo retest alone moves ≥3 of the 35 F4 questions (unstable judge).

## Cost and reproducibility

Three arms × 100 questions × (one answer + one semantic judge) ≈ 600 calls;
verbatim ingestion is deterministic and local. Output:
`results/retrieval_intervention_locomo_n100/`, with `interventions.jsonl` and
`summary.json`; every row stores the arm, the context item ids, the answer,
the judge verdict and the recomputed failure label.
