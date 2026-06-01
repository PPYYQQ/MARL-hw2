PYTHON ?= conda run -n marl_hw2 python
TECTONIC ?= conda run -n marl_hw2 tectonic
FINALIZE_DRY_RUN_NAME ?= Test Student
FINALIZE_DRY_RUN_ID ?= TEST123
FINALIZE_DRY_RUN_EMAIL ?= test@example.com
FINALIZE_DRY_RUN_ASSIGNMENT ?= MARL-hw2
FINAL_NAME ?=
FINAL_STUDENT_ID ?=
FINAL_EMAIL ?=
FINAL_ASSIGNMENT ?= MARL-hw2
MATH_MANUAL_RUN_ID ?= math-test-manual-v1
MATH_MANUAL_CHUNK_SIZE ?= 20
MATH_MANUAL_MAX_CONCURRENCY ?= 2
MATH_MANUAL_MAX_CHUNKS ?= 1
MATH_MANUAL_OUTPUT ?= report/tables/math_test_manual_chunked.md
MATH_MANUAL_MIN_CALLS ?= 2400
MATH_MANUAL_MIN_TOKENS ?= 2500000

PY_COMPILE_FILES = \
	experiments/run_baselines.py \
	experiments/run_workflows.py \
	experiments/run_chunked_workflows.py \
	experiments/collect_results.py \
	experiments/analyze_efficiency.py \
	experiments/analyze_api_budget.py \
	experiments/estimate_math_manual_test.py \
	experiments/summarize_chunked_run.py \
	experiments/verify_chunked_plan.py \
	experiments/verify_result_table.py \
	experiments/verify_final_report_ready.py \
	experiments/verify_report_pdf.py \
	experiments/verify_metadata_validation.py \
	experiments/verify_requirement_matrix.py \
	experiments/verify_package_verifier.py \
	experiments/verify_audit_warnings.py \
	experiments/export_evidence.py \
	experiments/verify_evidence.py \
	experiments/verify_git_sync.py \
	experiments/fill_report_metadata.py \
	experiments/finalize_submission.py \
	experiments/analyze_math_failures.py \
	experiments/analyze_humaneval_failures.py \
	experiments/audit_submission.py \
	experiments/package_submission.py \
	experiments/verify_submission_package.py \
	AFlow/benchmarks/math.py

.PHONY: py-compile verify-evidence verify-github-sync estimate-math-manual analyze-api-budget verify-math-manual-plan verify-math-manual-result verify-final-report-ready summarize-math-manual-chunks dry-run-math-manual-chunks resume-math-manual-chunk collect-math-manual-chunked verify-report-pdf verify-metadata-validation verify-requirement-matrix verify-package-verifier verify-known-warnings audit refresh-evidence build-report package-dry-run package verify-package finalize-dry-run finalize-submission-dry-run finalize-submission final-package-check final-check status-summary handoff-check post-push-check current-submit-check ready-to-submit-check

py-compile:
	$(PYTHON) -m py_compile $(PY_COMPILE_FILES)

verify-evidence:
	$(PYTHON) experiments/verify_evidence.py --output report/tables/evidence_verification.md

verify-github-sync:
	$(PYTHON) experiments/verify_git_sync.py

estimate-math-manual:
	$(PYTHON) experiments/estimate_math_manual_test.py --output report/tables/math_manual_test_estimate.md

analyze-api-budget:
	$(PYTHON) experiments/analyze_api_budget.py --output report/tables/api_budget_summary.md

verify-math-manual-plan:
	$(PYTHON) experiments/verify_chunked_plan.py --dataset MATH --split test --chunk-size 20 --expect-total-indices 486 --expect-total-chunks 25 --expect-first-index 0 --expect-last-index 485 --expect-contiguous

verify-math-manual-result:
	$(PYTHON) experiments/verify_result_table.py --table "$(MATH_MANUAL_OUTPUT)" --dataset MATH --method manual_v1 --split test --samples 486 --require-model kimi --min-calls $(MATH_MANUAL_MIN_CALLS) --min-tokens $(MATH_MANUAL_MIN_TOKENS)

verify-final-report-ready:
	$(PYTHON) experiments/verify_final_report_ready.py --table "$(MATH_MANUAL_OUTPUT)" --forbidden-phrase "main remaining experiment is the expensive full MATH" --forbidden-phrase "full MATH workflow evaluation should be rerun" --forbidden-phrase "no full-test \\texttt{manual\\_v1} chunk is reported yet" --forbidden-phrase "Current MATH workflow results are validation subsets and should not be interpreted as final benchmark gains" --forbidden-phrase "remaining core work is to resume the expensive full MATH workflow evaluation"

summarize-math-manual-chunks:
	$(PYTHON) experiments/summarize_chunked_run.py --dataset MATH --workflow manual_v1 --run-id "$(MATH_MANUAL_RUN_ID)"

dry-run-math-manual-chunks:
	$(PYTHON) experiments/run_chunked_workflows.py --dataset MATH --workflow manual_v1 --split test --chunk-size $(MATH_MANUAL_CHUNK_SIZE) --run-id "$(MATH_MANUAL_RUN_ID)" --dry-run

