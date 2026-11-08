# 初始科研审计报告（Claude Research Director）

> **审计日期：** 2026-11-08
> **审计对象：** `njuer-bin/memory-failure-attribution`，分支 `research/memory-filtering-protocol`
> **审计基线 commit：** `0d232ce8858b5ffdc70ad999fdd9fe2a0600b6e7`
> **审计性质：** 只读审计 + 低风险可逆验证；未启动任何模型实验，未修改研究假设，未推送。
> **证据标签：** VERIFIED = 本次直接核实；SUPPORTED = 有文档/一手来源支持；TENTATIVE = 暂时判断；UNKNOWN = 无法确认。

---

## 0. 结论摘要

**结论：有条件继续（NARROW），但当前不能进入确认性实验。**

- 当前候选问题**尚未被单一论文实质性完成**，但剩余空白很窄，且三个最接近的工作（REALM 2026、SPARE-RAG、TSHMem/TiMem）已覆盖其大部分外围。（SUPPORTED）
- 当前 RQ 作为书面表述**不可证伪**：没有方向、阈值或失效判据；protocol 中的 H1 也只是"may still differ"。（VERIFIED）
- 核心构造（Direct/Bridge）在 LoCoMo category-1 上的**可操作性存疑**：5 个 dry-run 题中只有 1 题存在可辩护的 Bridge 候选，其余 4 题是跨 session 聚合/多槽位列举。（VERIFIED，基于对原始对话的直接阅读）
- 统计上，LoCoMo 只有 **10 个独立对话簇**，30–50 题的 pilot 无法估计 role × necessity 交互；混合效应模型在 10 组下不稳定。（SUPPORTED）
- 代码层面**不存在**任何删除/干预实现、schema 校验或一致性统计；`requirements.txt` 不含 `jsonschema`/`pytest`。（VERIFIED）
- 文献/artifact 层面：REALM 正文与摘要已核实，OpenReview 附件**未获取**；SPARE-RAG 元数据与摘要已核实，MDPI 全文/代码**访问被拒**；其余 6 篇标题与摘要已核实。（VERIFIED / UNKNOWN）
- 用户指定的本地目录 `G:\PythonProject\memory-failure-attribution` **当前不在本分支**，且有 76 项未提交改动；本次审计在隔离克隆中完成，未触碰该工作区。（VERIFIED）

**一句话建议：先把"角色"从主假设降为探索性因素，先做 necessity/redundancy 的可识别对比，并用受控合成链验证构造；在 Bridge 正例数量与标注信度达标前，不要投入 LoCoMo 自然数据的大规模实验。**

---

## 1. 仓库状态核验

### 1.1 远程与隔离克隆（VERIFIED）

| 项目 | 状态 |
|---|---|
| 远程分支 | `origin/research/memory-filtering-protocol` = `0d232ce` |
| 隔离克隆 | `C:\Users\13742\tmp-memory-failure-attribution`，clean，HEAD = `0d232ce` |
| 本次新增提交 | 无（审计未提交、未推送） |
| 测试 | `pytest -q` → **22 passed in 0.87s** |
| `gh` CLI | **不可用**（command not found） |
| GitHub 凭证 | HTTPS 读可用；`git push --dry-run` 通过认证（Git Credential Manager），但本次未推送 |

### 1.2 用户本地工作目录存在冲突（VERIFIED，阻断写入）

`G:\PythonProject\memory-failure-attribution`：

- 当前分支是 `fix/formation-diagnostics-evidence-based`，**不是** `research/memory-filtering-protocol`。
- 工作区有 **76 项未提交/未跟踪改动**（含 `docs/paper/`、`experiments/mem0_system.py` 等）。
- 该工作区**不存在** `CLAUDE.md`、`docs/RESEARCH_CHARTER.md`、`docs/CURRENT_STATE.md`、`.claude/agents/`。
- 本地与远程该分支已分叉（HEAD 相对 research 分支 89/33）。

因此本次审计没有在 `G:` 工作区做任何写操作。若要让审计报告落到该目录，必须先由用户提交或 stash 现有工作，再切换/合并分支；这属于 L3 决策，需用户确认。

### 1.3 自动化研究基础设施（VERIFIED / UNKNOWN）

