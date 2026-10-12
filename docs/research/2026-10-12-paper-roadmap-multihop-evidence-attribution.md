# 论文路线：先完成 CCF-C，再以实验结果升级 CCF-B

日期：2026-10-12

## 0. 总策略

本研究采用 **C-first, B-upgrade** 路线：

> **第一阶段先把论文做成一篇完整、严谨、可复现的 CCF-C 级工作；第二阶段不预设一定冲 CCF-B，而是根据实验结果决定是否升级。**

这样做的原则是：

- CCF-C 是当前必须完成的目标；
- CCF-B 是实验结果足够强时的升级目标；
- 后续 B 实验不能推翻 C 的主线，而应作为 C 的自然增强；
- 现在所有工程和实验设计都应保留升级 B 的接口，但不为了“看起来像 B”而提前堆复杂模块。

---

## 1. 研究定位

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

P10 的启发不是简单加入一个“多跳检索模块”，而是发现 Retrieval/Rerank 与 Context 之间仍隐藏一层重要问题：**Evidence Composition**。

多跳问题的关键不是“检索到更多 memory”，而是：

> **让多个正确 memory 以正确的关系、路径和顺序共同到达最终 context。**

因此论文升级为：

```text
Memory Lifecycle Failure Attribution
                +
Multi-hop Evidence Composition Attribution
```

---

## 2. CCF-C 阶段必须回答的问题

### RQ1：Where do Agent Memory failures occur across the memory lifecycle?

验证 E0/F1-F6 framework 能否稳定定位 Agent Memory 的最早失败位置。

### RQ2：When memory agents fail, is the cause upstream memory failure, retrieval/context failure, or reasoning failure?

通过 Real Memory、Oracle Memory、Oracle Context 和严格 provenance 区分不同阶段。

### RQ3：Multi-hop failures 是否存在独立于普通 retrieval failure 的 Evidence Composition 问题？

初步定义：

```text
Evidence Missing
vs.
Evidence Found but Not Composed
vs.
Composed but Not Preserved
vs.
Composed and Preserved but Reasoning Wrong
```

CCF-C 阶段的目标不是证明 R1-R4 已经是一个“全新的理论”，而是建立可靠、可验证的诊断层，并用实验确认它是否值得进一步升级。

---

## 3. Failure Taxonomy

保留已有 E0/F1-F6，不推倒重来；针对 multi-hop / evidence-chain questions 增加 R1-R4。

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

### R1 Evidence Recall Failure

Gold evidence 中至少一条关键 memory 未进入候选 evidence。

### R2 Evidence Linking Failure

所需 memory 都已出现，但系统未恢复它们之间的实体、时间、因果或事件关系。

### R3 Path Completeness Failure

局部关系已发现，但完整 A→B→C 路径缺失，尤其是 bridge/intermediate evidence 缺失。

### R4 Bridge Preservation Failure

完整 evidence chain 已构建，但 rerank、top-k 截断、context compression 或邻域选择导致关键 bridge memory 没有进入最终 context。

Single-hop 问题继续使用 E0/F1-F6；R1-R4 主要用于 multi-hop/evidence-chain questions，避免 taxonomy 过度复杂化。

---

## 4. 为什么这条主线有价值

传统 evaluation 通常是：

```text
Question → Memory System → Answer → Accuracy
```

但 Accuracy 无法回答：

- 是没有形成记忆？
- 是没有检索到？
- 是检索到了但没有连接？
- 是路径不完整？
- 是 bridge 被 rerank/context 丢掉？
- 还是 evidence 已完整进入 context，但 LLM 仍然推理错误？

本研究改成：

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

核心贡献是 **why memory reasoning fails 的诊断框架**，而不是提出一个新的 Memory Engine。

---

## 5. CCF-C 主实验路线

### Phase A：冻结 evaluator

在继续增加实验前冻结：

- E0 evidence sufficiency protocol
- strict provenance
- temporal scorer
- F1-F6 definitions
- human ground-truth protocol
- first-loss attribution boundary

已有 25-case Human Ground Truth：

- final label exact agreement：21/25 = 84%
- Cohen's κ ≈ 0.774

这部分作为 evaluator validation evidence，不再因为新实验频繁修改规则。

### Phase B：建立 Multi-hop Gold Evidence Schema

至少保存：

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

表示回答所需 evidence path。hop count 应由回答所需 evidence chain 定义，而不是简单等同于 BFS depth。

### Phase C：Multi-hop Attribution Baseline

**先不修改 Memory Engine。**

直接在当前真实系统上记录：

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

输出：

- Evidence Recall
- Evidence Linking Rate
- Path Completeness
- Bridge Preservation
- Context Recall
- Answer Accuracy
- Earliest Failure

### Phase D：跨数据集验证

目标数据集：

- LoCoMo
- LongMemEval

最终规模目标：每个 benchmark 至少 n≥100；当前 n=50 仅用于 pipeline validation 与 failure-pattern exploration。

统计要求：

- bootstrap confidence intervals
- single-hop / multi-hop 分层统计
- per-class confusion matrix
- attribution precision / recall / F1

### Phase E：Human Validation

继续使用独立人工标注验证自动 attribution；R1-R4 的人工标注必须独立于自动 attribution，避免 circular evaluation。

---

## 6. P10-inspired Ablation：作为 C 的增强实验，同时为 B 留接口

将 `agent_memory` P10 定位为 motivating case study，而不是论文贡献本身。

已知基础：

- P2：bounded graph traversal / BFS
- P3：multi-hop evidence anchors
- P4：evidence-chain construction
- P10：进一步强化 evidence/context preservation、neighbor-window、state/temporal/session synthesis

因此不把 P10 表述为“第一次实现 multi-hop”。

建议 controlled ablation：

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

