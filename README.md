# SpecOracle & SlopBench: Exposing the "Blind Spot" in Agentic Evaluation

[**Read the Paper (PDF)**](paper/SlopBench.pdf)

SpecOracle is a Python evaluation pipeline for testing whether informal specifications can act as zero-cost in-context oracles for secure program synthesis. 

Current frontier models often generate "vibecoding slop"---code that passes functional unit tests but degrades into unmaintainable architectural debt. While formalizing subjective architectural quality is impractically expensive, we hypothesize that informal engineering principles (like the Zen of Python) can bridge this gap. 

**SlopBench** is our 50-task benchmark curated specifically to induce architectural degradation, allowing researchers to empirically measure whether soft specification conditioning collapses architectural degrees of freedom without breaking tests.

---

## The Three-Act Empirical Study

Based on a comprehensive run using Claude Sonnet 4.6, SpecOracle exposes a critical vulnerability in current agentic evaluations.

### Act 1: The Pilot (Collapsing Degrees of Freedom)
**Soft Oracles Work:** On a locked 20-task pilot split known to induce high baseline complexity, conditioning on informal specs yielded a **40% reduction in cyclomatic complexity** (8.101 down to 4.887, $p=0.004$) while maintaining a 95% functional pass rate. The model actively modularized the code rather than merely writing denser monolithic scripts.

### Act 2: Adversarial Control
**Oracles Follow Semantics, Not Just Brevity:** To prove the model isn't just defaulting to "shorter code," we introduced an adversarial task (Task 045) requiring explicit labeled branch variables. Conditioning on this specification successfully forced the model to *increase* cyclomatic complexity by +18.0 points, confirming that the LLM is strictly obeying specification semantics.

### Act 3: The Maintenance "Blind Spot"
**Standard Evaluations Mask Structural Slop:** We introduced a "Day 2" maintenance stress test to see if cleaner architecture improved downstream agentic maintainability. Surprisingly, context-ablation revealed a null result: current frontier maintenance agents can brute-force maintenance patches on toxic "vibecoded" slop with near 100% success, even with ablated context. 
> 🚨 **The Blind Spot:** Because frontier models can brute-force localized architectural debt, standard pass/fail agentic evaluations actively mask structural rot. We must enforce static structural discipline via soft oracles to prevent technical debt from silently accumulating beyond human auditability.

---

## Empirical Results (Act 3 Aggregate)

*Full 50-task scale evaluation, Claude Sonnet 4.6, n=3 samples, temperature 0.8.*

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Context P@1 | CC Avg | Nesting | Functions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 20 | 3 | 100.0% | 100.0% | 100.0% | 8.101 | 2.533 | 1.683 |
| In-Context Oracle | 20 | 3 | 95.0% | 96.7% | 100.0% | **4.887** | **2.100** | **2.683** |
| Human Reference | 20 | 1 | 100.0% | 100.0% | 100.0% | 4.492 | 2.000 | 2.200 |

*(Note: The above table reflects the legacy `SlopBench-Min` 20-task pilot for exact reproduction mapping. Full 50-task outputs are available in `runs/slopbench_full_claude/summary.csv`.)*

---

## Reviewer Quickstart (Zero-Friction Reproduction)

Reproduce the end-to-end evaluation pipeline in under 60 seconds using the offline `mock` provider. 

Docker is required, as generated code is executed in a highly restricted sandbox (no network, dropped capabilities, read-only mounts).

```bash
# 1. Clone and Install
git clone https://github.com/davidkimai/specoracle.git
cd specoracle
python3 -m pip install -e .

# 2. Build the Pytest Sandbox Image
specoracle sandbox prepare

# 3. Run the Offline Smoke Test (Full Pipeline: Generate -> Evaluate -> Day 2 Stress)
specoracle run --dataset data/slopbench_min --out runs/smoke --provider mock --judge-provider mock --samples 1
specoracle stress --run-dir runs/smoke --provider mock --context-ablation
specoracle validate --run-dir runs/smoke --dataset data/slopbench_min --samples 1 --context-ablation
```

---

## Evaluating on SlopBench (Frontier Models)

To run the full 50-task `SlopBench` benchmark against a real frontier model (e.g., Anthropic), install the provider extras and export your API key.

```bash
python3 -m pip install -e '.[anthropic]'
export ANTHROPIC_API_KEY="your_key_here"

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

# 3. Validate and build tables
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

### Core Files
- `src/specoracle/config.py`: Prompt templates and the Zen oracle spec.
- `src/specoracle/generator.py`: LLM routing (Baseline vs. Oracle).
- `src/specoracle/evaluator.py`: Radon structural metrics, AST nesting depth, and subprocess Dockerized pytest execution.
- `src/specoracle/stress.py`: SpecArena Day 2 maintenance-agent stress testing.
