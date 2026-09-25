# BeeDrill — Continuous Security Control Validation for Solana

**BeeDrill** is security regression testing for Solana.

It verifies whether real defensive controls detect and contain reproducible
attacks before those controls are needed during a real incident.

> **Audits test your code. BeeDrill tests your defenses.**

BeeDrill asks a simple question:

> If an attack starts now, will the configured detector, containment controls,
> and security authority actually protect capital?

## Why BeeDrill

Protocol teams may already have:

- audits;
- monitoring;
- alerts;
- anomaly detection;
- circuit breakers;
- pause mechanisms;
- emergency authorities;
- containment procedures.

But the existence of a control does not prove that it will work when an attack
actually happens.

BeeDrill turns that assumption into a repeatable test:

```text
Define
→ Isolate
→ Attack
→ Detect
→ Contain
→ Measure
→ Verdict
→ Replay
```

The goal is the security equivalent of regression testing:

```text
application change
→ unit / integration tests
→ PASS / FAIL

security-sensitive change
→ BeeDrill
→ security regression test
→ PASS / FAIL
```

## Current status

The MVP loop is implemented end to end:

```text
Define → Isolate → Attack → Detect → Contain → Measure → Verdict → Replay
```

The supported replays each run a broken and fixed condition from fresh isolated
state. The fixed phase is evaluated from validated evidence; host completion
alone is not a verdict.

| Replay                                 | Verified behavior                                                                                        |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `reference_target_containment_replay`  | Broken state permits a second withdrawal and fails; fixed containment rejects it and passes.             |
| `reference_oracle_manipulation_replay` | Broken state permits a second borrow and fails; fixed containment blocks it and passes.                  |
| `spl_token_freeze_containment_replay`  | Broken state permits a second SPL transfer and fails; freezing the target account rejects it and passes. |

The SPL Token replay is the external proof. It validates one canonical SPL
Token freeze-containment pattern in an isolated host-owned environment; it does
not claim arbitrary Solana protocol support, generic adapter coverage, or
production/mainnet safety. A bounded fresh result is at
[`docs/evidence/spl_token_freeze_containment_replay.example.json`](docs/evidence/spl_token_freeze_containment_replay.example.json).

BeeDrill remains `READ_ONLY`.

Execution, Surfpool lifecycle, RPC access, policy, timeouts, cleanup, and
credentials remain owned by BeeAgent.

Production/mainnet mutation is out of scope.

## Product thesis

BeeDrill is built around one core property:

```text
same attack
+ same starting state
+ different defensive condition
→ measurable security outcome
```

The target product proof is:

```text
BROKEN DEFENSE

same attack
→ detection
→ containment fails
→ higher residual loss
→ FAIL
```

Then:

```text
FIX DEFENSE
```

And replay:

```text
same attack
→ detection
→ containment succeeds
→ lower residual loss
→ PASS
```

The defense changes.

The attack does not.

That is the regression.

## What BeeDrill measures

BeeDrill is designed around objective evidence rather than subjective security
scores.

### Detection

Did the expected technical detector actually observe the attack?

### MTTD

```text
MTTD slots = first_detection_slot - attack_start_slot
```

MTTD is an integer Solana-slot metric and does not imply a wall-clock duration.

### Containment

Did the expected defensive control actually stop or limit the attack?

### MTTC

```text
MTTC slots = first_containment_slot - first_detection_slot
```

MTTC is an integer Solana-slot metric and does not imply a wall-clock duration.

### Economic outcome

How much damage occurred before and after the tested controls acted?

Expected metrics include:

```text
gross attack loss
residual loss
capital saved
```

### Verdict

Critical PASS / FAIL behavior is deterministic:

```text
same validated evidence
→ same metrics
→ same verdict
```

The target result is structured evidence such as:

```text
Attack executed          PASS
Detection                PASS
Containment              FAIL
MTTD                      4 slots
MTTC                      unavailable
Residual loss             480,000 units
Final verdict             FAIL
```

Not:

```text
Security score: 82/100
```

## Architecture

BeeDrill is a security/domain module hosted by BeeAgent.

```text
                   BeeSDK
             shared contracts
                  ↑     ↑
                  │     │
             BeeDrill   BeeAgent
             domain     host/runtime
                │          │
                └──────────┘
                 capability
                  boundary
```

Another way to read the boundary:

```text
BeeDrill
  what should be tested
  scenario semantics
  evidence validation
  metrics
  verdict

BeeAgent
  how bounded execution happens
  Surfpool
  Solana RPC
  process lifecycle
  execution authority
  timeouts
  cleanup

BeeSDK
  reusable shared contracts only
```

### BeeDrill owns

- drill semantics;
- scenario definitions;
- attack expectations;
- detector expectations;
- containment expectations;
- evidence validation;
- MTTD / MTTC semantics;
- economic metrics;
- deterministic verdicts;
- regression scenarios;
- BeeDrill-specific reporting.

### BeeAgent owns

- orchestration;
- module loading;
- runtime/session state;
- execution authority;
- Surfpool lifecycle;
- subprocess lifecycle;
- Solana RPC access;
- credentials;
- policy;
- timeouts;
- cleanup;
- storage and artifact implementation;
- external execution and egress.

### BeeSDK owns

Only reusable shared contracts used across Bee consumers.

