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

- `main.tex` is a draft report with setup notes, architecture summary, workflow design, and smoke-test results.
- Full benchmark tables should replace the smoke-test table after complete MATH-500 and HumanEval runs.
- Student name and ID placeholders still need to be filled before final submission.
