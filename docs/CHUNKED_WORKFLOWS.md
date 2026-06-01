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

Makefile shortcut:

```bash
make resume-math-manual-chunk
```

The shortcut defaults to `MATH_MANUAL_RUN_ID=math-test-manual-v1`, `MATH_MANUAL_CHUNK_SIZE=20`, `MATH_MANUAL_MAX_CONCURRENCY=2`, and `MATH_MANUAL_MAX_CHUNKS=1`. Override those variables if needed, for example:

```bash
make resume-math-manual-chunk MATH_MANUAL_MAX_CHUNKS=2
```

Preview the exact chunk plan without making API calls:

```bash
make dry-run-math-manual-chunks
```

Rerun the command to pick up the next incomplete chunk, or use `--start-chunk` to jump to a later chunk.

If the API returns quota or insufficient-balance errors for every item in a chunk, the chunk is marked `failed_quota` rather than `completed`, and the runner stops without counting that chunk in the aggregate.

## Resource Estimate

Generate the current full-test resource estimate from tracked evidence:

```bash
python experiments/estimate_math_manual_test.py --output report/tables/math_manual_test_estimate.md
```

The current estimate projects `2,430` LLM calls and about `3.40M` raw tokens for the full 486-example MATH test split, using 25 chunks at `--chunk-size 20`.

## Plan Check

Verify that the intended full-test command covers all 486 MATH test examples in 25 chunks before spending API quota:

```bash
make verify-math-manual-plan
```

Equivalent expanded command:

```bash
python experiments/verify_chunked_plan.py \
  --dataset MATH \
  --split test \
  --chunk-size 20 \
  --expect-total-indices 486 \
  --expect-total-chunks 25 \
  --expect-first-index 0 \
  --expect-last-index 485 \
  --expect-contiguous
```

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

Makefile shortcut:

```bash
make collect-math-manual-chunked
```
