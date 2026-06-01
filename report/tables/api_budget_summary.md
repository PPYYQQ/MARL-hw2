# API Budget Summary

This table summarizes local Kimi API usage from saved `run_config.json` files and estimates the remaining full MATH `manual_v1` run. It does not make API calls.

Pricing basis checked on 2026-06-01 from Kimi documentation: Kimi K2.5 input is CNY 0.70/1M tokens for cache hits or CNY 4.00/1M tokens for cache misses; output is CNY 21.00/1M tokens. The cost column is therefore a cache-hit to cache-miss input range.

Kimi rate-limit basis checked on 2026-06-01: Tier0 has 1.5M tokens per day; Tier1 starts at CNY 50 cumulative recharge and removes the daily token cap. The remaining run is larger than the Tier0 daily cap, so a CNY 50 recharge is the practical minimum if the account is currently at Tier0.

## Recorded Usage

| group | runs | calls | input_tokens | output_tokens | total_tokens | estimated Kimi K2.5 cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20-example validation experiments | 8 | 323 | 144,804 | 172,599 | 317,403 | CNY 3.73-4.20 |
| 3-example smoke and ablation checks | 8 | 48 | 26,096 | 36,467 | 62,563 | CNY 0.78-0.87 |
| HumanEval full test experiments | 4 | 958 | 273,040 | 334,352 | 607,392 | CNY 7.21-8.11 |
| MATH 50-example validation experiments | 4 | 450 | 249,617 | 292,434 | 542,051 | CNY 6.32-7.14 |
| MATH full direct/CoT baselines | 2 | 972 | 107,606 | 776,576 | 884,182 | CNY 16.38-16.74 |
| Recorded subtotal | 26 | 2,751 | 801,163 | 1,612,428 | 2,413,591 | CNY 34.42-37.07 |

## Estimated Unmetered Usage

15 early smoke/debug run configs predate reliable token accounting and are not assigned a cost here. The stopped full MATH `manual_v1` attempt did not write a usage file, so it is estimated from the 50-example validation run.

| group | runs | calls | input_tokens | output_tokens | total_tokens | estimated Kimi K2.5 cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Unmetered stopped MATH manual_v1 attempt (15 examples) | 1 | 75 | 56,248 | 48,607 | 104,855 | CNY 1.06-1.25 |
| Recorded plus estimated stopped attempts | 27 | 2,826 | 857,411 | 1,661,035 | 2,518,446 | CNY 35.48-38.31 |

## Remaining Required API Budget

| group | runs | calls | input_tokens | output_tokens | total_tokens | estimated Kimi K2.5 cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Remaining full MATH manual_v1 test estimate | 1 | 2,430 | 1,822,432 | 1,574,854 | 3,397,286 | CNY 34.35-40.36 |

Recommendation: keep at least CNY 50 available before resuming full MATH `manual_v1`; CNY 80-100 leaves room for retries or a small follow-up validation run.

Sources: `report/evidence/math_validate50/manual_v1/run_config.json`, `report/evidence/math_test_baselines/direct/run_config.json`, and saved run configs under `experiments/runs/`.
