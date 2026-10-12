# Multi-hop Gold Evidence Schema

日期：2026-10-12

## 目的

为 R1 Evidence Recall、R2 Evidence Linking、R3 Path Completeness、R4 Bridge Preservation 建立独立于最终答案评分的 Gold Evidence 表示。

## 核心原则

**evidence 数量 ≠ hop 数量。**

一道问题包含两个或多个 gold evidence，只说明答案可能需要多个证据；只有当这些证据之间存在回答所需的关系、顺序或中间路径时，才标记为 multi-hop。

因此当前自动 loader **禁止猜测**：

- hop_count
- hop_type
- ordered_path
- relations
- bridge_evidence

loader 只复制 benchmark 已有的 question、reference answer 和 evidence provenance，并将 annotation_status 设置为 `unreviewed`。

## Schema

```text
question_id
question
reference_answer

gold_evidence[]
  evidence_id
  text
  session_index
  message_index

hop_count
hop_type
ordered_path[]
relations[]
  source
  target
  relation
  order
bridge_evidence[]
annotation_status
notes
```

## 字段语义

### hop_count
回答所需 evidence chain 的 hop 数，而不是 evidence item 数量，也不简单等同于 BFS depth。

### hop_type
当前允许：

- `single`
- `multi_hop`
- `temporal`
- `causal`
- `entity`
- `unknown`

`unknown` 用于尚未完成人工判断的样本。

### ordered_path
回答所需的证据路径，例如：

```text
[A, B, C]
```

表示需要按 A → B → C 的证据链理解问题。

### relations
显式记录相邻 evidence 之间的关系，例如：

```text
A --causes--> B
B --changes--> C
```

关系必须来自人工确认或可靠的 benchmark 结构，不能仅凭 evidence 共现自动推断。

### bridge_evidence
路径中承担连接作用的中间证据。它是 R4 Bridge Preservation 的核心 Gold 标注。

例如：

```text
A → B → C
```

若 B 是从 A 推到 C 所必需的中间证据，则：

```text
bridge_evidence = [B]
```

## R1-R4 与 Schema 的对应关系

```text
Gold Evidence
      ↓
R1 Evidence Recall
      ↓
Evidence Linking / relations
      ↓
R2 Evidence Linking
      ↓
ordered_path / bridge_evidence
      ↓
R3 Path Completeness
      ↓
Rerank / context selection
      ↓
R4 Bridge Preservation
```

## 当前阶段

第一版只建立 schema 和 validation，不修改 Memory Engine。

下一步：

1. 从 LoCoMo 生成 `unreviewed` candidate records；
2. 识别 single-hop / multi-hop 候选；
3. 人工确认 hop_count、path、relations、bridge；
4. 冻结 Gold subset；
5. 在真实 Memory pipeline 上运行 R1-R4 baseline attribution。

## 研究纪律

如果无法从 benchmark evidence 或人工复核可靠判断路径关系，则保持 `unknown/unreviewed`，不为了扩大 multi-hop 样本而强行标注。

这样可以避免 circular evaluation 和 taxonomy inflation。
