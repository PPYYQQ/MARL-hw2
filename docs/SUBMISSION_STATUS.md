# Submission Status

This document tracks what is ready for submission, what is reproducible, and what still needs external support.

## Current Deliverables

- `AGENTS.md`: coding-agent guide with assignment overview, expected architecture, implementation plan, and testing plan.
- `README.md`: top-level repository entry point with current results, quick checks, evidence location, and blockers.
- `Makefile`: local shortcuts for compile checks, evidence verification, audit, evidence refresh, and packaging.
- `AFlow/`: imported AFlow codebase with Kimi-compatible async LLM configuration support.
- `experiments/run_baselines.py`: reproducible direct and CoT baseline runner.
- `experiments/run_workflows.py`: reproducible manual workflow runner.
- `experiments/run_chunked_workflows.py`: checkpointed workflow runner for expensive full-test jobs.
- `experiments/collect_results.py`: result table collection and MATH rescoring utility.
- `experiments/analyze_efficiency.py`: token-efficiency summary utility.
- `experiments/estimate_math_manual_test.py`: estimates full MATH `manual_v1` resource needs from tracked evidence.
- `experiments/export_evidence.py`: copies cited run artifacts into tracked report evidence.
- `experiments/verify_evidence.py`: verifies tracked evidence against cited scores, row counts, calls, and token totals.
- `experiments/fill_report_metadata.py`: fills author name, student ID, and email when provided.
- `experiments/finalize_submission.py`: orchestrates final metadata fill, PDF rebuild, and named zip packaging.
- `experiments/analyze_math_failures.py`: problem-level MATH run comparison utility.
- `experiments/analyze_humaneval_failures.py`: problem-level HumanEval run comparison utility.
- `experiments/audit_submission.py`: no-API submission readiness checker.
- `experiments/package_submission.py`: tracked-file submission zip builder with optional student/name/assignment output naming.
- `experiments/verify_submission_package.py`: validates generated zip contents against tracked files, manifest commit, PDF inclusion, manifest checksums, zero-failure audit summary, and secret hygiene.
- `docs/COMPLETION_AUDIT.md`: requirement-by-requirement handoff audit with evidence paths and remaining external inputs.
- `docs/EXPERIMENT_COMMANDS.md`: command ledger for API runs, table generation, analysis, evidence export, audit, and packaging.
- `docs/PAPER_NOTES.md`: notes linking AFlow and multi-agent debate ideas to the implemented workflows.
- `report/main.tex`: ICML-style draft report with current methods and result tables.
- `report/main.pdf`: locally compiled report PDF, included in generated submission packages when present.
- `report/evidence/`: raw CSV/config/log/token-summary evidence for the cited final runs.
- `PROGRESS.md`: chronological implementation and experiment log.
- Report coverage includes research context, AFlow engineering structure, environment setup, baseline prompts, workflow algorithm details, validation/test results, ablations, failure analysis, efficiency analysis, limitations, and remaining blockers.

## Current Results

- MATH 20-sample validation: direct `0.90000`, CoT `0.95000`, `manual_v1` `1.00000`, single-candidate ablation `0.90000`.
- MATH 50-sample validation: direct `0.96000`, CoT `0.94000`, `manual_v1` `0.98000`, single-candidate ablation `0.94000`.
- MATH 50-sample failure analysis: `manual_v1` fixes two of three CoT failures with no CoT-relative regressions; the remaining failure is index `91`, missed by every compared method.
- HumanEval full test: direct `0.97710`, CoT `0.98473`, `manual_v1` `0.98473`, no-public-test ablation `0.99237`.
- HumanEval full-test failure analysis: CoT, `manual_v1`, and no-public-test all fix the three direct failures; no-public-test has the fewest regressions against direct.
- MATH full test baselines: direct `0.88889`, CoT `0.89300`.
- Efficiency summary: MATH 50-sample `manual_v1` gains `+0.02000` over direct at `9.16x` tokens; HumanEval no-public-test gains `+0.01527` at `6.19x` tokens.
- MATH full `manual_v1` estimate: about `2,430` LLM calls and `3.40M` raw tokens for 486 test examples, split into 25 chunks at chunk size 20.
- Evidence verification: all 10 tracked cited runs in `report/evidence/` reproduce their expected rows, scores, call counts, and token totals.