- `.claude/agents/` 四个角色、`.claude/commands/research-cycle.md`、`CLAUDE.md`、持久状态文件均存在且内容完整。
- `.github/workflows/claude-research-cycle.yml` YAML 合法；但**只存在于 research 分支，未在 `main` 上**，因此定时任务目前不会运行。`docs/AUTONOMOUS_RESEARCH_SETUP.md` 已说明需要先人工合并到默认分支。
- `ANTHROPIC_API_KEY` secret 是否已配置：**UNKNOWN**（本次无法验证 GitHub 仓库设置）。

### 1.4 数据与许可（VERIFIED / UNKNOWN）

- 官方 LoCoMo 固定版本 `snap-research/locomo@cbfbc1db...` 已成功获取到仓库外的临时目录：**10 conversations / 1,986 QA**，category 计数 `1:282, 2:321, 3:96, 4:841, 5:446`，与 `docs/PHASE0_LOCOMO_AUDIT.md` 完全一致。
- 仓库内**没有**官方 `locomo10.json`；仓库内是另一份 `locomo_refined_dataset`（1,382 QA；category 计数 213/299/68/802，无 category 5）。二者**不是**同一数据集，索引不兼容。
- LoCoMo 许可证：`main` 分支有 `LICENSE.txt`，内容为 **CC BY-NC 4.0**；但在固定 commit `cbfbc1d` 的树中**没有 LICENSE.txt**（该文件是之后添加的）。引用时应写"官方仓库 main 分支 LICENSE.txt 为 CC BY-NC 4.0（固定数据 commit 本身未含许可证文件）"。
- `locomo_refined_dataset` 的来源、版本、许可证：**UNKNOWN**。`datasets/manifest.json` 与 `datasets/README.md` 均未记录 source/license/revision。仓库已提交其 raw 文件（2.7MB）和 public 对话（4.1MB），这与 `docs/PHASE0_LOCOMO_AUDIT.md:41-48` 的"不提交原始对话"政策存在潜在冲突，发布前必须处理。

---

## 2. 当前研究进度

### 2.1 已完成（VERIFIED）

- 研究章程、协议 v0.1、决策日志 D-001～D-004、停止条件、实验注册表、结果账本。
- 相关工作总结矩阵（12 篇最接近工作）。
- LoCoMo 官方数据 schema/category/license 审计。
- 5 题 dry-run manifest（5 个不同对话）与数据完整性校验。
- 注解手册 v0.1、JSON Schema（draft 2020-12）、空白注解表。
- 注解 packet 生成器。

### 2.2 本次审计新增完成的验证（VERIFIED）

**B-005 已实际执行成功**（审计前的 `docs/CURRENT_STATE.md` 曾记录为未完成）：

```
python experiments/prepare_locomo_annotation_packet.py \
  --dataset <官方固定版本>/data/locomo10.json \
  --output <仓库外临时目录>/packet.jsonl
```

输出：`Wrote 5 records`；5 条记录的证据 turn 全部解析成功；生成物位于仓库外。官方数据通过 `git fetch --depth 1 origin cbfbc1db...` 获取，未提交。

### 2.3 仍未完成（VERIFIED）

- 两名人工作者独立标注：**0/5**。
- 一致性统计：无。
- 删除/干预代码、不变量测试：无（全仓库 grep 无命中）。
- schema 校验代码/测试：无。
- 任何模型实验、效应量、CI、p 值：无（`RESULT_LEDGER.md:7` 明确记录）。
- REALM OpenReview 附件：未获取。
- SPARE-RAG 全文/代码：未获取（MDPI 403）。
- MemConflict / STALE / WMT 的脚本级审计：未完成。
- 统计功效/样本量分析：未完成。

### 2.4 文档一致性问题（VERIFIED）

1. `docs/MEMORY_FILTERING_RESEARCH_PROTOCOL.md:307,510` 引用 `docs/ARTIFACT_AUDIT.md`，文件不存在。
2. 同文件 `:326,480` 引用 `schemas/evidence_graph.schema.json`，实际文件名为 `schemas/evidence_annotation.schema.json`。
3. `docs/ANNOTATION_GUIDELINES.md:171` 要求"formal annotation 前建立 machine-validated JSON Schema"，但仓库无校验器、无相关测试，`requirements.txt` 不含 `jsonschema`。
4. **关键缺口**：修订后的 RQ 包含 `temporal validity` 与 `query intent` 两个 moderator，但 `schemas/evidence_annotation.schema.json` 与 `docs/ANNOTATION_GUIDELINES.md` **都没有对应字段或标注步骤**。这两个 moderator 目前只存在于文字中。
5. `README.md:177-189` 仍停留在旧的 lifecycle 归因线（n=10、LoCoMo n=50 重跑），没有本分支的说明；旧的 "10/10 semantically"、"stable" 表述可能被误读为本分支证据。

