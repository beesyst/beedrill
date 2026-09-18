# SPEC — BeeDrill

## 0. Terms

- Repository: `beedrill`
- Python distribution: `beedrill`
- Python import package: `beedrill`
- Host: runtime responsible for controlled execution, currently BeeAgent
- Shared contract package: BeeSDK
- Module: BeeDrill integration component loaded by the host
- Drill: one reproducible security-control validation run
- Scenario: domain definition of the attack condition and expected controls
- Target: protocol/state being tested in an approved isolated environment
- Attack: deterministic or bounded adversarial action used to exercise controls
- Detector: control expected to identify the attack
- Containment: control expected to stop or limit the attack
- Evidence: structured observation used to evaluate the drill
- MTTD: Mean/Measured Time To Detect for the evaluated drill contract
- MTTC: Mean/Measured Time To Contain for the evaluated drill contract
- Residual loss: economic damage remaining after evaluated controls act
- Verdict: deterministic security-control outcome derived from validated
  evidence
- Authority: permission level assigned and enforced by the host
- Artifact: structured output persisted through a host-owned artifact boundary
- Replay: repeat execution/evaluation intended to preserve equivalent security
  meaning
- Production/mainnet: non-isolated real environment, outside current MVP attack
  execution scope

## 1. Goal

BeeDrill provides continuous security-control validation for Solana protocols.

For `isolated_solana_smoke`, BeeDrill supplies only the fixed
`surfpool_local` intent through the BeeSDK `CapabilityCaller`. BeeAgent owns
the isolated process, local RPC, policy, authority and cleanup. Returned
capability evidence never upgrades BeeDrill's `READ_ONLY` authority.

For `reference_target_baseline`, BeeDrill supplies only the fixed
`surfpool_local` and `reference_vault` intent. The package-owned
`reference_target/reference_vault.json` resource defines the stable logical
target identity, canonical initial state and integer lamport baseline. BeeAgent
resolves that resource, owns the isolated lifecycle and returns bounded
evidence; malformed or incomplete evidence is refused by the module.

For `reference_target_attack`, BeeDrill supplies that same fixed intent through
the BeeSDK `CapabilityCaller`. BeeAgent alone owns the isolated target and
transaction execution. A successful response must provide the exact bounded
economic evidence contract in section 17; BeeDrill emits it as an artifact only
after strict validation and remains `READ_ONLY`.

The product goal is to verify that defenses actually work under reproducible
attack conditions.

BeeDrill is built around this distinction:

```text
audit
→ can the code be broken?

BeeDrill
→ when an attack occurs, do the defenses detect and contain it?
```

Target product flow:

```text
current protocol state
→ isolated Solana environment
→ deterministic attack
→ observe detector
→ observe containment
→ measure timing and economic outcome
→ deterministic PASS / FAIL
```

## 2. Product principles

- Solana-first;
- security controls, not generic vulnerability discovery;
- deterministic security outcomes;
- objective evidence over subjective scoring;
- reproducible scenarios;
- isolated execution;
- host-owned authority;
- fail closed on missing critical evidence;
- KISS;
- real scenarios before frameworks;
- domain behavior in BeeDrill;
- runtime/execution behavior in BeeAgent;
- reusable shared contracts in BeeSDK only when proven necessary.

## 3. Product boundary

BeeDrill is responsible for:

- drill semantics;
- scenario semantics;
- expected detector behavior;
- expected containment behavior;
- evidence validation;
- MTTD/MTTC semantics;
- residual-loss semantics;
- deterministic verdicts;
- scenario regression corpus;
- BeeDrill-specific structured reporting.

BeeDrill is not responsible for generic:

- runtime orchestration;
- subprocess management;
- Surfpool process lifecycle;
- arbitrary RPC execution;
- credentials;
- host policy;
- approvals;
- storage implementation;
- module registry;
- UI framework.

## 4. MVP boundary

The MVP focuses on proving one complete security-control validation loop on
Solana.

The required product behavior is:

```text
prepare reproducible isolated state
execute approved attack
observe real detector
observe or invoke actual containment path
collect evidence
calculate security metrics
produce deterministic verdict
replay after remediation
compare outcome
```

The intended demonstration pattern is:

```text
attack
→ detection succeeds
→ containment fails
→ measurable residual loss

fix control/configuration

same drill
→ detection succeeds
→ containment succeeds
→ materially lower residual loss
```

The exact reference protocol and scenario are delivered by roadmap iterations.

## 5. Explicit MVP exclusions

The current MVP does not require:

- production/mainnet attack execution;
- multi-chain support;
- universal security DSL;
- generic attack marketplace;
- SaaS runner fleet;
- reputation system;
- subjective AI trust scoring;
- large BeeUI application;
- BeeScan dependency;
- generic vulnerability scanner;
- generic AI pentester.

