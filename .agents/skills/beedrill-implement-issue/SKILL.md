---
name: beedrill-implement-issue
description: Implement one approved BeeDrill Issue in the exact target worktree and return complete implementation and verification evidence.
---

# BeeDrill approved Issue implementation workflow

## Purpose

Use this workflow after a BeeDrill Issue has been approved and a dedicated
target worktree and branch have been prepared.

This workflow may modify the target repository and run local checks.

Do not:

- work outside the approved Issue;
- perform unrelated refactoring or cleanup;
- create speculative abstractions;
- expand BeeDrill into a second BeeAgent runtime;
- move BeeAgent-owned execution into BeeDrill for implementation convenience;
- move BeeDrill domain semantics into BeeSDK;
- create production/mainnet mutation paths unless an approved future Issue
  explicitly changes that boundary;
- commit, push, create a PR or merge;
- change package version unless the Issue is explicitly release-related.

## Required inputs

Obtain:

- project;
- exact target worktree;
- expected branch;
- base branch;
- approved Issue or normalized approved task contract;
- Issue source when supplied;
- roadmap context;
- planning constraints;
- related repository contracts when explicitly supplied;
- additional implementation targets only when the approved Issue explicitly
  requires cross-repository work.

## Working contract

Before proposing or applying a change, read every declared file completely.

Keep a file inventory. When another file becomes necessary, add it to the
inventory and read it completely before editing it.

Map the work to the supplied current roadmap iteration and stay inside its
approved scope.

Before editing, determine:

```text
low-risk
runtime-risk
security-sensitive
```

Then derive required checks from:

- `docs/SDLC.md`;
- `docs/SECURITY.md`.

Make the smallest complete KISS change.

Do not:

- refactor unrelated code;
- run formatters over unrelated content;
- remove an existing check without an explicit task-specific reason;
- add speculative framework layers;
- create abstractions for future chains, protocols, runners or integrations
  without current evidence;
- add first-party production/test comments, explanatory docstrings, `TODO`,
  `FIXME`, `NOTE` or decorative separators unless the repository explicitly
  requires them.

Preserve required:

- license annotations;
- provenance annotations;
- security annotations;
- unrelated existing comments.

Use proportional tests for Acceptance Criteria and public behavior.

Prefer existing test files and helpers.

Create a new file, helper, model or abstraction only when demonstrably required
by the approved task.

Keep ownership explicit:

```text
BeeDrill
→ scenario semantics
→ target/domain semantics
→ expected controls
→ evidence validation
→ metrics
→ deterministic verdicts
→ BeeDrill-specific reporting

BeeAgent
→ runtime
→ orchestration
→ module loading
→ process execution
→ Surfpool lifecycle
→ Solana RPC access
→ credentials
→ authority
→ policy
→ timeouts
→ host storage/artifact implementation
→ external execution and egress

BeeSDK
→ proven reusable shared contracts only
```

If implementation evidence shows that required behavior belongs to another
repository, do not copy that responsibility into BeeDrill.

Report the ownership gap unless the approved Issue explicitly includes the
other repository as an implementation target.

Before reporting completion, inspect the final diff and remove every newly
introduced prohibited comment, unrelated formatting change and out-of-scope
change.

## Target safety gate

Before changing files:

1. verify the current working directory;
2. verify the current branch;
3. inspect `git status`;
4. verify that the worktree matches the requested target;
5. identify pre-existing staged, unstaged and untracked changes;
6. identify whether any pre-existing change overlaps the approved Issue.

Stop when:

- the path differs from the requested target;
- the branch differs from the expected branch;
- unrelated pre-existing changes make safe attribution impossible;
- the approved Issue materially conflicts with `AGENTS.md`;
- the approved Issue materially conflicts with current repository contracts;
- the task requires an unapproved cross-repository change;
- the task requires weakening an explicit execution or security boundary.

Do not silently:

- switch branches;
- substitute another worktree;
- discard existing work;
- absorb unrelated dirty changes into the task.

## Required reading

Read before implementation:

- `AGENTS.md`;
- the approved Issue or normalized approved task contract;
- the relevant `docs/ROADMAP.md` section;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- directly relevant architecture, product contracts, implementation and tests.

Read as applicable:

- `docs/SPEC.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DEV_GUIDE.md`;
- `pyproject.toml`;
- public package exports;
- relevant BeeSDK contracts;
- relevant scenario/evidence/verdict models;
- relevant fixtures;
- relevant integration code.

