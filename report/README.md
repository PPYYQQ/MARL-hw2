# Report

This folder contains the ICML 2022 LaTeX report draft.

Build command on a machine with LaTeX installed:

```bash
cd report
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Current status:

- `main.tex` is a draft report with setup notes, architecture summary, workflow design, validation tables, full HumanEval test results, and full MATH direct/CoT baselines.
- Full MATH `manual_v1` workflow results are still missing because the current Kimi account returns an insufficient-balance quota error for new API calls.
- Student name and ID placeholders still need to be filled before final submission.
- This machine does not currently have `pdflatex` or `xelatex`, so PDF compilation must be done after installing LaTeX or on another machine.
