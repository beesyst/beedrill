# ROADMAP — BeeDrill

## Purpose

This document defines the development path for `beedrill` through explicit product stages and substantial implementation iterations.

BeeDrill uses the ROADMAP as a lightweight SDLC artifact to:

- define the product direction;
- keep the hackathon scope bounded;
- define the acceptance boundary of each meaningful iteration;
- connect Issue → Code → Tests → Evidence → PR → Merge;
- keep BeeDrill separate from BeeAgent runtime responsibilities;
- prevent speculative framework development;
- preserve deterministic security verdicts;
- ensure security-sensitive execution remains controlled and reviewable;
- reserve enough time before the Colosseum deadline for hardening, external validation, demo work and submission.

The ROADMAP does not replace Issues or Pull Requests:

- **Issue** defines the exact approved implementation task;
- **PR** records what was actually implemented and verified;
- **ROADMAP** defines the iteration-level product contract and delivery direction.

A significant roadmap iteration is normally delivered through a PR.

Small low-risk maintenance that does not change runtime behavior, security boundaries, public contracts, dependencies or product semantics follows the shorter path defined in `docs/SDLC.md` and does not become a roadmap iteration merely to create another numbered item.

The ROADMAP does not duplicate full project rules:

- product behavior and public product contract belong in `docs/SPEC.md`;
- component ownership and dependency direction belong in `docs/ARCHITECTURE.md`;
- development workflow and change levels belong in `docs/SDLC.md`;
- execution, authority and trust boundaries belong in `docs/SECURITY.md`;
- local development and integration instructions belong in `docs/DEV_GUIDE.md`;
- repository-level AI/development instructions belong in `AGENTS.md`.

## Vision

| Block                          | Statement                                                                                                                                                                 |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Product identity**           | BeeDrill is continuous security-control validation for Solana protocols, implemented as a BeeAgent domain/security module rather than a standalone orchestration runtime. |
| **Primary objective**          | Prove whether technical defenses actually detect and contain reproducible attacks before teams depend on those defenses during a real incident.                           |
| **Core question**              | If this attack starts now, do the configured detector, breaker and containment controls actually protect capital?                                                         |
| **Security-control principle** | Existence of a control is not proof that the control works. BeeDrill validates behavior through execution evidence.                                                       |
| **Regression principle**       | A security defense should be testable repeatedly after relevant changes in the same way application behavior is regression-tested.                                        |
| **Ground-truth principle**     | Critical outcomes are derived from observable execution evidence, not subjective AI confidence scores.                                                                    |
| **Determinism principle**      | The same valid evidence must produce the same security metrics and verdict.                                                                                               |
| **AI principle**               | AI may explain results, assist scenario authoring or propose remediation, but it must not determine critical PASS/FAIL verdicts.                                          |
| **Solana principle**           | Solana is part of the actual execution and economic state being tested; blockchain integration is not decorative.                                                         |
| **Host principle**             | BeeAgent owns orchestration, execution, process lifecycle, runtime identity, policy, credentials, RPC access and artifact lifecycle.                                      |
| **Module principle**           | BeeDrill owns scenarios, domain semantics, expected controls, evidence validation, security metrics and deterministic verdicts.                                           |
| **SDK principle**              | BeeSDK provides shared contracts only and must not absorb BeeDrill runtime or Solana implementation.                                                                      |
| **Execution principle**        | Scenario input must never grant arbitrary process, filesystem, RPC or production execution authority.                                                                     |
| **Isolation principle**        | Hackathon attack execution is restricted to explicitly approved isolated environments.                                                                                    |
| **Mainnet principle**          | Production/mainnet mutation is outside the hackathon MVP.                                                                                                                 |
| **Evidence principle**         | Evidence may justify a verdict; evidence never grants execution authority.                                                                                                |
| **KISS principle**             | Implement only the minimum architecture needed to prove the end-to-end product thesis.                                                                                    |
| **Product principle**          | BeeDrill is not primarily a vulnerability scanner, generic pentester, incident-response chatbot or blockchain simulator.                                                  |

## Product thesis

BeeDrill does not primarily answer:

> Can this program contain a vulnerability?

Audits, fuzzers and vulnerability scanners already address that problem.

BeeDrill answers:

> If an attack starts despite existing preventive controls, will the technical defense stack actually detect and contain it before unacceptable economic loss occurs?

Target flow:

```text
current protocol state
→ isolated Solana environment
→ deterministic attack scenario
→ attack execution
→ detection observation
→ containment observation
→ economic outcome measurement
→ deterministic metrics
→ deterministic PASS / FAIL
→ exact replay after remediation
```

Core product principle:

> Audits test whether code can be broken.
> BeeDrill tests whether defenses actually stop the damage.

The hackathon MVP focuses on the technical control plane:

```text
attack
→ detector
→ automated signal
→ circuit breaker / pause path
→ resulting chain state
→ economic outcome
```

Human-heavy operational workflows such as:

```text
PagerDuty
→ human wakes up
→ opens multisig
→ hardware wallets
→ 3-of-5 coordination
```

are outside the automated MVP unless they expose a deterministic machine-verifiable interface.

## Architecture boundary

The intended ownership model is:

```text
BeeSDK
→ shared public contracts only

BeeAgent
→ runtime
→ orchestration
→ module registry
→ execution
→ Surfpool lifecycle
→ Solana RPC access
→ subprocess/process lifecycle
→ policy
→ authority
→ credentials
→ timeouts
→ artifact lifecycle

BeeDrill
→ scenario semantics
→ target semantics
→ attack expectations
→ expected controls
→ evidence validation
→ security metrics
→ deterministic verdicts
→ scenario corpus
→ drill reporting
```

Architecture invariants:

```text
BeeDrill
!=
second BeeAgent runtime
```

```text
domain intent
!=
execution authority
```

BeeDrill may request or describe bounded execution intent through approved host boundaries.

BeeDrill must not independently create an uncontrolled execution path around BeeAgent.

## Cross-repository ownership rule

BeeDrill development may expose integration gaps in BeeAgent or BeeSDK.

Those gaps must be implemented in the repository that owns the affected responsibility.

Correct flow:

```text
BeeDrill integration evidence
→ identify host/shared-contract gap
→ necessity decision
→ separate owning-repository Issue
→ implementation in owning repository
→ verification
→ BeeDrill integration continues
```

Examples:

```text
Surfpool process lifecycle
→ BeeAgent

bounded execution authority
→ BeeAgent

host capability injection
→ BeeAgent

shared stable module/capability contract
→ BeeSDK, but only if proven insufficient

scenario semantics
→ BeeDrill
```

BeeDrill roadmap iterations may require cross-repository implementation and integration evidence, but BeeDrill must not copy BeeAgent runtime implementation into this repository.

## Security invariants

The following rules apply to the complete hackathon roadmap.

### Isolation

Attack execution must be restricted to explicitly approved local or isolated environments.

Production/mainnet mutation is outside scope.

### Authority

A scenario cannot self-assign:

