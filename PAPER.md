# SpecOracle: Informal Specs as In-Context Oracles

## Paper Scaffolding - Pre-Writing Technical Extraction

This file is not the paper. It is the locked technical extraction that should
feed the LaTeX writing pass.

## Headline Result

Oracle conditioning with the Zen of Python reduces mean cyclomatic complexity
from 8.101 to 4.887, a 39.7% reduction, across 20 SlopBench-Min tasks with n=3
replicated samples at temperature 0.8 on Claude Sonnet 4.6.

Wilcoxon signed-rank p=0.004 on all tasks and p=0.023 on the day2-hard subset.
The effect is directionally consistent on the GPT-5.5 deterministic six-task
reference run, where mean CC falls from 8.389 to 4.356.

## Key Measurements

- Functional correctness: Oracle 95.0% pytest pass vs. Baseline 100.0%.
- CC: Baseline 8.101 -> Oracle 4.887 -> Human Reference 4.492.
- Nesting: Baseline 2.533 -> Oracle 2.100 -> Human Reference 2.000.
- Function count: Baseline 1.683 -> Oracle 2.683 -> Human Reference 2.200.
- Judge score: Baseline 7.800 -> Oracle 8.783.
- Maintenance token overhead: Baseline 1257.200 -> Oracle 1344.150.
- Context ablation: 100.0% across all variants for stub context. This weakens
  the downstream maintainability claim and suggests the Day 2 task mostly
  measures Claude Sonnet 4.6 feature-implementation capability in this run.
- Neutral-style ablation: CC average 8.222 on the original six smoke tasks.
  Generic "clean, maintainable Python" prompting does not produce the same
  structural reduction as the Zen oracle.

## Contributions

1. SlopBench-Min: A 20-task pre-registered curated benchmark for structural
   degradation in LLM-generated Python, with human gold references, custom
   informal specs, and Day 2 maintenance tasks.
2. SpecOracle: An open-source evaluation pipeline implementing dual-axis
   assessment through static metrics and LLM-as-a-Judge, with Dockerized secure
   execution of generated code.
3. SpecArena: A Day 2 maintenance stress protocol with context-ablation checks
   for measurement validity.
4. Empirical evidence: A replicated n=3 pilot showing informal spec
   conditioning significantly reduces cyclomatic complexity while preserving
   near-complete functional correctness.

## Full Benchmark Artifact

`data/slopbench/` is the 50-task standalone SlopBench benchmark. It keeps the
20-task pilot split byte-identical as tasks 001-020 and adds tasks 021-050
across async/generator patterns, reliability-critical code, object lifecycle
management, advanced data pipelines, and custom/adversarial informal specs.
Current paper claims should continue to cite the locked `slopbench_min` Claude
run; the full split is the community/release artifact for future model runs and
appendix-level smoke validation.

## Limitations

- Context ablation shows maintenance agents can often succeed without useful
  existing-code context. This is an honest null result on the strongest
  downstream maintainability claim.
- SlopBench-Min has 20 tasks. It is a pilot benchmark, not the full 50-task
  benchmark roadmap.
- Tasks are Python-only.
- Zen of Python is likely present in frontier-model pre-training. The
  memorization confound is partially addressed through three
  `custom_spec_override` tasks and cross-model directional consistency, but not
  eliminated.
- Human references were authored as part of the benchmark design process, not
  by independent external reviewers.
- LLM-as-a-Judge scores are supporting diagnostics, not ground truth.

## Legacy Invoice Nuance

The `legacy_invoice_spec` custom oracle intentionally raises CC for the oracle
variant. Corporate Legacy Spec QX-17 requires explicit branch-label local
variables for monetary decisions. That makes the code more locally auditable but
mechanically increases decision points. This is a spec-priority tradeoff, not a
conditioning failure.

## Citation Checklist (Confirmed)

### Primary Theoretical Context

