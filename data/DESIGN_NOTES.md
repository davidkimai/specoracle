# SlopBench Day 2 Stress Taxonomy

This document pre-commits the structural properties used to design Day 2
maintenance tasks. The goal is to evaluate whether existing code structure
helps a maintenance agent modify code, not to tune tasks toward a preferred
outcome.

Every task declares one or more `day2_stressors` from this taxonomy.

## Stressors

- `parameter_threading`: the change introduces a parameter or option whose
  value must be propagated through multiple logical stages or helper calls.
- `interface_generalization`: the public API must accept a broader input shape
  or expose a compatible extension without breaking original behavior.
- `streaming_compatibility`: the implementation must handle iterators or
  generator-like inputs without assuming eager list materialization.
- `cross_function_state`: the change requires state to stay coherent across
  multiple methods, helper functions, or calls.
- `audit_provenance`: the change adds review-facing explanations, audit logs,
  source labels, or provenance rows that must match the behavior.
- `error_surface_expansion`: the change adds stricter validation or richer
  failure modes while preserving existing successful cases.
- `backwards_compatibility`: old tests and calling conventions must continue to
  work after the Day 2 feature is added.

## Hard Subset

Tasks tagged `day2-hard` combine at least two stressors or require an update
across multiple structural sites. This tag is assigned before new real-model
results are inspected and is used only for subgroup analysis.

## Post-Study Note

The `legacy_invoice_spec` custom oracle illustrates that informal specs can
deliberately trade lower CC for higher auditability. Corporate Legacy Spec
QX-17 asks for explicit local branch labels around monetary decisions, so the
oracle can increase decision-count metrics while better satisfying the intended
review surface. This is expected behavior and a research finding in itself.

## Expansion: SlopBench Full (Tasks 021-050)

The full benchmark adds five category pillars beyond SlopBench-Min:

- **Async / Generator Patterns:** exposes eager-buffering slop, misplaced async
  context, and accidental loss of streaming behavior.
- **Reliability-Critical Patterns:** tests correctness-critical code paths for
  auditability, validation discipline, access control, rate enforcement, and
  structured logging.
- **Object Lifecycle / Resource Management:** targets leaked handles,
  double-close behavior, stale object state, and initialization-order bugs.
- **Advanced Data Pipelines:** exercises transformations that often trigger
  monolithic, nested implementations.
- **Custom-Spec and Adversarial-Spec:** five domain-specific custom oracles plus
  additional cross-cutting custom specs. Task 045 is a pre-registered
  adversarial spec designed to increase CC through explicit labeled branches.

The adversarial spec (`045_adversarial_spec`, tagged `adversarial_spec`) is a
control task. If the oracle reduces CC on task 045, that would weaken the claim
that CC movement follows the oracle's actual content rather than a generic
model-side preference for shorter code. If CC increases, it supports the claim
that the active informal spec is shaping structure, even when the spec's values
trade minimal branching for auditability.

Final stressor coverage in `data/slopbench/`:

| Stressor | Count |
| --- | ---: |
| `parameter_threading` | 12 |
| `interface_generalization` | 21 |
| `streaming_compatibility` | 7 |
| `cross_function_state` | 18 |
| `audit_provenance` | 17 |
| `error_surface_expansion` | 14 |
| `backwards_compatibility` | 50 |
