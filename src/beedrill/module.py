from beesdk.artifacts import ArtifactPort
from beesdk.capabilities import CapabilityCaller, CapabilityResult, CapabilityStatus
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleResult

from beedrill.domain import ContainmentStatus, EvidenceCompleteness, ObservationStatus
from beedrill.evaluator import (
    DrillEvaluation,
    DrillEvidence,
    EconomicLoss,
    evaluate_drill,
)

_REFERENCE_TARGET_CASE = "reference_target_baseline"
_REFERENCE_TARGET_CAPABILITY = "solana.reference_target_baseline"
_REFERENCE_TARGET_ATTACK_CASE = "reference_target_attack"
_REFERENCE_TARGET_ATTACK_CAPABILITY = "solana.reference_target_attack"
_REFERENCE_TARGET_DETECTION_CASE = "reference_target_detection"
_REFERENCE_TARGET_DETECTION_CAPABILITY = "solana.reference_target_detection"
_REFERENCE_TARGET_CONTAINMENT_CASE = "reference_target_containment_replay"
_REFERENCE_TARGET_CONTAINMENT_CAPABILITY = "solana.reference_target_containment"
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
_REFERENCE_TARGET_ATTACK_EVIDENCE_FIELDS = {
    "target_id",
    "initial_state_id",
    "economic_unit",
    "attack_start_slot",
    "attack_transaction_signature",
    "vault_lamports_before",
    "vault_lamports_after",
    "unsafe_withdraw_count_before",
    "unsafe_withdraw_count_after",
    "gross_loss_lamports",
}
_REFERENCE_TARGET_DETECTION_EVIDENCE_FIELDS = {
    "detector_id",
    "signal_id",
    "detection_status",
    "attack_start_slot",
}
_REFERENCE_TARGET_OBSERVED_DETECTION_EVIDENCE_FIELDS = (
    _REFERENCE_TARGET_DETECTION_EVIDENCE_FIELDS | {"first_detection_slot"}
)
_REFERENCE_TARGET_CONTAINMENT_EVIDENCE_FIELDS = {
    "target_id",
    "initial_state_id",
    "economic_unit",
    "defense_condition",
    "attack_sequence_id",
    "initial_vault_lamports",
    "attack_start_slot",
    "first_attack_signature",
    "first_attack_vault_lamports",
    "first_attack_unsafe_withdraw_count",
    "detection_status",
    "first_detection_slot",
    "containment_status",
    "first_containment_slot",
    "second_attack_status",
    "final_vault_lamports",
    "final_unsafe_withdraw_count",
    "residual_loss_lamports",
}
_REFERENCE_TARGET_CONTAINMENT_SCENARIO = {
    "scenario_id": "reference_target_containment_replay",
    "version": 1,
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
            _REFERENCE_TARGET_ATTACK_CASE,
            _REFERENCE_TARGET_DETECTION_CASE,
            _REFERENCE_TARGET_CONTAINMENT_CASE,
        ]

    def handle(self, context: ModuleContext) -> ModuleResult:
        if context.case_type not in self.supported_case_types():
            raise ValueError(f"Unsupported case_type: {context.case_type}")

        if context.case_type == _ISOLATED_SOLANA_CASE:
            return self._handle_isolated_solana_smoke(context)
        if context.case_type == _REFERENCE_TARGET_CASE:
            return self._handle_reference_target_baseline(context)
        if context.case_type == _REFERENCE_TARGET_ATTACK_CASE:
            return self._handle_reference_target_attack(context)
        if context.case_type == _REFERENCE_TARGET_DETECTION_CASE:
            return self._handle_reference_target_detection(context)
        if context.case_type == _REFERENCE_TARGET_CONTAINMENT_CASE:
            return self._handle_reference_target_containment(context)

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

    def _handle_reference_target_attack(
        self,
        context: ModuleContext,
    ) -> ModuleResult:
        if not _is_valid_reference_target_payload(context.payload):
            return self._reference_target_attack_result(
                context,
                "refused",
                "BeeDrill reference target attack intent is refused",
                {"capability_status": "refused"},
            )

        caller = context.capability_caller
        if caller is None:
            return self._reference_target_attack_result(
                context,
                "error",
                "Host capability caller is unavailable",
                {"capability_status": "missing"},
            )

        result = caller.call(
            _REFERENCE_TARGET_ATTACK_CAPABILITY,
            _REFERENCE_TARGET_PAYLOAD,
        )
        if not isinstance(result, CapabilityResult):
            return self._reference_target_attack_result(
                context,
                "error",
                "Host capability returned an invalid result",
                {"capability_status": "invalid"},
            )
        capability_evidence = {
            "capability_status": result.status.value,
            "capability_authority": result.authority.value,
        }
        if result.capability_name != _REFERENCE_TARGET_ATTACK_CAPABILITY:
            return self._reference_target_attack_result(
                context,
                "error",
                "Host capability returned inconsistent evidence",
                capability_evidence,
            )
        if result.status is CapabilityStatus.OK:
            if (
                result.authority is not AuthorityLevel.EXECUTION_CAPABLE
                or not _is_valid_reference_target_attack_evidence(result.data)
            ):
                return self._reference_target_attack_result(
                    context,
                    "error",
                    "Host capability attack evidence is incomplete",
                    capability_evidence,
                )
            return self._reference_target_attack_result(
                context,
                "ok",
                "BeeDrill reference target attack completed",
                {**capability_evidence, "attack": "verified"},
                result.data,
            )
        if result.status in {
            CapabilityStatus.REFUSED,
            CapabilityStatus.TIMEOUT,
            CapabilityStatus.ERROR,
        }:
            return self._reference_target_attack_result(
                context,
                result.status.value,
                "BeeDrill reference target attack did not complete",
                capability_evidence,
            )
        return self._reference_target_attack_result(
            context,
            "error",
            "Host capability returned an unknown status",
            {"capability_status": "invalid"},
        )

    def _handle_reference_target_detection(
        self,
        context: ModuleContext,
    ) -> ModuleResult:
        if not _is_valid_reference_target_payload(context.payload):
            return self._reference_target_detection_result(
                context,
                "refused",
                "BeeDrill reference target detection intent is refused",
                {"capability_status": "refused"},
            )

        caller = context.capability_caller
        if caller is None:
            return self._reference_target_detection_result(
                context,
                "error",
                "Host capability caller is unavailable",
                {"capability_status": "missing"},
            )

        result = caller.call(
            _REFERENCE_TARGET_DETECTION_CAPABILITY,
            _REFERENCE_TARGET_PAYLOAD,
        )
        if not isinstance(result, CapabilityResult):
            return self._reference_target_detection_result(
                context,
                "error",
                "Host capability returned an invalid result",
                {"capability_status": "invalid"},
            )
        capability_evidence = {
            "capability_status": result.status.value,
            "capability_authority": result.authority.value,
        }
        if result.capability_name != _REFERENCE_TARGET_DETECTION_CAPABILITY:
            return self._reference_target_detection_result(
                context,
                "error",
                "Host capability returned inconsistent evidence",
                capability_evidence,
            )
        if result.status is CapabilityStatus.OK:
            if (
                result.authority is not AuthorityLevel.EXECUTION_CAPABLE
                or not _is_valid_reference_target_detection_evidence(result.data)
            ):
                return self._reference_target_detection_result(
                    context,
                    "error",
                    "Host capability detection evidence is incomplete",
                    capability_evidence,
                )
            return self._reference_target_detection_result(
                context,
                "ok",
                "BeeDrill reference target detection completed",
                {**capability_evidence, "detection": "verified"},
                result.data,
            )
        if result.status in {
            CapabilityStatus.REFUSED,
            CapabilityStatus.TIMEOUT,
            CapabilityStatus.ERROR,
        }:
            return self._reference_target_detection_result(
                context,
                result.status.value,
                "BeeDrill reference target detection did not complete",
                capability_evidence,
            )
        return self._reference_target_detection_result(
            context,
            "error",
            "Host capability returned an unknown status",
            {"capability_status": "invalid"},
        )

    def _handle_reference_target_containment(
        self,
        context: ModuleContext,
    ) -> ModuleResult:
        if not _is_valid_reference_target_payload(context.payload):
            return self._reference_target_containment_result(
                context,
                "refused",
                "BeeDrill reference target containment intent is refused",
                {"capability_status": "refused"},
            )
        caller = context.capability_caller
        if caller is None:
            return self._reference_target_containment_result(
                context,
                "error",
                "Host capability caller is unavailable",
                {"capability_status": "missing"},
            )
        broken = self._call_reference_target_containment(caller, "broken")
        if isinstance(broken, ModuleResult):
            return self._reference_target_containment_result(
                context,
                broken.status,
                broken.summary,
                broken.data,
            )
        fixed = self._call_reference_target_containment(caller, "fixed")
        if isinstance(fixed, ModuleResult):
            return self._reference_target_containment_result(
                context,
                fixed.status,
                fixed.summary,
                fixed.data,
            )
        try:
            broken_evaluation = _containment_evaluation(
                broken, broken["residual_loss_lamports"]
            )
            fixed_evaluation = _containment_evaluation(
                fixed, broken["residual_loss_lamports"]
            )
        except KeyError, ValueError:
            return self._reference_target_containment_result(
                context,
                "error",
                "Host capability containment evidence is inconsistent",
                {
                    "capability_status": "ok",
                    "capability_authority": "execution_capable",
                },
            )
        if (
            broken_evaluation.verdict.status.value != "fail"
            or fixed_evaluation.verdict.status.value != "pass"
            or fixed_evaluation.metrics.capital_saved is None
            or fixed_evaluation.metrics.capital_saved.amount <= 0
        ):
            return self._reference_target_containment_result(
                context,
                "error",
                "Host capability containment replay did not prove FAIL to PASS",
                {
                    "capability_status": "ok",
                    "capability_authority": "execution_capable",
                },
            )
        return self._reference_target_containment_result(
            context,
            "ok",
            "BeeDrill reference target containment replay completed",
            {
                "capability_status": "ok",
                "capability_authority": "execution_capable",
                "broken_verdict": broken_evaluation.verdict.status.value,
                "fixed_verdict": fixed_evaluation.verdict.status.value,
            },
            {
                "scenario": _REFERENCE_TARGET_CONTAINMENT_SCENARIO,
                "broken": broken,
                "fixed": fixed,
                "metrics": {
                    "broken": _evaluation_to_dict(broken_evaluation),
                    "fixed": _evaluation_to_dict(fixed_evaluation),
                },
            },
        )

    def _call_reference_target_containment(
        self,
        caller: CapabilityCaller,
        defense_condition: str,
    ) -> dict[str, object] | ModuleResult:
        result = caller.call(
            _REFERENCE_TARGET_CONTAINMENT_CAPABILITY,
            {**_REFERENCE_TARGET_PAYLOAD, "defense_condition": defense_condition},
        )
        if not isinstance(result, CapabilityResult):
            return ModuleResult(
                module_id=self.module_id,
                case_type=_REFERENCE_TARGET_CONTAINMENT_CASE,
                authority=self.authority,
                status="error",
                summary="Host capability returned an invalid result",
                data={"capability_status": "invalid"},
            )
        evidence = {
            "capability_status": result.status.value,
            "capability_authority": result.authority.value,
        }
        if result.capability_name != _REFERENCE_TARGET_CONTAINMENT_CAPABILITY:
            return ModuleResult(
                self.module_id,
                _REFERENCE_TARGET_CONTAINMENT_CASE,
                self.authority,
                "error",
                "Host capability returned inconsistent evidence",
                evidence,
            )
        if result.status in {
            CapabilityStatus.REFUSED,
            CapabilityStatus.TIMEOUT,
            CapabilityStatus.ERROR,
        }:
            return ModuleResult(
                self.module_id,
                _REFERENCE_TARGET_CONTAINMENT_CASE,
                self.authority,
                result.status.value,
                "BeeDrill reference target containment replay did not complete",
                evidence,
            )
        if (
            result.status is not CapabilityStatus.OK
            or result.authority is not AuthorityLevel.EXECUTION_CAPABLE
            or not _is_valid_reference_target_containment_evidence(
                result.data, defense_condition
            )
        ):
            return ModuleResult(
                self.module_id,
                _REFERENCE_TARGET_CONTAINMENT_CASE,
                self.authority,
                "error",
                "Host capability containment evidence is incomplete",
                evidence,
            )
        return result.data

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

    def _reference_target_attack_result(
        self,
        context: ModuleContext,
        status: str,
        summary: str,
        data: dict[str, str],
        evidence: dict[str, object] | None = None,
    ) -> ModuleResult:
        artifact_api: ArtifactPort | None = context.artifact_api
        if artifact_api is not None:
            artifact_api.write_json(
                "reference_target_attack.json",
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
                    **({"evidence": evidence} if evidence is not None else {}),
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

    def _reference_target_detection_result(
        self,
        context: ModuleContext,
        status: str,
        summary: str,
        data: dict[str, str],
        evidence: dict[str, object] | None = None,
    ) -> ModuleResult:
        artifact_api: ArtifactPort | None = context.artifact_api
        if artifact_api is not None:
            artifact_api.write_json(
                "reference_target_detection.json",
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
                    **({"evidence": evidence} if evidence is not None else {}),
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

    def _reference_target_containment_result(
        self,
        context: ModuleContext,
        status: str,
        summary: str,
        data: dict[str, object],
        comparison: dict[str, object] | None = None,
    ) -> ModuleResult:
        artifact_api: ArtifactPort | None = context.artifact_api
        if artifact_api is not None:
            artifact_api.write_json(
                "reference_target_containment_replay.json",
                {
                    "module_id": self.module_id,
                    "case_type": context.case_type,
                    "status": status,
                    **data,
                    **({"comparison": comparison} if comparison is not None else {}),
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


def _is_valid_reference_target_attack_evidence(evidence: object) -> bool:
    if (
        type(evidence) is not dict
        or set(evidence) != _REFERENCE_TARGET_ATTACK_EVIDENCE_FIELDS
    ):
        return False
    values = evidence
    integer_fields = {
        "attack_start_slot",
        "vault_lamports_before",
        "vault_lamports_after",
        "unsafe_withdraw_count_before",
        "unsafe_withdraw_count_after",
        "gross_loss_lamports",
    }
    if any(
        isinstance(values[field], bool)
        or not isinstance(values[field], int)
        or values[field] < 0
        for field in integer_fields
    ):
        return False
    signature = values["attack_transaction_signature"]
    return (
        values["target_id"] == "reference_vault"
        and values["initial_state_id"] == "reference_vault_canonical_v1"
        and values["economic_unit"] == "lamports"
        and isinstance(signature, str)
        and bool(signature)
        and len(signature) <= 128
        and values["vault_lamports_before"] == 1_000_000
        and values["vault_lamports_after"] == 999_900
        and values["unsafe_withdraw_count_before"] == 0
        and values["unsafe_withdraw_count_after"] == 1
        and values["gross_loss_lamports"]
        == values["vault_lamports_before"] - values["vault_lamports_after"]
    )


def _is_valid_reference_target_detection_evidence(evidence: object) -> bool:
    if type(evidence) is not dict:
        return False
    values = evidence
    status = values.get("detection_status")
    if status == "observed":
        expected_fields = _REFERENCE_TARGET_OBSERVED_DETECTION_EVIDENCE_FIELDS
    elif status == "not_observed":
        expected_fields = _REFERENCE_TARGET_DETECTION_EVIDENCE_FIELDS
    else:
        return False

    if set(values) != expected_fields:
        return False

    attack_start_slot = values["attack_start_slot"]
    if (
        isinstance(attack_start_slot, bool)
        or not isinstance(attack_start_slot, int)
        or attack_start_slot < 0
        or values["detector_id"] != "reference_vault_outflow_monitor"
        or values["signal_id"] != "vault_outflow_signal"
    ):
        return False
    if status == "not_observed":
        return True
    first_detection_slot = values["first_detection_slot"]
    return (
        not isinstance(first_detection_slot, bool)
        and isinstance(first_detection_slot, int)
        and first_detection_slot >= attack_start_slot
    )


def _is_valid_reference_target_containment_evidence(
    evidence: object,
    defense_condition: str,
) -> bool:
    if (
        type(evidence) is not dict
        or set(evidence) != _REFERENCE_TARGET_CONTAINMENT_EVIDENCE_FIELDS
    ):
        return False
    values = evidence
    integer_fields = {
        "initial_vault_lamports",
        "attack_start_slot",
        "first_attack_vault_lamports",
        "first_attack_unsafe_withdraw_count",
        "first_detection_slot",
        "final_vault_lamports",
        "final_unsafe_withdraw_count",
        "residual_loss_lamports",
    }
    if any(
        isinstance(values[field], bool)
        or not isinstance(values[field], int)
        or values[field] < 0
        for field in integer_fields
    ):
        return False
    containment_slot = values["first_containment_slot"]
    if containment_slot is not None and (
        isinstance(containment_slot, bool)
        or not isinstance(containment_slot, int)
        or containment_slot < values["first_detection_slot"]
    ):
        return False
    if (
        values["target_id"] != "reference_vault"
        or values["initial_state_id"] != "reference_vault_canonical_v1"
        or values["economic_unit"] != "lamports"
        or values["defense_condition"] != defense_condition
        or values["attack_sequence_id"] != "reference_vault_unsafe_withdraw_twice_v1"
        or values["initial_vault_lamports"] != 1_000_000
        or values["first_attack_vault_lamports"] != 999_900
        or values["first_attack_unsafe_withdraw_count"] != 1
        or values["detection_status"] != "observed"
        or not isinstance(values["first_attack_signature"], str)
        or not values["first_attack_signature"]
        or len(values["first_attack_signature"]) > 128
        or values["residual_loss_lamports"]
        != values["initial_vault_lamports"] - values["final_vault_lamports"]
    ):
        return False
    if defense_condition == "broken":
        return (
            values["containment_status"] == "failed"
            and containment_slot is None
            and values["second_attack_status"] == "succeeded"
            and values["final_vault_lamports"] == 999_800
            and values["final_unsafe_withdraw_count"] == 2
            and values["residual_loss_lamports"] == 200
        )
    return (
        values["containment_status"] == "succeeded"
        and containment_slot is not None
        and values["second_attack_status"] == "rejected"
        and values["final_vault_lamports"] == 999_900
        and values["final_unsafe_withdraw_count"] == 1
        and values["residual_loss_lamports"] == 100
    )


def _containment_evaluation(
    evidence: dict[str, object],
    gross_loss_lamports: object,
) -> DrillEvaluation:
    if isinstance(gross_loss_lamports, bool) or not isinstance(
        gross_loss_lamports, int
    ):
        raise ValueError("gross loss must be an integer")
    detection_status = evidence["detection_status"]
    containment_status = evidence["containment_status"]
    attack_start_slot = evidence["attack_start_slot"]
    first_detection_slot = evidence["first_detection_slot"]
    first_containment_slot = evidence["first_containment_slot"]
    residual_loss_lamports = evidence["residual_loss_lamports"]
    if (
        not isinstance(detection_status, str)
        or not isinstance(containment_status, str)
        or isinstance(attack_start_slot, bool)
        or not isinstance(attack_start_slot, int)
        or isinstance(first_detection_slot, bool)
        or not isinstance(first_detection_slot, int)
        or (
            first_containment_slot is not None
            and (
                isinstance(first_containment_slot, bool)
                or not isinstance(first_containment_slot, int)
            )
        )
        or isinstance(residual_loss_lamports, bool)
        or not isinstance(residual_loss_lamports, int)
    ):
        raise ValueError("containment evidence has invalid field types")
    return evaluate_drill(
        DrillEvidence(
            evidence=EvidenceCompleteness(
                ("attack", "detection", "containment", "economics"),
                ("attack", "detection", "containment", "economics"),
                (),
            ),
            detection_status=ObservationStatus(detection_status),
            containment_status=ContainmentStatus(containment_status),
            attack_start_slot=attack_start_slot,
            first_detection_slot=first_detection_slot,
            first_containment_slot=first_containment_slot,
            gross_attack_loss=EconomicLoss(
                "SOL", "lamports", "reference_vault_lamports", gross_loss_lamports
            ),
            residual_loss=EconomicLoss(
                "SOL",
                "lamports",
                "reference_vault_lamports",
                residual_loss_lamports,
            ),
        )
    )


def _evaluation_to_dict(evaluation: DrillEvaluation) -> dict[str, object]:
    metrics = evaluation.metrics
    if (
        metrics.gross_attack_loss is None
        or metrics.residual_loss is None
        or metrics.capital_saved is None
    ):
        raise ValueError("containment evaluation metrics are incomplete")
    return {
        "verdict": evaluation.verdict.status.value,
        "mttd_slots": metrics.mttd_slots,
        "mttc_slots": metrics.mttc_slots,
        "gross_attack_loss_lamports": metrics.gross_attack_loss.amount,
        "residual_loss_lamports": metrics.residual_loss.amount,
        "capital_saved_lamports": metrics.capital_saved.amount,
    }