---

## 3. 最接近的已有论文及其研究边界

> 本次用一手来源核实标题、作者、venue、摘要；方法细节仅在有正文/摘要支持时下结论。

| 工作 | 设置 | 干预/构造 | 与本研究重叠 | 精确区别 | 核实状态 |
|---|---|---|---|---|---|
| **REALM 2026**（Vinayaka, ACL Anthology 2026.realm-1.16） | 记忆条件 QA；合成 VALIDITYMEM-530 + MemoryAgentBench 复现 | 固定候选集，操纵 resolver 质量与 assembly policy；targeted false-drop / false-keep | query-time 过滤、query-critical 假删除、下游答案损害 | 不做 Direct/Bridge 角色；不做跨 session 对话依赖图；不做 role×necessity 匹配对比 | **VERIFIED**（ACL 页面 + PDF） |
| **SPARE-RAG**（Guo et al., Information 17(10):1052, 2026-10-21） | 固定候选 passage pool 的多跳 RAG | 证据修复 + 顺序删除提案 + 删除后验证（接受/拒绝） | 固定池、删除、链保持验证 | RAG passage，不是演化中的对话记忆；不研究角色×必要性因果代价 | **VERIFIED**（Crossref/OpenAlex 摘要）；全文/代码 **UNKNOWN** |
| **TSHMem**（EMNLP 2026） | 长程对话记忆 | 时序-语义异构图、时序意图解析、图检索 | 跨 session、时序意图、证据检索 | 检索/排序架构；无随机删除干预 | **VERIFIED**（ACL 页面摘要） |
| **TiMem**（ACL Findings 2026） | 长程对话记忆 | Temporal Memory Tree、复杂度感知召回 | 时序分层、合并、召回 | 无因果删除/角色对比 | **VERIFIED**（ACL 页面摘要） |
| **STALE / CUPMem**（arXiv:2605.06527） | 隐式冲突与状态失效 | 400 场景 / 1200 查询；State Resolution 等 | 记忆有效性、状态更新 | 不是删除单位证据的边际因果损害 | **VERIFIED**（arXiv 摘要） |
| **MemConflict**（arXiv:2605.20926） | 多 session 冲突 | 动态/静态/条件冲突；支持记忆检索诊断 | 跨 session、query-conditioned 有效性、证据级诊断 | 非随机反事实删除 | **VERIFIED**（arXiv 摘要） |
| **Weighted Memory Tree**（REALM 2026 / arXiv:2608.20631） | 长程 agent 执行记忆 | 分层任务记忆、动态保留分数、投毒实验 | 保留/抑制、长程记忆管理 | 执行轨迹，不是对话证据链；投毒≠假删除 | **VERIFIED**（ACL 页面 + arXiv 标题/摘要） |

**REALM 附件状态：** 论文正文写明补充材料位于 OpenReview submission 52，包含代码、生成数据、prompts、冻结输出、评分/审计报告。本次通过 OpenReview API 检索**未返回该 note**，直接附件**未能获取**。任何"已复现 REALM"或"REALM 不含 X"的强断言都必须标为 UNKNOWN，直到附件被实际检查。（VERIFIED for the blocker）

**SPARE-RAG 附件状态：** MDPI 全文返回 403；Crossref/OpenAlex 仅提供摘要。矩阵中关于"顺序删除、父子证据状态、rollback"的方法级描述，本次**未能独立复核**，应标为 TENTATIVE（摘要支持"评估每个删除提案对剩余证据集的影响"，但"rollback"细节未在摘要中出现）。

---

## 4. 新颖性审查

### 4.1 是否已被实质性研究？（问题 1）

**答案：核心问题没有被单篇论文完整覆盖，但外围已被覆盖，剩余空白窄且脆弱。**（SUPPORTED）

