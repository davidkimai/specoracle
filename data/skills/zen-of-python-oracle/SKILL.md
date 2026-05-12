---
name: zen-of-python-oracle
description: >-
  SlopBench soft oracle enforcing the Zen of Python (PEP 20) as structural
  quality constraints during LLM code generation. Conditions outputs toward
  simplicity, flatness, explicitness, and local auditability.
  Pipeline: https://github.com/davidkimai/specoracle
license: MIT
---

# Zen of Python Oracle

Treat the Zen of Python as an informal in-context oracle for structural quality.
The oracle is not a style preference layer; it is a degree-of-freedom collapse
over the implementation space. Preserve functional correctness while choosing
the simplest architecture that satisfies the task.

## Operational Constraints

- Prefer small pure helpers over monolithic functions.
- Keep control flow flat; avoid deep nesting when guard clauses or extraction work.
- Make data movement explicit; avoid hidden mutation and implicit global state.
- Raise clear errors for invalid inputs instead of silently guessing.
- Choose ordinary standard-library constructs over clever metaprogramming.
- Use names that make the implementation easy to explain.
- Avoid speculative abstractions, framework-shaped code, and unused extension points.
- Keep code sparse enough that a maintainer can audit behavior locally.

## Zen of Python Primitives

- Beautiful is better than ugly.
- Explicit is better than implicit.
- Simple is better than complex.
- Complex is better than complicated.
- Flat is better than nested.
- Sparse is better than dense.
- Readability counts.
- Special cases are not special enough to break the rules.
- Although practicality beats purity.
- Errors should never pass silently.
- Unless explicitly silenced.
- In the face of ambiguity, refuse the temptation to guess.
- There should be one obvious way to do it.
- Although that way may not be obvious at first unless you are Dutch.
- Now is better than never.
- Although never is often better than right now.
- If the implementation is hard to explain, it is a bad idea.
- If the implementation is easy to explain, it may be a good idea.
- Namespaces are one honking great idea -- let's do more of those!
