# MATH 50-Sample Failure Analysis

Split: `validate`. Sample size: `50`. Baseline for comparisons: `cot`.
Scores are recomputed from saved predictions with the current MATH evaluator.

## Summary

| method | score | failures | fixes_vs_cot | regressions_vs_cot | shared_failures_vs_cot | calls | tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct | 0.96000 | 2 | 2 | 1 | 1 | 50 | 38140 |
| cot | 0.94000 | 3 | 0 | 0 | 3 | 50 | 39806 |
| manual_v1 | 0.98000 | 1 | 2 | 0 | 1 | 250 | 349515 |
| single | 0.94000 | 3 | 1 | 1 | 2 | 100 | 114590 |

## Failure And Disagreement Cases

| index | reference | scores | extracted_answers | question |
| --- | --- | --- | --- | --- |
| 15 | 19 | direct:1, cot:0, manual_v1:1, single:0 | direct:19; cot:17; manual_v1:19; single:Left,Right from {0,5,10,15}: pairs are (0,5),(0... | How many rectangles are in this figure? Each angle is a right angle. [asy] unitsize(0.0... |
| 63 | \text{C,E} | direct:0, cot:1, manual_v1:1, single:1 | direct:C; cot:C, E; manual_v1:C,E; single:C,E | Let $a$ be a factor of $b,$ and let $b$ and $c$ be divisors of $60$ such that $a<b<c<60... |
| 91 | \frac{25 \sqrt{10}}{4} | direct:0, cot:0, manual_v1:0, single:0 | direct:\dfrac{17\sqrt{10}}{2}; cot:\dfrac{17\sqrt{10}}{2}; manual_v1:\dfrac{17\sqrt{10}... | A tennis ball dipped in red paint rolls around on the coordinate plane, so that it is a... |
| 97 | \frac{10}{19} | direct:1, cot:1, manual_v1:1, single:0 | direct:\dfrac{10}{19}; cot:\dfrac{10}{19}; manual_v1:\dfrac{10}{19}; single:\dfrac{6}{19} | A regular dodecahedron is a convex polyhedron with 12 regular pentagonal faces and 20 v... |
| 100 | \frac{3}{16} | direct:1, cot:0, manual_v1:1, single:1 | direct:\dfrac{3}{16}; cot:\dfrac{11}{64}; manual_v1:\dfrac{3}{16}; single:\dfrac{3}{16} | While staying in a 15-story hotel, Polya plays the following game. She enters an elevat... |

## Interpretation Notes

- Shared failures across every compared method are unlikely to be fixed by rescoring alone: index `91` has reference `\frac{25 \sqrt{10}}{4}` and extracted predictions `\dfrac{17\sqrt{10}}{2}`.
