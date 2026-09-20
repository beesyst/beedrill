import json
from dataclasses import replace
from pathlib import Path

import pytest

from beedrill.domain import (
    ContainmentStatus,
    EvidenceCompleteness,
    ObservationStatus,
    VerdictStatus,
)
from beedrill.evaluator import DrillEvidence, EconomicLoss, evaluate_drill

FIXTURES = Path(__file__).parent / "fixtures"


def _evidence_from_fixture(name: str) -> tuple[DrillEvidence, str]:
    data = json.loads((FIXTURES / name).read_text())
    gross = data["gross_attack_loss"]
    residual = data["residual_loss"]
    return (
        DrillEvidence(
            evidence=EvidenceCompleteness(
                ("attack", "detection", "containment", "economics"),
                ("attack", "detection", "containment", "economics"),
                (),
            ),
            detection_status=ObservationStatus(data["detection_status"]),
            containment_status=ContainmentStatus(data["containment_status"]),
            attack_start_slot=data["attack_start_slot"],
            first_detection_slot=data["first_detection_slot"],
            first_containment_slot=data["first_containment_slot"],
            gross_attack_loss=EconomicLoss(**gross),
            residual_loss=EconomicLoss(**residual),
        ),
        data["expected_verdict"],
    )


def _complete_evidence(**changes: object) -> DrillEvidence:
    evidence = DrillEvidence(
        evidence=EvidenceCompleteness(
            ("attack", "detection", "containment", "economics"),
            ("attack", "detection", "containment", "economics"),
            (),
        ),
        detection_status=ObservationStatus.OBSERVED,
        containment_status=ContainmentStatus.SUCCEEDED,
        attack_start_slot=100,
        first_detection_slot=102,
        first_containment_slot=105,
        gross_attack_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 100),
        residual_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 20),
    )
    return replace(evidence, **changes)


@pytest.mark.parametrize(
    "fixture", ["complete_pass_evidence.json", "complete_fail_evidence.json"]
)
def test_fixture_expected_verdict_is_only_an_oracle(fixture: str) -> None:
    evidence, expected_verdict = _evidence_from_fixture(fixture)

    result = evaluate_drill(evidence)

    assert result.verdict.status.value == expected_verdict


def test_pass_calculates_metrics_and_partial_containment() -> None:
    result = evaluate_drill(_complete_evidence())

    assert result.verdict.status is VerdictStatus.PASS
    assert result.metrics.mttd_slots == 2
    assert result.metrics.mttc_slots == 3
    assert result.metrics.capital_saved == EconomicLoss(
        "USDC", "micro_usdc", "vault_balance", 80
    )


def test_completed_not_observed_detection_fails_without_mttd() -> None:
    result = evaluate_drill(
        _complete_evidence(
            detection_status=ObservationStatus.NOT_OBSERVED,
            containment_status=ContainmentStatus.FAILED,
            first_detection_slot=None,
            first_containment_slot=None,
        )
    )

    assert result.verdict.status is VerdictStatus.FAIL
    assert result.metrics.mttd_slots is None
    assert result.metrics.mttc_slots is None


def test_failed_containment_fails() -> None:
    result = evaluate_drill(
        _complete_evidence(
            containment_status=ContainmentStatus.FAILED,
            first_containment_slot=None,
            residual_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 100),
        )
    )

    assert result.verdict.status is VerdictStatus.FAIL


def test_missing_critical_evidence_is_incomplete() -> None:
    result = evaluate_drill(
        _complete_evidence(
            evidence=EvidenceCompleteness(
                ("attack", "detection", "containment", "economics"),
                ("attack", "detection", "containment"),
                ("economics",),
            ),
            residual_loss=None,
        )
    )

    assert result.verdict.status is VerdictStatus.INCOMPLETE


def test_missing_detection_slot_is_incomplete_without_mttd() -> None:
    result = evaluate_drill(_complete_evidence(first_detection_slot=None))

    assert result.verdict.status is VerdictStatus.INCOMPLETE
    assert result.metrics.mttd_slots is None


@pytest.mark.parametrize(
    "changes",
    [
        {"first_detection_slot": 99},
        {"first_containment_slot": 101},
        {"detection_status": ObservationStatus.NOT_OBSERVED},
        {"residual_loss": EconomicLoss("SOL", "lamports", "vault_balance", 20)},
        {"residual_loss": EconomicLoss("USDC", "micro_usdc", "other_balance", 20)},
        {"residual_loss": EconomicLoss("USDC", "micro_usdc", "vault_balance", 101)},
    ],
)
def test_contradictory_evidence_is_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _complete_evidence(**changes)


def test_zero_timing_and_zero_loss_pass() -> None:
    result = evaluate_drill(
        _complete_evidence(
            first_detection_slot=100,
            first_containment_slot=100,
            gross_attack_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 0),
            residual_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 0),
        )
    )

    assert result.verdict.status is VerdictStatus.PASS
    assert result.metrics.mttd_slots == 0
    assert result.metrics.mttc_slots == 0
    assert result.metrics.capital_saved is not None
    assert result.metrics.capital_saved.amount == 0


def test_equal_residual_loss_fails_and_nonzero_zero_loss_is_rejected() -> None:
    result = evaluate_drill(
        _complete_evidence(
            residual_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 100)
        )
    )

    assert result.verdict.status is VerdictStatus.FAIL
    with pytest.raises(ValueError, match="zero gross"):
        _complete_evidence(
            gross_attack_loss=EconomicLoss("USDC", "micro_usdc", "vault_balance", 0)
        )


def test_equivalent_evidence_replays_identically() -> None:
    evidence = _complete_evidence()

    assert evaluate_drill(evidence) == evaluate_drill(evidence)
