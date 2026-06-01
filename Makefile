PYTHON ?= conda run -n marl_hw2 python
TECTONIC ?= conda run -n marl_hw2 tectonic
FINALIZE_DRY_RUN_NAME ?= Test Student
FINALIZE_DRY_RUN_ID ?= TEST123
FINALIZE_DRY_RUN_EMAIL ?= test@example.com
FINALIZE_DRY_RUN_ASSIGNMENT ?= MARL-hw2
MATH_MANUAL_RUN_ID ?= math-test-manual-v1
MATH_MANUAL_CHUNK_SIZE ?= 20
MATH_MANUAL_MAX_CONCURRENCY ?= 2
MATH_MANUAL_MAX_CHUNKS ?= 1
MATH_MANUAL_OUTPUT ?= report/tables/math_test_manual_chunked.md

PY_COMPILE_FILES = \
	experiments/run_baselines.py \
	experiments/run_workflows.py \
	experiments/run_chunked_workflows.py \
	experiments/collect_results.py \
	experiments/analyze_efficiency.py \
	experiments/analyze_api_budget.py \
	experiments/estimate_math_manual_test.py \
	experiments/verify_chunked_plan.py \
	experiments/verify_report_pdf.py \
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

.PHONY: py-compile verify-evidence verify-github-sync estimate-math-manual analyze-api-budget verify-math-manual-plan dry-run-math-manual-chunks resume-math-manual-chunk collect-math-manual-chunked verify-report-pdf audit refresh-evidence build-report package-dry-run package verify-package finalize-dry-run final-package-check final-check handoff-check post-push-check

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

dry-run-math-manual-chunks:
	$(PYTHON) experiments/run_chunked_workflows.py --dataset MATH --workflow manual_v1 --split test --chunk-size $(MATH_MANUAL_CHUNK_SIZE) --run-id "$(MATH_MANUAL_RUN_ID)" --dry-run

resume-math-manual-chunk:
	$(PYTHON) experiments/run_chunked_workflows.py --dataset MATH --workflow manual_v1 --split test --chunk-size $(MATH_MANUAL_CHUNK_SIZE) --max-concurrency $(MATH_MANUAL_MAX_CONCURRENCY) --run-id "$(MATH_MANUAL_RUN_ID)" --max-chunks $(MATH_MANUAL_MAX_CHUNKS)

collect-math-manual-chunked:
	$(PYTHON) experiments/collect_results.py --runs-dir experiments/chunked_runs --latest-only --rescore-math --dataset MATH --split test --output $(MATH_MANUAL_OUTPUT)

verify-report-pdf:
	$(PYTHON) experiments/verify_report_pdf.py

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
	$(PYTHON) experiments/finalize_submission.py --name "$(FINALIZE_DRY_RUN_NAME)" --student-id "$(FINALIZE_DRY_RUN_ID)" --email "$(FINALIZE_DRY_RUN_EMAIL)" --assignment "$(FINALIZE_DRY_RUN_ASSIGNMENT)" --dry-run

final-package-check: verify-report-pdf package verify-package

final-check: analyze-api-budget audit package-dry-run

handoff-check: final-check verify-math-manual-plan finalize-dry-run final-package-check

post-push-check: handoff-check verify-github-sync
