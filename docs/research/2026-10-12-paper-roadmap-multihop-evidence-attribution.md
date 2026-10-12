# 论文路线升级：从生命周期归因到多跳 Evidence Composition Attribution

日期：2026-10-12

## 1. 研究定位升级

当前工作的核心贡献是：把 Agent Memory 的最终答错拆解到记忆生命周期中的最早失败位置，而不是只报告最终 Accuracy。

已有主线：

```text
Formation → Storage → Evolution → Retrieval/Rerank → Context → Reasoning
```

对应 E0/F1-F6：

- E0：Evidence Sufficiency / evidence 不足或无法支持问题
- F1：Formation failure
- F2：Storage failure
- F3：Evolution failure
- F4：Retrieval / Rerank failure
- F5：Context failure
- F6：Reasoning / Answer failure

P10 的启发不是简单加入一个“多跳检索模块”，而是发现当前生命周期划分在 Retrieval/Rerank 与 Context 之间仍隐藏了一层重要问题：**Evidence Composition**。

多跳问题的关键不是“检索到更多 memory”，而是：

> 让多个正确 memory 以正确的关系、路径和顺序共同到达最终 context。

因此论文路线升级为：

```text
Memory Lifecycle Failure Attribution
                +
Multi-hop Evidence Composition Attribution
```

目标是回答两个层次的问题：

1. Agent Memory 在生命周期的哪个阶段失败？
2. 对于需要多条记忆协同的多跳问题，失败到底发生在证据缺失、证据连接、路径恢复、bridge 保留、context 还是最终 reasoning？

---

## 2. 新的核心假设

### H1：Memory Recall 不等于 Evidence Recall

系统可能找到了若干相关 memory，但没有找全回答所需的 gold evidence。

### H2：Evidence Recall 不等于 Evidence Composition

即使 A、B、C 三条 memory 都被检索出来，也可能没有恢复：

```text
A → B → C
```

因此需要区分“找到证据”和“把证据正确连接起来”。

### H3：Evidence Composition 不等于 Context Preservation

系统可能已经建立完整证据链，但 rerank/context compression 仍然可能删除关键 bridge memory。

例如：

```text
A → B → C

Rerank 保留：A, C
Rerank 丢弃：B

Final Context = A + C
```

此时问题不是 Retrieval failure，也不是最终 Reasoning failure，而是 **Bridge Preservation Failure**。

### H4：Multi-hop failure rate 应随 hop complexity 分解

Single-hop、2-hop、3-hop 问题不应只比较最终 Accuracy，而应比较各类 failure distribution。

---

## 3. 推荐的新 failure taxonomy

保留已有 E0/F1-F6，不推倒重来；在 F4/F5 中间增加 Evidence Composition 层。

```text
E0 Evidence Sufficiency
        ↓
F1 Formation
        ↓
F2 Storage
        ↓
F3 Evolution
        ↓
F4 Retrieval / Rerank
        ↓
R1 Evidence Recall
        ↓
R2 Evidence Linking
        ↓
R3 Path Completeness
        ↓
R4 Bridge Preservation
        ↓
F5 Context
        ↓
F6 Reasoning / Answer
```

其中 R1-R4 是针对 multi-hop / evidence-chain 问题的诊断层，不要求每道 single-hop 问题都经过所有 R 层。

### R1 Evidence Recall Failure

Gold evidence 中至少一条关键 memory 未进入候选 evidence。

### R2 Evidence Linking Failure

所需 memory 都已出现，但系统未恢复它们之间的实体、时间、因果或事件关系。

### R3 Path Completeness Failure

已经发现局部关系，但完整的 A→B→C 路径缺失，尤其是 bridge/intermediate evidence 缺失。

### R4 Bridge Preservation Failure

完整 evidence chain 已经构建，但 rerank、top-k 截断、context compression 或邻域选择导致关键 bridge memory 没有进入最终 context。

---

## 4. 为什么这个升级比单纯增加 Multi-hop Retrieval 更有论文价值

传统 evaluation 通常是：

```text
Question → Memory System → Answer → Accuracy
```

这种 evaluation 无法回答：

- 是没有记住？
- 是没有检索到？
- 是检索到了但没有连接？
- 是路径不完整？
- 是 bridge 被 rerank/context 丢掉？
- 还是 evidence 已完整进入 context，但 LLM 仍然推理错误？

本研究应把 evaluation 改造成：

```text
Question
   ↓
Gold Evidence
   ↓
Gold Evidence Graph / Path
   ↓
Lifecycle Trace
   ↓
Evidence Composition Trace
   ↓
Final Context
   ↓
Answer
   ↓
Earliest Failure Attribution
```

