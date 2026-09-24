import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from beesdk._authority import AuthorityLevel
from beesdk.artifacts import ArtifactPort
from beesdk.capabilities import CapabilityResult, CapabilityStatus
from beesdk.modules import ModuleContext, ModuleContract, ModuleResult

from beedrill.module import BeeDrillModule


def test_first_party_package_initializer_is_byte_empty() -> None:
    initializer = Path(__file__).parents[1] / "src" / "beedrill" / "__init__.py"

    assert initializer.read_bytes() == b""


def test_module_identity_and_initial_authority() -> None:
    module = BeeDrillModule()

    assert module.module_id == "beedrill"
    assert module.authority is AuthorityLevel.READ_ONLY
    assert isinstance(module, ModuleContract)


def test_module_handles_only_the_bounded_integration_case() -> None:
    module = BeeDrillModule()
    artifact_api = _MemoryArtifactPort()
    context = ModuleContext(
        run_id="run-1",
        case_type="integration_smoke",
        module_id="beedrill",
        payload={"untrusted": "must not be echoed"},
        artifact_api=artifact_api,
    )

    result = module.handle(context)

    assert module.supported_case_types() == [
        "integration_smoke",
        "isolated_solana_smoke",
        "reference_target_baseline",
        "reference_target_attack",
        "reference_target_detection",
        "reference_target_containment_replay",
        "reference_oracle_manipulation_replay",
        "spl_token_freeze_containment_replay",
    ]
    assert isinstance(result, ModuleResult)
    assert result == ModuleResult(
        module_id="beedrill",
        case_type="integration_smoke",
        authority=AuthorityLevel.READ_ONLY,
        status="ok",
        summary="BeeDrill integration smoke completed",
        data={"integration": "beesdk_contract_smoke"},
    )
    assert artifact_api.artifacts == {
        "integration_smoke.json": {
            "module_id": "beedrill",
            "case_type": "integration_smoke",
            "status": "ok",
        }
    }


def test_module_rejects_unsupported_case_type() -> None:
    module = BeeDrillModule()

    with pytest.raises(ValueError, match="Unsupported case_type"):
        module.handle(
            ModuleContext(
                run_id="run-1",
                case_type="unsupported",
                module_id="beedrill",
            )
        )


class _FakeCapabilityCaller:
    def __init__(self, result: CapabilityResult) -> None:
        self.result = result
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(
        self,
        capability_name: str,
        payload: Mapping[str, Any],
    ) -> CapabilityResult:
        self.calls.append((capability_name, dict(payload)))
        return self.result


_VALID_ISOLATED_SOLANA_PAYLOAD = {"target_profile": "surfpool_local"}


def test_isolated_solana_smoke_requires_a_host_caller() -> None:
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
        )
    )

    assert result.status == "error"
    assert result.data == {"capability_status": "missing"}


def test_isolated_solana_smoke_uses_only_the_fixed_bounded_intent() -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.isolated_lifecycle",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data={
                "lifecycle": "completed",
                "readiness": "ok",
                "rpc": "ok",
                "cleanup": "ok",
            },
        )
    )
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.status == "ok"
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "lifecycle": "verified",
    }
    assert caller.calls == [
        ("solana.isolated_lifecycle", {"target_profile": "surfpool_local"})
    ]
    assert artifacts.artifacts["isolated_solana_smoke.json"] == {
        "module_id": "beedrill",
        "case_type": "isolated_solana_smoke",
        "status": "ok",
        "capability_status": "ok",
        "capability_authority": "execution_capable",
    }


def test_isolated_solana_smoke_rejects_incomplete_success_proof() -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.isolated_lifecycle",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.READ_ONLY,
            summary="completed",
            data={"lifecycle": "completed"},
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == "error"
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "read_only",
    }


@pytest.mark.parametrize(
    "status",
    [CapabilityStatus.REFUSED, CapabilityStatus.TIMEOUT, CapabilityStatus.ERROR],
)
def test_isolated_solana_smoke_preserves_host_non_success(
    status: CapabilityStatus,
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.isolated_lifecycle",
            status=status,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="not completed",
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == status.value
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": status.value,
        "capability_authority": "execution_capable",
    }


