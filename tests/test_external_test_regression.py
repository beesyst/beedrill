import pytest
from beesdk._authority import AuthorityLevel
from beesdk.capabilities import CapabilityResult, CapabilityStatus
from beesdk.modules import ModuleContext

from beedrill.module import BeeDrillModule, _classify_external_test_diff


def _run(side: str, outcome: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "side": side,
        "runner_id": "litesvm_mocha_tsx_v1",
        "runner_version": "v22.22.1",
        "isolation": "bubblewrap_unshare_all",
        "isolation_result": "verified",
        "project_fingerprint": "e" * 64,
        "test_path": "tests/litesvm.test.ts",
        "test_fingerprint": "a" * 64,
        "dependency_fingerprint": "b" * 64,
        "exit_code": 0 if outcome == "passed" else 1,
        "timed_out": False,
        "execution_status": "completed",
        "outcome": outcome,
        "elapsed_seconds": 1.0,
        "cleanup": "ok",
        "diagnostic_output_sha256": "c" * 64,
    }


def test_comparable_failed_candidate_is_test_regression() -> None:
    evidence = {
        "schema_version": 1,
        "baseline": _run("baseline", "passed"),
        "candidate": _run("candidate", "failed"),
    }
    assert _classify_external_test_diff(evidence) == "test_regression"


def test_invalid_or_noncomparable_evidence_is_incomplete() -> None:
    evidence = {
        "schema_version": 1,
        "baseline": _run("baseline", "passed"),
        "candidate": _run("candidate", "failed"),
    }
    evidence["candidate"]["test_fingerprint"] = "d" * 64
    assert _classify_external_test_diff(evidence) == "incomplete"


def test_boolean_schema_version_and_contradictory_outcome_are_incomplete() -> None:
    evidence = {
        "schema_version": True,
        "baseline": _run("baseline", "passed"),
        "candidate": _run("candidate", "failed"),
    }
    assert _classify_external_test_diff(evidence) == "incomplete"

    evidence["schema_version"] = 1
    evidence["candidate"]["exit_code"] = 0
    assert _classify_external_test_diff(evidence) == "incomplete"


def test_report_projection_is_deterministic_and_contains_execution_provenance() -> None:
    evidence = {
        "schema_version": 1,
        "baseline": _run("baseline", "passed"),
        "candidate": _run("candidate", "failed"),
    }
    first = _report(evidence)
    second = _report(evidence)

    assert first == second

    baseline = first["baseline"]
    assert isinstance(baseline, dict)

    assert set(baseline) == {
        "runner_id",
        "runner_version",
        "test_path",
        "test_fingerprint",
        "dependency_fingerprint",
        "project_fingerprint",
        "isolation",
        "isolation_result",
        "outcome",
        "exit_code",
        "execution_status",
        "timed_out",
        "cleanup",
        "elapsed_seconds",
        "diagnostic_output_sha256",
    }


def test_missing_test_dependencies_are_unsupported_without_a_security_verdict() -> None:
    class Caller:
        def call(self, capability_name: str, payload: object) -> CapabilityResult:
            assert capability_name == "solana.isolated_litesvm_test_diff"
            assert payload == {"baseline": "/baseline", "candidate": "/candidate"}
            return CapabilityResult(
                capability_name=capability_name,
                status=CapabilityStatus.REFUSED,
                authority=AuthorityLevel.EXECUTION_CAPABLE,
                summary="Missing dependencies",
                diagnostics={"reason": "missing_test_dependencies"},
            )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="external_test_regression_diff",
            module_id="beedrill",
            payload={"baseline": "/baseline", "candidate": "/candidate"},
            capability_caller=Caller(),
        )
    )

    assert result.status == "unsupported"
    assert result.data == {"classification": "unsupported"}


@pytest.mark.parametrize(
    ("status", "authority"),
    [
        (CapabilityStatus.OK, AuthorityLevel.READ_ONLY),
        (CapabilityStatus.ERROR, AuthorityLevel.EXECUTION_CAPABLE),
    ],
)
def test_only_ok_execution_capable_evidence_can_be_classified(
    status: CapabilityStatus, authority: AuthorityLevel
) -> None:
    class Caller:
        def call(self, capability_name: str, payload: object) -> CapabilityResult:
            return CapabilityResult(
                capability_name=capability_name,
                status=status,
                authority=authority,
                summary="Host result",
                data={
                    "schema_version": 1,
                    "baseline": _run("baseline", "passed"),
                    "candidate": _run("candidate", "failed"),
                },
            )

    result = BeeDrillModule().handle(
        ModuleContext(
            run_id="run-1",
            case_type="external_test_regression_diff",
            module_id="beedrill",
            payload={"baseline": "/baseline", "candidate": "/candidate"},
            capability_caller=Caller(),
        )
    )

    assert result.status == "incomplete"
    assert result.data == {"classification": "incomplete"}


def _report(evidence: dict[str, object]) -> dict[str, object]:
    from beedrill.module import _external_test_diff_report_evidence

    return _external_test_diff_report_evidence(evidence)