resume-math-manual-chunk:
	$(PYTHON) experiments/run_chunked_workflows.py --dataset MATH --workflow manual_v1 --split test --chunk-size $(MATH_MANUAL_CHUNK_SIZE) --max-concurrency $(MATH_MANUAL_MAX_CONCURRENCY) --run-id "$(MATH_MANUAL_RUN_ID)" --max-chunks $(MATH_MANUAL_MAX_CHUNKS)

collect-math-manual-chunked:
	$(PYTHON) experiments/collect_results.py --runs-dir experiments/chunked_runs --latest-only --rescore-math --dataset MATH --split test --output $(MATH_MANUAL_OUTPUT)

verify-report-pdf:
	$(PYTHON) experiments/verify_report_pdf.py

verify-metadata-validation:
	$(PYTHON) experiments/verify_metadata_validation.py

verify-requirement-matrix:
	$(PYTHON) experiments/verify_requirement_matrix.py

verify-package-verifier:
	$(PYTHON) experiments/verify_package_verifier.py

verify-known-warnings:
	$(PYTHON) experiments/verify_audit_warnings.py

audit: py-compile verify-evidence
	$(PYTHON) experiments/audit_submission.py

refresh-evidence:
	$(PYTHON) experiments/export_evidence.py --clean
	$(PYTHON) experiments/verify_evidence.py --output report/tables/evidence_verification.md

build-report:
	cd report && $(TECTONIC) main.tex

package-dry-run:
	$(PYTHON) experiments/package_submission.py --dry-run

package:
	$(PYTHON) experiments/package_submission.py

verify-package:
	$(PYTHON) experiments/verify_submission_package.py

finalize-dry-run:
	$(PYTHON) experiments/finalize_submission.py --name "$(FINALIZE_DRY_RUN_NAME)" --student-id "$(FINALIZE_DRY_RUN_ID)" --email "$(FINALIZE_DRY_RUN_EMAIL)" --assignment "$(FINALIZE_DRY_RUN_ASSIGNMENT)" --dry-run --allow-test-metadata

finalize-submission-dry-run:
	@test -n "$(FINAL_NAME)" || (echo "Set FINAL_NAME='Your Name'" && exit 1)
	@test -n "$(FINAL_STUDENT_ID)" || (echo "Set FINAL_STUDENT_ID='Your ID'" && exit 1)
	@test -n "$(FINAL_EMAIL)" || (echo "Set FINAL_EMAIL='you@example.com'" && exit 1)
	$(PYTHON) experiments/finalize_submission.py --name "$(FINAL_NAME)" --student-id "$(FINAL_STUDENT_ID)" --email "$(FINAL_EMAIL)" --assignment "$(FINAL_ASSIGNMENT)" --dry-run

finalize-submission:
	@test -n "$(FINAL_NAME)" || (echo "Set FINAL_NAME='Your Name'" && exit 1)
	@test -n "$(FINAL_STUDENT_ID)" || (echo "Set FINAL_STUDENT_ID='Your ID'" && exit 1)
	@test -n "$(FINAL_EMAIL)" || (echo "Set FINAL_EMAIL='you@example.com'" && exit 1)
	$(PYTHON) experiments/finalize_submission.py --name "$(FINAL_NAME)" --student-id "$(FINAL_STUDENT_ID)" --email "$(FINAL_EMAIL)" --assignment "$(FINAL_ASSIGNMENT)"

final-package-check: verify-report-pdf package verify-package

final-check: analyze-api-budget audit package-dry-run

status-summary: verify-known-warnings summarize-math-manual-chunks verify-github-sync

handoff-check: final-check verify-known-warnings verify-metadata-validation verify-requirement-matrix verify-package-verifier verify-math-manual-plan summarize-math-manual-chunks finalize-dry-run final-package-check

post-push-check: handoff-check verify-github-sync

current-submit-check:
	@test -n "$(FINAL_NAME)" || (echo "Set FINAL_NAME='Your Name'" && exit 1)
	@test -n "$(FINAL_STUDENT_ID)" || (echo "Set FINAL_STUDENT_ID='Your ID'" && exit 1)
	@test -n "$(FINAL_EMAIL)" || (echo "Set FINAL_EMAIL='you@example.com'" && exit 1)
	$(MAKE) finalize-submission-dry-run
	$(MAKE) handoff-check
	$(MAKE) finalize-submission
	$(MAKE) verify-github-sync

ready-to-submit-check:
	@test -n "$(FINAL_NAME)" || (echo "Set FINAL_NAME='Your Name'" && exit 1)
	@test -n "$(FINAL_STUDENT_ID)" || (echo "Set FINAL_STUDENT_ID='Your ID'" && exit 1)
	@test -n "$(FINAL_EMAIL)" || (echo "Set FINAL_EMAIL='you@example.com'" && exit 1)
	$(MAKE) finalize-submission-dry-run
	@test -f "$(MATH_MANUAL_OUTPUT)" || (echo "Missing $(MATH_MANUAL_OUTPUT); finish MATH manual_v1 chunks and run make collect-math-manual-chunked" && exit 1)
	@git ls-files --error-unmatch "$(MATH_MANUAL_OUTPUT)" >/dev/null 2>&1 || (echo "$(MATH_MANUAL_OUTPUT) is not tracked by Git; run git add and commit it before final submission" && exit 1)
	$(MAKE) verify-math-manual-result
	$(MAKE) verify-final-report-ready
	$(MAKE) handoff-check
	$(MAKE) finalize-submission
	$(MAKE) verify-github-sync
