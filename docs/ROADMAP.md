# ROADMAP — BeeDrill

## Purpose

This document defines the development path for `beedrill` through explicit stages and iterations.

BeeDrill uses the ROADMAP as a lightweight SDLC artifact:

- define the product direction;
- keep the hackathon scope bounded;
- define the goal and acceptance boundary of each meaningful iteration;
- connect Issue → Code → Tests → Evidence → PR → Merge;
- keep BeeDrill separate from BeeAgent runtime responsibilities;
- prevent speculative framework development;
- preserve deterministic security verdicts;
- ensure security-sensitive execution remains controlled and reviewable;
- reserve enough time before the Colosseum deadline for hardening, validation, demo work and submission.

The ROADMAP does not replace Issues or Pull Requests:

- **Issue** defines the exact approved implementation task;
- **PR** records what was actually implemented and verified;
- **ROADMAP** defines the iteration-level product contract and direction.

A significant roadmap iteration is normally delivered through a PR.

Small low-risk maintenance that does not change runtime behavior, security boundaries, public contracts, dependencies or product semantics may follow the shorter path defined in `docs/SDLC.md`.

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
| **Regression principle**       | A security defense should be testable repeatedly after changes in the same way application behavior is regression-tested.                                                 |
| **Ground-truth principle**     | Critical outcomes are derived from observable execution evidence, not subjective AI confidence scores.                                                                    |
| **Determinism principle**      | The same valid evidence must produce the same security verdict.                                                                                                           |
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
→ deterministic PASS / FAIL
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

Architecture invariant:

```text
BeeDrill
!=
second BeeAgent runtime
```

and:

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

shared stable module contract
→ BeeSDK, but only if proven necessary

scenario semantics
→ BeeDrill
```

BeeDrill roadmap iterations may require cross-repository integration evidence, but BeeDrill must not copy BeeAgent runtime implementation into this repository.

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

Critical PASS/FAIL behavior must be deterministic and based on bounded evidence.

### No hidden AI authority

LLM output may not:

- authorize execution;
- choose production targets;
- grant credentials;
- override evidence;
- silently convert an incomplete run into PASS;
- determine the final critical security verdict.

### Evidence integrity

Missing, malformed, inconsistent or insufficient critical evidence must produce an explicit degraded/refused/fail-closed outcome rather than an invented success.

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

BeeDrill uses small product-sized iterations.

Every significant roadmap iteration must:

- have a concrete product or integration goal;
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

For BeeDrill, especially important:

```text
simulation
!=
proof
```

A mocked attack event is not sufficient evidence for a real attack scenario.

And:

```text
control configured
!=
control validated
```

And:

```text
evidence
!=
authority
```

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

   Confirm:
   - real problem;
   - iteration necessity;
   - current architecture boundary;
   - closest existing implementation;
   - implementation owner.

2. **Requirements**

   Define:
   - Goal;
   - Scope;
   - Excluded;
   - Deliverable;
   - Acceptance criteria;
   - contract/config impact;
   - dependency impact;
   - security impact;
   - Checks;
   - DoD.

3. **Issue**

   Create one focused Issue in the repository that owns the implementation.

4. **Implementation**

   Implement the smallest complete solution on a dedicated branch.

5. **Verification**

   Execute applicable:
   - targeted tests;
   - full tests;
   - package build;
   - integration smoke;
   - artifact checks;
   - deterministic replay;
   - negative boundary tests;
   - quality/security checks.

6. **Review / PR**

   Record actual implementation and verification evidence.

7. **Merge**

   Merge only after iteration acceptance criteria are satisfied.

8. **Regression**

   Preserve completed scenario behavior through tests and replay fixtures.

9. **Release**

   Release only when a useful product/package milestone is reached.

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

Changes affecting trust, authority, execution or hostile input boundaries.

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

BeeDrill uses SemVer for package/product milestones.

Version source of truth:

```text
pyproject.toml
```

Roadmap iteration and release version are different concepts.

Ordinary implementation work must not manually bump the project version unless the task is explicitly release-related.

Target hackathon baseline:

```text
v0.1.0
```

should represent the first complete reproducible BeeDrill MVP, not merely repository bootstrap.

Expected v0.1.0 milestone:

```text
module integration
+
isolated real attack execution
+
real detection observation
+
real containment validation
+
deterministic metrics
+
repeatable security regression suite
+
judge-ready evidence
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

Release automation may be introduced during repository bootstrap, but release mechanics must not become a blocker for the product MVP.

