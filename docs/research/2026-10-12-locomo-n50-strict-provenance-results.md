# LoCoMo n=50 Strict Provenance Results

**Date:** 2026-10-12  
**Dataset:** `locomo_refined_public`  
**Sample size:** 50  
**Evaluation mode:** strict turn-level provenance for lifecycle attribution

## 1. Purpose

This experiment reruns the first 50 LoCoMo questions after replacing semantic lifecycle fallback with strict turn-level provenance matching.

The previous lifecycle evaluator could treat a semantically similar memory from another turn/session as `found`. This could mask a true Formation failure and inflate lifecycle recall. The strict evaluator requires the specific Gold Evidence `source_turn_id` / `turn_id` to be present at each lifecycle stage. Semantic similarity remains diagnostic only and cannot make a lifecycle stage pass.

The targeted validation of `conv-26#q0002`, `conv-26#q0016`, and `conv-26#q0041` had already confirmed the corrected attribution path, with all three ultimately attributed to `F1_FORMATION`.

## 2. Experiment outcome

- Records: 50
- Errors: 0
- Real Memory accuracy: 2% (1/50)
- Oracle Memory accuracy: 60% (30/50)
- Oracle Context accuracy: 60% (30/50)
- Evidence sufficient: 46/50
- Evidence insufficient / E0: 4/50

## 3. Lifecycle recall

| Stage | Real Memory recall |
|---|---:|
| Formation | 0.17 (17%) |
| Storage | 0.98 (98%) |
| Evolution | 0.17 (17%) |
| Retrieval | 0.54 (54%) |
| Rerank | 0.505 (50.5%) |
| Context | 0.29 (29%) |

These values supersede the previous lifecycle-recall figures for research interpretation. The previous figures were produced by an evaluator that allowed semantic fallback across turns/sessions and therefore could count wrong-source memories as lifecycle success.

## 4. First lifecycle loss

For Real Memory:

| First loss | Count | Proportion |
|---|---:|---:|
| Formation | 44 | 88% |
| Retrieval | 2 | 4% |
| Context | 1 | 2% |
| None | 3 | 6% |

Under the current attribution definition, the majority of the 50 samples have their earliest observed lifecycle loss at Formation. This is a dataset- and system-specific experimental finding; it is not yet a general claim about Agent Memory systems.

## 5. Answer failure attribution

The first answer-failure distribution was:

| Failure type | Count |
|---|---:|
| F1 Formation | 40 |
| E0 Evidence insufficiency | 4 |
| F4 Retrieval | 2 |
| F5 Context | 1 |
| F6 Reasoning | 2 |

The answer scorer used local Ollama token-F1 plus temporal phrase rules. No model errors were reported.

## 6. Oracle controls

Oracle Memory had 98% lifecycle recall at every lifecycle stage, with one Formation loss, and achieved 60% answer accuracy.

Oracle Context also achieved 60% answer accuracy. It is treated as a reasoning control rather than a theoretical upper bound.

The equality of Oracle Memory and Oracle Context accuracy suggests that, in this n=50 experiment, providing the correct evidence did not introduce an additional measurable answer-accuracy loss between Oracle Memory and the final context control. This does not establish that reasoning is never a bottleneck.

## 7. Main methodological finding

The most important finding from this rerun is the large change in Formation recall after enforcing provenance:

- Previous evaluator: Formation recall = 88.5%
- Strict provenance evaluator: Formation recall = 17%

Evolution recall changed similarly from 88.5% to 17%.

The change should not be interpreted as a sudden change in the MemoryEngine itself. The MemoryEngine and benchmark sample were rerun; the major methodological difference is the lifecycle matching criterion.

The result demonstrates that semantic fallback can substantially overestimate lifecycle retention when similar memories exist at different turns/sessions.

Conceptually:

```text
Gold Evidence
    |
    +-- exact source turn exists -> lifecycle PASS
    |
    +-- exact source turn missing
            |
            +-- similar memory elsewhere -> WRONG_SOURCE_SEMANTIC (diagnostic only)
            |
            +-- no similar memory -> TRUE_MISS
```

Therefore, semantic similarity is useful for diagnosis but should not be used as causal lifecycle evidence.

## 8. Interpretation boundary

The following claims are supported by this experiment:

1. Strict turn-level provenance materially changes lifecycle-recall estimates on `locomo_refined_public` n=50.
2. Under the current evaluator and MemoryEngine, Formation is the earliest observed loss in 44/50 samples.
3. Storage recall remains high (98%) while Formation recall is much lower (17%), indicating that raw-message persistence and formation of the corresponding memory representation should be analyzed as distinct failure points.
4. Oracle Memory and Oracle Context both reach 60% answer accuracy in this sample.

The following claims are **not** established yet:

- Formation is the dominant failure source for Agent Memory in general.
- The observed n=50 distribution generalizes to other datasets or memory systems.
- The 2 F6 cases are definitive reasoning failures without further case-level audit.
- Oracle Context is a theoretical optimum.

## 9. Next analysis

Before increasing the sample size, compute conditional/transition failure rates. In particular, distinguish:

- true Evolution failures among cases that successfully formed the relevant evidence;
- true Retrieval failures among cases that survived Formation and Evolution;
- true Rerank failures conditional on Retrieval success;
- true Context failures conditional on Rerank success.

This avoids interpreting downstream low recall as independent failures when an upstream Formation failure has already prevented the relevant evidence from existing.

After conditional analysis and evaluator validation, proceed to larger samples (target n>=100) and bootstrap confidence intervals. A human-annotation subset of roughly 20-30 cases should also be used to validate the attribution/evidence-gate stack before making broad causal claims.
