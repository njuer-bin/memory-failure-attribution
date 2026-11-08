# Annotation schemas

This directory contains machine-readable schemas for human evidence annotation. The current schema is a draft for the five-question LoCoMo dry run. It must be versioned when the ontology changes.

The annotation schema deliberately separates:
- evidence role (Direct / Bridge / Background / Irrelevant);
- evidence necessity (Necessary / Redundant / Optional / Distractor);
- question-level evidence sufficiency;
- dependency edges and alternative evidence paths.

Do not treat benchmark evidence IDs as unquestionable gold labels. Annotators must verify them against the original dialogue.

