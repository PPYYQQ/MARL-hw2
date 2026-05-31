# Completion Audit

This document maps the assignment requirements to the current repository evidence. It is intended as a final handoff checklist for the remaining manual steps.

## Requirement Coverage

| Requirement | Current status | Evidence |
| --- | --- | --- |
| Read and explain AFlow paper/code | Complete | `report/main.tex` sections `Research Context` and `AFlow Engineering Summary`; `docs/PAPER_NOTES.md` |
| Record environment setup | Complete | `report/main.tex` section `Environment Setup`; `docs/SETUP.md` |
| Configure base model safely | Complete | `AFlow/config/config2.kimi.example.yaml`; `AFlow/scripts/async_llm.py`; local `AFlow/config/config2.yaml` ignored |
| Run direct baseline | Complete for MATH validation/test and HumanEval test | `experiments/run_baselines.py`; `report/tables/validation20_results.md`; `report/tables/math_validation50_results.md`; `report/tables/humaneval_test_results.md`; `report/tables/math_test_baselines.md` |
| Run CoT baseline | Complete for MATH validation/test and HumanEval test | Same baseline runner and result tables as above |
| Design MATH workflow | Complete on validation; full test pending quota | `AFlow/workspace/MATH/workflows/manual_v1/graph.py`; `AFlow/workspace/MATH/workflows/manual_v1/prompt.py`; `report/tables/math_validation50_results.md` |
| Design HumanEval workflow | Complete on full test | `AFlow/workspace/HumanEval/workflows/manual_v1/graph.py`; `AFlow/workspace/HumanEval/workflows/manual_v1/prompt.py`; `report/tables/humaneval_test_results.md` |
| Compare against baselines | Complete for available runs | `report/main.tex` section `Validation Results`; `report/tables/efficiency_summary.md` |
| Include ablations | Complete | `AFlow/workspace/MATH/workflows/ablation_single/graph.py`; `AFlow/workspace/HumanEval/workflows/ablation_no_public_test/graph.py`; `docs/ABLATIONS.md` |
| Analyze failures | Complete for MATH validation50 and HumanEval full test | `report/tables/math_validation50_failure_analysis.md`; `report/tables/humaneval_test_failure_analysis.md` |
| Track raw evidence | Complete for cited runs | `report/evidence/`; `report/tables/evidence_verification.md`; `experiments/verify_evidence.py` |
| Prepare report PDF | Complete locally, needs final metadata rebuild | `report/main.pdf`; `Makefile` target `build-report`; `experiments/finalize_submission.py` |
| Prepare submission package | Complete default package; final named package needs metadata | `experiments/package_submission.py`; `experiments/finalize_submission.py`; `submission/MARL-hw2-submission.zip` |

## Remaining External Inputs

| Item | Why it remains open | Next command |
| --- | --- | --- |
| Student name, ID, and email | Required for final report metadata and named package | `conda run -n marl_hw2 python experiments/finalize_submission.py --name "Your Name" --student-id "Your ID" --email "you@example.com"` |
| Kimi account balance or replacement API key | Current Kimi calls return insufficient-balance quota errors | `conda run -n marl_hw2 python experiments/run_chunked_workflows.py --dataset MATH --workflow manual_v1 --split test --chunk-size 20 --max-concurrency 2 --run-id math-test-manual-v1 --max-chunks 1` |
| Full MATH `manual_v1` test result | Depends on restored API quota; estimated at about 2,430 calls and 3.40M raw tokens | `conda run -n marl_hw2 python experiments/collect_results.py --runs-dir experiments/chunked_runs --latest-only --rescore-math --dataset MATH --split test --output report/tables/math_test_manual_chunked.md` |

## Current Validation Gates

| Gate | Expected outcome |
| --- | --- |
| `make final-check` | Passes with warnings only for student metadata and missing full MATH `manual_v1` test table |
| `make build-report` | Rebuilds `report/main.pdf` with Tectonic |
| `make package` | Writes `submission/MARL-hw2-submission.zip` with tracked files, `report/main.pdf`, and `SUBMISSION_MANIFEST.txt` |
| `experiments/finalize_submission.py --dry-run ...` | Previews final metadata lines and named package contents without writing |

## Submission Risk Notes

- The report already states that full MATH `manual_v1` test evaluation is pending quota and uses validation evidence for the MATH workflow claim.
- The default generated zip is usable for review, but the final course submission should be regenerated with real metadata and the named package command.
- `make final-check` now fails if required files are present locally but not tracked by Git.
