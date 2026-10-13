# Multi-hop Human Review Audit

Date: 2026-10-12
Branch: `feat/multihop-human-review`
Source: `results/multihop_candidates/locomo_refined_public_human_review_annotated.csv`

## Audit scope

Audited all 65 reviewed candidate rows in the submitted human-review CSV. The audit checks whether the labels are consistent with the repository's own review protocol, especially the rules:

- evidence count is not hop count;
- multi-hop requires an ordered relationship/path, not merely multiple independent facts;
- chronological order alone is insufficient;
- relations must not be invented;
- the smallest sufficient path should be preferred;
- `uncertain` is appropriate when the answer is supported but the path cannot be verified.

## Overall result

The CSV is mechanically complete and the reviewer applied the intended conservative rule well to most direct, temporal, and causal questions. However, there is a major conceptual issue before this dataset can be frozen as a **relational multi-hop chain** Gold set:

> Of the 11 rows currently labeled `human_is_multi_hop=yes`, 8 are clearly multi-evidence aggregation/enumeration/counting rather than relational multi-hop chains, 2 are strong relational chains, and 1 (`q0041`) is ambiguous because the supplied textual evidence does not expose the image content needed for adjudication.

Only two rows currently have strong, text-verifiable multi-hop structure: `q0011` and `q0059`.

Therefore, **do not freeze the current `yes` labels as the R1-R4 chain Gold set yet.**

## Label distribution

- `no`: 51 / 65 = 78.5%
- `yes`: 11 / 65 = 16.9%
- `uncertain`: 3 / 65 = 4.6%

Hop-type distribution:

- `temporal`: 35
- `single`: 13
- `multi_hop`: 10
- `entity`: 1
- `causal`: 3
- `unknown`: 3

The three `uncertain` rows are `q0001`, `q0054`, and `q0091`; their notes correctly explain that the supplied Gold Evidence does not contain enough information to verify the requested answer/path.

## Strong multi-hop rows

### q0011 — valid entity/co-reference chain

Question: `Where did Caroline move from 4 years ago?`

Path:

`e0 -> e1`

- e0 establishes that Caroline moved from `my home country` four years ago.
- e1 identifies `my home country` as Sweden.

This is a genuine two-hop entity/co-reference chain. The relation is explicit in the annotation and the bridge evidence is correctly identified as e1.

**Audit verdict: KEEP as multi-hop.**

### q0059 — valid co-reference/count chain

Question: `How many children does Melanie have?`

Path:

`e0 -> e1`

- e0 establishes that Melanie has a son.
- e1 says `their brother would be OK`, which establishes additional children/siblings and allows the total to be derived as three.

This is a genuine relational/co-reference chain rather than simple independent enumeration.

**Audit verdict: KEEP as multi-hop.**

## Clear aggregation rows

The following 8 rows are better modeled as `aggregation` because each evidence item contributes an independent answer item or count component, without an evidence-to-evidence relation/path:

- `q0016` — beach, mountains, forest.
- `q0029` — activist group, pride parade, art show, mentorship program.
- `q0030` — count of two beach mentions.
- `q0036` — requested supporter groups are directly supplied rather than derived through a path.
- `q0038` — independent pet-name enumeration.
- `q0045` — clarinet + violin.
- `q0046` — Summer Sounds + Matt Patterson.
- `q0062` — figurines + shoes.

These are legitimate evidence-composition tasks and should be retained as an **aggregation/evidence-set** subset, not discarded.

## q0041 — requires adjudication

The answer is `Sunsets`, but the textual evidence shown in the CSV only says that Caroline and Melanie painted; it does not state `sunset` in the text. The current annotation treats each evidence item as contributing the shared subject, but that subject appears to depend on image content not represented in the textual evidence.

**Audit verdict: keep `uncertain` in the frozen derived dataset until image evidence is explicitly available.** If image evidence later establishes that both images depict sunsets, classify it as `aggregation`, not a relational chain.

## Important methodological finding

The current annotation has implicitly mixed two different capabilities:

1. **Relational multi-hop reasoning**
   - A -> B -> C
   - requires identity, co-reference, causal, temporal, or entity relations between evidence nodes.

2. **Multi-evidence aggregation**
   - A + B + C -> answer set/count
   - each evidence contributes an independent answer item.

These are both legitimate memory capabilities, but they should not share the same `multi_hop` label if the intended R1-R4 study is specifically about **evidence linking, path completeness, and bridge preservation**.

## Schema change

The derived Gold representation now uses an explicit `evidence_structure` field:

- `chain`: evidence nodes form a verifiable relational path;
- `aggregation`: multiple independent evidence items must be combined;
- `single`: one evidence item is sufficient;
- `uncertain`: structure cannot be established.

The original human annotation CSV is preserved unchanged. A separate freeze utility produces a structure-aware derived CSV.

## R1-R4 consequence

For the planned attribution study, only `chain` rows should be used as the primary R1-R4 relational multi-hop Gold set. The aggregation rows should be evaluated separately because their failure modes are about evidence-set completeness rather than bridge/path linking.

Current confirmed chain subset:

- q0011
- q0059

Current aggregation subset:

- q0016
- q0029
- q0030
- q0036
- q0038
- q0045
- q0046
- q0062

Current unresolved structure:

- q0041

## Freeze decision

**The original annotation remains unfrozen as relational multi-hop Gold. The new structure-aware derived dataset is the controlled input for the next experiment.**

Next action:

1. use `experiments/freeze_multihop_structure.py` to generate the derived dataset;
2. validate `chain` / `aggregation` / `single` / `uncertain` invariants with tests;
3. build R1-R4 attribution only on confirmed `chain` cases;
4. analyze aggregation cases separately.
