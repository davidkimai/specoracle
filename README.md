# SpecOracle

SpecOracle is a Python evaluation pipeline for testing whether informal
specifications can act as in-context oracles for secure program synthesis.

The core experiment is simple:

1. Generate a baseline implementation from a functional prompt.
2. Generate an oracle implementation from the same prompt plus an informal
   structural spec: Zen by default, or a task-local `custom_spec_override`.
3. Verify functional correctness with programmatic `pytest`.
4. Measure structural degradation with `radon` and standard-library `ast`.
5. Optionally ask an LLM judge to score adherence to the informal oracle.
6. Run a Day 2 maintenance stress test in SpecArena.
7. Compare generated code against human-written reference implementations.

This gives researchers a concrete way to test whether soft specification
conditioning collapses architectural degrees of freedom without breaking tests.

## Install

```bash
python3 -m pip install -e .
```

Docker is required for evaluation and stress testing. Generated code is treated
as untrusted and executed in a transient container with networking disabled,
memory/CPU limits, dropped Linux capabilities, a read-only bind mount, and a
temporary writable `/tmp`.

Prepare the pytest sandbox image once before evaluation:

```bash
specoracle sandbox prepare
```

For Anthropic models:

```bash
python3 -m pip install -e '.[anthropic]'
```

## Offline Smoke Run

The repo includes a 20-task `slopbench_min` dataset for local benchmark runs.
It covers JSON handling, state machines, concurrency, config parsing, CLI
validation, retry schedules, and data pipelines, including task-local custom
specs designed to test the memorization-confound objection. Day 2 maintenance
tasks are documented against the pre-committed stress taxonomy in
`data/DESIGN_NOTES.md`. The mock provider does not call any API and exists only
to prove the harness end to end.

```bash
specoracle sandbox prepare

specoracle run \
  --dataset data/slopbench_min \
  --out runs/smoke \
  --provider mock \
  --judge-provider mock \
  --samples 3
```

Run the Day 2 SpecArena maintenance test:

```bash
specoracle stress \
  --run-dir runs/smoke \
  --provider mock \
  --context-ablation

specoracle validate \
  --run-dir runs/smoke \
  --dataset data/slopbench_min \
  --samples 3 \
  --context-ablation
```

The run writes:

- `solution.py`: generated candidate module
- `generation.json`: prompt, provider, mode, and raw model output
- `evaluation.json`: static metrics, pytest result, and judge result
- `day2_solution.py`: maintenance-agent replacement module
- `stress.json`: Day 2 Pass@1, failure type, token-overhead estimate, and pytest result
- `summary.csv`: one row per task, artifact variant, and sample index

## Real Model Run

Set API keys in the shell before running real models. Do not commit them, paste
them into scripts, or include them in run artifacts.

```bash
test -n "${ANTHROPIC_API_KEY:-}"

specoracle sandbox prepare
```

Run a one-task Claude probe before any full replicated run:

```bash
specoracle run \
  --dataset data/slopbench_min --limit 1 \
  --out runs/claude_probe \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --judge-provider anthropic \
  --judge-model claude-sonnet-4-6 \
  --modes baseline oracle \
  --samples 1 \
  --temperature 0.8 \
  --require-temperature
```

Inspect the probe before continuing: `effective_temperature` should be `0.8`,
the generated `solution.py` files should parse as Python, pytest should have
been attempted, and judge scores should be parsed into JSON.

Run the stress/context-ablation probe:

```bash
specoracle stress \
  --run-dir runs/claude_probe \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --temperature 0.8 \
  --require-temperature \
  --context-ablation
```

Only after both probes pass, run the full replicated Claude study:

```bash
specoracle run \
  --dataset data/slopbench_min \
  --out runs/claude_replicated \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --judge-provider anthropic \
  --judge-model claude-sonnet-4-6 \
  --modes baseline oracle \
  --samples 3 \
  --temperature 0.8 \
  --require-temperature

specoracle stress \
  --run-dir runs/claude_replicated \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --temperature 0.8 \
  --require-temperature \
  --context-ablation

specoracle validate \
  --run-dir runs/claude_replicated \
  --dataset data/slopbench_min \
  --samples 3 \
  --context-ablation
```

