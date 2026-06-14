# Completion Audit

This document maps the assignment requirements to the current repository evidence. It is intended as a final handoff checklist for the remaining manual steps.

## Requirement Coverage

| Requirement | Current status | Evidence |
| --- | --- | --- |
| Read and explain workflow context | Complete | `report/main.tex` sections `Research Context`, `Proposed Workflow Design`, and `Algorithmic Rationale`; `docs/PAPER_NOTES.md` |
| Record environment setup | Complete outside the final report | `docs/SETUP.md`; `AFlow/config/config2.kimi.example.yaml` |
| Configure base model safely | Complete | `AFlow/config/config2.kimi.example.yaml`; `AFlow/scripts/async_llm.py`; local `AFlow/config/config2.yaml` ignored |
| Run direct baseline | Complete for MATH validation/test and HumanEval test | `experiments/run_baselines.py`; `report/tables/validation20_results.md`; `report/tables/math_validation50_results.md`; `report/tables/humaneval_test_results.md`; `report/tables/math_test_baselines.md` |
| Run CoT baseline | Complete for MATH validation/test and HumanEval test | Same baseline runner and result tables as above |
| Design MATH workflow | Complete on validation and full test | `AFlow/workspace/MATH/workflows/manual_v1/graph.py`; `AFlow/workspace/MATH/workflows/manual_v1/prompt.py`; `report/tables/math_validation50_results.md`; `report/tables/math_test_manual_chunked.md` |
| Design HumanEval workflow | Complete on full test | `AFlow/workspace/HumanEval/workflows/manual_v1/graph.py`; `AFlow/workspace/HumanEval/workflows/manual_v1/prompt.py`; `report/tables/humaneval_test_results.md` |
| Compare against baselines | Complete for primary full runs and validation ablations | `report/main.tex` section `Validation Results`; `report/tables/efficiency_summary.md` |
| Include ablations | Complete | `AFlow/workspace/MATH/workflows/ablation_single/graph.py`; `AFlow/workspace/HumanEval/workflows/ablation_no_public_test/graph.py`; `docs/ABLATIONS.md` |
| Analyze failures | Complete for MATH validation50 and HumanEval full test | `report/tables/math_validation50_failure_analysis.md`; `report/tables/humaneval_test_failure_analysis.md` |
| Account for API budget | Complete locally | `report/tables/api_budget_summary.md`; `experiments/analyze_api_budget.py`; `Makefile` target `analyze-api-budget` |
| Track raw evidence | Complete for cited runs | `report/evidence/`; `report/tables/evidence_verification.md`; `experiments/verify_evidence.py` |
| Prepare report PDF | Complete locally, needs final metadata rebuild | `report/main.pdf`; `Makefile` targets `build-report` and `verify-report-pdf`; `experiments/finalize_submission.py` |
| Prepare submission package | Complete default package; final named package needs metadata | `experiments/package_submission.py`; `experiments/finalize_submission.py`; `submission/MARL-hw2-submission.zip` |
| Verify missing MATH run plan | Complete locally | `experiments/verify_chunked_plan.py`; `Makefile` target `verify-math-manual-plan`; `docs/CHUNKED_WORKFLOWS.md` |

## Remaining External Inputs

| Item | Why it remains open | Next command |
| --- | --- | --- |
| Student name, ID, and email | Required for final report metadata and named package; finalization restores source placeholders by default after packaging | `conda run -n marl_hw2 python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com"` |
| Optional follow-up API budget | No required API run remains; more Kimi budget is only needed for optional full-test ablations or prompt tuning | `docs/KIMI_QUOTA_RECOVERY_CN.md` |

## Current Validation Gates