- 已经被覆盖：query-critical false-drop 的损害（REALM）；固定池内的链保持删除（SPARE-RAG）；跨 session 时序图检索（TSHMem）；时序分层合并（TiMem）；状态失效/冲突（STALE、MemConflict）；动态保留与投毒（WMT）。
- 未被明确覆盖：在**长程对话记忆**中，把 **证据功能角色（Direct/Bridge）** 与 **实际必要性** 分开标注，并在**匹配必要性、替代路径、依赖深度、图位置、token 数**后估计 role 的额外因果代价。
- 但"未被覆盖"不等于"值得发表"：如果 role 效应在控制结构变量后消失，或者 Bridge 在自然数据中近乎不存在，该空白就无法转化为实证贡献。

### 4.2 真正剩下的知识空白（问题 2）

**候选空白（TENTATIVE）：** 异质记忆删除代价的**条件结构**——不是"假删除有害"（已知），而是"同样必要的证据，因其在查询特定推导中的功能位置不同，删除代价是否系统地不同；以及该差异是否被时序有效性/查询意图调节"。

必须同时满足三个条件才成立：
1. 角色可从必要性中独立、可靠地标注；
2. 自然或半自然数据中存在足够的 Necessary-Bridge 正例；
3. 效应不能被图位置/度数/深度/token 位置/检索变化吸收。

**当前证据对条件 1-2 不利**（见 §6.1）。

### 4.3 必须避免的主张（VERIFIED）

- 不得主张"首次发现 query-critical false-drop 有害"（REALM）。
- 不得主张"首次提出依赖感知的链保持删除"（SPARE-RAG）。
- 不得主张"首次做时序图检索/时序分层记忆"（TSHMem/TiMem）。
- 不得主张"首次研究记忆冲突/失效"（STALE/MemConflict）。
- 在 REALM 附件与 SPARE-RAG 全文未审计前，不得写"REALM 没有 X"或"SPARE-RAG 没有 Y"的否定性新颖性断言。

---

## 5. 研究假设审查

### 5.1 可证伪性（问题 3）

**当前 RQ 不可证伪**（VERIFIED）："how does ... vary with ... and how are these moderated by ..." 没有方向、没有最小有意义效应、没有失效判据。protocol §4.1 的 H1 使用 "may still differ"，属于探索性表述。

### 5.2 建议的可证伪重述（SUPPORTED）

固定候选集、模型、prompt、顺序随机化、解码、上下文预算；仅比较**同为 Necessary 且无替代路径**、并在删除 token 数与推导深度上匹配的 Direct vs Bridge：

- **H0：** `Δ_Bridge − Δ_Direct ≤ δ`
- **H1：** `Δ_Bridge − Δ_Direct > δ`

其中 `Δ_r = P(fail | do(drop), r) − P(fail | keep)`，`δ` 需预先设定（例如 0.10–0.15，须由 pilot 方差与领域意义共同决定）。

**失效条件：** 在足够精度下无法拒绝 H0，或 95% CI 上界低于 δ；或调整结构协变量后角色对比的 CI 包含 0；或角色标签与必要性高度共线。（SUPPORTED）

### 5.3 识别的根本限制（VERIFIED）

- 删除是受控/随机的，但**角色与必要性是 item 的固有属性，不可随机化**。因此 role 对比是"跨 item 类的效应差"，不是随机化的 role 操纵；因果解释需要额外的 ignorability 假设。
- 必要性由 remove-one answerability 定义，necessity 主效应**接近同义反复**，且会压缩取值范围（attenuation）。
- 角色与必要性由同一套 remove-one/依赖分析标注（`docs/ANNOTATION_GUIDELINES.md:26-28, 98-110`），存在**循环风险**：Bridge 可能只是"依赖深度/度数/token 位置"的重命名。

**结论：** 当前设计只能支持"条件关联 + 受控删除效应"，不能支持"role 的因果调节"。除非引入**保持内容不变、只改变功能位置**的合成操纵（Tier A），否则不要使用 "causal moderation by role" 的措辞。

---

## 6. 实验设计审查

### 6.1 构造效度：自然数据中 Bridge 是否存在（VERIFIED，关键风险）

对官方 LoCoMo category-1 的统计：

