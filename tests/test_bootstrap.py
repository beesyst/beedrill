from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from beesdk.artifacts import ArtifactPort
from beesdk.capabilities import CapabilityResult, CapabilityStatus
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleContract, ModuleResult

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