| Gate | Expected outcome |
| --- | --- |
| `make final-check` | Passes with warnings only for student metadata and `KIMI_API_KEY` if unset |
| `make verify-known-warnings` | Fails if the submission audit emits any warning outside the maintained warning allowlist |
| `make analyze-api-budget` | Refreshes the recorded usage and remaining Kimi budget table without making API calls |
| `make verify-math-manual-plan` | Confirms the full MATH `manual_v1` test plan covers 486 examples in 25 contiguous chunks |
| `make verify-math-manual-result` | Confirms the collected full MATH `manual_v1` result table has one 486-example MATH test row with valid score/model fields and at least 2,400 calls plus 2.5M tokens by default |
| `make verify-final-report-ready` | Confirms the report source includes the completed full MATH `manual_v1` score/calls/tokens and does not retain stale pending-run language |
| `make verify-metadata-validation` | Confirms placeholder/example metadata is rejected and maintained test metadata only passes with explicit opt-in |
| `make verify-requirement-matrix` | Confirms the assignment run matrix matches tracked result tables, budget totals, and the completed full MATH status |
| `make verify-package-verifier` | Confirms package-verifier regression checks catch manifest count drift and active API key leakage |
| `make dry-run-math-manual-chunks` | Prints the chunked runner's full MATH `manual_v1` plan without making API calls |
| `make summarize-math-manual-chunks` | Prints completed, quota-failed, missing, and next chunk status without making API calls |
| `make resume-math-manual-chunk` | Resumes one checkpointed full MATH `manual_v1` chunk by default; no required chunk remains after 25/25 completion |
| `make collect-math-manual-chunked` | Collects completed chunked full MATH `manual_v1` outputs into the report table |
| `make build-report` | Rebuilds `report/main.pdf` with Tectonic |
| `make verify-report-pdf` | Confirms `report/main.pdf` is present and newer than the TeX source files |
| `make package` | Writes `submission/MARL-hw2-submission.zip` from a clean tracked worktree, `report/main.pdf`, and `SUBMISSION_MANIFEST.txt` |
| `make verify-package` | Verifies the zip against tracked files, clean tracked worktree state, current commit, manifest output path, included PDF, manifest file counts, archive/filesystem checksums, zero-failure audit summary, forbidden secret/run paths, and active `KIMI_API_KEY` leakage when available |
| `make finalize-dry-run` | Previews finalization with test metadata without writing files |
| `make finalize-submission-dry-run FINAL_NAME="..." FINAL_STUDENT_ID="..." FINAL_EMAIL="..."` | Previews the final named package path using real metadata without writing files |
| `make finalize-submission FINAL_NAME="..." FINAL_STUDENT_ID="..." FINAL_EMAIL="..."` | Builds and verifies the final named package once real student metadata is known |
| `make final-package-check` | Creates the default zip and verifies it in one local gate |
| `make status-summary` | Prints the known-warning check, current MATH chunk status, and GitHub sync status without building packages |
| `make handoff-check` | Runs all local no-API handoff gates, including known-warning verification, in one target |
| `make post-push-check` | Runs `make handoff-check` and then verifies the local branch matches its GitHub upstream |
| `make current-submit-check` | Validates real metadata, runs handoff gates, builds the named package, and verifies GitHub sync |
| `make ready-to-submit-check` | Validates real metadata, requires a verified Git-tracked full MATH `manual_v1` table, and checks the updated report before building the final named package and verifying GitHub sync |
| `experiments/finalize_submission.py --dry-run ...` | Previews final metadata lines and named package contents without writing |
| `experiments/finalize_submission.py ...` | Requires a clean tracked worktree, builds and verifies a filled-metadata zip/PDF, checks report metadata inside the archive, then restores local `report/main.tex` and `report/main.pdf` placeholders unless `--keep-filled-report` is passed |

## Submission Risk Notes

- The report now includes the completed Full MATH `manual_v1` test result: score `0.91770`, 2,431 calls, and 3,786,936 tracked tokens.
- The MATH validate50 failure analysis classifies the remaining shared failure at index `91` as a reasoning error rather than a rescoring issue.
- The default generated zip is usable for review, but the final course submission should be regenerated from a clean worktree with real metadata and the named package command.
- The finalization helper starts from a clean tracked worktree, checks filled metadata inside the generated archive, and avoids leaving personal metadata in the worktree by default; use `--keep-filled-report` only if you intentionally want `report/main.tex` and `report/main.pdf` to remain filled locally.
- Final metadata commands reject placeholder/example metadata, case variants, `TODO`, and angle-bracket placeholders for normal finalization and real-metadata dry-runs; `make finalize-dry-run` is the only maintained path that intentionally enables `--allow-test-metadata`.
- `make final-check` now fails if required files are present locally but not tracked by Git.
- `make verify-known-warnings` keeps expected external blockers separate from new audit warnings that should be fixed before handoff.