## Delivery window

Hackathon dates used for planning:

```text
Start:    2026-09-14
Deadline: 2026-10-12
```

Implementation window:

```text
2026-09-15 → 2026-10-04
20 calendar build days
15 iterations
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

| Phase                                            | Status      | What it means                                                                                                                   |
| ------------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Phase A — Repository and contract foundation** | IN PROGRESS | Establish BeeDrill as a standalone BeeAgent module with explicit contracts, governance and development boundaries.              |
| **Phase B — End-to-end falsification prototype** | PLANNED     | Prove that a real isolated Solana attack can produce real detection/containment evidence and a reproducible FAIL → PASS result. |
| **Phase C — Security regression product**        | PLANNED     | Turn the successful falsification path into deterministic metrics, multiple scenarios and repeatable CI-style regression tests. |
| **Phase D — Hardening and external validation**  | PLANNED     | Secure the execution boundary, obtain non-toy validation and freeze the judge-ready MVP.                                        |
| **Submission buffer**                            | PLANNED     | Stabilization, testing, external feedback, demo and submission only; no planned major scope.                                    |

### Stages

- **Stage 1 — Repository and module foundation:** package, governance, BeeSDK contract use and BeeAgent compatibility.
- **Stage 2 — End-to-end falsification prototype:** isolated Solana runtime, target, real attack, detector and containment.
- **Stage 3 — Metrics and regression product:** deterministic verdict engine, additional scenarios and CI-style replay.
- **Stage 4 — Hardening and product validation:** fail-closed execution security, external evidence and submission freeze.

## Stage 1 — Repository and module foundation

### Purpose of stage

Stage 1 establishes BeeDrill as a small standalone product module before security-sensitive Solana execution is introduced.

The stage must prove:

```text
BeeDrill
→ independent package
→ BeeSDK contract consumer
→ BeeAgent-compatible module
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

- standalone repository:
  - `beedrill`;

- Python distribution:
  - `beedrill`;

- Python import package:
  - `beedrill`;

- Python:
  - `>=3.14`;

- package management:
  - `uv`;

- standard `src` layout;

- minimal module entrypoint:
  - `BeeDrillModule`;

- stable identity:
  - `module_id = "beedrill"`;

- initial module authority:
  - `read_only`;

- repository documentation:
  - `README.md`;
  - `docs/ROADMAP.md`;
  - `docs/SPEC.md`;
  - `docs/ARCHITECTURE.md`;
  - `docs/SDLC.md`;
  - `docs/SECURITY.md`;
  - `docs/DEV_GUIDE.md`;

- repository-level:
  - `AGENTS.md`;

- project-local AI/development workflow:
  - `.agents/prompts/01-planning.md`;
  - `.agents/prompts/02-implementation-tests.md`;
  - `.agents/prompts/03-final-review.md`;
  - corresponding BeeDrill-local skills;

- GitHub Issue template;
- GitHub PR template;

- release/package metadata baseline;

- minimal package/import tests;
- module identity and initial-authority tests;
- build configuration;
- repository hygiene baseline.

#### Excluded

BD-1 does not include:

- BeeSDK dependency integration;
- BeeSDK `ModuleContract` implementation;
- BeeAgent module-registry integration;
- BeeAgent invocation smoke;
- host artifact-port integration;
- Surfpool execution;
- Solana RPC execution;
- Solana transactions;
- attack execution;
- detector integration;
- circuit-breaker integration;
- containment execution;
- custom execution framework;
- BeeAgent runtime implementation;
- BeeSDK expansion;
- BeeScan;
- BeeUI;
- dashboard;
- production credentials;
- mainnet mutation.

#### Deliverable

A standalone BeeDrill repository/package that is ready for BeeSDK contract integration and feature development without unresolved ownership or workflow ambiguity.

Expected minimal structure:

```text
beedrill/
├── .agents/
├── .github/
├── docs/
├── src/
│   └── beedrill/
├── tests/
├── AGENTS.md
├── README.md
├── CHANGELOG.md
├── pyproject.toml
└── uv.lock
```

Additional implementation directories must not be created speculatively.

#### Acceptance criteria

