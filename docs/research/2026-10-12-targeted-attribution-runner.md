# Targeted attribution runner

Date: 2026-10-12

## Motivation

After fixing lifecycle attribution to require exact turn-level provenance, provenance-sensitive cases need to be rerun through the final `run_oracle_experiments -> attribute_failure` path.

Running the full LoCoMo benchmark for every single case is unnecessarily expensive during evaluator validation. A targeted runner was therefore added.

## New tool

`experiments/run_targeted_attribution.py`

The runner accepts one or more exact normalized question IDs:

```powershell
G:\aconda\python.exe -u -m experiments.run_targeted_attribution --dataset locomo_refined_public --question-id "conv-26#q0002"
```

Multiple questions can be supplied by repeating `--question-id`:

```powershell
G:\aconda\python.exe -u -m experiments.run_targeted_attribution --dataset locomo_refined_public --question-id "conv-26#q0002" --question-id "conv-26#q0016" --question-id "conv-26#q0041"
```

The runner reuses the existing `run_record()` implementation, so the targeted result follows the same lifecycle tracing, evidence gate, answer scoring, and final attribution path as the main experiment.

Results are saved to:

`results/oracle_experiments/targeted_attribution.json`

## Regression coverage

Added:

`tests/test_targeted_attribution_runner.py`

The test verifies that the CLI exposes the exact `--question-id` option.

## Research purpose

This runner is specifically for the current provenance validation sequence:

```text
q0000 -> final F1 validation already completed
q0002 -> final attribution validation pending
q0016 -> final attribution validation pending
q0041 -> final attribution validation pending
          |
          v
     rerun n=50 only after all targeted checks pass
```

The targeted runner does not change the attribution algorithm. It is an experiment-control convenience that makes evaluator regression checks reproducible and cheap enough to run repeatedly.
