# SDLC — BeeDrill

## Purpose

This document defines the lightweight software delivery lifecycle used in
`beedrill`.

The process exists to:

- keep product scope focused;
- preserve BeeDrill/BeeAgent/BeeSDK ownership;
- keep security drills reproducible;
- prevent accidental execution-authority expansion;
- preserve deterministic verdict behavior;
- keep releases reviewable;
- avoid unnecessary process overhead.

BeeDrill uses two delivery paths:

```text
low-risk maintenance
→ check
→ main
```

and:

```text
significant product/runtime/security change
→ ROADMAP / Issue
→ branch
→ implementation
→ tests
→ verification
→ review
→ PR
→ merge
→ release process
```

GitHub Project/Kanban is not required by this repository.

## Sources of truth

Documents divide responsibility as follows:

- `docs/ROADMAP.md` — product delivery sequence;
- `docs/SPEC.md` — BeeDrill product/domain contract;
- `docs/ARCHITECTURE.md` — repository and runtime ownership;
- approved Issue — exact significant-task contract;
- PR — actual delivered implementation and verification evidence;
- `docs/SDLC.md` — delivery process;
- `docs/SECURITY.md` — security/trust requirements;
- `docs/DEV_GUIDE.md` — development usage;
- `pyproject.toml` — package metadata, dependencies and package version.

## Core principles

Development follows these rules:

- KISS;
- small coherent increments;
- evidence before abstraction;
- deterministic security outcomes;
- host-owned execution authority;
- isolated attack execution;
- explicit repository ownership;
- no hidden second runtime;
- minimal dependency surface;
- verification proportional to actual risk;
- no manual version bump in ordinary feature/fix work.

## Delivery paths

### Path A — low-risk direct maintenance

Direct `main` may be acceptable for obviously low-risk changes such as:

- typo or wording fixes;
- small documentation alignment;
- test-only cleanup with no behavior change;
- formatting;
- minor repository housekeeping.

Issue and PR may be optional.

Conditions:

- no product behavior change;
- no public/module contract change;
- no scenario/evidence/verdict semantics change;
- no dependency change;
- no BeeAgent/BeeSDK compatibility change;
- no execution, RPC or authority impact;
- no release behavior change;
- change is easy to verify locally.

Run applicable checks before commit.

### Path B — significant change

Use Issue → branch → PR when a task affects:

- product behavior;
- scenario semantics;
- evidence contracts;
- metrics;
- verdicts;
- module/public API;
- package/build behavior;
- BeeAgent integration;
- BeeSDK compatibility;
- runtime dependency surface;
- Solana RPC integration;
- Surfpool execution;
- detector integration;
- containment integration;
- authority/trust boundary;
- release mechanics.

Direct `main` should not be the default path for these changes.

## ROADMAP

`docs/ROADMAP.md` contains coherent BeeDrill delivery increments.

A numbered iteration should define:

- Goal;
- Scope;
- Excluded;
- Deliverable;
- Acceptance criteria;
- Checks;
- DoD.

Do not create roadmap iterations for:

- typos;
- small docs corrections;
- trivial test cleanup;
- unrelated housekeeping.

Completed iteration history should remain stable.

## Issue

Significant tasks should use:

```text
.github/ISSUE_TEMPLATE/issue.md
```

The Issue defines:

- current limitation;
- why now;
- Scope;
- Excluded;
- Deliverable;
- Acceptance Criteria;
- change level;
- product/contract impact;
- dependency impact;
- security impact;
- required checks.

One implementation repository should normally have one Issue.

Cross-repository implementation should use separate Issues in the owning
repositories.

## Branch

Use a dedicated branch for significant work.

Recommended forms:

```text
feature/<short-name>
fix/<short-name>
docs/<short-name>
chore/<short-name>
test/<short-name>
```

For roadmap iterations, retaining the iteration identity is useful:

```text
feature/bd-4-surfpool-host-execution
feature/bd-9-deterministic-verdicts
```

`main` should remain stable.

## Code

Implementation rules:

- stay inside approved scope;
- reuse existing implementation;
- preserve architecture ownership;
- do not redesign unrelated code;
- do not introduce speculative frameworks;
- do not create generic multi-chain abstractions during the Solana MVP;
- do not move BeeAgent runtime responsibilities into BeeDrill;
- do not move BeeDrill domain semantics into BeeSDK;
- do not add dependencies without approved need;
- do not change version manually;
- preserve deterministic behavior where required.