## Reproducibility Commands

Use the dedicated environment:

```bash
make py-compile
```

Expanded command:

```bash
conda run -n marl_hw2 python -m py_compile \
  experiments/run_baselines.py \
  experiments/run_workflows.py \
  experiments/run_chunked_workflows.py \
  experiments/collect_results.py \
  experiments/analyze_efficiency.py \
  experiments/estimate_math_manual_test.py \
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

Dry-run the checkpointed MATH workflow plan without calling the API:

```bash
conda run -n marl_hw2 python experiments/run_chunked_workflows.py \
  --dataset MATH \
  --workflow manual_v1 \
  --split test \
  --chunk-size 20 \
  --run-id dry-run-check \
  --max-chunks 1 \
  --dry-run
```

Verify the full MATH `manual_v1` chunk plan without calling the API:

```bash
make verify-math-manual-plan
```

Run the no-API submission audit:

```bash
make final-check
```

Audit only:

```bash
conda run -n marl_hw2 python experiments/audit_submission.py
```

The audit is expected to warn until the Kimi quota, report metadata, and full MATH `manual_v1` test run are resolved.

Build the report PDF with Tectonic:

```bash
make build-report
```

Verify that the local report PDF is current for its TeX sources:

```bash
make verify-report-pdf
```

Refresh tracked evidence files from local ignored run directories:

```bash
make refresh-evidence
```

Expanded commands:

```bash
conda run -n marl_hw2 python experiments/export_evidence.py --clean
conda run -n marl_hw2 python experiments/verify_evidence.py --output report/tables/evidence_verification.md
```

See `docs/EXPERIMENT_COMMANDS.md` for the full command ledger behind the cited results and submission package.

Fill report author metadata before final packaging:

```bash
conda run -n marl_hw2 python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

Preview the final zip contents:

```bash
make package-dry-run
```

Expanded command:

```bash
conda run -n marl_hw2 python experiments/package_submission.py --dry-run
```

Verify the generated default zip:

```bash
make verify-package
```

Create and verify the default zip in one command:

```bash
make final-package-check
```

After filling report metadata, preview the course-style named zip:

```bash
conda run -n marl_hw2 python experiments/package_submission.py --student-id "Your ID" --name "Your Name" --assignment "MARL-hw2" --dry-run
```

After metadata is known, run finalization in one command:

```bash
conda run -n marl_hw2 python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com" --assignment "MARL-hw2"
```

This command verifies the generated zip and restores local `report/main.tex` and `report/main.pdf` placeholders after packaging by default, while the generated zip retains the filled report source and PDF. Pass `--keep-filled-report` only if you intentionally want local report artifacts to stay filled.
The generated zip verification also checks that `report/main.tex` inside the archive contains the provided name, student ID, and email instead of placeholders.
Default packaging refuses uncommitted tracked changes; finalization only permits the temporary `report/main.tex` metadata edit.

After Kimi quota is restored, resume the missing full MATH workflow evaluation:

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

Rerun the same command to process the next incomplete chunk. Remove `--max-chunks 1` to run continuously.

## Known Blockers

- New Kimi API calls currently fail with an insufficient-balance quota error.
- Full MATH `manual_v1` test results are therefore not available yet.
- `report/main.tex` still contains placeholder student name, student ID, and email fields; use `experiments/fill_report_metadata.py` after those values are known.

## Next Actions

1. Recharge the Kimi account or provide another valid `KIMI_API_KEY`.
2. Resume full MATH `manual_v1` with the chunked runner.
3. Collect the chunked MATH result table after enough chunks complete.
4. Run `experiments/finalize_submission.py --name ... --student-id ... --email ...` to fill metadata, rebuild the PDF, and create the final named zip.
