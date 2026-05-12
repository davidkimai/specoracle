# SlopBench Inspect Export Stub

This directory contains a pre-submission export stub for adapting SpecOracle/SlopBench
results to the Inspect ecosystem.

This is not a submitted or merged Inspect Evals PR. Full Inspect Evals integration is
planned for the fellowship period.

## References

- Inspect: https://inspect.aisi.org.uk/
- Inspect Evals announcement: https://www.aisi.gov.uk/work/inspect-evals
- Inspect Evals repository: https://github.com/UKGovernmentBEIS/inspect_evals

## Export Existing Results

```bash
python3 integrations/inspect/export.py \
  runs/slopbench_full_claude \
  --out integrations/inspect/inspect_results.json
```

The exporter reads a SpecOracle `summary.csv` and writes a compact JSON payload with
dataset metadata, model identifiers, and variant-level metrics.