- 282 题，覆盖 10 个对话；每对话 11–37 题。
- 276/282 有 ≥2 个 evidence ID；证据数分布：2 个 134 题、3 个 57、4 个 45、5 个 20，其余少量。
- 仅 1 条 compound evidence ID（`D8:6; D9:17` 形式）。
- 5 题 dry-run 的原始证据阅读结果：
  - `conv-26#qa[11]`：存在**可辩护的 entity-resolution bridge**（D3:13 说"from my home country"，D4:3 指明 home country 是 Sweden）。
  - `conv-41#qa[3]`、`conv-42#qa[11]`、`conv-43#qa[1]`、`conv-44#qa[12]`：均为**跨 speaker/跨 session 的独立事实聚合或多槽位列举**，不是推导链。
- 即 dry-run 中 **1/5** 有 Bridge 候选，与 `docs/PHASE0_LOCOMO_AUDIT.md:79` 的警告一致。

**判断（SUPPORTED）：** LoCoMo category-1 的 "multi-hop" 主要是跨 session 聚合，而不是依赖链。若把 Bridge 作为主因子，样本会在构造层面先失败。**在未统计 Necessary-Bridge 正例数量前，不应扩大自然数据标注。**

### 6.2 混杂与识别（SUPPORTED）

| 混杂 | 协议状态 | 审计判断 |
|---|---|---|
| 角色 vs 必要性 | 独立标注 + 分层 | 计划中；实施与信度未验证 |
| 冗余/替代路径 | remove-one + path-count 协变量 | 仅报告/调整，未操纵；定义主观 |
| 依赖深度 | 协变量 | 与 Bridge 共线 |
| 图度数/位置 | 非 schema 字段，可推导 | 仅调整，不操纵 |
| 删除 token 数 | "尽量匹配" | 部分；总上下文仍不同，除非 padding |
| 位置/顺序 | 固定 seed 随机化 | 部分；目标位置仍与角色相关 |
| 上下文截断 | 声称固定预算 | **未实现，无 no-truncation 断言** |
| 检索集变化 | 冻结候选集 | 强控制，但**未实现** |
| 对话聚类 | cluster bootstrap / 混合模型 | 计划；只有 10 簇 |
| 模型/prompt 方差 | 确认阶段 ≥2 家族 | pilot 单模型；本机有 3 个可用模型 |
| query intent | **schema 缺失** | **缺失** |
| 时序有效性 | schema 缺失；答案 prompt 不含时间戳 | 高风险/缺失 |
| 派生记忆泄漏 | 引擎存 raw + facts/relations | 只能通过固定外部上下文规避 |
| judge 方差 | LLM judge，同本地家族 | 需盲法与人工审计 |

### 6.3 最小可证伪实验（问题 4）

**Tier A（机制，可识别）：** 80–120 条半合成问题，≥8 个模板；每条有 gold DAG：一个 Necessary-Direct、一个 Necessary-Bridge（token/深度匹配）、一个 Redundant-Bridge、一个 Background；角色通过"保持内容不变、改变功能位置"操纵。

**Tier B（自然数据，描述性）：** 30–50 条经审计的 LoCoMo cat-1 题，预先声明只做描述性分析。

**条件：** keep-all；drop-Necessary-Direct；drop-Necessary-Bridge；drop-Redundant-Bridge；drop-Background；matched random-drop；可选 token-matched padding。

**固定：** candidate-set hash、模型（`qwen2.5:7b` + 至少一个不同家族，如 `mistral:7b`/`gemma3:12b`）、prompt hash、温度 0、上下文预算、顺序 seed（≥3 种顺序）。

**指标：** 主指标 = 盲评 all-slots-correct；次要 = F1、abstention、necessary-evidence recall、path availability。

**可行性（VERIFIED）：** 本机 Ollama 可用，模型 `qwen2.5:7b`、`mistral:7b`、`gemma3:12b`、`bge-m3`；`evaluation/answer_generation.py:generate_and_score` 可直接复用。当前**没有**删除/干预代码，需新建。

### 6.4 架构混杂、数据泄漏与评价偏差（问题 5）