def test_isolated_solana_smoke_preserves_authority_for_inconsistent_evidence() -> None:
    artifacts = _MemoryArtifactPort()
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="other.capability",
            status=CapabilityStatus.ERROR,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="wrong capability",
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
            artifact_api=artifacts,
            capability_caller=caller,
        )
    )

    assert result.status == "error"
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": "error",
        "capability_authority": "execution_capable",
    }
    assert artifacts.artifacts["isolated_solana_smoke.json"] == {
        "module_id": "beedrill",
        "case_type": "isolated_solana_smoke",
        "status": "error",
        "capability_status": "error",
        "capability_authority": "execution_capable",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"target_profile": "other"},
        {"target_profile": "surfpool_local", "unknown": "value"},
        {"target_profile": "surfpool_local", "executable": "untrusted"},
        {"target_profile": "surfpool_local", "command": "untrusted"},
        {"target_profile": "surfpool_local", "args": "untrusted"},
        {"target_profile": "surfpool_local", "rpc_url": "untrusted"},
        {"target_profile": "surfpool_local", "rpc_endpoint": "untrusted"},
    ],
)
def test_isolated_solana_smoke_refuses_invalid_intent_without_host_call(
    payload: dict[str, str],
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.isolated_lifecycle",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )

    assert result.status == "refused"
    assert result.data == {"capability_status": "refused"}
    assert caller.calls == []


_VALID_REFERENCE_TARGET_PAYLOAD = {
    "target_profile": "surfpool_local",
    "target_id": "reference_vault",
}
_REFERENCE_TARGET_PROOF = {
    "target_id": "reference_vault",
    "initial_state_id": "reference_vault_canonical_v1",
    "economic_unit": "lamports",
    "vault_lamports": 1_000_000,
    "normal_operation": "ok",
    "unsafe_condition": "reachable",
    "detector_signal": "vault_outflow_signal",
    "breaker": "available",
    "containment_config": "broken_available",
    "reset": "equivalent",
    "cleanup": "ok",
}
_REFERENCE_TARGET_ATTACK_EVIDENCE = {
    "target_id": "reference_vault",
    "initial_state_id": "reference_vault_canonical_v1",
    "economic_unit": "lamports",
    "attack_start_slot": 42,
    "attack_transaction_signature": "attack-signature",
    "vault_lamports_before": 1_000_000,
    "vault_lamports_after": 999_900,
    "unsafe_withdraw_count_before": 0,
    "unsafe_withdraw_count_after": 1,
    "gross_loss_lamports": 100,
}
_REFERENCE_TARGET_DETECTION_EVIDENCE = {
    "detector_id": "reference_vault_outflow_monitor",
    "signal_id": "vault_outflow_signal",
    "detection_status": "observed",
    "attack_start_slot": 42,
    "first_detection_slot": 44,
}


def test_reference_target_baseline_uses_only_the_fixed_bounded_intent() -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_baseline",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_PROOF,
        )
    )
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_baseline",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.status == "ok"
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "baseline": "verified",
    }
    assert caller.calls == [
        ("solana.reference_target_baseline", _VALID_REFERENCE_TARGET_PAYLOAD)
    ]
    assert artifacts.artifacts["reference_target_baseline.json"] == {
        "module_id": "beedrill",
        "case_type": "reference_target_baseline",
        "status": "ok",
        "capability_status": "ok",
        "capability_authority": "execution_capable",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"target_profile": "other", "target_id": "reference_vault"},
        {"target_profile": "surfpool_local", "target_id": "other"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "rpc_url": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "program_path": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "raw_transaction": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "credential": "untrusted"},
    ],
)
def test_reference_target_baseline_refuses_invalid_intent(
    payload: dict[str, str],
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_baseline",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_PROOF,
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_baseline",
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )

    assert result.status == "refused"
    assert result.data == {"capability_status": "refused"}
    assert caller.calls == []


def test_reference_target_baseline_fails_closed_for_incomplete_evidence() -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_baseline",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data={"target_id": "reference_vault"},
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_baseline",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == "error"


def test_reference_target_attack_uses_only_the_fixed_bounded_intent() -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_attack",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_ATTACK_EVIDENCE,
        )
    )
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_attack",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.status == "ok"
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "attack": "verified",
    }
    assert caller.calls == [
        ("solana.reference_target_attack", _VALID_REFERENCE_TARGET_PAYLOAD)
    ]
    assert artifacts.artifacts["reference_target_attack.json"] == {
        "module_id": "beedrill",
        "case_type": "reference_target_attack",
        "status": "ok",
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "evidence": _REFERENCE_TARGET_ATTACK_EVIDENCE,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"target_profile": "other", "target_id": "reference_vault"},
        {"target_profile": "surfpool_local", "target_id": "other"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "rpc_url": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "executable": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "argv": ["untrusted"]},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "program_path": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "raw_transaction": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "credential": "untrusted"},
    ],
)
def test_reference_target_attack_refuses_invalid_intent(
    payload: dict[str, object],
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_attack",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_ATTACK_EVIDENCE,
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_attack",
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )

    assert result.status == "refused"
    assert result.data == {"capability_status": "refused"}
    assert caller.calls == []


@pytest.mark.parametrize(
    "status",
    [CapabilityStatus.REFUSED, CapabilityStatus.TIMEOUT, CapabilityStatus.ERROR],
)
def test_reference_target_attack_preserves_host_non_success(
    status: CapabilityStatus,
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_attack",
            status=status,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="not completed",
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_attack",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == status.value
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": status.value,
        "capability_authority": "execution_capable",
    }


@pytest.mark.parametrize(
    "result",
    [
        CapabilityResult(
            capability_name="solana.reference_target_attack",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.READ_ONLY,
            summary="completed",
            data=_REFERENCE_TARGET_ATTACK_EVIDENCE,
        ),
        CapabilityResult(
            capability_name="other.capability",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_ATTACK_EVIDENCE,
        ),
        CapabilityResult(
            capability_name="solana.reference_target_attack",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data={**_REFERENCE_TARGET_ATTACK_EVIDENCE, "gross_loss_lamports": 99},
        ),
        CapabilityResult(
            capability_name="solana.reference_target_attack",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data={
                key: value
                for key, value in _REFERENCE_TARGET_ATTACK_EVIDENCE.items()
                if key != "attack_transaction_signature"
            },
        ),
    ],
)
def test_reference_target_attack_fails_closed_for_invalid_success_evidence(
    result: CapabilityResult,
) -> None:
    artifacts = _MemoryArtifactPort()
    caller = _FakeCapabilityCaller(result)

    module_result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_attack",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert module_result.status == "error"
    assert module_result.authority is AuthorityLevel.READ_ONLY
    assert "evidence" not in artifacts.artifacts["reference_target_attack.json"]


def test_reference_target_detection_uses_only_the_fixed_bounded_intent() -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_detection",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_DETECTION_EVIDENCE,
        )
    )
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_detection",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.status == "ok"
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "detection": "verified",
    }
    assert caller.calls == [
        ("solana.reference_target_detection", _VALID_REFERENCE_TARGET_PAYLOAD)
    ]
    assert artifacts.artifacts["reference_target_detection.json"] == {
        "module_id": "beedrill",
        "case_type": "reference_target_detection",
        "status": "ok",
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "evidence": _REFERENCE_TARGET_DETECTION_EVIDENCE,
    }