Read related repository files only when required to verify:

- an existing public contract;
- repository ownership;
- host compatibility;
- cross-repository integration explicitly required by the Issue.

Do not modify a related repository unless the approved Issue explicitly assigns
work to it.

## Change classification

Determine the actual change level:

- `low-risk`;
- `runtime-risk`;
- `security-sensitive`.

Use `docs/SDLC.md` and `docs/SECURITY.md` to derive required checks.

Typical BeeDrill security-sensitive changes include:

- Surfpool/process execution;
- Solana RPC execution;
- RPC target selection;
- filesystem/path handling;
- scenario parsing that influences execution;
- detector integration;
- containment execution;
- credentials or private keys;
- authority semantics;
- network egress;
- subprocess lifecycle;
- execution timeouts;
- dependency additions affecting the execution surface.

If the actual implementation requires a higher change level than the Issue
declares, report the mismatch before continuing.

Do not silently downgrade the change level to reduce required verification.

## Architecture boundary

Preserve the current BeeDrill architecture unless the approved Issue explicitly
changes it.

Canonical boundary:

```text
BeeSDK
→ shared contracts

BeeAgent
→ host runtime and controlled execution

BeeDrill
→ security-control validation domain logic
```

BeeDrill must not become a second runtime.

Do not move into BeeDrill:

- arbitrary process execution;
- generic runtime orchestration;
- unrestricted RPC clients;
- production credential management;
- runtime policy ownership;
- host authority decisions;
- generic artifact/storage implementation;
- generic module registry;
- BeeAgent session/run lifecycle.

Do not move into BeeSDK:

- Solana-specific models;
- BeeDrill scenarios;
- Surfpool behavior;
- attack logic;
- detector semantics;
- containment semantics;
- BeeDrill metrics;
- BeeDrill verdict rules.

When a host capability is required but absent:

```text
BeeDrill evidence
→ identify exact BeeAgent gap
→ implement in BeeAgent only if the approved Issue includes that target
```

Otherwise stop and report the dependency.

## Security invariants

The following invariants apply unless an approved future Issue explicitly
changes them.

### No scenario-controlled authority

Scenario or module-controlled input must not grant or override:

- execution authority;
- runtime identity;
- host policy;
- credentials;
- arbitrary executable selection;
- arbitrary filesystem access;
- arbitrary RPC destination.

### Isolation

Hackathon attack execution must remain restricted to explicitly approved
isolated environments.

Production/mainnet mutation is outside the current MVP boundary.

### Deterministic verdicts

Critical security verdicts must remain deterministic.

The same valid evidence must produce the same result.

Do not make final critical PASS/FAIL depend on:

- LLM confidence;
- prose interpretation;
- undocumented heuristics;
- manual operator preference.

### Evidence is not authority

Execution evidence may inform a verdict.

It must not grant new runtime authority.

### Fail closed

Missing, malformed or inconsistent critical evidence must not silently produce
PASS.

Use explicit:

- failure;
- degraded;
- refused;
- incomplete;

behavior according to the approved contract.

### Secrets

Do not place production credentials, private keys or unrelated secrets in:

- source;
- fixtures;
- logs;
- test output;
- artifacts;
- documentation examples.

## Implementation

Implement the smallest complete solution satisfying Scope and Acceptance
Criteria.

Requirements:

- follow KISS;
- stay inside the current roadmap iteration;
- reuse existing implementation before creating new abstractions;
- preserve BeeDrill/BeeAgent/BeeSDK ownership;
- use existing public contracts and sources of truth;
- do not introduce hidden defaults for required behavior;
- do not create a second source of truth;
- do not duplicate existing contracts or logic;
- do not hardcode values that belong in an existing contract or configuration
  source of truth;
- do not turn fixture data into unrestricted executable instructions;
- preserve deterministic behavior where the product contract requires it;
- preserve fail-closed behavior on security boundaries;
- follow PEP 8;
- keep public identifiers, package metadata, scenario fields and artifacts in
  English;
- preserve compatibility unless the Issue explicitly permits a breaking
  change;
- keep `pyproject.toml.version` unchanged for ordinary feature, fix, docs and
  chore work.

Do not add:

- generic plugin systems;
- generic workflow engines;
- multi-chain abstractions;
- provider frameworks;
- generalized scenario DSLs;
- large UI layers;
- future SaaS infrastructure;

