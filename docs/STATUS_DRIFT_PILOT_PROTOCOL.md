# Recursive Status Drift Pilot — Protocol v1.0

**Status:** pre-run protocol; no model outputs have been collected.  
**Runner:** `experiments/status_drift_recursive_pilot.py`  
**Default endpoint:** local Ollama-compatible `/api/chat`  
**Default model:** `qwen2.5:7b`

## 1. Purpose

Test whether a multi-turn dialogue memory changes the status of a target proposition under one-shot and recursive compression, while distinguishing unsupported drift from evidence-supported user updates.

This is a synthetic controlled pilot, not a benchmark and not evidence of generalization.

## 2. Dataset

The runner deterministically generates 30 Chinese trajectories:
- 10 epistemic trajectories;
- 10 intentional trajectories;
- 10 conditional trajectories.

Within each dimension, examples include both stable status and explicit later updates. Each trajectory also contains unrelated conversational turns. The default `--limit 6` runs two trajectories per dimension as a smoke test; `--limit 30` runs the full pilot set.

The gold label describes the final status after considering the entire dialogue, not merely the first utterance.

## 3. Conditions

- **Raw:** judge the full dialogue without compression.
- **One-shot:** compress the full dialogue once, then judge.
- **Recursive:** compress the previous memory repeatedly and judge at D1, D2, D3, and D5.
- **Direct-from-source:** independently compress the full dialogue to produce a comparison memory at each requested depth. This is a control for repeated rewriting, not a claim of token-budget equivalence.

The recursive writer receives only the previous compressed memory after D1. It does not receive the original transcript again.

## 4. Labels

- Epistemic: `POSSIBLE`, `CERTAIN`.
- Intentional: `CONSIDERING`, `COMMITTED`.
- Conditional: `CONDITION_ACTIVE`, `CONDITION_SATISFIED`.

The judge also returns `proposition_retained` and a short rationale. Parse failures and ambiguous labels are retained as errors; they are not silently converted to correct labels.

## 5. Metrics

- Accuracy by condition and dimension.
- Proposition retention rate.
- CPSD = status errors among proposition-retained memories / proposition-retained memories.
- Omission rate.
- Legitimate transition accuracy (subset with explicit later update).
- Paired recursive-vs-direct error delta at each depth.

Because this is a small synthetic pilot, report raw counts and denominators. Do not use significance tests to imply generalizable findings.

## 6. Run commands

Smoke test:
```bash
python -m experiments.status_drift_recursive_pilot --limit 6 --writer-model qwen2.5:7b --judge-model qwen2.5:7b
```

Full controlled pilot:
```bash
python -m experiments.status_drift_recursive_pilot --limit 30 --writer-model qwen2.5:7b --judge-model qwen2.5:7b --resume
```

Use a genuinely independent judge model if available. If writer and judge are the same model, treat results as exploratory only.

## 7. Outputs

The runner writes:
- `results/status_drift_v2_pilot/records.jsonl`: full per-trajectory inputs, intermediate memories, judge outputs, and errors;
- `results/status_drift_v2_pilot/summary.json`: aggregate counts and metrics;
- `results/status_drift_v2_pilot/run_config.json`: run configuration.

Do not commit raw outputs containing private conversations. The included pilot uses synthetic examples only. Do not edit raw records; put human adjudications in a separate file.

## 8. Limitations

- Synthetic Chinese templates may overstate the clarity of status markers.
- The six-trajectory smoke test is only for checking the pipeline.
- Same-model writer/judge bias may be correlated.
- Direct-from-source and recursive conditions are not automatically token-matched.
- The pilot does not yet evaluate downstream actions or a mitigation method.
- A positive result supports only a model/prompt-specific observation until replicated with other models, annotators, and natural dialogue data.
