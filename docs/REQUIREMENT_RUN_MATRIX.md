# Requirement Run Matrix

This document maps the assignment's required experiments to the runs completed in this repository. It is meant as a quick answer to: what the homework asks for, what has been run, and what remains blocked by external inputs.

## Requirement Matrix

| Assignment requirement | Expected run coverage | Completed run coverage | Status |
| --- | --- | --- | --- |
| Direct base-model baseline | Run direct prompting on MATH-500 and HumanEval | MATH validate20, MATH validate50, MATH full test 486 examples, HumanEval validate20, HumanEval full test 131 examples | Complete |
| CoT base-model baseline | Run chain-of-thought prompting on MATH-500 and HumanEval | MATH validate20, MATH validate50, MATH full test 486 examples, HumanEval validate20, HumanEval full test 131 examples | Complete |
| New MATH multi-agent workflow | Design and evaluate a workflow that improves over direct and CoT | `manual_v1` completed on MATH validate20 and validate50; validate50 score `0.98000` exceeds direct `0.96000` and CoT `0.94000` | Validation complete; full test pending quota |
| New HumanEval multi-agent workflow | Design and evaluate a workflow that improves over the base model | `manual_v1` completed on full HumanEval test; score `0.98473` exceeds direct `0.97710` and ties CoT `0.98473` | Complete enough for report; no-public-test ablation is best |
| Ablation experiments | Compare final workflow against reduced variants | MATH `ablation_single`; HumanEval `ablation_no_public_test` | Complete |
| Full benchmark comparison | Compare direct, CoT, workflow, and ablations where feasible | HumanEval full comparison complete; MATH full direct and CoT complete; MATH workflow full test not complete | Partially blocked by Kimi quota |
| Token and efficiency analysis | Track calls, tokens, and score/cost tradeoffs | `report/tables/efficiency_summary.md` reports call and token multipliers | Complete |
| API budget accounting | Explain historical quota usage and remaining quota needs | `report/tables/api_budget_summary.md` summarizes recorded usage, stopped-run estimate, and remaining full MATH budget | Complete |
| Failure analysis | Explain where workflows fix or regress against baselines | MATH validate50 failure analysis and HumanEval full-test failure analysis complete | Complete |
| Report and package | Produce a PDF report, code, evidence, and submission package | `report/main.pdf`, tracked evidence, package builder, package verifier, and default zip exist | Default package complete; final named package needs metadata |

## Key Result Matrix

| Dataset | Method | Split and size | Score | Calls | Tokens | Evidence |
| --- | --- | --- | --- | ---: | ---: | --- |
| MATH | direct | test, 486 | `0.88889` | 486 | 425,052 | `report/tables/math_test_baselines.md` |
| MATH | CoT | test, 486 | `0.89300` | 486 | 459,130 | `report/tables/math_test_baselines.md` |
| MATH | direct | validate, 50 | `0.96000` | 50 | 38,140 | `report/tables/math_validation50_results.md` |
| MATH | CoT | validate, 50 | `0.94000` | 50 | 39,806 | `report/tables/math_validation50_results.md` |
| MATH | `manual_v1` | validate, 50 | `0.98000` | 250 | 349,515 | `report/tables/math_validation50_results.md` |
| MATH | `ablation_single` | validate, 50 | `0.94000` | 100 | 114,590 | `report/tables/math_validation50_results.md` |
| HumanEval | direct | test, 131 | `0.97710` | 131 | 48,941 | `report/tables/humaneval_test_results.md` |
| HumanEval | CoT | test, 131 | `0.98473` | 131 | 120,573 | `report/tables/humaneval_test_results.md` |
| HumanEval | `manual_v1` | test, 131 | `0.98473` | 287 | 134,751 | `report/tables/humaneval_test_results.md` |
| HumanEval | `ablation_no_public_test` | test, 131 | `0.99237` | 409 | 303,127 | `report/tables/humaneval_test_results.md` |

## Remaining Run

The main missing experiment is the full MATH `manual_v1` test run on 486 examples. It was estimated from the 50-example validation run at about 2,430 LLM calls and 3.40M raw tokens. The checkpointed runner is ready, but the current Kimi account returns an insufficient-balance quota error for new API calls.

Resume one chunk after quota is restored:

```bash
conda run -n marl_hw2 python experiments/run_chunked_workflows.py \
  --dataset MATH \
  --workflow manual_v1 \
  --split test \
  --chunk-size 20 \
  --max-concurrency 2 \
  --run-id math-test-manual-v1 \
  --max-chunks 1
```
