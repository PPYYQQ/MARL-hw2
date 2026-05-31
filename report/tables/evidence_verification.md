# Evidence Verification

This table is computed from tracked `report/evidence/` CSV/config/token-summary files.
MATH rows are rescored with the current evaluator; HumanEval rows use saved evaluator scores.

| group | method | rows | score | expected_score | calls | tokens | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| math_validate50 | direct | 50 | 0.96000 | 0.96000 | 50 | 38140 | ok |
| math_validate50 | cot | 50 | 0.94000 | 0.94000 | 50 | 39806 | ok |
| math_validate50 | manual_v1 | 50 | 0.98000 | 0.98000 | 250 | 349515 | ok |
| math_validate50 | ablation_single | 50 | 0.94000 | 0.94000 | 100 | 114590 | ok |
| humaneval_test | direct | 131 | 0.97710 | 0.97710 | 131 | 48941 | ok |
| humaneval_test | cot | 131 | 0.98473 | 0.98473 | 131 | 120573 | ok |
| humaneval_test | manual_v1 | 131 | 0.98473 | 0.98473 | 287 | 134751 | ok |
| humaneval_test | ablation_no_public_test | 131 | 0.99237 | 0.99237 | 409 | 303127 | ok |
| math_test_baselines | direct | 486 | 0.88889 | 0.88889 | 486 | 425052 | ok |
| math_test_baselines | cot | 486 | 0.89300 | 0.89300 | 486 | 459130 | ok |
