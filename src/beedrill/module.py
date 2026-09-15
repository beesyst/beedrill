from beesdk.artifacts import ArtifactPort
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleResult


class BeeDrillModule:
    module_id = "beedrill"
    authority = AuthorityLevel.READ_ONLY

    def supported_case_types(self) -> list[str]:
        return ["integration_smoke"]

    def handle(self, context: ModuleContext) -> ModuleResult:
        if context.case_type not in self.supported_case_types():
            raise ValueError(f"Unsupported case_type: {context.case_type}")

        artifact_api: ArtifactPort | None = context.artifact_api
        if artifact_api is not None:
            artifact_api.write_json(
                "integration_smoke.json",
                {
                    "module_id": self.module_id,
                    "case_type": context.case_type,
                    "status": "ok",
                },
            )

        return ModuleResult(
            module_id=self.module_id,
            case_type=context.case_type,
            authority=self.authority,
            status="ok",
            summary="BeeDrill integration smoke completed",
            data={"integration": "beesdk_contract_smoke"},
        )
