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
- `experiments/export_evidence.py`: copies cited run artifacts into tracked report evidence.
- `experiments/verify_evidence.py`: verifies tracked evidence against cited scores, row counts, calls, and token totals.
- `experiments/fill_report_metadata.py`: fills author name, student ID, and email when provided.
- `experiments/analyze_math_failures.py`: problem-level MATH run comparison utility.
- `experiments/analyze_humaneval_failures.py`: problem-level HumanEval run comparison utility.
- `experiments/audit_submission.py`: no-API submission readiness checker.
- `experiments/package_submission.py`: tracked-file submission zip builder.
- `docs/EXPERIMENT_COMMANDS.md`: command ledger for API runs, table generation, analysis, evidence export, audit, and packaging.
- `docs/PAPER_NOTES.md`: notes linking AFlow and multi-agent debate ideas to the implemented workflows.
- `report/main.tex`: ICML-style draft report with current methods and result tables.
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
  experiments/export_evidence.py \
  experiments/verify_evidence.py \
  experiments/fill_report_metadata.py \
  experiments/analyze_math_failures.py \
  experiments/analyze_humaneval_failures.py \
  experiments/audit_submission.py \
  experiments/package_submission.py \
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

Run the no-API submission audit:

```bash
make final-check
```

Audit only:

```bash
conda run -n marl_hw2 python experiments/audit_submission.py
```

The audit is expected to warn until the Kimi quota, report metadata, full MATH `manual_v1` test run, and local PDF build are resolved.

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
- `pdflatex` and `xelatex` are not installed on this machine, so the report PDF has not been compiled locally.
- `report/main.tex` still contains placeholder student name, student ID, and email fields; use `experiments/fill_report_metadata.py` after those values are known.

## Next Actions

1. Recharge the Kimi account or provide another valid `KIMI_API_KEY`.
2. Resume full MATH `manual_v1` with the chunked runner.
3. Collect the chunked MATH result table after enough chunks complete.
4. Fill student metadata in `report/main.tex` with `experiments/fill_report_metadata.py`.
5. Compile the final PDF on a machine with LaTeX installed.
6. Run `experiments/package_submission.py` to create the final tracked-file zip.
