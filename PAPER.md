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

## Citation Checklist

- Zen of Python: Tim Peters, PEP 20.
- Radon: Python static analysis package used for CC and MI.
- Chen et al. 2021: Evaluating Large Language Models Trained on Code, including
  HumanEval and the unbiased Pass@k estimator.
- Wilcoxon signed-rank test.
- LLM-as-a-Judge / MT-Bench: Zheng et al. 2023.
- Docker sandboxing and container security references for untrusted code
  execution.
- Secure program synthesis and executable-oracle framing.

## Citations to Verify

These works are referenced in the fellowship proposal and must be verified as
citable publications before inclusion in the paper bibliography. If any are
informal references, replace them with the underlying formal work they describe.

- "Lies, Damned Lies, and Proofs" by Quinn Dougherty and Max von Hippel.
- "Specifications Don't Exist" by Mike Dodds.
- "Approximately Aligned Decoding" by Melcer et al.
- John Regehr's "collapse the degrees of freedom" framing for executable
  oracles.
