# Requirement Run Matrix

This document maps the assignment's required experiments to the runs completed in this repository. It is meant as a quick answer to: what the homework asks for, what has been run, and what remains before final submission.

## 中文交接矩阵

| 作业要求 | 作业应该跑什么 | 已经跑了什么 | 当前状态 | 还需要什么支持 |
| --- | --- | --- | --- | --- |
| Direct baseline | MATH-500 和 HumanEval 的 direct prompting 基线 | MATH validate20、MATH validate50、MATH full test 486 题；HumanEval validate20、HumanEval full test 131 题 | 已完成 | 无 |
| CoT baseline | MATH-500 和 HumanEval 的 chain-of-thought 基线 | MATH validate20、MATH validate50、MATH full test 486 题；HumanEval validate20、HumanEval full test 131 题 | 已完成 | 无 |
| MATH 多智能体 workflow | 设计 workflow，并证明优于 direct 和 CoT | `manual_v1` 已跑 MATH validate20、validate50 和 full test；full test 分数 `0.91770`，高于 direct `0.88889` 和 CoT `0.89300` | full test 已完成 | 无 |
| HumanEval 多智能体 workflow | 设计 workflow，并证明优于 base model | `manual_v1` 已跑 HumanEval full test；分数 `0.98473`，高于 direct `0.97710`，持平 CoT `0.98473` | 已完成，可写入报告 | 无 |
| Ablation 消融 | 对最终 workflow 做简化版对比 | MATH `ablation_single`；HumanEval `ablation_no_public_test` | 已完成 | 无 |
| Full benchmark comparison | 尽可能全量比较 direct、CoT、workflow、ablation | HumanEval 全量完成；MATH direct/CoT/`manual_v1` 全量完成；MATH ablation 完成 validate50 | 核心 full benchmark 完成 | full ablation 仅作可选扩展 |
| Token/efficiency analysis | 统计调用量、token 和精度/成本权衡 | `report/tables/efficiency_summary.md` 和 `report/tables/api_budget_summary.md` 已生成 | 已完成 | 无 |
| Report/package | PDF 报告、代码、证据、提交 zip | 默认 PDF、证据、package builder、package verifier、默认 zip 都已准备 | 默认包完成 | 最终提交前需要姓名、学号、邮箱 |

## 执行命令与证据矩阵

| 作业要求 | 已执行/应执行命令 | 当前产物和证据 | 是否还要跑 |
| --- | --- | --- | --- |
| MATH direct baseline | `python experiments/run_baselines.py --dataset MATH --baseline direct --split test --max-concurrency 4` | `report/tables/math_test_baselines.md`、`report/evidence/math_test_baselines/direct/` | 不需要 |
| MATH CoT baseline | `python experiments/run_baselines.py --dataset MATH --baseline cot --split test --max-concurrency 4` | `report/tables/math_test_baselines.md`、`report/evidence/math_test_baselines/cot/` | 不需要 |
| HumanEval direct baseline | `python experiments/run_baselines.py --dataset HumanEval --baseline direct --split test --max-concurrency 8` | `report/tables/humaneval_test_results.md`、`report/evidence/humaneval_test/direct/` | 不需要 |
| HumanEval CoT baseline | `python experiments/run_baselines.py --dataset HumanEval --baseline cot --split test --max-concurrency 8` | `report/tables/humaneval_test_results.md`、`report/evidence/humaneval_test/cot/` | 不需要 |
| MATH workflow validation | `python experiments/run_workflows.py --dataset MATH --workflow manual_v1 --sample-size 50 --sample-seed 1 --max-concurrency 2` | `report/tables/math_validation50_results.md`、`report/evidence/math_validate50/manual_v1/` | 不需要；full test 已完成 |
| HumanEval workflow full test | `python experiments/run_workflows.py --dataset HumanEval --workflow manual_v1 --split test --max-concurrency 8` | `report/tables/humaneval_test_results.md`、`report/evidence/humaneval_test/manual_v1/` | 不需要 |
| MATH ablation | `python experiments/run_workflows.py --dataset MATH --workflow ablation_single --sample-size 50 --sample-seed 1 --max-concurrency 2` | `report/tables/math_validation50_results.md`、`report/evidence/math_validate50/ablation_single/` | 不需要，除非补 full ablation |
| HumanEval ablation | `python experiments/run_workflows.py --dataset HumanEval --workflow ablation_no_public_test --split test --max-concurrency 8` | `report/tables/humaneval_test_results.md`、`report/evidence/humaneval_test/ablation_no_public_test/` | 不需要 |
| Full MATH workflow test | `make resume-math-manual-chunk`，完成后 `make collect-math-manual-chunked` | `report/tables/math_test_manual_chunked.md`、`report/evidence/math_test_manual/manual_v1/`；`make summarize-math-manual-chunks` 显示 25/25 chunks 完成 | 不需要 |
| Local handoff verification | `make post-push-check` | audit、evidence verification、package verification、GitHub sync 均通过；只保留学生 metadata warning | 每次关键 commit 后重跑 |
| Final course package | `make finalize-submission FINAL_NAME=... FINAL_STUDENT_ID=... FINAL_EMAIL=...` | 默认 zip 已可生成和验证；最终命名 zip 需要真实 metadata | 需要姓名、学号、邮箱 |

