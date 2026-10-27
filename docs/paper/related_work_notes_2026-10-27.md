# Related-work / 投稿调研笔记（2026-10-27）

来源：用户提供的外部搜索材料（`G:\PythonProject\paper_survey\` 下的
`submission_and_related_work_survey_2026-10-27.md` 与 `survey.txt`）。本文件
是写入仓库的蒸馏版；两份材料冲突处已标注 ⚠，投稿前须逐一核实。

---

## 1. 时间线结论（解决 "venue deadline unverified" 阻塞）

- **2026 年内所有窗口已关闭**：
  - ARR October 2026 投稿截止 **2026-10-12**（已过）。COLING 2027 与
    NAACL 2027 共用该轮 ARR（commitment 2026-12-23，也已不可及——投稿本身
    已截止）。
  - NLPCC 2026 已截止（两份材料给出的截止日不同：06-20 vs 09-23，但均已过，
    不再重要）。⚠️ "COLING 2026" 不存在可投稿渠道（ICCL 序列是 COLING 2025 →
    COLING 2027 澳门 2027-05-09~14）；第三方网站的 "COLING 2026 Barcelona"
    为不可靠信息。
- **下一现实目标：ARR ~2027 年 1 月 cycle → ACL 2027**。日期未官宣（ARR 改为
  10 周/5 cycle 年后逐周期公布），需每周盯 https://aclrollingreview.org/dates。
- **页数假设成立**：ACL 系共用 acl.sty，长文 8 页正文（不含 references、
  Limitations、Ethics、附录）。
- ARR 投稿本身 venue-agnostic：表单只选 primary/secondary 主题领域（本论文选
  "Resources and Evaluation"；contribution types 勾 Data resources / Data
  analysis），commitment 阶段才指定会议。

### 投稿前合规 checklist（2026-10 起 ARR 新规，违反 desk reject）

1. 全体作者 OpenReview 完整 profile（含 ORCID），仅邮箱注册无效；投稿后宽限
   仅 1 周。service contributor 48h 内登记；Responsible NLP Checklist 截稿后
   48h 内单独填写。
2. 匿名：正文/附录不得含作者身份链接（GitHub 仓库名、本机绝对路径）；代码走
   Anonymous GitHub / anonymous.4open.science；附录结果路径一律写相对路径
   （`./results/…`）；清除 PDF metadata。自引第三人称。
3. ARR 无强制匿名期（评审期间可挂非匿名 arXiv 预印本，但须在表单如实申报）。
4. 模板：官方 Overleaf ACL 模板（review 模式开启）+ aclpubcheck 自检。

---

## 2. 必读竞品（写 §2 之前必须先读全文）

| 论文 | 出处 | 重叠点 | 对本论文的威胁 |
|---|---|---|---|
| **MemTrace**: Tracing and Attributing Errors in LLM Memory Systems (Deng et al.) | arXiv 2605.28732 (2026-05) ⚠ | 记忆流水线 → 可执行 memory evolution graph；MemTraceBench；操作子图追踪定位失败根因；覆盖 Long-Context/RAG/**Mem0**/EverMemOS；用归因信号改进提示词 | **最直接竞品**。"首次生命周期失败归因"措辞不可再用 |
| **MemOps**: Benchmarking Lifecycle Memory Operations in Long-Horizon Conversations (Hao et al.) | arXiv 2607.12893 (2026-07) ⚠ | 操作级生命周期轨迹（记住/遗忘/更新/反思/组合）+ 结构化证据追踪 | 生命周期视角重叠 |
| **HaluMem**: Evaluating Hallucinations in Memory Systems (Chen et al.) | arXiv 2511.03506 (v3 2026-01) ⚠ | **操作级**幻觉定位：extraction/updating/QA 三阶段各自设 ground truth；实测 Mem0/Memobase/Supermemory/Zep；结论"错误在抽取/更新阶段产生并传播到 QA" | C1 最强竞品。但其评分用 GPT-4o 自动判，**无 judge 可靠性校正**（其自述 limitation）→ 正是本论文 C2 的区分点 |
| **LoCoMo-Plus** (Li et al.) | ACL 2026, 2026.acl-long.1150 ⚠ | 隐含约束/认知记忆评测 | 检验"仅追踪显式 gold evidence"的局限，§2 需引 |
| A Survey for LLM Agent Trajectory Analysis: From Failure Attribution to Enhancement | IEEE TSE Early Access 2026 ⚠ | agent 失败归因综述；指出操作级归因准确性仍局限 | 定义"可观测性"边界时引用 |

**§2 写作红线**（两份材料一致）：
- 不得把既有基准描述成"只测端到端正确率"——LongMemEval 本身含
  **indexing/retrieval/reading 阶段分析**（须读原文对应小节后准确转述）。
- MemoryAgentBench（四能力分段）、Rethinking Memory 综述（六原子操作分类）
  都是"生命周期视角"，但是能力/操作分类，非逐阶段证据流追踪。

### C1 重定位（候选措辞）

不能用："首次提出 memory lifecycle failure attribution"。

可用区分（三者叠加才是完整差异化）：
1. **追踪对象是"问题所需的必要证据"跨阶段可用性**（retrieval → memory 写入 →
   上下文注入 → 生成 → 自动判分全链路），而非操作执行是否成功（MemOps/
   MemTrace 的操作图）或幻觉类型（HaluMem）。
2. **证据充分性（E0）与证据可达性分开判定** + Real/Oracle Memory/Oracle
   Context 三层对照区分"记忆过程失败"与"最终回答失败"。
3. **评测器不确定性显式校准**（judge 弃权假阳性 20/66、gate 三轮校准
   κ=0.835、朴素弃权规则 52% → 守卫版 13/13）——三个竞品都依赖未校正的
   自动评分。MemTrace/MemOps/HaluMem 均无人工标注审计环节。
4. C4（架构条件性阶段定位，含 A1/A3 消融）与干预 null 的诚实报告
   （"阶段定位 ≠ 可操作诊断"）也是竞品没有的负结果维度。

⚠ 上述差异化在读完 MemTrace/MemOps 全文的归因算法与标注协议之前是"候选"，
不是已确立新颖性。

---

## 3. C2 的外部佐证

- **Penfield Labs（2026-04，灰色文献/博客，非同行评审）**：LoCoMo 答案键
  ~6.4% 错误；LLM judge 接受 63% 刻意错误答案；Zep vs Mem0 曾公开互指对方
  LoCoMo 评测无效。⚠ 引用前核对原文；若仅作动机叙述可脚注灰色文献。
- 学界 judge 偏差文献（MT-Bench、not-fair-evaluators、self-preference、
  Justice or Prejudice 等）见 §4 BibTeX 组 4。

---

## 4. BibTeX（两份材料合并；⚠ = 投稿前须按 Anthology/arXiv 页终校）

### 组 1 记忆基准

```bibtex
@inproceedings{maharana-etal-2024-locomo,
    title = "Evaluating Very Long-Term Conversational Memory of {LLM} Agents",
    % ⚠ 两份材料冲突：anthology ID 241 vs 747；作者列表也不同
    % （Turek+Chowdhury vs Tulyakov+Bansal+Barbieri+Fang——后者疑似张冠李戴）。
    % 以 aclanthology.org 页面为准核实 ID 与完整作者序。
    author = "Maharana, Adyasha and Lee, Dong-Ho and Turek, Sergey and Chowdhury, Amrita and others",
    booktitle = "Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    year = "2024", publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.acl-long.747/"
}