The generator and judge use the same `LLMClient` interface, so cross-model runs
can swap providers, but do not merge summaries from runs with different model,
temperature, sample count, or task coverage into one aggregate table.

`--require-temperature` makes replicated runs fail fast if the model/API rejects
temperature control. This prevents n=3 tables from being presented as
independent samples when the provider behaved deterministically.

The supplementary neutral-style ablation is intentionally run on the original
six smoke tasks, not a randomized subset:

```bash
specoracle run \
  --dataset data/slopbench_min \
  --limit 6 \
  --out runs/claude_neutral_ablation \
  --provider anthropic \
  --model claude-sonnet-4-6 \
  --judge-provider anthropic \
  --judge-model claude-sonnet-4-6 \
  --modes neutral_style \
  --samples 3 \
  --temperature 0.8 \
  --require-temperature
```

## Paper Tables

Generate reviewer-facing comparison tables separately for each evidence regime:

```bash
python3 scripts/analyze.py \
  runs/claude_replicated/summary.csv \
  --dataset data/slopbench_min \
  --markdown-out runs/claude_replicated/comparison.md \
  --latex-out runs/claude_replicated/comparison.tex

python3 scripts/analyze.py \
  runs/sample/summary.csv \
  --dataset data/slopbench_min \
  --markdown-out runs/cross_model/gpt55_comparison.md \
  --latex-out runs/cross_model/gpt55_comparison.tex
```

The script reports `Vibecoded Baseline`, `In-Context Oracle`,
`Neutral Style`, and `Human Reference` rows over pytest pass rate, Day 2
maintenance Pass@1, Chen et al. Pass@3, context-ablation Pass@1, cyclomatic
complexity, nesting depth, function count, and maintenance token overhead. It
also emits a supplementary MI table, per-task paired baseline-vs-oracle deltas,
inter-sample CC variance checks, and a Wilcoxon signed-rank p-value for paired
CC means. Markdown output is README-ready; LaTeX output is paper-ready for the
ETAPS/TACAS table path.

The repo can track sanitized `runs/sample/`, `runs/claude_probe/`,
`runs/claude_replicated/`, `runs/claude_neutral_ablation/`, and
`runs/cross_model/` evidence. Other run directories remain ignored by default.

## Results

Primary evidence is the Claude Sonnet 4.6 replicated run:
20 SlopBench tasks, n=3 samples for generated variants, temperature 0.8, and
context ablation enabled. The run validates at 140 rows:
20 human-reference rows plus 120 generated rows.

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 20 | 3 | 100.0% | 100.0% | 100.0% | 100.0% | 8.101 | 2.533 | 1.683 | 1257.200 |
| In-Context Oracle | 20 | 3 | 95.0% | 96.7% | 100.0% | 100.0% | 4.887 | 2.100 | 2.683 | 1344.150 |
| Human Reference | 20 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 4.492 | 2.000 | 2.200 | 851.550 |

Paired CC delta oracle-baseline: mean=-3.214, oracle lower=13 tasks, oracle
higher=4 tasks, ties=3 tasks, Wilcoxon p=0.004. On the `day2-hard` subset, the
oracle also lowers CC with mean delta -2.959 and Wilcoxon p=0.023.

Measurement-validity result: context ablation performs as well as real-context
maintenance for baseline and human-reference code, and better than real-context
maintenance for the oracle variant in this run. This means Day 2 Pass@1 should
be interpreted as mostly measuring Claude's feature-implementation capability,
not strong evidence that the maintenance agent depends on code-structure
quality. The structural result remains positive: oracle conditioning
substantially reduces cyclomatic complexity while preserving near-complete
functional correctness.

The supplementary neutral-style ablation covers the original six smoke tasks,
not a randomized full-benchmark condition:

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Neutral Style | 6 | 3 | 100.0% | 100.0% | 100.0% | 100.0% | 8.222 | 2.611 | 1.667 | 955.778 |
| Human Reference | 6 | 1 | 100.0% | 100.0% | 100.0% | 100.0% | 5.722 | 1.833 | 1.667 | 733.667 |

