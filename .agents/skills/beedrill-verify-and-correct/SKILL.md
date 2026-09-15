---
name: beedrill-verify-and-correct
description: Independently verify an implemented BeeDrill Issue, apply only necessary in-scope corrections, and return final evidence for read-only review.
---

# BeeDrill verification and correction workflow

## Purpose

Use this workflow after initial implementation or after a read-only final review
has returned blocking findings.

The executor may:

- inspect files;
- modify the exact target worktree;
- run local repository checks.

Use this workflow once for independent post-implementation verification.

Reuse it only to address explicit blocking findings returned by a completed final
review.

Do not:

- expand the approved Issue;
- add optional polish;
- create speculative architecture;
- perform unrelated cleanup;
- create preventive closing patches without a demonstrated blocker;
- move BeeAgent-owned runtime behavior into BeeDrill;
- move BeeDrill-specific domain semantics into BeeSDK;
- weaken execution, isolation or authority boundaries;
- create production/mainnet mutation paths outside explicitly approved future
  scope;
- commit, push, create a PR or merge;
- change package version unless the Issue is explicitly release-related.

## Required inputs

For every run obtain:

- project;
- exact target worktree;
- expected branch;
- base branch;
- related repository contracts when explicitly supplied.

For initial independent verification also obtain:

- approved Issue or normalized approved task contract;
- roadmap context;
- planning constraints.

For a correction run also obtain:

- explicit blocking findings from the completed final review.

Do not require:

- implementation report;
- previous verification report;
- previous executor conclusions.

The current target worktree is authoritative.

## Working contract

Before proposing or applying a change, read every declared file completely.

Keep a file inventory.

When another file becomes necessary:

1. add it to the inventory;
2. read it completely;
3. only then edit or evaluate it.

For initial verification:

- map the work to the supplied roadmap context;
- map the work to the approved task contract;
- verify the actual implementation independently.

For a correction run:

- treat the supplied final-review blockers as the complete correction scope;
- do not require the full planning discussion;
- do not reopen already reviewed unrelated scope;
- verify affected Acceptance Criteria and regression risk.

Before editing, determine the actual change level:

```text
low-risk
runtime-risk
security-sensitive
```

Then derive required checks from:

- `docs/SDLC.md`;
- `docs/SECURITY.md`.

Make the smallest complete KISS correction.

Do not:

- refactor unrelated code;
- run formatters over unrelated content;
- remove an existing check without an explicit task-specific reason;
- introduce abstractions for future scenarios, protocols, chains or runners;
- add first-party production/test comments;
- add explanatory docstrings;
- add `TODO`;
- add `FIXME`;
- add `NOTE`;
- add decorative separators.

Preserve required:

- license annotations;
- provenance annotations;
- security annotations;
- unrelated existing comments.

Use proportional tests for:

- Acceptance Criteria;
- public behavior;
- deterministic behavior;
- security boundaries;
- integration behavior where applicable.

Prefer existing test files, fixtures and helpers.

Create a new file, helper, class or abstraction only when demonstrably necessary
to satisfy the current approved task or valid review blocker.

Preserve repository ownership:

```text
BeeDrill
→ scenario semantics
→ drill domain models
→ expected-control semantics
→ evidence validation
→ security metrics
→ deterministic verdicts
→ BeeDrill-specific reports

BeeAgent
→ runtime
→ orchestration
→ execution authority
→ process lifecycle
→ Surfpool lifecycle
→ Solana RPC access
→ policy
→ credentials
→ timeouts
→ host storage/artifact implementation
→ external execution and egress

BeeSDK
→ proven reusable shared contracts only
```

When required behavior belongs to another repository, do not implement a local
workaround that violates ownership merely to close the BeeDrill task.

Before reporting completion, inspect the final diff and remove:

- prohibited comments;
- unrelated formatting changes;
- unrelated cleanup;
- speculative changes;
- accidental dependency changes;
- accidental version changes.

## Target safety gate

Before verification:

1. verify the current working directory;
2. verify the current branch;
3. inspect `git status`;
4. inventory committed changes relative to the base branch;
5. inventory staged changes;
6. inventory unstaged changes;
7. inventory untracked files;
8. distinguish current-Issue changes from unrelated changes.

