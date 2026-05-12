# Oracle x Model Factorial Comparison - Full SlopBench (50 tasks x 3 samples)

Two oracle sources x three frontier models. Each cell shows mean CC delta (%) relative to that model's baseline.

| Oracle Source | Claude 4.6 | GPT-5.5 | Gemini 2.5 Pro | Mean |
|---|---:|---:|---:|---:|
| Zen of Python | -16.6% | -25.1% | -23.1% | -21.6% |
| Karpathy Guidelines | -3.2% | 1.3% | -2.4% | -1.4% |
| **Model Mean** | **-9.9%** | **-11.9%** | **-12.7%** | **-11.5%** |

## Detailed Metrics

| Oracle | Model | N | CC (Base) | CC (Oracle) | Delta CC | Delta % | P@1 (B) | P@1 (O) | Judge |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Zen | Claude 4.6 | 50 | 5.753 | 4.800 | -0.953 | -16.6% | 88.7% | 89.3% | 8.796 |
| Zen | GPT-5.5 | 50 | 5.643 | 4.224 | -1.419 | -25.1% | 92.7% | 94.0% | 7.927 |
| Zen | Gemini 2.5 Pro | 50 | 5.146 | 3.959 | -1.187 | -23.1% | 80.7% | 78.7% | 7.017 |
| Karpathy | Claude 4.6 | 50 | 5.758 | 5.576 | -0.182 | -3.2% | 88.7% | 90.7% | 8.980 |
| Karpathy | GPT-5.5 | 50 | 5.643 | 5.714 | 0.071 | 1.3% | 92.7% | 92.7% | 8.483 |
| Karpathy | Gemini 2.5 Pro | 50 | 5.146 | 5.023 | -0.123 | -2.4% | 80.7% | 79.3% | 6.340 |

Zen oracle: PEP 20 (https://peps.python.org/pep-0020/)
Karpathy oracle: https://github.com/forrestchang/andrej-karpathy-skills
Pipeline: https://github.com/davidkimai/specoracle
