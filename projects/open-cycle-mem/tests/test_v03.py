import unittest

from opencycle_mem_v03 import (
    CheckpointState,
    Evidence,
    EvidenceStance,
    HysteresisConsolidator,
)


class OpenCycleV03Tests(unittest.TestCase):
    @staticmethod
    def evidence(stance, source, trust=0.9, confidence=0.9, provenance=True, cycle=0):
        return Evidence(
            content="test evidence",
            source=source,
            stance=stance,
            confidence=confidence,
            metadata={
                "source_trust": trust,
                "provenance_verified": provenance,
                "available_from_cycle": cycle,
            },
        )

    def test_promotes_after_repeated_trusted_support(self):
        agent = HysteresisConsolidator()
        evidence = [
            self.evidence(EvidenceStance.SUPPORT, "a"),
            self.evidence(EvidenceStance.SUPPORT, "b"),
        ]
        self.assertEqual(agent.update(evidence, 0).state, CheckpointState.OPEN)
        self.assertEqual(agent.update(evidence, 1).state, CheckpointState.ACTIVE)

    def test_reopens_after_strong_contradiction(self):
        agent = HysteresisConsolidator()
        evidence = [
            self.evidence(EvidenceStance.SUPPORT, "a"),
            self.evidence(EvidenceStance.SUPPORT, "b"),
        ]
        agent.update(evidence, 0)
        agent.update(evidence, 1)
        evidence.extend([
            self.evidence(EvidenceStance.CONTRADICT, "c", confidence=0.99, cycle=2),
            self.evidence(EvidenceStance.CONTRADICT, "d", confidence=0.99, cycle=2),
        ])
        self.assertIn(
            agent.update(evidence, 2).state,
            {CheckpointState.REOPENED, CheckpointState.REVOKED},
        )

    def test_rejects_untrusted_unverified_contamination(self):
        agent = HysteresisConsolidator()
        evidence = [
            self.evidence(EvidenceStance.SUPPORT, "a", trust=0.1, provenance=False),
            self.evidence(EvidenceStance.SUPPORT, "b", trust=0.1, provenance=False),
        ]
        agent.update(evidence, 0)
        self.assertNotEqual(agent.update(evidence, 1).state, CheckpointState.ACTIVE)


if __name__ == "__main__":
    unittest.main()
