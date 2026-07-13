# OpenCycle-Mem v0.3 Research Note

## New mechanism: evidence-convergent checkpoints

v0.3 replaces one-way memory promotion with a reversible checkpoint lifecycle:

`open -> active -> reopened -> active` or `open/active -> revoked`.

A checkpoint is activated only after repeated cycles of sufficiently positive evidence from independent, trusted, provenance-verified sources. It is not treated as permanently correct: later contradictory evidence can reopen or revoke it.

## Convergence rule

For evidence item `i`, the effective mass is:

`confidence_i * source_trust_i * provenance_factor_i * temporal_decay_i`.

The normalized convergence score is:

`(support_mass - contradiction_mass) / (support_mass + contradiction_mass)`.

Activation uses a high threshold and repeated stability; reopening uses a lower threshold. This hysteresis band is intended to prevent noisy evidence from repeatedly toggling memory state while still allowing genuine revisions.

## Controlled-simulation scope

The bundled simulation is an algorithmic stress test, not a real-LLM performance claim. It evaluates five evidence-stream families across repeated random seeds:

- clean support;
- delayed contradiction;
- low-trust memory contamination;
- noisy but true evidence;
- environmental regime shift.

Baselines are raw memory and static governed memory without reversible reopening.

## Intended use in future agents

The mechanism can sit between any agent's episodic memory and reusable skill/semantic memory. It is especially suitable for:

- AutoResearch hypotheses;
- long-horizon tool-use conclusions;
- learned user/environment models;
- multi-agent trust beliefs;
- reusable reasoning or planning checkpoints.

It should not govern hard safety constraints or raw observations by itself. Those require separate policy and provenance layers.