GPT-5.5 is kept as a separate deterministic reference snapshot, not merged into
the Claude aggregate. It covers the older six-task sample with n=1 and no
context-ablation data because the API rejected temperature control:

| Variant | Tasks | Samples | Pytest | Maint. P@1 | Maint. P@3 | Context P@1 | CC Avg | Nesting | Functions | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vibecoded Baseline | 6 | 1 | 100.0% | 100.0% | 100.0% | -- | 8.389 | 2.333 | 2.000 | 1022.000 |
| In-Context Oracle | 6 | 1 | 100.0% | 100.0% | 100.0% | -- | 4.356 | 1.833 | 3.333 | 1155.333 |
| Human Reference | 6 | 1 | 100.0% | 100.0% | 100.0% | -- | 5.722 | 1.833 | 1.667 | 731.000 |

Maintainability Index is intentionally supplementary. Radon's MI can penalize
decomposed helper-heavy files even when decomposition lowers cyclomatic
complexity and nesting depth, so headline claims should prioritize CC, nesting,
function count, and Day 2/context-ablation outcomes.

## Dataset Schema

Each task is a YAML, JSON, or JSONL object:

```yaml
id: nested_json_index
entry_point: build_user_purchase_index
tags: [json, aggregation]
custom_spec_override: |
  Optional task-specific informal spec. When present, oracle_generation uses
  this instead of the Zen of Python.
prompt: |
  Functional requirements for the generated module.
test_code: |
  from solution import build_user_purchase_index

  def test_behavior():
      ...
day2_prompt: |
  New maintenance requirement that should be applied to the existing solution.
day2_test_code: |
  from solution import build_user_purchase_index

  def test_day2_behavior():
      ...
day2_stressors: [interface_generalization, backwards_compatibility]
human_reference: |
  Human-written reference implementation used as the gold-standard baseline.
mock_solution: |
  Optional offline fixture used only by --provider mock.
mock_day2_solution: |
  Optional offline maintenance fixture used only by specoracle stress
  --provider mock.
```

`human_reference`, `day2_prompt`, `day2_test_code`, and `day2_stressors` are
required. This keeps the benchmark explicit and curated: correctness has a
gold-standard reference, and maintainability is measured by intentional feature
requests, not generic source mutations. Generated code is always tested as
`solution.py`, so tests should import from `solution`.

## Core Files

- `src/specoracle/config.py`: model settings, prompt templates, and the Zen
  oracle spec.
- `src/specoracle/generator.py`: `LLMClient`, OpenAI/Anthropic/mock adapters,
  and baseline versus oracle routing.
- `src/specoracle/evaluator.py`: radon metrics, AST nesting depth, subprocess
  Dockerized pytest checks, and LLM-as-a-Judge.
- `src/specoracle/cli.py`: argparse entry point for `generate`, `evaluate`,
  `run`, and `stress`.
- `src/specoracle/stress.py`: SpecArena Day 2 maintenance-agent stress tests.

## Measurement Notes

Cyclomatic complexity and maintainability index come from `radon`. Nesting depth
uses Python `ast` and counts standard control-flow nodes such as `if`, loops,
`try`, `with`, and `match`. Python represents `elif` as an `else` containing
another `if`, so SpecOracle treats an `elif` chain as one decision depth instead
of artificial nesting.

Generated code executes in a temporary directory through:

```bash
docker run --rm --network none ... specoracle-pytest:py311-alpine \
  python -m pytest -q -p no:cacheprovider test_solution.py
```

Evaluation never builds Docker images implicitly. `specoracle sandbox prepare`
builds a small local `specoracle-pytest:py311-alpine` image from
`python:3.11-alpine` with pinned `pytest` installed. The generated code itself
runs with `--network none`, `--memory 256m`, `--cpus 1.0`, `--pids-limit 128`,
`--cap-drop ALL`, `--security-opt no-new-privileges`, and a read-only source
mount. To inspect warm-run overhead:

```bash
specoracle sandbox benchmark --iterations 5
```
