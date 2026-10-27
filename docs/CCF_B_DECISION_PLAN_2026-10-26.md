# CCF-B 决策计划 — 先做决定性实验，再定投稿路线

制定日期：2026-10-26。本文件是当前阶段的**主计划**，优先于
`docs/PUBLICATION_ROADMAP.md` 的阶段推进；`docs/STATUS.md` 仍是每日续接点，
`docs/reviews/2026-10-26-direction-kill-argument.md` 是被本计划回应的对抗复审。

## 0. 策略总则

不立即放弃 CCF-B，也不提前认定现有结果足以支撑 CCF-B。用**可证伪的实验结果**
决定最终路线：

1. 先冻结协议；
2. 重新分析并补齐人工测量；
3. 用决定性实验检验"失败阶段分布是否只是当前系统设计的直接产物"；
4. 只有架构混杂实质性缓解、人工测量达标后，才做重新预注册的干预；
5. 再扩第二基准；
6. 每个阶段结束执行明确的**通过 / 失败 / 收窄主张**决策。

现阶段优先级：**协议冻结、架构消融设计、标注者协调**。不急于润色论文。

## 1. 阶段 F — 协议冻结（立即执行）

冻结对象：代码、数据、评估协议、模型配置、标注协议。冻结后任何变更都记入
`docs/PRE_REGISTRATION_CHANGELOG.md`（新建），并注明变更原因与影响的分析。

| 项目 | 冻结值 |
|---|---|
| 代码 | commit `b8b1f6e`（branch `fix/formation-diagnostics-evidence-based`，已 push） |
| 回答/judge/gate 模型 | `deepseek-v4.1-flash`（opencode zen gateway） |
| 检索 embedding（已报告跑批） | 进程内 `hash:384` 回退 |
| 诊断用 embedding 检查 | `bge-m3:latest`（本地 Ollama，1024 维） |
| LoCoMo 原始数据 | `locomo_refined_dataset/raw/locomo_refined.json`，sha256_16 `42c737807ed2ee64` |
| LongMemEval full-haystack 试点 | `longmemeval_s_sample10.json`，sha256_16 `4e8e2b4cc9d5999d` |
| LongMemEval oracle（仅诊断） | `longmemeval_oracle.json`，sha256_16 `5a6a52e1a98f85eb` |
| EvolutionProbe v2 | `datasets/evolution_probe/probe_v2.jsonl`，sha256_16 `8436254b1413538c` |
| BEAM 100K（候选第二基准） | `100K-00000-of-00001.parquet`，sha256_16 `c0519be25907005b` |
| 评估协议 | `docs/PROTOCOL.md` + `evaluation/attribution.py`（F1–F6/E0/EVAL/RC） |
| 人工 gate 协议 | round-3 逐事实二元（`README_round3.md`），fact kappa 0.835 / row 0.889 |
| 冻结产物 | `docs/PROTOCOL_FREEZE.md`（由本表生成，含 git 状态与哈希） |

冻结期规则：不再用新协议跑 headline；所有新分析必须标注所用标签版本
（auto / abstention-corrected / human-gated）。

## 2. 阶段 A — LoCoMo n=100 重分析与测量补齐

目标：确认 headline 在更严格的测量下是否仍成立，并补齐人工阶段标注。

1. **重分析**（无 API）：
   - 主分析改为**排除 E0 样本**后的阶段分布检验（E0 是 gate 噪声最大的类别）；
   - 同时报告包含 E0 的版本作为敏感性分析；
   - 明确区分"失败标签"（90% 人工确认）与"E0 水平"（不引用）。
2. **人工阶段标注**（新标注轮，预注册）：
   - 对象：LoCoMo n=100 全部问题，含当前未覆盖的 52 题；
   - 至少 2 名标注者，独立、盲法；
   - 每人完成两件事：(a) 事实级证据审核（参考 round-3 逐事实表）；
     (b) 阶段归因（证据首次不可得发生在哪个阶段）；
   - 报告：Cohen's κ、混淆矩阵、uncertain 比例；**目标门槛 κ ≥ 0.70**；
   - 若 κ < 0.70：不放宽门槛，先修标注协议（任务形态而非措辞），再重标。
3. **阶段决策门 A**：
   - 通过：排除 E0 后三对阶段分布仍显著，且阶段标注 κ ≥ 0.70；
   - 失败：结论依赖 E0 或标注不可靠 → 收窄为"仅报告 failure-label 分布，
     不报 E0 水平"，并进入分析型论文路线。

## 3. 阶段 B — 决定性实验：架构混杂

要回答的问题：失败阶段分布是不是当前系统设计的直接产物？

两条路径，优先做成本低、判别力强的：

