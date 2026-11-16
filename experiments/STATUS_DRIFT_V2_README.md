# Status Drift v2 Pilot

This directory contains the first multi-turn pilot for the revised research plan.

## Before running

1. Start Ollama locally.
2. Ensure the model is available, for example:
   ```powershell
   ollama pull qwen2.5:7b
   ollama list
   ```
3. From the repository root, run the smoke test:
   ```powershell
   python -m experiments.status_drift_recursive_pilot --limit 6 --writer-model qwen2.5:7b --judge-model qwen2.5:7b
   ```

The default smoke test covers two trajectories in each of the three dimensions (epistemic, intentional, conditional), including stable and evidence-supported update cases. It makes multiple local model calls per trajectory; it is not a one-request quick check.

After inspecting every output, run the full 30-trajectory synthetic pilot:
```powershell
python -m experiments.status_drift_recursive_pilot --limit 30 --writer-model qwen2.5:7b --judge-model qwen2.5:7b --resume
```

Use a different local judge model if available:
```powershell
python -m experiments.status_drift_recursive_pilot --limit 6 --writer-model qwen2.5:7b --judge-model <your-judge-model>
```

## Conditions

- Raw full dialogue.
- Direct-from-source compression at target budgets D1/D2/D3/D5.
- Recursive compression chain D1 → D2 → D3 → D4 → D5, with evaluations at D1/D2/D3/D5.

The writer prompt is held constant across direct and recursive conditions. The source text differs: full dialogue for direct compression, previous compressed memory for recursive compression.

## Output

Results are written locally to `results/status_drift_v2_pilot/` and are intentionally git-ignored. Preserve the raw JSONL and configuration locally; do not commit private dialogue data.

## Important limitations

- Synthetic templates are a controlled pilot, not natural conversational data.
- Same-model writer and judge can share correlated errors.
- Character budgets are approximate and do not guarantee token-matched conditions.
- LLM judge outputs require manual adjudication.
- This pilot cannot establish generalization, causality in real-world agents, or paper-level novelty.
