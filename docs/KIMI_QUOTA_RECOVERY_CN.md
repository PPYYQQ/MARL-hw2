# Kimi checkpoint 运行手册

本手册覆盖 full MATH `manual_v1` test 的 checkpoint 复现和扩展流程。当前作业必跑实验已经完成；这些步骤用于复现实验、恢复失败 chunk，或继续做可选 ablation/prompt tuning。

## 当前状态

| 项目 | 当前值 |
| --- | --- |
| 数据集 | MATH test |
| 样本数 | 486 |
| workflow | `manual_v1` |
| chunk size | 20 |
| 总 chunk 数 | 25 |
| 当前 checkpoint run id | `math-test-manual-v1` |
| 当前进度命令 | `make summarize-math-manual-chunks` |
| 当前完成度 | 25/25 chunks |
| 已记录调用 | 2,431 LLM calls |
| 已记录 token | 3,786,936 tracked tokens |
| 必跑剩余额度 | 0；更多额度只用于复现或可选扩展 |

## 复现前检查

先确认本地没有未提交改动，且 GitHub 同步：

```bash
make status-summary
```

预期 warning 只应来自学生信息占位符，以及当前 shell 没有设置 `KIMI_API_KEY` 时的环境提示。

确认 chunk 计划覆盖 486 道题：

```bash
make verify-math-manual-plan
```

预览 runner，不调用 API：

```bash
make dry-run-math-manual-chunks
```

## 复现或继续一个 API chunk

默认 run id 已完成 25/25 chunks；再次运行会跳过已完成 chunk。若要复现新 run，请先设置新的 run id 或在明确知道影响的情况下清理本地 ignored run 目录。复现时建议先只跑 1 个 chunk：

```bash
make resume-math-manual-chunk
```

跑完立刻检查 checkpoint：

```bash
make summarize-math-manual-chunks
```

如果 completed 数量增加，说明额度、限速和 checkpoint 都正常。随后可以继续一次跑 1 个 chunk，或者小幅提高批量：

```bash
MATH_MANUAL_MAX_CHUNKS=3 make resume-math-manual-chunk
```

不建议一开始就把 `MATH_MANUAL_MAX_CHUNKS` 调得很大；当前 workflow 每 20 题约 100 calls，长时间运行更容易受限速、网络和余额影响。

## 失败时怎么判断

如果 summary 显示 `quota-failed`：

- 不要删除 `experiments/chunked_runs/`。
- 先补余额或替换有效 `KIMI_API_KEY`。
- 重新运行 `make resume-math-manual-chunk`；已完成 chunk 会被跳过。

如果进程中断但没有 quota 报错：

- 运行 `make summarize-math-manual-chunks` 看最近完成的 chunk。
- 继续运行 `make resume-math-manual-chunk`，runner 会从下一个未完成 chunk 继续。

如果出现新的非 quota 错误：

- 保留终端输出和 chunk 目录。
- 先运行 `make status-summary` 确认 Git 状态。
- 不要把失败 chunk 当作完成结果写入报告。

## 全部 chunk 完成后或刷新结果时

当前 full MATH `manual_v1` 已完成。需要刷新表格时，汇总 chunked 结果表：

```bash
make collect-math-manual-chunked
```

验证表里有 486 题的 MATH test `manual_v1` 行：

```bash
make verify-math-manual-result
```

该 gate 默认还会要求至少 `2400` calls 和 `2500000` tokens，避免部分 chunk 结果被误当作完整 full-test 表。

之后需要确认 `report/main.tex` 中的 full-test 分数、calls、tokens 与表格一致，并确认报告不保留 pending-run 表述：

```bash
make verify-final-report-ready
```

如果 full-test 结果被报告引用，还需要刷新 evidence、重建 PDF、跑完整交接检查：

```bash
make refresh-evidence
make build-report
make handoff-check
```

最后提交并推送相关改动：

```bash
git add report/tables/math_test_manual_chunked.md report/main.tex report/evidence PROGRESS.md
git commit -m "Add full MATH manual workflow result"
git push origin main
make post-push-check
```

`report/main.pdf` 是本地生成文件并被 `.gitignore` 忽略；提交包会在打包时包含当前 PDF。正常情况下不要把 PDF 加入 Git，除非课程明确要求仓库也跟踪 PDF。

## 最终提交

拿到真实姓名、学号、邮箱，并且 full MATH `manual_v1` 结果表已提交后，运行最终 gate：

```bash
make ready-to-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

如果不需要复现或扩展实验，可以跳过本手册的 API 步骤，按 `docs/FINAL_HANDOFF_CN.md` 的当前实验状态流程提交当前版本。
