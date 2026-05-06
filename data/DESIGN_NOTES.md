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
