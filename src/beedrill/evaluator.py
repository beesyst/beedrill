from __future__ import annotations

from dataclasses import dataclass

from beedrill.domain import (
    _ASSET,
    _MAX_AMOUNT,
    ContainmentStatus,
    DrillVerdict,
    EvidenceCompleteness,
    ObservationStatus,
    VerdictStatus,
    _identifier,
    _integer,
)


@dataclass(frozen=True, slots=True)
class EconomicLoss:
    asset: str
    unit: str
    economic_basis: str
    amount: int

    def __post_init__(self) -> None:
        if not isinstance(self.asset, str) or not _ASSET.fullmatch(self.asset):
            raise ValueError("asset must be an uppercase asset symbol")
        _identifier(self.unit, "unit")
        _identifier(self.economic_basis, "economic_basis")
        _integer(self.amount, "amount", minimum=0, maximum=_MAX_AMOUNT)


@dataclass(frozen=True, slots=True)
class DrillEvidence:
    evidence: EvidenceCompleteness
    detection_status: ObservationStatus
    containment_status: ContainmentStatus
    attack_start_slot: int | None
    first_detection_slot: int | None
    first_containment_slot: int | None
    gross_attack_loss: EconomicLoss | None
    residual_loss: EconomicLoss | None

    def __post_init__(self) -> None:
        if not isinstance(self.evidence, EvidenceCompleteness):
            raise ValueError("evidence must be EvidenceCompleteness")
        if not isinstance(self.detection_status, ObservationStatus):
            raise ValueError("detection_status must be ObservationStatus")
        if not isinstance(self.containment_status, ContainmentStatus):
            raise ValueError("containment_status must be ContainmentStatus")
        _optional_slot(self.attack_start_slot, "attack_start_slot")
        _optional_slot(self.first_detection_slot, "first_detection_slot")
        _optional_slot(self.first_containment_slot, "first_containment_slot")
        _optional_loss(self.gross_attack_loss, "gross_attack_loss")
        _optional_loss(self.residual_loss, "residual_loss")
        if self.detection_status is not ObservationStatus.OBSERVED:
            if self.first_detection_slot is not None:
                raise ValueError("unobserved detection cannot have a detection slot")
        elif (
            self.attack_start_slot is not None
            and self.first_detection_slot is not None
            and self.first_detection_slot < self.attack_start_slot
        ):
            raise ValueError("detection cannot precede attack start")
        if self.containment_status is not ContainmentStatus.SUCCEEDED:
            if self.first_containment_slot is not None:
                raise ValueError(
                    "unsuccessful containment cannot have a containment slot"
                )
        elif self.detection_status is not ObservationStatus.OBSERVED:
            raise ValueError("successful containment requires observed detection")
        elif (
            self.first_detection_slot is not None
            and self.first_containment_slot is not None
            and self.first_containment_slot < self.first_detection_slot
        ):
            raise ValueError("containment cannot precede detection")
        if self.gross_attack_loss is not None and self.residual_loss is not None:
            if (
                self.gross_attack_loss.asset != self.residual_loss.asset
                or self.gross_attack_loss.unit != self.residual_loss.unit
                or self.gross_attack_loss.economic_basis
                != self.residual_loss.economic_basis
            ):
                raise ValueError(
                    "economic losses must use the same asset, unit, and basis"
                )
            if self.gross_attack_loss.amount == 0 and self.residual_loss.amount != 0:
                raise ValueError("zero gross attack loss requires zero residual loss")
            if self.residual_loss.amount > self.gross_attack_loss.amount:
                raise ValueError("residual loss cannot exceed gross attack loss")


@dataclass(frozen=True, slots=True)
class DrillMetrics:
    detection_result: ObservationStatus
    containment_result: ContainmentStatus
    mttd_slots: int | None
    mttc_slots: int | None
    gross_attack_loss: EconomicLoss | None
    residual_loss: EconomicLoss | None
    capital_saved: EconomicLoss | None


@dataclass(frozen=True, slots=True)
class DrillEvaluation:
    metrics: DrillMetrics
    verdict: DrillVerdict


def evaluate_drill(evidence: DrillEvidence) -> DrillEvaluation:
    if not isinstance(evidence, DrillEvidence):
        raise TypeError("evidence must be DrillEvidence")
    metrics = _metrics(evidence)
    gross_attack_loss = evidence.gross_attack_loss
    residual_loss = evidence.residual_loss
    if _is_incomplete(evidence) or gross_attack_loss is None or residual_loss is None:
        return DrillEvaluation(metrics, DrillVerdict(VerdictStatus.INCOMPLETE))
    if evidence.detection_status is ObservationStatus.NOT_OBSERVED:
        return DrillEvaluation(metrics, DrillVerdict(VerdictStatus.FAIL))
    if evidence.containment_status is ContainmentStatus.FAILED:
        return DrillEvaluation(metrics, DrillVerdict(VerdictStatus.FAIL))
    if gross_attack_loss.amount == 0 or residual_loss.amount < gross_attack_loss.amount:
        return DrillEvaluation(metrics, DrillVerdict(VerdictStatus.PASS))
    return DrillEvaluation(metrics, DrillVerdict(VerdictStatus.FAIL))


def _metrics(evidence: DrillEvidence) -> DrillMetrics:
    mttd_slots = None
    if (
        evidence.detection_status is ObservationStatus.OBSERVED
        and evidence.attack_start_slot is not None
        and evidence.first_detection_slot is not None
    ):
        mttd_slots = evidence.first_detection_slot - evidence.attack_start_slot
    mttc_slots = None
    if (
        evidence.containment_status is ContainmentStatus.SUCCEEDED
        and evidence.first_detection_slot is not None
        and evidence.first_containment_slot is not None
    ):
        mttc_slots = evidence.first_containment_slot - evidence.first_detection_slot
    capital_saved = None
    if evidence.gross_attack_loss is not None and evidence.residual_loss is not None:
        capital_saved = EconomicLoss(
            asset=evidence.gross_attack_loss.asset,
            unit=evidence.gross_attack_loss.unit,
            economic_basis=evidence.gross_attack_loss.economic_basis,
            amount=evidence.gross_attack_loss.amount - evidence.residual_loss.amount,
        )
    return DrillMetrics(
        detection_result=evidence.detection_status,
        containment_result=evidence.containment_status,
        mttd_slots=mttd_slots,
        mttc_slots=mttc_slots,
        gross_attack_loss=evidence.gross_attack_loss,
        residual_loss=evidence.residual_loss,
        capital_saved=capital_saved,
    )


def _is_incomplete(evidence: DrillEvidence) -> bool:
    return (
        bool(evidence.evidence.missing)
        or evidence.attack_start_slot is None
        or evidence.gross_attack_loss is None
        or evidence.residual_loss is None
        or evidence.detection_status is ObservationStatus.MISSING
        or evidence.containment_status is ContainmentStatus.MISSING
        or (
            evidence.detection_status is ObservationStatus.OBSERVED
            and evidence.first_detection_slot is None
        )
        or (
            evidence.containment_status is ContainmentStatus.SUCCEEDED
            and evidence.first_containment_slot is None
        )
    )


def _optional_slot(value: int | None, name: str) -> None:
    if value is not None:
        _integer(value, name, minimum=0, maximum=_MAX_AMOUNT)


def _optional_loss(value: EconomicLoss | None, name: str) -> None:
    if value is not None and not isinstance(value, EconomicLoss):
        raise ValueError(f"{name} must be EconomicLoss")