说明：MATH 表格使用 `experiments/collect_results.py --rescore-math` 的当前 evaluator 重新评分；`report/evidence/` 中部分 CSV 文件名和 `raw_average_score` 反映的是原始 AFlow 评分，不是最终报告采用的重评分数。

## 矩阵校验

每次修改这个文件或重生成结果表后，运行：

```bash
make verify-requirement-matrix
```

该检查会把本文件的关键结果行和额度行对照 `report/tables/math_test_baselines.md`、`report/tables/math_test_manual_chunked.md`、`report/tables/math_validation50_results.md`、`report/tables/humaneval_test_results.md`、`report/tables/api_budget_summary.md`，并确认当前 full MATH `manual_v1` 状态已正确标记为完成。

## 额度使用矩阵

| 用途 | runs | calls | tokens | 估算 Kimi K2.5 成本 | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| 20-example validation experiments | 8 | 323 | 317,403 | CNY 3.73-4.20 | 小样本验证 direct、CoT、workflow、ablation |
| 3-example smoke and ablation checks | 8 | 48 | 62,563 | CNY 0.78-0.87 | 环境/API/格式 smoke test |
| HumanEval full test experiments | 4 | 958 | 607,392 | CNY 7.21-8.11 | HumanEval direct、CoT、`manual_v1`、ablation |
| MATH 50-example validation experiments | 4 | 450 | 542,051 | CNY 6.32-7.14 | MATH 50 题 direct、CoT、`manual_v1`、ablation |
| MATH full direct/CoT baselines | 2 | 972 | 884,182 | CNY 16.38-16.74 | MATH 486 题 direct 和 CoT 全量基线 |
| MATH full `manual_v1` workflow | 1 | 2,431 | 3,786,936 | CNY 38.73-45.36 | MATH 486 题 full workflow |
| Recorded subtotal | 27 | 5,182 | 6,200,527 | CNY 73.15-82.43 | 已记录 token 的主要实验 |
| Stopped MATH `manual_v1` attempt estimate | 1 | 75 | 104,855 | CNY 1.06-1.25 | 一次未产出最终 CSV 的 full workflow 尝试估算 |
| Recorded plus estimated stopped attempts | 28 | 5,257 | 6,305,382 | CNY 74.21-83.67 | 已记录和估算总量；没有剩余必跑 API 实验 |

## Requirement Matrix