def test_reference_target_detection_accepts_completed_not_observed() -> None:
    evidence = {
        "detector_id": "reference_vault_outflow_monitor",
        "signal_id": "vault_outflow_signal",
        "detection_status": "not_observed",
        "attack_start_slot": 42,
    }
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_detection",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=evidence,
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_detection",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == "ok"
    assert result.data["detection"] == "verified"


def test_reference_target_detection_preserves_semantics_for_replayed_evidence() -> None:
    results = []
    for _ in range(2):
        caller = _FakeCapabilityCaller(
            CapabilityResult(
                capability_name="solana.reference_target_detection",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=_REFERENCE_TARGET_DETECTION_EVIDENCE,
            )
        )
        results.append(
            BeeDrillModule().handle(
                ModuleContext(
                    run_id="run-1",
                    case_type="reference_target_detection",
                    module_id="beedrill",
                    payload=_VALID_REFERENCE_TARGET_PAYLOAD,
                    capability_caller=caller,
                )
            )
        )

    assert results[0] == results[1]


@pytest.mark.parametrize(
    "evidence",
    [
        {},
        CapabilityResult(
            capability_name="solana.reference_target_detection",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.READ_ONLY,
            summary="completed",
            data=_REFERENCE_TARGET_DETECTION_EVIDENCE,
        ),
        CapabilityResult(
            capability_name="other.capability",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_DETECTION_EVIDENCE,
        ),
        {**_REFERENCE_TARGET_DETECTION_EVIDENCE, "first_detection_slot": 41},
        {
            key: value
            for key, value in _REFERENCE_TARGET_DETECTION_EVIDENCE.items()
            if key != "first_detection_slot"
        },
        {**_REFERENCE_TARGET_DETECTION_EVIDENCE, "unknown": "value"},
        {**_REFERENCE_TARGET_DETECTION_EVIDENCE, "detector_id": "other"},
        {**_REFERENCE_TARGET_DETECTION_EVIDENCE, "signal_id": "other"},
        {**_REFERENCE_TARGET_DETECTION_EVIDENCE, "attack_start_slot": True},
        {
            "detector_id": "reference_vault_outflow_monitor",
            "signal_id": "vault_outflow_signal",
            "detection_status": "not_observed",
            "attack_start_slot": 42,
            "first_detection_slot": 44,
        },
    ],
)
def test_reference_target_detection_fails_closed_for_invalid_success_evidence(
    evidence: CapabilityResult | dict[str, object],
) -> None:
    artifacts = _MemoryArtifactPort()
    host_result = (
        evidence
        if isinstance(evidence, CapabilityResult)
        else CapabilityResult(
            capability_name="solana.reference_target_detection",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=evidence,
        )
    )
    caller = _FakeCapabilityCaller(host_result)

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_detection",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.status == "error"
    assert "evidence" not in artifacts.artifacts["reference_target_detection.json"]


@pytest.mark.parametrize(
    "status",
    [CapabilityStatus.REFUSED, CapabilityStatus.TIMEOUT, CapabilityStatus.ERROR],
)
def test_reference_target_detection_preserves_host_non_success(
    status: CapabilityStatus,
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_detection",
            status=status,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="not completed",
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_detection",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == status.value
    assert result.authority is AuthorityLevel.READ_ONLY


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"target_profile": "other", "target_id": "reference_vault"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "rpc_url": "untrusted"},
        {**_VALID_REFERENCE_TARGET_PAYLOAD, "detector": "untrusted"},
    ],
)
def test_reference_target_detection_refuses_invalid_intent(
    payload: dict[str, str],
) -> None:
    caller = _FakeCapabilityCaller(
        CapabilityResult(
            capability_name="solana.reference_target_detection",
            status=CapabilityStatus.OK,
            authority=AuthorityLevel.EXECUTION_CAPABLE,
            summary="completed",
            data=_REFERENCE_TARGET_DETECTION_EVIDENCE,
        )
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_detection",
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )

    assert result.status == "refused"
    assert caller.calls == []


def _containment_evidence(condition: str) -> dict[str, object]:
    broken = condition == "broken"
    return {
        "target_id": "reference_vault",
        "initial_state_id": "reference_vault_canonical_v1",
        "economic_unit": "lamports",
        "defense_condition": condition,
        "attack_sequence_id": "reference_vault_unsafe_withdraw_twice_v1",
        "initial_vault_lamports": 1_000_000,
        "attack_start_slot": 42,
        "first_attack_signature": "attack-1",
        "first_attack_vault_lamports": 999_900,
        "first_attack_unsafe_withdraw_count": 1,
        "detection_status": "observed",
        "first_detection_slot": 44,
        "containment_status": "failed" if broken else "succeeded",
        "first_containment_slot": None if broken else 46,
        "second_attack_status": "succeeded" if broken else "rejected",
        "final_vault_lamports": 999_800 if broken else 999_900,
        "final_unsafe_withdraw_count": 2 if broken else 1,
        "residual_loss_lamports": 200 if broken else 100,
    }


class _ContainmentCapabilityCaller:
    def __init__(self, results: list[CapabilityResult]) -> None:
        self.results = iter(results)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def call(
        self,
        capability_name: str,
        payload: Mapping[str, Any],
    ) -> CapabilityResult:
        self.calls.append((capability_name, dict(payload)))
        return next(self.results)