```text
execution authority
runtime identity
credentials
RPC destination
filesystem scope
host policy
```

### Deterministic verdicts

Critical PASS/FAIL behavior must be deterministic and based on bounded validated evidence.

### No hidden AI authority

LLM output may not:

- authorize execution;
- choose production targets;
- grant credentials;
- override evidence;
- silently convert an incomplete run into PASS;
- determine the final critical security verdict.

### Evidence integrity

Missing, malformed, inconsistent or insufficient critical evidence must produce an explicit incomplete/refused/error/fail-closed outcome rather than an invented success.

### Economic measurement

Economic outcomes must be calculated from explicit state/evidence with documented units and assumptions.

### Secrets

Production credentials, private keys and unrelated secrets must not appear in:

- scenario fixtures;
- repository content;
- logs;
- test artifacts;
- demo artifacts.

## Development principles

BeeDrill uses small but substantial product-sized iterations.

Every significant roadmap iteration must:

- have a concrete product or integration goal;
- produce a meaningful code or artifact-level increment;
- remain inside its declared scope;
- avoid speculative abstractions;
- preserve project ownership boundaries;
- preserve deterministic verdict semantics;
- explicitly classify trust-boundary changes;
- prefer fixture-driven and replayable validation;
- add tests proportional to actual risk;
- keep artifacts bounded and understandable;
- keep execution fail-closed;
- keep AI outside critical security authority;
- avoid broad compatibility work before the first product thesis is proven.

For BeeDrill:

```text
simulation
!=
proof
```

A mocked attack event is not sufficient evidence for a real attack scenario.

```text
control configured
!=
control validated
```

```text
evidence
!=
authority
```

## Iteration significance rule

A numbered iteration must produce at least one substantial increment of the following kinds:

- a new stable domain/public contract required by the product;
- a new bounded runtime capability or real integration;
- a new reproducible Solana target or attack path;
- a new machine-verifiable detector/containment path;
- a new deterministic metric/verdict capability;
- a new materially distinct replayable security scenario;
- a new CI/regression execution surface;
- a material security-boundary hardening increment;
- a real external validation artifact;
- a judge-ready reproducibility/evidence package.

The following do **not** justify a standalone roadmap iteration by themselves:

- wording changes;
- formatting;
- README cleanup;
- one small helper;
- one extra test with no contract/risk increment;
- speculative abstraction;
- a new wrapper around existing behavior;
- a second synthetic scenario that does not prove a materially new product property.

If two planned iterations produce one inseparable product capability, they should be merged.

## KISS roadmap rule

BeeDrill has a short hackathon implementation window.

Do not add roadmap iterations simply because the following may eventually be useful:

```text
dashboard
SaaS scheduler
multi-chain support
generic plugin system
generic pentest framework
marketplace
reputation
agent wallet
x402
BeeScan integration
production autonomous response
remote runner fleet
custom blockchain simulator
general-purpose scenario DSL
```

A new scope item is justified only when at least one condition holds:

1. it is necessary to prove the central BeeDrill product thesis;
2. a current iteration cannot be completed correctly without it;
3. real integration evidence exposes a concrete gap;
4. an external design partner requires it for validation;
5. it materially increases submission credibility without threatening the delivery window.

Insufficient reasons include:

```text
"might be useful later"
"makes the architecture cleaner"
"other platforms have it"
"we should make it generic now"
"we may support another chain later"
```

## SDLC workflow for roadmap items

A significant BeeDrill iteration follows this flow:

1. **Planning**
   - confirm the real problem;
   - confirm iteration necessity;
   - inspect the closest existing implementation;
   - confirm implementation ownership;
   - reject redundant or speculative scope.

2. **Requirements**
   - define Goal;
   - define Scope;
   - define Excluded;
   - define Deliverable;
   - define Acceptance criteria;
   - define contract/config impact;
   - define dependency impact;
   - define security impact;
   - define Checks;
   - define DoD.

3. **Issue**
   - create one focused Issue in the repository that owns the implementation.

4. **Implementation**
   - implement the smallest complete solution on a dedicated branch.

5. **Verification**
   - execute applicable targeted tests;
   - full tests;
   - package build;
   - integration smoke;
   - artifact checks;
   - deterministic replay;
   - negative boundary tests;
   - quality/security checks.

6. **Review / PR**
   - record actual implementation and verification evidence.

7. **Merge**
   - merge only after iteration acceptance criteria are satisfied.

8. **Regression**
   - preserve completed scenario behavior through tests and replay fixtures.

9. **Release**
   - release only when a useful package/product milestone is reached.

Tiny low-risk documentation or test maintenance may use the shorter path defined in `docs/SDLC.md`.

## Status values

Allowed roadmap iteration statuses:

- **PLANNED** — scope is approved, implementation has not started;
- **IN PROGRESS** — active implementation or bootstrap work is underway;
- **DONE** — iteration contract is fully delivered;
- **DONE (partial)** — iteration was intentionally closed with explicit documented limitations.

For post-hackathon directions:

- **FUTURE / orientation** — known direction, not approved implementation scope.

`FUTURE / orientation` does not pre-authorize architecture or implementation.

## Roadmap item format

Iterations use:

- `Goal`
- `Scope`
- `Excluded`
- `Deliverable`
- `Acceptance criteria`
- `Checks`
- `DoD`

The ROADMAP defines iteration-level contracts.

Detailed implementation steps, exact files, complete payload schemas, exhaustive test matrices, command evidence and review findings belong in:

```text
Issue
implementation handoff
tests
PR
```

## Global Definition of Done

A significant BeeDrill iteration is complete only when:

- declared scope is implemented;
- excluded scope was not silently introduced;
- ownership boundaries remain correct;
- critical verdict logic remains deterministic;
- AI does not receive execution or verdict authority;
- runtime execution remains host-controlled;
- isolated-environment restrictions remain intact;
- no production/mainnet mutation path was accidentally created;
- input/evidence validation is explicit;
- failure states are visible and fail closed where security requires;
- targeted tests pass;
- full BeeDrill tests pass when applicable;
- package build passes when public/package surface changes;
- integration smoke passes when integration behavior changes;
- relevant replay scenarios remain reproducible;
- logs/artifacts are understandable and bounded;
- no secrets leak into source, logs or artifacts;
- required security checks from `docs/SDLC.md` and `docs/SECURITY.md` are complete;
- docs are updated when architecture, contract, behavior or security boundary changes;
- significant delivery is recorded in PR;
- no unrelated architecture or cleanup is mixed into the iteration.

## Change levels for verification

BeeDrill uses three change levels.

### low-risk

Changes without meaningful runtime/security behavior impact.

Examples:

- documentation;
- formatting;
- test-only cleanup;
- wording;
- internal refactor with no behavior or contract change.

Usually required:

- relevant targeted checks;
- full tests when Python/test infrastructure is affected.

### runtime-risk

Changes affecting normal product behavior without changing a critical execution/trust boundary.

Examples:

