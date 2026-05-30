# AGENTS.md

请所有 coding agent 在本目录及其子目录中工作时遵守本文件。每次回复用户都必须以 `Harry` 开头。
github目录：https://github.com/PPYYQQ/MARL-hw2.git
写作使用模版：/home/yongqian/Documents/yongqian/MARL大作业/hw2/icml2022.zip
参考的论文在：/home/yongqian/Documents/yongqian/MARL大作业/hw2/refpaper
AFlow代码仓库：https://github.com/FoundationAgents/AFlow.git
如果遇到hugging face的网络问题考虑挂：https://hf-mirror.com
如果遇到网络问题需要代理，可以考虑看batshrc里的setp

## 作业总体概述

本作业是“多智能体系统作业：多智能体工作流设计”。目标是基于 AFlow codebase 理解、复现并改进大模型多智能体系统，用多智能体 workflow 提升基模在数学与代码推理任务上的表现。

作业文档要求完成：

- 阅读 AFlow 论文与代码，在报告中说明基于大模型构建多智能体系统的工程方法。
- 按 AFlow README 完成环境配置，并在报告中记录安装流程。
- 在不同设定下运行仅使用基模的结果，至少包含直接调用基模和 CoT baseline。
- 针对 `MATH-500` 与 `HumanEval` 两个 benchmark 设计新的多智能体系统。
- 改进方案应超过仅使用基模，包括 CoT baseline；报告需包含算法设计、结果对比图表、消融结果等。
- Bonus 可探索更难 benchmark，例如 AIME 24/25，或提出新的自动化 workflow 构建方案。

默认基模使用课程指定的 `kimi-k2-0905-preview`。API key、代金券兑换、平台模型可用性和具体限额必须由用户提供或确认，不要把密钥写入仓库。
（更新 使用`kimi-K2.5`，api key放在了环境变量中 KIMI_API_KEY）

## 完成预期评估

在具备 API key、数据集访问和足够 token 预算的前提下，coding agent 可以自动完成大部分工程工作：

- 可以自动完成：AFlow 代码拉取或整理、环境配置说明、基线脚本、workflow/operator 实现、实验运行脚本、日志汇总、结果表格和报告初稿。
- 可以半自动完成：根据小样本结果迭代 prompt、operator 和 workflow；选择最终图表；撰写论文阅读总结和实验分析。
- 需要人工支持：Kimi 账号注册、代金券兑换、API key 提供、课程群信息确认、最终报告署名信息、是否投入高 token 预算跑完整实验。
- 不应承诺自动保证：在所有 benchmark 上一定超过 CoT baseline。若初版未超过，需要通过消融、prompt 调参、样本数和 workflow 结构迭代。

建议计算资源：

- 本地机器：Python 3.9 环境，4 核 CPU，8 GB 内存可跑；16 GB 内存更稳；无需 GPU。
- 磁盘：至少 5 GB，用于 AFlow 仓库、数据集、实验日志、CSV 和报告图。
- 网络：需要稳定访问 Kimi/OpenAI-compatible API、GitHub、数据集下载地址。
- API/token：直接 baseline 通常是最低成本；多智能体 workflow 约为直接调用的 3-8 倍；AFlow 自动搜索可能进一步放大到 10 倍以上。先小样本验证，再扩大到完整 `MATH-500` 和 `HumanEval`。
- 时间：环境与数据准备约 0.5-2 小时；小样本 workflow 迭代约 2-6 小时；完整实验取决于 API 限速和 token 预算，通常预留半天到 1 天；报告整理至少预留 0.5-1 天。

## 预估项目与代码架构

当前目录只有作业 PPT。若 AFlow 代码尚未存在，应优先在本目录下创建或克隆 `AFlow/`，不要把临时文件、密钥和大型缓存混入提交包。

推荐结构：

```text
.
|-- AGENTS.md
|-- hw2.pptx
|-- AFlow/
|   |-- run.py
|   |-- run_baseline.py
|   |-- config/
|   |   |-- config2.example.yaml
|   |   `-- config2.yaml          # 本地私密配置，不提交
|   |-- data/
|   |   `-- datasets/
|   |-- benchmarks/
|   |   |-- math.py
|   |   `-- humaneval.py
|   |-- scripts/
|   |   |-- async_llm.py
|   |   |-- evaluator.py
|   |   |-- operators.py
|   |   |-- optimizer.py
|   |   `-- workflow.py
|   `-- workspace/
|       |-- MATH/
|       |   `-- workflows/
|       `-- HumanEval/
|           `-- workflows/
|-- experiments/
|   |-- baselines/
|   |-- ablations/
|   `-- final/
`-- report/
    |-- figures/
    |-- tables/
    `-- report.tex 或 report.docx
