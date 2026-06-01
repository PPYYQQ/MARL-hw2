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
- `experiments/analyze_api_budget.py`: summarizes recorded Kimi token usage, estimated stopped-run usage, and remaining full MATH `manual_v1` budget.
- `experiments/estimate_math_manual_test.py`: estimates full MATH `manual_v1` resource needs from tracked evidence.
- `experiments/verify_chunked_plan.py`: verifies the planned full MATH `manual_v1` chunks without API calls.
- `experiments/verify_result_table.py`: verifies that a collected Markdown result table contains an expected experiment row.
- `experiments/verify_final_report_ready.py`: verifies that the final report reflects the completed full MATH `manual_v1` result.
- `experiments/verify_report_pdf.py`: verifies that the local report PDF is current for tracked TeX sources.
- `experiments/verify_audit_warnings.py`: verifies that submission-audit warnings are limited to known external blockers.
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
- `docs/REQUIREMENT_RUN_MATRIX.md`: matrix of assignment-required experiment coverage, completed runs, remaining gaps, and evidence files.
- `docs/FINAL_HANDOFF_CN.md`: Chinese final handoff checklist covering what can be submitted now, what external inputs remain, and exact final commands.
- `docs/KIMI_QUOTA_RECOVERY_CN.md`: Chinese low-risk recharge and resume runbook for the remaining full MATH workflow.
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
- MATH 50-sample failure analysis: `manual_v1` fixes two of three CoT failures with no CoT-relative regressions; the remaining failure is index `91`, missed by every compared method and classified as a reasoning error rather than a rescoring issue.
- HumanEval full test: direct `0.97710`, CoT `0.98473`, `manual_v1` `0.98473`, no-public-test ablation `0.99237`.
- HumanEval full-test failure analysis: CoT, `manual_v1`, and no-public-test all fix the three direct failures; no-public-test has the fewest regressions against direct.
- MATH full test baselines: direct `0.88889`, CoT `0.89300`.
- Efficiency summary: MATH 50-sample `manual_v1` gains `+0.02000` over direct at `9.16x` tokens; HumanEval no-public-test gains `+0.01527` at `6.19x` tokens.
- API budget summary: recorded runs use `2.41M` tracked tokens; the remaining full MATH `manual_v1` run is estimated at `3.40M` tokens and about `CNY 34-41` before retry margin.
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
  experiments/analyze_api_budget.py \
  experiments/estimate_math_manual_test.py \
  experiments/summarize_chunked_run.py \
  experiments/verify_chunked_plan.py \
  experiments/verify_result_table.py \
  experiments/verify_final_report_ready.py \
  experiments/verify_report_pdf.py \
  experiments/verify_audit_warnings.py \
  experiments/export_evidence.py \
  experiments/verify_evidence.py \
  experiments/verify_git_sync.py \
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

Verify that audit warnings are limited to the known external blockers:

```bash
make verify-known-warnings
```

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

Package verification checks tracked entries, optional PDF inclusion, manifest commit, per-file SHA-256 checksums, the embedded zero-failure audit summary, and forbidden secret/run paths.

Create and verify the default zip in one command:

```bash
make final-package-check
```

Run all local no-API handoff gates:

```bash
make handoff-check
```

This also fails if `experiments/audit_submission.py` emits any warning outside the maintained known-blocker allowlist.

Print a shorter current-status snapshot:

```bash
make status-summary
```

After pushing a key commit, verify that the local branch matches its GitHub upstream:

```bash
make verify-github-sync
```

After the final handoff commit is pushed, run the package/audit gates plus GitHub sync in one command:

```bash
make post-push-check
```

After the full MATH `manual_v1` result table is tracked in Git and real metadata is available, run the final submission gate:

```bash
make ready-to-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

After filling report metadata, preview the course-style named zip:

```bash
conda run -n marl_hw2 python experiments/package_submission.py --student-id "Your ID" --name "Your Name" --assignment "MARL-hw2" --dry-run
```

After metadata is known, run finalization in one command:

```bash
conda run -n marl_hw2 python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com" --assignment "MARL-hw2"
```

Equivalent Make shortcut:

```bash
make finalize-submission FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

Preview the same final Make command with real metadata without writing files:

```bash
make finalize-submission-dry-run FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

Preview the finalization sequence with test metadata:

```bash
make finalize-dry-run
```

This command verifies the generated zip and restores local `report/main.tex` and `report/main.pdf` placeholders after packaging by default, while the generated zip retains the filled report source and PDF. Pass `--keep-filled-report` only if you intentionally want local report artifacts to stay filled.
The generated zip verification also checks that `report/main.tex` inside the archive contains the provided name, student ID, and email instead of placeholders.
Default packaging refuses uncommitted tracked changes; finalization only permits the temporary `report/main.tex` metadata edit.
Finalization refuses to start if any tracked file already has uncommitted changes.
Finalization also rejects placeholder/example metadata such as `Your Name`, `Your ID`, `you@example.com`, `Test Student`, `TEST123`, and `test@example.com` for real writes; the built-in `make finalize-dry-run` path allows the test values only because it writes no files.

After Kimi quota is restored, resume the missing full MATH workflow evaluation:

```bash
make resume-math-manual-chunk
```

Use `docs/KIMI_QUOTA_RECOVERY_CN.md` for the full step-by-step sequence before increasing `MATH_MANUAL_MAX_CHUNKS`.

Check current chunked MATH progress without making API calls:

```bash
make summarize-math-manual-chunks
```

The summary also prints the next non-completed chunk and the suggested follow-up Make command.

Rerun the same command to process the next incomplete chunk. Override `MATH_MANUAL_MAX_CHUNKS` to process more chunks in one invocation.

After enough chunks complete, refresh the local result table:

```bash
make collect-math-manual-chunked
```

Verify the collected full MATH `manual_v1` table before final submission:

```bash
make verify-math-manual-result
```

This gate checks the 486-example row and requires a plausible full-run budget by default: at least `2400` calls and `2500000` tokens.

Verify the report has been updated from pending-run language to the completed full-test result:

```bash
make verify-final-report-ready
```

## Known Blockers

- New Kimi API calls currently fail with an insufficient-balance quota error; the current budget estimate recommends at least CNY 50 before resuming the missing run.
- Full MATH `manual_v1` test results are therefore not available yet.
- `report/main.tex` still contains placeholder student name, student ID, and email fields; use `experiments/fill_report_metadata.py` after those values are known.

## Next Actions

1. Recharge the Kimi account or provide another valid `KIMI_API_KEY`.
2. Resume full MATH `manual_v1` with the chunked runner.
3. Collect the chunked MATH result table after enough chunks complete.
4. Run `experiments/finalize_submission.py --name ... --student-id ... --email ...` to fill metadata, rebuild the PDF, and create the final named zip.
