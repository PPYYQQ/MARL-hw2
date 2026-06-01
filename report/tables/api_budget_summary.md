# API Budget Summary

This table summarizes local Kimi API usage from saved `run_config.json` files. It does not make API calls.

Pricing basis checked on 2026-06-01 from Kimi documentation: Kimi K2.5 input is CNY 0.70/1M tokens for cache hits or CNY 4.00/1M tokens for cache misses; output is CNY 21.00/1M tokens. The cost column is therefore a cache-hit to cache-miss input range.

Kimi rate-limit basis checked on 2026-06-01: Tier0 has 1.5M tokens per day; Tier1 starts at CNY 50 cumulative recharge and removes the daily token cap. The completed full MATH `manual_v1` run is larger than the Tier0 daily cap, so a Tier1 account or equivalent quota is required to reproduce it in one day.

## Recorded Usage

| group | runs | calls | input_tokens | output_tokens | total_tokens | estimated Kimi K2.5 cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20-example validation experiments | 8 | 323 | 144,804 | 172,599 | 317,403 | CNY 3.73-4.20 |
| 3-example smoke and ablation checks | 8 | 48 | 26,096 | 36,467 | 62,563 | CNY 0.78-0.87 |
| HumanEval full test experiments | 4 | 958 | 273,040 | 334,352 | 607,392 | CNY 7.21-8.11 |
| MATH 50-example validation experiments | 4 | 450 | 249,617 | 292,434 | 542,051 | CNY 6.32-7.14 |
| MATH full direct/CoT baselines | 2 | 972 | 107,606 | 776,576 | 884,182 | CNY 16.38-16.74 |
| MATH full manual_v1 workflow | 1 | 2,431 | 2,009,595 | 1,777,341 | 3,786,936 | CNY 38.73-45.36 |
| Recorded subtotal | 27 | 5,182 | 2,810,758 | 3,389,769 | 6,200,527 | CNY 73.15-82.43 |

## Estimated Unmetered Usage

15 early smoke/debug run configs predate reliable token accounting and are not assigned a cost here. The stopped full MATH `manual_v1` attempt did not write a usage file, so it is estimated from the 50-example validation run.

| group | runs | calls | input_tokens | output_tokens | total_tokens | estimated Kimi K2.5 cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Unmetered stopped MATH manual_v1 attempt (15 examples) | 1 | 75 | 56,248 | 48,607 | 104,855 | CNY 1.06-1.25 |
| Recorded plus estimated stopped attempts | 28 | 5,257 | 2,867,006 | 3,438,376 | 6,305,382 | CNY 74.21-83.67 |

## Remaining Required API Budget

No required API run remains for the assignment experiments. Additional Kimi budget is only needed for optional follow-up ablations or prompt tuning.

Sources: `report/evidence/math_validate50/manual_v1/run_config.json`, `report/evidence/math_test_baselines/direct/run_config.json`, `experiments/chunked_runs/MATH/manual_v1/math-test-manual-v1/run_config.json`, and saved run configs under `experiments/runs/`.
