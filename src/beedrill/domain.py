from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar, cast

_IDENTIFIER = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")
_ASSET = re.compile(r"[A-Z][A-Z0-9]{1,15}\Z")
_MAX_VERSION = 1_000_000
_MAX_AMOUNT = 10**18
_MAX_COLLECTION = 32

_EnumT = TypeVar("_EnumT", bound=Enum)


class ControlType(str, Enum):
    DETECTOR = "detector"
    CONTAINMENT = "containment"


class ControlExpectation(str, Enum):
    OBSERVED = "observed"
    SUCCEEDED = "succeeded"


class ObservationSubject(str, Enum):
    ATTACK = "attack"
    CONTROL = "control"


class ObservationStatus(str, Enum):
    OBSERVED = "observed"
    NOT_OBSERVED = "not_observed"
    MISSING = "missing"


class ContainmentStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    MISSING = "missing"


class VerdictStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class ScenarioIdentity:
    scenario_id: str
    version: int

    def __post_init__(self) -> None:
        _identifier(self.scenario_id, "scenario_id")
        _integer(self.version, "version", minimum=1, maximum=_MAX_VERSION)


@dataclass(frozen=True, slots=True)
class Target:
    target_id: str
    protocol: str
    state_ref: str

    def __post_init__(self) -> None:
        _identifier(self.target_id, "target_id")
        _identifier(self.protocol, "protocol")
        _identifier(self.state_ref, "state_ref")


@dataclass(frozen=True, slots=True)
class InitialState:
    state_id: str
    description: str

    def __post_init__(self) -> None:
        _identifier(self.state_id, "state_id")
        _text(self.description, "description")


@dataclass(frozen=True, slots=True)
class AttackStep:
    attack_id: str
    attack_type: str
    expected_effect: str

    def __post_init__(self) -> None:
        _identifier(self.attack_id, "attack_id")
        _identifier(self.attack_type, "attack_type")
        _text(self.expected_effect, "expected_effect")


@dataclass(frozen=True, slots=True)
class ExpectedControl:
    control_id: str
    control_type: ControlType
    expectation: ControlExpectation

    def __post_init__(self) -> None:
        _identifier(self.control_id, "control_id")
        _enum(self.control_type, ControlType, "control_type")
        _enum(self.expectation, ControlExpectation, "expectation")
        expected = (
            ControlExpectation.OBSERVED
            if self.control_type is ControlType.DETECTOR
            else ControlExpectation.SUCCEEDED
        )
        if self.expectation is not expected:
            raise ValueError("control_type and expectation are inconsistent")


@dataclass(frozen=True, slots=True)
class Observation:
    observation_id: str
    subject_id: str
    subject: ObservationSubject
    status: ObservationStatus
    evidence_id: str

    def __post_init__(self) -> None:
        _identifier(self.observation_id, "observation_id")
        _identifier(self.subject_id, "subject_id")
        _enum(self.subject, ObservationSubject, "subject")
        _enum(self.status, ObservationStatus, "status")
        _identifier(self.evidence_id, "evidence_id")


@dataclass(frozen=True, slots=True)
class ContainmentResult:
    control_id: str
    status: ContainmentStatus
    evidence_id: str

    def __post_init__(self) -> None:
        _identifier(self.control_id, "control_id")
        _enum(self.status, ContainmentStatus, "status")
        _identifier(self.evidence_id, "evidence_id")


@dataclass(frozen=True, slots=True)
class EconomicDelta:
    asset: str
    unit: str
    before: int
    after: int

    def __post_init__(self) -> None:
        if not isinstance(self.asset, str) or not _ASSET.fullmatch(self.asset):
            raise ValueError("asset must be an uppercase asset symbol")
        _identifier(self.unit, "unit")
        _integer(self.before, "before", minimum=-_MAX_AMOUNT, maximum=_MAX_AMOUNT)
        _integer(self.after, "after", minimum=-_MAX_AMOUNT, maximum=_MAX_AMOUNT)


@dataclass(frozen=True, slots=True)
class EvidenceCompleteness:
    required: tuple[str, ...]
    present: tuple[str, ...]
    missing: tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier_tuple(self.required, "required", nonempty=True)
        _identifier_tuple(self.present, "present")
        _identifier_tuple(self.missing, "missing")
        required = set(self.required)
        present = set(self.present)
        missing = set(self.missing)
        if present | missing != required or present & missing:
            raise ValueError(
                "present and missing evidence must partition required evidence"
            )


