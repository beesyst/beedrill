from beesdk.artifacts import ArtifactPort
from beesdk.capabilities import CapabilityResult, CapabilityStatus
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleResult

_REFERENCE_TARGET_CASE = "reference_target_baseline"
_REFERENCE_TARGET_CAPABILITY = "solana.reference_target_baseline"
_REFERENCE_TARGET_PAYLOAD = {
    "target_profile": "surfpool_local",
    "target_id": "reference_vault",
}
_REFERENCE_TARGET_PROOF = {
    "target_id": "reference_vault",
    "initial_state_id": "reference_vault_canonical_v1",
    "economic_unit": "lamports",
    "vault_lamports": 1000000,
    "normal_operation": "ok",
    "unsafe_condition": "reachable",
    "detector_signal": "vault_outflow_signal",
    "breaker": "available",
    "containment_config": "broken_available",
    "reset": "equivalent",
    "cleanup": "ok",
}

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
        return [
            "integration_smoke",
            _ISOLATED_SOLANA_CASE,
            _REFERENCE_TARGET_CASE,
        ]

    def handle(self, context: ModuleContext) -> ModuleResult:
        if context.case_type not in self.supported_case_types():
            raise ValueError(f"Unsupported case_type: {context.case_type}")

        if context.case_type == _ISOLATED_SOLANA_CASE:
            return self._handle_isolated_solana_smoke(context)
        if context.case_type == _REFERENCE_TARGET_CASE:
            return self._handle_reference_target_baseline(context)

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

    def _handle_reference_target_baseline(
        self,
        context: ModuleContext,
    ) -> ModuleResult:
        if not _is_valid_reference_target_payload(context.payload):
            return self._reference_target_result(
                context,
                "refused",
                "BeeDrill reference target intent is refused",
                {"capability_status": "refused"},
            )

        caller = context.capability_caller
        if caller is None:
            return self._reference_target_result(
                context,
                "error",
                "Host capability caller is unavailable",
                {"capability_status": "missing"},
            )

        result = caller.call(_REFERENCE_TARGET_CAPABILITY, _REFERENCE_TARGET_PAYLOAD)
        if not isinstance(result, CapabilityResult):
            return self._reference_target_result(
                context,
                "error",
                "Host capability returned an invalid result",
                {"capability_status": "invalid"},
            )
        evidence = {
            "capability_status": result.status.value,
            "capability_authority": result.authority.value,
        }
        if result.capability_name != _REFERENCE_TARGET_CAPABILITY:
            return self._reference_target_result(
                context,
                "error",
                "Host capability returned inconsistent evidence",
                evidence,
            )
        if result.status is CapabilityStatus.OK:
            if result.data != _REFERENCE_TARGET_PROOF:
                return self._reference_target_result(
                    context,
                    "error",
                    "Host capability baseline proof is incomplete",
                    evidence,
                )
            return self._reference_target_result(
                context,
                "ok",
                "BeeDrill reference target baseline completed",
                {**evidence, "baseline": "verified"},
            )
        if result.status in {
            CapabilityStatus.REFUSED,
            CapabilityStatus.TIMEOUT,
            CapabilityStatus.ERROR,
        }:
            return self._reference_target_result(
                context,
                result.status.value,
                "BeeDrill reference target baseline did not complete",
                evidence,
            )
        return self._reference_target_result(
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

    def _reference_target_result(
        self,
        context: ModuleContext,
        status: str,
        summary: str,
        data: dict[str, str],
    ) -> ModuleResult:
        artifact_api: ArtifactPort | None = context.artifact_api
        if artifact_api is not None:
            artifact_api.write_json(
                "reference_target_baseline.json",
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


def _is_valid_reference_target_payload(payload: object) -> bool:
    return type(payload) is dict and payload == _REFERENCE_TARGET_PAYLOAD