These require separate evidence and roadmap work.

## 6. Architecture contract

Canonical responsibility model:

```text
BeeSDK
→ shared contracts

BeeAgent
→ host runtime
→ policy
→ authority
→ execution

BeeDrill
→ scenario
→ evidence interpretation
→ metrics
→ verdict
```

BeeDrill must not become a second host runtime.

## 7. Dependency rule

Target shared-contract dependency:

```text
beedrill -> beesdk
```

BeeSDK must not depend on BeeDrill.

BeeDrill should not import private BeeAgent internals when an approved
public/shared contract is available.

Cross-repository runtime integration must preserve repository ownership.

## 8. Module identity

BeeDrill module identity:

```text
beedrill
```

Initial authority:

```text
read_only
```

Authority is assigned by the host.

BeeDrill does not grant itself authority.

## 9. Module contract

BeeDrill should conform to the approved shared module contract when the BeeSDK
baseline is available.

Conceptually the module supports:

```text
module_id
authority
supported_case_types()
handle(context)
```

The host provides invocation context.

BeeDrill returns bounded structured results.

The exact Python contract comes from BeeSDK rather than a BeeDrill-local copy.

## 10. Host relationship

BeeAgent is the primary host.

BeeAgent owns:

```text
module runtime
module registry
run/session lifecycle
authority
policy
process execution
Surfpool lifecycle
Solana RPC execution
credentials
timeouts
cleanup
artifact/storage implementation
external execution and egress
```

BeeDrill owns the drill-specific meaning of the evidence returned by those
capabilities.

## 11. Scenario contract

A scenario represents one complete, reproducible security-control validation
case. The BD-3 public domain contract is available from `beedrill` and is
implemented in `beedrill.domain`.

`Scenario` contains these required immutable values:

```text
identity: ScenarioIdentity(scenario_id, version)
target: Target(target_id, protocol, state_ref)
initial_state: InitialState(state_id, description)
attack_steps: tuple[AttackStep(attack_id, attack_type, expected_effect)]
expected_controls: tuple[ExpectedControl(control_id, control_type, expectation)]
observations: tuple[Observation(observation_id, subject_id, subject, status, evidence_id)]
containment: ContainmentResult(control_id, status, evidence_id)
economic_delta: EconomicDelta(asset, unit, before, after)
evidence: EvidenceCompleteness(required, present, missing)
verdict: DrillVerdict(status)
```

`scenario_id`, all contract identifiers and all references are stable lowercase
identifiers. `version` is an explicit positive integer. No model derives an
identifier, version, verdict or evidence state from a clock, UUID, process or
environment value. Attack steps are semantic descriptions only: their bounded
fields do not carry an executable, command, script, code, process arguments,
RPC destination, filesystem path or credentials.

Collections are immutable tuples in the model and are bounded to 32 values.

This is a concrete contract for one Solana-first drill domain, not a generic
scenario language or YAML DSL.

## 12. Scenario safety

A scenario is data and intent.

It is not authority.

Scenario-controlled input must not directly grant:

```text
arbitrary executable
arbitrary shell command
arbitrary RPC endpoint
arbitrary filesystem path
production credentials
host identity
host authority
policy override
```

The host remains responsible for translating approved bounded intent into
execution.

## 13. Target contract

`Target` and `InitialState` describe the logical protocol and its known starting
state. They are not runtime target selection, an RPC endpoint, an authority
grant or an instruction to create state. A future host must resolve any
execution target through its own approved isolated-environment policy.

Production/mainnet mutation remains outside this data contract.

## 14. Attack contract

Each `AttackStep` carries an attack identifier, a bounded attack type and the
expected observable effect. It represents the adversarial condition, not how to
execute it. BeeAgent retains execution mechanism, process/RPC lifecycle,
timeouts, cleanup and authority.

## 15. Detector contract

`ExpectedControl` has one of two types: `detector` or `containment`. A detector
must explicitly expect `observed`; a containment control must explicitly expect
`succeeded`. An `Observation` explicitly records `observed`, `not_observed` or
`missing` for an attack or expected control. Detector integration details are
not part of BD-3.

## 16. Containment contract

`ContainmentResult` references a declared containment control and explicitly
states `succeeded`, `failed` or `missing`; no request or prose is treated as
proof of containment. Containment execution is outside BD-3.

## 17. Evidence contract

`EvidenceCompleteness` explicitly lists required, present and missing evidence
identifiers. Present and missing values must be unique, disjoint and together
partition required values. `EconomicDelta` carries an uppercase asset symbol, a
unit identifier and explicit integer `before` and `after` values. Integer units
are authoritative; floats are rejected. BD-3 does not calculate a delta, MTTD,
MTTC, residual loss or a verdict.

