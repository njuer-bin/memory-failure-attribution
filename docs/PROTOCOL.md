# Frozen experiment protocol

This document records the definitions the repaired instrumentation implements.
It is the reference for the regenerated LongMemEval run and the LoCoMo
cross-benchmark run. Numbers produced before the 2026-10-18 audit repairs are
archived (see `docs/RESEARCH_LOG.md` corrigendum) and must not be mixed with
results produced under this protocol.

## Conditions

- **Real Memory** — benchmark conversation → real memory ingestion → retrieval →
  rerank → context → answer model.
- **Oracle Memory** — Gold Evidence written directly into a fresh store as raw turns,
  then retrieved through the real retrieval/rerank/context path. Formation and storage
  are controlled (direct write) and reported as unmeasured; retrieval, rerank, and
  context are measured.
- **Oracle Context** — Gold Evidence placed directly in the answer context. All stages
  before context are unmeasured; only context is measured.

## Lifecycle attribution

First-loss is computed over measured stages only, in order:
formation → storage → retrieval → rerank → context.
Evolution is **not measured** (no evolution operation is applied by the tracing layer)
and is never a first-loss stage.

## Evidence matching (recall)

For each Gold Evidence item:

- Provenance is a constraint, not proof. An artifact whose turn/session conflicts with
  the gold provenance cannot satisfy the item, even if the text is identical.
- Among provenance-compatible (or provenance-absent) artifacts, exact normalized text is
  `exact`; otherwise maximal token-overlap similarity ≥ 0.55 is `semantic`.
- A gold item whose turn matches but whose stored content does not represent it is
  `provenance_only` and counts as **missing**.
- An item matched in an artifact that carries no provenance is recorded in
  `unverified_provenance`; its share of recall is reported rather than hidden.
- Evolution recall is reported as `null`, not `0.0`.

## Evidence-sufficiency gate (E0)

The gate is judged against the **benchmark reference answer**, never the model
prediction (non-circular). The judge is told explicitly that the candidate is the
benchmark reference. If there is no Gold Evidence, or the judge errors, or the answer is
not a clear boolean, the gate is `error`/`uncertain` and attribution yields
`EVAL_SEMANTIC_UNCERTAIN`. A missing stored benchmark reference is an error condition,
never an empty-string judge call.

## Answer evaluation

Model answers are judged with the prompt that states the candidate is a
model-generated answer. Deterministic layers:

1. Pre-judge lexical support: candidate fully covered by one evidence item AND
   question-related. Relative-temporal equivalence applies only to temporal questions.
2. Post-judge repair: only for question-related candidates, or temporal answers to
   temporal questions; never for refusals (`does not provide`, `cannot`, ...).
3. Ordering refutation (2026-10-19): a post-judge FALSE-OVERTURN layer. For a
   two-option ordering question ("Which ... first, A or B?") whose candidate names
   exactly one option, the verdict flips to false only when each option's supporting
   sentence carries a resolvable date (explicit, or relative resolved against the
   turn timestamp) and the picked option's date is strictly later than the other's.
   Ambiguous cases — both or neither option named, unbindable sentences, equal
   dates, unresolvable phrases — stay with the judge. Adjudication is recorded as
   `ordering_refutation`; the offline equivalent is
   `experiments/rescore_answers.py --apply-ordering-refutation`.

## Failure attribution

Order of decisions for a failed answer:

1. `semantic_correct is True` → no failure. (`semantic_correct is None` with lexical
   `correct is True` → no failure; a contradictory semantic verdict is never overridden
   by lexical overlap.)
2. `semantic_correct is None` → `EVAL_SEMANTIC_UNCERTAIN`.
3. Gate `insufficient` → `E0_EVIDENCE_INSUFFICIENT`.
4. Gate not `sufficient` → `EVAL_SEMANTIC_UNCERTAIN`.
5. Confidence not in {medium, high} → `EVAL_SEMANTIC_UNCERTAIN`.
6. Oracle Context mode → `RC_REASONING_CONTROL_FAILURE`.
7. No gold evidence ids → `E0_EVIDENCE_INSUFFICIENT`.
8. Otherwise first missing measured stage → `F1`/`F2`/`F4`/`F5`.
9. All evidence present → `F6_REASONING_CANDIDATE`.

A missing/empty gate is a programming error and raises.

Motivation for the refutation layer (2026-10-19 audit): both qwen2.5:7b and
gemma3:12b mark the *wrong* option of a two-option ordering question correct at
high confidence when the evidence resolves the dates; a raw-judge cross-model
kappa of ≈ 0.03 shows that no LLM judge can be the sole instrument for F6.
The refutation floor is deterministic; it does not consult the judge.

## Intervention (P2)

The intervention experiment asks whether the diagnosis names a useful repair
target. It reuses the baseline run's stored trace for routing but regenerates
every answer under the same model, judge, gate and deterministic floors.

Routing arms (per question, never per dataset):

- `first_loss` — repair the stored answer-failure label: F1 → formation
  write-through, F4 → wider candidate pool, F5 → wider context, F6 →
  answer-time self-check.
- `path` — repair the stage that blocks the answer's evidence path. If the
  final context already contains every gold item, the arm routes to reasoning
  even when an earlier stage (typically semantic formation) missed it; if the
  context is missing evidence, route to context assembly, or to retrieval when
  reranking also dropped it.
- `agnostic` — apply formation write-through, context widening and self-check
  to every attributable failure (the stage-agnostic baseline).

Repairs:

- **Formation write-through** writes a provenance-carrying verbatim event for
  each raw turn whose content is not represented by any semantic artifact from
  the same turn (tracer similarity threshold 0.55). It does not read gold.
- **Retrieval repair** raises the candidate budget (`top_k` 10 → 20) with the
  context type cap unchanged.
- **Context repair** raises `top_k` 10 → 20 and the EvidenceBuilder per-type cap
  3 → 8.
- **Reasoning repair** keeps the evidence fixed and adds one temperature-0
  verification call that may replace the draft answer.

Reporting: each arm is compared with the freshly generated no-repair baseline
on its targeted subset using exact McNemar and a paired bootstrap CI; the
target-stage breakdown is reported alongside.

## Statistics

- Paired design: every condition answers the same questions. Differences use exact
  McNemar on discordant pairs and a paired bootstrap CI over questions
  (`evaluation/paired_stats.py`).
- Judge reliability is measured by re-judging stored answers (`experiments/judge_reliability.py`)
  and reported as agreement and Cohen's kappa; a different judge model should be used for
  a cross-model estimate.
- Every summary carries `run_metadata`: dataset sha256, limit, answer/judge model and
  temperature, the probed embedding backend and dimension, python version, git
  commit/branch and dirty flag. Comparisons are only valid within one embedding
  backend; the 2026-10-10-onward runs use the deterministic hash fallback
  (`hash:384`), verified from the stored vectors on 2026-10-20.

## Reproducibility checklist

- `results/oracle_experiments/` holds the current run; prior runs are archived under
  `results/archive/`.
- Judge prompt role (`candidate_is_reference`) is stored per verdict.
- Per-answer `semantic_adjudication` records the path taken (`judge`,
  `deterministic_temporal`, `deterministic_lexical`, `lexical_anchor_override`).