@inproceedings{wu2025longmemeval,
    title = "{L}ong{M}em{E}val: Benchmarking Chat Assistants on Long-Term Interactive Memory",
    % ⚠ 作者冲突：Zhang, Yunsheng vs Zhang, Yuwei——以 ICLR/OpenReview 页为准。
    author = "Wu, Di and Wang, Hongwei and Yu, Wenhao and Zhang, Yunsheng and Chang, Kai-Wei and Yu, Dong",
    booktitle = "International Conference on Learning Representations",
    year = "2025", url = "https://arxiv.org/abs/2410.10813"
}

@inproceedings{tan-etal-2025-membench,
    title = "{M}em{B}ench: Towards More Comprehensive Evaluation on the Memory of {LLM}-based Agents",
    author = "Tan, Haoran and Zhang, Zeyu and Ma, Chen and Chen, Xu and Dai, Quanyu and Dong, Zhenhua",
    booktitle = "Findings of the Association for Computational Linguistics: ACL 2025",
    pages = "19336--19352", year = "2025",
    doi = "10.18653/v1/2025.findings-acl.989",
    url = "https://aclanthology.org/2025.findings-acl.989/"
}

@article{hu2025memoryagentbench,
    title = "Evaluating Memory in {LLM} Agents via Incremental Multi-Turn Interactions",
    author = "Hu, Yuanzhe and Wang, Yu and McAuley, Julian",
    journal = "arXiv preprint arXiv:2507.05257", year = "2025",
    % ⚠ arXiv 号需核实
}

