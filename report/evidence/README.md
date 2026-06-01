# Experiment Evidence Manifest

This directory contains copied artifacts for the experiment runs cited in the report tables.
Generated files come from ignored `experiments/runs/` directories so the submission can include raw evidence without tracking every debug run.
For MATH rows, `raw_average_score` is the original CSV score; report tables may use `experiments/collect_results.py --rescore-math` with the current evaluator.

| group | method | rows | raw_average_score | calls | tokens | target |
| --- | --- | --- | --- | --- | --- | --- |
| math_validate50 | direct | 50 | 0.90000 | 50 | 38140 | report/evidence/math_validate50/direct |
| math_validate50 | cot | 50 | 0.88000 | 50 | 39806 | report/evidence/math_validate50/cot |
| math_validate50 | manual_v1 | 50 | 0.90000 | 250 | 349515 | report/evidence/math_validate50/manual_v1 |
| math_validate50 | ablation_single | 50 | 0.88000 | 100 | 114590 | report/evidence/math_validate50/ablation_single |
| humaneval_test | direct | 131 | 0.97710 | 131 | 48941 | report/evidence/humaneval_test/direct |
| humaneval_test | cot | 131 | 0.98473 | 131 | 120573 | report/evidence/humaneval_test/cot |
| humaneval_test | manual_v1 | 131 | 0.98473 | 287 | 134751 | report/evidence/humaneval_test/manual_v1 |
| humaneval_test | ablation_no_public_test | 131 | 0.99237 | 409 | 303127 | report/evidence/humaneval_test/ablation_no_public_test |
| math_test_baselines | direct | 486 | 0.88889 | 486 | 425052 | report/evidence/math_test_baselines/direct |
| math_test_baselines | cot | 486 | 0.89300 | 486 | 459130 | report/evidence/math_test_baselines/cot |
| math_test_manual | manual_v1 | 486 | 0.91770 | 2431 | 3786936 | report/evidence/math_test_manual/manual_v1 |
