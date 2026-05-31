# Chunked Workflow Runs

Use `experiments/run_chunked_workflows.py` for expensive workflow evaluations that should survive API stalls or local interruptions.

## Why

The full MATH `manual_v1` test run can require thousands of LLM calls. A monolithic run may keep partial results only in memory until the final CSV is written. The chunked runner evaluates small index batches, writes each chunk's CSV and `chunk_config.json`, and refreshes an aggregate `run_config.json` after every completed chunk.

Generated chunk outputs are ignored under `experiments/chunked_runs/`.

## Dry Run

```bash
python experiments/run_chunked_workflows.py \
  --dataset MATH \
  --workflow manual_v1 \
  --split test \
  --chunk-size 20 \
  --run-id math-test-manual-v1 \
  --dry-run
```

## Full MATH Manual Workflow

```bash
python experiments/run_chunked_workflows.py \
  --dataset MATH \
  --workflow manual_v1 \
  --split test \
  --chunk-size 20 \
  --max-concurrency 2 \
  --run-id math-test-manual-v1
```

To resume, rerun the same command with the same `--run-id`. Completed chunks are skipped.

For controlled batches, add `--max-chunks`:

```bash
python experiments/run_chunked_workflows.py \
  --dataset MATH \
  --workflow manual_v1 \
  --split test \
  --chunk-size 20 \
  --max-concurrency 2 \
  --run-id math-test-manual-v1 \
  --max-chunks 1
```

Rerun the command to pick up the next incomplete chunk, or use `--start-chunk` to jump to a later chunk.

If the API returns quota or insufficient-balance errors for every item in a chunk, the chunk is marked `failed_quota` rather than `completed`, and the runner stops without counting that chunk in the aggregate.

## Summarize

```bash
python experiments/collect_results.py \
  --runs-dir experiments/chunked_runs \
  --latest-only \
  --rescore-math \
  --dataset MATH \
  --split test \
  --output report/tables/math_test_manual_chunked.md
```