- scenario models;
- evidence models;
- deterministic metric calculation;
- verdict logic;
- package/public API;
- scenario selection;
- artifact structure;
- CI command behavior.

Usually required:

- targeted tests;
- `uv run pytest -q`;
- package build when public/package surface changes;
- relevant smoke;
- deterministic replay;
- artifact verification where applicable.

### security-sensitive

Changes affecting trust, authority, execution or hostile-input boundaries.

Examples:

- subprocess/process lifecycle;
- Surfpool execution;
- Solana RPC execution;
- target allowlisting;
- filesystem paths;
- external detector integration;
- containment execution;
- private-key handling;
- network egress;
- untrusted scenario parsing;
- credentials;
- authority semantics;
- dependency additions affecting execution surface.

Usually required:

- applicable runtime-risk checks;
- SAST;
- SCA when dependencies change;
- negative/adversarial boundary tests;
- explicit trust-boundary review;
- timeout/cleanup verification where relevant;
- secret leakage verification.

DAST, IAST and fuzzing are used only when the actual change creates a meaningful corresponding surface.

## Versioning and release rule

BeeDrill uses SemVer.

Version source of truth:

```text
pyproject.toml
```

Roadmap iteration and release version are different concepts.

The ROADMAP does not predeclare a fixed package version for the final hackathon MVP.

Reasons:

- release automation may advance versions before the MVP is complete;
- iteration count is not package version;
- product readiness must be determined from behavior and evidence, not from a historical version number.

Ordinary implementation work must not manually bump the project version unless the task is explicitly release-related.

The first judge-ready BeeDrill MVP milestone requires:

```text
module integration
+
validated domain contracts
+
isolated real attack execution
+
real detection observation
+
real containment validation
+
deterministic metrics and verdict
+
repeatable security regression suite
+
external/non-toy validation evidence
+
judge-ready reproducibility package
```

Conventional Commits should be used.

Recommended release impact:

| Commit          | Release impact                         |
| --------------- | -------------------------------------- |
| `feat:`         | MINOR                                  |
| `fix:`          | PATCH                                  |
| `docs:`         | normally no release bump               |
| `test:`         | normally no release bump               |
| `refactor:`     | normally no release bump               |
| `chore:`        | normally no release bump               |
| `ci:`           | normally no release bump               |
| `build:`        | normally no release bump               |
| breaking change | MAJOR when SemVer maturity requires it |

Release mechanics must not become a blocker for the product MVP.

## Delivery window

Hackathon dates used for planning:

```text
Start:    2026-09-14
Deadline: 2026-10-12
```

Core implementation window:

```text
2026-09-15 → 2026-10-04
20 calendar build days
14 substantial iterations
```

Reserved buffer:

```text
2026-10-05 → 2026-10-12
8 calendar days
```

The buffer is intentionally not allocated to planned product features.

Allowed buffer work:

- bug fixes;
- reliability;
- integration correction;
- test strengthening;
- performance;
- design-partner feedback;
- documentation;
- demo recording;
- submission assets;
- submission fixes.

New architecture or broad product scope during the buffer requires an explicit GO/NO-GO decision.

## Product phases

| Phase                                                       | Status  | What it means                                                                                                                                           |
| ----------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Phase A — Repository, module and domain foundation**      | DONE    | BeeDrill exists as an independent package, consumes BeeSDK module contracts, runs under BeeAgent and has deterministic local domain contracts/fixtures. |
| **Phase B — End-to-end falsification prototype**            | PLANNED | Prove that a real isolated Solana attack can produce real detection/containment evidence, deterministic metrics and a reproducible FAIL → PASS result.  |
| **Phase C — Security regression product**                   | PLANNED | Prove the architecture generalizes to a second attack class and expose a repeatable CI/regression entry point.                                          |
| **Phase D — Hardening, external validation and submission** | PLANNED | Harden the execution boundary, validate against something non-toy and freeze the judge-ready MVP.                                                       |
| **Submission buffer**                                       | PLANNED | Stabilization, testing, feedback, demo and submission only; no planned major scope.                                                                     |

### Stages

- **Stage 1 — Repository, module and domain foundation:** package, governance, BeeSDK contract use, BeeAgent compatibility and deterministic BeeDrill-local domain contracts.
- **Stage 2 — End-to-end falsification prototype:** isolated Solana runtime, reference target, real attack, detector, metrics/verdict and real containment replay.
- **Stage 3 — Security regression product:** second attack class and CI-style repeatable execution.
- **Stage 4 — Hardening and external validation:** adversarial hardening, non-toy evidence and submission freeze.

## Product gates

These are decision gates, not extra iterations.

### Gate 1 — Host execution viability

After Iteration 4:

```text
BeeDrill intent
→ BeeAgent-owned bounded capability
→ isolated Solana environment
→ bounded evidence
```

must be real.

If this cannot be achieved without BeeDrill gaining arbitrary process/RPC authority, stop feature expansion and fix the host boundary first.

### Gate 2 — Product thesis

After Iteration 9:

```text
same attack
→ same relevant initial state
→ real detection
→ containment FAIL before fix
→ containment PASS after fix
→ objectively better economic outcome
→ deterministic verdict
```

must be reproducible.

If this is not real, do not spend time on extra scenarios, CI polish or UI.

### Gate 3 — Non-toy relevance

After Iteration 13, BeeDrill must have at least one external/non-toy validation artifact.

If this is not available, the submission must explicitly state that the current evidence remains synthetic/reference-target based.

---

## Stage 1 — Repository, module and domain foundation

### Purpose of stage

Stage 1 establishes BeeDrill as a small standalone product module before security-sensitive Solana execution is introduced.

The stage proves:

```text
BeeDrill
→ independent package
→ BeeSDK contract consumer
→ BeeAgent-compatible module
→ deterministic BeeDrill-local domain model
```

without creating:

```text
second runtime
custom execution framework
Solana execution inside the module
```

### Iteration 1 — Repository architecture and governance

**Status:** DONE

#### Goal

Bootstrap BeeDrill as an independent BeeAgent cybersecurity module with explicit repository, architecture, security, development and ownership boundaries.

#### Scope

Included:

- standalone `beedrill` repository;
- Python distribution/import package `beedrill`;
- Python `>=3.14`;
- `uv`;
- standard `src` layout;
- minimal `BeeDrillModule`;
- stable `module_id = "beedrill"`;
- initial `read_only` authority;
- core repository documentation;
- `AGENTS.md`;
- BeeDrill-local prompts and skills;
- GitHub Issue/PR templates;
- release/package metadata baseline;
- package/import/module bootstrap tests;
- repository hygiene baseline.

#### Excluded

- BeeSDK dependency integration;
- BeeAgent runtime integration;
- domain contracts;
- Surfpool;
- Solana RPC/transactions;
- attacks;
- detectors;
- containment;
- BeeUI/BeeScan;
- production credentials;
- mainnet mutation.

#### Deliverable

A standalone BeeDrill package/repository ready for shared-contract integration and feature development.

#### Acceptance criteria

