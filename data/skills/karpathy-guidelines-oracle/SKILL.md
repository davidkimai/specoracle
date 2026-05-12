---
name: karpathy-guidelines-oracle
description: >-
  SlopBench soft oracle derived from Andrej Karpathy's behavioral guidelines
  for LLM coding (https://github.com/forrestchang/andrej-karpathy-skills).
  Enforces simplicity-first design, surgical changes, and goal-driven
  execution as structural constraints.
  Pipeline: https://github.com/davidkimai/specoracle
license: MIT
---

# Karpathy Guidelines Oracle

Treat the Karpathy Guidelines as an informal in-context oracle for structural
quality. The oracle is not a style preference layer; it is a degree-of-freedom
collapse over the implementation space. Preserve functional correctness while
choosing the simplest architecture that satisfies the task.

## Operational Constraints

Derived from Andrej Karpathy's observations on LLM coding pitfalls:

- Think before coding: state assumptions explicitly; if uncertain about a design
  choice, choose the most conservative interpretation.
- Simplicity first: write the minimum code that solves the problem. No features
  beyond what was asked. No abstractions for single-use code. No speculative
  flexibility or configurability. If you write 200 lines and it could be 50,
  rewrite it.
- Surgical changes: touch only what you must. Do not improve adjacent code,
  comments, or formatting. Match existing style even if you would do it
  differently.
- Goal-driven execution: define verifiable success criteria. Every function
  should have a clear, testable contract. Prefer writing tests first, then
  implementation.