Stop when:

- the path differs from the requested target;
- the branch differs from the expected branch;
- unrelated changes prevent safe verification;
- mandatory target information is missing;
- the approved task contract is missing for initial verification;
- explicit final-review blockers are missing for a correction run;
- safe attribution of current changes is impossible;
- the requested correction requires an unapproved cross-repository change.

Do not silently:

- switch branches;
- replace the requested worktree;
- discard existing changes;
- reset unrelated work;
- absorb unrelated changes into the current task.

## Required reading

Read for every run:

- `AGENTS.md`;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- all changed and untracked files;
- directly related contracts;
- directly related implementation;
- directly related tests.

Read as applicable:

- `docs/ROADMAP.md`;
- `docs/SPEC.md`;
- `docs/ARCHITECTURE.md`;
- `docs/DEV_GUIDE.md`;
- `README.md`;
- `pyproject.toml`;
- package exports;
- BeeSDK contracts;
- BeeAgent integration contracts;
- module entrypoint;
- scenario/domain models;
- evidence models;
- metrics;
- verdict logic;
- fixtures;
- artifact/report contracts;
- execution adapters.

For initial independent verification also read:

- the approved Issue or normalized approved task contract;
- the relevant roadmap section;
- supplied planning constraints.

For a correction run also read:

- every supplied final-review blocker;
- directly related current files;
- related contracts;
- related tests;
- code touched by the required correction.

Do not request or depend on:

- implementation report;
- previous verification report;
- previous executor reasoning.

The following are authoritative:

```text
current target worktree
actual diff
current contracts
tests
runtime evidence
package outputs
integration evidence
```

## Verification

### Initial independent verification

Evaluate every Acceptance Criterion as:

```text
satisfied
partially satisfied
not satisfied
not verifiable
not applicable
```

Do not assume an Acceptance Criterion is satisfied because the implementation
report says so.

Verify it from:

- code;
- contracts;
- tests;
- command results;
- runtime evidence;
- artifacts;
- integration behavior.

### Correction run

Verify:

- every supplied blocking finding;
- every affected Acceptance Criterion explicitly referenced by those findings;
- behavior touched by the correction;
- regressions caused by the correction.

Do not reopen unrelated already-reviewed scope.

## Verification dimensions

Verify as applicable:

- source of truth;
- BeeDrill / BeeAgent / BeeSDK ownership;
- public/module contracts;
- top-level exports;
- type/protocol compatibility;
- backward compatibility;
- package metadata;
- package build behavior;
- independent package importability;
- dependency direction;
- runtime dependency surface;
- BeeSDK compatibility;
- BeeAgent module compatibility;
- scenario validation;
- fixture behavior;
- evidence contracts;
- deterministic serialization;
- deterministic metrics;
- deterministic verdicts;
- replay behavior;
- artifact behavior;
- execution isolation;
- execution authority;
- RPC restrictions;
- target restrictions;
- timeout behavior;
- cleanup behavior;
- detector integration;
- containment integration;
- dependency and version status;
- security boundaries;
- required tests and checks.

Determine the actual change level from:

- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- actual changed behavior.

Do not rely only on the change level written in the Issue if the implementation
has become more security-sensitive.

## BeeDrill architecture verification

Canonical boundary:

```text
BeeSDK
→ shared public contracts

BeeAgent
→ host runtime and controlled execution

BeeDrill
→ security-control-validation domain behavior
```

Verify that the implementation does not create a second BeeAgent runtime inside
BeeDrill.

BeeDrill may own:

- scenarios;
- target semantics specific to drills;
- expected controls;
- evidence validation;
- metrics;
- deterministic verdicts;
- drill-specific reporting.

BeeDrill must not silently take ownership of:

- generic process execution;
- generic runtime orchestration;
- unrestricted subprocess execution;
- unrestricted RPC access;
- production credential management;
- runtime policy;
- host authority decisions;
- module registry;
- host state/session lifecycle;
- generic storage implementation.

If such behavior is required and not already supplied by BeeAgent:

- report the repository ownership gap;
- do not hide it behind BeeDrill-local implementation unless the approved task
  explicitly authorizes that architecture change.

## Security verification

### Scenario input is untrusted

Treat scenario, fixture and drill configuration input as untrusted unless the
repository contract explicitly states otherwise.

Verify that scenario-controlled data cannot directly grant:

- arbitrary executable selection;
- arbitrary command-line execution;
- arbitrary filesystem path access;
- arbitrary RPC destination;
- production credentials;
- runtime identity;
- execution authority;
- host policy override.

### Host-owned execution

Where execution exists, verify that actual authority remains within the approved
host/runtime boundary.

A pattern equivalent to:

```text
scenario data
→ arbitrary subprocess
```

is blocking unless the approved architecture explicitly permits and constrains
that exact mechanism.

### Isolation

For the current hackathon MVP:

```text
production/mainnet mutation
= excluded
```

Verify where applicable that attack execution is restricted to approved isolated
environments.

Unexpected mainnet mutation capability is blocking.

### Deterministic verdicts

Where the task affects verdict behavior, verify:

```text
same valid evidence
→ same metrics
→ same final verdict
```

Critical PASS/FAIL must not depend on:

- LLM confidence;
- free-form prose interpretation;
- undocumented heuristic judgment;
- hidden manual override.

AI may assist:

- explanation;
- authoring;
- summarization;
- remediation suggestions.

AI must not become the final authority for a deterministic security verdict.

### Fail-closed behavior

Missing, malformed, incomplete or inconsistent critical evidence must not
silently produce PASS.

Verify the approved explicit behavior, such as:

```text
fail
degraded
refused
incomplete
```

### Evidence is not authority

Evidence may determine product outcome.

Evidence must not grant new execution authority.

### Secret handling

Verify as applicable that the implementation does not expose:

- production private keys;
- credentials;
- tokens;
- unrelated secrets

through:

- source;
- fixtures;
- logs;
- artifacts;
- documentation examples;
- test output.

## Dependency and lockfile rules

When the approved Issue has no dependency change:

- do not regenerate `uv.lock`;
- do not modify `uv.lock`;
- do not separately validate `uv.lock`;
- do not introduce new dependencies during correction.

When the approved Issue explicitly requires a dependency change:

- allow only the minimum necessary dependency change;
- inspect the corresponding relevant lockfile diff;
- verify dependency necessity;
- run applicable SCA.

Never run or require:

```text
uv lock --check
```

Do not treat unrelated lockfile noise as an independent finding.

Do not change package version unless the approved Issue is explicitly
release-related.

## Corrections

Apply corrections only when required by:

- an unsatisfied Acceptance Criterion;
- a supplied valid final-review blocker;
- incorrect current-Issue behavior;
- unsafe current-Issue behavior;
- architecture ownership violation;
- source-of-truth violation;
- public/module contract incompatibility;
- type/protocol incompatibility;
- package/build incompatibility;
- deterministic-verdict violation;
- execution/isolation violation;
- missing required verification.

Corrections must be:

- limited to current scope;
- minimal;
- complete;
- compatible with current contracts;
- compatible with repository ownership;
- free of duplicate logic;
- free of duplicate contracts;
- free of unnecessary defaults;
- free of unnecessary hardcoding;
- free of speculative abstractions;
- PEP 8 compliant;
- free of newly introduced comments.

Do not create a preventive patch merely because a theoretical problem might
appear later.

Do not introduce a new requirement because it may be useful after the
hackathon.

If a new function or class is necessary, identify its exact insertion location
in the final report.

## Cross-repository correction rule

If verification proves that a required correction belongs to another
repository:

```text
BeeDrill domain/product defect
→ BeeDrill

host runtime/execution defect
→ BeeAgent

stable reusable shared-contract defect
→ BeeSDK, only when proven
```

Do not implement another repository's responsibility locally merely to satisfy
the current test.

If the approved task explicitly includes multiple implementation repositories:

1. verify exact worktree and branch for each repository;
2. read the owning repository's instructions;
3. modify only the repository-owned behavior;
4. run repository-specific checks;
5. verify the final integration.

If cross-repository work is necessary but was not approved, stop and report the
blocking dependency.