```

AFlow 关键模块：

- `run.py`：AFlow optimizer 入口，选择 dataset、operator 列表、轮数、模型配置和输出目录。
- `run_baseline.py`：基线或已有 workflow 测试入口，可改造成统一 baseline runner。
- `scripts/async_llm.py`：OpenAI-compatible 异步 LLM 客户端与 token/cost 统计。
- `scripts/operators.py`：基础 operator，如 `Custom`、`AnswerGenerate`、`CustomCodeGenerate`、`ScEnsemble`、`Programmer`、`Test`、`Review`、`Revise`。
- `scripts/workflow.py`：workflow 基类。
- `scripts/evaluator.py`：benchmark 到 evaluator 的分发逻辑。
- `benchmarks/math.py`：数学任务判分与答案抽取。
- `benchmarks/humaneval.py`：HumanEval 代码执行与测试判分。
- `workspace/<Dataset>/workflows/`：每轮生成或手写 workflow 的主要落点。

推荐新建或改造的实验代码：

- `experiments/run_baselines.py`：统一运行 direct、CoT、可选 self-consistency baseline。
- `experiments/run_workflows.py`：统一运行最终 MATH 与 HumanEval workflow。
- `experiments/collect_results.py`：汇总 CSV、计算平均分、平均 cost、总 token 和相对提升。
- `AFlow/workspace/MATH/workflows/manual_v1/graph.py`：手写数学 workflow。
- `AFlow/workspace/HumanEval/workflows/manual_v1/graph.py`：手写代码 workflow。

## 实施计划

1. 准备环境与资料
   - 克隆或复制 AFlow 到 `AFlow/`。
   - 创建 Python 3.9 环境并安装 `requirements.txt`。
   - 复制 `config/config2.example.yaml` 为本地 `config/config2.yaml`。
   - 配置 `kimi-k2-0905-preview` 的 `base_url`、`api_key`、`temperature`，避免提交密钥。

2. 数据与基线
   - 下载 AFlow 数据集，并确认 `MATH-500` 与 `HumanEval` 的实际 JSONL 路径。
   - 若 AFlow 默认 `MATH` 不是 `MATH-500`，新增或转换 `math500_validate.jsonl`、`math500_test.jsonl`。
   - 实现 direct baseline：只让基模直接回答。
   - 实现 CoT baseline：加入逐步推理 prompt，并统一答案抽取。
   - 记录模型名、temperature、top_p、样本数、并发数、时间和 token/cost。

3. MATH-500 workflow
   - 先实现手写 workflow，不急于跑 AFlow 自动搜索。
   - 推荐结构：多路解题生成 `k=3` 或 `k=5`，可选 `Programmer` 做符号/数值验证，`Review` 检查答案，`Revise` 修正，`ScEnsemble` 选择最终解。
   - 输出必须保留可被 `MATHBenchmark.extract_model_answer` 识别的最终答案，优先使用 `\boxed{...}`。
   - 先在 10-30 题子集验证，再逐步扩到完整 `MATH-500`。

4. HumanEval workflow
   - 推荐结构：`CustomCodeGenerate` 生成函数代码，`Test` 用公开测试或自构造测试执行，失败后 `Revise` 或 reflection 修复，最后可对多个候选做选择。
   - 输出必须是可执行 Python 代码，并包含指定 `entry_point`。
   - 对执行超时、导入限制和代码清洗保持谨慎，不要放宽危险执行限制。

5. 消融与对比
   - 至少比较 direct、CoT、final workflow。
   - 建议消融：去掉 ensemble、去掉 review/revise、改变生成候选数 `k`、只用代码测试修复。
   - 每个实验都保存原始 CSV、失败样例日志和配置快照。

6. 报告
   - 报告建议不少于 3 页，双栏。
   - 内容包括：AFlow 工程结构理解、环境配置过程、baseline 设置、workflow 设计原因、实验结果表、消融图表、失败案例分析、限制与未来工作。
   - 引用 AFlow、multi-agent debate、GPTSwarm 等参考文献。

## 测试计划

优先从小范围、可复现测试开始，不要直接消耗大量 API token。

1. 静态与导入检查
   - 运行 `python -m py_compile` 检查新增脚本和 workflow。
   - 对新增 benchmark adapter、结果汇总脚本运行最小参数 smoke test。

2. Mock 或小样本功能测试
   - 对答案抽取、CSV 汇总、结果表生成等纯本地逻辑写最小测试。
   - 如果新增 LLM wrapper，优先用 mock response 验证格式解析。

3. 小样本 API smoke test
   - MATH 先跑 3-5 题 direct 和 CoT，确认日志、CSV、cost 正常。
   - HumanEval 先跑 3-5 题，确认代码可被 benchmark 执行，超时与失败日志正常。
   - workflow 每次结构变化后先跑 5-10 题，检查格式和成本。

4. 子集验证
   - MATH 使用 30-50 题子集比较 direct、CoT、workflow。
   - HumanEval 使用 20-40 题子集比较 direct、CoT、workflow。
   - 若 workflow 未超过 CoT，不要扩大完整实验，先分析失败样例并调整。

5. 完整评估
   - 在预算允许时运行完整 `MATH-500` 与 `HumanEval`。
   - 保存完整命令、配置、输出 CSV、日志、平均分、总 cost、平均 cost。
   - 结果进入报告前，抽查若干错误样例，确认不是答案抽取或代码格式问题导致误判。

6. 报告校验
   - 图表数字必须来自保存的 CSV 或汇总脚本。
   - 报告中的模型名、参数、样本数、日期和 benchmark 名称必须与实验日志一致。
   - 最终压缩包按“学号+姓名+作业名称”命名，报告为 PDF；代码作为补充材料可选提交。

## 工作约束

- 不要提交 API key、代金券码、平台账号信息或 `.env`。
- 不要删除原始 `hw2.pptx`。
- 忽略 `~$hw2——.pptx` 这类 Office 临时锁文件。
- 优先小样本验证，避免一次性跑高成本全量实验。
- 修改 AFlow 时保持最小改动，优先新增 `experiments/` 脚本和 `workspace/.../manual_v*` workflow。
- 所有重要实验都要可复现：保留命令、配置、随机种子或样本索引。