- repository is an independent Git repository;
- package/import identity is `beedrill`;
- Python requirement is `>=3.14`;
- project uses `uv`;
- source uses standard `src` layout;
- BeeDrill does not copy BeeAgent or BeeSDK platform contracts;
- `BeeDrillModule` exposes stable `module_id = "beedrill"`;
- initial module authority is `read_only`;
- package imports without starting runtime services;
- no Surfpool, RPC, subprocess or external execution exists;
- architecture assigns execution to BeeAgent;
- architecture assigns scenario/evidence/verdict semantics to BeeDrill;
- BeeSDK ownership remains limited to shared contracts;
- documentation is internally consistent;
- prompts/skills are BeeDrill-local;
- Issue/PR templates exist;
- release/package metadata baseline exists;
- tests cover package import, module identity and initial authority;
- no production secrets or private keys are present.

#### Checks

Required:

```bash
uv sync
uv run pytest -q
uv build
uv run python -c "import beedrill; print(beedrill.__file__)"
git diff --check
```

Architecture review:

```text
BeeDrill does not own host runtime
BeeDrill does not own arbitrary execution
BeeDrill does not copy BeeAgent or BeeSDK platform contracts
module authority is read_only
no production/mainnet execution surface exists
```

Security/quality:

```text
SAST for package/module bootstrap
SCA for initial dependency surface
DAST not applicable
IAST not applicable
fuzzing not required
```

#### DoD

- standalone package/repository exists;
- architecture boundaries are explicit;
- repository workflow is defined;
- tests pass;
- package builds;
- import smoke passes;
- module scaffold is ready for BeeSDK contract integration in Iteration 2;
- no execution/egress path exists;
- no shared platform contract duplication is introduced;
- docs, AGENTS, prompts, skills and GitHub templates agree on the same architecture;
- BD-1 bootstrap baseline is complete.

### Iteration 2 — BeeSDK module contract and BeeAgent load smoke

**Status:** PLANNED

#### Goal

Prove that BeeDrill can consume the approved BeeSDK v0.1 module contracts and can be loaded and invoked by the current BeeAgent module runtime without duplicating platform contracts or requiring a broad BeeAgent migration.

#### Scope

- declare BeeSDK `0.1.0` as an explicit BeeDrill runtime dependency through a verified available source;
- import shared contracts from the explicit BeeSDK public contract modules:
  - `beesdk.modules`;
  - `beesdk.artifacts`;

- implement `BeeDrillModule` against `ModuleContract`;
- preserve `module_id = "beedrill"`;
- use `AuthorityLevel.READ_ONLY`;
- expose one explicit bounded integration case;
- return a bounded `ModuleResult`;
- verify structural compatibility with the current BeeAgent `ModuleRegistry`;
- invoke BeeDrill through the current BeeAgent `execute_module_case()` path;
- verify BeeAgent authority normalization accepts BeeSDK authority;
- verify the host-provided `ArtifactAPI` satisfies `ArtifactPort` structurally;
- write one bounded module artifact through the BeeAgent-owned artifact lifecycle;
- record compatibility evidence against the current BeeAgent runtime.

#### Excluded

- broad BeeAgent migration to BeeSDK;
- `beeagent-rop` migration to BeeSDK;
- BeeSDK redesign or new shared contracts without proven need;
- production BeeAgent registry configuration changes;
- drill domain models or scenario semantics from BD-3;
- Surfpool, Solana RPC, attack, detector or containment execution;
- new execution authority;
- BeeUI or BeeScan integration.

#### Deliverable

BeeDrill is a real BeeSDK v0.1 contract consumer that the current BeeAgent registry/runtime can discover and invoke through the existing module boundary, including one host-owned artifact write, without changing BeeAgent or BeeSDK unless an actual compatibility gap is demonstrated.

#### Acceptance criteria

- BeeDrill declares `beesdk==0.1.0` from a verified available source;
- BeeDrill imports shared contracts from `beesdk.modules` and `beesdk.artifacts`;
- `BeeDrillModule` satisfies BeeSDK `ModuleContract`;
- `module_id == "beedrill"`;
- authority is `AuthorityLevel.READ_ONLY`;
- supported case types are explicit and bounded;
- the current BeeAgent `ModuleRegistry` loads BeeDrill;
- the current BeeAgent runtime invokes BeeDrill through `execute_module_case()`;
- BeeSDK authority is accepted by current BeeAgent authority normalization;
- a BeeSDK `ModuleResult` is accepted and normalized by the current BeeAgent runtime;
- BeeAgent `ArtifactAPI` satisfies the required `ArtifactPort` shape;
- one artifact write succeeds through the BeeAgent-owned artifact lifecycle;
- unsupported case types are rejected explicitly;
- BeeDrill imports no private BeeAgent contracts;
- no BeeAgent or BeeSDK implementation change is introduced without demonstrated compatibility evidence.

