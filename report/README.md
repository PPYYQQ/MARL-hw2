# Report

This folder contains the ICML 2022 LaTeX report draft and local PDF build output.

Preferred local build command:

```bash
make build-report
```

Equivalent command from this folder:

```bash
conda run -n marl_hw2 tectonic main.tex
```

Current status:

- `main.tex` is a draft report with setup notes, architecture summary, workflow design, validation tables, full HumanEval test results, and full MATH direct/CoT baselines.
- `main.pdf` has been compiled locally with Tectonic; rebuild it after filling final student metadata.
- `evidence/` contains copied CSV/config/log/token-summary artifacts for the report's cited final runs.
- Full MATH `manual_v1` workflow results are still missing because the current Kimi account returns an insufficient-balance quota error for new API calls.
- Student name and ID placeholders still need to be filled before final submission.
