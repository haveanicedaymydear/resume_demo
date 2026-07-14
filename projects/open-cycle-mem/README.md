# OpenCycle-Mem

> **Canonical standalone repository:** [haveanicedaymydear/OpenCycle-Mem](https://github.com/haveanicedaymydear/OpenCycle-Mem)  
> This directory is retained as a historical portfolio snapshot. Future development and review should use the standalone repository.

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

## Public v0.3 snapshot

This directory contains:

- a runnable standalone implementation of the convergence mechanism;
- raw-memory and static-governance baselines;
- five controlled evidence-stream scenarios;
- 1,000-episode aggregate results;
- automated tests for promotion, contradiction reopening, and contamination rejection.

## Quick start

```bash
cd projects/open-cycle-mem
python opencycle_mem_v03.py
python -m unittest discover -s tests -v
```

## Controlled simulation result

Across 1,000 episodes per method covering clean support, delayed contradiction, low-trust contamination, noisy evidence, and regime shift, OpenCycle-Mem v0.3 achieved 0.9496 mean state accuracy, compared with 0.8000 for static governed memory and 0.5000 for raw memory. Its false-active rate was 0.0501, and obsolete checkpoints reopened in 0.5075 cycles on average.

These are controlled algorithmic results, not real-LLM performance claims.
