# Experiments

This folder contains reproducible helpers for assignment experiments. Generated run outputs go under `experiments/runs/`, which is ignored by Git.

## Kimi Config

Create the local AFlow config from the safe example:

```bash
cp AFlow/config/config2.kimi.example.yaml AFlow/config/config2.yaml
export KIMI_API_KEY=...
```

The example uses the OpenAI-compatible Kimi endpoint and keeps the API key in the `KIMI_API_KEY` environment variable.

## Baselines

Run a tiny MATH smoke test:

```bash
python experiments/run_baselines.py --dataset MATH --baseline direct --sample-size 3 --max-concurrency 1
python experiments/run_baselines.py --dataset MATH --baseline cot --sample-size 3 --max-concurrency 1
```

Run a tiny HumanEval smoke test:

```bash
python experiments/run_baselines.py --dataset HumanEval --baseline direct --sample-size 3 --max-concurrency 1
python experiments/run_baselines.py --dataset HumanEval --baseline cot --sample-size 3 --max-concurrency 1
```

Use `--data-path` if the downloaded dataset is not at AFlow's default path. Keep full runs until after smoke tests confirm formatting and cost.

## Result Summary

Run the manual workflow after baseline smoke tests:

```bash
python experiments/run_workflows.py --dataset MATH --workflow manual_v1 --sample-size 3 --max-concurrency 1
python experiments/run_workflows.py --dataset HumanEval --workflow manual_v1 --sample-size 3 --max-concurrency 1
```

Run ablation workflows on the same sampled indices:

```bash
python experiments/run_workflows.py --dataset MATH --workflow ablation_single --sample-size 3 --sample-seed 1 --max-concurrency 1
python experiments/run_workflows.py --dataset HumanEval --workflow ablation_no_public_test --sample-size 3 --sample-seed 1 --max-concurrency 1
```

Run the current 20-sample validation subset:

```bash
python experiments/run_baselines.py --dataset MATH --baseline direct --sample-size 20 --sample-seed 1 --max-concurrency 4
python experiments/run_baselines.py --dataset MATH --baseline cot --sample-size 20 --sample-seed 1 --max-concurrency 4
python experiments/run_baselines.py --dataset HumanEval --baseline direct --sample-size 20 --sample-seed 1 --max-concurrency 4
python experiments/run_baselines.py --dataset HumanEval --baseline cot --sample-size 20 --sample-seed 1 --max-concurrency 4
python experiments/run_workflows.py --dataset MATH --workflow manual_v1 --sample-size 20 --sample-seed 1 --max-concurrency 2
python experiments/run_workflows.py --dataset MATH --workflow ablation_single --sample-size 20 --sample-seed 1 --max-concurrency 2
python experiments/run_workflows.py --dataset HumanEval --workflow manual_v1 --sample-size 20 --sample-seed 1 --max-concurrency 4
python experiments/run_workflows.py --dataset HumanEval --workflow ablation_no_public_test --sample-size 20 --sample-seed 1 --max-concurrency 4
```

After runs finish:

```bash
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --output report/tables/experiment_summary.md
```

The summary table is intended for the report, but always verify the underlying CSV files before citing results.
Use `--rescore-math` when citing MATH results so saved predictions are scored with the current text and list-answer normalizer.
Each new run also writes `llm_usage.json` next to `run_config.json`, with raw input/output token counts and call history. Prefer raw token counts over the `total_cost` field until Kimi pricing is added and verified.
