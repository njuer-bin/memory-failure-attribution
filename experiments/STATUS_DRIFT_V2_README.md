# Status Drift Pilot — v2.4

This folder contains the controlled synthetic pilot runner. The current revision hardens resume safety and clarifies the distinction between topic mention, proposition identity, and status fidelity.

## Before running

1. Start local Ollama and verify the selected model.
2. From the repository root, run a smoke test in a fresh output directory:

~~~powershell
python -m experiments.status_drift_recursive_pilot --design v3 --limit 6 --writer-model qwen2.5:7b --judge-model qwen2.5:7b --out-dir results/status_drift_v2_pilot/v24_smoke
~~~

3. Inspect every generated memory and the raw judge responses.
4. Run the full 30-trajectory pilot only after the smoke test is manually reviewed:

~~~powershell
python -m experiments.status_drift_recursive_pilot --design v3 --limit 30 --writer-model qwen2.5:7b --judge-model qwen2.5:7b --rewrite-matched --out-dir results/status_drift_v2_pilot/v24_full
~~~

## Design

- v2: crossed topic × stable/update × dimension design.
- v3: same crossed design, but the final conditional turn states only whether the condition is satisfied; it does not restate the downstream action.
- raw: full dialogue.
- direct: compress full source independently at each target depth.
- recursive: repeatedly compress the previous memory.
- rewrite-matched: repeated rewrite control with matched writer-call count.

Direct/recursive/rewrite-matched final lengths are not guaranteed to match. The runner records Unicode character and UTF-8 byte lengths, not token counts. Do not call this a token-budget-matched experiment.

## Output safety

Use a new out-dir for every materially different run. Resume now requires an exact run-configuration fingerprint match and refuses cross-design/config reuse. Old output folders without fingerprints cannot be resumed under the new guard; rerun into a fresh directory.

Outputs:
- records.jsonl: source trajectories, intermediate memories, judge outputs, diagnostic topic mentions, and memory-size metadata.
- summary.json: aggregate diagnostic metrics and paired error-rate differences.
- run_config.json: run configuration and fingerprint.

Results are git-ignored. Do not commit raw outputs containing private conversations.

## Metric interpretation

- topic_mentioned is lexical mention only; it is not proposition retention.
- cpsd_judge_provisional depends on the LLM judge's own retention decision; it is not confirmatory CPSD.
- status_error_given_topic_mention is a lexical diagnostic, not semantic status drift.
- condition_marker_heuristic_* is a rule-based sanity check, not gold annotation.
- Primary unsupported status drift must be computed from human-adjudicated proposition identity and status labels. See docs/STATUS_DRIFT_V2_4_ANNOTATION_GUIDE.md.

If writer and judge are the same model, judge metrics are exploratory only.