def test_reference_target_containment_replay_evaluates_real_host_evidence() -> None:
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name="solana.reference_target_containment",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=_containment_evidence("broken"),
            ),
            CapabilityResult(
                capability_name="solana.reference_target_containment",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=_containment_evidence("fixed"),
            ),
        ]
    )
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_containment_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.status == "ok"
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "broken_verdict": "fail",
        "fixed_verdict": "pass",
        "security_verdict": "pass",
    }
    assert caller.calls == [
        (
            "solana.reference_target_containment",
            {**_VALID_REFERENCE_TARGET_PAYLOAD, "defense_condition": "broken"},
        ),
        (
            "solana.reference_target_containment",
            {**_VALID_REFERENCE_TARGET_PAYLOAD, "defense_condition": "fixed"},
        ),
    ]
    comparison = artifacts.artifacts["reference_target_containment_replay.json"]
    assert isinstance(comparison, Mapping)
    artifact_comparison = comparison["comparison"]
    assert isinstance(artifact_comparison, Mapping)
    metrics = artifact_comparison["metrics"]
    assert isinstance(metrics, Mapping)
    broken_metrics = metrics["broken"]
    fixed_metrics = metrics["fixed"]
    assert isinstance(broken_metrics, Mapping)
    assert isinstance(fixed_metrics, Mapping)
    assert broken_metrics["mttc_slots"] is None
    assert fixed_metrics["capital_saved_lamports"] == 100


def test_reference_target_containment_reports_a_completed_fixed_regression() -> None:
    fixed = _containment_evidence("broken")
    fixed["defense_condition"] = "fixed"
    artifacts = _MemoryArtifactPort()
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_containment_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=_ContainmentCapabilityCaller(
                [
                    CapabilityResult(
                        capability_name="solana.reference_target_containment",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=_containment_evidence("broken"),
                    ),
                    CapabilityResult(
                        capability_name="solana.reference_target_containment",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=fixed,
                    ),
                ]
            ),
            artifact_api=artifacts,
        )
    )

    assert result.status == "ok"
    assert result.data["security_verdict"] == "fail"
    assert result.data["fixed_verdict"] == "fail"
    artifact = artifacts.artifacts["reference_target_containment_replay.json"]
    assert isinstance(artifact, Mapping)
    assert artifact["security_verdict"] == "fail"


def test_reference_target_containment_rejects_a_passing_negative_control() -> None:
    broken = _containment_evidence("fixed")
    broken["defense_condition"] = "broken"
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_containment_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=_ContainmentCapabilityCaller(
                [
                    CapabilityResult(
                        capability_name="solana.reference_target_containment",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=broken,
                    ),
                    CapabilityResult(
                        capability_name="solana.reference_target_containment",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=_containment_evidence("fixed"),
                    ),
                ]
            ),
        )
    )

    assert result.status == "error"
    assert "security_verdict" not in result.data


def test_reference_target_containment_replays_deterministically() -> None:
    results = []
    for _ in range(2):
        results.append(
            BeeDrillModule().handle(
                ModuleContext(
                    run_id="run-1",
                    case_type="reference_target_containment_replay",
                    module_id="beedrill",
                    payload=_VALID_REFERENCE_TARGET_PAYLOAD,
                    capability_caller=_ContainmentCapabilityCaller(
                        [
                            CapabilityResult(
                                capability_name="solana.reference_target_containment",
                                status=CapabilityStatus.OK,
                                authority=AuthorityLevel.EXECUTION_CAPABLE,
                                summary="completed",
                                data=_containment_evidence("broken"),
                            ),
                            CapabilityResult(
                                capability_name="solana.reference_target_containment",
                                status=CapabilityStatus.OK,
                                authority=AuthorityLevel.EXECUTION_CAPABLE,
                                summary="completed",
                                data=_containment_evidence("fixed"),
                            ),
                        ]
                    ),
                )
            )
        )

    assert results[0] == results[1]


@pytest.mark.parametrize(
    "status",
    [CapabilityStatus.REFUSED, CapabilityStatus.TIMEOUT, CapabilityStatus.ERROR],
)
def test_reference_target_containment_preserves_host_non_success(
    status: CapabilityStatus,
) -> None:
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name="solana.reference_target_containment",
                status=status,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="not completed",
            )
        ]
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_containment_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == status.value
    assert len(caller.calls) == 1


def test_reference_target_containment_fails_closed_for_contradictory_evidence() -> None:
    broken = _containment_evidence("broken")
    broken["second_attack_status"] = "rejected"
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name="solana.reference_target_containment",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=broken,
            )
        ]
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_containment_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == "error"
    assert result.data["capability_status"] == "ok"


class _MemoryArtifactPort:
    def __init__(self) -> None:
        self.artifacts: dict[str, dict[str, object] | list[object]] = {}

    def write_json(
        self,
        filename: str,
        data: dict[str, object] | list[object],
    ) -> str:
        self.artifacts[filename] = data
        return filename


def test_memory_artifact_port_satisfies_beesdk_contract() -> None:
    assert isinstance(_MemoryArtifactPort(), ArtifactPort)


_VALID_REFERENCE_ORACLE_PAYLOAD = {
    "target_profile": "surfpool_local",
    "target_id": "reference_oracle_market",
}


def test_reference_oracle_market_resource_has_fixed_economics() -> None:
    resource = (
        Path(__file__).parents[1]
        / "src"
        / "beedrill"
        / "reference_target"
        / "reference_oracle_market.json"
    )

    data = json.loads(resource.read_text())

    assert data == {
        "canonical_initial_state": {
            "borrow_increment_micro_usdc": 25_000_000,
            "canonical_debt_limit_micro_usdc": 50_000_000,
            "canonical_oracle_price_micro_usd": 1_000_000,
            "collateral_units": 100,
            "initial_debt_micro_usdc": 50_000_000,
            "initial_reserve_micro_usdc": 100_000_000,
            "ltv_bps": 5_000,
            "manipulated_oracle_price_micro_usd": 2_000_000,
        },
        "resource_id": "beedrill.reference_oracle_market.v1",
        "target_id": "reference_oracle_market",
    }