@article{chen2025halumem,
    title = "{H}alu{M}em: Evaluating Hallucinations in Memory Systems of Agents",
    author = "Chen, Ding and Niu, Simin and Li, Kehang and Liu, Peng and Zheng, Xiangping and Tang, Bo and Li, Xinchi and Xiong, Feiyu and Li, Zhiyu",
    journal = "arXiv preprint arXiv:2511.03506", year = "2025"
}

@article{deng2026memtrace,
    title = "{M}em{T}race: Tracing and Attributing Errors in Large Language Model Memory Systems",
    author = "Deng, Xinle and Zhong, Ruobin and Peng, Hujin and Lu, Xiaoben and Wu, Yanzhe and Li, Guang and Xu, Buqiang and Yao, Yunzhi and Fang, Jizhan and Guo, Junjie and Yuan, Yuan and Ma, Ziqing and Yu, Rui and Zhang, Ningyu",
    journal = "arXiv preprint arXiv:2605.28732", year = "2026"
}

@article{hao2026memops,
    title = "{M}em{O}ps: Benchmarking Lifecycle Memory Operations in Long-Horizon Conversations",
    author = "Hao, Xixuan and Zhang, Zeyu and Lin, Zehao and Sun, Yihang and Guo, Ziliang and Zhang, Xichong and Liang, Yuxuan and Xiong, Feiyu and Li, Zhiyu",
    journal = "arXiv preprint arXiv:2607.12893", year = "2026"
}

@inproceedings{li2026locomoplus,
    title = "{L}ocomo-{P}lus: Beyond-Factual Cognitive Memory Evaluation Framework for {LLM} Agents",
    author = "Li, Yifei and Guo, Weidong and Zhang, Lingling and Xu, Rongman and Huang, Muye and Liu, Hui and Xu, Lijiao and Xu, Yu and Liu, Jun",
    booktitle = "Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    pages = "25085--25100", year = "2026",
    doi = "10.18653/v1/2026.acl-long.1150",
    url = "https://aclanthology.org/2026.acl-long.1150/"
    % ⚠ survey-2 独有条目，须核对
}

@inproceedings{jia2025evaluatingltm,
    title = "Evaluating the Long-Term Memory of Large Language Models",
    author = "Jia, Zixi and Liu, Qinghua and Li, Hexiao and Chen, Yuyan and Liu, Jiqiang",
    booktitle = "Findings of the Association for Computational Linguistics: ACL 2025",
    pages = "19759--19777", year = "2025",
    doi = "10.18653/v1/2025.findings-acl.1014",
    url = "https://aclanthology.org/2025.findings-acl.1014/"
    % ⚠ survey-2 独有条目，须核对
}