@dataclass(frozen=True, slots=True)
class DrillVerdict:
    status: VerdictStatus

    def __post_init__(self) -> None:
        _enum(self.status, VerdictStatus, "status")


@dataclass(frozen=True, slots=True)
class Scenario:
    identity: ScenarioIdentity
    target: Target
    initial_state: InitialState
    attack_steps: tuple[AttackStep, ...]
    expected_controls: tuple[ExpectedControl, ...]
    observations: tuple[Observation, ...]
    containment: ContainmentResult
    economic_delta: EconomicDelta
    evidence: EvidenceCompleteness
    verdict: DrillVerdict

    def __post_init__(self) -> None:
        _instance(self.identity, ScenarioIdentity, "identity")
        _instance(self.target, Target, "target")
        _instance(self.initial_state, InitialState, "initial_state")
        _typed_tuple(self.attack_steps, AttackStep, "attack_steps", nonempty=True)
        _typed_tuple(
            self.expected_controls, ExpectedControl, "expected_controls", nonempty=True
        )
        _typed_tuple(self.observations, Observation, "observations", nonempty=True)
        _instance(self.containment, ContainmentResult, "containment")
        _instance(self.economic_delta, EconomicDelta, "economic_delta")
        _instance(self.evidence, EvidenceCompleteness, "evidence")
        _instance(self.verdict, DrillVerdict, "verdict")
        if self.target.state_ref != self.initial_state.state_id:
            raise ValueError("target state_ref must match initial_state state_id")
        _unique((step.attack_id for step in self.attack_steps), "attack_steps")
        _unique(
            (control.control_id for control in self.expected_controls),
            "expected_controls",
        )
        _unique(
            (observation.observation_id for observation in self.observations),
            "observations",
        )
        attack_ids = {step.attack_id for step in self.attack_steps}
        controls = {control.control_id: control for control in self.expected_controls}
        if attack_ids & set(controls):
            raise ValueError("attack and control identifiers must be distinct")
        if not any(
            control.control_type is ControlType.DETECTOR
            for control in controls.values()
        ):
            raise ValueError("a scenario requires a detector expectation")
        if not any(
            control.control_type is ControlType.CONTAINMENT
            for control in controls.values()
        ):
            raise ValueError("a scenario requires a containment expectation")
        for observation in self.observations:
            subjects = (
                attack_ids
                if observation.subject is ObservationSubject.ATTACK
                else set(controls)
            )
            if observation.subject_id not in subjects:
                raise ValueError(
                    "observation subject_id is not defined by the scenario"
                )
        observed_attacks = {
            observation.subject_id
            for observation in self.observations
            if observation.subject is ObservationSubject.ATTACK
        }
        observed_detectors = {
            observation.subject_id
            for observation in self.observations
            if observation.subject is ObservationSubject.CONTROL
            and controls[observation.subject_id].control_type is ControlType.DETECTOR
        }
        detector_ids = {
            control.control_id
            for control in controls.values()
            if control.control_type is ControlType.DETECTOR
        }
        if observed_attacks != attack_ids:
            raise ValueError("each attack step requires an observation")
        if observed_detectors != detector_ids:
            raise ValueError("each detector requires an observation")
        containment_control = controls.get(self.containment.control_id)
        if (
            containment_control is None
            or containment_control.control_type is not ControlType.CONTAINMENT
        ):
            raise ValueError("containment result must reference a containment control")
        required = set(self.evidence.required)
        present = set(self.evidence.present)
        missing = set(self.evidence.missing)
        evidence_statuses = [
            (observation.status, observation.evidence_id)
            for observation in self.observations
        ]
        containment_observation = (
            ObservationStatus.MISSING
            if self.containment.status is ContainmentStatus.MISSING
            else ObservationStatus.OBSERVED
        )
        evidence_statuses.append(
            (containment_observation, self.containment.evidence_id)
        )
        for status, evidence_id in evidence_statuses:
            if evidence_id not in required:
                raise ValueError("observation evidence must be required")
            if status is ObservationStatus.MISSING and evidence_id not in missing:
                raise ValueError(
                    "missing observation evidence must be listed as missing"
                )
            if status is not ObservationStatus.MISSING and evidence_id not in present:
                raise ValueError(
                    "available observation evidence must be listed as present"
                )
        if self.evidence.missing and self.verdict.status is VerdictStatus.PASS:
            raise ValueError("missing evidence cannot have a pass verdict")