- **B1 架构消融（首选）**：在可控引擎上改变存储/检索瓶颈，而不是调参。
  例：semantic 引擎在"原子事实抽取"与"原始 turn 存储"之间切换；
  summary 在"会话摘要"与"原始 turn"之间切换；retrieval 在
  "top-k 余弦"与"混合检索/更大候选池"之间切换。
  预注册：每个消融条件下重算 F1–F6 分布；用 Stuart–Maxwell/置换检验比较
  架构条件；预测"阶段随瓶颈移动"。
- **B2 第三方系统（若 B1 不足）**：接入 Mem0 / A-MEM 类黑盒系统，跑同一
  n=100 问题、同一 gate/judge。本机未安装，需要联网安装与适配。

**阶段决策门 B（架构独立性）**：
- 通过：原指纹（semantic→formation、summary→context、verbatim→retrieval）
  在至少一个**实质性不同**的架构下不被复制，或阶段分布按预注册方向随架构
  旋钮移动；
- 失败：指纹在所有架构下都原样出现（说明是设计产物）或完全消失（说明是
  特定实现偶然）→ 停止宣称"普遍失败指纹"，转向分析型论文。

## 4. 阶段 C — 重新预注册的干预

只有阶段 A 与 B 通过后才执行。

1. 对象：**人工确认的检索失败样本**（F4），不使用自动标签单独定样本。
2. 三臂：`placebo`（重答不修复）、`targeted`（只修定向失败样本）、
   `non-targeted`（非定向修复，作用于全部）。
3. 事先完成**样本量与统计功效分析**：以重测地板（当前 9/35 ≈ 26%）为
   噪声基准，估算达到 CI 排除 0 所需的 n 与重复次数；写入预注册。
4. 成功标准（全部满足）：
   - 定向修复的准确率提升 95% CI **排除 0**；
   - 提升幅度**超过重测波动**（placebo 对照）；
   - 检索召回率确实提高（机制检验）。
5. 若要主张"阶段诊断比通用修复更有价值"：还必须得到
   **targeted 优于 non-targeted** 的证据；否则只能主张"修复有效"，
   不能主张"诊断有额外价值"。
6. 阶段决策门 C：任一条件不满足 → contribution 4 记 null，不写可用性主张。

## 5. 阶段 D — 第二基准（LongMemEval ≥50）

1. 把 LongMemEval full-haystack 从 n=10 扩到 **至少 50 题**；
   根据功效分析决定是否扩到 100。
2. 分别检验：
   - 失败阶段分布能否跨基准复现（同 B 的检验口径）；
   - 干预效用能否跨基准复现（若阶段 C 通过）。
3. 注意：当前 LongMemEval oracle 变体检索退化，不能用于检索主张；
   必须用 full-haystack（`longmemeval_s_sample10` 或其全量）。
4. 阶段决策门 D：不能复现 → 把论文范围收窄到 LoCoMo，并明确外部效度限制。

## 6. 记录与审计（贯穿全程）

每个实验保留：原始数据、配置、版本、标注记录、预注册变更记录。
每个阶段结束写一份 `results/decision_gate_<stage>.json`：
- 输入 artifact 路径与哈希；
- 预注册的通过/失败判据；
- 实际结果与判定；
- 若收窄主张，写明收窄后的措辞。
禁止事后改判据；改判据必须记入 `docs/PRE_REGISTRATION_CHANGELOG.md`。

## 7. 总决策树

| 观察 | 决策 |
|---|---|
| 架构独立性 + 人工测量 + 定向干预 + 跨基准复现**全部支持** | 继续冲 CCF-B（现象 + 可用性论文） |
| 阶段归因、Oracle ladder 等**测量贡献可靠**，但架构混杂或干预效用未获支持 | 停止宣称"普遍失败指纹"或"可操作诊断"；转 COLING / NLPCC 等分析型/资源型论文 |
| **核心测量与复现本身不可靠** | 停止当前论文叙事，重新评估研究问题 |

## 8. 当前阶段的执行清单（下一步）

- [ ] 生成 `docs/PROTOCOL_FREEZE.md`（本文件第 1 节的冻结表 + git 状态）。
- [ ] 建立 `docs/PRE_REGISTRATION_CHANGELOG.md`。
- [ ] 阶段 A：写"排除 E0"的重分析脚本并落盘（无 API）。
- [ ] 阶段 A：起草新一轮人工阶段标注包（问题、证据、阶段定义、盲法流程、
      κ 门槛、混淆矩阵模板），协调至少 2 名标注者。
- [ ] 阶段 B：完成架构消融设计文档（消融条件、预注册判据、预期方向、
      样本量/成本），先不跑。
- [ ] 每完成一项，更新 `docs/STATUS.md` 的 punch list 与对应 decision gate。

**明确不做**：在阶段 A/B 结果出来前润色论文、扩写 CCF-B 主张、或在自动
gate 上继续累积 E0 数字。
