# SpecOracle v2 Audit Report

## Existing Provider Support
- `src/specoracle/generator.py` already implements `OpenAIClient`, `AnthropicClient`, and `MockLLMClient`.
- OpenAI uses the Responses API, preserves the shared prompt templates, and falls back when a model rejects `temperature` unless `--require-temperature` is set.
- `src/specoracle/config.py` currently declares providers as `openai`, `anthropic`, and `mock`; no Google/Gemini provider exists yet.

## Existing Metrics and Evaluation
- `src/specoracle/evaluator.py` computes syntax status, LOC, function/class counts, Radon cyclomatic complexity, maintainability index, max nesting depth, Dockerized pytest, and optional LLM judge scores.
- Docker pytest runs network-disabled, read-only, and resource-constrained.

## Existing Stress Flow
- `src/specoracle/stress.py` implements one-step Day 2 SpecArena maintenance.
- Existing stress artifacts are `stress.json` plus `day2_solution.py`.
- Stress idempotency already checks complete artifacts, key/model mismatches, and context-ablation completeness.
- No chained maintenance or chain-depth support exists.

## CLI Surface
- `specoracle run` supports `--modes baseline oracle neutral_style`.
- `specoracle stress` has no `--chain-depth`.
- `specoracle validate --dataset` already exists and validates dataset-only state.

## Tests
- Current tests cover generator prompts/provider behavior, CLI run/stress/validate, dataset coverage, evaluator/sandbox behavior, analyze script behavior, and idempotency.
- No current tests cover Google provider, hybrid oracle retries, chain-depth stress, cross-provider comparison, or Inspect export.

## Run Directories
- Locked evidence directories present: `runs/claude_replicated/` and `runs/slopbench_full_claude/`.
- Additional run directories include probe, sample, neutral ablation, smoke, and phase mock artifacts.
- Locked evidence should remain unchanged.