@inproceedings{kim2024dialsim,
    title = "{D}ial{S}im: Dynamic Simulator for Conversational Question Answering with Long-term Dialogue Memory",
    author = "Kim, Hyunbin and others",
    booktitle = "arXiv preprint arXiv:2406.13144", year = "2024"
    % ⚠ 录用 venue 待核实
}
```

### 组 2 记忆系统架构

```bibtex
@article{chhikara2025mem0,
    title = "{M}em0: Building Production-Ready {AI} Agents with Scalable Long-Term Memory",
    author = "Chhikara, Prateek and Khant, Dev and Aryan, Saket and Singh, Taranjeet and Yadav, Deshraj",
    journal = "arXiv preprint arXiv:2504.19413", year = "2025"
}

@inproceedings{gutierrez2024hipporag,
    title = "{H}ippo{RAG}: Neurobiologically Inspired Long-Term Memory for Large Language Models",
    author = "Guti{\'e}rrez, Bernal Jim{\'e}nez and Shu, Yiheng and Gu, Yu and Yasunaga, Michihiro and Su, Yu",
    booktitle = "Advances in Neural Information Processing Systems 37 (NeurIPS)", year = "2024"
}

@article{xu2025amem,
    title = "{A}-{MEM}: Agentic Memory for {LLM} Agents",
    author = "Xu, Wujiang and Liang, Zujie and Wang, Kai and others",
    journal = "arXiv preprint arXiv:2502.12110", year = "2025"
}

@article{packer2023memgpt,
    title = "{M}em{GPT}: Towards {LLM}s as Operating Systems",
    author = "Packer, Charles and Wooders, Sarah and Lin, Kevin and Fang, Vivian and Patil, Shishir G. and Stoica, Ion and Gonzalez, Joseph E.",
    journal = "arXiv preprint arXiv:2310.08560", year = "2023"
}

@article{wang2024scm,
    title = "Enhancing Large Language Model with Self-Controlled Memory Framework",
    author = "Wang, Bing and Liang, Xinnian and Yang, Jian and Huang, Hui and Wu, Shuangzhi and Wu, Peihao and Lu, Lu and Ma, Zejun and Li, Zhoujun",
    journal = "arXiv preprint arXiv:2304.13343", year = "2024"
}

@inproceedings{pan2025secom,
    title = "{S}e{C}om: On Memory Construction and Retrieval for Personalized Conversational Agents",
    author = "Pan, Zhuoshi and Wu, Qianhui and Jiang, Huiqiang and Luo, Xufang and Cheng, Hao and Li, Dongsheng and Yang, Yuqing and Lin, Chin-Yew and Zhao, H. Vicky and Qiu, Lili and Gao, Jianfeng",
    booktitle = "International Conference on Learning Representations", year = "2025",
    url = "https://openreview.net/forum?id=xKDZAW0He3"
}

@article{li2025memos,
    title = "{M}em{OS}: A Memory {OS} for {AI} System",
    author = "Li, Zhiyu and others",
    journal = "arXiv preprint arXiv:2507.03724", year = "2025"
    % ⚠ 作者列表以 arXiv 页为准
}
```

### 组 3 综述

```bibtex
@article{zhang2024memorysurvey,
    title = "A Survey on the Memory Mechanism of Large Language Model based Agents",
    author = "Zhang, Zeyu and Bo, Xiaohe and Ma, Chen and Li, Rui and Chen, Xu and Dai, Quanyu and Zhu, Jieming and Dong, Zhenhua and Wen, Ji-Rong",
    % ⚠ arXiv 2404.13501；survey-2 称已刊 ACM TOIS 2025——若属实引用正式版。
    journal = "ACM Transactions on Information Systems", year = "2025",
    note = "arXiv:2404.13501"
}

@article{du2025rethinking,
    title = "Rethinking Memory in {AI}: Taxonomy, Operations, Topics, and Future Directions",
    author = "Du, Yiming and Huang, Wenyu and Zheng, Danna and Wang, Zhaowei and Montella, S{\'e}bastien and Lapata, Mirella and Wong, Kam-Fai and Pan, Jeff Z.",
    journal = "arXiv preprint arXiv:2505.00675", year = "2025"
    % ⚠ arXiv 号待核实（约 2505.00675）
}
```

### 组 4 LLM-as-judge / 评测可靠性

```bibtex
@inproceedings{zheng2023judging,
    title = "Judging {LLM}-as-a-{J}udge with {MT}-{B}ench and Chatbot Arena",
    author = "Zheng, Lianmin and Chiang, Wei-Lin and Sheng, Ying and Zhuang, Siyuan and Wu, Zhanghao and Zhuang, Yonghao and Lin, Zi and Li, Zhuohan and Li, Dacheng and Xing, Eric and Zhang, Hao and Gonzalez, Joseph E. and Stoica, Ion",
    booktitle = "Advances in Neural Information Processing Systems 36 (NeurIPS)", year = "2023"
}