### 17.1 Reference-target attack evidence

The `reference_target_attack` capability has one fixed request:
`{"target_profile": "surfpool_local", "target_id": "reference_vault"}`. Its
successful evidence has exactly these fields and no others:

- `target_id`: `reference_vault`;
- `initial_state_id`: `reference_vault_canonical_v1`;
- `economic_unit`: `lamports`;
- `attack_start_slot`: non-negative integer local-slot reference;
- `attack_transaction_signature`: bounded non-empty transaction identifier;
- `vault_lamports_before`: `1000000`;
- `vault_lamports_after`: `999900`;
- `unsafe_withdraw_count_before`: `0`;
- `unsafe_withdraw_count_after`: `1`;
- `gross_loss_lamports`: `100`.

BeeDrill accepts the evidence only when the integer loss equals `before - after`
and the complete state transition matches this fixed isolated reference target.
It writes one `reference_target_attack.json` artifact containing the bounded
evidence. Refused, timeout, error and invalid host results remain non-successful
module results; this evidence is neither a detector result nor a verdict.

## 18. Evidence validity

Critical invalid data is rejected, including unknown fields, missing required
fields, invalid identifiers/enums/integers, duplicate identifiers and
inconsistent evidence partitioning. A scenario with missing evidence cannot
carry a `pass` verdict.

## 19. Evidence is not authority

Evidence describes what happened.

It must not create permission for another action.

Required distinction:

```text
evidence != authority
result != approval
scenario != runtime identity
```

## 19.1 JSON conversion and verdict values

`scenario_from_dict`, `scenario_from_json`, `scenario_to_dict` and
`scenario_to_json` are the only BD-3 conversion functions. Input objects are
strict: every object rejects unknown fields. This bounded schema therefore also
rejects execution-shaped fields without attempting to interpret ordinary prose.

Canonical JSON uses sorted keys, compact separators and UTF-8-compatible text;
the same valid model always produces byte-identical JSON and conversion adds no
timestamps, random values or environment state.

`tests/fixtures/failed_containment_drill.json` is the sanitized deterministic
baseline: the attack and detector are observed, containment fails, and explicit
USDC integer-unit before/after evidence records damage of 480,000,000 units.
All required evidence is present and the explicitly supplied verdict is `fail`.
It contains no execution instructions, private keys, seed phrases or
credentials.

`DrillVerdict.status` is a required typed value: `pass`, `fail` or
`incomplete`. It is supplied data, not inferred from prose, AI or defaults. A
future BD-9 verdict engine may decide a status from validated evidence, but is
not implemented by this contract.

## 20. MTTD

MTTD measures detection responsiveness for the drill.

Conceptually:

```text
valid detector observation time
-
attack start time
```

The exact reference points and units must be defined by the domain contract that
introduces the metric.

MTTD must be derived deterministically from validated evidence.

## 21. MTTC

MTTC measures containment responsiveness for the drill.

The exact reference point must be explicit in the metric contract.

Possible interpretations such as:

```text
containment time - attack start time
```

or:

```text
containment time - detection time
```

must not be mixed implicitly.

The approved metric contract must define one semantic meaning.

## 22. Residual loss

Residual loss represents measurable economic damage remaining after the tested
controls act.

The calculation must:

- use explicit inputs;
- use deterministic arithmetic;
- define units/assets where required;
- define missing-input behavior;
- avoid subjective AI scoring.

The exact formula belongs to the roadmap iteration introducing the metric.

## 23. Verdict contract

Critical verdicts are deterministic.

Required property:

```text
same validated evidence
→ same metrics
→ same verdict
```

The verdict engine must not depend on:

- LLM confidence;
- free-form prose interpretation;
- undocumented heuristic judgment;
- hidden operator preference.

AI may explain a verdict.

AI does not determine the critical verdict.

## 24. PASS semantics

PASS means the approved scenario's required controls and outcome thresholds were
satisfied by valid evidence.

PASS must not mean merely:

- attack execution completed;
- a detector returned some output;
- containment was requested;
- an AI considered the result acceptable.

The relevant iteration defines the exact required conditions.

## 25. Failure/incomplete semantics

A drill must explicitly represent non-success cases.

Depending on the approved contract, these may include:

```text
FAIL
INCOMPLETE
REFUSED
DEGRADED
ERROR
```

The exact status vocabulary is not fixed by bootstrap documentation.

The invariant is:

> Missing critical proof must not become PASS.

## 26. Replay contract

Replay is used to confirm that a control change improves the outcome under an
equivalent scenario.

A valid replay should preserve:

- equivalent relevant starting state;
- equivalent scenario semantics;
- equivalent attack semantics;
- equivalent metric definitions;
- equivalent verdict rules.

