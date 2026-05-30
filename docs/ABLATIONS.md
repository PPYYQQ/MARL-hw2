# Ablation Plan

The report needs ablations that separate workflow structure from the base model. Current tracked variants:

| Dataset | Workflow | Purpose |
| --- | --- | --- |
| MATH | `manual_v1` | Three independent solution candidates, self-consistency selection, final boxed-answer cleanup. |
| MATH | `ablation_single` | One solution candidate plus final boxed-answer cleanup; tests the value of multi-candidate generation and ensemble. |
| HumanEval | `manual_v1` | Two code candidates, public-test repair when tests are available, ensemble fallback. |
| HumanEval | `ablation_no_public_test` | Two code candidates plus ensemble, but no public-test repair; tests the value of execution feedback. |

Recommended low-cost validation commands:

```bash
conda run -n marl_hw2 python experiments/run_workflows.py --dataset MATH --workflow ablation_single --sample-size 3 --sample-seed 1 --max-concurrency 1
conda run -n marl_hw2 python experiments/run_workflows.py --dataset HumanEval --workflow ablation_no_public_test --sample-size 3 --sample-seed 1 --max-concurrency 1
```

Recommended larger validation commands after the low-cost checks:

```bash
conda run -n marl_hw2 python experiments/run_workflows.py --dataset MATH --workflow manual_v1 --sample-size 20 --sample-seed 2 --max-concurrency 1
conda run -n marl_hw2 python experiments/run_workflows.py --dataset MATH --workflow ablation_single --sample-size 20 --sample-seed 2 --max-concurrency 2
conda run -n marl_hw2 python experiments/run_workflows.py --dataset HumanEval --workflow manual_v1 --sample-size 20 --sample-seed 2 --max-concurrency 1
conda run -n marl_hw2 python experiments/run_workflows.py --dataset HumanEval --workflow ablation_no_public_test --sample-size 20 --sample-seed 2 --max-concurrency 2
```

Use the same sample seed across compared methods. Do not compare methods run on different sampled indices unless the report clearly labels them as smoke tests.
