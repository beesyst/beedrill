import copy
import json
from pathlib import Path
from typing import Any

import pytest

from beedrill.domain import (
    ContainmentStatus,
    EconomicDelta,
    EvidenceCompleteness,
    ScenarioIdentity,
    VerdictStatus,
    scenario_from_dict,
    scenario_from_json,
    scenario_to_dict,
    scenario_to_json,
)

FIXTURE = Path(__file__).parent / "fixtures" / "failed_containment_drill.json"


def _fixture_data() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text())


def test_sanitized_fixture_represents_the_complete_failed_drill() -> None:
    scenario = scenario_from_json(FIXTURE.read_text())

    assert scenario.identity == ScenarioIdentity("pool_drain_control_failure", 1)
    assert scenario.observations[0].status.value == "observed"
    assert scenario.observations[1].status.value == "observed"
    assert scenario.containment.status is ContainmentStatus.FAILED
    assert scenario.economic_delta == EconomicDelta(
        "USDC",
        "micro_usdc",
        1_000_000_000,
        520_000_000,
    )
    assert scenario.economic_delta.before - scenario.economic_delta.after == 480_000_000
    assert scenario.evidence.missing == ()
    assert scenario.verdict.status is VerdictStatus.FAIL


def test_valid_scenario_round_trips_through_canonical_json() -> None:
    scenario = scenario_from_json(FIXTURE.read_text())
    serialized = scenario_to_json(scenario)

    assert serialized == scenario_to_json(scenario_from_json(serialized))
    assert scenario_from_dict(scenario_to_dict(scenario)) == scenario
    assert serialized.encode("utf-8") == scenario_to_json(scenario).encode("utf-8")
    assert "timestamp" not in serialized


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("identity", "scenario_id"), "not stable"),
        (("identity", "version"), 0),
        (("verdict", "status"), "maybe"),
        (("economic_delta", "before"), 1.5),
        (("economic_delta", "after"), 1.5),
        (("economic_delta", "asset"), "usdc"),
    ],
)
def test_malformed_critical_values_are_rejected(
    path: tuple[str, str], value: object
) -> None:
    data = _fixture_data()
    data[path[0]][path[1]] = value

    with pytest.raises(ValueError):
        scenario_from_dict(data)


def test_duplicate_identifiers_and_inconsistent_evidence_are_rejected() -> None:
    duplicate_attack = _fixture_data()
    duplicate_attack["attack_steps"].append(
        copy.deepcopy(duplicate_attack["attack_steps"][0])
    )
    incomplete_partition = _fixture_data()
    incomplete_partition["evidence"]["present"] = ["attack_event"]

    with pytest.raises(ValueError, match="duplicate"):
        scenario_from_dict(duplicate_attack)
    with pytest.raises(ValueError, match="partition"):
        scenario_from_dict(incomplete_partition)


def test_missing_required_field_is_rejected() -> None:
    data = _fixture_data()
    del data["identity"]["version"]

    with pytest.raises(ValueError, match="missing fields"):
        scenario_from_dict(data)


def test_missing_evidence_cannot_be_pass() -> None:
    data = _fixture_data()
    data["evidence"]["present"] = data["evidence"]["present"][:-1]
    data["evidence"]["missing"] = ["economic_delta"]
    data["verdict"]["status"] = "pass"

    with pytest.raises(ValueError, match="missing evidence"):
        scenario_from_dict(data)


def test_observations_require_explicit_matching_evidence_state() -> None:
    data = _fixture_data()
    data["evidence"]["present"].remove("detector_event")
    data["evidence"]["missing"].append("detector_event")

    with pytest.raises(ValueError, match="available observation evidence"):
        scenario_from_dict(data)


@pytest.mark.parametrize(
    "field",
    [
        "command",
        "shell",
        "executable",
        "script",
        "code",
        "args",
        "process_args",
        "rpc_destination",
        "rpc_url",
        "path",
        "filesystem_path",
        "credentials",
        "credential",
        "private_key",
        "private_keys",
    ],
)
def test_execution_shaped_fields_are_rejected_by_the_bounded_schema(field: str) -> None:
    data = _fixture_data()
    data["attack_steps"][0][field] = "untrusted"

    with pytest.raises(ValueError, match="unknown fields"):
        scenario_from_dict(data)


def test_unknown_fields_are_rejected_at_every_object_boundary() -> None:
    data = _fixture_data()
    data["target"]["unexpected"] = "value"

    with pytest.raises(ValueError, match="unknown fields"):
        scenario_from_dict(data)


def test_value_contracts_are_immutable_and_typed() -> None:
    evidence = EvidenceCompleteness(("attack_event",), ("attack_event",), ())
    attribute_name = "required"

    with pytest.raises((AttributeError, TypeError)):
        setattr(evidence, attribute_name, ())
    with pytest.raises(ValueError):
        EconomicDelta("USDC", "micro_usdc", True, 0)
