import pytest
from beesdk.artifacts import ArtifactPort
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleContract, ModuleResult

from beedrill.module import BeeDrillModule


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

    assert module.supported_case_types() == ["integration_smoke"]
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
