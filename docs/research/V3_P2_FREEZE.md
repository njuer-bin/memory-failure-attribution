# V3 P2 Freeze Record (2026-11-17)

**Decision:** freeze the v3.2.3 annotation ontology and the P2 paired
transformation design before confirmatory generation.

## Frozen artifacts (SHA-256)

| SHA-256 | File |
|---|---|
| `6e7fe4307dd27cc07ce205c263ab9534805cf9c51784f256c4e93532793f219b` | `docs/research/V3_ANNOTATION_GUIDELINES.md` (v3.2.3) |
| `85e52413afb2779663f047eb4ffef8b52d2bc6c3873e5c347b4b4a3d3d5fe3e2` | `docs/research/V3_ANNOTATION_HOWTO.md` (v3.2.3) |
| `ff26e30ee4441c0f40a51e9cf04834d055c2d76c20c50534d458d65b6449abcb` | `docs/research/V3_FORMAL_DEFINITIONS.md` (v3.2.3) |
| `053bf004492d45c5915aecf3ef5460a7ea132e60b9d65ee2843666fba098175c` | `docs/research/V3_EXPERIMENT_PROTOCOL.md` |
| `2548989c653d9d1da72fa18bcf8077ac408ff11cc21ebf4290a165b68a95e70b` | `docs/research/V3_P2_PROTOCOL.md` |
| `02b62b3da46b5b932efa9a5336d618b4ff0f1d70850e6be10f20ab78568e195d` | `docs/research/V3_STATISTICAL_ANALYSIS_PLAN.md` |
| `0d5cb0fc6f8591bdac4098f26c5fec343e2a76f5653ddd635c02f4f4026512cf` | `experiments/v3_p2_paired_study.py` |

Base commit: `70b9baa4b475518a03b57900d4fff3cb6e5550a9`.

## Calibration evidence

- V3.2.2 identity re-annotation (60 conditional items): primary-judgment
  κ 0.827, proposition identity κ 0.837, evidence support κ 0.961,
  action status κ 1.000, condition status κ 0.974.
- Pre-registered gate: primary κ ≥ 0.80 and every dimension κ ≥ 0.70. Passed.
- Seven residual boundary items were adjudicated under v3.2.3 (serial-verb
  targets, `AMBIGUOUS` identity preemption, generic satisfaction cues).
- Annotator provenance is unrecorded by maintainer decision; report the
  calibration as annotator-unspecified.

## P2 design

- 30 new trajectories: 5 topics × 3 dimensions × stable/updated.
- Conditions: `raw`, `direct`, `recursive`, `rewrite_matched`,
  `repeated_direct`, `source_peek`, `para`, `temp1`, `temp2`, `path_s2`,
  `retrieval`.
- Writer: `qwen2.5:7b`, neutral prompt, final budget 100 characters,
  temperature 0/0.7, seeds 42/43.
- Completeness gate: 30/30 trajectories, 300/300 generated conditions,
  0 silent missing, error rate ≤ 1%.
- Primary contrast: `source_peek` vs `recursive`; key secondary contrasts as
  in `V3_STATISTICAL_ANALYSIS_PLAN.md` §11.
- P3 human annotation under the frozen v3.2.3 guide is the primary
  measurement; P2 deterministic diagnostics are not proposition-retention
  evidence.

## Freeze rule

Any change to a frozen artifact invalidates this record. Create a new protocol
version and a separate cohort; do not edit P2 outputs or the runner in place.
