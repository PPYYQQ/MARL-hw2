# MARL HW2: Multi-Agent Workflow Design with AFlow

This repository contains the implementation, experiment runners, evidence, and report draft for the multi-agent workflow assignment.

## What Is Included

- `AFlow/`: imported AFlow codebase plus local assignment workflow additions.
- `experiments/`: reproducible runners, table collectors, analysis utilities, audit checks, evidence export, and packaging helpers.
- `report/main.tex`: ICML-style report draft.
- `report/tables/`: tracked report tables and analysis summaries.
- `report/evidence/`: copied CSV/config/log/token-summary artifacts for the cited final runs.
- `docs/`: setup notes, ablation notes, experiment command ledger, paper notes, chunked-run guide, completion audit, and submission status.
- `docs/REQUIREMENT_RUN_MATRIX.md`: assignment requirement matrix showing required runs, completed runs, gaps, and evidence.
- `PROGRESS.md`: chronological work log.

## Current Result Summary

- MATH 20-sample validation: `manual_v1` reaches `1.00000`, above CoT at `0.95000`.
- MATH 50-sample validation: `manual_v1` reaches `0.98000`, above direct at `0.96000` and CoT at `0.94000`.
- HumanEval full test: no-public-test ablation reaches `0.99237`; CoT and `manual_v1` both reach `0.98473`.
- MATH full test baselines: direct reaches `0.88889`; CoT reaches `0.89300`.
- MATH full `manual_v1` estimate: about `2,430` calls and `3.40M` raw tokens for the 486-example test split.
- Efficiency tradeoff: MATH `manual_v1` costs `9.16x` direct tokens on 50 validation samples; HumanEval no-public-test costs `6.19x` direct tokens on the full test split.
- API budget summary: recorded runs use about `2.41M` tracked tokens; the remaining full MATH `manual_v1` run is estimated at `3.40M` tokens.

## Quick Checks

Run the no-API submission audit:

```bash
conda run -n marl_hw2 python experiments/audit_submission.py
```

Or use the Makefile shortcut:

```bash
make final-check
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

Run every local no-API handoff gate:

```bash
make handoff-check
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

Preview that sequence with test metadata:

```bash
make finalize-dry-run
```

By default, finalization verifies the generated zip and then restores local `report/main.tex` and `report/main.pdf` placeholders so personal metadata is not left in the worktree. The generated zip still contains the filled report source and PDF.
The finalization verifier checks that the zip's report source contains the provided name, student ID, and email.
Default packaging refuses uncommitted tracked changes; finalization only allows the temporary `report/main.tex` metadata edit needed for the filled archive.
Finalization also refuses to start if any tracked file already has uncommitted changes.

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

Verify the planned full MATH `manual_v1` chunks before spending API quota:

```bash
make verify-math-manual-plan
```

Preview the chunked runner plan without making API calls:

```bash
make dry-run-math-manual-chunks
```

After quota is restored, resume one checkpointed MATH `manual_v1` chunk:

```bash
make resume-math-manual-chunk
```

Collect completed chunked outputs into the local report table:

```bash
make collect-math-manual-chunked
```

Fill the report author metadata before final packaging:

```bash
conda run -n marl_hw2 python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

## Known Blockers

- New Kimi API calls currently fail with an insufficient-balance quota error, so full MATH `manual_v1` test evaluation is not complete.
- `report/main.tex` still contains placeholder student name, ID, and email fields; use `experiments/fill_report_metadata.py` after those values are known.
