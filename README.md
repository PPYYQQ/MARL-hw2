# MARL HW2: Multi-Agent Workflow Design with AFlow

This repository contains the implementation, experiment runners, evidence, and report draft for the multi-agent workflow assignment.

## What Is Included

- `AFlow/`: imported AFlow codebase plus local assignment workflow additions.
- `experiments/`: reproducible runners, table collectors, analysis utilities, audit checks, evidence export, and packaging helpers.
- `report/main.tex`: ICML-style report draft.
- `report/tables/`: tracked report tables and analysis summaries.
- `report/evidence/`: copied CSV/config/log/token-summary artifacts for the cited final runs.
- `docs/`: setup notes, ablation notes, experiment command ledger, paper notes, chunked-run guide, completion audit, and submission status.
- `PROGRESS.md`: chronological work log.

## Current Result Summary

- MATH 20-sample validation: `manual_v1` reaches `1.00000`, above CoT at `0.95000`.
- MATH 50-sample validation: `manual_v1` reaches `0.98000`, above direct at `0.96000` and CoT at `0.94000`.
- HumanEval full test: no-public-test ablation reaches `0.99237`; CoT and `manual_v1` both reach `0.98473`.
- MATH full test baselines: direct reaches `0.88889`; CoT reaches `0.89300`.
- MATH full `manual_v1` estimate: about `2,430` calls and `3.40M` raw tokens for the 486-example test split.
- Efficiency tradeoff: MATH `manual_v1` costs `9.16x` direct tokens on 50 validation samples; HumanEval no-public-test costs `6.19x` direct tokens on the full test split.

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

After filling report metadata, create the course-style named zip:

```bash
conda run -n marl_hw2 python experiments/package_submission.py --student-id "Your ID" --name "Your Name" --assignment "MARL-hw2"
```

Or run the final no-API metadata/PDF/package sequence in one command:

```bash
conda run -n marl_hw2 python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

By default, finalization restores local `report/main.tex` and `report/main.pdf` placeholders after packaging so personal metadata is not left in the worktree. The generated zip still contains the filled report source and PDF.

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

Fill the report author metadata before final packaging:

```bash
conda run -n marl_hw2 python experiments/fill_report_metadata.py --name "Your Name" --student-id "Your ID" --email "you@example.com"
```

## Known Blockers

- New Kimi API calls currently fail with an insufficient-balance quota error, so full MATH `manual_v1` test evaluation is not complete.
- `report/main.tex` still contains placeholder student name, ID, and email fields; use `experiments/fill_report_metadata.py` after those values are known.