- independent Git repository;
- package/import identity `beedrill`;
- Python `>=3.14`;
- `uv` project;
- standard `src` layout;
- no copied BeeAgent/BeeSDK platform contracts;
- stable `module_id = "beedrill"`;
- initial authority `read_only`;
- import has no hidden runtime side effects;
- no external execution surface;
- architecture ownership is explicit;
- docs/workflow/templates are present and internally consistent;
- bootstrap tests pass;
- no production secrets/private keys.

#### Checks

```text
uv sync
uv run pytest -q
uv build
package import smoke
git diff --check
architecture/security review
SAST
SCA
```

#### DoD

BeeDrill exists as an independent governed package with correct architecture ownership and no execution authority.

### Iteration 2 — BeeSDK module contract and BeeAgent load smoke

**Status:** DONE

#### Goal

Prove that BeeDrill consumes the approved BeeSDK module contracts and can be loaded/invoked by current BeeAgent without duplicated platform contracts or broad BeeAgent migration.

#### Scope

- explicit BeeSDK dependency;
- imports from public BeeSDK contract modules;
- `BeeDrillModule` satisfies `ModuleContract`;
- stable `module_id = "beedrill"`;
- `AuthorityLevel.READ_ONLY`;
- one bounded integration case;
- bounded `ModuleResult`;
- BeeAgent registry load;
- BeeAgent runtime invocation;
- authority normalization;
- host `ArtifactAPI` / BeeSDK `ArtifactPort` compatibility;
- one host-owned artifact write.

#### Excluded

- broad BeeAgent migration;
- beeagent-rop migration;
- speculative BeeSDK redesign;
- production module registration;
- BeeDrill domain models;
- Solana/Surfpool/attack/detector/containment execution;
- BeeUI/BeeScan.

#### Deliverable

BeeDrill is a real BeeSDK contract consumer that current BeeAgent can discover and invoke through the normal host boundary.

#### Acceptance criteria

- BeeSDK dependency is explicit and resolvable;
- BeeDrill imports only approved public BeeSDK contracts;
- module satisfies `ModuleContract`;
- authority remains `READ_ONLY`;
- supported case types are bounded;
- BeeAgent registry loads BeeDrill;
- BeeAgent runtime invokes it;
- BeeSDK authority/result normalize correctly;
- host artifact port works;
- unsupported cases are refused;
- no private BeeAgent imports;
- no new execution/egress capability.

#### Checks

```text
targeted module/contract tests
uv run pytest -q
uv build
package import smoke
BeeAgent registry/runtime smoke
authority normalization check
artifact boundary smoke
git diff --check
SAST boundary review
SCA for dependency change
```

#### DoD

BeeDrill runs under BeeAgent through the shared module contract without ownership violations or new execution authority.

### Iteration 3 — Drill domain contracts and fixture baseline

**Status:** DONE

#### Goal

Define the smallest deterministic BeeDrill-local domain model needed to represent one complete security-control validation drill.

#### Scope

Bounded contracts for:

- target;
- scenario;
- scenario identity/version;
- initial state;
- attack step;
- expected control;
- observation;
- containment result;
- economic delta;
- evidence completeness;
- drill verdict;
- strict deterministic serialization;
- sanitized deterministic fixtures.

#### Excluded

- generic scenario language;
- plugin system;
- YAML DSL;
- arbitrary executable scenario payloads;
- AI-generated verdicts;
- Solana execution;
- production protocol schema;
- moving BeeDrill domain models into BeeSDK.

#### Deliverable

A fixture-driven domain baseline capable of expressing one complete drill without invoking Solana.

#### Acceptance criteria

- one complete drill is representable;
- required fields are explicit;
- invalid critical fields are refused;
- serialization is deterministic;
- scenario identity is stable;
- evidence completeness is explicit;
- PASS/FAIL is typed and not inferred from prose;
- scenario data carries no arbitrary executable/code authority;
- fixtures contain no secrets/private keys;
- models remain BeeDrill-local.

#### Checks

```text
schema/model tests
malformed-input tests
deterministic serialization tests
fixture tests
negative executable-input tests
full tests
package build when applicable
```

#### DoD

One complete security-control drill can be described as validated deterministic domain data before runtime execution exists.

---

## Stage 2 — End-to-end falsification prototype

### Purpose of stage

Stage 2 is the central product falsification stage.

It must prove:

```text
real isolated state
→ real attack execution
→ real detector evidence
→ deterministic metrics
→ real containment behavior
→ measurable economic outcome
→ FAIL
→ fix
→ exact replay
→ PASS
```

If this stage requires fake alerts, fake attacks or manually invented verdict evidence, the product thesis is not proven.

### Iteration 4 — BeeAgent-owned isolated Solana execution capability

**Status:** DONE

#### Goal

Establish the smallest real host-controlled capability that lets BeeDrill request a bounded isolated Solana lifecycle without gaining arbitrary process or RPC authority.

#### Scope

Product increment:

```text
BeeDrill bounded intent
→ approved shared/module boundary
→ BeeAgent-owned capability
→ Surfpool / isolated Solana lifecycle
→ bounded result/evidence
```

Required behavior:

- explicit local/sandbox target;
- startup;
- readiness check;
- bounded RPC smoke;
- timeout;
- shutdown;
- cleanup;
- failure evidence;
- capability/result returned through an approved boundary.

Ownership:

```text
BeeAgent
→ process lifecycle
→ Surfpool lifecycle
→ RPC
→ target policy
→ timeout/cleanup
→ execution authority

BeeDrill
→ bounded intent
→ interpretation of returned evidence
```

If current BeeAgent does not inject or implement the necessary bounded capability boundary, create a separate BeeAgent Issue/branch/PR for the minimal host change.

Use existing BeeSDK `CapabilityCaller`/`CapabilityResult` contracts if sufficient. Change BeeSDK only if real integration proves those contracts insufficient.

#### Excluded

- arbitrary subprocess from BeeDrill;
- arbitrary executable/path supplied by scenario input;
- arbitrary RPC destinations;
- mainnet transaction submission;
- production private keys;
- generic process framework;
- broad BeeAgent capability redesign.

#### Deliverable

One production-quality bounded host capability path for:

```text
start
→ ready
→ bounded RPC
→ stop
→ clean
```

plus BeeDrill integration evidence.

#### Acceptance criteria

- isolated environment starts reproducibly;
- readiness is machine-verifiable;
- bounded RPC smoke succeeds;
- timeout is bounded;
- cleanup is reliable;
- startup/readiness failure produces explicit evidence;
- forbidden target is refused;
- module cannot select arbitrary executable/process args;
- no production key is required;
- no mainnet mutation path exists;
- host/module ownership is explicit;
- no orphan process remains after tested success/failure paths.

#### Checks

```text
successful startup
startup failure
readiness failure
timeout
cleanup
forbidden target refusal
untrusted input refusal
no orphan-process check
BeeDrill/BeeAgent integration smoke
security review
SAST
SCA only if dependencies change
```

#### DoD

BeeDrill can reach a real isolated Solana environment only through a bounded BeeAgent-owned capability.