- **架构混杂：** 若删除后重新检索，删除会同时改变候选集与排序，无法归因于过滤本身。protocol §7.1 已要求冻结候选集、不重检索；但**未实现、无断言**。必须在代码中强制 `candidate_set_hash` 不变，并断言除目标 ID 外上下文逐字节相同（允许 token padding 时需记录）。
- **数据泄漏：** 问题可能在无证据时仍可答（参数知识）。必须加入"无证据基线"并单独分析；若模型在 keep-all 之外的随机删除下仍高准确率，说明题目可被先验知识回答。
- **评价偏差：** 本地 LLM judge 与答案模型同家族；必须盲法、随机顺序、预注册 judge 版本/prompt hash，并在人工裁决子集上估计 sensitivity/specificity（按条件分层），必要时用 Rogan–Gladen 校正。abstention 必须预定义（建议主分析计为失败，abstention rate 作次要结果），不得丢弃。
- **截断：** 当前无 no-truncation 断言；token 预算与 padding 必须记录。否则"角色效应"可能只是"被删内容长度效应"。

### 6.5 缺失的操控检查/阴性对照（SUPPORTED）

- placebo drop：删除一个已核实无关、token 匹配的项。
- keep-all / oracle-context 天花板检查。
- 配对上下文 hash diff：只允许目标 ID 不同。
- 顺序/位置平衡表。
- 多 seed / 多模型 / prompt 改写。
- judge 盲法与人工审计子集。

---

## 7. 统计学审查

### 7.1 独立单位与有效样本（SUPPORTED）

- 独立簇 = 对话 = **k=10**；category-1 共 282 题，平均簇大小约 28.2。
- 设计效应 `DEFF = 1+(m−1)ρ`，`ρ` UNKNOWN。举例（仅示意）：ρ=0.05 → n_eff≈120；ρ=0.10 → ≈76；ρ=0.20 → ≈44。
- 决定性的不是 n_eff，而是 **10 个簇**。聚类稳健 SE、随机效应、对话层 moderator 最多只有 9–10 个自由度，低于通常建议的 20–30+。
- 题目之间还可能共享 evidence turn/实体，单一对话随机截距可能低估依赖；需报告 evidence overlap，并做排除共享证据题的敏感性分析。

### 7.2 30–50 题 pilot 能估计什么（SUPPORTED）

可以：标注可行性、失败模式、配对不一致率、粗略配对风险差（宽 CI）、簇方差（很不精确）。

不可以：稳定的 role 效应、稀有 cell 效应、**role × necessity 交互**。3×2 设计约 6 个 cell（每 cell 5–8 题），且条件只对部分题可用；交互检验通常需要主效应约 4 倍的样本，聚类后意味着数千题、数十簇。**不要拟合交互；只报告 cell 计数与描述性对比。**

### 7.3 具体方法建议（SUPPORTED）

- 配对二分类：**精确 McNemar / mid-p**，报告 b、c、不一致总数、配对 RD 与 CI；不要只用渐近卡方。
- 配对 RD 的簇 bootstrap（按对话，≥10,000 次，BCa/percentile）作为敏感性分析；10 簇下可能欠覆盖；wild cluster bootstrap 优于朴素聚类 SE，但仍脆弱。
- 条件 logistic 回归（以 question 为 stratum）优于混合模型：可调整 depth、token 数、替代路径，且避免随机效应。
- 混合效应 logistic：10 组下弱识别，role 随机斜率不可估；仅作敏感性分析，必要时 Firth 惩罚；不要解释方差成分。
- GEE 需小样本校正（Mancl–DeRouen），10 簇仍不可靠，不作主分析。
- 多重比较：**先定一个主对比**（建议：necessary 条件下 Bridge vs Direct 的配对 RD），其余为次要并用 Holm；不得对主对比做校正。
- 不得从"不显著"推断等价；应把 CI 与预先设定的最小有意义效应比较。

### 7.4 标注不确定性（VERIFIED as statistical fact）

- 2 名标注者 × 5 题**不能**支持 Cohen's κ；CI 几乎覆盖全范围，一个分歧可让 κ 移动约 0.2；稀有类别（Bridge/Necessary）会触发 prevalence paradox。
- 应报告：原始一致率、逐字段混淆矩阵、类别 prevalence、完整分歧清单；Gwet AC1/AC2 或 Krippendorff α（带 CI）只作补充，不作可靠性裁决。
- 要声称可靠性，需扩到 ≥50–100 个单元，且每个稀有类 ≥10–20 例；可能需要分层富集 + prevalence 加权；2 名标注者无法分离 rater bias 与 disagreement，需第三人复核子集。

