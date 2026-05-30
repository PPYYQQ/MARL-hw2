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

## Next Steps

1. Add reproducible baseline and workflow experiment scripts.
2. Add manual MATH and HumanEval workflow variants.
3. Run local static checks first, then only use API calls for small smoke tests.
4. Keep pushing each new key commit to GitHub after local validation.

## Open Issues

- Full API experiments require a valid `KIMI_API_KEY` in the shell environment.
- The example config uses the official Kimi K2.5 model id `kimi-k2.5` and Moonshot OpenAI-compatible base URL `https://api.moonshot.cn/v1`; account availability still needs to be confirmed before paid runs.
- Complete benchmark runs should wait until small-sample runs show the output format and cost are acceptable.
- GitHub push works through the SSH remote `git@github.com:PPYYQQ/MARL-hw2.git`.
