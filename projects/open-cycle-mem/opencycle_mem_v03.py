"""OpenCycle-Mem v0.3 standalone controlled-simulation prototype."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Iterable
import csv
import json
import random
import statistics

class EvidenceStance(str, Enum):
    SUPPORT = "support"
    CONTRADICT = "contradict"
    NEUTRAL = "neutral"

@dataclass(slots=True)
class Evidence:
    content: str
    source: str
    stance: EvidenceStance
    confidence: float = 0.5
    metadata: dict = field(default_factory=dict)

class CheckpointState(str, Enum):
    OPEN = "open"
    ACTIVE = "active"
    REOPENED = "reopened"
    REVOKED = "revoked"

@dataclass(slots=True)
class ConvergenceConfig:
    promote_threshold: float = 0.55
    reopen_threshold: float = 0.12
    revoke_threshold: float = -0.30
    min_stable_cycles: int = 2
    min_independent_sources: int = 2
    min_source_trust: float = 0.50
    provenance_penalty: float = 0.10
    temporal_decay: float = 0.96
    duplicate_source_discount: float = 0.35

@dataclass(slots=True)
class ConvergenceSnapshot:
    cycle_index: int
    score: float
    support_mass: float
    contradiction_mass: float
    trusted_sources: int
    state: CheckpointState
    stable_cycles: int
    transition: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["state"] = self.state.value
        return data

@dataclass(slots=True)
class HysteresisConsolidator:
    config: ConvergenceConfig = field(default_factory=ConvergenceConfig)
    state: CheckpointState = CheckpointState.OPEN
    stable_cycles: int = 0
    history: list[ConvergenceSnapshot] = field(default_factory=list)

    def _weight(self, item: Evidence, age: int) -> float:
        trust = float(item.metadata.get("source_trust", 1.0))
        provenance = bool(item.metadata.get("provenance_verified", True))
        if not provenance:
            trust *= self.config.provenance_penalty
        return item.confidence * trust * (self.config.temporal_decay ** max(0, age))

    def score(self, evidence: Iterable[Evidence], cycle_index: int) -> tuple[float, float, float, int]:
        by_source: dict[str, list[tuple[Evidence, float]]] = {}
        for item in evidence:
            available = int(item.metadata.get("available_from_cycle", 0))
            age = max(0, cycle_index - available)
            by_source.setdefault(item.source, []).append((item, self._weight(item, age)))
        support_mass = 0.0
        contradiction_mass = 0.0
        trusted_sources: set[str] = set()
        for source, items in by_source.items():
            items = sorted(items, key=lambda pair: pair[1], reverse=True)
            for idx, (item, weight) in enumerate(items):
                if idx > 0:
                    weight *= self.config.duplicate_source_discount
                trust = float(item.metadata.get("source_trust", 1.0))
                provenance = bool(item.metadata.get("provenance_verified", True))
                if trust >= self.config.min_source_trust and provenance:
                    trusted_sources.add(source)
                if item.stance == EvidenceStance.SUPPORT:
                    support_mass += weight
                elif item.stance == EvidenceStance.CONTRADICT:
                    contradiction_mass += weight
        total = support_mass + contradiction_mass
        score = 0.0 if total <= 1e-12 else (support_mass - contradiction_mass) / total
        return score, support_mass, contradiction_mass, len(trusted_sources)

    def update(self, evidence: Iterable[Evidence], cycle_index: int) -> ConvergenceSnapshot:
        score, support_mass, contradiction_mass, trusted_sources = self.score(evidence, cycle_index)
        previous = self.state
        eligible = score >= self.config.promote_threshold and trusted_sources >= self.config.min_independent_sources
        self.stable_cycles = self.stable_cycles + 1 if eligible else 0
        if self.state in {CheckpointState.OPEN, CheckpointState.REOPENED}:
            if self.stable_cycles >= self.config.min_stable_cycles:
                self.state = CheckpointState.ACTIVE
        elif self.state == CheckpointState.ACTIVE:
            if score <= self.config.revoke_threshold:
                self.state = CheckpointState.REVOKED
                self.stable_cycles = 0
            elif score < self.config.reopen_threshold:
                self.state = CheckpointState.REOPENED
                self.stable_cycles = 0
        snapshot = ConvergenceSnapshot(
            cycle_index=cycle_index,
            score=round(score, 6),
            support_mass=round(support_mass, 6),
            contradiction_mass=round(contradiction_mass, 6),
            trusted_sources=trusted_sources,
            state=self.state,
            stable_cycles=self.stable_cycles,
            transition=None if self.state == previous else f"{previous.value}->{self.state.value}",
        )
        self.history.append(snapshot)
        return snapshot

def make_evidence(rng, stance, cycle, source, trust, provenance, confidence_mean):
    confidence = min(0.999, max(0.01, rng.gauss(confidence_mean, 0.06)))
    return Evidence(
        content=f"{source} reports {stance.value} evidence at cycle {cycle}",
        source=source,
        stance=stance,
        confidence=confidence,
        metadata={"available_from_cycle": cycle, "source_trust": trust, "provenance_verified": provenance},
    )

def stream_for(scenario: str, seed: int, cycles: int = 8):
    rng = random.Random(seed)
    stream, expected = [], []
    for cycle in range(cycles):
        batch = []
        if scenario == "clean_support":
            expected.append(cycle >= 1)
            batch.extend([
                make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"trusted-a-{cycle}", 0.92, True, 0.86),
                make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"trusted-b-{cycle}", 0.88, True, 0.82),
            ])
            if rng.random() < 0.25:
                batch.append(make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"noise-{cycle}", 0.35, True, 0.55))
        elif scenario == "delayed_contradiction":
            expected.append(1 <= cycle < 4)
            if cycle < 3:
                batch.extend([
                    make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"early-a-{cycle}", 0.90, True, 0.84),
                    make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"early-b-{cycle}", 0.86, True, 0.80),
                ])
            else:
                batch.extend([
                    make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"late-a-{cycle}", 0.97, True, 0.93),
                    make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"late-b-{cycle}", 0.94, True, 0.88),
                ])
        elif scenario == "contamination":
            expected.append(False)
            batch.extend([
                make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"untrusted-a-{cycle}", 0.08, False, 0.98),
                make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"untrusted-b-{cycle}", 0.12, False, 0.97),
            ])
            if cycle >= 3:
                batch.append(make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"audit-{cycle}", 0.95, True, 0.82))
        elif scenario == "noisy_true":
            expected.append(cycle >= 2)
            batch.append(make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"signal-{cycle}", 0.88, True, 0.78))
            if cycle % 2 == 0:
                batch.append(make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"replication-{cycle}", 0.80, True, 0.72))
            if rng.random() < 0.55:
                batch.append(make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"noise-{cycle}", 0.42, True, 0.58))
        elif scenario == "regime_shift":
            expected.append(1 <= cycle < 5)
            if cycle < 4:
                batch.extend([
                    make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"old-a-{cycle}", 0.91, True, 0.84),
                    make_evidence(rng, EvidenceStance.SUPPORT, cycle, f"old-b-{cycle}", 0.87, True, 0.79),
                ])
            else:
                batch.extend([
                    make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"shift-a-{cycle}", 0.96, True, 0.90),
                    make_evidence(rng, EvidenceStance.CONTRADICT, cycle, f"shift-b-{cycle}", 0.91, True, 0.86),
                ])
        else:
            raise ValueError(scenario)
        stream.append(batch)
    return stream, expected

class RawConsolidator:
    def __init__(self):
        self.active = False
        self.transitions = 0
    def update(self, cumulative, cycle):
        previous = self.active
        if any(e.stance == EvidenceStance.SUPPORT for e in cumulative):
            self.active = True
        if previous != self.active:
            self.transitions += 1
        return self.active

class StaticGovernedConsolidator:
    def __init__(self):
        self.active = False
        self.stable = 0
        self.transitions = 0
    def update(self, cumulative, cycle):
        previous = self.active
        trusted_support = {e.source for e in cumulative if e.stance == EvidenceStance.SUPPORT and float(e.metadata.get("source_trust", 1)) >= 0.5 and e.metadata.get("provenance_verified", True)}
        support = sum(e.confidence * float(e.metadata.get("source_trust", 1)) for e in cumulative if e.stance == EvidenceStance.SUPPORT)
        contra = sum(e.confidence * float(e.metadata.get("source_trust", 1)) for e in cumulative if e.stance == EvidenceStance.CONTRADICT)
        score = 0 if support + contra == 0 else (support - contra) / (support + contra)
        self.stable = self.stable + 1 if score >= 0.55 and len(trusted_support) >= 2 else 0
        if self.stable >= 2:
            self.active = True
        if previous != self.active:
            self.transitions += 1
        return self.active

def evaluate_method(method_name, stream, expected):
    cumulative, states = [], []
    transitions = 0
    convergence_cycle = None
    reopen_latency = None
    method = RawConsolidator() if method_name == "raw_memory" else StaticGovernedConsolidator() if method_name == "static_governed" else HysteresisConsolidator(ConvergenceConfig())
    first_expected_drop = next((i for i in range(1, len(expected)) if expected[i - 1] and not expected[i]), None)
    for cycle, batch in enumerate(stream):
        cumulative.extend(batch)
        if method_name == "opencycle_v0.3":
            snapshot = method.update(cumulative, cycle)
            active = snapshot.state == CheckpointState.ACTIVE
            transitions += int(snapshot.transition is not None)
        else:
            active = method.update(cumulative, cycle)
            transitions = method.transitions
        states.append(active)
        if active and convergence_cycle is None:
            convergence_cycle = cycle
        if first_expected_drop is not None and cycle >= first_expected_drop and not active and reopen_latency is None:
            reopen_latency = cycle - first_expected_drop
    return {
        "method": method_name,
        "state_accuracy": sum(int(a == e) for a, e in zip(states, expected)) / len(expected),
        "false_active_rate": sum(int(a and not e) for a, e in zip(states, expected)) / len(expected),
        "missed_active_rate": sum(int((not a) and e) for a, e in zip(states, expected)) / len(expected),
        "convergence_cycle": -1 if convergence_cycle is None else convergence_cycle,
        "reopen_latency": -1 if reopen_latency is None else reopen_latency,
        "memory_churn": transitions,
    }

def run_simulation(output_dir="results/v0.3_simulation", seeds=200, cycles=8):
    scenarios = ["clean_support", "delayed_contradiction", "contamination", "noisy_true", "regime_shift"]
    methods = ["raw_memory", "static_governed", "opencycle_v0.3"]
    rows = []
    for scenario in scenarios:
        for seed in range(seeds):
            stream, expected = stream_for(scenario, seed, cycles)
            for method in methods:
                row = evaluate_method(method, stream, expected)
                row.update({"scenario": scenario, "seed": seed})
                rows.append(row)
    summary = []
    for method in methods:
        group = [r for r in rows if r["method"] == method]
        valid_convergence = [r["convergence_cycle"] for r in group if r["convergence_cycle"] >= 0]
        valid_reopen = [r["reopen_latency"] for r in group if r["reopen_latency"] >= 0]
        summary.append({
            "method": method,
            "episodes": len(group),
            "mean_state_accuracy": round(statistics.mean(r["state_accuracy"] for r in group), 4),
            "false_active_rate": round(statistics.mean(r["false_active_rate"] for r in group), 4),
            "missed_active_rate": round(statistics.mean(r["missed_active_rate"] for r in group), 4),
            "mean_convergence_cycle": round(statistics.mean(valid_convergence), 4) if valid_convergence else -1,
            "mean_reopen_latency": round(statistics.mean(valid_reopen), 4) if valid_reopen else -1,
            "mean_memory_churn": round(statistics.mean(r["memory_churn"] for r in group), 4),
        })
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return rows, summary

if __name__ == "__main__":
    _, summary = run_simulation()
    print(json.dumps(summary, indent=2))