### 7.5 缺失输出与排除（SUPPORTED）

- 按 ITT 分析所有计划运行：API 错误、上下文溢出、空输出、judge 解析失败都是结局/类别，不是静默排除。
- 预定义排除只能是数据完整性规则，并在运行前冻结；报告每条件完成率/失败率。
- 不得以"no-drop 成功"作为主分析条件（post-treatment/collider）；"answerable subset"只作次要并注明。
- 对缺失输出做 worst-case/best-case 敏感性分析。
- 禁止在看到结果后选择题目、标签或 Bridge。

**统计结论（VERIFIED）：现有样本（10 对话，282 聚类题；pilot 30–50 题）无法支持关于 role 效应或 role×necessity 交互的确认性推断。**

---

## 8. CCF-B 审稿风险

1. **最强拒稿理由：** 没有执行任何研究；且中心对比不可识别。仅"计划 + 文档"不构成论文证据。（VERIFIED）
2. **构造循环：** role 与 necessity 来自同一 remove-one/依赖分析；Bridge 可能只是图位置/深度/度数的重命名。需要：逐字段双标注 κ、联合 cell 计数、以及一个**不含 role 标签的结构预测器**（degree/centrality/depth/token position）证明其无法吸收效应。
3. **因果识别与混杂：** 无干预、无不变量执行；删除会改变 token 数、位置、题目族，甚至一次删除多个事实；pilot 单模型、10 簇、四因素混合模型被 §9.4 自认 underpowered。
4. **新颖性/重叠：** REALM 已确立 false-drop 代价；SPARE-RAG 覆盖链保持删除。仓库对 REALM/SPARE-RAG 的否定性断言是在 artifact 未审计时写的，审稿人会抓住这一点。
5. **两轨串味（claim bleed）：** `README.md:1-31` 与 `docs/RESEARCH_LOG.md:5-115` 是生命周期归因（F1–F6、n=10），本分支是独立的 false-drop 因果研究。协议 `:4-5` 与日志 `:600-602` 已声明不得合并，但两者共享 README、LoCoMo adapter 与 "failure" 词汇。草稿可能误引 README 的 "Real Memory 9/10"/"0 F6" 作为动机；审稿人可能把 F6/E0 与本研究的 false-drop 混为一谈。缓解：分论文产物、显式"非本线证据"横幅、未经桥接实验不得复用旧数字。
6. **过度声明：** RQ 中的 "causal diagnosis"/"causal cost"（`docs/RESEARCH_CHARTER.md:3,14`；protocol `:20`）在 do-干预存在前应改为 "counterfactual deletion effect"。
7. **统计计划超出数据：** 同时承诺 McNemar、cluster bootstrap、混合效应（§9.1），但 §9.4 与 matrix `:109` 自认 10 簇。

**审稿裁决（本次审计）：NARROW（置信度：中等）。** 问题合法，文档纪律强；但当前 role × necessity × temporal/query-intent 计划过宽、识别不足、重叠风险高。条件：(i) 通过 artifact 级新颖性门；(ii) 证明足够 joint cells 与 role/necessity 信度；(iii) 用结构协变量执行决定性实验。若 role 信度失败或与结构共线 → PIVOT 到 necessity/redundancy；若 REALM/SPARE-RAG 或其他最近工作已含匹配的角色对比、Bridge 持续缺失、或无法超过 10 个独立簇 → STOP。

---

## 9. 必须解决的问题（问题 6、7）

### 9.1 什么结果意味着假设失败（问题 6）

- 调整后的角色对比 95% CI 包含 0，或低于预先设定的最小有意义效应。
- 角色差异被图位置/度数/深度/token 数完全吸收。
- 差异可由检索/截断差异解释。
- role κ 低，或不存在明确无歧义的 Bridge 正例（`docs/ANNOTATION_GUIDELINES.md:184-193`）。
- 效应只在单一模型或单一合成模板家族出现。

### 9.2 什么情况下应放弃（问题 7）

- REALM/SPARE-RAG 或其他最近工作已包含匹配的 role 对比（artifact 级审计后确认）。
- Bridge 正例持续缺失（例如 Necessary-Bridge < 10 例且无法通过预先声明的规则扩展）。
- 标注者在一次代码本修订后仍无法区分 role/necessity。
- 独立对话/轨迹数无法超过 10，且没有可验证的第二基准。
- 效应无法在 ≥2 个模型家族复现。