核心贡献不是提出一个新的 Memory Engine，而是提出一个能够解释 **why memory reasoning fails** 的诊断框架。

---

## 5. 新 Research Questions

### RQ1：Where do Agent Memory failures occur across the memory lifecycle?

保留原始主问题，验证 F1-F6/E0 framework 的有效性。

### RQ2：How does failure distribution change with multi-hop complexity?

比较：

- Single-hop
- 2-hop
- 3-hop（如果数据集允许）

重点报告 R1-R4、F5、F6 的变化。

### RQ3：When a memory agent fails on a multi-hop question, is the cause missing evidence or failed evidence composition?

这是论文升级后的核心问题。

区分：

```text
Evidence Missing
vs.
Evidence Found but Not Composed
vs.
Composed but Not Preserved
vs.
Composed and Preserved but Reasoning Wrong
```

### RQ4：Can lifecycle attribution guide targeted system improvement?

用 attribution → intervention → re-evaluation 验证诊断框架是否具有实际价值。

---

## 6. 实验路线

### Phase A：冻结现有 attribution evaluator

在增加新实验前固定：

- E0 evidence sufficiency protocol
- strict provenance
- temporal scorer
- F1-F6 definitions
- human ground-truth protocol
- first-loss attribution boundary

已有 25-case human GT：

- final label exact agreement：21/25 = 84%
- Cohen's κ ≈ 0.774

这部分作为 evaluator validation evidence，不再频繁修改规则后重复解释结果。

---

### Phase B：建立 Multi-hop Gold Evidence Schema

对 benchmark question 增加研究字段：

```text
question_id
hop_count
hop_type
reference_answer
gold_evidence
entities
relations
ordered_path
bridge_evidence
```

其中：

```text
ordered_path = [A, B, C]
```

表示回答所需 evidence path。

关系可以包括：

- entity relation
- temporal relation
- causal relation
- event transition
- speaker/action relation

不要把“hop count”仅定义成图 BFS 深度；应以回答所需 evidence chain 为准。

---

### Phase C：Multi-hop Attribution Baseline

先不要修改 Memory Engine。

直接在当前真实系统上建立：

```text
Question
 → Real Memory
 → Retrieval
 → Rerank
 → Evidence Linking
 → Path Check
 → Context
 → Answer
```

记录每一层是否保留 gold evidence。

输出：

- evidence recall
- linking recall
- path completeness
- bridge preservation
- context recall
- answer accuracy
- earliest failure

这样可以先回答“问题到底发生在哪里”，而不是先回答“如何把系统变强”。

---

### Phase D：P10-inspired Ablation

将 `agent_memory` P10 当作 motivating case study，而不是把 P10 本身作为论文贡献。

建议逐层增加机制：

```text
B0：普通 retrieval baseline
 ↓
B1：+ evidence linking
 ↓
B2：+ evidence chain / path completion
 ↓
B3：+ bridge-aware preservation
 ↓
B4：+ neighboring-turn / result-window expansion
 ↓
B5：+ temporal/state/session synthesis
```

重点观察：

```text
Accuracy
Multi-hop Accuracy
Evidence Recall
Path Completeness
Bridge Preservation
Context Recall
Failure Distribution
```

重要：每一步只增加一个机制，避免无法归因的“大改版”。

---

## 7. P10 的正确定位

P10 不应被表述为“第一次实现 multi-hop”。当前仓库分析显示，多跳相关基础已经分布在此前分支：

- P2：bounded graph traversal / BFS
- P3：multi-hop evidence anchors
- P4：evidence-chain construction
- P10：在既有能力上强化 evidence/context preservation、neighbor-window、state/temporal/session synthesis 等能力

因此论文应该借 P10 说明一个更重要的问题：

> Multi-hop capability is a lifecycle property of evidence composition, not merely a retrieval feature.

即：

```text
Multi-hop
≠ retrieve more memories

Multi-hop
= retrieve + link + complete path + preserve bridge + compose context + reason
```

---

## 8. 最重要的 Case Study 设计

至少构造一个完整失败案例：

```text
Question
  ↓
Gold: A → B → C
  ↓
Retrieval: A, B, C ✓
  ↓
Evidence Graph: A → B → C ✓
  ↓
Rerank: A, C ✓ / B ✗
  ↓
Final Context: A, C
  ↓
Wrong Answer
```

归因结果应为：

```text
R4 Bridge Preservation Failure
```

而不是：

```text
F6 Reasoning Failure
```

该案例用于直观证明：只看最终 answer accuracy 无法定位 memory reasoning failure。