## Tests

Default test command:

```bash
uv run pytest -q
```

Package/build changes additionally run:

```bash
uv build
```

Import smoke when applicable:

```bash
uv run python -c "import beedrill; print(beedrill.__file__)"
```

Scenario, evidence, metrics and verdict changes should include targeted tests.

Security-sensitive execution changes should include negative behavior tests.

## Runtime evidence

Some BeeDrill iterations require runtime/integration evidence in addition to
unit tests.

Examples:

- isolated Solana execution;
- detector observation;
- containment observation;
- timeout behavior;
- cleanup behavior;
- replay;
- residual-loss calculation.

Runtime evidence must be bounded and reproducible enough to support the
Acceptance Criteria.

## Artifacts

BeeDrill does not own a standalone runtime storage hierarchy.

Relevant outputs may include:

- tests;
- fixtures;
- structured evidence;
- structured drill reports;
- package build outputs;
- integration evidence.

Host-persisted production artifacts remain owned by BeeAgent.

Generated build outputs are verification evidence and normally are not
committed.

## Pull Request

A significant PR should explain:

- Summary;
- related Issue;
- iteration;
- Scope;
- actual Changes;
- package/public/contract impact;
- verification;
- security review;
- dependency/version decision;
- limitations/follow-ups.

The PR is the primary delivery evidence for significant work.

## Merge

A significant task is ready to merge when:

- Acceptance Criteria are satisfied;
- implementation matches repository ownership;
- required tests pass;
- required runtime/integration smoke passes;
- deterministic behavior is verified where applicable;
- security checks are complete;
- docs match actual behavior;
- no unintended dependency or version change exists;
- final review has no blocking findings.

## Change levels

Use only three levels:

```text
low-risk
runtime-risk
security-sensitive
```

### low-risk

Examples:

- docs;
- test-only additions;
- formatting;
- internal cleanup with no product/public impact;
- prompt/skill maintenance that does not change runtime behavior.

Usually required:

- relevant targeted check;
- full tests only when code or test infrastructure warrants them.

Issue/PR may be skipped when truly trivial.

### runtime-risk

Examples:

- scenario-domain behavior;
- evidence validation;
- deterministic metrics;
- verdict behavior;
- package/public API changes;
- module integration changes without new authority;
- fixture/replay behavior;
- artifact/report shape changes;
- compatible BeeSDK/BeeAgent integration changes.

Usually required:

```text
targeted tests
uv run pytest -q
uv build when package/public metadata is affected
import smoke when package surface is affected
integration compatibility smoke when relevant
deterministic/replay checks when relevant
```

### security-sensitive

Examples:

- subprocess/process execution;
- Surfpool lifecycle integration;
- Solana RPC execution or RPC target selection;
- scenario input influencing execution;
- filesystem/path handling;
- private keys or credentials;
- authority semantics;
- host policy boundary;
- detector or containment execution with external side effects;
- serialization/parsing of security-sensitive untrusted input;
- runtime dependency addition;
- external network egress.

Usually required:

- applicable runtime-risk checks;
- explicit security review;
- SAST;
- SCA when dependencies changed;
- negative/adversarial tests;
- bounded target tests;
- timeout/cleanup tests when execution is involved;
- secret-leak review when credentials are involved.

DAST, IAST and fuzzing are used only when the actual surface justifies them.

## Security-aware check selection

Do not run every security technique for every PR.

### SAST

Expected for security-sensitive code and useful for code-heavy changes such as:

- execution boundaries;
- scenario validation influencing execution;
- evidence parsers;
- authority logic;
- path handling;
- non-trivial validation.

Look for:

- arbitrary execution;
- unsafe target selection;
- authority escalation;
- hidden I/O;
- unsafe path handling;
- secret exposure;
- ownership bypass.

### SCA

Expected when dependency surface changes.

Review:

```text
pyproject.toml
uv.lock
```

Check:

- necessity;
- direct dependencies;
- transitive dependencies;
- known vulnerabilities;
- maintenance impact.

### DAST

Use only when the actual change creates or modifies a meaningful externally
reachable runtime surface.

Do not require DAST for pure domain logic.

### IAST

Not a default requirement.

Use only when a security-sensitive instrumentable runtime path exists.

### Fuzzing

