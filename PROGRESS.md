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

## Next Steps

1. Rerun CoT/manual workflows after token logging if raw usage comparisons are needed.
2. Run larger subset experiments on 20-50 validation examples.
3. Analyze failures and tune workflows.
4. Keep pushing each new key commit to GitHub after local validation.

## Open Issues

- Full API experiments require a valid `KIMI_API_KEY` in the shell environment.
- The example config uses the official Kimi K2.5 model id `kimi-k2.5` and Moonshot OpenAI-compatible base URL `https://api.moonshot.cn/v1`; account availability still needs to be confirmed before paid runs.
- Complete benchmark runs should wait until small-sample runs show the output format and cost are acceptable.
- GitHub push works through the SSH remote `git@github.com:PPYYQQ/MARL-hw2.git`.