def _oracle_evidence(condition: str) -> dict[str, object]:
    broken = condition == "broken"
    return {
        "target_id": "reference_oracle_market",
        "initial_state_id": "reference_oracle_market_canonical_v1",
        "economic_unit": "micro_usdc",
        "defense_condition": condition,
        "attack_sequence_id": "reference_oracle_manipulation_borrow_twice_v1",
        "canonical_oracle_price_micro_usd": 1_000_000,
        "manipulated_oracle_price_micro_usd": 2_000_000,
        "collateral_units": 100,
        "ltv_bps": 5_000,
        "canonical_debt_limit_micro_usdc": 50_000_000,
        "initial_debt_micro_usdc": 50_000_000,
        "initial_reserve_micro_usdc": 100_000_000,
        "attack_start_slot": 42,
        "oracle_manipulation_signature": "oracle-manipulation",
        "first_borrow_signature": "borrow-1",
        "first_borrow_debt_micro_usdc": 75_000_000,
        "first_borrow_reserve_micro_usdc": 75_000_000,
        "detector_id": "reference_oracle_deviation_monitor",
        "signal_id": "oracle_price_deviation_signal",
        "detection_status": "observed",
        "first_detection_slot": 44,
        "containment_status": "failed" if broken else "succeeded",
        "first_containment_slot": None if broken else 46,
        "containment_state": "borrowing_open" if broken else "borrowing_blocked",
        "second_borrow_status": "succeeded" if broken else "rejected",
        "final_debt_micro_usdc": 100_000_000 if broken else 75_000_000,
        "final_reserve_micro_usdc": 50_000_000 if broken else 75_000_000,
        "residual_loss_micro_usdc": 50_000_000 if broken else 25_000_000,
    }


def _oracle_caller() -> _ContainmentCapabilityCaller:
    return _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name="solana.reference_oracle_manipulation",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=_oracle_evidence("broken"),
            ),
            CapabilityResult(
                capability_name="solana.reference_oracle_manipulation",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=_oracle_evidence("fixed"),
            ),
        ]
    )


def test_reference_oracle_manipulation_replay_evaluates_host_evidence() -> None:
    caller = _oracle_caller()
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )

    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.status == "ok"
    assert result.data["broken_verdict"] == "fail"
    assert result.data["fixed_verdict"] == "pass"
    assert result.data["security_verdict"] == "pass"
    assert caller.calls == [
        (
            "solana.reference_oracle_manipulation",
            {**_VALID_REFERENCE_ORACLE_PAYLOAD, "defense_condition": "broken"},
        ),
        (
            "solana.reference_oracle_manipulation",
            {**_VALID_REFERENCE_ORACLE_PAYLOAD, "defense_condition": "fixed"},
        ),
    ]
    artifact = artifacts.artifacts["reference_oracle_manipulation_replay.json"]
    assert isinstance(artifact, Mapping)
    comparison = artifact["comparison"]
    assert isinstance(comparison, Mapping)
    assert comparison["scenario"] == {
        "scenario_id": "reference_oracle_manipulation_replay",
        "version": 1,
    }
    metrics = comparison["metrics"]
    assert isinstance(metrics, Mapping)
    assert metrics["broken"]["residual_loss_micro_usdc"] == 50_000_000
    assert metrics["fixed"]["residual_loss_micro_usdc"] == 25_000_000
    assert metrics["fixed"]["gross_attack_loss_micro_usdc"] == 50_000_000
    assert metrics["fixed"]["capital_saved_micro_usdc"] == 25_000_000


def test_reference_oracle_reports_a_completed_fixed_regression() -> None:
    fixed = _oracle_evidence("broken")
    fixed["defense_condition"] = "fixed"
    artifacts = _MemoryArtifactPort()
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
            capability_caller=_ContainmentCapabilityCaller(
                [
                    CapabilityResult(
                        capability_name="solana.reference_oracle_manipulation",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=_oracle_evidence("broken"),
                    ),
                    CapabilityResult(
                        capability_name="solana.reference_oracle_manipulation",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=fixed,
                    ),
                ]
            ),
            artifact_api=artifacts,
        )
    )

    assert result.status == "ok"
    assert result.data["security_verdict"] == "fail"
    assert result.data["fixed_verdict"] == "fail"
    artifact = artifacts.artifacts["reference_oracle_manipulation_replay.json"]
    assert isinstance(artifact, Mapping)
    assert artifact["security_verdict"] == "fail"


def test_reference_oracle_rejects_a_passing_negative_control() -> None:
    broken = _oracle_evidence("fixed")
    broken["defense_condition"] = "broken"
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
            capability_caller=_ContainmentCapabilityCaller(
                [
                    CapabilityResult(
                        capability_name="solana.reference_oracle_manipulation",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=broken,
                    ),
                    CapabilityResult(
                        capability_name="solana.reference_oracle_manipulation",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=_oracle_evidence("fixed"),
                    ),
                ]
            ),
        )
    )

    assert result.status == "error"
    assert "security_verdict" not in result.data


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"target_profile": "other", "target_id": "reference_oracle_market"},
        {"target_profile": "surfpool_local", "target_id": "reference_vault"},
        {**_VALID_REFERENCE_ORACLE_PAYLOAD, "price": 2_000_000},
        {**_VALID_REFERENCE_ORACLE_PAYLOAD, "borrow": 25_000_000},
        {**_VALID_REFERENCE_ORACLE_PAYLOAD, "rpc_url": "untrusted"},
        {**_VALID_REFERENCE_ORACLE_PAYLOAD, "executable": "untrusted"},
    ],
)
def test_reference_oracle_manipulation_refuses_untrusted_intent(
    payload: dict[str, object],
) -> None:
    caller = _oracle_caller()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )

    assert result.status == "refused"
    assert caller.calls == []


