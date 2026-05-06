## Headline Metrics

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 20 | 3 | 100.0% | 100.0% | 100.0% | 100.0% | 8.101 | 2.533 | 1.683 | 1257.200 |
| In-Context Oracle | 20 | 3 | 95.0% | 96.7% | 100.0% | 100.0% | 4.887 | 2.100 | 2.683 | 1344.150 |
| Human Reference | 20 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 4.492 | 2.000 | 2.200 | 851.550 |

Paired CC delta oracle-baseline: mean=-3.214, oracle lower=13, oracle higher=4, ties=3, Wilcoxon p=0.004.

Inter-sample CC variance check: 3/20 paired tasks have std < 0.05.

## Measurement Validity

| Variant | Real Context P@1 | Stub Context P@1 | Delta |
| --- | ---: | ---: | ---: |
| Vibecoded Baseline | 100.0% | 100.0% | 0.0% |
| In-Context Oracle | 96.7% | 100.0% | -3.3% |
| Human Reference | 100.0% | 100.0% | 0.0% |

## Supplementary Metrics

| Variant | Tasks | Samples | MI | Judge |
| --- | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 20 | 3 | 72.370 | 7.800 |
| In-Context Oracle | 20 | 3 | 74.813 | 8.783 |
| Human Reference | 20 | 1 | 60.545 | 8.800 |

## Per-Task Paired Breakdown

| Task | Base CC | Oracle CC | Delta | Base Stress | Oracle Stress | Context Std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| archival_binding_spec | 9.000 | 9.000 | 0.000 | 100.0% | 100.0% | 0.000 |
| cli_argument_validation | 14.333 | 3.617 | -10.717 | 100.0% | 100.0% | 5.894 |
| config_precedence_merge | 4.950 | 5.167 | +0.217 | 100.0% | 100.0% | 0.441 |
| csv_sales_aggregate | 15.000 | 5.722 | -9.278 | 100.0% | 100.0% | 5.433 |
| dedupe_event_stream | 10.000 | 4.555 | -5.445 | 100.0% | 100.0% | 2.992 |
| dependency_order | 13.333 | 4.683 | -8.650 | 100.0% | 33.3% | 4.758 |
| event_windows | 11.333 | 3.444 | -7.889 | 100.0% | 100.0% | 4.429 |
| feature_flag_matrix | 4.000 | 3.667 | -0.333 | 100.0% | 100.0% | 0.408 |
| incident_desk_spec | 6.000 | 5.000 | -1.000 | 100.0% | 100.0% | 1.049 |
| inventory_reorder | 13.000 | 3.556 | -9.444 | 100.0% | 100.0% | 5.289 |
| json_path_projection | 10.667 | 6.000 | -4.667 | 100.0% | 100.0% | 2.961 |
| legacy_invoice_spec | 7.333 | 9.000 | +1.667 | 100.0% | 100.0% | 0.983 |
| log_sessionizer | 10.333 | 4.778 | -5.556 | 100.0% | 100.0% | 3.096 |
| nested_json_index | 9.000 | 7.667 | -1.333 | 100.0% | 100.0% | 1.033 |
| policy_merge | 7.667 | 8.000 | +0.333 | 100.0% | 100.0% | 1.329 |
| retry_backoff_schedule | 5.000 | 5.000 | 0.000 | 100.0% | 100.0% | 0.000 |
| retry_state_machine | 1.333 | 1.333 | 0.000 | 100.0% | 100.0% | 0.000 |
| round_robin_scheduler | 5.000 | 3.000 | -2.000 | 100.0% | 100.0% | 1.095 |
| sliding_window_limiter | 2.333 | 2.344 | +0.011 | 100.0% | 100.0% | 0.120 |
| thread_safe_counter | 2.400 | 2.200 | -0.200 | 100.0% | 100.0% | 0.110 |

## Day 2 Hard Subset

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 9 | 3 | 100.0% | 100.0% | 100.0% | 100.0% | 8.409 | 2.963 | 1.741 | 1474.481 |
| In-Context Oracle | 9 | 3 | 88.9% | 92.6% | 100.0% | 100.0% | 5.450 | 2.519 | 2.778 | 1568.926 |
| Human Reference | 9 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 4.789 | 2.333 | 2.333 | 879.444 |

Paired CC delta oracle-baseline: mean=-2.959, oracle lower=7, oracle higher=1, ties=1, Wilcoxon p=0.023.