BeeSDK does not own:

- BeeDrill scenarios;
- Solana attack semantics;
- detector semantics;
- containment semantics;
- BeeDrill metrics;
- BeeDrill verdict rules.

## Execution model

BeeDrill describes **what should be tested**.

BeeAgent controls **how execution is allowed to happen**.

```text
BeeDrill scenario
→ bounded capability request
→ BeeAgent authority / policy
→ isolated Solana execution
→ bounded evidence
→ BeeDrill validation
→ metrics
→ deterministic verdict
```

A BeeDrill scenario is not an unrestricted execution script.

Scenario-controlled input must not grant:

- arbitrary subprocess execution;
- arbitrary filesystem access;
- arbitrary RPC destinations;
- arbitrary executables or argv;
- arbitrary transactions;
- production credentials;
- runtime authority;
- host policy overrides.

## Reference scenario

The current reference target is a deliberately bounded vulnerable Solana vault.

It provides a reproducible environment for validating:

```text
known initial state
→ real economic attack
→ observable vault outflow
→ independent detection
→ future containment
→ measurable economic result
```

The current detector observes the fixed:

```text
vault_outflow_signal
```

Successful detection evidence includes:

```text
detector identity
signal identity
attack-start slot
first-detection slot
detection status
```

For an observed detection:

```text
first_detection_slot >= attack_start_slot
```

Malformed, incomplete, contradictory, or unexpected evidence is rejected
fail-closed.

## Evidence model

BeeDrill treats evidence as structured input to deterministic evaluation.

Examples:

```text
attack started
attack executed
target state changed
detector observed attack
containment executed
economic loss measured
```

Important distinction:

```text
evidence != authority
result != approval
scenario != runtime identity
```

Missing critical evidence must never silently become PASS.

## Isolation and safety

The current MVP executes only against explicitly approved isolated Solana
environments.

Invariant:

```text
production/mainnet mutation = prohibited
```

BeeDrill must never silently fall back from an isolated environment to a
production target.

Other core invariants:

```text
host-owned execution authority
bounded targets
bounded RPC
bounded subprocess execution
scenario input is untrusted
evidence is not authority
critical verdicts are deterministic
cleanup is required
production secrets are excluded
```

## AI boundary

AI may assist with:

- scenario authoring;
- explanation;
- summaries;
- remediation suggestions.

AI must not determine critical security truth.

In particular, AI does not decide:

- whether detection occurred;
- whether containment occurred;
- MTTD;
- MTTC;
- economic loss;
- final PASS / FAIL.

Those outcomes are derived from validated machine evidence.

## Product boundary

BeeDrill is focused on **continuous security-control validation**.

It is not primarily:

- a vulnerability scanner;
- a generic AI pentester;
- a generic blockchain simulator;
- a SIEM;
- a SOC platform;
- an incident-response chatbot;
- a multi-chain security framework.

The current MVP is deliberately Solana-first.

## Roadmap

Current product path:

```text
Define
→ Isolate
→ Attack
→ Detect
→ Contain
→ Measure
→ Verdict
→ Replay
```

### Working now

```text
Define
Isolate
Attack
Detect
Contain
Measure
Verdict
Replay
```

The scope is frozen for submission: no additional scenario, protocol, control,
runtime, UI, or AI verdict capability is implied by this repository state.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the complete delivery plan and
iteration contracts.

## Development

Requirements:

- Python 3.14+
- `uv`
- Git

Install:

```bash
uv sync
```

Run tests:

```bash
uv run pytest -q
```

Build:

```bash
uv build
```

Import smoke:

```bash
uv run python -c "import beedrill; print(beedrill.__file__)"
```

Show dependencies:

```bash
uv tree
```

For a clean workspace, compatible sibling repositories, tool prerequisites,
regression commands, and artifact locations are in
[`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md). The evidence map, submission copy,
and 60–90 second demo/pitch scripts are in
[`docs/SUBMISSION.md`](docs/SUBMISSION.md).

Do not run or require:

```text
uv lock --check
```

## Development workflow

Significant changes follow:

```text
ROADMAP
→ planning
→ Issue
→ branch
→ implementation
→ tests
→ independent verification
→ final review
→ PR
→ merge
```

Repository-wide development rules are defined in
[`AGENTS.md`](AGENTS.md).

## Documentation

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — delivery plan and iteration contracts
- [`docs/SPEC.md`](docs/SPEC.md) — product and domain specification
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — ownership and architecture boundaries
- [`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md) — local development and integration
- [`docs/SDLC.md`](docs/SDLC.md) — development workflow and change levels
- [`docs/SECURITY.md`](docs/SECURITY.md) — trust, authority and execution boundaries
- [`AGENTS.md`](AGENTS.md) — repository guidance for development agents

## KISS

BeeDrill should prove the product before building a platform.

Current priority:

```text
real attack
→ real detection
→ real containment
→ objective evidence
→ deterministic verdict
→ reproducible replay
```

Not:

```text
framework
→ abstractions
→ large UI
→ multi-chain support
→ eventually attempt product proof
```

## Goal

BeeDrill succeeds when a protocol team can repeatedly answer:

> Under this reproducible attack, did our real defenses detect the attack,
> contain it, and limit economic damage?

with machine-verifiable evidence rather than assumption.
