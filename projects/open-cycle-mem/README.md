# OpenCycle-Mem

**Reversible Evidence Convergence and Governed Memory for Long-Horizon Agents**

OpenCycle-Mem studies how an autonomous agent can consolidate repeatedly supported conclusions into reusable checkpoints without turning memory into an irreversible store of model-generated claims.

## v0.3: evidence-convergent checkpoints

The core contribution in v0.3 is a reversible checkpoint lifecycle:

```text
open -> active -> reopened -> active
                  \-> revoked
```

A checkpoint becomes active only after stable, independent, provenance-verified support. Later contradictory evidence can reopen or revoke it. A hysteresis band separates activation and reopening thresholds, reducing memory churn under noisy evidence.

The effective evidence mass combines confidence, source trust, provenance validity, source independence, and temporal decay. The system stores concise decision summaries and evidence references; it does not require hidden chain-of-thought storage.

## Main capabilities

- evidence-weighted convergence score;
- repeated-cycle stability requirement;
- independent-source and provenance gates;
- reversible reopening and revocation;
- temporal decay and duplicate-source discounting;
- stateless, raw, summary, static-governed, and reversible-governed comparisons;
- OpenAI-compatible structured-output backend;
- controlled convergence simulation and 30-task pilot suite.

## Quick start

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m opencycle_mem.cli simulate --seeds 200
python -m opencycle_mem.cli pilot --backend heuristic
```

## Real-model pilot

```bash
export OPENCYCLE_API_KEY="..."
export OPENCYCLE_MODEL="..."
export OPENCYCLE_BASE_URL="https://api.openai.com/v1"
python -m opencycle_mem.cli pilot --backend openai
```

The bundled heuristic and controlled-simulation results validate the implementation and algorithmic behavior only. Real-agent effectiveness requires declared model runs, multiple seeds, stronger tasks, and manual error analysis.

## Controlled simulation result

Across 1,000 episodes covering clean support, delayed contradiction, low-trust contamination, noisy evidence, and regime shift, OpenCycle-Mem v0.3 achieved 0.9496 mean state accuracy, compared with 0.8000 for static governed memory and 0.5000 for raw memory. Its false-active rate was 0.0501, and obsolete checkpoints reopened in 0.5075 cycles on average. These are controlled algorithmic results, not real-LLM performance claims.

## Research question

> Can reversible, provenance-aware reasoning checkpoints reduce redundant long-horizon deliberation while preventing unsupported, contaminated, or obsolete beliefs from becoming persistent agent memory?

## Current status

Independent open-source research in progress, July 2026.