---

## 9. Evaluation 指标升级

除了最终 Accuracy，建议至少报告：

### Lifecycle metrics

- Formation recall
- Storage recall
- Evolution recall
- Retrieval recall
- Rerank recall
- Context recall

### Evidence composition metrics

- Evidence Recall
- Evidence Linking Rate
- Path Completeness
- Bridge Preservation Rate
- Final Context Evidence Recall

### Answer metrics

- Accuracy
- Exact Match
- Token F1

### Attribution metrics

- Human agreement
- Cohen's κ
- Per-class precision / recall / F1
- Earliest-failure accuracy

---

## 10. 论文实验矩阵

最终建议形成下面的核心表格：

| System / Ablation | Single-hop Acc | 2-hop Acc | 3-hop Acc | Evidence Recall | Path Completeness | Bridge Preservation | Context Recall | F6 Reasoning |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | | | | | | | | |
| + Linking | | | | | | | | |
| + Chain | | | | | | | | |
| + Bridge | | | | | | | | |
| + Window | | | | | | | | |
| + State/Temporal | | | | | | | | |

这里所有数字必须来自实际实验，不允许用示意数字替代。

---

## 11. 统计与可靠性要求

当前 n=50 结果主要用于 pipeline validation 和 failure pattern exploration，不应作为最终强结论。

最终实验建议：

- 每个 benchmark 至少 n≥100
- bootstrap confidence intervals
- single-hop / multi-hop 分层统计
- 预先冻结 evaluator
- human annotation 20–30 作为独立验证集
- 报告 per-class confusion matrix
- 对关键 attribution 类别报告 precision / recall / F1

尤其注意：R1-R4 新类别的人工标注必须独立于自动 attribution，避免 circular evaluation。

---

## 12. 防止论文出现的主要风险

### 风险 1：把 P10 的功能直接当创新

避免：论文贡献是 attribution framework，不是“复刻 P10”。

### 风险 2：把 BFS depth 当 multi-hop 真值

避免：hop 应由 gold evidence chain / question dependency 定义。

### 风险 3：把 evidence found 当 reasoning solved

避免：必须检查 evidence relation、path 和 final context。

### 风险 4：把所有最终错误都归到 F6

避免：F6 必须满足 E0 sufficient + gold evidence reaches final context + answer scorer confirms incorrect。

### 风险 5：样本太小

避免：n=50 只用于探索，最终结论基于扩大后的 benchmark。

### 风险 6：新 taxonomy 太复杂

避免：R1-R4 只针对 multi-hop/evidence-chain questions；single-hop 继续使用原 F1-F6。

---

## 13. 最终论文故事

论文不应该讲成：

> 我实现了一个 Memory Failure Analyzer。

而应该讲成：

> Existing agent-memory benchmarks report whether an agent answers correctly, but provide limited information about where and why memory-based reasoning fails. We introduce a lifecycle-based failure attribution framework that traces errors from memory formation to final reasoning. We further show that multi-hop questions expose an overlooked intermediate failure layer: evidence composition. Even when individual memories are successfully retrieved, the system may fail to link evidence, complete the required path, preserve bridge evidence, or deliver the chain to the final context. We formalize these failure modes and use controlled ablations to quantify their contribution to memory reasoning failures.

中文核心叙事：

> **记忆系统的失败不只是“有没有记住”，多跳推理的关键也不只是“有没有检索到”。真正决定最终回答的是：正确证据能否被找到、连接、组成完整路径、保留关键桥接信息，并共同到达最终上下文。**

---

## 14. 后续执行顺序

按以下顺序推进，不提前堆复杂模型：

1. **冻结当前 E0/F1-F6 evaluator。**
2. **定义 R1-R4 operational criteria。**
3. **从现有 benchmark 中构建 single-hop / 2-hop / 3-hop 样本。**
4. **建立 Gold Evidence + Gold Evidence Path。**
5. **实现 evidence-chain tracing，但先不修改 Memory Engine。**
6. **跑 baseline，得到 multi-hop failure distribution。**
7. **做 linking / chain / bridge / context-window ablation。**
8. **至少 n≥100 后进行 bootstrap CI。**
9. **对 R1-R4 做独立 human annotation。**
10. **整理 case studies。**
11. **最后再决定是否需要修改 Memory Engine。**

---

## 15. 研究主线的一句话版本

> **从“Agent Memory 为什么答错”升级到“Agent Memory 的多跳推理到底在哪一层证据链断裂”。**

这条路线应成为后续实验、论文结构和 GitHub research log 的统一主线。
