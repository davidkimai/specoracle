## Headline Metrics

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 6 | 1 | 100.0% | 100.0% | 100.0% | -- | 8.389 | 2.333 | 2.000 | 1022.000 |
| In-Context Oracle | 6 | 1 | 100.0% | 100.0% | 100.0% | -- | 4.356 | 1.833 | 3.333 | 1155.333 |
| Human Reference | 6 | 1 | 100.0% | 100.0% | 100.0% | -- | 5.722 | 1.833 | 1.667 | 731.000 |

Paired CC delta oracle-baseline: mean=-4.033, oracle lower=4, oracle higher=0, ties=2, Wilcoxon p=0.125.

Inter-sample CC variance check: 2/6 paired tasks have std < 0.05.

## Measurement Validity

| Variant | Real Context P@1 | Stub Context P@1 | Delta |
| --- | ---: | ---: | ---: |
| Vibecoded Baseline | 100.0% | -- | -- |
| In-Context Oracle | 100.0% | -- | -- |
| Human Reference | 100.0% | -- | -- |

## Supplementary Metrics

| Variant | Tasks | Samples | MI | Judge |
| --- | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 6 | 1 | 67.472 | 8.167 |
| In-Context Oracle | 6 | 1 | 56.934 | 8.833 |
| Human Reference | 6 | 1 | 60.617 | 8.833 |

## Per-Task Paired Breakdown

| Task | Base CC | Oracle CC | Delta | Base Stress | Oracle Stress | Context Std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dependency_order | 14.000 | 4.667 | -9.333 | 100.0% | 100.0% | 6.599 |
| event_windows | 12.000 | 4.333 | -7.667 | 100.0% | 100.0% | 5.421 |
| legacy_invoice_spec | 10.000 | 9.000 | -1.000 | 100.0% | 100.0% | 0.707 |
| nested_json_index | 9.000 | 2.800 | -6.200 | 100.0% | 100.0% | 4.384 |
| policy_merge | 3.667 | 3.667 | 0.000 | 100.0% | 100.0% | 0.000 |
| retry_state_machine | 1.667 | 1.667 | 0.000 | 100.0% | 100.0% | 0.000 |

## Day 2 Hard Subset

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 2 | 1 | 100.0% | 100.0% | 100.0% | -- | 11.500 | 3.000 | 1.000 | 1134.000 |
| In-Context Oracle | 2 | 1 | 100.0% | 100.0% | 100.0% | -- | 3.733 | 2.000 | 4.000 | 1240.500 |
| Human Reference | 2 | 1 | 100.0% | 100.0% | 100.0% | -- | 7.500 | 2.000 | 1.000 | 746.500 |

Paired CC delta oracle-baseline: mean=-7.767, oracle lower=2, oracle higher=0, ties=0, Wilcoxon p=0.500.
