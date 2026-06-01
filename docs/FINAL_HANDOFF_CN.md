# 最终交接清单

本文件面向最后接手提交的人，回答三个问题：现在能交什么、还缺什么、如果拿到外部支持应该怎么继续。

## 当前可交付状态

| 项目 | 状态 | 位置 |
| --- | --- | --- |
| 作业代码 | 已整理并提交到 GitHub | `AFlow/`, `experiments/`, `Makefile` |
| 报告 PDF | 已本地编译，可进入默认提交包 | `report/main.pdf` |
| 实验结果表 | 已生成并写入报告 | `report/tables/` |
| 原始证据 | 已导出被报告引用的 CSV/config/log/token summary | `report/evidence/` |
| 默认提交 zip | 已可生成并验证 | `submission/MARL-hw2-submission.zip` |
| 作业要求矩阵 | 已整理中英文视图 | `docs/REQUIREMENT_RUN_MATRIX.md` |
| 完成度审计 | 已整理 requirement-by-requirement 证据 | `docs/COMPLETION_AUDIT.md` |
| 进度日志 | 持续维护 | `PROGRESS.md` |

## 最终提交前必须补的信息

| 缺口 | 为什么需要 | 补齐后执行 |
| --- | --- | --- |
| 姓名 | 报告作者和命名 zip 需要 | `make finalize-submission FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"` |
| 学号 | 报告 affiliation 和课程提交文件名需要 | 同上 |
| 邮箱 | 报告 corresponding author 需要 | 同上 |

`finalize_submission.py` 默认会临时填入个人信息、重编译 PDF、生成带姓名学号的 zip、验证 zip 内的元数据，然后恢复本地 `report/main.tex` 和 `report/main.pdf` 的占位符，避免把个人信息留在工作树里。

正式打包前可以先用真实信息预演，不写文件：

```bash
make finalize-submission-dry-run FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

## 如果不补 Kimi 额度

可以提交当前版本，但报告会明确说明 full MATH `manual_v1` test 因 Kimi 余额不足未完成。当前已有证据仍支持：

- MATH direct/CoT full test 已完成。
- HumanEval direct/CoT/`manual_v1`/ablation full test 已完成。
- MATH `manual_v1` 在 validate20 和 validate50 上超过 direct 与 CoT。
- 成本、失败案例、消融和证据验证都已完成。

提交前运行：

```bash
make handoff-check
```

预期结果是 0 failures，只有两个 warning：学生信息占位符和 full MATH `manual_v1` test 表缺失。`handoff-check` 还会运行 known-warning 门禁，如果出现其他 warning 会失败，避免把新问题混在已知外部缺口里。拿到学生信息后再运行最终打包命令。

如果只想单独检查 warning 是否仍然只来自已知外部缺口，运行：

```bash
make verify-known-warnings
```

每次关键提交 push 后，确认本地分支和 GitHub 同步：

```bash
make verify-github-sync
```

如果要做一次完整的 push 后交接检查，运行：

```bash
make post-push-check
```

## 如果补到 Kimi 额度

建议至少准备 CNY 50；CNY 80-100 更稳。剩余 full MATH `manual_v1` 预计约 2,430 次调用、3.40M raw tokens、25 个 chunk。

先预览计划，不调用 API：

```bash
make dry-run-math-manual-chunks
```

然后先跑一个 chunk，确认余额、限速和 checkpoint 都正常：

```bash
make resume-math-manual-chunk
```

查看当前 chunk 完成情况和下一个待跑 chunk：

```bash
make summarize-math-manual-chunks
```

这个命令会输出 completed/quota-failed/missing 数量、下一个未完成 chunk，以及建议下一条 Make 命令。

继续重复同一命令，或按需要提高每次 chunk 数：

```bash
MATH_MANUAL_MAX_CHUNKS=3 make resume-math-manual-chunk
```

chunk 完成后汇总结果：

```bash
make collect-math-manual-chunked
```

之后需要更新报告、重建 PDF、刷新证据、重跑交接 gate：

```bash
make build-report
make verify-report-pdf
make handoff-check
```

如果新增结果表被报告引用，还应把对应 evidence 导出并提交。

full MATH `manual_v1` 表已经提交到 Git，并且真实姓名学号邮箱都补齐后，可以用一个最终提交 gate 同时检查 handoff、生成实名 zip、并确认 GitHub 同步：

```bash
make ready-to-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

## 不要做的事

- 不要把 `KIMI_API_KEY`、`.env`、`AFlow/config/config2.yaml` 或平台账号信息提交到 Git。
- 不要直接删除 `experiments/runs/` 或 `experiments/chunked_runs/` 中的本地结果；这些目录被忽略，但仍可能用于重新导出证据。
- 不要在有未提交 tracked 改动时打包；package 脚本会拒绝这种状态。
- 不要把 full MATH `manual_v1` 的 validation 分数当作 full test 分数写入报告。

## 快速定位

| 你想看 | 文件 |
| --- | --- |
| 作业要求跑什么、实际跑了什么 | `docs/REQUIREMENT_RUN_MATRIX.md` |
| 每一步干了什么 | `PROGRESS.md` |
| 所有实验命令 | `docs/EXPERIMENT_COMMANDS.md` |
| 还差什么才能最终提交 | `docs/COMPLETION_AUDIT.md` |
| 当前提交状态 | `docs/SUBMISSION_STATUS.md` |
| 额度花在哪里、还要多少 | `report/tables/api_budget_summary.md` |
