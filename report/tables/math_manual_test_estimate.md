# MATH Manual Workflow Full-Test Resource Estimate

This estimate uses the tracked 50-sample MATH `manual_v1` validation run as the per-example cost source.
It is a planning estimate, not a measured full-test result.

| item | estimate |
| --- | --- |
| validation source | 50 MATH validation examples |
| test examples | 486 |
| planned chunk size | 20 examples |
| planned chunks | 25 chunks; last chunk has 6 examples |
| manual calls per example | 5.00 |
| manual tokens per example | 6,990 |
| estimated full-test calls | 2,430 |
| estimated full-test tokens | 3,397,286 |
| estimated tokens per full chunk | 139,806 |
| estimated calls per full chunk | 100 |
| token multiplier vs direct test | 7.99x |
| token multiplier vs CoT test | 7.40x |