#### Checks

- BeeDrill targeted module/contract tests;
- `uv run pytest -q`;
- `uv build`;
- package import smoke;
- BeeSDK `ModuleContract` structural compatibility check;
- BeeSDK explicit contract-module import check;
- current BeeAgent registry load smoke;
- current BeeAgent `execute_module_case()` smoke;
- authority normalization compatibility check;
- `ArtifactAPI` / `ArtifactPort` structural compatibility and artifact-write smoke;
- `git diff --check`;
- SAST mindset review of the module/authority boundary;
- SCA for the approved BeeSDK dependency change.

#### DoD

- BeeDrill consumes BeeSDK v0.1 contracts directly;
- current BeeAgent loads and invokes BeeDrill without a broad BeeAgent migration;
- host-owned artifact integration works through the shared structural boundary;
- read-only authority remains host-owned and compatible;
- no duplicated platform contract exists in BeeDrill;
- no execution or egress capability is added;
- BeeAgent and BeeSDK remain unchanged unless a concrete gap is proven;
- dependency and contract documentation matches the implemented behavior;
- BeeDrill is ready to proceed directly to BD-3.

### Iteration 3 — Drill domain contracts and fixture baseline

**Status:** PLANNED
**Window:** Days 3–4 — 2026-09-17..2026-09-18

#### Goal

Define the smallest deterministic BeeDrill domain model needed to represent one complete security-control validation drill.

#### Scope

Define bounded domain contracts for:

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
- drill verdict.

Add sanitized deterministic fixtures.

#### Excluded

- generic scenario language;
- extensible plugin system;
- YAML DSL framework;
- arbitrary executable scenario payloads;
- AI-generated verdicts;
- Solana chain execution;
- production protocol schema.

#### Deliverable

A fixture-driven domain baseline capable of expressing the first complete drill without invoking Solana.

#### Acceptance criteria

- one complete drill is representable using bounded models;
- required fields are explicit;
- invalid critical fields are refused;
- serialization is deterministic;
- scenario identity is stable;
- evidence completeness can be represented explicitly;
- PASS/FAIL is not inferred from free-form text;
- no executable command or arbitrary code is carried by scenario data;
- fixtures contain no real secrets/private keys;
- models remain BeeDrill-local and are not added to BeeSDK.

#### Checks

```text
schema/model tests
malformed-input tests
deterministic serialization tests
fixture tests
negative executable-input tests
```

#### DoD

One security-control drill can be described completely as validated domain data before execution infrastructure exists.

---

## Stage 2 — End-to-end falsification prototype

### Purpose of stage

Stage 2 is the central product falsification stage.

It must prove that BeeDrill can produce:

```text
real isolated state
→ real attack execution
→ real detector evidence
→ real containment behavior
→ measurable economic outcome
→ FAIL
→ fix
→ exact replay
→ PASS
```

If this stage requires fake alerts, fake attacks or manually invented verdict evidence, the product thesis is not considered proven.

---

### Iteration BD-4 — Surfpool host-execution integration spike

**Status:** PLANNED
**Window:** Day 5 — 2026-09-19

#### Goal

Prove that BeeAgent can create and control an isolated Solana execution environment for BeeDrill while keeping execution authority host-owned.

#### Scope

Product milestone:

- bounded Surfpool lifecycle;
- explicitly approved local/sandbox target;
- startup;
- readiness check;
- bounded RPC smoke;
- timeout;
- shutdown;
- cleanup;
- bounded execution result returned as evidence.

Ownership rule:

```text
BeeAgent
→ execution implementation

BeeDrill
→ execution intent / domain interpretation
```

If current BeeAgent lacks the required bounded host execution path, implementation belongs in a separate BeeAgent Issue/branch/PR.

#### Excluded

- arbitrary subprocess execution from BeeDrill;
- arbitrary binary/path supplied by scenario input;
- arbitrary RPC destinations;
- mainnet transaction submission;
- production private keys;
- generic process-execution framework;
- broad capability redesign.

#### Deliverable

One reproducible approved sandbox lifecycle:

```text
start
→ ready
→ RPC
→ stop
→ clean
```

with host-owned execution authority.

#### Acceptance criteria