## Iteration 5 — Reference vulnerable protocol and reproducible state

**Status:** DONE

### Goal

Create one deliberately vulnerable Solana reference target whose economic state and defensive-control state can be reproduced through the approved BeeAgent-owned isolated execution boundary.

### Scope

Included:

- one minimal BeeDrill-owned reference vault/protocol;
- one stable logical target identity and canonical initial-state identity;
- deterministic integer economic state and balances;
- one intentionally reachable unsafe economic condition for the later attack iteration;
- one machine-observable detector-relevant signal source;
- one pause/breaker control path;
- one containment configuration that can be deliberately valid or broken without changing the vulnerability;
- source-owned reproducible target assets;
- a bounded BeeDrill module intent for reference-target baseline validation;
- bounded machine-readable baseline evidence;
- host-owned preparation, state observation and reset through a dedicated BeeAgent capability;
- repeatable fresh-state validation.

### Excluded

- the Iteration 6 attack trace and gross-loss evidence;
- detector success/failure evaluation;
- containment verdicts or FAIL → PASS replay;
- deterministic final drill verdict computation;
- production protocol integration;
- production/mainnet mutation;
- caller-selected executables, commands, program paths or RPC targets;
- large lending/DEX implementation;
- realistic frontend;
- generic protocol SDK;
- generic Solana execution framework;
- vulnerability discovery engine.

### Deliverable

A minimal real Solana reference target that BeeAgent can prepare in the approved isolated environment and BeeDrill can validate as the same known economic/control baseline across repeated runs.

### Acceptance criteria

- target source and build inputs are reproducible and owned by BeeDrill;
- canonical logical initial state is explicit;
- two fresh preparations produce equivalent security-relevant starting state;
- normal target operation succeeds;
- the intentionally unsafe path is demonstrably reachable at target level;
- economic state is measurable using deterministic integer units;
- a detector-relevant machine signal exists;
- a pause/breaker path exists;
- containment configuration can be deliberately broken without changing the vulnerability;
- reset or fresh preparation restores the canonical state;
- BeeDrill reaches target execution only through the BeeAgent-owned bounded capability;
- BeeDrill module authority remains `READ_ONLY`;
- scenario/module input cannot select arbitrary execution or RPC;
- no production credential, private data or mainnet fallback is used.

### Checks

```text
reference-target build/test
canonical baseline validation
normal operation
unsafe-path target-level probe
control availability
broken-control configuration
fresh-state reset
repeatability
BeeDrill unit/contract tests
full BeeDrill tests
package build when package resources change
BeeAgent cross-repository integration smoke
malformed/forbidden intent tests
artifact inspection
secret-leak review
SAST
SCA only if dependency surface changes
git diff --check
```

### DoD

BeeDrill has one real, intentionally vulnerable and reproducible Solana target that starts every later drill from the same measurable economic/control state without giving BeeDrill direct process, RPC or production execution authority.

### Iteration 6 — First real economic attack and attack evidence

**Status:** DONE

#### Goal

Выполнить первую детерминированную экономическую атаку на `reference_vault` через approved BeeAgent-owned isolated execution boundary и получить bounded machine-verifiable attack/economic evidence.

#### Scope

First attack class:

```text
vault drain / abnormal outflow
```

Included:

- один фиксированный BeeDrill-owned attack intent для `reference_vault`;
- dedicated bounded BeeAgent capability для подготовки target, выполнения фиксированной атаки и наблюдения результата в `surfpool_local`;
- host-owned Surfpool lifecycle, Solana RPC, process execution, target resolution, timeout and cleanup;
- attack start marker;
- safe submitted transaction identifier(s);
- slots/timing reference;
- target state and balances before/after attack;
- relevant state transitions;
- completion evidence;
- integer gross economic loss;
- bounded BeeDrill validation and artifact/report of returned attack evidence;
- repeatable fresh-state execution from the canonical Iteration 5 baseline.

Ownership:

```text
BeeAgent
→ execution authority
→ process / Surfpool lifecycle
→ RPC target selection
→ target preparation
→ transaction submission
→ timeout / cleanup
→ bounded host evidence

BeeDrill
→ fixed attack intent
→ attack/economic evidence validation
→ domain artifact/report semantics
```

#### Excluded

- detector verdict or MTTD calculation;
- containment verdict, MTTC calculation, or FAIL → PASS replay;
- final deterministic verdict computation;
- AI analysis;
- additional attack classes;
- arbitrary transaction submission, executable, argv, program path, RPC endpoint/method, raw transaction, or credentials from BeeDrill input;
- generic Solana provider, execution framework, or scenario DSL;
- production/mainnet mutation or production private keys;
- BeeSDK contract changes unless a real integration gap is proven.

#### Deliverable

A reproducible real isolated attack trace with objectively measurable economic loss, bounded transaction/state evidence, and an explicit host/module authority boundary.

#### Acceptance criteria

- attack changes real isolated Solana target state from the canonical Iteration 5 baseline;
- attack succeeds against the intentionally vulnerable baseline;
- gross loss is measurable in explicit integer units;
- transaction and state evidence is captured with bounded identifiers;
- repeated fresh execution produces equivalent security-relevant economic outcome;
- BeeDrill reaches execution only through the dedicated BeeAgent-owned bounded capability;
- BeeDrill module authority remains `READ_ONLY`;
- module/scenario input cannot select arbitrary execution, RPC destination, target, path, transaction, or credential;
- invalid or incomplete host evidence is explicit and cannot be reported as successful attack evidence;
- no fake attack event is injected;
- execution remains isolated from production/mainnet;
- timeout, failure, cleanup, and no-orphan-process outcomes are explicit.

#### Checks

```text
attack success
economic delta
transaction/state evidence
repeatability
fresh-state reset and replay
bounded serialization and malformed-evidence refusal
approved module/case/capability/payload scope
forbidden execution-shaped input refusal
target preparation / transaction / observation failure
timeout and cleanup
no orphan process
BeeDrill/BeeAgent real isolated integration smoke
artifact and log inspection
SAST
SCA only if dependency surface changes
```

#### DoD

BeeDrill has a real isolated attack path, not a mocked security event, with host-owned execution authority and bounded evidence sufficient for the later detection, metrics, and containment iterations.

### Iteration 7 — Independent detection observation

**Status:** DONE

#### Goal

Integrate one real independent technical reference monitor for the existing `reference_vault` attack and capture bounded machine-verifiable detection evidence suitable for later deterministic MTTD calculation.

#### Scope

Included:

- one fixed BeeDrill detection intent for `reference_vault`;
- one dedicated BeeAgent-owned bounded detection capability;
- reuse of the canonical reference target and fixed attack from Iterations 5–6;
- an independent host-owned reference monitor observing `vault_outflow_signal`;
- attack-start slot reference;
- first valid detection slot reference when detection occurs;
- explicit detector identity and signal identity;
- bounded detection status distinguishing `observed` from `not_observed`;
- explicit host timeout/error outcomes distinct from a completed observation with no detection;
- strict BeeDrill validation of returned detection evidence;
- bounded detection artifact/report semantics;
- repeatable fresh-state observation through the existing isolated execution boundary.