Replay need not preserve irrelevant wall-clock or process identifiers.

It must preserve equivalent security meaning.

## 27. Regression contract

Scenario regression tests should make security behavior reproducible.

The desired relationship is:

```text
scenario fixture
+ evidence fixture
→ expected metrics
→ expected verdict
```

Real runtime drills may supplement fixture tests but do not replace deterministic
domain tests.

## 28. Artifact contract

BeeDrill may produce structured drill artifacts through the host-provided
artifact boundary.

Artifact content may include:

- scenario identity;
- validated evidence;
- metrics;
- verdict;
- bounded diagnostics.

BeeDrill does not define the host filesystem/storage implementation.

Artifacts must not contain production secrets.

## 29. Package/public API

BeeDrill public API should remain minimal.

Public contracts use explicit module imports:

```python
from beedrill.domain import Scenario
from beedrill.domain import DrillVerdict
from beedrill.module import BeeDrillModule
```

`src/beedrill/__init__.py` is byte-empty and is not a re-export layer. Do not
publish speculative domain types before their contracts are introduced by
roadmap work.

## 30. Package guarantees

BeeDrill should remain:

- importable without starting runtime services;
- free from hidden execution at import;
- free from production credential ownership;
- usable independently for domain-level tests;
- compatible with approved BeeSDK shared contracts;
- focused on Solana during the MVP.

## 31. Dependency guarantees

Dependency additions must be explicit and justified.

BeeDrill should not add a dependency merely because the dependency is common in
larger security frameworks.

When BeeSDK becomes an actual package dependency, the declaration must refer to
an approved available source.

Do not invent future package versions.

## 32. AI usage

AI is optional and assistive.

Allowed examples:

- explain evidence;
- draft scenario descriptions;
- summarize results;
- suggest remediation.

Not allowed for critical product truth:

- final detector success decision;
- final containment success decision;
- metric calculation;
- final security PASS/FAIL.

Deterministic evidence and rules remain authoritative.

## 33. UI

The MVP does not require a large dedicated UI.

Product truth must exist independently of presentation.

A future UI may visualize:

```text
scenario
attack
detector
containment
metrics
verdict
evidence
```

but UI is not the source of truth.

## 34. BeeScan relationship

BeeScan and BeeDrill solve different problems.

Conceptually:

```text
BeeScan
→ find/explore security weaknesses

BeeDrill
→ continuously verify that defenses work
```

BeeDrill does not depend on BeeScan for the MVP.

Shared integration may be considered later only if a concrete product need is
proven.

## 35. BeeUI relationship

BeeUI owns generic presentation behavior.

BeeDrill should not create its own large presentation framework.

BeeUI integration should occur only when there is an actual presentation need.

## 36. Security guarantees

The current product contract requires:

```text
production/mainnet mutation
= excluded

scenario-controlled authority
= prohibited

arbitrary scenario-controlled execution
= prohibited

critical false PASS from missing evidence
= prohibited

critical LLM-controlled verdict
= prohibited
```

These are architecture/security invariants, not optional implementation details.

## 37. Versioning

BeeDrill uses SemVer.

Version source of truth:

```text
pyproject.toml
```

BeeDrill versions are independent of:

- BeeAgent;
- BeeSDK;
- BeeUI;
- BeeScan;
- BeeROP.

Ordinary feature/fix work does not manually bump package version.

Release automation owns release version lifecycle.

## 38. Maturity rule

BeeDrill is developing correctly when:

- real scenarios can be reproduced;
- actual controls are observed;
- control failures produce explicit failures;
- remediation can be replayed;
- metrics are objective;
- verdicts are deterministic;
- execution remains host-controlled;
- domain behavior remains understandable without a large framework.

BeeDrill is developing incorrectly when:

- it becomes a generic pentest framework;
- it becomes a second BeeAgent runtime;
- scenario input gains arbitrary execution;
- verdicts become subjective AI scores;
- multi-chain abstraction appears before the Solana product works;
- UI complexity arrives before end-to-end drill evidence;
- framework code grows faster than real scenarios.

## 39. Current bootstrap boundary

Initial repository bootstrap should remain limited to:

```text
package foundation
module foundation
repository governance
documentation
tests required for bootstrap
```

Domain contracts, Surfpool execution, attack scenarios, metrics and additional
integrations are added by their corresponding roadmap iterations.

Do not implement later iterations during bootstrap merely because their eventual
shape is described in this specification.

## Summary

BeeDrill answers one product question:

> Under a reproducible Solana attack, did the real security controls detect the
> attack, contain it, and limit economic damage?

The implementation should remain centered on:

```text
reproducible scenario
+ bounded execution
+ objective evidence
+ deterministic metrics
+ deterministic verdict
```

Everything else should remain outside the product until proven necessary.
