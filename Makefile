PYTHON ?= conda run -n marl_hw2 python
TECTONIC ?= conda run -n marl_hw2 tectonic
FINALIZE_DRY_RUN_NAME ?= Test Student
FINALIZE_DRY_RUN_ID ?= TEST123
FINALIZE_DRY_RUN_EMAIL ?= test@example.com
FINALIZE_DRY_RUN_ASSIGNMENT ?= MARL-hw2

PY_COMPILE_FILES = \
	experiments/run_baselines.py \
	experiments/run_workflows.py \
	experiments/run_chunked_workflows.py \
	experiments/collect_results.py \
	experiments/analyze_efficiency.py \
	experiments/estimate_math_manual_test.py \
	experiments/verify_chunked_plan.py \
	experiments/verify_report_pdf.py \
	experiments/export_evidence.py \
	experiments/verify_evidence.py \
	experiments/fill_report_metadata.py \
	experiments/finalize_submission.py \
	experiments/analyze_math_failures.py \
	experiments/analyze_humaneval_failures.py \
	experiments/audit_submission.py \
	experiments/package_submission.py \
	experiments/verify_submission_package.py \
	AFlow/benchmarks/math.py

.PHONY: py-compile verify-evidence estimate-math-manual verify-math-manual-plan verify-report-pdf audit refresh-evidence build-report package-dry-run package verify-package finalize-dry-run final-package-check final-check

py-compile:
	$(PYTHON) -m py_compile $(PY_COMPILE_FILES)

verify-evidence:
	$(PYTHON) experiments/verify_evidence.py --output report/tables/evidence_verification.md

estimate-math-manual:
	$(PYTHON) experiments/estimate_math_manual_test.py --output report/tables/math_manual_test_estimate.md

verify-math-manual-plan:
	$(PYTHON) experiments/verify_chunked_plan.py --dataset MATH --split test --chunk-size 20 --expect-total-indices 486 --expect-total-chunks 25 --expect-first-index 0 --expect-last-index 485 --expect-contiguous

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

final-check: audit package-dry-run
