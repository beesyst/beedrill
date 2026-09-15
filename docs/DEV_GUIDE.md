# DEV_GUIDE — BeeDrill development and BeeAgent integration

## Purpose

This document explains:

- how to develop `beedrill`;
- how to use the Python environment through `uv`;
- how to run tests and package checks;
- how to add drill-domain behavior without creating a second runtime;
- how to preserve deterministic security evaluation;
- how to integrate BeeDrill with BeeAgent;
- how to work within the lightweight BeeDrill SDLC;
- how to handle version and release lifecycle.

## Related project docs

Use this document together with:

- `docs/ROADMAP.md` — delivery stages and iteration scope;
- `docs/SPEC.md` — BeeDrill product and domain contract;
- `docs/ARCHITECTURE.md` — ownership and dependency boundaries;
- `docs/SDLC.md` — delivery workflow and change levels;
- `docs/SECURITY.md` — trust, isolation and execution rules.

Rule:

> `DEV_GUIDE` explains how to work on the project. It does not replace the
> product, architecture, security or roadmap contracts.

## Requirements

- Python 3.14+
- `uv`
- Git

## Repository

Primary repository:

```text
/home/bee/Pro/beedrill
```

Python distribution:

```text
beedrill
```

Python import:

```python
import beedrill
```

Module identity:

```text
beedrill
```

## Development setup

From the repository root:

```bash
uv sync
```

Manual `.venv` activation is not required.

Run Python and tool commands through:

```bash
uv run ...
```

## Basic commands

| Task                            | Command                                                        |
| ------------------------------- | -------------------------------------------------------------- |
| install development environment | `uv sync`                                                      |
| run tests                       | `uv run pytest -q`                                             |
| build package                   | `uv build`                                                     |
| package import smoke            | `uv run python -c "import beedrill; print(beedrill.__file__)"` |
| show dependency tree            | `uv tree`                                                      |
| add a dev dependency            | `uv add --dev <pkg>`                                           |
| add a runtime dependency        | only through an approved Issue                                 |
| remove a dependency             | `uv remove <pkg>`                                              |

## Dependency source of truth

Dependency sources of truth:

```text
pyproject.toml
uv.lock
```

Rules:

- keep dependencies minimal;
- add dependencies only for a demonstrated implementation need;
- update `pyproject.toml` and `uv.lock` together when an approved dependency
  change occurs;
- do not run or require `uv lock --check`;
- do not modify dependency surface during unrelated work.

The bootstrap package may start with:

```text
runtime dependencies = []
```

BeeSDK should be added only through an approved and actually available package
source.

Do not invent a BeeSDK version or dependency source.

## Package structure

Initial package structure:

```text
src/beedrill/
├── __init__.py
└── module.py
```

Do not create package directories only for organizational symmetry.

Add a new layer when:

- a current roadmap iteration requires it;
- a coherent domain responsibility has appeared;
- keeping the code flat would make ownership less clear.

Do not precreate generic:

```text
runtime/
execution/
providers/
plugins/
state/
config/
```

layers.

## Development model

BeeDrill is a domain module hosted by BeeAgent.

The development boundary is:

```text
BeeDrill
→ what the drill means

BeeAgent
→ how bounded execution occurs
```

BeeDrill should implement:

- scenario semantics;
- evidence validation;
- metrics;
- verdict rules;
- regression scenarios.

BeeDrill should not implement generic:

- process lifecycle;
- Surfpool lifecycle;
- RPC lifecycle;
- credential management;
- runtime policy;
- module registry;
- host storage.

## Module integration

BeeDrill should use shared BeeSDK contracts when the approved BeeSDK dependency
is available.

Import those contracts only from their explicit public contract modules:

```python
from beesdk.artifacts import ArtifactPort
from beesdk.modules import AuthorityLevel, ModuleContext, ModuleContract, ModuleResult
```

Do not import module or artifact contracts from the top-level `beesdk` package.

Expected module properties include:

```text
module_id = beedrill
authority = read_only
```

The module should remain structurally compatible with the host module contract.

Do not copy BeeAgent or BeeSDK contract classes into BeeDrill.

## Initial authority

The initial module authority is:

```text
read_only
```

This does not mean the overall drill can never cause bounded test execution.

It means the BeeDrill module itself does not receive autonomous execution
authority.