- isolated environment starts reproducibly;
- readiness can be verified;
- RPC smoke succeeds;
- timeout behavior is bounded;
- shutdown/cleanup is reliable;
- failed startup produces explicit failure evidence;
- forbidden/non-approved target is refused;
- BeeDrill cannot choose arbitrary executable/process arguments;
- no production key is required;
- no mainnet mutation path is created;
- host/module ownership remains explicit.

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
security review
```

#### DoD

BeeAgent can safely provide the isolated Solana execution primitive needed by BeeDrill without moving runtime execution into the module.

---

### Iteration BD-5 — Reference vulnerable protocol and reproducible state

**Status:** PLANNED
**Window:** Days 6–7 — 2026-09-20..2026-09-21

#### Goal

Create one deliberately vulnerable Solana reference target with measurable economic state and an explicit technical defensive control.

#### Scope

Included:

- minimal reference vault/protocol;
- deterministic balances/state;
- one intentionally attackable condition;
- detector signal source;
- pause/breaker path;
- resettable environment;
- reproducible initial state.

#### Excluded

- production protocol integration;
- large lending/DEX implementation;
- realistic frontend;
- arbitrary protocol SDK;
- vulnerability discovery engine.

#### Deliverable

A minimal reference target where attack damage and defensive containment can be measured objectively.

#### Acceptance criteria

- initial state is reproducible;
- normal operation succeeds;
- vulnerable path exists intentionally;
- economic value/state is measurable;
- detector can observe a relevant signal;
- pause/breaker control exists;
- target resets between runs;
- reference target is clearly marked as intentionally vulnerable;
- no production/private data is used.

#### Checks

```text
baseline state
normal operation
vulnerable operation
control availability
state reset
repeatability
```

#### DoD

Every drill run can begin from the same known target state with measurable capital and explicit defense controls.

---

### Iteration BD-6 — First real attack scenario

**Status:** PLANNED
**Window:** Day 8 — 2026-09-22

#### Goal

Execute the first deterministic economic attack against the reference target.

#### Scope

First scenario:

```text
vault drain / abnormal outflow
```

Capture:

- attack start;
- submitted transactions;
- signatures/identifiers where safe;
- slots;
- balances;
- state transitions;
- completion evidence;
- gross economic loss.

#### Excluded

- detector verdict;
- containment verdict;
- AI analysis;
- additional attack classes.

#### Deliverable

A reproducible real attack trace with objectively measurable economic loss.

#### Acceptance criteria

- attack changes real isolated Solana state;
- attack succeeds against the intentionally vulnerable baseline;
- economic loss is measurable;
- transaction/state evidence is captured;
- repeated execution from identical initial state produces equivalent outcome;
- attack does not depend on fake event injection;
- scenario remains isolated from production/mainnet.

#### Checks

```text
attack success
economic delta
repeatability
bounded evidence
serialization
reset and replay
```

#### DoD

BeeDrill has executed a real isolated attack rather than a mocked security event.

---

### Iteration BD-7 — Detection observation

**Status:** PLANNED
**Window:** Days 9–10 — 2026-09-23..2026-09-24

#### Goal

Measure whether an independent technical detector observes the attack and capture machine-verifiable detection timing.

#### Scope

Included:

- bounded detector observation contract;
- one real detector/reference-monitor integration;
- attack-start marker;
- detection marker;
- slot/time evidence;
- MTTD input evidence;
- timeout;
- missing-alert handling.

#### Excluded

- human PagerDuty response;
- SOC workflow;
- manual operator judgment;
- subjective AI detection score;
- broad SIEM integrations.

#### Deliverable

Machine-verifiable detection evidence capable of producing deterministic detection PASS/FAIL.

#### Acceptance criteria

- detector receives/observes real attack-related state or events;
- successful alert is captured as evidence;
- absent alert is distinguishable from execution failure;
- delayed alert is measurable;
- malformed detector output is refused/degraded explicitly;
- attack start and detection event have comparable timing evidence;
- AI is not used to decide whether detection occurred.

#### Checks

```text
alert produced
alert absent
alert delayed
malformed observation
detector unavailable
timeout
replay consistency
```

#### DoD

Detection status is derived from actual bounded evidence rather than narrative or manual interpretation.

---

### Iteration BD-8 — Containment and FAIL → PASS replay

**Status:** PLANNED
**Window:** Day 11 — 2026-09-25

#### Goal

Prove the central BeeDrill thesis by showing one identical attack fail before a defensive fix and pass after the fix.

#### Scope

Included:

- pause/breaker observation or invocation through the approved host boundary;
- intentionally broken containment configuration;
- failed containment run;
- corrected configuration;
- exact scenario replay;
- successful containment run;
- resulting economic-state comparison.

#### Excluded

- production autonomous response;
- human multisig workflow;
- broad incident-response automation;
- new attack class.

#### Deliverable

Same scenario:

```text
before fix
→ DETECT
→ CONTAINMENT FAIL
→ high loss
→ FAIL

