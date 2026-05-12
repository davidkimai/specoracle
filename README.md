# SpecOracle & SlopBench

[**Read the Paper (PDF)**](paper/SlopBench.pdf)

SpecOracle is an evaluation pipeline designed to test whether informal specifications can function as zero-cost in-context oracles for secure program synthesis. 

In secure program synthesis, specification elicitation has superseded code generation as the primary bottleneck. While executable oracles successfully restrict a model's degrees of freedom, formalizing subjective architectural quality to prevent unmaintainable "vibecoding slop" remains impractically expensive. SpecOracle investigates whether informal engineering principles (e.g., the Zen of Python) can bridge this gap by enforcing structural discipline at inference time.

To measure this, we introduce **SlopBench**: a benchmark curated specifically to induce architectural degradation, allowing researchers to empirically measure whether soft specification conditioning collapses architectural degrees of freedom without compromising functional correctness.

---

## Experimental Design and Findings

Based on comprehensive evaluation across three frontier models (Claude 4.6, GPT-5.5, Gemini 2.5 Pro) and a suite of downstream stress tests, SpecOracle provides four core empirical insights regarding agentic evaluation and structural maintainability.

### 1. Cross-Model Generalization & The Deterministic Inversion
**Soft Oracles Shift the Mode, Not Just the Mean:** Across three frontier architectures and two sampling regimes, conditioning on informal specifications yielded consistent **30-42% reductions in mean cyclomatic complexity (CC)** with minimal functional degradation. 

Crucially, this effect persists under **deterministic decoding** (GPT-5.5 at temperature 0). When a model is forced to output its single most-preferred completion, the oracle still enforces severe structural compression. This proves that soft oracles structurally shift what the model *wants to produce*, rather than merely sampling simpler variants from the tail of a probability distribution.

### 2. The CEGIS Bridge: Hybrid Oracles
**Formal Feedback from Informal Specs:** SpecOracle implements a CEGIS-inspired (Counterexample-Guided Inductive Synthesis) feedback loop via the `hybrid` mode. By coupling an informal specification prompt with hard structural gates (e.g., Radon CC threshold > 8), the system generates deterministic, targeted feedback naming specific violating functions and branch counts. 

On a 20-task proof-of-concept run, the Hybrid Oracle fired on 55% of tasks, **improving cyclomatic complexity on every single retried task** (average $\Delta$CC = -4.0) until all artifacts passed the strict complexity gate. This demonstrates that executable structural gates can instantiate formal CEGIS loops over informal specs at zero formalization cost.

### 3. Boundary Conditions: The Maintenance Null
**Epistemic Discipline in Threshold Hunting:** To assess whether structural rigor improves downstream agentic maintainability, we introduced a long-horizon chained maintenance stress test via SpecArena v2. 

At SlopBench-Min complexity across 3-step maintenance chains, we observe a **null result**: `THRESHOLD_FOUND: False`. Current frontier maintenance agents successfully brute-force feature patches on highly complex, unconstrained code with near 100% success. We report this explicitly. However, the data reveals a persistent structural advantage: **oracle-conditioned code maintains a cyclomatic complexity ~1.2 points lower than unconstrained code even after 3 rounds of context-ablated maintenance.** Finding the failure threshold requires scaling to 50+ task suites and 5-10 step chains.

### 4. Adversarial Control: Isolating Semantic Adherence
**Oracles Follow Semantics, Not Brevity Bias:** To confirm models respond to specification semantics rather than a generic pressure to "write less code," we use an adversarial control task (Task 045) requiring explicit labeled branch variables. Conditioning on this specification successfully forces the model to *increase* cyclomatic complexity, confirming strict adherence to the in-context constraint even when it conflicts with simplicity.

---

## Empirical Results (Aggregate)

*SlopBench-Min 20-task evaluation. Stochastic (n=3, T=0.8) and Deterministic (n=3, T=0.0) sampling.*

| Model | CC Avg (Base) | CC Avg (Oracle) | CC Delta | Pass@1 (Base) | Pass@1 (Oracle) | Judge Score (Oracle) |
|---|---:|---:|---:|---:|---:|---:|
| **anthropic/claude-sonnet-4-6** | 8.101 | 4.887 | **-39.7%** | 100.0% | 95.0% | 8.783 |
| **openai/gpt-5.5** *(deterministic)* | 6.876 | 4.009 | **-41.7%** | 96.7% | 93.3% | 7.850 |
| **google/models/gemini-2.5-pro** | 3.383 | 2.372 | **-29.9%** | 55.0% | 50.0% | 4.367 |

*(Note: Full evaluation outputs and intermediate generation files are locked in the `runs/` directory.)*

---

## Reviewer Quickstart

Reproduce the end-to-end evaluation pipeline using the offline `mock` provider. 

Docker is required, as generated code is executed in a highly restricted sandbox (no networking, dropped capabilities, read-only mounts).

```bash
# 1. Clone and Install
git clone https://github.com/davidkimai/specoracle.git
cd specoracle
python3 -m pip install -e .

# 2. Build the Pytest Sandbox Image
specoracle sandbox prepare

# 3. Run the Offline Smoke Test (Generate -> Evaluate -> Long-Horizon Stress)
specoracle run --dataset data/slopbench_min --out runs/smoke --provider mock --judge-provider mock --samples 1
specoracle stress --run-dir runs/smoke --dataset data/slopbench_min --provider mock --context-ablation
specoracle validate --run-dir runs/smoke --dataset data/slopbench_min --samples 1 --context-ablation
```

---

## Full Benchmark Evaluation

To run real model evaluations against Anthropic, OpenAI, or Google models, install the relevant provider extras and export your API keys.

```bash
python3 -m pip install -e '.[anthropic,openai,google]'
export ANTHROPIC_API_KEY="your_api_key"
export OPENAI_API_KEY="your_api_key"
export GEMINI_API_KEY="your_api_key"

# 1. Generate solutions and evaluate static metrics + functional tests
specoracle run \
  --dataset data/slopbench_min \
  --out runs/slopbench_min_hybrid_claude \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --modes hybrid \
  --max-cc 6 \
  --hybrid-max-retries 3 \
  --samples 1 \
  --temperature 0.8 \
  --require-temperature

# 2. Run the Long-Horizon Maintenance Stress Test
specoracle stress \
  --run-dir runs/slopbench_min_hybrid_claude \
  --dataset data/slopbench_min \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --temperature 0.8 \
  --chain-depth 3 \
  --context-ablation

# 3. Analyze Chains and Compile Tables
python3 scripts/analyze_chain.py runs/slopbench_min_hybrid_claude
```

---

## Dataset Schema & Architecture

The repository contains two SlopBench splits:
- `data/slopbench_min/`: The locked 20-task pilot split used for cross-model evidence.
- `data/slopbench/`: The full 50-task benchmark containing adversarial controls, async patterns, and object lifecycle management tasks.

### Core Architecture
- `src/specoracle/config.py`: Prompt templates and the Zen oracle specification.
- `src/specoracle/generator.py`: LLM routing logic for baseline, oracle, and hybrid generation.
- `src/specoracle/hybrid.py`: CEGIS-inspired feedback loop generating structured gate failure reports.
- `src/specoracle/evaluator.py`: Static structural metrics (Radon, AST nesting depth) and subprocess Dockerized pytest execution.
- `src/specoracle/stress.py`: SpecArena v2 downstream maintenance-agent stress testing environment.
- `integrations/inspect/`: Pre-submission export stub aligning metrics with the UK AISI `inspect_evals` schema.