@inproceedings{wang2024notfairevaluators,
    title = "Large Language Models are not Fair Evaluators",
    author = "Wang, Peiyi and Li, Lei and Shang, Liang and Liu, Zehua and Xie, Qingxuan and Zhang, Miran and Liu, Zhifang and Lu, Yaqing and others",
    booktitle = "Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics", year = "2024",
    note = "arXiv:2305.17926"
}

@inproceedings{liu2023geval,
    title = "{G}-{E}val: {NLG} Evaluation using {GPT}-4 with Better Human Alignment",
    author = "Liu, Yang and Iter, Dan and Xu, Yichong and Wang, Shuohang and Xu, Ruochen and Zhu, Chenguang",
    booktitle = "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)", year = "2023"
}

@article{panickssery2024selfpreference,
    title = "{LLM} Evaluators Recognize and Favor Their Own Generations",
    author = "Panickssery, Arjun and Bowman, Samuel R. and Feng, Shi",
    journal = "arXiv preprint arXiv:2404.13076", year = "2024"
}

@inproceedings{ye2025justice,
    title = "Justice or Prejudice? Quantifying Biases in {LLM}-as-a-Judge",
    author = "Ye, Jiayi and Wang, Yanbo and Huang, Yue and Chen, Dongping and Zhang, Qihui and Moniz, Nuno and Gao, Tian and Geyer, Werner and Huang, Chao and Chen, Pin-Yu and Chawla, Nitesh V. and Zhang, Xiangliang",
    booktitle = "International Conference on Learning Representations", year = "2025"
    % ⚠ venue：survey-1 称 CALM，survey-2 称 ICLR 2025——以后者可能性高，仍须核
}

@inproceedings{chen2024humansjudge,
    title = "Humans or {LLM}s as the Judge? A Study on Judgement Biases",
    author = "Chen, Guiming Hardy and Chen, Shunian and Liu, Ziche and Jiang, Feng and Wang, Benyou",
    booktitle = "Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing", year = "2024",
    url = "https://aclanthology.org/2024.emnlp-main.474/"
}

@inproceedings{shi2025judgingjudges,
    title = "Judging the Judges: A Systematic Study of Position Bias in {LLM}-as-a-Judge",
    author = "Shi, Lin and Ma, Chiyu and Liang, Wenhua and Diao, Xingjian and Ma, Weicheng and Vosoughi, Soroush",
    booktitle = "Proceedings of the 14th IJCNLP and the 4th AACL",
    pages = "292--314", year = "2025",
    url = "https://aclanthology.org/2025.ijcnlp-long.18/"
}

@article{artstein2008kappa,
    title = "Inter-Coder Agreement for Computational Linguistics",
    author = "Artstein, Ron and Poesio, Massimo",
    journal = "Computational Linguistics", volume = "34", number = "4",
    pages = "555--596", year = "2008"
}
```

### 组 5 失败归因

```bibtex
@article{zhang2025whoandwhen,
    title = "Which Agent Causes Task Failures and When? On Automated Failure Attribution of {LLM} Multi-Agent Systems",
    author = "Zhang, Shaokun and Yin, Ming and Zhang, Jieyu and Liu, Jiale and Han, Zhiguang and Zhang, Jingyang and Li, Beibin and Wang, Chi and Wang, Huazheng and Chen, Yiran and Wu, Qingyun",
    journal = "arXiv preprint arXiv:2505.00212", year = "2025"
    % step 级归因最佳方法仅 14.2%——可引作"归因准确性仍开放"的佐证
}

