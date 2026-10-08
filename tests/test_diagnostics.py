import json
from collections.abc import Mapping
from typing import Any

import pytest
from beesdk.capabilities import CapabilityResult, CapabilityStatus
from beesdk.modules import AuthorityLevel, ModuleContext

from beedrill.module import BeeDrillModule, _bounded_diagnostic_reason

_CASES = [
    ("isolated_solana_smoke", "solana.isolated_lifecycle", None),
    (
        "reference_target_baseline",
        "solana.reference_target_baseline",
        "reference_vault",
    ),
    ("reference_target_attack", "solana.reference_target_attack", "reference_vault"),
    (
        "reference_target_detection",
        "solana.reference_target_detection",
        "reference_vault",
    ),
    (
        "reference_target_containment_replay",
        "solana.reference_target_containment",
        "reference_vault",
    ),
    (
        "reference_oracle_manipulation_replay",
        "solana.reference_oracle_manipulation",
        "reference_oracle_market",
    ),
    (
        "spl_token_freeze_containment_replay",
        "solana.spl_token_freeze_containment",
        "spl_token_freeze_containment",
    ),
]


class _Artifacts:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any] | list[Any]] = {}

    def write_json(self, filename: str, data: dict[str, Any] | list[Any]) -> None:
        self.values[filename] = data


class _Caller:
    def __init__(self, result: CapabilityResult) -> None:
        self.result = result

    def call(
        self,
        capability_name: str,
        payload: Mapping[str, Any],
    ) -> CapabilityResult:
        return self.result


@pytest.mark.parametrize(
    "reason",
    [
        ["sentinel-secret"],
        {"key": "sentinel-secret"},
        None,
        42,
        1.5,
        True,
        "unknown-sentinel-secret",
        "unknown-sentinel-secret_timeout",
        "cleanup_unknown-sentinel-secret",
        "unknown-build-sentinel-secret",
        "preparation_build_error",
        "cleanup_success",
        "deploy_timeout",
    ],
)
@pytest.mark.parametrize("case,capability,target", _CASES)
@pytest.mark.parametrize(
    "status",
    [
        CapabilityStatus.ERROR,
        CapabilityStatus.TIMEOUT,
        CapabilityStatus.REFUSED,
        CapabilityStatus.OK,
    ],
)
def test_malformed_diagnostics_cannot_crash_leak_or_produce_pass(
    reason, case, capability, target, status
):
    artifacts = _Artifacts()
    payload = {"target_profile": "surfpool_local"}
    if target is not None:
        payload["target_id"] = target
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-diagnostics",
            module_id="beedrill",
            case_type=case,
            payload=payload,
            artifact_api=artifacts,
            capability_caller=_Caller(
                CapabilityResult(
                    capability_name=capability,
                    status=status,
                    authority=AuthorityLevel.EXECUTION_CAPABLE,
                    summary="sentinel-secret",
                    diagnostics={"reason": reason, "stderr": "sentinel-secret"},
                    data={"private_key": "sentinel-secret"},
                )
            ),
        )
    )
    assert result.status != "ok"
    assert result.authority is AuthorityLevel.READ_ONLY
    assert "security_verdict" not in result.data
    assert "explanation_facts" not in result.data
    assert "diagnostic_reason" not in result.data
    assert "sentinel-secret" not in json.dumps(
        [result.data, result.summary, artifacts.values]
    )


@pytest.mark.parametrize(
    "reason,mapped",
    [
        ("missing_cargo", "missing_cargo"),
        ("missing_solana_cli", "missing_solana_cli"),
        ("missing_sbf_builder", "missing_sbf_builder"),
        ("incompatible_toolchain", "incompatible_toolchain"),
        ("executable_unavailable", "missing_surfpool"),
        ("startup_failed", "surfpool_startup_failed"),
        ("early_process_exit", "surfpool_startup_failed"),
        ("rpc_error", "rpc_unavailable"),
        ("rpc_failed", "rpc_unavailable"),
        ("build_failed", "build_failed"),
        ("build_timeout", "timeout"),
        ("readiness_timeout", "timeout"),
        ("rpc_timeout", "timeout"),
        ("transaction_confirmation_timeout", "timeout"),
        ("state_observation_timeout", "timeout"),
        ("detector_observation_timeout", "timeout"),
        ("containment_observation_timeout", "timeout"),
        ("deployment_timeout", "timeout"),
        ("cleanup_forced", "cleanup_failed"),
        ("cleanup_reap_failed", "cleanup_failed"),
        ("missing_surfpool", "missing_surfpool"),
        ("surfpool_startup_failed", "surfpool_startup_failed"),
        ("rpc_unavailable", "rpc_unavailable"),
        ("timeout", "timeout"),
        ("cleanup_failed", "cleanup_failed"),
    ],
)
def test_existing_diagnostic_mappings_are_preserved(reason, mapped):
    assert _bounded_diagnostic_reason(reason) == mapped


@pytest.mark.parametrize("case,capability,target", _CASES)
def test_diagnosed_reason_is_persisted_without_raw_host_output(
    case, capability, target
):
    artifacts = _Artifacts()
    payload = {"target_profile": "surfpool_local"}
    if target is not None:
        payload["target_id"] = target
    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-diagnostics",
            module_id="beedrill",
            case_type=case,
            payload=payload,
            artifact_api=artifacts,
            capability_caller=_Caller(
                CapabilityResult(
                    capability_name=capability,
                    status=CapabilityStatus.ERROR,
                    authority=AuthorityLevel.EXECUTION_CAPABLE,
                    summary="sentinel-secret",
                    diagnostics={
                        "reason": "missing_surfpool",
                        "stderr": "sentinel-secret",
                    },
                )
            ),
        )
    )
    assert result.status == "error"
    assert result.data["diagnostic_reason"] == "missing_surfpool"
    assert all(
        isinstance(value, dict) and value["diagnostic_reason"] == "missing_surfpool"
        for value in artifacts.values.values()
    )
    assert "sentinel-secret" not in json.dumps(
        [result.data, result.summary, artifacts.values]
    )