def scenario_to_dict(scenario: Scenario) -> dict[str, Any]:
    _instance(scenario, Scenario, "scenario")
    return {
        "identity": {
            "scenario_id": scenario.identity.scenario_id,
            "version": scenario.identity.version,
        },
        "target": {
            "target_id": scenario.target.target_id,
            "protocol": scenario.target.protocol,
            "state_ref": scenario.target.state_ref,
        },
        "initial_state": {
            "state_id": scenario.initial_state.state_id,
            "description": scenario.initial_state.description,
        },
        "attack_steps": [
            {
                "attack_id": step.attack_id,
                "attack_type": step.attack_type,
                "expected_effect": step.expected_effect,
            }
            for step in scenario.attack_steps
        ],
        "expected_controls": [
            {
                "control_id": control.control_id,
                "control_type": control.control_type.value,
                "expectation": control.expectation.value,
            }
            for control in scenario.expected_controls
        ],
        "observations": [
            {
                "observation_id": observation.observation_id,
                "subject_id": observation.subject_id,
                "subject": observation.subject.value,
                "status": observation.status.value,
                "evidence_id": observation.evidence_id,
            }
            for observation in scenario.observations
        ],
        "containment": {
            "control_id": scenario.containment.control_id,
            "status": scenario.containment.status.value,
            "evidence_id": scenario.containment.evidence_id,
        },
        "economic_delta": {
            "asset": scenario.economic_delta.asset,
            "unit": scenario.economic_delta.unit,
            "before": scenario.economic_delta.before,
            "after": scenario.economic_delta.after,
        },
        "evidence": {
            "required": list(scenario.evidence.required),
            "present": list(scenario.evidence.present),
            "missing": list(scenario.evidence.missing),
        },
        "verdict": {"status": scenario.verdict.status.value},
    }