@pytest.mark.parametrize(
    "mutation",
    [
        lambda evidence: evidence.pop("detector_id"),
        lambda evidence: evidence.update({"unknown": "value"}),
        lambda evidence: evidence.update({"canonical_oracle_price_micro_usd": 1}),
        lambda evidence: evidence.update({"first_borrow_debt_micro_usdc": 50_000_000}),
        lambda evidence: evidence.update({"first_detection_slot": 41}),
        lambda evidence: evidence.update({"first_detection_slot": True}),
        lambda evidence: evidence.update({"second_borrow_status": "rejected"}),
        lambda evidence: evidence.update({"residual_loss_micro_usdc": 0}),
    ],
)
def test_reference_oracle_manipulation_fails_closed_for_invalid_evidence(
    mutation: Any,
) -> None:
    broken = _oracle_evidence("broken")
    mutation(broken)
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name="solana.reference_oracle_manipulation",
                status=CapabilityStatus.OK,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="completed",
                data=broken,
            )
        ]
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == "error"
    assert len(caller.calls) == 1


@pytest.mark.parametrize(
    "status",
    [CapabilityStatus.REFUSED, CapabilityStatus.TIMEOUT, CapabilityStatus.ERROR],
)
def test_reference_oracle_manipulation_preserves_host_non_success(
    status: CapabilityStatus,
) -> None:
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name="solana.reference_oracle_manipulation",
                status=status,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="not completed",
            )
        ]
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
            capability_caller=caller,
        )
    )

    assert result.status == status.value
    assert len(caller.calls) == 1


def test_reference_oracle_manipulation_replays_deterministically() -> None:
    results = []
    for _ in range(2):
        results.append(
            BeeDrillModule().handle(
                ModuleContext(
                    run_id="run-1",
                    case_type="reference_oracle_manipulation_replay",
                    module_id="beedrill",
                    payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
                    capability_caller=_oracle_caller(),
                )
            )
        )

    assert results[0] == results[1]


@pytest.mark.parametrize(
    ("field", "value", "expected_status"),
    [
        ("status", "ok", "error"),
        ("authority", "execution_capable", "error"),
        ("capability_name", 1, "error"),
        ("data", ["sentinel-secret-value"], "error"),
        ("diagnostics", "sentinel-secret-value", "error"),
        ("summary", "sentinel-secret-value", "ok"),
    ],
)
def test_isolated_solana_smoke_rejects_malformed_envelopes_without_secret_leaks(
    field: str,
    value: object,
    expected_status: str,
) -> None:
    sentinel = "sentinel-secret-value"
    host_result = CapabilityResult(
        capability_name="solana.isolated_lifecycle",
        status=CapabilityStatus.OK,
        authority=AuthorityLevel.EXECUTION_CAPABLE,
        summary="completed",
        data={
            "lifecycle": "completed",
            "readiness": "ok",
            "rpc": "ok",
            "cleanup": "ok",
        },
        diagnostics={"sentinel": sentinel},
    )
    object.__setattr__(host_result, field, value)
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
            capability_caller=_FakeCapabilityCaller(host_result),
            artifact_api=artifacts,
        )
    )

    assert result.status == expected_status
    assert result.authority is AuthorityLevel.READ_ONLY
    assert sentinel not in repr(artifacts.artifacts)


@pytest.mark.parametrize("value", [True, -1, 1_000_000_001])
def test_reference_target_attack_rejects_unbounded_integer_evidence(
    value: object,
) -> None:
    evidence = dict(_REFERENCE_TARGET_ATTACK_EVIDENCE)
    evidence["attack_start_slot"] = value
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_attack",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=_FakeCapabilityCaller(
                CapabilityResult(
                    capability_name="solana.reference_target_attack",
                    status=CapabilityStatus.OK,
                    authority=AuthorityLevel.EXECUTION_CAPABLE,
                    summary="completed",
                    data=evidence,
                )
            ),
            artifact_api=artifacts,
        )
    )

    assert result.status == "error"
    assert "evidence" not in artifacts.artifacts["reference_target_attack.json"]


def test_reference_target_containment_rejects_oversized_evidence_before_arithmetic() -> (
    None
):
    broken = _containment_evidence("broken")
    broken["final_vault_lamports"] = 10**1000

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_target_containment_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_TARGET_PAYLOAD,
            capability_caller=_ContainmentCapabilityCaller(
                [
                    CapabilityResult(
                        capability_name="solana.reference_target_containment",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=broken,
                    )
                ]
            ),
        )
    )

    assert result.status == "error"
    assert "security_verdict" not in result.data


def test_reference_oracle_rejects_oversized_evidence_before_arithmetic() -> None:
    broken = _oracle_evidence("broken")
    broken["collateral_units"] = 10**1000

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="reference_oracle_manipulation_replay",
            module_id="beedrill",
            payload=_VALID_REFERENCE_ORACLE_PAYLOAD,
            capability_caller=_ContainmentCapabilityCaller(
                [
                    CapabilityResult(
                        capability_name="solana.reference_oracle_manipulation",
                        status=CapabilityStatus.OK,
                        authority=AuthorityLevel.EXECUTION_CAPABLE,
                        summary="completed",
                        data=broken,
                    )
                ]
            ),
        )
    )

    assert result.status == "error"
    assert "security_verdict" not in result.data


