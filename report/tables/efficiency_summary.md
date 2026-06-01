# Efficiency Summary

Score deltas and multipliers are computed against the direct baseline within each result group.

| group | method | score | delta_vs_direct | calls | call_multiplier | tokens | token_multiplier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MATH validate50 | ablation_single | 0.94000 | -0.02000 | 100 | 2.00x | 114590 | 3.00x |
| MATH validate50 | cot | 0.94000 | -0.02000 | 50 | 1.00x | 39806 | 1.04x |
| MATH validate50 | direct | 0.96000 | +0.00000 | 50 | 1.00x | 38140 | 1.00x |
| MATH validate50 | manual_v1 | 0.98000 | +0.02000 | 250 | 5.00x | 349515 | 9.16x |
| HumanEval test | ablation_no_public_test | 0.99237 | +0.01527 | 409 | 3.12x | 303127 | 6.19x |
| HumanEval test | cot | 0.98473 | +0.00763 | 131 | 1.00x | 120573 | 2.46x |
| HumanEval test | direct | 0.97710 | +0.00000 | 131 | 1.00x | 48941 | 1.00x |
| HumanEval test | manual_v1 | 0.98473 | +0.00763 | 287 | 2.19x | 134751 | 2.75x |
| MATH test | cot | 0.89300 | +0.00411 | 486 | 1.00x | 459130 | 1.08x |
| MATH test | direct | 0.88889 | +0.00000 | 486 | 1.00x | 425052 | 1.00x |
| MATH test | manual_v1 | 0.91770 | +0.02881 | 2431 | 5.00x | 3786936 | 8.91x |