after fix
→ DETECT
→ CONTAINMENT PASS
→ bounded residual loss
→ PASS
```

#### Acceptance criteria

- first run produces a real containment failure;
- failure reason is evidenced;
- attack scenario identity remains unchanged;
- initial state is equivalent;
- correction changes only the intended defense condition;
- replay produces real successful containment;
- resulting state/economic loss differs measurably;
- no manual verdict override is required.

#### Checks

```text
broken defense run
fixed defense run
scenario identity check
initial-state equivalence
chain-state evidence
economic comparison
repeatability
```

#### DoD

BeeDrill demonstrates that a concrete security-control correction changes the real economic outcome of the same attack.

---

## Stage 3 — Metrics and regression product

### Purpose of stage

Stage 3 converts the successful falsification prototype into a repeatable product.

The stage must produce:

```text
bounded evidence
→ deterministic metrics
→ deterministic verdict
→ multiple attack classes
→ repeatable release regression
```

---

### Iteration BD-9 — Deterministic security metrics and verdict engine

**Status:** PLANNED
**Window:** Day 12 — 2026-09-26

#### Goal

Convert execution evidence into objective security-control metrics and one stable drill verdict.

#### Scope

Calculate:

- detection result;
- containment result;
- MTTD;
- MTTC;
- gross attack loss;
- residual loss;
- capital saved;
- evidence completeness;
- deterministic final verdict.

#### Excluded

- proprietary risk score;
- subjective LLM score;
- arbitrary weighted security score;
- benchmark percentile;
- financial modeling outside observed drill scope.

#### Deliverable

Stable `DrillVerdict` semantics based only on validated evidence.

#### Acceptance criteria

- metric definitions are explicit;
- units are explicit;
- missing critical evidence cannot become PASS;
- inconsistent evidence produces explicit degraded/error behavior;
- same evidence produces same metrics;
- same metrics/evidence produce same verdict;
- LLM output has no verdict authority;
- calculation assumptions are documented.

#### Checks

```text
known PASS
known FAIL
missing evidence
inconsistent evidence
zero-loss case
partial-containment case
boundary timing
deterministic replay
```

#### DoD

The same valid evidence always produces the same metrics and final security verdict.

---

### Iteration BD-10 — Oracle manipulation scenario

**Status:** PLANNED
**Window:** Days 13–14 — 2026-09-27..2026-09-28

#### Goal

Add a second materially different economic attack class to prove the architecture is not hardcoded to one vault-drain path.

#### Scope

Included:

- bounded oracle manipulation scenario;
- unsafe economic action;
- expected detector behavior;
- expected containment behavior;
- measurable economic outcome;
- deterministic replay.

#### Excluded

- generic oracle framework;
- all Solana oracle providers;
- production oracle manipulation;
- arbitrary runtime scripting.

#### Deliverable

Second reproducible scenario exercising the same BeeDrill evidence/verdict architecture through a different economic failure class.

#### Acceptance criteria

- scenario uses the same core domain/evidence model;
- no duplicated orchestration framework is introduced;
- manipulation results in measurable unsafe economic state/action;
- detector expectation is machine-verifiable;
- containment expectation is machine-verifiable;
- PASS/FAIL remains deterministic;
- scenario resets and replays reproducibly.

#### Checks

```text
attack baseline
detector PASS
detector FAIL
containment PASS
containment FAIL
economic delta
deterministic replay
```

#### DoD

BeeDrill supports at least two materially distinct security scenarios without scenario-specific orchestration duplication.

---

### Iteration BD-11 — Broken authority / containment scenario

**Status:** PLANNED
**Window:** Day 15 — 2026-09-29

#### Goal

Validate a control-plane failure where attack detection succeeds but containment cannot execute because the defensive authority/configuration is incorrect.

#### Scope

Reference failure:

```text
attack detected
→ pause requested
→ wrong authority / invalid control configuration
→ containment fails
```

Then:

```text
authority/config fixed
→ exact replay
→ containment succeeds
```

#### Excluded

- production multisig operations;
- credential harvesting;
- private-key testing;
- generalized IAM platform.

#### Deliverable

Third scenario focused on operational defensive control failure rather than vulnerability discovery.

#### Acceptance criteria

- detection succeeds in both baseline and fixed runs;
- containment failure is caused by deterministic control configuration;
- failure reason is explicit;
- no real secret/private key is required;
- corrected configuration passes exact replay;
- verdict reflects containment outcome;
- scenario demonstrates that configured control presence is insufficient proof of operability.

#### Checks

```text
broken authority/config
successful detection
failed containment
corrected authority/config
successful replay
economic outcome comparison
```

#### DoD

BeeDrill demonstrates that a configured defensive control may exist while remaining operationally unusable during an attack.

---

### Iteration BD-12 — Reproducible regression suite and CI entry point

**Status:** PLANNED
**Window:** Day 16 — 2026-09-30

#### Goal

Turn individual drills into repeatable security regression tests suitable for release/CI workflows.

#### Scope

Included:

- stable BeeDrill command/entrypoint;
- scenario selection;
- environment reset;
- deterministic exit status;
- machine-readable summary;
- reproducible scenario execution;
- CI-friendly invocation;
- regression tests for known defenses.

#### Excluded

- SaaS scheduler;
- hosted CI fleet;
- dashboard;
- marketplace;
- generalized workflow engine.

#### Deliverable

A release/test pipeline can fail when a previously passing security-control scenario regresses.

#### Acceptance criteria

- stable local invocation exists;
- scenario can be selected explicitly;
- run starts from clean/reset state;
- PASS returns stable successful exit behavior;
- FAIL returns stable failure exit behavior;
- infrastructure error is distinguishable from security FAIL;
- machine-readable summary is produced;
- all existing scenarios can run repeatedly;
- intentional defense regression causes expected failure;
- restored defense causes expected pass.

#### Checks

```text
all expected-pass scenarios
intentional regression
clean rerun
exit status
machine-readable output
environment reset
repeatability
```

#### DoD

BeeDrill behaves as a reproducible security regression product rather than a one-off demonstration script.

---

## Stage 4 — Hardening and product validation

### Purpose of stage

Stage 4 makes the BeeDrill MVP safe enough to demonstrate publicly and credible enough to submit as a product rather than a toy.

Priorities:

```text
execution safety
→ external relevance
→ reproducibility
→ product evidence
→ demo freeze
```

No broad product expansion is allowed.

---

### Iteration BD-13 — Execution safety and fail-closed hardening

**Status:** PLANNED
**Window:** Days 17–18 — 2026-10-01..2026-10-02

#### Goal

Harden the highest-risk execution and input boundaries before public demo or external use.

#### Scope

Included:

- local/sandbox-only execution guard;
- explicit target allowlisting;
- no production private keys;
- bounded RPC destinations;
- scenario input validation;
- process/subprocess timeout;
- cleanup;
- artifact bounds;
- path restrictions;
- secret redaction;
- deterministic refusals;
- malformed/adversarial scenario tests.

#### Excluded

- production autonomous response;
- mainnet mutation;
- remote arbitrary command execution;
- arbitrary executable selection;
- generalized sandbox product.

#### Deliverable

Security-sensitive BeeDrill execution fails closed and untrusted scenario input cannot escape the approved sandbox boundary.

#### Acceptance criteria

- arbitrary executable selection is impossible through scenario data;
- arbitrary RPC target is refused;
- production/mainnet mutation target is refused;
- production private keys are not accepted/required for MVP execution;
- timeout terminates bounded execution;
- cleanup occurs after failure;
- unsafe paths are rejected;
- malformed scenarios are rejected;
- secret material is not emitted in logs/artifacts;
- incomplete critical evidence cannot produce PASS;
- security assumptions are documented.

#### Checks

Required as applicable:

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
git diff --check
```

