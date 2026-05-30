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

## Next Steps

1. Initialize Git, set the GitHub remote, and commit the current assignment materials plus tracking files.
2. Add AFlow code under `AFlow/` from upstream.
3. Configure a safe local Kimi config template without exposing secrets.
4. Add reproducible baseline and workflow experiment scripts.
5. Run local static checks first, then only use API calls for small smoke tests.

## Open Issues

- Full API experiments require a valid `KIMI_API_KEY` in the shell environment.
- The exact Kimi model identifier and API base URL need to be verified against the account/platform configuration before running paid calls.
- Complete benchmark runs should wait until small-sample runs show the output format and cost are acceptable.
