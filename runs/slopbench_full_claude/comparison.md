## Headline Metrics

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 50 | 3 | 88.7% | 85.3% | 86.0% | 86.0% | 5.753 | 2.213 | 2.107 | 1270.247 |
| In-Context Oracle | 50 | 3 | 89.3% | 84.7% | 88.0% | 86.0% | 4.800 | 1.953 | 2.500 | 1287.387 |
| Human Reference | 50 | 1 | 100.0% | 88.0% | 88.0% | 86.0% | 4.098 | 1.800 | 1.840 | 735.820 |

Paired CC delta oracle-baseline: mean=-0.953, oracle lower=26, oracle higher=19, ties=5, Wilcoxon p=0.155.

Inter-sample CC variance check: 4/50 paired tasks have std < 0.05.

## Measurement Validity

| Variant | Real Context P@1 | Stub Context P@1 | Delta |
| --- | ---: | ---: | ---: |
| Vibecoded Baseline | 85.3% | 86.0% | -0.7% |
| In-Context Oracle | 84.7% | 86.0% | -1.3% |
| Human Reference | 88.0% | 86.0% | +2.0% |

## Supplementary Metrics

| Variant | Tasks | Samples | MI | Judge |
| --- | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 50 | 3 | 77.027 | 8.107 |
| In-Context Oracle | 50 | 3 | 78.566 | 8.796 |
| Human Reference | 50 | 1 | 66.289 | 8.500 |

## Per-Task Paired Breakdown

