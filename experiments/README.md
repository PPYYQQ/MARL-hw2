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

After runs finish:

```bash
python experiments/collect_results.py --runs-dir experiments/runs --output report/tables/experiment_summary.md
```

The summary table is intended for the report, but always verify the underlying CSV files before citing results.
