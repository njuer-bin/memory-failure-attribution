# Protocol Freeze — 2026-10-26

This freeze is the reference point for the CCF-B decision plan
(`docs/CCF_B_DECISION_PLAN_2026-10-26.md`). Any change to the items below must
be recorded in `docs/PRE_REGISTRATION_CHANGELOG.md` before new headline runs.

## Code and environment

| item | frozen value |
|---|---|
| git commit | `b8b1f6e` (branch `fix/formation-diagnostics-evidence-based`, pushed to origin) |
| worktree at freeze | clean |
| Python | `G:\aconda\python.exe` (3.13.x) |
| answer model | `deepseek-v4.1-flash` |
| judge model | `deepseek-v4.1-flash` (temperature 0) |
| gate model | `deepseek-v4.1-flash` (temperature 0) |
| answer/judge gateway | `https://opencode.ai/zen/go`, `ANSWER_API_STYLE=anthropic` |
| reported-run embedding | in-process deterministic `hash:384` fallback |
| diagnostic embedding | `bge-m3:latest` (local Ollama, 1024-dim) — used only for the confound check, never mixed into headline tables |

## Datasets

| dataset | path | sha256_16 |
|---|---|---|
| LoCoMo refined (raw) | `locomo_refined_dataset/raw/locomo_refined.json` | `42c737807ed2ee64` |
| LongMemEval full-haystack pilot | `longmemeval_s_sample10.json` | `4e8e2b4cc9d5999d` |
| LongMemEval oracle (diagnostic only) | `longmemeval_oracle.json` | `5a6a52e1a98f85eb` |
| EvolutionProbe v2 | `datasets/evolution_probe/probe_v2.jsonl` | `8436254b1413538c` |
| BEAM 100K (candidate second benchmark) | `100K-00000-of-00001.parquet` | `c0519be25907005b` |

Note: `locomo_refined_public` is a directory source; the runner records a benign
PermissionError instead of a file digest. The raw-file digest above is the
authoritative freeze for LoCoMo.

## Evaluation and annotation protocols

| protocol | frozen reference |
|---|---|
| failure attribution | `evaluation/attribution.py` + `docs/PROTOCOL.md` (F1–F6, E0, EVAL, RC) |
| first-loss definition | "first observable evidence-loss boundary"; never "causal root cause" |
| abstention correction | `experiments/abstention_correct.py`; naive rule 52% precision, guarded rule 13/13 and 12/12 on the human sample |
| human gate (round 3) | per-fact binary, `results/annotation_package/README_round3.md`; fact kappa 0.835, row kappa 0.889 |
| gate in headline runs | automatic gate; E0 counts are relative patterns only, never levels |
| canonical accuracy | semantic accuracy on judged rows; `attributed_accuracy` reported separately |

## Headline artifacts frozen for re-analysis

- LoCoMo n=100: `results/systems_locomo_n200_fixedgate/` ( `summary.json`
  records `limit: 100`), analysis `results/analysis_ladder_locomo_n100_fixedgate.json`.
- Oracle ladder n=200: `results/analysis_ladder_{locomo,longmemeval}_n200_{auto,corrected}.json`.
- Intervention null: `results/retrieval_intervention_locomo_n100/summary.json`.
- Adversarial review: `docs/reviews/2026-10-26-direction-kill-argument.{md,json}`.

## Freeze rules

1. No new headline run on a different model, embedding backend, gate, or judge
   without a changelog entry and an explicit "not comparable" label.
2. Exploratory diagnostics (e.g. bge-m3 retrieval ranking) may run outside the
   freeze but must be labelled diagnostic and must not enter headline tables.
3. Re-analysis of stored rows is allowed and is not a protocol change, provided
   the label version used (auto / abstention-corrected / human-gated) is stated.
4. Every decision-gate report cites artifact paths and hashes and the
   pre-registered criterion it was judged against.
