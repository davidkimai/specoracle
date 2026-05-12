---
name: dafny-formal-verification
description: Use this to mathematically guarantee zero race conditions and logical correctness via Dafny formal verification.
license: MIT
---

# Dafny Formal Verification

Use Dafny when the task needs a hard correctness oracle rather than a style
oracle. First write the behavior as a small verified Dafny program, then compile
the executable subset to Python. Keep the proof small enough that the compiled
Python remains understandable.

## Core Shape

- Put executable behavior in `method` bodies. Use `function` only for pure specs
  or simple executable expressions.
- Use `requires` for caller obligations and input bounds.
- Use `ensures` for the postcondition that must prove the result is correct.
- Use `invariant` on loops to preserve the facts needed by the final `ensures`.
- Use `decreases` on recursive functions or loops when termination is not obvious.
- Use `assert` sparingly to expose one proof step at a time.
- Use ghost variables only for proof bookkeeping. Do not let ghost state drive
  executable behavior, because it is erased from compiled Python.

## Race-Free State

- Prefer pure values, sequences, maps, and explicit state transitions.
- If mutable state is needed, make the ownership and update frame explicit with
  `modifies`.
- Prove each transition preserves the invariant before adding convenience code.
- Avoid hidden global state and callbacks. They make both the proof and compiled
  target harder to audit.

## Python Compilation Discipline

- Keep datatypes, generics, and higher-order constructs minimal.
- Avoid proof-only helper layers that do not affect executable code.
- Favor straight-line methods plus small loops with clear invariants.
- Do not add a Dafny abstraction unless it either proves a required property or
  reduces duplicated executable logic.
- After verification, inspect the compiled Python and measure complexity on that
  compiled Python, not on the `.dfy` source.

## Minimal Template

```dafny
method Clamp(x: int, lo: int, hi: int) returns (y: int)
  requires lo <= hi
  ensures lo <= y <= hi
  ensures x < lo ==> y == lo
  ensures lo <= x <= hi ==> y == x
  ensures hi < x ==> y == hi
{
  if x < lo {
    y := lo;
  } else if hi < x {
    y := hi;
  } else {
    y := x;
  }
}
```