#### DoD

Untrusted or malformed input cannot grant arbitrary execution, reach a forbidden target or silently convert an unsafe/incomplete drill into success.

---

### Iteration BD-14 — Real integration and product evidence

**Status:** PLANNED
**Window:** Day 19 — 2026-10-03

#### Goal

Prove that BeeDrill is useful beyond its own synthetic reference target.

#### Scope

Obtain at least one substantial external validation path:

- real external detector integration; or
- design-partner configuration; or
- real open-source Solana protocol configuration; or
- independently reproduced security-control failure against realistic protocol state.

Capture:

- setup;
- evidence;
- limitations;
- product relevance.

#### Excluded

- broad protocol compatibility;
- production mutation;
- unsupported claims of universal coverage;
- custom work for many protocols.

#### Deliverable

At least one external/non-toy validation artifact showing that BeeDrill's security-control testing model applies outside the internal reference target.

#### Acceptance criteria

- validation target/integration is meaningfully external to the synthetic demo;
- setup is reproducible enough for review;
- verdict is based on machine evidence;
- no hidden manual PASS/FAIL override is used;
- limitations are documented;
- no production/mainnet mutation is performed;
- result supports the product thesis rather than only demonstrating infrastructure.

#### Checks

```text
repeatable setup
external evidence
deterministic verdict
artifact inspection
limitation review
security-boundary review
```