#### Excluded

- MTTD calculation or final metric evaluation;
- containment execution, MTTC or FAIL → PASS replay;
- final deterministic drill verdict;
- subjective AI detection decisions;
- human/SOC/PagerDuty workflow;
- broad SIEM or generic detector framework;
- module-controlled RPC endpoints, executable, argv, transaction or credentials;
- production/mainnet observation or mutation;
- changes to the existing Iteration 6 attack-evidence contract;
- BeeSDK changes unless a real shared-contract gap is proven.

#### Deliverable

A real independent detector trace for the fixed reference attack, with comparable attack-start and detection timing evidence and explicit distinction between no detection and detector/runtime failure.

#### Acceptance criteria

- the reference monitor observes the real isolated target independently of the attack success assertion;
- the real fixed attack can produce a bounded `observed` detection result;
- successful detection contains an attack-start slot and a first valid detection slot;
- detection timing references are comparable and suitable as later MTTD inputs;
- a completed observation window with no signal produces explicit `not_observed` evidence rather than infrastructure error;
- detector/runtime failure and timeout remain distinct from `not_observed`;
- malformed, contradictory or incomplete host evidence is rejected explicitly;
- repeated fresh runs preserve equivalent detection semantics;
- BeeDrill reaches detector/RPC execution only through the BeeAgent-owned bounded capability;
- BeeDrill remains `READ_ONLY`;
- AI does not determine whether detection occurred;
- existing attack capability behavior remains compatible.

#### Checks

```text
real detection produced
completed observation with detection absent
delayed detection evidence
malformed/inconsistent detection evidence
detector/runtime failure
timeout
approved module/case/capability/payload scope
forbidden execution-shaped input refusal
fresh-state replay consistency
BeeDrill/BeeAgent real isolated integration smoke
artifact inspection
secret-leak review
SAST
SCA only if dependency surface changes
git diff --check
```

#### DoD

BeeDrill receives real bounded independent detection evidence for the existing reference attack without owning detector execution, RPC authority or MTTD/verdict calculation.

### Iteration 8 — Deterministic metrics and verdict engine

**Status:** DONE

#### Goal

Implement the deterministic evaluator before using PASS/FAIL as a product claim in the real containment replay.

#### Scope

Calculate from validated evidence:

- detection result;
- containment result;
- MTTD;
- MTTC;
- gross attack loss;
- residual loss;
- capital saved;
- evidence completeness;
- final `DrillVerdict`.

Required rule:

```text
same validated evidence
→ same metrics
→ same verdict
```

Important contract clarification:

- fixture-provided verdict values are test expectations/oracles only;
- runtime/product verdict must be computed by the evaluator;
- a scenario or fixture must never self-authorize a PASS result.

#### Excluded

- proprietary risk score;
- subjective LLM score;
- arbitrary weighted score;
- benchmark percentile;
- financial modeling outside observed drill scope.

#### Deliverable

A stable deterministic evaluator that turns bounded evidence into explicit metrics and one typed verdict.

#### Acceptance criteria

- metric definitions are explicit;
- timing reference points are explicit;
- units/assets are explicit;
- missing critical evidence cannot become PASS;
- inconsistent evidence produces explicit incomplete/error behavior;
- same evidence produces same metrics;
- same evidence/metrics produce same verdict;
- runtime verdict is computed, not trusted from scenario input;
- LLM output has no verdict authority;
- assumptions are documented.

#### Checks

```text
known PASS fixture
known FAIL fixture
missing evidence
inconsistent evidence
zero-loss case
partial-containment case
boundary timing
deterministic replay
fixture expected-verdict vs computed-verdict check
```

#### DoD

BeeDrill has a deterministic product truth function before the real FAIL → PASS demonstration.

### Iteration 9 — Real containment and FAIL → PASS replay

**Status:** DONE

#### Goal

Prove the central BeeDrill thesis by replaying the same bounded attack sequence against a broken and then corrected containment condition and obtaining deterministic FAIL → PASS from real evidence.

#### Scope

- reuse the existing `reference_vault`, canonical initial state, unsafe-withdraw attack, reference detector and deterministic evaluator;
- require a dedicated BeeAgent-owned bounded containment capability before BeeDrill integration;
- execute equivalent fresh-state `broken` and `fixed` defense phases;
- use the same scenario identity/version and the same fixed attack sequence in both phases;
- observe detection before containment evaluation;
- verify the containment effect through real target state and a subsequent identical unsafe operation;
- derive gross and residual economic loss from machine evidence in integer lamports;
- validate all critical host evidence fail closed;
- build `DrillEvidence` and use the existing `evaluate_drill` truth function;
- produce a bounded comparison artifact containing evidence, metrics and computed verdicts for both phases.

#### Excluded

- new attack class;
- new reference target;
- BeeDrill-owned process, Surfpool or RPC execution;
- generic containment framework;
- arbitrary runtime configuration supplied by scenario input;
- production/mainnet mutation;
- human multisig workflow;
- autonomous production response;
- manual or AI verdict override;
- BeeSDK contract changes unless a new shared gap is independently proven.

#### Deliverable

One reproducible real security-control regression:

```text
same bounded attack sequence
+ broken containment
→ higher residual loss
→ deterministic FAIL

same bounded attack sequence
+ corrected containment
→ lower residual loss
→ deterministic PASS
```

#### Acceptance criteria

- both phases start from equivalent canonical economic state;
- scenario identity/version is unchanged between phases;
- attack semantics and bounded attack sequence are unchanged;
- only the intended defensive condition changes;
- the broken phase has observed detection and machine-evidenced failed containment;
- the fixed phase has observed detection and machine-evidenced successful containment;
- containment success is proven by target effect, not by a request or success string;
- the fixed phase prevents a subsequent identical unsafe operation;
- economic evidence does not erase already incurred loss;
- residual loss is lower after the defense correction;
- existing `evaluate_drill` produces FAIL then PASS without manual override;
- missing, malformed or contradictory critical evidence cannot produce PASS;
- repeated fresh replay preserves equivalent security meaning;
- BeeDrill remains `READ_ONLY`;
- execution authority remains owned by BeeAgent.

#### Checks

```text
broken-defense real run
fixed-defense real run
canonical-state equivalence
scenario identity/version equality
same-attack-sequence verification
detection evidence
containment-effect evidence
economic comparison
computed MTTD/MTTC/loss/capital-saved metrics
FAIL → PASS verdict sequence
malformed/incomplete evidence refusal
host refusal/timeout/error handling
fresh-state repeatability
BeeDrill/BeeAgent integration smoke
artifact inspection
SAST
SCA only if dependency surface changes
git diff --check
```

#### DoD

BeeDrill proves with real isolated execution evidence that correcting one containment condition changes the economic outcome of the same attack sequence from deterministic FAIL to deterministic PASS without taking ownership of runtime execution.

