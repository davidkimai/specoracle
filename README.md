# SpecOracle & SlopBench

[**Read the Paper (PDF)**](paper/SlopBench.pdf)

SpecOracle is an evaluation pipeline designed to test whether informal specifications can function as zero-cost in-context oracles for secure program synthesis. 

In secure program synthesis, specification elicitation has superseded code generation as the primary bottleneck. While executable oracles successfully restrict a model's degrees of freedom, formalizing subjective architectural quality remains impractically expensive. SpecOracle investigates whether informal engineering principles (e.g., the Zen of Python) can bridge this gap by enforcing structural discipline at inference time.

To measure this, we introduce **SlopBench**: a 50-task benchmark curated specifically to induce architectural degradation, allowing researchers to empirically measure whether soft specification conditioning collapses architectural degrees of freedom without compromising functional correctness.

---

## Experimental Design and Findings

Based on a comprehensive evaluation using Claude Sonnet 4.6, SpecOracle provides three core empirical insights regarding agentic evaluation and structural maintainability.

### 1. The Pilot: Collapsing Degrees of Freedom
**Soft Oracles Reduce Complexity:** On a locked 20-task pilot split known to induce high baseline complexity, conditioning on informal specifications yielded a **40% reduction in mean cyclomatic complexity** (8.101 down to 4.887, $p=0.004$) while maintaining a 95% functional pass rate. The model actively modularized the code rather than merely generating denser monolithic scripts.

### 2. Adversarial Control: Isolating Semantic Adherence
**Oracles Follow Semantics, Not Brevity Bias:** To confirm that models respond to specification semantics rather than a generic pressure to "write less code," we introduced an adversarial control task (Task 045) requiring explicit labeled branch variables. Conditioning on this specification successfully forced the model to increase cyclomatic complexity by +18.0 points, confirming strict adherence to the in-context structural constraint.

### 3. Boundary Conditions: The Maintenance Blind Spot
**Pass/Fail Evaluations Mask Structural Degradation:** To assess whether structural rigor improves downstream agentic maintainability, we introduced a "Day 2" maintenance stress test. Context-ablation revealed a null result: current frontier maintenance agents successfully brute-force feature patches on highly complex, unconstrained code with near 100% success, even with ablated context. Because frontier models can presently brute-force localized architectural debt, standard pass/fail agentic evaluations actively mask structural degradation. This highlights the necessity of enforcing static structural discipline via soft oracles to ensure long-term human auditability.

---

## Empirical Results (Aggregate)

*SlopBench-Min 20-task pilot evaluation, Claude Sonnet 4.6, n=3 samples, temperature 0.8.*

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Context P@1 | CC Avg | Nesting | Functions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 20 | 3 | 100.0% | 100.0% | 100.0% | 8.101 | 2.533 | 1.683 |
| In-Context Oracle | 20 | 3 | 95.0% | 96.7% | 100.0% | **4.887** | **2.100** | **2.683** |
| Human Reference | 20 | 1 | 100.0% | 100.0% | 100.0% | 4.492 | 2.000 | 2.200 |

*(Note: Full 50-task scale evaluation outputs are available in `runs/slopbench_full_claude/summary.csv`.)*

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

# 3. Run the Offline Smoke Test (Generate -> Evaluate -> Day 2 Stress)
specoracle run --dataset data/slopbench_min --out runs/smoke --provider mock --judge-provider mock --samples 1
specoracle stress --run-dir runs/smoke --provider mock --context-ablation
specoracle validate --run-dir runs/smoke --dataset data/slopbench_min --samples 1 --context-ablation
```

---

## Full Benchmark Evaluation

To run the full 50-task `SlopBench` benchmark against Anthropic models, install the provider extras and export your API key.

```bash
python3 -m pip install -e '.[anthropic]'
export ANTHROPIC_API_KEY="your_api_key_here"

# 1. Generate solutions and evaluate static metrics + functional tests
specoracle run \
  --dataset data/slopbench \
  --out runs/slopbench_full_claude \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --judge-provider anthropic \
  --judge-model claude-sonnet-4-6 \
  --modes baseline oracle \
  --samples 3 \
  --temperature 0.8 \
  --require-temperature

# 2. Run the Day 2 Maintenance Stress Test
specoracle stress \
  --run-dir runs/slopbench_full_claude \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --temperature 0.8 \
  --require-temperature \
  --context-ablation

# 3. Validate and compile tables
specoracle validate \
  --run-dir runs/slopbench_full_claude \
  --dataset data/slopbench \
  --samples 3 \
  --context-ablation

python3 scripts/analyze.py \
  runs/slopbench_full_claude/summary.csv \
  --dataset data/slopbench \
  --markdown-out runs/slopbench_full_claude/comparison.md \
  --latex-out runs/slopbench_full_claude/comparison.tex
```

---

## Dataset Schema & Architecture

The repository contains two SlopBench splits:
- `data/slopbench_min/`: The locked 20-task pilot split used for baseline evidence.
- `data/slopbench/`: The full 50-task benchmark containing adversarial controls, async patterns, and object lifecycle management tasks.

### Core Architecture
- `src/specoracle/config.py`: Prompt templates and the Zen oracle specification.
- `src/specoracle/generator.py`: LLM routing logic for baseline versus oracle generation.
- `src/specoracle/evaluator.py`: Static structural metrics (Radon, AST nesting depth) and subprocess Dockerized pytest execution.
- `src/specoracle/stress.py`: SpecArena Day 2 maintenance-agent stress testing environment.