| Task | Base CC | Oracle CC | Delta | Base Stress | Oracle Stress | Context Std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| access_control_log | 1.667 | 1.333 | -0.333 | 100.0% | 100.0% | 0.837 |
| adversarial_spec | 1.000 | 19.000 | +18.000 | 100.0% | 100.0% | 11.296 |
| archival_binding_spec | 9.000 | 9.000 | 0.000 | 100.0% | 100.0% | 0.000 |
| async_batch_processor | 9.000 | 3.444 | -5.556 | 0.0% | 0.0% | 3.236 |
| async_rate_limiter | 4.000 | 3.667 | -0.333 | 100.0% | 66.7% | 0.408 |
| audit_log_writer | 1.333 | 3.000 | +1.667 | 0.0% | 0.0% | 0.913 |
| audit_trail_builder | 10.667 | 4.000 | -6.667 | 100.0% | 100.0% | 3.737 |
| circuit_breaker | 2.523 | 2.340 | -0.183 | 0.0% | 100.0% | 0.401 |
| cli_argument_validation | 14.000 | 4.083 | -9.917 | 100.0% | 100.0% | 5.471 |
| config_precedence_merge | 5.167 | 5.211 | +0.044 | 100.0% | 100.0% | 0.375 |
| connection_pool | 2.913 | 2.491 | -0.422 | 66.7% | 100.0% | 0.336 |
| csv_sales_aggregate | 12.000 | 4.500 | -7.500 | 100.0% | 100.0% | 5.261 |
| dedupe_event_stream | 10.000 | 4.445 | -5.555 | 100.0% | 100.0% | 3.053 |
| dependency_order | 14.000 | 4.533 | -9.467 | 100.0% | 100.0% | 5.233 |
| event_correlator | 11.333 | 4.267 | -7.067 | 0.0% | 0.0% | 4.010 |
| event_windows | 9.333 | 3.111 | -6.222 | 100.0% | 100.0% | 3.544 |
| feature_flag_matrix | 4.000 | 3.000 | -1.000 | 100.0% | 100.0% | 0.548 |
| financial_reconciler | 10.000 | 6.667 | -3.333 | 100.0% | 100.0% | 2.875 |
| hierarchical_flattener | 4.333 | 4.333 | 0.000 | 100.0% | 100.0% | 1.169 |
| incident_desk_spec | 5.667 | 8.000 | +2.333 | 100.0% | 100.0% | 2.563 |
| input_sanitizer | 5.000 | 3.500 | -1.500 | 100.0% | 100.0% | 0.987 |
| inventory_reorder | 11.667 | 3.778 | -7.889 | 100.0% | 100.0% | 5.226 |
| json_path_projection | 6.667 | 5.833 | -0.833 | 100.0% | 100.0% | 0.987 |
| lazy_file_chunker | 4.667 | 6.000 | +1.333 | 100.0% | 100.0% | 1.033 |
| lazy_singleton | 2.333 | 3.000 | +0.667 | 100.0% | 100.0% | 0.365 |
| legacy_invoice_spec | 7.667 | 9.333 | +1.667 | 100.0% | 100.0% | 1.049 |
| log_aggregator | 4.000 | 4.667 | +0.667 | 100.0% | 100.0% | 0.408 |
| log_sessionizer | 11.000 | 5.222 | -5.778 | 100.0% | 100.0% | 3.351 |
| medical_intake_form | 13.333 | 13.000 | -0.333 | 0.0% | 0.0% | 0.753 |
| multiformat_serializer | 3.000 | 2.600 | -0.400 | 0.0% | 0.0% | 0.219 |
| nested_json_index | 9.000 | 8.333 | -0.667 | 100.0% | 100.0% | 0.816 |
| object_registry | 2.200 | 1.876 | -0.324 | 100.0% | 33.3% | 0.251 |
| paginated_api_cursor | 3.000 | 5.000 | +2.000 | 100.0% | 100.0% | 1.095 |
| permission_gate | 2.000 | 3.667 | +1.667 | 100.0% | 100.0% | 1.329 |
| policy_merge | 7.000 | 9.000 | +2.000 | 100.0% | 100.0% | 1.095 |
| priority_queue_merger | 5.000 | 6.000 | +1.000 | 100.0% | 100.0% | 1.378 |
| resource_scope | 2.067 | 2.000 | -0.067 | 100.0% | 100.0% | 0.082 |
| retry_backoff_schedule | 5.000 | 5.000 | 0.000 | 100.0% | 100.0% | 0.000 |
| retry_state_machine | 1.333 | 1.333 | 0.000 | 100.0% | 100.0% | 0.000 |
| round_robin_scheduler | 5.000 | 3.000 | -2.000 | 100.0% | 100.0% | 1.095 |
| schema_coercer | 4.000 | 3.500 | -0.500 | 100.0% | 100.0% | 0.612 |
| sliding_window_limiter | 2.333 | 2.467 | +0.133 | 100.0% | 100.0% | 0.110 |
| spec_elicitation_stub | 4.667 | 4.000 | -0.667 | 100.0% | 100.0% | 0.516 |
| state_diff_tracker | 3.000 | 4.333 | +1.333 | 0.0% | 0.0% | 1.033 |
| streaming_csv_parser | 4.667 | 5.167 | +0.500 | 100.0% | 66.7% | 2.154 |
| thread_safe_counter | 2.200 | 2.200 | 0.000 | 100.0% | 100.0% | 0.000 |
| time_series_resampler | 5.667 | 6.000 | +0.333 | 100.0% | 66.7% | 0.753 |
| timing_safe_compare | 3.667 | 4.000 | +0.333 | 100.0% | 100.0% | 0.408 |
| token_bucket_enforcer | 2.143 | 3.333 | +1.190 | 100.0% | 100.0% | 0.658 |
| ttl_cache | 2.415 | 2.429 | +0.014 | 100.0% | 100.0% | 0.102 |

## Day 2 Hard Subset

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 39 | 3 | 85.5% | 81.2% | 82.1% | 82.1% | 5.341 | 2.239 | 2.239 | 1317.598 |
| In-Context Oracle | 39 | 3 | 86.3% | 80.3% | 84.6% | 82.1% | 4.907 | 2.026 | 2.496 | 1328.214 |
| Human Reference | 39 | 1 | 100.0% | 84.6% | 84.6% | 82.1% | 4.055 | 1.821 | 1.769 | 710.923 |

Paired CC delta oracle-baseline: mean=-0.433, oracle lower=20, oracle higher=16, ties=3, Wilcoxon p=0.530.
