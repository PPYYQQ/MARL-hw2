# Experiments

This folder contains reproducible helpers for assignment experiments. Generated run outputs go under `experiments/runs/` and `experiments/chunked_runs/`, which are ignored by Git.

For the final cited runs and submission commands, see `docs/EXPERIMENT_COMMANDS.md`.

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

Run expensive workflows in checkpointed chunks:

```bash
python experiments/run_chunked_workflows.py --dataset MATH --workflow manual_v1 --split test --chunk-size 20 --max-concurrency 2 --run-id math-test-manual-v1
```

Verify the full MATH chunk plan before spending API quota:

```bash
python experiments/verify_chunked_plan.py --dataset MATH --split test --chunk-size 20 --expect-total-indices 486 --expect-total-chunks 25 --expect-first-index 0 --expect-last-index 485 --expect-contiguous
```

If the command is interrupted, rerun the same command with the same `--run-id`; completed chunks are skipped and the aggregate CSV/config are refreshed after each chunk.
Use `--max-chunks 1` for controlled incremental batches.

After runs finish:

```bash
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --output report/tables/experiment_summary.md
```

The summary table is intended for the report, but always verify the underlying CSV files before citing results.
Use `--rescore-math` when citing MATH results so saved predictions are scored with the current MATH answer normalizer.
Use `--dataset` and `--sample-size` to keep tables for different validation subsets reproducible, for example:

```bash
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --sample-size 20 --output report/tables/validation20_results.md
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --dataset MATH --sample-size 50 --output report/tables/math_validation50_results.md
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --dataset MATH --split test --output report/tables/math_test_baselines.md
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --dataset HumanEval --split test --output report/tables/humaneval_test_results.md
python experiments/collect_results.py --runs-dir experiments/chunked_runs --latest-only --rescore-math --dataset MATH --split test --output report/tables/math_test_manual_chunked.md
```

After collecting the full MATH `manual_v1` chunked result, verify the table and the report before final packaging:

```bash
make verify-math-manual-result
make verify-final-report-ready
```

Each new run also writes `llm_usage.json` next to `run_config.json`, with raw input/output token counts and call history. Prefer raw token counts over the `total_cost` field until Kimi pricing is added and verified.

Summarize score and token-efficiency tradeoffs from tracked result tables:

```bash
python experiments/analyze_efficiency.py --output report/tables/efficiency_summary.md
python experiments/analyze_api_budget.py --output report/tables/api_budget_summary.md
```

Export raw evidence for the cited result runs:

```bash
python experiments/export_evidence.py --clean
python experiments/verify_evidence.py --output report/tables/evidence_verification.md
```

Fill final report metadata:

```bash
python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

For final packaging, prefer `make finalize-submission-dry-run` and `make finalize-submission` so the filled report source, rebuilt PDF, named zip, and metadata verification stay in one path.

Compare saved MATH runs at the problem level:

```bash
python experiments/analyze_math_failures.py \
  --baseline cot \
  --run direct=experiments/runs/MATH/direct/20260531_001748 \
  --run cot=experiments/runs/MATH/cot/20260531_001748 \
  --run manual_v1=experiments/runs/MATH/manual_v1/20260531_002230 \
  --run single=experiments/runs/MATH/ablation_single/20260531_002230 \
  --output report/tables/math_validation50_failure_analysis.md
```

Compare saved HumanEval runs at the problem level:

```bash
python experiments/analyze_humaneval_failures.py \
  --baseline direct \
  --run direct=experiments/runs/HumanEval/direct/20260531_004920 \
  --run cot=experiments/runs/HumanEval/cot/20260531_004920 \
  --run manual_v1=experiments/runs/HumanEval/manual_v1/20260531_005625 \
  --run no_public=experiments/runs/HumanEval/ablation_no_public_test/20260531_005625 \
  --output report/tables/humaneval_test_failure_analysis.md
```

Run the local submission audit without making API calls:

```bash
python experiments/audit_submission.py
```

Verify the assignment run matrix against tracked result and budget tables:

```bash
python experiments/verify_requirement_matrix.py
```

Use `--strict` before final packaging when the Kimi quota, student metadata, and local PDF build blockers have been resolved.

Run the maintained Make gates before handoff or final submission:

```bash
make handoff-check
make post-push-check
make verify-requirement-matrix
make current-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
make ready-to-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

Use `current-submit-check` for the current known-blocker package after real metadata is available. Use `ready-to-submit-check` only after the full MATH `manual_v1` table is generated, tracked, and reflected in the report.

Create a submission zip from tracked files and an optional `report/main.pdf`:

```bash
python experiments/package_submission.py --dry-run
python experiments/package_submission.py
```
