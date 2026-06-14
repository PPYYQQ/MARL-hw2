# Report

This folder contains the ICML 2022 LaTeX report source and local PDF build output.

Preferred local build command:

```bash
make build-report
```

Equivalent command from this folder:

```bash
conda run -n marl_hw2 tectonic main.tex
```

Current status:

- `main.tex` is the English final-report source with setup notes, architecture summary, workflow design, validation/test tables, full HumanEval test results, and full MATH direct/CoT/`manual_v1` results.
- `main.pdf` has been compiled locally with Tectonic, but the Overleaf project zip intentionally excludes the PDF.
- `evidence/` contains copied CSV/config/log/token-summary artifacts for the report's cited final runs.
- Student name and ID placeholders still need to be filled before final submission.

Create an Overleaf-ready LaTeX source zip without compiling a PDF:

```bash
make package-latex-project
```