unless they are explicitly required by the approved Issue and current evidence.

## Dependency and lockfile rules

When the approved Issue has no dependency change:

- do not regenerate `uv.lock`;
- do not modify `uv.lock`;
- do not separately validate `uv.lock`;
- do not add dependencies “just in case”.

When the approved Issue explicitly requires a dependency change:

- add only the minimum necessary dependency;
- use the repository's normal dependency workflow;
- inspect the relevant dependency and lockfile diff;
- perform applicable SCA;
- document why the dependency is necessary.

Never run or require:

```text
uv lock --check
```

Do not treat unrelated lockfile noise as an independent task.

## Tests and verification

Add or update only tests proportional to the approved Issue.

Prefer existing test files, fixtures and helpers.

Do not create a new test file or helper unless the required behavior cannot be
covered cleanly in the existing structure.

Run every check required by the actual change level and Acceptance Criteria.

As applicable:

- targeted tests;
- `uv run pytest -q`;
- `uv build`;
- package import smoke;
- public API verification;
- BeeSDK contract compatibility;
- BeeAgent module compatibility smoke;
- deterministic serialization checks;
- deterministic verdict checks;
- fixture/replay tests;
- artifact verification;
- execution smoke;
- Surfpool lifecycle smoke;
- Solana RPC smoke;
- negative target tests;
- timeout tests;
- cleanup tests;
- malformed-input tests;
- forbidden execution tests;
- secret-leak checks;
- SAST;
- SCA;
- DAST;
- IAST;
- fuzzing.

Use `uv run` for Python commands when applicable.

For a security-sensitive execution path, verify negative behavior in addition to
the happy path.

Examples where applicable:

```text
approved isolated target succeeds
forbidden target is refused
timeout is bounded
failed process is cleaned up
missing evidence cannot PASS
malformed scenario is rejected
scenario cannot select arbitrary executable
scenario cannot override authority
```

For deterministic scenario/verdict work, verify replay behavior when required by
the Issue.

Record:

- exact command;
- exit code;
- passed;
- failed;
- skipped;
- relevant warnings.

Do not claim a check passed when it was not executed.

Do not substitute narrative reasoning for required runtime evidence.

## Cross-repository implementation

When the approved Issue explicitly includes multiple repositories:

1. verify the exact worktree and branch for every implementation target;
2. read the owning repository's `AGENTS.md` and applicable skill;
3. preserve repository ownership;
4. make only the changes assigned to that repository;
5. run repository-specific required checks;
6. report verification separately per repository;
7. verify the final integration boundary.

Do not:

- hide several repository implementations inside one BeeDrill change;
- copy host implementation into BeeDrill to avoid a BeeAgent change;
- expand BeeSDK merely to avoid a consumer-local implementation;
- modify an additional repository that was supplied for context only.

## Final diff review

Before reporting completion:

- inspect `git status`;
- inspect the complete final diff;
- inspect untracked files created by the task;
- confirm all changes belong to the approved Issue;
- confirm no required file is missing;
- confirm no unrelated file changed;
- confirm no accidental formatting sweep occurred;
- confirm no prohibited comments or TODOs were introduced;
- confirm no secrets/private keys were introduced;
- confirm dependency and version changes match approved scope;
- confirm security boundaries remain intact.

If the final state differs materially from the approved Issue, report the
difference instead of silently expanding the task.

## Implementation report

Return one report containing:

1. `Target verification`
2. `Files read`
3. `Roadmap / iteration`
4. `Change level`
5. `Required checks`
6. `Sources of truth`
7. `BeeDrill / BeeAgent / BeeSDK boundary`
8. `Changed files`
9. `Acceptance Criteria coverage`
10. `Tests and commands`
11. `Runtime / integration smoke`
12. `Artifacts and evidence`
13. `Determinism / replay`
14. `Public API and compatibility`
15. `Security review`
16. `Dependencies`
17. `Known limitations`
18. `Recommended Conventional Commit`
19. `Version status`

For cross-repository implementation, clearly separate changed files, tests and
evidence by repository.

For every substantive correction made during implementation, describe:

- `File`
- `Before`
- `After`
- `Why`

Do not include a full diff.

Do not claim completion when required Acceptance Criteria or required checks are
still missing.

End with:

```text
version not changed
```

unless the approved Issue explicitly requires release versioning.
