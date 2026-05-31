# Experiment Commands

This document records the commands behind the report tables and evidence files. Commands that call Kimi require a valid `KIMI_API_KEY` and available account balance. Post-processing commands are local and do not call the API.

## Environment

```bash
make py-compile
```

Equivalent expanded command:

```bash
conda run -n marl_hw2 python -m py_compile \
  experiments/run_baselines.py \
  experiments/run_workflows.py \
  experiments/run_chunked_workflows.py \
  experiments/collect_results.py \
  experiments/analyze_efficiency.py \
  experiments/estimate_math_manual_test.py \
  experiments/verify_chunked_plan.py \
  experiments/export_evidence.py \
  experiments/verify_evidence.py \
  experiments/fill_report_metadata.py \
  experiments/finalize_submission.py \
  experiments/analyze_math_failures.py \
  experiments/analyze_humaneval_failures.py \
  experiments/audit_submission.py \
  experiments/package_submission.py \
  experiments/verify_submission_package.py \
  AFlow/benchmarks/math.py
```

## API Runs

MATH 50-sample validation:

```bash
python experiments/run_baselines.py --dataset MATH --baseline direct --sample-size 50 --sample-seed 1 --max-concurrency 4
python experiments/run_baselines.py --dataset MATH --baseline cot --sample-size 50 --sample-seed 1 --max-concurrency 4
python experiments/run_workflows.py --dataset MATH --workflow manual_v1 --sample-size 50 --sample-seed 1 --max-concurrency 2
python experiments/run_workflows.py --dataset MATH --workflow ablation_single --sample-size 50 --sample-seed 1 --max-concurrency 2
```

HumanEval full test:

```bash
python experiments/run_baselines.py --dataset HumanEval --baseline direct --split test --max-concurrency 8
python experiments/run_baselines.py --dataset HumanEval --baseline cot --split test --max-concurrency 8
python experiments/run_workflows.py --dataset HumanEval --workflow manual_v1 --split test --max-concurrency 8
python experiments/run_workflows.py --dataset HumanEval --workflow ablation_no_public_test --split test --max-concurrency 8
```

MATH full test baselines:

```bash
python experiments/run_baselines.py --dataset MATH --baseline direct --split test --max-concurrency 4
python experiments/run_baselines.py --dataset MATH --baseline cot --split test --max-concurrency 4
```

Quota-safe MATH full workflow resume command:

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

## Report Tables

```bash
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --sample-size 20 --output report/tables/validation20_results.md
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --dataset MATH --sample-size 50 --output report/tables/math_validation50_results.md
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --dataset HumanEval --split test --output report/tables/humaneval_test_results.md
python experiments/collect_results.py --runs-dir experiments/runs --latest-only --rescore-math --dataset MATH --split test --output report/tables/math_test_baselines.md
python experiments/analyze_efficiency.py --output report/tables/efficiency_summary.md
python experiments/estimate_math_manual_test.py --output report/tables/math_manual_test_estimate.md
python experiments/verify_chunked_plan.py --dataset MATH --split test --chunk-size 20 --expect-total-indices 486 --expect-total-chunks 25 --expect-first-index 0 --expect-last-index 485 --expect-contiguous
python experiments/verify_evidence.py --output report/tables/evidence_verification.md
```

## Failure Analysis

```bash
python experiments/analyze_math_failures.py \
  --baseline cot \
  --run direct=experiments/runs/MATH/direct/20260531_001748 \
  --run cot=experiments/runs/MATH/cot/20260531_001748 \
  --run manual_v1=experiments/runs/MATH/manual_v1/20260531_002230 \
  --run single=experiments/runs/MATH/ablation_single/20260531_002230 \
  --output report/tables/math_validation50_failure_analysis.md

python experiments/analyze_humaneval_failures.py \
  --baseline direct \
  --run direct=experiments/runs/HumanEval/direct/20260531_004920 \
  --run cot=experiments/runs/HumanEval/cot/20260531_004920 \
  --run manual_v1=experiments/runs/HumanEval/manual_v1/20260531_005625 \
  --run no_public=experiments/runs/HumanEval/ablation_no_public_test/20260531_005625 \
  --output report/tables/humaneval_test_failure_analysis.md
```

## Evidence And Submission

Fill report metadata before final packaging:

```bash
python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

```bash
make refresh-evidence
make build-report
make verify-math-manual-plan
make final-check
make package
make verify-package
make final-package-check
```

Equivalent expanded commands:

```bash
python experiments/export_evidence.py --clean
python experiments/verify_evidence.py --output report/tables/evidence_verification.md
python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
cd report && conda run -n marl_hw2 tectonic main.tex
python experiments/audit_submission.py
python experiments/package_submission.py --student-id "Your ID" --name "Your Name" --assignment "MARL-hw2" --dry-run
python experiments/package_submission.py --student-id "Your ID" --name "Your Name" --assignment "MARL-hw2"
python experiments/verify_submission_package.py --package submission/MARL-hw2-submission.zip
python experiments/verify_submission_package.py --package "submission/Your_ID_Your_Name_MARL-hw2.zip" --expect-name "Your Name" --expect-student-id "Your ID" --expect-email "you@example.com"
```

`make final-package-check` is the default-package equivalent of running `make package` followed by `make verify-package`.
Default packaging refuses uncommitted tracked changes; use `experiments/finalize_submission.py` for the final filled-metadata archive because it allows only the temporary `report/main.tex` metadata edit.

Equivalent one-command finalization after metadata is known:

```bash
python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com" --assignment "MARL-hw2"
```