## Tests and checks

Run all checks required by the actual change level.

Include as applicable:

- targeted regression tests;
- `uv run pytest -q`;
- `uv build`;
- package import smoke;
- top-level public API verification;
- BeeSDK structural compatibility;
- BeeAgent module compatibility smoke;
- package metadata checks;
- dependency direction checks;
- deterministic serialization tests;
- deterministic metric tests;
- deterministic verdict tests;
- fixture tests;
- replay tests;
- artifact verification;
- Surfpool lifecycle smoke;
- Solana RPC smoke;
- detector integration smoke;
- containment integration smoke;
- malformed-input tests;
- forbidden-target tests;
- authority-boundary tests;
- timeout tests;
- cleanup tests;
- secret-leak tests;
- SAST;
- SCA;
- DAST;
- IAST;
- fuzzing.

Use only checks justified by:

- approved task;
- actual change level;
- `docs/SDLC.md`;
- `docs/SECURITY.md`.

Do not invent irrelevant verification requirements.

### Security-sensitive execution checks

For an execution-related security-sensitive change, verify negative behavior as
applicable:

```text
approved isolated target succeeds

forbidden target
→ refused

invalid RPC target
→ refused

malformed scenario
→ refused

scenario-supplied arbitrary executable
→ impossible/refused

timeout
→ bounded failure

failed process
→ cleaned up

missing critical evidence
→ cannot PASS
```

### Replay checks

For scenario/verdict changes where reproducibility is part of the contract,
verify that equivalent initial state plus equivalent scenario produces
equivalent expected outcome.

Record exact:

- commands;
- exit codes;
- passed count;
- failed count;
- skipped count;
- relevant warnings.

Do not claim a check passed when it was not executed.

## Final diff review

Before reporting completion:

1. inspect `git status`;
2. inspect the complete final diff;
3. inspect untracked files;
4. verify every changed file belongs to the approved Issue or supplied blocker;
5. verify no required correction remains missing;
6. verify no unrelated formatting sweep occurred;
7. verify no unrelated refactor occurred;
8. verify no prohibited comment/docstring/TODO was introduced;
9. verify no accidental secret/private key was added;
10. verify dependency changes match approved scope;
11. verify package version matches approved scope;
12. verify repository ownership remains intact.

When correcting review blockers, also verify that no correction regressed
already-correct behavior within the approved task.

## Final readiness

Return one of:

```text
ready for final read-only review
```

or:

```text
not ready for final read-only review
```

Use `ready for final read-only review` only when:

- required corrections are complete;
- required tests/checks have been executed successfully or explicitly accounted
  for;
- no known current-scope blocker remains;
- changed-file inventory is clean with respect to the task;
- no unresolved security-boundary problem remains.

Do not call the implementation merge-ready.

Final merge readiness belongs to the read-only final review.

## Final report

Return one consolidated report containing:

1. `Target verification`
2. `Actual changed-file inventory`
3. `Roadmap / iteration`
4. `Acceptance Criteria coverage`
5. `Blocking findings received`
6. `Corrections made`
7. `Change level`
8. `Required checks`
9. `Tests and commands`
10. `Runtime / integration smoke`
11. `Determinism / replay`
12. `Artifacts and evidence`
13. `Public/module API and compatibility`
14. `BeeDrill / BeeAgent / BeeSDK boundary`
15. `Security review`
16. `Dependencies`
17. `Unrelated-file check`
18. `Known limitations`
19. `Recommended Conventional Commit`
20. `Final readiness`
21. `Version status`

For every substantive correction, report:

```text
File:
`path/to/file`

Before:
<previous incorrect behavior>

After:
<implemented required behavior>

Why:
<current-Issue requirement or supplied blocker and verification evidence>
```

Do not include a full diff.

When no correction was required, state exactly:

```text
No corrections required.
```

For initial verification, include every Acceptance Criterion with its status.

For a correction run, include:

- every supplied blocking finding;
- its correction status;
- affected Acceptance Criteria;
- regression result.

Do not claim verification that was not executed.

End with:

```text
version not changed
```

unless the approved Issue explicitly requires release versioning.