---

## Stage 3 — Security regression product

### Purpose of stage

Stage 3 proves BeeDrill is a reusable security regression product rather than a one-off reference demo.

It must show:

```text
same core domain/evidence/evaluator
→ second materially different attack class
→ repeatable runner
→ CI-compatible failure semantics
```

### Iteration 10 — Second attack class: oracle manipulation

**Status:** PLANNED
**Window:** 2026-09-27..2026-09-28

#### Goal

Add one materially different economic attack class to prove the architecture is not hardcoded to the first vault-drain path.

#### Scope

Included:

- bounded oracle manipulation scenario;
- unsafe economic action;
- expected detector behavior;
- expected containment behavior;
- measurable economic outcome;
- deterministic replay;
- reuse of existing domain/evidence/evaluator contracts.

#### Excluded

- generic oracle framework;
- support for every Solana oracle provider;
- production oracle manipulation;
- arbitrary runtime scripting;
- a third synthetic scenario merely for count.

#### Deliverable

A second real replayable scenario exercising the same BeeDrill core through a different economic failure class.

#### Acceptance criteria

- uses the same core domain/evidence/evaluator model;
- no duplicated orchestration framework;
- manipulation creates measurable unsafe economic state/action;
- detector expectation is machine-verifiable;
- containment expectation is machine-verifiable;
- PASS/FAIL remains deterministic;
- scenario resets/replays reproducibly.

#### Checks

```text
attack baseline
detection PASS/FAIL
containment PASS/FAIL
economic delta
computed verdict
reset
deterministic replay
```

#### DoD

BeeDrill supports two materially different security scenarios without scenario-specific architecture duplication.

---

### Iteration 11 — Reproducible regression runner and CI entry point

**Status:** PLANNED
**Window:** 2026-09-29

#### Goal

Turn the validated scenarios into a stable repeatable security regression product surface.

#### Scope

Included:

- stable BeeDrill local command/entrypoint;
- explicit scenario selection;
- environment reset;
- deterministic exit status;
- machine-readable run summary;
- canonical references to evidence/metrics/verdict artifacts;
- repeatable scenario execution;
- CI-friendly invocation;
- regression tests for known defenses.

#### Excluded

- SaaS scheduler;
- hosted CI fleet;
- dashboard;
- marketplace;
- generalized workflow engine.

#### Deliverable

A release/test pipeline can fail when a previously passing security-control drill regresses.

#### Acceptance criteria

- stable local invocation exists;
- scenario is selected explicitly;
- run starts from clean/reset state;
- PASS returns stable success behavior;
- security FAIL returns stable failure behavior;
- infrastructure ERROR/INCOMPLETE is distinguishable from security FAIL;
- machine-readable summary is produced;
- both scenario classes run repeatedly;
- intentional defense regression fails;
- restored defense passes;
- runner does not bypass BeeAgent execution ownership.

#### Checks

```text
expected-pass scenarios
intentional regression
clean rerun
exit status
machine-readable output
artifact references
environment reset
repeatability
```

#### DoD

BeeDrill behaves like a repeatable security regression tool rather than a manually orchestrated demo script.

---

## Stage 4 — Hardening, external validation and submission

### Purpose of stage

Stage 4 makes the BeeDrill MVP safe enough to demonstrate publicly and credible enough to submit as a product rather than a toy.

Priorities:

```text
adversarial hardening
→ external/non-toy validation
→ reproducibility
→ evidence package
→ demo freeze
```

No broad product expansion is allowed.

### Iteration 12 — Execution safety and fail-closed hardening

**Status:** PLANNED
**Window:** 2026-09-30..2026-10-01

#### Goal

Adversarially harden the execution and hostile-input boundaries already introduced by the working product.

Baseline safety is required from Iteration 4 onward; this iteration is not permission to defer fundamental isolation/authority controls.

#### Scope

Included:

- local/sandbox-only execution guard review;
- explicit target allowlisting;
- bounded RPC destinations;
- scenario input validation;
- process/subprocess timeout;
- cleanup under failure;
- artifact bounds;
- path restrictions;
- secret redaction;
- deterministic refusals;
- malformed/adversarial scenario tests;
- no-production-key enforcement;
- evidence fail-closed review.

#### Excluded

- production autonomous response;
- mainnet mutation;
- remote arbitrary command execution;
- arbitrary executable selection;
- generalized sandbox product.

#### Deliverable

A tested fail-closed execution boundary where malformed/untrusted input cannot escape the approved sandbox or manufacture a successful security result.

#### Acceptance criteria

- arbitrary executable selection impossible through scenario data;
- arbitrary RPC target refused;
- production/mainnet mutation target refused;
- production private keys not accepted/required;
- timeout terminates bounded execution;
- cleanup occurs after failures;
- unsafe paths rejected;
- malformed scenarios rejected;
- secret material not emitted in logs/artifacts;
- incomplete critical evidence cannot produce PASS;
- security assumptions documented;
- existing positive scenarios still pass after hardening.

#### Checks

```text
targeted negative tests
full tests
integration smoke
SAST
SCA if dependencies changed
forbidden target tests
path/input tests
timeout tests
cleanup tests
secret-leak tests
artifact-bound checks
positive-regression rerun
git diff --check
```

#### DoD

The working BeeDrill execution path remains functional while hostile input and execution-boundary failures are handled safely and explicitly.

---

### Iteration 13 — Real external integration and product evidence

**Status:** PLANNED
**Window:** 2026-10-02..2026-10-03

#### Goal

Prove BeeDrill is useful beyond its own synthetic reference target.

Design-partner and ecosystem outreach should begin earlier in parallel; this iteration closes the technical artifact.

#### Scope

Obtain at least one substantial external validation path:

- real external detector integration; or
- design-partner configuration; or
- real open-source Solana protocol configuration; or
- independently reproduced security-control failure against realistic protocol state.

Capture:

- setup;
- bounded configuration;
- evidence;
- deterministic result;
- limitations;
- product relevance;
- reproducibility instructions.

#### Excluded

- broad protocol compatibility;
- production mutation;
- unsupported universal claims;
- custom integrations for many protocols;
- a bespoke fork that cannot be reproduced.

#### Deliverable

At least one external/non-toy validation artifact demonstrating that BeeDrill's model applies outside the internal reference target.

#### Acceptance criteria

- target/integration is meaningfully external to the synthetic demo;
- setup is reproducible enough for review;
- verdict is based on machine evidence;
- no hidden manual PASS/FAIL override;
- limitations are documented;
- no production/mainnet mutation;
- result supports the product thesis rather than merely showing infrastructure;
- any external configuration contains no secrets.

#### Checks

```text
repeatable setup
external evidence
computed deterministic verdict
artifact inspection
limitation review
security-boundary review
clean rerun when feasible
```

#### DoD

The hackathon submission has non-toy evidence that BeeDrill can validate a real-world-shaped security-control surface.

---

### Iteration 14 — Hackathon demo, reproducibility package and submission freeze

