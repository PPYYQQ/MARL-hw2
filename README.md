# MARL HW2: Multi-Agent Workflow Design with AFlow

This repository contains the implementation, experiment runners, evidence, and English final-report source for the multi-agent workflow assignment.

## What Is Included

- `AFlow/`: imported AFlow codebase plus local assignment workflow additions.
- `experiments/`: reproducible runners, table collectors, analysis utilities, audit checks, evidence export, and packaging helpers.
- `report/main.tex`: ICML-style English final-report source.
- `report/tables/`: tracked report tables and analysis summaries.
- `report/evidence/`: copied CSV/config/log/token-summary artifacts for the cited final runs.
- `docs/`: setup notes, ablation notes, experiment command ledger, paper notes, chunked-run guide, completion audit, and submission status.
- `docs/REQUIREMENT_RUN_MATRIX.md`: assignment requirement matrix showing required runs, completed runs, gaps, and evidence.
- `docs/FINAL_HANDOFF_CN.md`: Chinese final handoff checklist for submission metadata, completed experiment evidence, and final commands.
- `docs/KIMI_QUOTA_RECOVERY_CN.md`: Chinese runbook for reproducing or extending the checkpointed full MATH workflow.
- `PROGRESS.md`: chronological work log.

## Current Result Summary

- MATH 20-sample validation: `manual_v1` reaches `1.00000`, above CoT at `0.95000`.
- MATH 50-sample validation: `manual_v1` reaches `0.98000`, above direct at `0.96000` and CoT at `0.94000`.
- HumanEval full test: no-public-test ablation reaches `0.99237`; CoT and `manual_v1` both reach `0.98473`.
- MATH full test baselines: direct reaches `0.88889`; CoT reaches `0.89300`.
- MATH full `manual_v1`: reaches `0.91770`, above direct and CoT, with `2,431` calls and `3.79M` tracked tokens.
- Efficiency tradeoff: MATH full `manual_v1` costs `8.91x` direct tokens; HumanEval no-public-test costs `6.19x` direct tokens on the full test split.
- API budget summary: recorded required runs use about `6.20M` tracked tokens; no required API run remains.

## Quick Checks

Run the no-API submission audit:

```bash
conda run -n marl_hw2 python experiments/audit_submission.py
```

Or use the Makefile shortcut:

```bash
make final-check
```

Confirm that any audit warnings are only the maintained warning cases:

```bash
make verify-known-warnings
```

Preview the tracked-file submission package:

```bash
conda run -n marl_hw2 python experiments/package_submission.py --dry-run
```

Create the local submission zip:

```bash
conda run -n marl_hw2 python experiments/package_submission.py
```

Verify the generated zip:

```bash
make verify-package
```

Create and verify the default local submission zip in one step:

```bash
make final-package-check
```

Create an Overleaf-ready LaTeX project zip without compiling or including a PDF:

```bash
make package-latex-project
```

Run every local no-API handoff gate:

```bash
make handoff-check
```

This includes the known-warning gate, so new audit warnings fail the handoff path instead of being hidden among expected blockers.

Verify the assignment run matrix against tracked result and budget tables:

```bash
make verify-requirement-matrix
```

For a shorter progress snapshot, run:

```bash
make status-summary
```

After pushing a key commit, confirm local `main` matches GitHub:

```bash
make verify-github-sync
```

After pushing the final handoff commit, run the full local gate plus GitHub sync check:

```bash
make post-push-check
```

If real metadata is available, run the current submission gate:

```bash
make current-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

After the full MATH `manual_v1` table is tracked in Git and real metadata is available, run the strict final-submission gate:

```bash
make ready-to-submit-check FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

Refresh the API budget summary without making API calls:

```bash
make analyze-api-budget
```

After filling report metadata, create the course-style named zip:

```bash
conda run -n marl_hw2 python experiments/package_submission.py --student-id "Your ID" --name "Your Name" --assignment "MARL-hw2"
```

Or run the final no-API metadata/PDF/package sequence in one command:

```bash
conda run -n marl_hw2 python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

Equivalent Make shortcut:

```bash
make finalize-submission FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

Preview the same final command with real metadata, without writing files:

```bash
make finalize-submission-dry-run FINAL_NAME="Your Name" FINAL_STUDENT_ID="Your ID" FINAL_EMAIL="you@example.com"
```

Preview that sequence with test metadata:

```bash
make finalize-dry-run
```

Verify package-verifier regression checks without writing project files:

```bash
make verify-package-verifier
```

By default, finalization verifies the generated zip and then restores local `report/main.tex` and `report/main.pdf` placeholders so personal metadata is not left in the worktree. The generated zip still contains the filled report source and PDF.
The finalization verifier checks that the zip's report source contains the provided name, student ID, and email.
Default packaging refuses uncommitted tracked changes; finalization only allows the temporary `report/main.tex` metadata edit needed for the filled archive.
Finalization also refuses to start if any tracked file already has uncommitted changes. Package verification likewise refuses dirty tracked files unless an explicit temporary allowlist is provided by the finalization helper, and it scans generated archives for the active `KIMI_API_KEY` value when that environment variable is set.

The equivalent packaging shortcut is:

```bash
make package
```

## Reproducibility

The full command ledger is in `docs/EXPERIMENT_COMMANDS.md`. The cited raw artifacts are in `report/evidence/`.

Generated run directories under `experiments/runs/` and `experiments/chunked_runs/` are ignored. Use `experiments/export_evidence.py --clean` to refresh the tracked evidence from local ignored runs, then `experiments/verify_evidence.py` to verify cited rows, scores, calls, and token totals.

The Makefile target `make refresh-evidence` runs both evidence export and verification.

The report PDF can be built locally with Tectonic:

```bash
make build-report
```

Verify the local PDF is current for the TeX sources:

```bash
make verify-report-pdf
```

Verify the full MATH `manual_v1` chunk plan before reproducing or extending the run:

```bash
make verify-math-manual-plan
```

Preview the chunked runner plan without making API calls:

```bash
make dry-run-math-manual-chunks
```

Summarize current chunked-run progress without making API calls:

```bash
make summarize-math-manual-chunks
```

To reproduce or extend the checkpointed MATH `manual_v1` run, resume one chunk:

```bash
make resume-math-manual-chunk
```

For the full checkpointed-run sequence, see `docs/KIMI_QUOTA_RECOVERY_CN.md`.

Collect completed chunked outputs into the local report table:

```bash
make collect-math-manual-chunked
```

Verify that the collected full MATH `manual_v1` result table has the expected test row:

```bash
make verify-math-manual-result
```

After updating the report with that full-test result, check that the report no longer contains stale pending-run language:

```bash
make verify-final-report-ready
```

Fill the report author metadata before final packaging:

```bash
conda run -n marl_hw2 python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

## Known Blockers

- `report/main.tex` still contains placeholder student name, ID, and email fields; use `experiments/fill_report_metadata.py` after those values are known.
