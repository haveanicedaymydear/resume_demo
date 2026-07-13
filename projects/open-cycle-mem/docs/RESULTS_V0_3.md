# v0.3 Controlled Simulation Results

This report is generated from a controlled evidence-stream simulation. It evaluates the checkpoint-governance algorithm under explicit assumptions; it does not establish gains on real language models.

The key expected behavior is selective convergence:

- converge after repeated independent support;
- remain stable under weak noise;
- reject high-confidence low-trust contamination;
- reopen or revoke after strong delayed contradiction;
- avoid irreversible commitment to obsolete beliefs.

Run:

```bash
python opencycle_mem_v03.py
```

See `results/v0.3_simulation/summary.csv` for the generated aggregate table.