Consider when BeeDrill introduces:

- non-trivial parser;
- serializer/deserializer;
- structured untrusted-input validator;
- complex normalization of attacker-controlled data.

Simple dataclasses or deterministic arithmetic do not automatically require
fuzzing.

## Deterministic behavior checks

When a change affects critical verdict semantics, verify:

```text
same valid evidence
→ same metrics
→ same verdict
```

When replay is part of the task, verify equivalent starting state and equivalent
scenario produce equivalent security meaning.

## Isolation checks

For attack execution, verify as applicable:

```text
approved isolated target
→ allowed

forbidden or production target
→ refused
```

Production/mainnet mutation is outside the current MVP.

## Fail-closed checks

When critical evidence is required, test relevant cases such as:

- missing evidence;
- malformed evidence;
- contradictory evidence;
- failed detector observation;
- failed containment observation.

These cases must not silently produce PASS.

## Cross-repository changes

Use:

```text
one implementation repository
= one Issue
= one target worktree
= one branch
= one PR
```

Typical ownership:

```text
BeeDrill scenario/verdict behavior
→ beedrill

host execution/RPC/Surfpool lifecycle
→ beeagent

shared reusable contract
→ beesdk
```

Do not hide a BeeAgent implementation inside a BeeDrill PR.

## Dependency rules

Dependencies must be minimal.

Any new runtime dependency requires an approved Issue.

For security-sensitive dependency changes:

- explain why existing stdlib/current dependencies are insufficient;
- explain why the dependency belongs in BeeDrill;
- update `pyproject.toml`;
- update `uv.lock`;
- run SCA;
- verify package build.

Do not run or require:

```text
uv lock --check
```

## Versioning

BeeDrill uses SemVer.

Version source of truth:

```text
pyproject.toml
```

Ordinary feature/fix PR:

```text
do not manually edit version
```

Release automation uses Conventional Commits and release-please.

Typical mapping:

```text
feat:          additive product capability
fix:           compatible defect correction
docs:          no product release intent by itself
test:          no product release intent by itself
refactor:      no intended behavior change
chore:         maintenance
ci:            CI
build:         build tooling
feat!:         breaking change
BREAKING CHANGE: breaking change
```

Release-please owns release PR/version/changelog/tag lifecycle.

## CHANGELOG

`CHANGELOG.md` is release history.

It is not an implementation diary.

Do not manually append entries for every local change unless the release process
explicitly requires it.

## ROADMAP update rules

Update `docs/ROADMAP.md` when:

- iteration status changes;
- iteration contract changes;
- product direction changes;
- significant scope is added or removed;
- sequencing materially changes.

Do not update ROADMAP for tiny implementation details.

## Documentation update rules

Check relevant documentation when one of these changes:

- product contract;
- scenario semantics;
- evidence contract;
- metrics/verdict semantics;
- architecture boundary;
- security/trust boundary;
- BeeAgent/BeeSDK integration;
- dependency rules;
- development/release flow.

Do not touch every document mechanically.

## Definition of Done

For significant BeeDrill work:

- implementation matches the approved Issue;
- repository ownership is correct;
- targeted tests exist;
- `uv run pytest -q` passes;
- `uv build` passes when applicable;
- import smoke passes when applicable;
- deterministic behavior is verified when applicable;
- runtime/integration evidence exists when required;
- required security checks are complete;
- dependency changes are intentional;
- docs reflect actual behavior;
- package version was not manually changed unless the task is release-related;
- PR contains sufficient verification evidence;
- final review has no blockers.

For low-risk direct maintenance:

- the change is truly low-risk;
- applicable checks pass;
- no hidden product/security/dependency/release impact exists.

## KISS process rule

Do not require:

- an Issue for a typo;
- a PR for every one-line docs correction;
- the full security suite for contract-neutral work;
- runtime smoke for a docs-only task;
- a roadmap iteration for housekeeping.

Do require stronger process when BeeDrill's core guarantees are changing:

```text
execution isolation
authority
scenario semantics
evidence integrity
deterministic verdict
dependencies
```

## Summary

BeeDrill SDLC exists to prevent expensive failures such as:

```text
attack path escapes isolation
scenario gains execution authority
evidence produces a false PASS
host/domain ownership becomes duplicated
replay becomes non-deterministic
dependency surface drifts accidentally
```

The process should remain proportional to those risks.