| Assignment requirement | Expected run coverage | Completed run coverage | Status |
| --- | --- | --- | --- |
| Direct base-model baseline | Run direct prompting on MATH-500 and HumanEval | MATH validate20, MATH validate50, MATH full test 486 examples, HumanEval validate20, HumanEval full test 131 examples | Complete |
| CoT base-model baseline | Run chain-of-thought prompting on MATH-500 and HumanEval | MATH validate20, MATH validate50, MATH full test 486 examples, HumanEval validate20, HumanEval full test 131 examples | Complete |
| New MATH multi-agent workflow | Design and evaluate a workflow that improves over direct and CoT | `manual_v1` completed on MATH validate20, validate50, and full test; full-test score `0.91770` exceeds direct `0.88889` and CoT `0.89300` | Full test complete |
| New HumanEval multi-agent workflow | Design and evaluate a workflow that improves over the base model | `manual_v1` completed on full HumanEval test; score `0.98473` exceeds direct `0.97710` and ties CoT `0.98473` | Complete enough for report; no-public-test ablation is best |
| Ablation experiments | Compare final workflow against reduced variants | MATH `ablation_single`; HumanEval `ablation_no_public_test` | Complete |
| Full benchmark comparison | Compare direct, CoT, workflow, and ablations where feasible | HumanEval full comparison complete; MATH full direct, CoT, and `manual_v1` complete; MATH full ablation remains optional | Core full comparison complete |
| Token and efficiency analysis | Track calls, tokens, and score/cost tradeoffs | `report/tables/efficiency_summary.md` reports call and token multipliers | Complete |
| API budget accounting | Explain historical quota usage and remaining quota needs | `report/tables/api_budget_summary.md` summarizes recorded usage, stopped-run estimate, and notes that no required API run remains | Complete |
| Failure analysis | Explain where workflows fix or regress against baselines | MATH validate50 failure analysis and HumanEval full-test failure analysis complete | Complete |
| Report and package | Produce a PDF report, code, evidence, and submission package | `report/main.pdf`, tracked evidence, package builder, package verifier, and default zip exist | Default package complete; final named package needs metadata |

## Key Result Matrix

| Dataset | Method | Split and size | Score | Calls | Tokens | Evidence |
| --- | --- | --- | --- | ---: | ---: | --- |
| MATH | direct | test, 486 | `0.88889` | 486 | 425,052 | `report/tables/math_test_baselines.md` |
| MATH | CoT | test, 486 | `0.89300` | 486 | 459,130 | `report/tables/math_test_baselines.md` |
| MATH | `manual_v1` | test, 486 | `0.91770` | 2,431 | 3,786,936 | `report/tables/math_test_manual_chunked.md` |
| MATH | direct | validate, 50 | `0.96000` | 50 | 38,140 | `report/tables/math_validation50_results.md` |
| MATH | CoT | validate, 50 | `0.94000` | 50 | 39,806 | `report/tables/math_validation50_results.md` |
| MATH | `manual_v1` | validate, 50 | `0.98000` | 250 | 349,515 | `report/tables/math_validation50_results.md` |
| MATH | `ablation_single` | validate, 50 | `0.94000` | 100 | 114,590 | `report/tables/math_validation50_results.md` |
| HumanEval | direct | test, 131 | `0.97710` | 131 | 48,941 | `report/tables/humaneval_test_results.md` |
| HumanEval | CoT | test, 131 | `0.98473` | 131 | 120,573 | `report/tables/humaneval_test_results.md` |
| HumanEval | `manual_v1` | test, 131 | `0.98473` | 287 | 134,751 | `report/tables/humaneval_test_results.md` |
| HumanEval | `ablation_no_public_test` | test, 131 | `0.99237` | 409 | 303,127 | `report/tables/humaneval_test_results.md` |

## Remaining Submission Step

No required API run remains for the assignment experiments. The full MATH `manual_v1` test run is complete on 486 examples with score `0.91770`, 2,431 LLM calls, 3,786,936 tracked tokens, and 25/25 chunks 完成.

The remaining required submission step is to fill real student metadata and rebuild the final named package:

```bash
make ready-to-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```
