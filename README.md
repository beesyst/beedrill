# BeeDrill — Continuous Security Control Validation for Solana

**BeeDrill** is a Solana-first security regression testing product that verifies
whether real technical defenses detect and contain reproducible attacks before
those defenses are needed during a real incident.

> **Audits test your code. BeeDrill tests your defenses.**

BeeDrill does not primarily ask:

> Can this protocol contain a vulnerability?

It asks:

> If an attack starts now, will the configured detector, circuit breaker and
> containment controls actually protect capital?

## Core idea

Security controls are often present without being continuously validated.

A protocol may already have:

- monitoring;
- alerts;
- anomaly detection;
- circuit breakers;
- pause mechanisms;
- authority configuration;
- emergency controls.

Their existence does not prove that they work together correctly.

BeeDrill validates the complete control path:

```text
current protocol state
→ isolated Solana environment
→ reproducible attack
→ detection observation
→ containment observation
→ economic outcome measurement
→ deterministic PASS / FAIL
```

The target workflow is analogous to application regression testing:

```text
application change
→ unit/integration tests
→ PASS / FAIL

security-sensitive change
→ BeeDrill
→ security regression tests
→ PASS / FAIL
```

## What BeeDrill measures

BeeDrill is designed around objective evidence rather than subjective security
scores.

Core metrics include:

### Detection

Did the expected technical detector actually observe the attack?

### MTTD

Time from attack start to validated detection.

```text
attack start
→ detector signal
= MTTD
```

### Containment

Did the expected defensive control actually stop or limit the attack?

### MTTC

Time required to reach validated containment according to the scenario contract.

### Residual capital loss

How much economic damage remained after the tested controls acted?

The goal is to produce evidence such as:

```text
Attack executed          PASS
Detection                PASS
Containment              FAIL
MTTD                      4.2 s
MTTC                      unavailable
Residual loss             480,000 units
Final verdict             FAIL
```

rather than:

```text
Security score: 82/100
```

## Target demo

The central BeeDrill product proof is a reproducible FAIL → fix → PASS replay.

### Broken defense

```text
attack
→ detector fires
→ containment requested
→ defensive authority/configuration is wrong
→ containment fails
→ high residual loss
→ FAIL
```

### Fixed defense

The defensive configuration is corrected.

The attack scenario remains the same.

```text
same attack
→ detector fires
→ containment succeeds
→ substantially lower residual loss
→ PASS
```

This demonstrates a security property that a code audit alone cannot prove:

> A defensive control may exist while being operationally unable to protect the
> protocol during an attack.

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

## Architecture

BeeDrill is a domain/security module rather than an independent execution
runtime.

```text
BeeSDK
  shared contracts
      ↑
BeeAgent
  host / runtime / orchestration / execution
      ↑
BeeDrill
  scenarios / evidence / metrics / verdicts
```

### BeeDrill owns

- drill-specific domain semantics;
- scenario semantics;
- attack expectations;
- expected detector behavior;
- expected containment behavior;
- evidence validation;
- MTTD / MTTC semantics;
- economic outcome metrics;
- deterministic verdicts;
- security regression scenarios;
- BeeDrill-specific reporting.

### BeeAgent owns

- orchestration;
- module loading;
- runtime/session state;
- execution authority;
- process lifecycle;
- Surfpool lifecycle;
- Solana RPC access;
- credentials;
- policy;
- timeouts;
- cleanup;
- storage and artifact implementation;
- external execution and egress.

### BeeSDK owns

Only reusable shared contracts proven to be common across Bee consumers.

BeeDrill-specific Solana scenarios, attacks, evidence semantics, metrics and
verdicts remain in BeeDrill.

## Execution model

BeeDrill describes **what should be tested**.

BeeAgent controls **how execution is allowed to happen**.

Correct flow:

```text
BeeDrill scenario
→ bounded execution intent
→ BeeAgent policy / authority
→ approved isolated Solana environment
→ execution evidence
→ BeeDrill evaluation
→ deterministic verdict
```

A BeeDrill scenario is not an unrestricted execution script.

Scenario-controlled input must not grant:

- arbitrary subprocess execution;
- arbitrary filesystem access;
- arbitrary RPC destinations;
- production credentials;
- runtime authority;
- host policy overrides.

## Isolation

The hackathon MVP uses explicitly approved isolated Solana environments.

Current invariant:

```text
production/mainnet mutation = out of scope
```

BeeDrill must never silently fall back from an isolated environment to a
production target.

## Deterministic verdicts

Critical PASS / FAIL behavior must be deterministic.

```text
same valid evidence
→ same metrics
→ same verdict
```