@pytest.mark.parametrize("field", ["status", "authority", "capability_name", "data"])
def test_isolated_solana_smoke_rejects_missing_capability_envelope_fields(
    field: str,
) -> None:
    sentinel = "sentinel-secret-value"
    host_result = CapabilityResult(
        capability_name="solana.isolated_lifecycle",
        status=CapabilityStatus.OK,
        authority=AuthorityLevel.EXECUTION_CAPABLE,
        summary="completed",
        data={
            "lifecycle": "completed",
            "readiness": "ok",
            "rpc": "ok",
            "cleanup": "ok",
        },
        diagnostics={"sentinel": sentinel},
    )
    object.__delattr__(host_result, field)
    artifacts = _MemoryArtifactPort()

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="isolated_solana_smoke",
            module_id="beedrill",
            payload=_VALID_ISOLATED_SOLANA_PAYLOAD,
            capability_caller=_FakeCapabilityCaller(host_result),
            artifact_api=artifacts,
        )
    )

    assert result.status == "error"
    assert result.data == {"capability_status": "invalid"}
    assert sentinel not in repr(artifacts.artifacts)


@pytest.mark.parametrize(
    ("case_type", "capability_name", "signature_field"),
    [
        (
            "reference_target_attack",
            "solana.reference_target_attack",
            "attack_transaction_signature",
        ),
        (
            "reference_target_containment_replay",
            "solana.reference_target_containment",
            "first_attack_signature",
        ),
        (
            "reference_oracle_manipulation_replay",
            "solana.reference_oracle_manipulation",
            "oracle_manipulation_signature",
        ),
    ],
)
def test_replays_reject_oversized_transaction_identifiers(
    case_type: str,
    capability_name: str,
    signature_field: str,
) -> None:
    if case_type == "reference_target_attack":
        payload = _VALID_REFERENCE_TARGET_PAYLOAD
        evidence = dict(_REFERENCE_TARGET_ATTACK_EVIDENCE)
        caller_type = _FakeCapabilityCaller
    elif case_type == "reference_target_containment_replay":
        payload = _VALID_REFERENCE_TARGET_PAYLOAD
        evidence = _containment_evidence("broken")
        caller_type = _ContainmentCapabilityCaller
    else:
        payload = _VALID_REFERENCE_ORACLE_PAYLOAD
        evidence = _oracle_evidence("broken")
        caller_type = _ContainmentCapabilityCaller
    evidence[signature_field] = "x" * 129
    host_result = CapabilityResult(
        capability_name=capability_name,
        status=CapabilityStatus.OK,
        authority=AuthorityLevel.EXECUTION_CAPABLE,
        summary="completed",
        data=evidence,
    )
    caller = (
        caller_type(host_result)
        if caller_type is _FakeCapabilityCaller
        else _ContainmentCapabilityCaller([host_result])
    )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type=case_type,
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )

    assert result.status == "error"
    assert "security_verdict" not in result.data


_VALID_SPL_TOKEN_FREEZE_PAYLOAD = {
    "target_profile": "surfpool_local",
    "target_id": "spl_token_freeze_containment",
}


def _spl_token_evidence(condition: str) -> dict[str, object]:
    broken = condition == "broken"
    return {
        "target_id": "spl_token_freeze_containment",
        "initial_state_id": "spl_token_freeze_containment_canonical_v1",
        "economic_unit": "base_units",
        "program_id": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        "defense_condition": condition,
        "attack_sequence_id": "spl_token_transfer_twice_v1",
        "initial_source_balance_units": 1_000_000,
        "initial_target_balance_units": 0,
        "attack_start_slot": 42,
        "first_transfer_signature": "transfer-1",
        "first_transfer_source_balance_units": 900_000,
        "first_transfer_target_balance_units": 100_000,
        "detector_id": "spl_token_target_balance_monitor",
        "signal_id": "spl_token_target_balance_signal",
        "detection_status": "observed",
        "first_detection_slot": 44,
        "containment_status": "failed" if broken else "succeeded",
        "first_containment_slot": None if broken else 46,
        "target_account_state": "initialized" if broken else "frozen",
        "second_transfer_status": "succeeded" if broken else "rejected",
        "final_source_balance_units": 800_000 if broken else 900_000,
        "final_target_balance_units": 200_000 if broken else 100_000,
        "residual_loss_units": 200_000 if broken else 100_000,
    }


def _spl_token_caller() -> _ContainmentCapabilityCaller:
    return _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                "solana.spl_token_freeze_containment",
                CapabilityStatus.OK,
                AuthorityLevel.EXECUTION_CAPABLE,
                "completed",
                _spl_token_evidence("broken"),
            ),
            CapabilityResult(
                "solana.spl_token_freeze_containment",
                CapabilityStatus.OK,
                AuthorityLevel.EXECUTION_CAPABLE,
                "completed",
                _spl_token_evidence("fixed"),
            ),
        ]
    )