- Quinn and Max von Hippel. 2026. "Lies, Damned Lies, and Proofs: Formal
  Methods are not Slopless." LessWrong. January 12, 2026.
  https://www.lesswrong.com/posts/rhAPh3YzhPoBNpgHg/lies-damned-lies-and-proofs-formal-methods-are-not-slopless
  Key use: formal verification does not automatically remove structural slop;
  specification elicitation and validation remain bottlenecks.
- Max von Hippel, Simon Henniger, Quinn Dougherty, and miyazono. 2026. "How to
  Solve Secure Program Synthesis." LessWrong. March 30, 2026.
  https://www.lesswrong.com/posts/8wtrLoDPyCfMLuHkt/how-to-solve-secure-program-synthesis
  Key use: SPS should be attacked directly rather than by proxy; specification
  is one of the hard central problems.
- Mike Dodds. 2025. "Specifications Don't Exist." Galois Blog. June 16, 2025.
  https://www.galois.com/articles/specifications-dont-exist
  Key use: complete coherent formal specifications are absent for many real
  systems; informal specifications can be wrong but useful communication tools.
- John Regehr. 2026. "Zero-Degree-of-Freedom LLM Coding using Executable
  Oracles." Blog post. March 26, 2026.
  https://john.regehr.org/writing/zero_dof_programming.html
  Key use: LLM coding improves when executable oracles collapse
  failure-producing degrees of freedom; SpecOracle tests whether informal specs
  can act as weaker structural oracles.

### Closest Technical Prior Work

- Daniel Melcer, Sujan Gonugondla, Pramuditha Perera, Haifeng Qian,
  Wen-Hao Chiang, Yanjun Wang, Nihal Jain, Pranav Garg, Xiaofei Ma, and Anoop
  Deoras. 2024. "Approximately Aligned Decoding." arXiv:2410.01103.
  https://arxiv.org/abs/2410.01103
  Key use: spec-conditioned decoding that balances distribution distortion with
  computational efficiency.
- Remy Wang. "Counterexample-guided Inductive Synthesis." Primer.
  Key use: formal spec-driven synthesis through oracle feedback loops.

### Empirical / Evaluation Methods

- Mark Chen et al. 2021. "Evaluating Large Language Models Trained on Code."
  arXiv:2107.03374. https://arxiv.org/abs/2107.03374
  Key use: HumanEval and the unbiased Pass@k estimator used in `analyze.py`.
- Lianmin Zheng et al. 2023. "Judging LLM-as-a-Judge with MT-Bench and Chatbot
  Arena." arXiv:2306.05685. https://arxiv.org/abs/2306.05685
  Key use: LLM-as-a-Judge methodology.
- Frank Wilcoxon. 1945. "Individual comparisons by ranking methods."
  Biometrics Bulletin. Key use: paired signed-rank significance reporting.

### Python / Measurement Tools

- Tim Peters. 2004. "The Zen of Python." PEP 20.
  https://peps.python.org/pep-0020/
  Key use: the default informal oracle for `oracle_generation`.
- Radon. Python static analysis package. https://radon.readthedocs.io/
  Key use: cyclomatic complexity and maintainability index.

## Differentiation from Melcer et al.

Approximately Aligned Decoding constrains LLM decoding using hard constraints at
the token distribution level. SpecOracle conditions at the prompt level using
informal philosophical principles and measures whether this soft conditioning
produces structurally different outputs. The approaches are complementary:
AprAD asks whether constraints can be enforced mechanically during generation;
SpecOracle asks whether informal specs work as soft oracles without decoding
machinery.

## Differentiation from Regehr

Regehr's framework requires strong executable oracles such as fuzzers,
property-based testers, and reference implementations to approach zero degrees
of freedom. SpecOracle is a direct empirical test of the weaker case: whether
informal specs can collapse structural degrees of freedom at prompt cost. The
40% CC reduction (p=0.004) suggests that informal Zen-of-Python conditioning
does collapse some structural freedom, while the context-ablation null result
supports Regehr's skepticism about using informal structure alone as a
functional maintenance oracle.