---

## 10. 是否建议继续当前方向

**建议：有条件继续（NARROW），但不继续当前"role 为主因子"的宽版本。**

- **不停止**：问题本身合法，文档纪律与可复现意识明显高于平均；necesity/redundancy 的可识别对比仍有价值。
- **必须收窄**：把 role 从主假设降为探索性因素；主对比改为 **necessary vs redundant/background 的配对删除效应**（这是可识别、可证伪、且不与 REALM 的 resolver 设定重复的）。
- **必须补构造验证**：先用 Tier A 合成链证明 Bridge 可被独立标注、可与必要性分离，再决定是否投入自然数据。
- **必须补 artifact 审计**：REALM OpenReview 附件与 SPARE-RAG 全文/代码是新颖性门的硬前提。
- **在完成上述三项前，不得进入 Phase 2 的确认性实验，也不得使用 "causal role effect" 措辞。**

---

## 11. 下一阶段优先级最高的五项工作

1. **B-001（L1，最高优先）：** 继续获取 REALM OpenReview submission 52 附件。本次已确认论文与附件声明，但 API 检索未返回、附件未下载。若仍不可达，记录精确 blocker，并把矩阵中所有 REALM 否定性断言降级为 TENTATIVE。
2. **B-002（L1）：** 获取 SPARE-RAG 全文/附录/代码（MDPI 403；尝试作者主页、机构库、Crossref 链接的补充材料）。产出 feature-by-feature 重叠表。
3. **构造验证（L1/L2，新增建议）：** 构建 20–40 条最小合成链（Direct/Bridge/Redundant/Background × Necessary/Redundant），先做**只读**的 schema 校验与三人独立标注演练；目标是验证 role 可与 necessity 分离，而不是产出论文结果。
4. **B-006 的前置（L1）：** 把 dry-run 从 5 题扩到预先声明的 30–50 题之前，先修复三件事：(a) `query_intent` 与 `temporal_validity` 字段进入 schema 与标注手册；(b) compound evidence ID 拆分规则；(c) schema 校验器 + `pytest` 测试。
5. **L2 提案（需用户批准）：** 把主假设改为 necessity/redundancy 的可识别对比，role 作为次要/探索性因素；同步更新 charter、protocol、stop conditions，并在 decision log 记录理由。**这属于改变核心假设，必须人工批准。**

---

## 附录 A：本次实际执行的验证（可复现）

| 验证 | 命令/方法 | 结果 |
|---|---|---|
| 测试套件 | `python -m pytest -q` | 22 passed |
| 官方 LoCoMo 获取 | `git fetch --depth 1 origin cbfbc1db...` | 10 conv / 1,986 QA；category 1=282 |
| Packet 生成（B-005） | `python experiments/prepare_locomo_annotation_packet.py --dataset ... --output ...` | Wrote 5 records；输出在仓库外 |
| 数据统计 | 官方 JSON 直接解析 | cat1 evidence 分布、per-conv 计数、compound ID=1 |
| 构造检查 | 阅读 5 题证据原文 | 1/5 有 Bridge 候选 |
| 依赖检查 | `grep` / `cat requirements.txt` | 无 intervention 代码；无 jsonschema/pytest 依赖 |
| Workflow | YAML 解析 + `git ls-tree origin/main` | YAML 合法；文件不在 main |
| Ollama | `GET /api/tags` | qwen2.5:7b, mistral:7b, gemma3:12b, bge-m3 |
| 文献 | ACL Anthology / arXiv / Crossref / OpenAlex / PDF | 见 §3 |

## 附录 B：本次未能核实的事项（UNKNOWN）

- REALM OpenReview submission 52 附件的实际内容、代码入口、复现命令。
- SPARE-RAG 的全文细节、rollback 实现、代码/数据可用性。
- `locomo_refined_dataset` 的原始来源、版本与许可证。
- GitHub Actions secret `ANTHROPIC_API_KEY` 是否已配置。
- 用户 `G:` 工作区 76 项未提交改动的意图与归属。
- 任何 role/necessity 的人工标注结果（尚不存在）。