def test_spl_token_freeze_containment_replay_evaluates_bounded_host_evidence() -> None:
    caller = _spl_token_caller()
    artifacts = _MemoryArtifactPort()
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
            capability_caller=caller,
            artifact_api=artifacts,
        )
    )
    assert result.authority is AuthorityLevel.READ_ONLY
    assert result.status == "ok"
    assert result.data == {
        "capability_status": "ok",
        "capability_authority": "execution_capable",
        "broken_verdict": "fail",
        "fixed_verdict": "pass",
        "security_verdict": "pass",
    }
    assert caller.calls == [
        (
            "solana.spl_token_freeze_containment",
            {**_VALID_SPL_TOKEN_FREEZE_PAYLOAD, "defense_condition": "broken"},
        ),
        (
            "solana.spl_token_freeze_containment",
            {**_VALID_SPL_TOKEN_FREEZE_PAYLOAD, "defense_condition": "fixed"},
        ),
    ]
    artifact = artifacts.artifacts["spl_token_freeze_containment_replay.json"]
    assert isinstance(artifact, Mapping)
    comparison = artifact["comparison"]
    assert isinstance(comparison, Mapping)
    assert comparison["scenario"] == {
        "scenario_id": "spl_token_freeze_containment_replay",
        "version": 1,
    }
    assert comparison["metrics"]["broken"]["residual_loss_units"] == 200_000
    assert comparison["metrics"]["fixed"]["capital_saved_units"] == 100_000
    assert "completed" not in repr(artifact)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"target_profile": "other", "target_id": "spl_token_freeze_containment"},
        {"target_profile": "surfpool_local", "target_id": "other"},
        {**_VALID_SPL_TOKEN_FREEZE_PAYLOAD, "program_id": "untrusted"},
        {**_VALID_SPL_TOKEN_FREEZE_PAYLOAD, "rpc_url": "untrusted"},
        {**_VALID_SPL_TOKEN_FREEZE_PAYLOAD, "executable": "untrusted"},
    ],
)
def test_spl_token_freeze_refuses_untrusted_intent(payload: dict[str, object]) -> None:
    caller = _spl_token_caller()
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=payload,
            capability_caller=caller,
        )
    )
    assert result.status == "refused"
    assert caller.calls == []


@pytest.mark.parametrize(
    "mutation",
    [
        lambda evidence: evidence.pop("program_id"),
        lambda evidence: evidence.update({"unknown": "value"}),
        lambda evidence: evidence.update({"program_id": "untrusted"}),
        lambda evidence: evidence.update({"first_detection_slot": True}),
        lambda evidence: evidence.update({"final_target_balance_units": -1}),
        lambda evidence: evidence.update({"attack_start_slot": 1_000_000_001}),
        lambda evidence: evidence.update({"second_transfer_status": "rejected"}),
        lambda evidence: evidence.update({"residual_loss_units": 0}),
    ],
)
def test_spl_token_freeze_fails_closed_for_invalid_evidence(mutation: Any) -> None:
    broken = _spl_token_evidence("broken")
    mutation(broken)
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                "solana.spl_token_freeze_containment",
                CapabilityStatus.OK,
                AuthorityLevel.EXECUTION_CAPABLE,
                "completed",
                broken,
            )
        ]
    )
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
            capability_caller=caller,
        )
    )
    assert result.status == "error"
    assert "security_verdict" not in result.data
    assert len(caller.calls) == 1


@pytest.mark.parametrize(
    "status",
    [CapabilityStatus.REFUSED, CapabilityStatus.TIMEOUT, CapabilityStatus.ERROR],
)
def test_spl_token_freeze_preserves_host_non_success(status: CapabilityStatus) -> None:
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                "solana.spl_token_freeze_containment",
                status,
                AuthorityLevel.EXECUTION_CAPABLE,
                "not completed",
            )
        ]
    )
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
            capability_caller=caller,
        )
    )
    assert result.status == status.value
    assert len(caller.calls) == 1


@pytest.mark.parametrize(
    "capability_name, authority",
    [
        ("solana.other", AuthorityLevel.EXECUTION_CAPABLE),
        ("solana.spl_token_freeze_containment", AuthorityLevel.READ_ONLY),
    ],
)
def test_spl_token_freeze_rejects_wrong_capability_or_authority(
    capability_name: str,
    authority: AuthorityLevel,
) -> None:
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                capability_name,
                CapabilityStatus.OK,
                authority,
                "completed",
                _spl_token_evidence("broken"),
            )
        ]
    )
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
            capability_caller=caller,
        )
    )
    assert result.status == "error"
    assert "security_verdict" not in result.data


def test_spl_token_freeze_rejects_missing_caller_and_malformed_envelope() -> None:
    missing = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
        )
    )
    malformed = CapabilityResult(
        "solana.spl_token_freeze_containment",
        CapabilityStatus.OK,
        AuthorityLevel.EXECUTION_CAPABLE,
        "completed",
        _spl_token_evidence("broken"),
    )
    object.__setattr__(malformed, "diagnostics", "private")
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
            capability_caller=_FakeCapabilityCaller(malformed),
        )
    )
    assert missing.status == "error"
    assert result.status == "error"
    assert result.data == {"capability_status": "invalid"}


def test_spl_token_freeze_replay_is_deterministic() -> None:
    results = [
        BeeDrillModule().handle(
            ModuleContext(
                run_id="run-1",
                case_type="spl_token_freeze_containment_replay",
                module_id="beedrill",
                payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
                capability_caller=_spl_token_caller(),
            )
        )
        for _ in range(2)
    ]
    assert results[0] == results[1]


@pytest.mark.parametrize(
    ("requested_condition", "evidence_condition"),
    [("fixed", "broken"), ("broken", "fixed")],
)
def test_spl_token_freeze_rejects_cross_labelled_phase_evidence(
    requested_condition: str, evidence_condition: str
) -> None:
    evidence = _spl_token_evidence(evidence_condition)
    evidence["defense_condition"] = requested_condition
    caller = _ContainmentCapabilityCaller(
        [
            CapabilityResult(
                "solana.spl_token_freeze_containment",
                CapabilityStatus.OK,
                AuthorityLevel.EXECUTION_CAPABLE,
                "completed",
                evidence,
            )
        ]
    )
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="spl_token_freeze_containment_replay",
            module_id="beedrill",
            payload=_VALID_SPL_TOKEN_FREEZE_PAYLOAD,
            capability_caller=caller,
        )
    )
    assert result.status == "error"
    assert "security_verdict" not in result.data
