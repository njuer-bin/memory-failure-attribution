# Multi-hop Gold Evidence Human Review Protocol

## Purpose

Step 3 generated conservative LoCoMo multi-hop candidates. The 65 candidates from the first 100 normalized records are **not** treated as 65 confirmed multi-hop questions.

This step creates a human-review artifact so that hop count, hop type, ordered evidence path, relations, and bridge evidence are frozen independently of the candidate-generation heuristics.

## Review principle

> Evidence count is not hop count.

Multiple gold evidence items may support one direct answer. A question is multi-hop only when answering it requires combining evidence through an ordered relationship/path rather than merely reading one evidence item or independently aggregating several facts.

## Fields to annotate

- `human_is_multi_hop`: `yes` / `no` / `uncertain`
- `human_hop_count`: integer when known; leave blank when uncertain
- `human_hop_type`: `single`, `multi_hop`, `temporal`, `causal`, `entity`, or `unknown`
- `human_ordered_path`: evidence IDs in reasoning order, e.g. `e1 -> e3 -> e5`
- `human_relations`: explicit relation labels between adjacent evidence nodes, e.g. `e1 -cause-> e3; e3 -leads_to-> e5`
- `human_bridge_evidence`: IDs that connect otherwise separate facts
- `annotation_status`: initially `unreviewed`; later `reviewed` or `adjudicated`
- `notes`: short justification or ambiguity note

## Annotation rules

1. Do not infer a path merely because evidence appears in chronological order.
2. Do not infer multi-hop merely because there are two or more gold evidence items.
3. Prefer the smallest sufficient evidence path that supports the reference answer.
4. Mark `uncertain` when the evidence supports the answer but the relationship/path cannot be established reliably.
5. Do not invent relations that are absent from the evidence.
6. For temporal questions, distinguish a temporal lookup from a genuine multi-step temporal chain.
7. For causal questions, require evidence that connects cause and outcome; the presence of the words “why” or “because” is not sufficient.
8. For relational questions, require an entity/relationship chain rather than a single direct relation.
9. A bridge node is evidence needed to connect otherwise separate facts; it should be explicitly listed when present.
10. Keep the original gold evidence text/provenance unchanged.

## Workflow

1. Run candidate generation on the target dataset.
2. Export the candidate JSONL to a CSV review sheet.
3. Human-review every candidate.
4. Adjudicate uncertain/disputed cases.
5. Freeze the reviewed JSON/CSV as the Gold Multi-hop Dataset.
6. Only then evaluate R1-R4 failure attribution.

## Export command

```text
G:\aconda\python.exe -u -m experiments.export_multihop_review_csv --input results\multihop_candidates\locomo_refined_public_candidates.jsonl
```

Default output:

`results/multihop_candidates/locomo_refined_public_human_review.csv`

## Research boundary

The review artifact is intentionally separate from MemoryEngine behavior. Candidate generation may have false positives, but it must not silently define the experimental gold labels. The human-frozen labels are the ground truth for later multi-hop failure attribution and P10-inspired ablations.
