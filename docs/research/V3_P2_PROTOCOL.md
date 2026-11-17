# V3 P2 Paired Transformation Study — Frozen Protocol

**Status:** frozen 2026-11-17 before confirmatory generation. Do not modify the
generation script or condition definitions based on interim outputs. Any change
creates a new protocol version and a separate cohort.
**Ontology / annotation:** `V3_FORMAL_DEFINITIONS.md` §12 (v3.2.3),
`V3_ANNOTATION_GUIDELINES.md` (v3.2.3).
**Analysis plan:** `V3_STATISTICAL_ANALYSIS_PLAN.md` §11.
**Freeze record:** `V3_P2_FREEZE.md`.

## 1. Trajectories

30 synthetic trajectories, all new to the confirmatory cohort:

- 5 topics × 3 dimensions (epistemic, intentional, conditional) × 2 update
  variants (stable, updated) = 30.
- Topics: `换一份工作`, `开始健身`, `开一家网店`, `学会游泳`, `考驾照`.
- None of these topics was used in the P1a/P1b/P1c pilots. P1 used
  `购买电脑`, `去上海工作`, `申请研究生`, `参加数学建模比赛`,
  `开始学习日语`, `申请海外交换`, `报名马拉松`.
- Templates follow `_make_row` (epistemic: possible → confirmed; intentional:
  considering → committed; conditional: prerequisite active → satisfied, with
  the action state held at consideration).

## 2. Conditions

Every trajectory appears in every condition. `raw` is the source dialogue, not a
generated memory.

| Condition | Definition |
|---|---|
| `raw` | Full source dialogue supplied at evaluation; reference ceiling. |
| `direct` | One writer call from the full dialogue to the final budget. |
| `recursive` | Five chained rewrites, budgets 220 → 180 → 140 → 120 → 100. |
| `rewrite_matched` | Five chained rewrites, budgets 220 → 220 → 220 → 220 → 100 (intermediate budgets held constant). |
| `repeated_direct` | Five independent direct compressions of the full dialogue at budget 100, keeping the last; matches call count without chaining. |
| `source_peek` | Five chained rewrites with the original dialogue appended at every stage; same budget schedule as `recursive`. |
| `para` | Five chained rewrites with the `neutral_paraphrase` prompt; same schedule as `recursive`. |
| `temp1` | Five chained rewrites at temperature 0.7, seed 42. |
| `temp2` | Five chained rewrites at temperature 0.7, seed 43. |
| `path_s2` | Five chained rewrites with schedule 220 → 160 → 150 → 120 → 100; schedule-only control. |
| `retrieval` | Lexical evidence retrieval from the source turns under budget 100; deterministic, no writer call. |

`recursive` is the S1 schedule and serves as the reference chained condition.

## 3. Generation settings

- Writer model: `qwen2.5:7b` via local Ollama (`http://127.0.0.1:11434`).
- Prompt style: `neutral` (the status-aware prompt is a mitigation for P5, not
  a P2 condition).
- Final budget: 100 Chinese characters, as a prompt target, not a hard
  truncation.
- Temperature 0.0 for all deterministic conditions; 0.7 for `temp1`/`temp2`.
- Seed 42 for deterministic conditions and `temp1`; seed 43 for `temp2`.
- `num_predict` 220; timeout 180 s; 2 retries.
- Record model digest from `/api/tags` in `run_config.json`.

## 4. Artifact schema

For every trajectory × condition:

- condition name, spec, prompt style, temperature, seed, schedule;
- every intermediate memory and its size (characters, UTF-8 bytes);
- final memory;
- prompt-eval and eval token counts, total/load/eval durations;
- retry count, error text, completion status;
- timestamp;
- prompt hash (system + user template) for each prompt style.

Files: `records.jsonl` (one trajectory per line), `run_config.json`,
`summary.json`, `errors.jsonl`. No output is dropped because of length or
content.

## 5. Exclusions

Predeclared only:

- corrupted or missing source dialogue;
- target proposition absent from the source;
- generation failure after all retries;
- malformed artifact that cannot be evaluated.

Do not exclude by observed label, length, condition performance, or interim
diagnostics. Report every exclusion with reason and condition.

## 6. Completeness gate

P2 is a generation phase, not a hypothesis test. The gate is:

- 30/30 trajectories attempted;
- every declared condition present for every trajectory (300 generated
  conditions + 30 raw references = 330 artifacts);
- 0 silent missing conditions;
- generation error rate ≤ 1% after retries, with all errors logged;
- deterministic topic-mention diagnostics reported, but **not** used as a
  proposition-retention gate.

Proposition retention and status fidelity are measured by blind human
annotation in P3 under the frozen v3.2.3 guide.

## 7. Primary contrasts (analysis after P3 labels)

- Source access: `source_peek` vs `recursive`.
- Decoding: `temp1`/`temp2` vs `recursive`; `temp1` vs `temp2` is sampling
  variance.
- Prompt wording: `para` vs `recursive`.
- Chaining mechanism: `rewrite_matched` vs `recursive`; `repeated_direct` vs
  `recursive`; `direct` vs `recursive`.
- Schedule-only: `path_s2` vs `recursive` (near-null control).
- Reference: `raw` and `retrieval`.

Primary outcome is the joint distribution of proposition identity × status
fidelity, reported unconditionally; conditional USDR is secondary and never
reported alone.

## 8. Data isolation

P2 outputs are not pooled with v2.x exploratory runs or P1a–P1c pilots. The
annotator provenance limitation (annotator-unspecified calibration) applies to
the guide calibration, not to P2 generation.

## 9. Freeze rule

The runner and this protocol are hashed in `V3_P2_FREEZE.md`. Confirmatory
generation starts only after the hashes are recorded. Interim outputs do not
change the design.
