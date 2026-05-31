PYTHON ?= conda run -n marl_hw2 python
TECTONIC ?= conda run -n marl_hw2 tectonic

PY_COMPILE_FILES = \
	experiments/run_baselines.py \
	experiments/run_workflows.py \
	experiments/run_chunked_workflows.py \
	experiments/collect_results.py \
	experiments/analyze_efficiency.py \
	experiments/estimate_math_manual_test.py \
	experiments/export_evidence.py \
	experiments/verify_evidence.py \
	experiments/fill_report_metadata.py \
	experiments/analyze_math_failures.py \
	experiments/analyze_humaneval_failures.py \
	experiments/audit_submission.py \
	experiments/package_submission.py \
	AFlow/benchmarks/math.py

.PHONY: py-compile verify-evidence estimate-math-manual audit refresh-evidence build-report package-dry-run package final-check

py-compile:
	$(PYTHON) -m py_compile $(PY_COMPILE_FILES)

verify-evidence:
	$(PYTHON) experiments/verify_evidence.py --output report/tables/evidence_verification.md

estimate-math-manual:
	$(PYTHON) experiments/estimate_math_manual_test.py --output report/tables/math_manual_test_estimate.md

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

final-check: audit package-dry-run
