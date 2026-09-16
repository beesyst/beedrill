from beesdk.artifacts import ArtifactPort
from beesdk.capabilities import CapabilityResult, CapabilityStatus
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleResult

_ISOLATED_SOLANA_CASE = "isolated_solana_smoke"
_ISOLATED_SOLANA_CAPABILITY = "solana.isolated_lifecycle"
_ISOLATED_SOLANA_PAYLOAD = {"target_profile": "surfpool_local"}
_LIFECYCLE_PROOF = {
    "lifecycle": "completed",
    "readiness": "ok",
    "rpc": "ok",
    "cleanup": "ok",
}


class BeeDrillModule:
    module_id = "beedrill"
    authority = AuthorityLevel.READ_ONLY

    def supported_case_types(self) -> list[str]:
        return ["integration_smoke", _ISOLATED_SOLANA_CASE]

    def handle(self, context: ModuleContext) -> ModuleResult:
        if context.case_type not in self.supported_case_types():
            raise ValueError(f"Unsupported case_type: {context.case_type}")

        if context.case_type == _ISOLATED_SOLANA_CASE:
            return self._handle_isolated_solana_smoke(context)

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

    def _handle_isolated_solana_smoke(self, context: ModuleContext) -> ModuleResult:
        if not _is_valid_isolated_solana_payload(context.payload):
            return self._capability_result(
                context,
                "refused",
                "BeeDrill isolated Solana intent is refused",
                {"capability_status": "refused"},
            )

        caller = context.capability_caller
        if caller is None:
            return self._capability_result(
                context,
                "error",
                "Host capability caller is unavailable",
                {"capability_status": "missing"},
            )

        result = caller.call(_ISOLATED_SOLANA_CAPABILITY, _ISOLATED_SOLANA_PAYLOAD)
        if not isinstance(result, CapabilityResult):
            return self._capability_result(
                context,
                "error",
                "Host capability returned an invalid result",
                {"capability_status": "invalid"},
            )
        capability_evidence = {
            "capability_status": result.status.value,
            "capability_authority": result.authority.value,
        }
        if result.capability_name != _ISOLATED_SOLANA_CAPABILITY:
            return self._capability_result(
                context,
                "error",
                "Host capability returned inconsistent evidence",
                capability_evidence,
            )
        if result.status is CapabilityStatus.OK:
            if result.data != _LIFECYCLE_PROOF:
                return self._capability_result(
                    context,
                    "error",
                    "Host capability lifecycle proof is incomplete",
                    capability_evidence,
                )
            return self._capability_result(
                context,
                "ok",
                "BeeDrill isolated Solana smoke completed",
                {**capability_evidence, "lifecycle": "verified"},
            )
        if result.status in {
            CapabilityStatus.REFUSED,
            CapabilityStatus.TIMEOUT,
            CapabilityStatus.ERROR,
        }:
            return self._capability_result(
                context,
                result.status.value,
                "BeeDrill isolated Solana smoke did not complete",
                capability_evidence,
            )
        return self._capability_result(
            context,
            "error",
            "Host capability returned an unknown status",
            {"capability_status": "invalid"},
        )

    def _capability_result(
        self,
        context: ModuleContext,
        status: str,
        summary: str,
        data: dict[str, str],
    ) -> ModuleResult:
        artifact_api: ArtifactPort | None = context.artifact_api
        if artifact_api is not None:
            artifact_api.write_json(
                "isolated_solana_smoke.json",
                {
                    "module_id": self.module_id,
                    "case_type": context.case_type,
                    "status": status,
                    "capability_status": data["capability_status"],
                    **(
                        {"capability_authority": data["capability_authority"]}
                        if "capability_authority" in data
                        else {}
                    ),
                },
            )
        return ModuleResult(
            module_id=self.module_id,
            case_type=context.case_type,
            authority=self.authority,
            status=status,
            summary=summary,
            data=data,
        )


def _is_valid_isolated_solana_payload(payload: object) -> bool:
    return type(payload) is dict and payload == _ISOLATED_SOLANA_PAYLOAD
