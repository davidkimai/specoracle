# Oracle Source Independence - Claude 4.6, Full SlopBench (50 tasks x 3 samples)

Comparative evaluation of two independent oracle sources on Claude 4.6 (T=0.8).
Zen of Python data from Sprint 1; Karpathy Guidelines from Sprint 3.

| Oracle Source | N | CC (Base) | CC (Oracle) | Delta CC | Delta CC % | P@1 (Base) | P@1 (Oracle) | Judge |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Zen of Python | 50 | 5.753 | 4.800 | -0.953 | -16.6% | 88.7% | 89.3% | 8.796 |
| Karpathy Guidelines | 50 | 5.758 | 5.576 | -0.182 | -3.2% | 88.7% | 90.7% | 8.980 |

Zen oracle: PEP 20 (https://peps.python.org/pep-0020/)
Karpathy oracle: https://github.com/forrestchang/andrej-karpathy-skills
Pipeline: https://github.com/davidkimai/specoracle
