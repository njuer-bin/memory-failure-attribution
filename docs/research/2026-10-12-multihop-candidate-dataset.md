# Step 3：LoCoMo Multi-hop Candidate Dataset

## 目标

在 Step 2 的 `MultiHopGoldEvidence` schema 之后，生成一个**候选集**，用于后续人工冻结 multi-hop Gold subset。

本阶段不做最终的 multi-hop 判定，不推断 hop_count、ordered_path、relations 或 bridge_evidence。

## 为什么必须先做 Candidate，而不是直接标注

现有 LoCoMo-Refined 归一化记录已经包含 `gold_evidence`。但：

> evidence count ≠ hop count。

一条问题拥有两个或更多支持证据，只能说明它值得进入候选池，不能证明这些证据构成 A→B→C 的多跳路径。

因此候选生成器只记录弱信号：

- 多个 Gold Evidence
- 跨 session evidence
- 跨 turn evidence
- 时间问题语言
- 因果问题语言
- 关系问题语言
- benchmark task type 中的 `multi_hop`

这些信号用于提高候选召回率，不作为最终标签。

## 实现

新增：

- `experiments/generate_multihop_candidates.py`
- `tests/test_multihop_candidates.py`

运行：

```bash
G:\\aconda\\python.exe -u -m experiments.generate_multihop_candidates --dataset locomo_refined_public --limit 100
```

默认输出：

```text
results/multihop_candidates/locomo_refined_public_candidates.jsonl
```

每条候选记录保留：

- 原问题与 reference answer
- 原始 Gold Evidence
- candidate_features
- query_signals
- task_type
- candidate_reasons
- 空的 review 字段

其中 review 明确保持：

```json
{
  "status": "unreviewed",
  "hop_count": null,
  "hop_type": "unknown",
  "ordered_path": [],
  "relations": [],
  "bridge_evidence": []
}
```

## 研究纪律

候选生成器不能把启发式信号直接变成研究结论。例如：

- `gold_evidence_count >= 2` ≠ multi-hop
- `cross_session_evidence = true` ≠ multi-hop
- `task_type = multi_hop` 也暂不替代人工 Gold 冻结
- temporal / causal / relational question signal 只能帮助召回候选

## 下一步

1. 在本地 LoCoMo-Refined public 数据上运行候选生成器。
2. 统计候选数量、按 signal 分布和 evidence 数量分布。
3. 抽取候选进入人工 review 表。
4. 人工确定 `hop_count / hop_type / ordered_path / relations / bridge_evidence`。
5. 只将 `annotation_status=reviewed` 且结构通过 validation 的样本冻结为 Multi-hop Gold subset。
6. 再运行 R1–R4 baseline attribution。

在 Gold subset 冻结前，不修改 MemoryEngine，不做针对 multi-hop 的系统优化，以避免把方法改进和诊断基线混在一起。