每次只增加一个机制，记录：

- Accuracy
- Multi-hop Accuracy
- Evidence Recall
- Path Completeness
- Bridge Preservation
- Context Recall
- Failure Distribution

这组实验首先服务 CCF-C 的“诊断是否具有实际价值”，同时为后续 B 升级保留完整实验接口。

---

## 7. CCF-C 完成标准（必须先达成）

在考虑 B 之前，至少完成：

1. E0/F1-F6 evaluator 冻结；
2. provenance、temporal scorer、Human GT protocol 稳定；
3. R1-R4 定义和标注规则冻结；
4. LoCoMo ≥100；
5. LongMemEval ≥100；
6. 至少 20–30 个独立 Human Validation cases；
7. bootstrap CIs；
8. baseline multi-hop attribution；
9. 至少一个完整 R1/R2/R3/R4 failure case study；
10. 至少一组 controlled ablation；
11. 完整 confusion matrix 和 per-class metrics；
12. 论文能够形成“问题 → 方法 → 验证 → 发现 → 限制”的闭环。

达到这里，就以 CCF-C 投稿为第一目标，不等待 B 实验全部完成。

---

## 8. CCF-B 升级不是预设目标，而是结果驱动

CCF-C 完成后，根据实验结果设置 **B-upgrade gate**。

只有满足大部分条件才值得冲 B：

### B-Gate 1：R1-R4 必须是高频或结构性失败

如果绝大多数错误仍然来自 F1/F4/F5，而 R1-R4 很少出现，则不应强行把 Evidence Composition 包装成核心创新。

### B-Gate 2：失败率应随 hop complexity 呈现可解释变化

比较：

```text
Single-hop
2-hop
3-hop（数据允许时）
```

如果 hop 增加伴随 R1-R4 明显增加，说明 multi-hop evidence composition 是真实的系统性瓶颈。

### B-Gate 3：R1-R4 必须具有可区分性

需要能够稳定区分：

```text
R1：evidence missing
R2：evidence found but disconnected
R3：path incomplete
R4：bridge dropped
F6：evidence complete but reasoning wrong
```

### B-Gate 4：人工验证支持 taxonomy

R1-R4 的自动 attribution 必须获得可靠的人类一致性，而不是只依赖自动规则。

### B-Gate 5：跨数据集成立

至少在 LoCoMo + LongMemEval 中出现一致或具有解释力的趋势。

### B-Gate 6：Intervention 有效

最重要的升级证据是：

```text
Attribution
   ↓
Targeted Intervention
   ↓
Re-evaluation
```

例如系统被诊断为 R4 后，只增加 bridge-aware preservation；如果 R4 类错误显著下降，同时其他类别没有异常恶化，就证明 attribution 不只是“解释”，而具有诊断指导能力。

### B-Gate 7：形成新的科学结论

理想结果不是：

> “我们的模块让 Accuracy 提高了 X%。”

而是：

> **多跳 Agent Memory 的主要瓶颈不仅是 memory retrieval；证据之间的连接、路径完整性和 bridge preservation 构成了一个可独立测量、可归因、可干预的中间失败层。**

只有实验真正支持这一结论，才升级为 CCF-B 版本。

---

## 9. 最关键 Case Study

至少准备一个完整失败案例：

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

此时应归因：

```text
R4 Bridge Preservation Failure
```

而不是：

```text
F6 Reasoning Failure
```

该案例用于证明只看最终 Accuracy 无法定位 memory reasoning failure。

---

## 10. 论文最终结构

### CCF-C 版本

```text
1. Introduction
2. Related Work
3. Problem Definition
4. Lifecycle Failure Attribution Framework
5. Evidence Composition Attribution for Multi-hop Memory
6. Experimental Setup
7. Lifecycle Failure Analysis
8. Multi-hop Evidence Composition Analysis
9. Human Validation and Case Studies
10. Controlled Ablation / Intervention
11. Limitations
12. Conclusion
```

核心故事：

> Existing agent-memory benchmarks report whether an agent answers correctly, but provide limited information about where and why memory-based reasoning fails. We introduce a lifecycle-based failure attribution framework that traces errors from memory formation to final reasoning. We further investigate multi-hop questions and identify an intermediate evidence-composition layer where retrieved memories may fail to be linked, complete the required path, preserve bridge evidence, or reach final context.

### CCF-B 升级版本

**不需要重写整个研究。**

在 CCF-C 基础上重点增强：

- 更大规模实验
- hop-complexity 分层
- R1-R4 独立性证据
- 更强 ablation
- targeted intervention
- 跨 benchmark 一致性
- 更完整 case studies
- 更强 statistical analysis

如果这些结果不足以支撑更强结论，就保留 CCF-C 版本。

---

## 11. 当前执行顺序

严格按以下顺序，不提前堆复杂模型：

```text
1. Freeze E0/F1-F6 evaluator
        ↓
2. Freeze Human GT / provenance / temporal protocol
        ↓
3. Define and freeze R1-R4
        ↓
4. Build Multi-hop Gold Evidence Schema
        ↓
5. Run baseline attribution
        ↓
6. Expand LoCoMo / LongMemEval to ≥100 each
        ↓
7. Human validation
        ↓
8. Controlled P10-inspired ablation
        ↓
9. Complete CCF-C paper package
        ↓
10. CCF-C readiness decision
        ↓
11. Run B-upgrade experiments only if justified
        ↓
12. Decide CCF-C submission or CCF-B upgrade
```

---

## 12. 一句话研究主线

> **先建立一个可信的 Agent Memory 生命周期失败归因框架，再证明多跳问题中存在可独立诊断的 Evidence Composition 失败层；先完成 CCF-C 的完整闭环，再由实验结果决定是否升级 CCF-B。**