def scenario_to_json(scenario: Scenario) -> str:
    return json.dumps(
        scenario_to_dict(scenario),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def scenario_from_json(value: str) -> Scenario:
    if not isinstance(value, str):
        raise ValueError("scenario JSON must be a string")
    try:
        data = json.loads(value, parse_constant=_reject_json_constant)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("scenario JSON is invalid") from error
    return scenario_from_dict(data)


def scenario_from_dict(data: object) -> Scenario:
    scenario = _object(
        data,
        "scenario",
        {
            "identity",
            "target",
            "initial_state",
            "attack_steps",
            "expected_controls",
            "observations",
            "containment",
            "economic_delta",
            "evidence",
            "verdict",
        },
    )
    identity = _object(scenario["identity"], "identity", {"scenario_id", "version"})
    target = _object(
        scenario["target"],
        "target",
        {"target_id", "protocol", "state_ref"},
    )
    initial_state = _object(
        scenario["initial_state"],
        "initial_state",
        {"state_id", "description"},
    )
    return Scenario(
        identity=ScenarioIdentity(identity["scenario_id"], identity["version"]),
        target=Target(target["target_id"], target["protocol"], target["state_ref"]),
        initial_state=InitialState(
            initial_state["state_id"], initial_state["description"]
        ),
        attack_steps=tuple(
            _attack_step(item)
            for item in _array(scenario["attack_steps"], "attack_steps")
        ),
        expected_controls=tuple(
            _expected_control(item)
            for item in _array(scenario["expected_controls"], "expected_controls")
        ),
        observations=tuple(
            _observation(item)
            for item in _array(scenario["observations"], "observations")
        ),
        containment=_containment(scenario["containment"]),
        economic_delta=_economic_delta(scenario["economic_delta"]),
        evidence=_evidence(scenario["evidence"]),
        verdict=_verdict(scenario["verdict"]),
    )


def _attack_step(data: object) -> AttackStep:
    value = _object(
        data, "attack_step", {"attack_id", "attack_type", "expected_effect"}
    )
    return AttackStep(
        value["attack_id"], value["attack_type"], value["expected_effect"]
    )


def _expected_control(data: object) -> ExpectedControl:
    value = _object(
        data, "expected_control", {"control_id", "control_type", "expectation"}
    )
    return ExpectedControl(
        value["control_id"],
        _enum_value(value["control_type"], ControlType, "control_type"),
        _enum_value(value["expectation"], ControlExpectation, "expectation"),
    )


def _observation(data: object) -> Observation:
    value = _object(
        data,
        "observation",
        {"observation_id", "subject_id", "subject", "status", "evidence_id"},
    )
    return Observation(
        value["observation_id"],
        value["subject_id"],
        _enum_value(value["subject"], ObservationSubject, "subject"),
        _enum_value(value["status"], ObservationStatus, "status"),
        value["evidence_id"],
    )


def _containment(data: object) -> ContainmentResult:
    value = _object(data, "containment", {"control_id", "status", "evidence_id"})
    return ContainmentResult(
        value["control_id"],
        _enum_value(value["status"], ContainmentStatus, "status"),
        value["evidence_id"],
    )


def _economic_delta(data: object) -> EconomicDelta:
    value = _object(data, "economic_delta", {"asset", "unit", "before", "after"})
    return EconomicDelta(
        value["asset"],
        value["unit"],
        value["before"],
        value["after"],
    )


def _evidence(data: object) -> EvidenceCompleteness:
    value = _object(data, "evidence", {"required", "present", "missing"})
    return EvidenceCompleteness(
        tuple(_array(value["required"], "required")),
        tuple(_array(value["present"], "present")),
        tuple(_array(value["missing"], "missing")),
    )


def _verdict(data: object) -> DrillVerdict:
    value = _object(data, "verdict", {"status"})
    return DrillVerdict(_enum_value(value["status"], VerdictStatus, "status"))


def _object(data: object, name: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be an object")
    if not all(isinstance(key, str) for key in data):
        raise ValueError(f"{name} keys must be strings")
    unknown = set(data) - fields
    missing = fields - set(data)
    if unknown:
        raise ValueError(
            f"{name} contains unknown fields: {', '.join(sorted(unknown))}"
        )
    if missing:
        raise ValueError(f"{name} is missing fields: {', '.join(sorted(missing))}")
    return cast(dict[str, Any], data)


def _array(data: object, name: str) -> list[Any]:
    if not isinstance(data, list):
        raise ValueError(f"{name} must be an array")
    return cast(list[Any], data)


def _identifier(value: object, name: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{name} must be a stable lowercase identifier")


def _text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > 512:
        raise ValueError(f"{name} must be non-empty text up to 512 characters")


def _integer(value: object, name: str, *, minimum: int, maximum: int) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not minimum <= value <= maximum
    ):
        raise ValueError(f"{name} must be an integer between {minimum} and {maximum}")


def _enum(value: object, enum_type: type[Enum], name: str) -> None:
    if not isinstance(value, enum_type):
        raise ValueError(f"{name} must be a {enum_type.__name__}")


def _enum_value(
    value: object,
    enum_type: type[_EnumT],
    name: str,
) -> _EnumT:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string enum value")
    try:
        return enum_type(value)
    except ValueError as error:
        raise ValueError(f"{name} is invalid") from error


def _identifier_tuple(value: object, name: str, *, nonempty: bool = False) -> None:
    if (
        not isinstance(value, tuple)
        or (nonempty and not value)
        or len(value) > _MAX_COLLECTION
    ):
        raise ValueError(f"{name} must be a {'non-empty ' if nonempty else ''}tuple")
    for item in value:
        _identifier(item, name)
    _unique(value, name)


def _typed_tuple(
    value: object, item_type: type[object], name: str, *, nonempty: bool
) -> None:
    if (
        not isinstance(value, tuple)
        or (nonempty and not value)
        or len(value) > _MAX_COLLECTION
    ):
        raise ValueError(f"{name} must be a non-empty tuple")
    for item in value:
        _instance(item, item_type, name)


def _unique(values: Iterable[str], name: str) -> None:
    items = tuple(values)
    if len(items) != len(set(items)):
        raise ValueError(f"{name} must not contain duplicate identifiers")


def _instance(value: object, expected: type[object], name: str) -> None:
    if not isinstance(value, expected):
        raise ValueError(f"{name} must be a {expected.__name__}")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"unsupported JSON constant: {value}")