@article{cemri2025whymasfail,
    title = "Why Do Multi-Agent {LLM} Systems Fail?",
    author = "Cemri, Mert and others",
    journal = "arXiv preprint arXiv:2503.13657", year = "2025"
}

@article{agentracer2025,
    title = "{A}gen{T}racer: Who Is Inducing Failure in the {LLM} Agentic Systems?",
    author = "Zhang, Guibin and others",
    journal = "arXiv preprint arXiv:2509.03312", year = "2025"
}

@article{agentsfaillearn2025,
    title = "Where {LLM} Agents Fail and How They can Learn From Failures",
    journal = "arXiv preprint arXiv:2509.25370", year = "2025"
}

@article{diagnosingfailures2025,
    title = "Diagnosing Failures in {LLM}s' Answers: Integrating Error Attribution into Evaluation Framework",
    journal = "arXiv preprint arXiv:2507.08459", year = "2025"
}
% ⚠ 后两条 survey 只给 arXiv 号未给作者，终校时补全
```

### 组 6 hash embedding / 检索敏感性

```bibtex
@inproceedings{weinberger2009hashing,
    title = "Feature Hashing for Large Scale Multitask Learning",
    author = "Weinberger, Kilian and Dasgupta, Anirban and Langford, John and Smola, Alex and Attenberg, Josh",
    booktitle = "Proceedings of the 26th International Conference on Machine Learning (ICML)", year = "2009"
}

@inproceedings{svenstrup2017hashembeddings,
    title = "Hash Embeddings for Efficient Word Representations",
    author = "Svenstrup, Dan Tito and Hansen, Jonas and Winther, Ole",
    booktitle = "Advances in Neural Information Processing Systems 30 (NeurIPS)", year = "2017"
}
% Hash2Vec（Argerich et al. 2016）如需引用 limitation 措辞再补条目。
% SeCom（pan2025secom）已观察到"turn/session 级方法随检索模型变化大"——
% embedding-swap 敏感性 limitation 的最直接可引证据。
```

---

## 5. 待核实清单（投稿前逐一关闭）

1. LoCoMo anthology ID（241 vs 747）+ 完整作者列表（两份材料冲突，survey-2
   的作者列表疑似张冠李戴）。
2. LongMemEval 作者（Zhang Yunsheng vs Yuwei）。
3. MemTrace / MemOps / HaluMem：arXiv ID、作者列表，**并读全文**（方法、归因
   算法、标注协议）——这是写 §2 的前置条件。
4. Du Rethinking Memory arXiv 号（~2505.00675）。
5. Justice or Prejudice 的 venue（ICLR 2025 vs CALM）。
6. LoCoMo-Plus、jia-etal-2025 两条 survey-2 独有条目。
7. Penfield Labs LoCoMo 审计原文（灰色文献，仅作动机脚注）。
8. LongMemEval 原文 indexing/retrieval/reading 阶段分析的具体小节——§2 转述
   必须准确。
9. ARR 2027-01 cycle 日期——每周盯 aclrollingreview.org/dates。
10. Zhang memory survey 是否已正式刊于 ACM TOIS 2025（是则引正式版）。

## 6. §2 结构建议（两份材料综合）

- 三小节骨架：(a) memory benchmarks；(b) memory systems + lifecycle/operation
  级诊断（MemTrace/MemOps/HaluMem 放这里，逐点对照）；(c) evaluation
  reliability（C2）。参考 LongMemEval 的 related-work 组织与 MemoryAgentBench
  的"能力 × 基准对比矩阵"表格写法。
- 定位句候选："Existing work localizes errors at the operation level or
  evaluates capability coverage; none traces the *necessary evidence* for a
  question through retrieval, memory write, context assembly, generation and
  automatic judging while explicitly calibrating the judge itself. We fill
  this gap and show the resulting labels change the conclusions."
- 与 HaluMem 的边界句必须出现在 §2 第一段或 §1 贡献处，防审稿人拿
  2511.03506 直接质疑新颖性。