**Status:** PLANNED
**Window:** 2026-10-04

#### Goal

Freeze the hackathon MVP and produce the final judge-ready reproducibility/evidence package.

This is an artifact-level product increment, not a documentation cleanup iteration.

#### Scope

Included:

- clean-checkout quickstart;
- final architecture/product documentation;
- concise competitor positioning;
- canonical example machine-readable output;
- final evidence bundle;
- final regression run;
- 60–90 second core demo flow;
- submission copy;
- demo video script;
- pitch video script;
- repository cleanup required for public review;
- verification that claims in the submission are backed by artifacts.

Target product story:

```text
attack
→ real detection
→ containment failure
→ measurable loss
→ fix
→ exact replay
→ containment success
→ lower residual loss
→ deterministic PASS
```

#### Excluded

- new scenario classes;
- new architecture;
- UI redesign;
- major refactor;
- speculative features;
- multichain;
- production autonomous response.

#### Deliverable

A judge can understand, reproduce and evaluate the central BeeDrill thesis from the repository, evidence and demo.

#### Acceptance criteria

- clean environment setup works from documented instructions;
- complete BeeDrill test suite passes;
- both attack classes execute as expected;
- FAIL → fix → exact replay → PASS is reproducible;
- security checks required by current implementation pass;
- no secrets/private keys are committed or leaked;
- architecture boundary is clearly documented;
- product differentiation is accurate;
- limitations are explicit;
- demo fits target duration;
- evidence artifacts support every material submission claim;
- repository has no known critical blocker;
- product scope is frozen before the buffer.

#### Checks

```text
clean checkout/install
full tests
package build
import smoke
all scenario regressions
security checks
artifact inspection
secret scan/review
demo rehearsal
documentation review
submission-claim-to-evidence review
```

#### DoD

BeeDrill MVP is frozen, reproducible and ready for Colosseum submission.

---

## Submission buffer — 2026-10-05..2026-10-12

### Purpose

The buffer protects the submission from predictable integration, reliability, review and presentation failures.

It is not a feature-development stage.

#### Allowed

- defects;
- reliability fixes;
- regression fixes;
- test strengthening;
- dependency/environment correction;
- design-partner feedback;
- performance fixes required for demo/reproducibility;
- documentation;
- demo/pitch recording;
- submission assets;
- submission corrections;
- critical compatibility fixes.

#### Not allowed without explicit GO/NO-GO review

- new major scenario category;
- new runtime architecture;
- broad BeeAgent redesign;
- new blockchain ecosystem;
- multichain support;
- marketplace;
- SaaS control plane;
- new UI product;
- x402 integration added only for hackathon optics;
- BeeScan integration;
- generalized pentesting platform;
- autonomous production response.

#### Freeze rule

By the start of the buffer, the product story is fixed:

```text
BeeDrill
=
continuous security-control validation for Solana

attack
→ detect
→ contain
→ measure
→ deterministic verdict
→ replay as regression test
```

## Post-hackathon orientation

Post-hackathon work is not pre-approved by this roadmap.

Potential directions may include:

- additional real protocol adapters;
- additional detector/control integrations;
- historical exploit scenario corpus;
- managed scheduled drills;
- hosted execution;
- STRIDE/SOS evidence mapping;
- protocol-specific scenario packs;
- benchmark datasets;
- team reporting;
- additional Solana security-control classes.

A post-hackathon item becomes real scope only after:

```text
product evidence
→ user/design-partner need
→ architecture review
→ necessity verdict
→ ownership decision
→ roadmap item
→ Issue
```

Do not create framework layers merely because future commercialization may need them.

## Related project boundaries

### BeeAgent

BeeAgent is the primary host/runtime.

BeeAgent owns:

```text
orchestration
module registry
runtime context
execution authority
process lifecycle
Surfpool lifecycle
RPC access
credentials
policy
timeouts
state
artifact implementation
external integrations
execution / egress
```

BeeDrill must not absorb these responsibilities.

If BeeDrill exposes a missing host capability, the fix belongs in BeeAgent unless a stable shared BeeSDK contract is proven insufficient and a shared-contract change is actually required.

### BeeSDK

BeeSDK owns only reusable shared public contracts.

BeeDrill may consume:

```text
ModuleContract
ModuleContext
ModuleResult
AuthorityLevel
ArtifactPort
CapabilityCaller
CapabilityResult
CapabilityStatus
```

when real integration requires them.

BeeSDK must not gain:

```text
Solana semantics
BeeDrill scenarios
Surfpool runtime
attack execution
detector implementation
containment implementation
BeeDrill metrics
BeeDrill verdict semantics
```

solely to support BeeDrill.

### BeeROP

BeeROP is a separate domain module.

BeeDrill may use its repository architecture as historical reference for module structure, but BeeDrill must not depend on BeeROP or inherit ROP domain semantics.

### BeeScan

BeeScan is not a dependency of the hackathon MVP.

BeeDrill does not wait for BeeScan and does not move BeeScan scanning responsibilities into BeeDrill.

Future integration requires separate evidence and scope.

### BeeUI

BeeUI is not required for the initial product proof.

A large web UI must not block or precede:

```text
real attack
→ real detection
→ real containment
→ deterministic verdict
```

Any future UI integration requires a separate product need.

### Bee Dev MCP

Bee Dev MCP remains a development/review tool.

BeeDrill is registered as an independent project so planning and review can operate against the actual repository.

Bee Dev MCP is not a BeeDrill runtime dependency.

## Future roadmap rule

The hackathon iterations are a fixed delivery plan, not permission for unlimited framework expansion.

After Iteration 14, new roadmap work follows:

```text
real user / product gap
→ evidence
→ necessity decision
→ ownership decision
→ roadmap item
→ Issue
→ implementation
→ verification
→ PR
```

Not:

```text
Iteration 14
→ Iteration 15
→ Iteration 16
→ Iteration 17
```

only because more numbers are available.

The correct outcome after the hackathon may be:

```text
no architecture change
```

if the current product surface is sufficient.

## Related process documents

BeeDrill development uses:

- `docs/SPEC.md` — product behavior, terminology and public product contract;
- `docs/ARCHITECTURE.md` — component ownership, dependency direction and runtime boundaries;
- `docs/DEV_GUIDE.md` — local development, tests, package build and integration workflow;
- `docs/SDLC.md` — change levels, Issues, branches, verification, PR and merge process;
- `docs/SECURITY.md` — isolation, authority, execution, RPC, secrets and hostile-input rules;
- `AGENTS.md` — repository-level development and AI-agent instructions.

## Summary

BeeDrill develops according to this principle:

```text
prove the product thesis first
→ make evidence deterministic
→ make the drill repeatable
→ harden the execution boundary
→ validate against something real
→ freeze the MVP
```

Not:

```text
build a platform
→ add abstractions
→ add UI
→ add integrations
→ eventually try to prove the product
```

Target hackathon state:

```text
small
Solana-native
deterministic
reproducible
security-sensitive
fail-closed
evidence-driven
useful
```