AI may assist with:

- explanation;
- scenario authoring;
- result summaries;
- remediation suggestions.

AI must not determine the final critical security verdict.

## Evidence model

BeeDrill evaluates structured evidence such as:

```text
attack started
attack executed
detector observed attack
containment executed
relevant state changed
economic loss measured
```

Important distinction:

```text
evidence != authority
result != approval
scenario != runtime identity
```

Missing, malformed or contradictory critical evidence must not silently produce
PASS.

## Current status

The repository currently contains the initial BeeDrill bootstrap baseline.

Implemented:

- standalone `beedrill` Python package;
- Python `>=3.14`;
- `uv` development environment;
- `src` package layout;
- minimal `BeeDrillModule`;
- stable module identity:
  - `module_id = "beedrill"`;
- initial authority:
  - `read_only`;
- repository architecture and product documentation;
- security and SDLC rules;
- project-local planning/implementation/review workflows;
- Issue and Pull Request templates;
- release-please configuration;
- package/import bootstrap tests;
- package build baseline.

Current module foundation intentionally has no:

- Solana RPC execution;
- Surfpool execution;
- subprocess execution;
- attack implementation;
- detector integration;
- containment integration;
- verdict engine;
- production/mainnet access.

The next integration milestone is to connect BeeDrill to the approved BeeSDK
module contract and verify normal BeeAgent module loading/invocation.

## Roadmap

The hackathon implementation plan contains 15 focused iterations.

### Stage 1 — Foundation

```text
BD-1 Repository architecture and governance
BD-2 BeeSDK module contract and BeeAgent load smoke
BD-3 Drill domain contracts and fixture baseline
```

### Stage 2 — End-to-end falsification prototype

```text
BD-4 Surfpool host-execution integration
BD-5 Reference vulnerable protocol and reproducible state
BD-6 First real attack scenario
BD-7 Detection observation
BD-8 Containment and FAIL → PASS replay
```

### Stage 3 — Metrics and regression product

```text
BD-9  Deterministic security metrics and verdict engine
BD-10 Oracle manipulation scenario
BD-11 Broken authority / containment scenario
BD-12 Reproducible regression suite and CI entry point
```

### Stage 4 — Hardening and validation

```text
BD-13 Execution safety and fail-closed hardening
BD-14 Real integration and product evidence
BD-15 Hackathon demo and submission readiness
```

Planned core implementation window:

```text
2026-09-15
→
2026-10-04
```

Submission/hardening buffer:

```text
2026-10-05
→
2026-10-12
```

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the complete iteration contracts.

## Development

Requirements:

- Python 3.14+
- `uv`
- Git

Install the development environment:

```bash
uv sync
```

Run tests:

```bash
uv run pytest -q
```

Build the package:

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

Do not run or require:

```text
uv lock --check
```

## Repository structure

Current bootstrap structure:

```text
beedrill/
├── .agents/
│   ├── prompts/
│   └── skills/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE/
│   ├── release-please/
│   └── workflows/
├── docs/
│   ├── ROADMAP.md
│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   ├── SDLC.md
│   ├── SECURITY.md
│   └── DEV_GUIDE.md
├── src/
│   └── beedrill/
│       ├── __init__.py
│       └── module.py
├── tests/
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── pyproject.toml
└── uv.lock
```

Additional implementation layers are introduced only when a roadmap iteration
demonstrates a concrete need.

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

Repository-wide rules are defined in [`AGENTS.md`](AGENTS.md).

## Security principles

The current MVP preserves these invariants:

```text
isolated execution
host-owned authority
bounded targets
bounded execution
scenario input is untrusted
evidence is not authority
critical verdicts are deterministic
missing critical evidence cannot PASS
production/mainnet mutation is excluded
```

See [`docs/SECURITY.md`](docs/SECURITY.md) for the complete security contract.

## Documentation

- [`docs/ROADMAP.md`](docs/ROADMAP.md) — delivery plan and iteration contracts
- [`docs/SPEC.md`](docs/SPEC.md) — product/domain specification
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — ownership and architecture boundaries
- [`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md) — local development and integration
- [`docs/SDLC.md`](docs/SDLC.md) — delivery workflow and change levels
- [`docs/SECURITY.md`](docs/SECURITY.md) — trust, authority and execution boundaries
- [`AGENTS.md`](AGENTS.md) — repository guidance for development agents

## KISS rule

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

## Product thesis

BeeDrill succeeds when a protocol team can repeatedly answer:

> Under this reproducible attack, did our real defenses detect the attack,
> contain it, and limit economic damage?

with machine-verifiable evidence rather than assumption.
