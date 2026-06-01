# HW2 Progress

This document tracks concrete progress toward completing the multi-agent workflow assignment.

## Current Goal

Complete as much of the assignment as possible with a reproducible Git history. Every key implementation or documentation change should be committed, and this document should record what changed, why it matters, and what remains.

## Assignment Scope

- Understand AFlow paper and codebase.
- Configure and run AFlow-style experiments with the Kimi base model.
- Run direct and CoT baselines for MATH-500 and HumanEval.
- Design improved multi-agent workflows for MATH-500 and HumanEval.
- Produce experiment tables, ablations, and a final report.

## Known Inputs

- Assignment slides: `hw2.pptx`
- Report template: `icml2022.zip`
- Reference papers: `refpaper/`
- AFlow upstream: `https://github.com/FoundationAgents/AFlow.git`
- Course GitHub repository: `https://github.com/PPYYQQ/MARL-hw2.git`
- Kimi API key location: environment variable `KIMI_API_KEY`
- Intended base model: `kimi-K2.5` per local `AGENTS.md` note

## Progress Log

### 2026-05-30

- Read assignment slides and created `AGENTS.md` with project overview, expected automation boundary, estimated resources, proposed architecture, implementation plan, and test plan.
- Confirmed the working directory was not a Git repository yet.
- Added repository hygiene rules in `.gitignore` so API keys, local config, generated datasets, logs, and report build artifacts are not committed.
- Started this `PROGRESS.md` file as the canonical work log for future steps.
- Initialized a local Git repository on branch `main`, added GitHub remote `https://github.com/PPYYQQ/MARL-hw2.git`, and committed the initial workspace state.
- Tried to push `main` to GitHub, but HTTPS authentication was not available in this non-interactive shell.
- Imported AFlow source into `AFlow/` from upstream commit `3f457218fc716093fe53f6df8a5d5e6379d66346` and recorded provenance in `AFlow_UPSTREAM.md`.
- Narrowed AFlow's imported `.gitignore` so future assignment workflows under `AFlow/workspace/` can be tracked while generated logs/results stay ignored.
- Confirmed SSH authentication to GitHub as `PPYYQQ`, switched `origin` to `git@github.com:PPYYQQ/MARL-hw2.git`, and pushed `main`.
- Updated AFlow LLM config loading so `config2.yaml` can read API keys from an environment variable such as `KIMI_API_KEY` instead of storing secrets in the repository.
- Added `AFlow/config/config2.kimi.example.yaml` with Kimi K2.5 model aliases and the Moonshot OpenAI-compatible base URL.
- Added `experiments/run_baselines.py` for reproducible direct and CoT baselines on MATH and HumanEval with sample-size, seed, index, concurrency, model, and data-path controls.
- Added `experiments/collect_results.py` and `experiments/README.md` to summarize run CSVs into a report-ready Markdown table.
- Added `AFlow/workspace/MATH/workflows/manual_v1/` with a three-candidate math solver, self-consistency selection, and final boxed-answer cleanup.
- Added `AFlow/workspace/HumanEval/workflows/manual_v1/` with two code-generation candidates, optional public-test repair, and ensemble fallback.
- Fixed experiment runners so commands launched from the repository root still use `AFlow/config/config2.yaml`.
- Added `experiments/run_workflows.py` for reproducible evaluation of tracked workflows such as `manual_v1`.
- Created conda environment `marl_hw2` with Python 3.9, downgraded pip to `24.2` after the default pip failed under Python 3.9, and installed `AFlow/requirements.txt`.
- Created ignored local config `AFlow/config/config2.yaml` from the Kimi example and verified that `KIMI_API_KEY` loads without printing the secret.
- Verified syntax for experiment scripts, `async_llm.py`, and both manual workflows in the `marl_hw2` environment.
- Added `docs/SETUP.md` to preserve the installation and validation commands for the final report.
- Found that AFlow's data downloader imports `requests` even though the imported `requirements.txt` did not include it; added `requests==2.32.3`.
- Found that the local proxy environment requires `socksio` for `httpx`/OpenAI client initialization; added `socksio==1.0.0`.
- Ran a 1-sample MATH direct smoke test; the API reached Kimi but returned `invalid top_p: only 0.95 is allowed`, so `AFlow/config/config2.kimi.example.yaml` was corrected to `top_p: 0.95`.
- Retried the 1-sample MATH direct smoke test; default Kimi thinking behavior stayed open for more than two minutes, so `scripts/async_llm.py` now supports `extra_body`, `max_tokens`, and request timeouts, with the default Kimi alias disabling thinking for practical experiments.
- Retried with thinking disabled; Kimi returned `invalid temperature: only 0.6 is allowed`, so the default non-thinking aliases now use `temperature: 0.6`.
- A later MATH direct smoke test returned the correct `\boxed{\dfrac{1}{12}}` answer but scored zero because SymPy LaTeX parsing needed `antlr4`; added `antlr4-python3-runtime==4.11.0`.
- Downloaded AFlow datasets into ignored `AFlow/data/datasets/`. Available counts: `math_validate.jsonl` 119, `math_test.jsonl` 486, `humaneval_validate.jsonl` 33, `humaneval_test.jsonl` 131, `humaneval_public_test.jsonl` 159.
- Re-ran the same 1-sample MATH direct smoke test after installing `antlr4`; it completed successfully with score `1.00000` at `experiments/runs/MATH/direct/20260530_224550/`.
- Completed 1-sample smoke tests for MATH direct, MATH CoT, MATH `manual_v1`, HumanEval direct, HumanEval CoT, and HumanEval `manual_v1`; all final smoke runs scored `1.00000`.
- Added `--latest-only` to `experiments/collect_results.py` so report tables can ignore earlier parameter-debug runs and keep the newest result per dataset/method/model/split.
- Started the ICML 2022 report draft in `report/main.tex`, with sections for AFlow structure, environment setup, baseline design, manual workflow design, smoke results, limitations, and planned full experiments.
- Added report support files from the provided ICML template and `report/references.bib` with AFlow, multi-agent debate, GPTSwarm, HumanEval, and MATH references.
- Ran 3-sample validation subsets for MATH and HumanEval direct, CoT, and `manual_v1`; all six runs scored `1.00000`.
- Regenerated `report/tables/smoke_results.md` with the latest 3-sample runs and updated the report text from one-sample smoke tests to small-subset results.
- Updated experiment runners to save `llm_usage.json` for each new run and copy raw input/output token totals plus call counts into `run_config.json`.
- Updated `experiments/collect_results.py` so future tables include `calls`, `input_tokens`, `output_tokens`, and total `tokens`; this avoids relying on the currently unpriced Kimi `total_cost` field.
- Added MATH workflow `ablation_single`, which uses one solution candidate plus final formatting to isolate the effect of multi-candidate generation and self-consistency.
- Added HumanEval workflow `ablation_no_public_test`, which removes public-test repair to isolate the effect of execution feedback.
- Added `docs/ABLATIONS.md` with tracked ablation variants and exact low-cost/larger validation commands.
- Ran 3-sample validation ablations with sample seed 1. `MATH/ablation_single` scored `1.00000` using 6 LLM calls and 10,153 tokens. `HumanEval/ablation_no_public_test` scored `1.00000` using 9 LLM calls and 7,882 tokens.
- Regenerated `report/tables/smoke_results.md` with ablation rows and updated `report/main.tex` to explain that the tiny subset validates code paths but does not yet distinguish workflow quality.
- Re-ran 3-sample direct baselines after token logging. `MATH/direct` scored `1.00000` using 3 LLM calls and 2,586 tokens. `HumanEval/direct` scored `1.00000` using 3 LLM calls and 1,748 tokens.
- Refreshed `report/tables/smoke_results.md` and report text with the newly available direct/ablation token counts.
- Re-ran 3-sample CoT baselines after token logging. `MATH/cot` scored `1.00000` using 3 LLM calls and 3,444 tokens. `HumanEval/cot` scored `1.00000` using 3 LLM calls and 3,240 tokens.
- Re-ran 3-sample manual workflows after token logging. `MATH/manual_v1` scored `1.00000` using 15 LLM calls and 30,235 tokens. `HumanEval/manual_v1` scored `1.00000` using 6 LLM calls and 3,275 tokens.
- Refreshed `report/tables/smoke_results.md` and `report/main.tex` so all eight 3-sample result rows now include raw call and token usage.
- Ran 20-sample validation baselines with sample seed 1. Raw saved scores before MATH text-answer rescoring were `MATH/direct=0.80000`, `MATH/cot=0.85000`, `HumanEval/direct=1.00000`, and `HumanEval/cot=1.00000`.
- Ran 20-sample validation workflows and ablations with sample seed 1. Raw saved scores before MATH text-answer rescoring were `MATH/manual_v1=0.85000`, `MATH/ablation_single=0.80000`, `HumanEval/manual_v1=1.00000`, and `HumanEval/ablation_no_public_test=1.00000`.
- Found MATH evaluator false negatives for simple text answers such as `MAKE` versus `\text{MAKE}` and comma spacing in `\text{C,E}`. Updated `AFlow/benchmarks/math.py` to normalize simple text wrappers and comma spacing.
- Updated `experiments/collect_results.py` with `--rescore-math`, allowing saved MATH predictions to be rescored without repeating expensive API calls.
- Generated `report/tables/validation20_results.md` from the 20-sample runs with corrected MATH scoring. Corrected scores are `MATH/direct=0.85000`, `MATH/cot=0.95000`, `MATH/manual_v1=0.95000`, and `MATH/ablation_single=0.85000`; all HumanEval rows remain `1.00000`.
- Updated `report/main.tex` and `experiments/README.md` with the 20-sample validation commands, token-aware table, evaluator correction note, and remaining experiment plan.
- Added generated `tester.txt` files to `.gitignore` after HumanEval execution tests produced a local scratch log.
- Tightened MATH rescoring again after discovering that SymPy could incorrectly treat `2,-1` as equal to `2`. The evaluator now treats comma-separated answers as unordered lists, keeps thousands separators numeric, and combines multiple boxed reference answers such as `\boxed{-1}` and `\boxed{2}`.
- Regenerated `report/tables/validation20_results.md` with list-aware MATH scoring. Corrected 20-sample MATH scores are now `direct=0.90000`, `cot=0.95000`, `manual_v1=1.00000`, and `ablation_single=0.90000`; this is the first validation subset where the manual workflow exceeds CoT.
- Updated `report/main.tex` to describe the MATH manual workflow's 20-sample gain over CoT and the remaining need to validate that gain on larger subsets.
- Tightened MATH rescoring further for nested `\boxed{...}` answers, percent answers such as `28` versus `28%`, variable-assignment prefixes such as `a = -2 + \sqrt{3}`, and grouped coordinate answers. This leaves only one 50-sample `manual_v1` MATH failure after rescoring.
- Ran 50-sample MATH validation with sample seed 1. Final rescored results are `direct=0.96000`, `cot=0.94000`, `manual_v1=0.98000`, and `ablation_single=0.94000`. `manual_v1` stays above direct, CoT, and the single-candidate ablation, but uses 349,515 tokens.
- Added `--dataset` and `--sample-size` filters to `experiments/collect_results.py` so 20-sample and 50-sample result tables remain reproducible after later runs.
- Generated `report/tables/math_validation50_results.md` and updated `report/main.tex`, `experiments/README.md`, and this progress log with the 50-sample MATH validation result.
- Ran full HumanEval test split evaluations. Results are `direct=0.97710` with 48,941 tokens, `cot=0.98473` with 120,573 tokens, `manual_v1=0.98473` with 134,751 tokens, and `ablation_no_public_test=0.99237` with 303,127 tokens.
- Added `--split` filtering to `experiments/collect_results.py`, generated `report/tables/humaneval_test_results.md`, and updated `report/main.tex` with the full HumanEval test table.
- Added generated `error.log` files to `.gitignore` after HumanEval execution tests produced local failure logs.
- Ran full MATH test split baselines. `MATH/direct` scored `0.88889` using 486 LLM calls and 425,052 tokens; `MATH/cot` scored `0.89300` using 486 LLM calls and 459,130 tokens.
- Generated `report/tables/math_test_baselines.md` and updated `report/main.tex` with the full MATH direct/CoT baseline table.
- Attempted full MATH `manual_v1` test with `--max-concurrency 2`; the process stayed alive but stopped updating run files for more than 20 minutes before producing a final CSV, so it was stopped. The next full workflow run should be checkpointed in chunks to avoid losing progress to a single long API wait.
- Added `experiments/run_chunked_workflows.py` for checkpointed workflow evaluation. It writes per-chunk CSV/config files, refreshes an aggregate result after every completed chunk, supports `--run-id` resume plus `--start-chunk`/`--max-chunks` batch controls, and keeps generated outputs under ignored `experiments/chunked_runs/`.
- Added `docs/CHUNKED_WORKFLOWS.md` and updated `experiments/README.md` with dry-run, full MATH `manual_v1`, resume, and summarization commands.
- Attempted the first chunked MATH test `manual_v1` batch, but Kimi returned `exceeded_current_quota_error` / insufficient balance for every problem, producing no usable LLM calls. Updated `experiments/run_chunked_workflows.py` so quota-only chunks are marked `failed_quota`, excluded from aggregates, and stop the run instead of being treated as completed.
- Refreshed `report/main.tex` and `report/README.md` so the report status matches the current evidence: MATH validation subsets, full HumanEval test results, full MATH direct/CoT baselines, and the remaining quota-blocked full MATH `manual_v1` run.
- Added `docs/SUBMISSION_STATUS.md` as a submission checklist with current deliverables, exact result summary, reproducibility commands, known blockers, and next actions.
- Added `experiments/analyze_math_failures.py` and generated `report/tables/math_validation50_failure_analysis.md` for problem-level comparison of the 50-sample MATH validation runs. The analysis shows `manual_v1` fixes two of three CoT failures with no CoT-relative regressions, leaving only index `91` as a shared failure across all compared methods.
- Added `experiments/audit_submission.py`, a no-API submission readiness audit that checks required files, Python syntax, report sections, result table snippets, secret hygiene, and known external blockers.
- Added `experiments/analyze_humaneval_failures.py` and generated `report/tables/humaneval_test_failure_analysis.md` for problem-level comparison of full HumanEval test runs. CoT, `manual_v1`, and no-public-test each solve the three direct failures; no-public-test introduces the fewest regressions against direct.
- Added `experiments/package_submission.py` to build a submission zip from tracked files plus an optional compiled report PDF, and ignored local generated zip outputs under `submission/`.
- Added `experiments/analyze_efficiency.py` and generated `report/tables/efficiency_summary.md` to summarize score deltas and token multipliers against direct prompting. The report now explicitly states the main cost tradeoffs for MATH `manual_v1` and HumanEval no-public-test.
- Added `experiments/export_evidence.py` and generated tracked `report/evidence/` artifacts for the cited final runs, including copied CSVs, configs, failure logs, and token summaries without full call histories.
- Added a report section for explicit workflow algorithm details, covering MATH `manual_v1`, MATH single-candidate ablation, HumanEval `manual_v1`, and the no-public-test ablation.
- Added `docs/EXPERIMENT_COMMANDS.md` as a command ledger for API runs, result table regeneration, failure analysis, evidence export, audit, and packaging.
- Added `docs/PAPER_NOTES.md` and a report research-context section connecting AFlow's code-represented workflow search and multi-agent debate's candidate-diversity idea to the implemented manual workflows.
- Added a top-level `README.md` as the GitHub/submission entry point, summarizing repository contents, current results, reproducibility checks, evidence location, and known blockers.
- Added `experiments/verify_evidence.py` and `report/tables/evidence_verification.md` so tracked evidence can reproduce the cited scores, row counts, call counts, and token totals without using ignored run directories.
- Added a top-level `Makefile` with local shortcuts for compile checks, evidence verification, audit, evidence refresh, dry-run packaging, and final packaging.
- Added `experiments/fill_report_metadata.py` so final report author name, student ID, and email placeholders can be filled safely once provided.
- Installed Tectonic in the `marl_hw2` conda environment, generated `report/main.pdf`, and added a `make build-report` shortcut plus audit checks for the local report PDF.
- Polished `report/main.tex` path formatting and narrow tables so the Tectonic build no longer reports overfull boxes.
- Extended `experiments/package_submission.py` with optional student ID, name, and assignment arguments so the final zip can follow the course naming convention once metadata is known.
- Added `experiments/estimate_math_manual_test.py` and `report/tables/math_manual_test_estimate.md`, estimating the missing full MATH `manual_v1` run at about 2,430 calls and 3.40M raw tokens.
- Added `experiments/finalize_submission.py` to run the final metadata fill, report PDF rebuild, zip verification, and named submission packaging once student metadata is available; it restores local report source/PDF placeholders after packaging by default to avoid accidental personal metadata commits.
- Added `docs/COMPLETION_AUDIT.md` to map each assignment requirement to current evidence files, validation gates, and remaining external inputs.
- Added `experiments/verify_submission_package.py` and `make verify-package` to validate generated zip contents, manifest commit, PDF inclusion, and forbidden secret/run paths.
- Added `make final-package-check` as a one-command default submission packaging gate, running package creation and zip verification together.
- Added `experiments/verify_chunked_plan.py` and `make verify-math-manual-plan` to confirm the remaining full MATH `manual_v1` run covers 486 contiguous test examples in 25 chunks before spending restored API quota.
- Extended final submission verification so `experiments/finalize_submission.py` checks that `report/main.tex` inside the generated zip contains the provided student name, ID, and email instead of placeholders.
- Tightened packaging integrity so `experiments/package_submission.py` refuses uncommitted tracked changes by default; finalization allows only the temporary filled `report/main.tex` metadata edit.
- Added `experiments/verify_report_pdf.py` and `make verify-report-pdf` so packaging gates can confirm the local report PDF is current for the tracked TeX sources before including it.
- Tightened `experiments/verify_submission_package.py` so generated package manifests must include a parseable audit summary with zero failures and no failing audit lines.
- Added per-file SHA-256 checksums to `SUBMISSION_MANIFEST.txt` and made package verification recompute archive hashes, so generated zips are checked for content integrity rather than only entry names.
- Refreshed `docs/SUBMISSION_STATUS.md` so its deliverable list and expanded compile command include the latest local verifiers and explain the current package verification coverage.
- Tightened `experiments/finalize_submission.py` so finalization refuses to start when tracked files already have uncommitted changes, while still allowing its own temporary report metadata edit during packaging.
- Added `make finalize-dry-run` with overrideable test metadata variables so the finalization command path can be previewed without writing files.
- Added `make handoff-check` to run all local no-API handoff gates in one command: final audit/package dry-run, MATH chunk-plan verification, finalization dry-run, and final package verification.
- Refreshed `docs/SETUP.md` so the local validation section points at the maintained Makefile gates instead of an outdated hand-written `py_compile` command.
- Added `docs/REQUIREMENT_RUN_MATRIX.md` to show the assignment-required experiment matrix, completed runs, status, and evidence paths in one place.
- Added `experiments/analyze_api_budget.py`, `make analyze-api-budget`, and `report/tables/api_budget_summary.md` to track historical Kimi token usage, stopped-run estimates, and the remaining full MATH `manual_v1` budget.
- Updated the report limitations section so the PDF now reflects the verified Kimi budget summary instead of saying Kimi pricing still needs to be added.
- Extended MATH failure analysis so the remaining shared validate50 failure is explicitly classified as a reasoning error rather than a local rescoring issue.
- Added `make resume-math-manual-chunk` and `make collect-math-manual-chunked` so the quota-restored full MATH `manual_v1` continuation path is a short, documented command instead of a long hand-written invocation.
- Added `make dry-run-math-manual-chunks` to preview the chunked full MATH `manual_v1` plan without making API calls.
- Expanded `docs/REQUIREMENT_RUN_MATRIX.md` with Chinese handoff tables for assignment-required runs, completed runs, remaining support needs, historical quota use, and the remaining MATH `manual_v1` budget.
- Added `docs/FINAL_HANDOFF_CN.md` as a Chinese final handoff checklist for submit-ready artifacts, missing student metadata, optional Kimi quota recovery, and final packaging commands.
- Extended `experiments/audit_submission.py` so the no-API submission audit now requires the Chinese final handoff checklist and verifies key handoff-document snippets.
- Added `experiments/verify_git_sync.py` and `make verify-github-sync` so each pushed key commit can be checked against the configured GitHub upstream.
- Added `make post-push-check` so the final pushed handoff state can run package/audit gates and GitHub synchronization verification in one command.

## Next Steps

1. Recharge the Kimi account or provide another valid `KIMI_API_KEY`; the practical minimum is CNY 50 for Tier1 limits, with CNY 80-100 leaving retry margin.
2. Resume full MATH `manual_v1` with the chunked runner in 20-example chunks, starting with `--max-chunks 1` to confirm quota and checkpointing.
3. After chunks complete, collect the full MATH `manual_v1` table, export evidence, rebuild the report, and rerun `make handoff-check`.
4. Run `experiments/finalize_submission.py` with final student name, student ID, and email before course submission.
5. Keep pushing each new key commit to GitHub after local validation.

## Open Issues

- Full API experiments require a valid `KIMI_API_KEY` in the shell environment.
- The Kimi account currently returns an insufficient-balance quota error for new calls; further API experiments require recharge or another valid `KIMI_API_KEY`.
- Full MATH `manual_v1` test evaluation is the main missing benchmark run.
- Report metadata still needs the final student name, student ID, and email.
- GitHub push works through the SSH remote `git@github.com:PPYYQQ/MARL-hw2.git`.
