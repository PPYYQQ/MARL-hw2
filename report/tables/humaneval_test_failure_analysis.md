# HumanEval Full-Test Failure Analysis

Split: `test`. Sample size: `131`. Baseline for comparisons: `direct`.
Scores are read from the saved HumanEval evaluator outputs.

## Summary

| method | score | failures | fixes_vs_direct | regressions_vs_direct | shared_failures_vs_direct | calls | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct | 0.97710 | 3 | 0 | 0 | 3 | 131 | 48941 |
| cot | 0.98473 | 2 | 3 | 2 | 0 | 131 | 120573 |
| manual_v1 | 0.98473 | 2 | 3 | 2 | 0 | 287 | 134751 |
| no_public | 0.99237 | 1 | 3 | 1 | 0 | 409 | 303127 |

## Failure And Disagreement Cases

| index | entry_point | scores | failure_reasons |
| --- | --- | --- | --- |
| 10 | encode | direct:0, cot:1, manual_v1:1, no_public:1 | direct:Error: This prints if this assert fails 1 (good for debugging!). |
| 26 | car_race_collision | direct:1, cot:1, manual_v1:0, no_public:1 | manual_v1:Error: . |
| 29 | poly | direct:1, cot:0, manual_v1:1, no_public:0 | cot:Error: .; no_public:Error: . |
| 70 | intersection | direct:0, cot:1, manual_v1:1, no_public:1 | direct:Error: . |
| 117 | tri | direct:0, cot:1, manual_v1:1, no_public:1 | direct:Error: local variable 'result' referenced before assignment. |
| 120 | sort_array | direct:1, cot:0, manual_v1:0, no_public:1 | cot:Error: .; manual_v1:failed |
