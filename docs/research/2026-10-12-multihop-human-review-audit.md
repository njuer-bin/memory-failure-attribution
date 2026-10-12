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

The CSV is mechanically complete and the reviewer applied the intended conservative rule well to most direct, temporal, and causal questions. However, there is a major conceptual issue before this dataset can be frozen as a **multi-hop chain** Gold set:

> 10 of the 11 rows currently labeled `human_is_multi_hop=yes` are better described by their own notes as **multi-evidence aggregation/enumeration/counting**, not relational multi-hop chains.

Only two rows currently have strong, text-verifiable multi-hop structure: `q0011` and `q0059`.

One additional row, `q0041`, should be re-adjudicated because the supplied evidence text does not expose the image content needed to verify the claimed shared subject.

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

## Rows requiring relabeling or taxonomy separation

### q0016 — independent location enumeration

`e0`, `e1`, and `e2` independently provide beach, mountains, and forest. There is no evidence-to-evidence relation/path. The note itself calls this `Enumeration aggregation`.

**Audit verdict: not relational multi-hop.**

### q0029 — independent activity enumeration

The four evidence items independently supply four LGBTQ-community activities: activist group, pride parade, art show, and mentorship program. The answer is a union of independent facts.

**Audit verdict: not relational multi-hop.**

### q0030 — counting aggregation

Two independent beach mentions are combined to answer a count of 2. This is aggregation/counting, not a two-hop relation chain.

**Audit verdict: not relational multi-hop.**

### q0036 — one evidence already names the requested supporter groups

e1 directly names `friends, family and mentors`. e0 provides contextual support after the negative experience, but the reference answer's entities are already supplied by e1. The current note says both are needed, but the requested names are not derived through a path.

**Audit verdict: not relational multi-hop; likely single/direct or evidence aggregation.**

### q0038 — independent pet-name enumeration

e0/e1 distribute pet names across messages. Their union gives Oliver, Luna, Bailey, but there is no relation chain between evidence nodes.

**Audit verdict: not relational multi-hop.**

### q0041 — shared-subject/image evidence ambiguity

The answer is `Sunsets`, but the textual evidence shown in the CSV only says that Caroline and Melanie painted; it does not state `sunset` in the text. The current annotation treats each evidence item as contributing the shared subject, but that subject appears to depend on image content not represented in the textual evidence.

**Audit verdict: RE-ADJUDICATE.** If image evidence is available and both images independently establish `sunset`, this is multi-evidence aggregation, not a relational chain. If the image content is unavailable, keep `uncertain`.

### q0045 — independent instrument enumeration

e0 supplies clarinet and e1 supplies violin. Combining the two facts gives the answer, but there is no evidence-to-evidence relation.

**Audit verdict: not relational multi-hop.**

### q0046 — independent artist/band enumeration

e0 supplies Summer Sounds and e1 supplies Matt Patterson. This is a union of independent facts, not a chain.

**Audit verdict: not relational multi-hop.**

### q0062 — independent purchase enumeration

e0 supplies figurines and e1 supplies shoes. The answer is the union of two independent purchase facts.

**Audit verdict: not relational multi-hop.**

## Important methodological finding

The current annotation has implicitly mixed two different capabilities:

1. **Relational multi-hop reasoning**
   - A -> B -> C
   - requires identity, co-reference, causal, temporal, or entity relations between evidence nodes.

2. **Multi-evidence aggregation**
   - A + B + C -> answer set/count
   - each evidence contributes an independent answer item.

These are both legitimate memory capabilities, but they should not share the same `multi_hop` label if the intended R1-R4 study is specifically about **evidence linking, path completeness, and bridge preservation**.

## Recommended schema change before freezing Gold

Add an explicit evidence-structure field, for example:

- `chain`: evidence nodes form a verifiable relational path;
- `aggregation`: multiple independent evidence items must be combined;
- `single`: one evidence item is sufficient;
- `uncertain`: structure cannot be established.

Alternatively, extend `human_hop_type` with `aggregation` and reserve `multi_hop` for genuine relational chains.

This would prevent a counting question such as q0030 from being interpreted as evidence-linking failure when the real capability being tested is evidence aggregation/counting.

## R1-R4 consequence

For the planned attribution study, the current 11 `yes` rows should **not** all be used as chain-style multi-hop Gold.

The strongest current chain subset is:

- q0011
- q0059

with q0041 requiring adjudication.

The remaining apparent multi-hop rows are valuable, but they should be retained as a separate **aggregation/evidence-set** subset rather than discarded.

## Freeze decision

**NOT READY TO FREEZE AS A RELATIONAL MULTI-HOP GOLD SET.**

Recommended next action:

1. re-adjudicate q0041;
2. separate `chain` from `aggregation` in the schema;
3. relabel the 9 clear aggregation rows as aggregation rather than multi-hop;
4. keep q0011 and q0059 as confirmed chain cases;
5. regenerate summary statistics;
6. only then construct R1-R4 attribution experiments.