Execution remains host-controlled.

## Adding drill-domain behavior

Before introducing a new domain contract, answer:

```text
Which roadmap iteration requires it?
Which real scenario needs it?
What current gap does it close?
Why does it belong in BeeDrill?
Why does it not belong in BeeAgent?
Why does it not belong in BeeSDK?
Can the requirement be represented by an existing contract?
```

If these questions do not have concrete answers, do not add the abstraction yet.

## Scenario development

A scenario should represent a reproducible security-control test.

Prefer concrete scenarios over a generic scenario framework.

Scenario development should focus on:

```text
initial state
attack condition
expected detection
expected containment
required evidence
expected outcome
```

Scenario data must not be treated as unrestricted execution instructions.

Do not place arbitrary shell commands, arbitrary RPC endpoints or credentials
inside scenario contracts.

## Fixture-driven development

BeeDrill should use fixtures or equivalent deterministic test inputs for
scenario and verdict behavior.

A useful scenario fixture should make this relationship inspectable:

```text
initial state
+ scenario
+ evidence
→ metrics
→ verdict
```

When a rule changes, a regression test or fixture should explain the intended
behavior.

Avoid large synthetic fixture frameworks before real scenarios exist.

## Determinism

Critical verdict behavior must be reproducible.

For deterministic evaluation:

```text
same valid evidence
→ same metrics
→ same verdict
```

Tests should cover this whenever verdict or metric behavior changes.

Do not use AI output as the final source of truth for:

- detection result;
- containment result;
- MTTD;
- MTTC;
- residual loss;
- critical PASS/FAIL.

## Replay development

When an iteration introduces replay behavior, preserve:

- equivalent starting state;
- equivalent scenario;
- equivalent evidence interpretation;
- equivalent verdict semantics.

The goal is not byte-for-byte equality of every runtime timestamp.

The goal is deterministic security meaning.

## BeeAgent integration

BeeAgent is the host/runtime.

BeeAgent owns:

- runtime context;
- module loading;
- execution authority;
- subprocesses;
- Surfpool lifecycle;
- RPC access;
- credentials;
- timeouts;
- cleanup;
- storage;
- artifacts.

BeeDrill integration should use public/shared contracts rather than importing
private BeeAgent implementation details.

If BeeDrill requires a host capability that does not exist:

1. verify that it really belongs to BeeAgent;
2. create a separate BeeAgent task when necessary;
3. implement and verify the host capability there;
4. integrate BeeDrill against the resulting contract.

Do not add the host implementation to BeeDrill as a shortcut.

## Related repository environments

Each repository must be verified in its own environment.

For BeeDrill:

```bash
cd /home/bee/Pro/beedrill
uv sync
uv run pytest -q
uv build
```

Do not use another repository's `.venv` as evidence that BeeDrill works
independently.

Cross-repository integration checks should be run separately in the relevant
repository.

## Surfpool integration

Surfpool is part of the intended isolated Solana execution path.

BeeDrill may define what state or operation the drill requires.

BeeAgent owns the Surfpool runtime lifecycle.

BeeDrill must not add its own generic Surfpool process manager.

Do not invent a BeeDrill-local start/stop command unless a future approved
architecture explicitly gives that responsibility to BeeDrill.

## Solana RPC integration

Solana RPC execution is host-controlled.

BeeDrill should describe bounded drill intent rather than arbitrary endpoint
selection.

When an iteration adds RPC-backed behavior, verify:

- the approved target is isolated;
- the host selects or approves the RPC endpoint;
- scenario input cannot redirect execution to an arbitrary target;
- errors and timeouts are bounded;
- required evidence is collected.

## Evidence development

Evidence contracts should be:

- structured;
- bounded;
- deterministic to interpret;
- independent from execution authority.

When adding evidence:

- identify who produces it;
- identify who validates it;
- identify which metric or verdict consumes it;
- define missing/malformed behavior;
- add negative tests where security-critical.

Do not treat evidence as permission for another action.

## Verdict development

A verdict engine should consume validated evidence.

It should not perform runtime execution.

Conceptually:

```text
validated evidence
→ metrics
→ deterministic rules
→ verdict
```

When changing verdict logic, test:

- expected PASS;
- expected FAIL;
- missing evidence;
- malformed evidence;
- contradictory evidence;
- boundary values when relevant.

## Economic metrics

When an iteration introduces or changes economic metrics, define the formula in
the relevant contract and test it with deterministic values.

Avoid heuristic "risk scores" when the product can measure an objective
economic result instead.

## Tests

Primary command:

```bash
uv run pytest -q
```

### What should be tested in BeeDrill

As applicable:

- package imports;
- module identity;
- module contract compatibility;
- scenario validation;
- fixture behavior;
- evidence validation;
- deterministic metrics;
- deterministic verdicts;
- replay behavior;
- artifact/result shapes;
- malformed inputs;
- missing evidence;
- security boundary behavior;
- host integration contract.

### What is not BeeDrill test ownership

BeeDrill unit tests should not become the primary test suite for:

- BeeAgent orchestration;
- generic process management;
- generic Surfpool lifecycle;
- BeeAgent storage implementation;
- BeeAgent credentials;
- BeeAgent module registry;
- BeeUI rendering;
- BeeScan scanning logic.

Those responsibilities are tested in their owning repositories.

## Package build

When package or public metadata is affected, run:

```bash
uv build
```

Check at minimum:

- wheel is produced;
- source distribution is produced;
- `beedrill` is importable;
- unrelated repository code is not packaged;
- dependency metadata matches `pyproject.toml`.

Generated directories such as:

```text
dist/
build/
*.egg-info/
```

are verification outputs and normally remain ignored.

## Public API

Keep the public API minimal.

Public names should be intentionally exported through:

```text
src/beedrill/__init__.py
```

Do not publish every internal domain helper.

When a public contract changes:

1. identify the source of truth;
2. update targeted tests;
3. evaluate compatibility;
4. update `docs/SPEC.md`;
5. update other affected docs only when their contract changed.

## Docs

When implementation changes, inspect only relevant documentation.

Possible sources include:

```text
README.md
docs/SPEC.md
docs/ARCHITECTURE.md
docs/DEV_GUIDE.md
docs/ROADMAP.md
docs/SDLC.md
docs/SECURITY.md
```

Do not mechanically modify every document.

## Versioning

Current package version source of truth:

```text
pyproject.toml
```

BeeDrill uses SemVer.

Ordinary implementation work must not manually change the version.

Use Conventional Commits.

Typical mapping:

```text
feat:       additive product capability
fix:        compatible defect correction
docs:       documentation only
test:       tests only
refactor:   no intended behavior change
chore:      maintenance
ci:         CI
build:      build tooling
```

Breaking changes use the repository's conventional breaking-change syntax.

Release-please manages release PR/version/changelog/tag lifecycle.

## Contribution flow

For significant work:

```text
ROADMAP
→ Issue
→ feature branch
→ implementation
→ tests
→ independent verification
→ final review
→ PR
→ merge
→ release process when applicable
```

For truly trivial low-risk maintenance, the lighter path defined in
`docs/SDLC.md` may be used.

## What not to do

Do not:

- create a second runtime;
- add arbitrary shell execution;
- add unrestricted RPC access;
- store production credentials;
- create a generic plugin framework;
- build a generic scenario DSL before real need;
- build multi-chain abstractions during the Solana MVP;
- add a large UI before the core drill works end-to-end;
- move BeeAgent responsibilities into BeeDrill;
- move BeeDrill semantics into BeeSDK;
- add dependencies "for later";
- manually bump version in an ordinary task.

## Before a significant PR

Run the checks required by the actual change level.

Typical package baseline:

```bash
uv sync
uv run pytest -q
```

When package/build behavior is affected:

```bash
uv build
```

Also run task-specific checks from:

```text
docs/SDLC.md
docs/SECURITY.md
```

Before PR, the reviewer should be able to answer:

- what product behavior changed;
- which roadmap iteration owns it;
- which repository owns the implementation;
- whether execution authority changed;
- whether isolation changed;
- whether verdict behavior remains deterministic;
- whether dependencies changed;
- which tests and runtime checks were executed;
- which limitations remain.

## Summary

BeeDrill development should remain focused on:

```text
reproducible scenario
bounded evidence
deterministic metrics
deterministic verdict
correct host boundary
```

The repository should not become a second BeeAgent runtime merely to make the
first implementation easier.