#### DoD

Hackathon submission includes evidence that BeeDrill is not merely a self-contained synthetic demonstration.

---

### Iteration BD-15 — Hackathon demo and submission readiness

**Status:** PLANNED
**Window:** Day 20 — 2026-10-04

#### Goal

Freeze the hackathon MVP and make BeeDrill reproducible, understandable and judge-ready.

#### Scope

Included:

- clean-checkout quickstart;
- architecture documentation;
- README;
- product positioning;
- competitor positioning;
- 60–90 second demo flow;
- evidence bundle;
- example machine-readable output;
- final regression run;
- submission copy;
- demo/video script;
- repository cleanup required for public review.

Target demo:

```text
attack
→ detect
→ containment failure
→ measurable loss
→ fix
→ exact replay
→ PASS
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

A judge can understand, run and evaluate the central BeeDrill thesis from the repository and demo.

#### Acceptance criteria

- clean environment setup works from documented instructions;
- complete BeeDrill test suite passes;
- all three scenario classes execute as expected;
- FAIL → fix → exact replay → PASS demo is reproducible;
- security checks required by current implementation pass;
- no secrets/private keys are committed or leaked;
- architecture boundary is clearly documented;
- product differentiation is accurately stated;
- limitations are explicit;
- demo fits the target duration;
- evidence artifacts support claims made in the submission;
- no known critical blocker remains.

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
```

#### DoD

BeeDrill MVP is frozen, reproducible and ready for Colosseum submission.

---

## Submission buffer — 2026-10-05..2026-10-12

### Purpose

The buffer protects the submission from predictable integration, reliability, review and presentation failures.

It is not a fifth feature-development stage.

#### Allowed

- defects;
- reliability fixes;
- regression fixes;
- test strengthening;
- dependency or environment corrections;
- design-partner feedback;
- performance fixes required for demo/reproducibility;
- documentation;
- demo recording;
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

By the start of the buffer, the expected product story is fixed:

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

---

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
→ roadmap item
→ Issue
```

Do not create framework layers merely because future commercialization may need them.

---

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

If BeeDrill exposes a missing host capability, the fix belongs in BeeAgent unless a stable shared BeeSDK contract is proven necessary.

---

### BeeSDK

BeeSDK owns only reusable shared public contracts.

BeeDrill may consume:

```text
ModuleContract
ModuleContext
ModuleResult
AuthorityLevel
ArtifactPort
CapabilityCaller / CapabilityResult when real integration requires them
```

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

---

### BeeROP

BeeROP is a separate domain module.

BeeDrill may use its repository architecture as historical reference for module structure, but BeeDrill must not depend on BeeROP or inherit ROP domain semantics.

---

### BeeScan

BeeScan is not a dependency of the hackathon MVP.

BeeDrill does not wait for BeeScan and does not move BeeScan scanning responsibilities into BeeDrill.

Future integration requires separate evidence and scope.

---

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

---

### Bee Dev MCP

Bee Dev MCP remains a development/review tool.

BeeDrill should be registered as an independent project so planning and review can operate against the actual repository.

Bee Dev MCP is not a BeeDrill runtime dependency.

---

## Future roadmap rule

The 15 hackathon iterations are a fixed delivery plan, not permission for unlimited framework expansion.

After BD-15, new roadmap work follows:

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
BD-15
→ BD-16
→ BD-17
→ BD-18
```

only because more numbers are available.

The correct outcome after the hackathon may be:

```text
no architecture change
```

if the current product surface is sufficient.

---

## Related process documents

BeeDrill development uses:

- `docs/SPEC.md` — product behavior, terminology and public product contract;
- `docs/ARCHITECTURE.md` — component ownership, dependency direction and runtime boundaries;
- `docs/DEV_GUIDE.md` — local development, tests, package build and integration workflow;
- `docs/SDLC.md` — change levels, Issues, branches, verification, PR and merge process;
- `docs/SECURITY.md` — isolation, authority, execution, RPC, secrets and hostile-input rules;
- `AGENTS.md` — repository-level development and AI-agent instructions.

---

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
