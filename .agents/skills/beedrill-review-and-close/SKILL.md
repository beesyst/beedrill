---
name: beedrill-review-and-close
description: Perform a complete read-only BeeDrill review against an approved Issue, using the exact worktree and base branch, then return one consolidated verdict and PR close package.
---

# BeeDrill review and close workflow

## Purpose

Use this workflow after implementation is complete and the user has supplied:

- an approved Issue or acceptance criteria;
- implementation evidence;
- exact worktree information;
- expected branch and base branch.

This workflow is read-only.

Do not:

- modify files;
- run repository commands;
- switch branches;
- create commits;
- push;
- create or merge a PR.

The review must determine whether the actual target is ready to become the
accepted implementation of the approved BeeDrill task.

Review only the approved scope.

Do not expand the review into:

- speculative architecture work;
- optional product improvements;
- unrelated cleanup;
- future roadmap work;
- broad BeeAgent, BeeSDK, BeeUI or BeeScan review.

## Required inputs

Obtain:

- project;
- instruction worktree;
- expected target worktree path;
- expected branch;
- expected base branch;
- mode;
- roadmap context;
- approved Issue content or GitHub Issue URL;
- current PR description, GitHub Pull Request URL or `none`;
- implementation and verification evidence;
- additional target context when explicitly requested;
- previous blocking findings for re-review when applicable.

## Working contract

Read every declared file completely before forming findings.

Keep a file inventory.

When another file becomes necessary:

1. add it to the inventory;
2. read it completely;
3. only then evaluate it.

Map the review to the supplied roadmap iteration and evaluate only its approved
scope.

Determine the actual change level:

```text
low-risk
runtime-risk
security-sensitive
```

from:

- the approved Issue;
- actual changed files;
- resulting runtime/security behavior.

Derive required evidence from:

- `docs/SDLC.md`;
- `docs/SECURITY.md`.

Require the smallest complete KISS change.

Treat as blocking when introduced by the current Issue without explicit need:

- unrelated refactoring;
- formatter churn;
- speculative architecture;
- duplicated runtime responsibility;
- duplicated shared contracts;
- newly introduced first-party production/test comments;
- explanatory docstrings;
- `TODO`;
- `FIXME`;
- `NOTE`;
- decorative separators.

Preserve required:

- license annotations;
- provenance annotations;
- security annotations;
- unrelated existing comments.

Require proportional tests for:

- Acceptance Criteria;
- public behavior;
- security boundaries;
- deterministic behavior;
- integration behavior where applicable.

Prefer existing tests and helpers unless a new one is demonstrably necessary.

Confirm that repository ownership remains correct:

```text
BeeDrill
→ security-control-validation domain behavior
→ scenario semantics
→ evidence interpretation
→ metrics
→ deterministic verdicts

BeeAgent
→ runtime
→ orchestration
→ execution
→ authority
→ policy
→ credentials
→ Surfpool/process lifecycle
→ Solana RPC
→ host storage/artifact implementation

BeeSDK
→ proven reusable shared contracts only
```

Before returning a verdict, inspect the complete final diff for:

- unrelated changes;
- forbidden comments;
- formatter churn;
- ownership violations;
- unexpected dependency changes;
- unexpected version changes.

The following are separate identifiers:

```text
worktree path
MCP target
Git branch
```

Do not treat them as interchangeable.

---

## Phase 0 — Resolve supplied GitHub context

Follow the GitHub context resolution contract from `AGENTS.md`.

When the approved Issue input contains a GitHub Issue URL:

1. call `get_github_context`;
2. read the Issue title;
3. read the complete Issue body;
4. read all available Issue comments;
5. use explicit accepted clarifications from comments when establishing the
   approved scope.

When the current PR input contains a GitHub Pull Request URL:

1. call `get_github_context`;
2. read the PR title;
3. read the complete PR body;
4. read all available conversation comments;
5. read reviews;
6. read inline review comments.

The approved Issue establishes:

- required scope;
- excluded scope;
- Deliverable;
- Acceptance Criteria;
- task-specific verification contract.

The PR provides:

- delivery context;
- implementation context;
- reviewer context.

The PR does not override:

- the approved Issue;
- repository contracts;
- actual target worktree state.

When pasted content and a URL are supplied together, consider both.

If they materially conflict, report the conflict instead of silently choosing
one source.

If required GitHub context cannot be read completely, return:

```text
REVIEW INCOMPLETE
```

Do not continue to a code verdict from incomplete required GitHub context.

---

## Phase 1 — Resolve the exact target

1. Call `list_worktrees` for the project.
2. Find the entry whose `path` exactly matches the expected target worktree
   path.
3. Use the returned MCP `target`.
4. Call `get_project_context` for that target and supplied mode.
5. Verify:
   - project;
   - path;
   - branch;
   - HEAD;
   - dirty state.

If the exact path or mandatory metadata is unavailable, return:

```text
REVIEW INCOMPLETE
```

If the project differs from the expected value:

- report expected;
- report actual;
- do not issue a code verdict.

If the branch differs from the expected branch:

- report expected;
- report actual;
- do not issue a code verdict.

Do not:

- infer an MCP target from a branch name;
- substitute the main worktree for a requested feature worktree;
- review a similar-looking worktree.

---

## Phase 2 — Read the complete manifest and diff

### Review manifest

1. Call `get_review_manifest` with an empty cursor.
2. Append each returned `content` page.
3. Continue using the exact `next_cursor` while `has_more=true`.
4. Require the same `snapshot_id` on every page.
5. Parse the combined content as one manifest.

Verify:

- project;
- target;
- branch;
- HEAD;
- expected base branch;
- dirty state;
- committed files;
- staged files;
- unstaged files;
- untracked files;
- deleted files;
- renamed files;
- omitted or redacted paths.

The manifest is the authoritative changed-file inventory.

### Review diff

1. Call `get_review_bundle_page` with an empty cursor.
2. Append each returned `content` page.
3. Continue using the exact `next_cursor` while `has_more=true`.
4. Require the same snapshot as the manifest.
5. Finish only when:
   - `has_more=false`;
   - `next_cursor=null`;
   - `truncated=false`.

Do not use compatibility `get_review_bundle` as a substitute for the paginated
review flow.

If:

- pagination fails;
- snapshot identity changes;
- required content is truncated;

return:

```text
REVIEW INCOMPLETE
```

The complete diff is evidence of the actual changes.

---

## Phase 3 — Resolve review instructions

Read from the primary target:

- `AGENTS.md`;
- `.agents/skills/beedrill-review-and-close/SKILL.md`.

If they are absent because the feature worktree predates their introduction,
use the explicitly supplied canonical BeeDrill instruction worktree.

Expected normal canonical instruction source:

```text
/home/bee/Pro/beedrill
```

The exact supplied `INSTRUCTION_WORKTREE` remains authoritative.

When fallback is required:

1. resolve the instruction worktree through `list_worktrees`;
2. verify its exact path;
3. verify it is on the expected canonical branch, normally `main`;
4. read:
   - `AGENTS.md`;
   - `.agents/skills/beedrill-review-and-close/SKILL.md`;

5. use them only as review instructions;
6. continue reviewing implementation exclusively from the original target
   worktree.

The absence of newer instructions from a legacy target worktree is not itself a
finding.

Do not silently select another instruction source.

---

## Phase 4 — Read required files

Use `read_project_file`.

When continuation metadata is returned:

- continue with the exact `next_line`;
- continue with the exact `next_column`;
- finish only when both are null.

Read completely:

- `AGENTS.md`;
- this skill;
- `.github/PULL_REQUEST_TEMPLATE/pr.md`;
- relevant `docs/ROADMAP.md` section;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- relevant architecture documentation;
- relevant product/specification documentation;
- package/public API contracts where applicable;
- every changed and untracked text file;
- relevant tests;
- directly related unchanged contracts and implementation required to interpret
  the changes correctly.

Read as applicable:

- `docs/ARCHITECTURE.md`;
- `docs/SPEC.md`;
- `docs/DEV_GUIDE.md`;
- `README.md`;
- `pyproject.toml`;
- package exports;
- BeeSDK imports/contracts;
- BeeDrill module contract;
- scenario models;
- evidence models;
- metrics;
- verdict implementation;
- fixtures;
- execution adapters;
- integration boundaries;
- artifact/report formats.

### Deleted files

For deleted files:

- inspect the complete diff;
- inspect affected current imports;
- inspect affected public contracts;
- inspect affected tests;
- inspect affected runtime/integration usage.

### Renamed files

For renamed files:

- inspect old and new paths in the manifest and diff;
- read the destination file completely;
- verify updated references.

If a required relevant file is:

- omitted;
- redacted;
- unreadable through the available safe MCP interface;

return:

```text
REVIEW INCOMPLETE
```

Do not issue a code verdict from partial file content.

---

## Phase 5 — Related repository context

When an additional repository is explicitly supplied:

1. resolve its exact path through `list_worktrees`;
2. verify its expected branch through `get_project_context`;
3. follow the supplied `Role`, `Mode` and `Skill`;
4. read only the contracts and implementation required by that declared role;
5. do not broaden the primary review unnecessarily;
6. do not include unrelated repository state in the primary verdict.

If the primary BeeDrill implementation depends on code or a contract absent
from the expected related branch, report a blocking cross-repository dependency
when that dependency is required by the approved Issue.

### BeeDrill ownership

BeeDrill owns:

- drill-specific domain models;
- scenario semantics;
- target semantics specific to drills;
- expected-control semantics;
- evidence interpretation;
- deterministic metrics;
- deterministic verdict rules;
- scenario corpus;
- BeeDrill-specific product/report behavior.

### BeeAgent ownership

BeeAgent owns:

- orchestration;
- runtime/session state;
- module registry;
- runtime context creation;
- execution authority;
- process/subprocess lifecycle;
- Surfpool lifecycle;
- Solana RPC access;
- credentials and secrets;
- policy;
- approvals;
- timeouts;
- external execution and egress;
- artifact/storage implementation;
- host runtime logging.

### BeeSDK ownership

BeeSDK owns only proven reusable shared public contracts such as:

- shared module contracts;
- artifact ports;
- reusable capability contracts;
- shared type contracts.

BeeSDK must not gain BeeDrill-specific:

- Solana semantics;
- scenarios;
- attack logic;
- detector semantics;
- containment semantics;
- metrics;
- verdicts.

### BeeUI ownership

BeeUI owns generic presentation behavior when explicitly in scope.

Do not make BeeUI part of BeeDrill implementation merely because visualization
would be useful.

### BeeScan ownership

BeeScan owns BeeScan-specific scanning/pentesting product behavior.

Do not move BeeScan implementation into BeeDrill.

---

## Phase 6 — BeeDrill security and architecture review

For changes affecting BeeDrill security behavior, explicitly verify the
applicable boundaries.

### Scenario-controlled authority

Scenario or module-controlled data must not silently grant or override:

- execution authority;
- runtime identity;
- credentials;
- host policy;
- arbitrary executable selection;
- arbitrary command-line execution;
- arbitrary filesystem access;
- arbitrary RPC destination;
- production/mainnet mutation authority.

A violation is blocking.

### Host-owned execution

When execution is required, verify that BeeAgent or another explicitly approved
host-owned boundary remains responsible for execution.

Do not accept:

```text
BeeDrill domain model
→ arbitrary subprocess
```

as an implementation shortcut unless the approved architecture explicitly
authorizes that exact boundary.

### Isolation

For the current hackathon MVP, verify where applicable that attack execution
remains limited to explicitly approved isolated environments.

Unexpected production/mainnet mutation capability is blocking.

### Deterministic verdict

When the Issue affects verdict behavior, verify:

```text
same valid evidence
→ same metrics
→ same verdict
```

Do not accept final critical PASS/FAIL decisions based solely on:

- LLM confidence;
- free-form prose interpretation;
- undocumented heuristics;
- hidden manual overrides.

### Fail-closed behavior

When critical evidence is:

- missing;
- malformed;
- inconsistent;
- incomplete;

verify that it cannot silently become a successful PASS.

Expected behavior must follow the approved contract, such as:

```text
fail
degraded
refused
incomplete
```

### Evidence is not authority

Evidence may determine product outcome.

Evidence must not grant new runtime execution authority.

### Secret handling

Verify where applicable that changes do not expose:

- production private keys;
- credentials;
- tokens;
- unrelated secrets

through:

- source;
- fixtures;
- logs;
- artifacts;
- examples;
- test output.

---

## Phase 7 — Evidence and Acceptance Criteria

Follow the instruction and evidence precedence defined in `AGENTS.md`.

The implementation report is supporting evidence, not the source of truth.

Bee Dev MCP cannot execute tests.

Treat supplied command output as reported evidence.

Never claim MCP ran:

- tests;
- builds;
- SAST;
- SCA;
- smoke checks;
- runtime commands.

When the approved Issue has no dependency change:

- do not require lockfile regeneration;
- do not require dedicated lockfile validation;
- do not require `uv lock --check`.

When the approved Issue explicitly requires a dependency change:

- inspect only the relevant dependency change;
- inspect the corresponding minimal lockfile diff as applicable;
- evaluate required SCA evidence.

Never request, evaluate or treat:

```text
uv lock --check
```

as merge evidence.

Evaluate every Acceptance Criterion as exactly one:

```text
satisfied
partially satisfied
not satisfied
not verifiable
not applicable
```

Check as applicable:

- observable BeeDrill behavior;
- public/module API compatibility;
- BeeSDK compatibility;
- BeeAgent integration compatibility;
- package source of truth;
- package/build behavior;
- independent installability/importability;
- dependency direction;
- runtime dependency surface;
- repository ownership;
- execution authority;
- isolation;
- scenario validation;
- evidence contract;
- deterministic serialization;
- deterministic metrics;
- deterministic verdict behavior;
- replay behavior;
- artifact output;
- detector integration;
- containment integration;
- timeout/cleanup behavior;
- forbidden-target behavior;
- secret handling;
- documentation;
- version declarations;
- required tests/build/smoke/security evidence.

`Not verifiable` is blocking only when the approved Issue, SDLC or security
rules require that evidence for merge readiness.

---

## Phase 8 — Verification evidence by change level

Determine required evidence from the actual change level.

### low-risk

Typical evidence may include:

- targeted checks;
- full tests when Python/test infrastructure changed;
- documentation consistency.

### runtime-risk

Typical evidence may include:

- targeted tests;
- `uv run pytest -q`;
- package build when package/public surface changed;
- import/public API smoke;
- deterministic scenario/evidence tests;
- integration smoke where applicable;
- artifact checks;
- replay verification when relevant.

### security-sensitive

Typical evidence may include applicable runtime-risk checks plus:

- SAST;
- SCA if dependencies changed;
- negative/adversarial tests;
- forbidden-target tests;
- malformed-input tests;
- timeout tests;
- cleanup tests;
- secret-leak checks;
- authority-boundary checks;
- explicit security review.

Use only checks justified by:

- Issue;
- actual changes;
- `docs/SDLC.md`;
- `docs/SECURITY.md`.

Do not invent irrelevant security tooling requirements.

---

## Phase 9 — Blocking findings

A blocker must affect readiness of the current approved Issue.

Examples:

- unmet Acceptance Criterion;
- incorrect BeeDrill behavior;
- unsafe execution behavior;
- security or authority bypass;
- scenario-controlled execution escalation;
- production/mainnet mutation path introduced outside approved scope;
- missing required isolation;
- BeeDrill/BeeAgent ownership violation;
- BeeDrill/BeeSDK ownership violation;
- duplicated shared contract;
- conflicting source of truth;
- incompatible public/module contract;
- missing required public export;
- deterministic verdict violation;
- missing critical evidence incorrectly resulting in PASS;
- incorrect scenario/evidence serialization;
- replay regression;
- artifact contract regression;
- package/build regression;
- unintended dependency;
- missing required verification evidence;
- unrelated files entering the PR;
- unintended dependency or version change;
- documentation contradicting actual behavior;
- missing required cross-repository dependency;
- newly introduced first-party production/test comments;
- explanatory docstrings;
- `TODO`;
- `FIXME`;
- `NOTE`;
- decorative separators;
- unrelated formatter churn;
- unrelated refactoring.

Do not make blockers from:

- optional polish;
- personal naming/style preferences;
- speculative future architecture;
- future product ideas;
- unrelated cleanup;
- requirements absent from the Issue;
- MCP limitations themselves;
- missing checks that are not required by the actual change level.

Find and consolidate all real blockers before returning the verdict.

---

## Phase 10 — Completeness gate

Before issuing a code verdict, confirm:

- exact target verified;
- exact branch verified;
- expected base branch verified;
- complete manifest consumed;
- complete non-truncated diff consumed;
- manifest and diff use the same snapshot;
- committed/staged/unstaged/untracked changes inventoried;
- deleted and renamed paths inspected;
- every required changed file fully read;
- relevant unchanged contracts fully read;
- related repository context evaluated where requested;
- architecture ownership evaluated;
- every Acceptance Criterion evaluated;
- supplied verification evidence evaluated;
- package/dependency/version scope checked;
- applicable security boundaries reviewed;
- all blockers consolidated.

If mandatory inspection remains incomplete, return:

```text
REVIEW INCOMPLETE
```

Include:

- completed inspection;
- exact missing tool, metadata, file or continuation;
- reason no code verdict was issued.

Do not include:

- implementation findings based on partial inspection;
- correction prompt;
- PR body;
- code verdict.

---

## Phase 11 — Verdict

Return exactly one completed-review verdict:

```text
APPROVED FOR PR
```

or:

```text
CHANGES REQUIRED
```

### APPROVED FOR PR

Use only when no blocking findings remain.

State exactly:

```text
No corrections required.
```

Then provide:

1. Acceptance Criteria coverage;
2. files reviewed;
3. supplied verification evidence;
4. non-blocking limitations;
5. reviewed branch;
6. recommended squash commit;
7. completed PR body using the repository template;
8. merge readiness;
9. explicit next actions:
   - commit the reviewed changes;
   - push the feature branch;
   - open or update the PR;
   - wait for CI;
   - squash merge after approval.

Do not claim Bee Dev MCP ran tests.

### CHANGES REQUIRED

Provide every blocker using:

### <Finding title>

File:

`path/to/file`

Exact location:

<existing function, class, contract, configuration or documentation section>

Current:

```<language>
<exact bounded current fragment>
```

Required:

```<language>
<complete bounded replacement or insertion>
```

Why:

<Acceptance Criterion, existing contract and concrete blocking impact>

For code, configuration or contract blockers:

- include the exact bounded current fragment;
- include the complete bounded replacement or insertion when it can be stated
  safely from inspected evidence.

For behavior-only blockers:

- describe the exact observed behavior;
- describe the exact required behavior.

For evidence-only blockers:

- provide the exact missing command or verification scenario;
- do not invent a code change.

Do not return only a correction prompt.

Present every real blocker first.

Then provide one consolidated correction prompt.

Do not prepare a final PR body while blockers remain.

---

## Consolidated correction prompt

The correction prompt is an executor prompt for Copilot or Codex.

It is not a continuation of the Bee Dev MCP review.

Select and name the executor:

- **Copilot** for localized, clearly specified corrections;
- **Codex** for broader diagnosis, multi-contract changes, cross-repository
  corrections or security-sensitive corrections.

The correction prompt must authorize the executor to:

- inspect files locally;
- modify files;
- run required repository checks;

inside the exact target worktree using its available local tools.

Do not copy reviewer-only restrictions into the correction prompt, including:

- `Use only Bee Dev MCP`;
- read-only mode;
- MCP target identifiers;
- MCP review mode.

Use this controlled structure:

```text
Executor: <Copilot or Codex>

Project: beedrill
Instruction worktree: <exact instruction worktree>
Target worktree: <exact target worktree>
Expected branch: <feature branch>
Base branch: <base branch>

Read instructions from:

- <instruction worktree>/AGENTS.md
- <instruction worktree>/.agents/skills/beedrill-verify-and-correct/SKILL.md

Use the instruction worktree only for reading instructions.
Inspect, modify and verify files only in the target worktree.
Do not modify the instruction worktree.

Fix only the blocking findings from the current final review.
Preserve all already-correct behavior within the approved Issue.

For every blocker use:

### <Finding title>

File:
`<path>`

Exact location:
<existing function, class, contract, configuration or documentation section>

Current:
<exact bounded current fragment or observed behavior>

Required:
<complete bounded replacement, insertion or required behavior>

Why:
<Acceptance Criterion, contract violation or concrete impact>

For code, configuration or contract blockers, use the bounded current fragment
and required replacement or insertion supplied by the review.

For behavior-only or evidence-only blockers, implement or verify only the exact
required behavior or scenario.

Required verification:

- targeted regression tests for every blocker;
- full tests required by the actual change level;
- applicable package build/import/public API smoke;
- applicable BeeSDK/BeeAgent compatibility checks;
- applicable scenario/evidence/verdict checks;
- applicable deterministic replay checks;
- applicable runtime/integration smoke;
- applicable security and authority checks;
- `git diff --check`;
- dependency and version verification;
- unrelated-file check.

Return one consolidated report according to
`beedrill-verify-and-correct`.

For every implemented correction report:

File → Before → After → Why

Include:

- exact changed files;
- commands and results;
- runtime/integration evidence;
- deterministic/replay evidence when applicable;
- security review;
- dependency status;
- public/module contract impact;
- known limitations.

End with:

version not changed

Do not commit, push, create or update a PR, or merge.
```

The correction prompt must include every blocking finding from the completed
review.

Do not copy:

- the full Issue;
- the full review report;
- stable repository rules;

into the correction prompt.

Do not introduce:

- new requirements;
- optional cleanup;
- architecture improvements;
- future scope;

that are not necessary to close the current blockers.

---

## Cross-repository correction rule

If a blocker belongs to another repository:

- identify the owning repository;
- do not instruct the BeeDrill executor to implement it in BeeDrill;
- require a separate target/worktree/Issue flow where the approved scope allows
  that correction;
- preserve one implementation repository per Issue/branch/PR.

Examples:

```text
Surfpool host lifecycle bug
→ BeeAgent

missing reusable shared contract
→ BeeSDK, only if proven necessary

BeeDrill scenario/verdict defect
→ BeeDrill
```

Do not hide cross-repository implementation inside one correction prompt unless
the approved Issue explicitly defined coordinated multi-repository work and the
prompt contains the exact worktree for every implementation target.

---

## Re-review

For re-review:

1. obtain a new complete manifest;
2. obtain a new complete paginated diff;
3. verify the same target path;
4. verify the same expected branch;
5. verify the same expected base branch;
6. verify every previous blocker;
7. evaluate the original Acceptance Criteria again;
8. inspect regressions introduced by corrections;
9. re-evaluate applicable security boundaries;
10. return:

- `APPROVED FOR PR`; or
- only the remaining current blockers.

Do not introduce unrelated optional findings during re-review.

A previous blocker that is resolved must not remain in the new blocker list.

---

## PR close package

When approved, prepare the PR body using the actual repository template.

The PR body must reflect actual reviewed implementation rather than planning
intent.

Include only template-required content and relevant reviewed evidence.

As applicable, summarize:

- roadmap iteration;
- approved Issue;
- actual implementation;
- Acceptance Criteria completion;
- tests and supplied command results;
- package/build evidence;
- runtime/integration evidence;
- scenario/replay evidence;
- security review;
- dependency status;
- known limitations;
- version status.

Do not claim MCP executed any command.

Do not include speculative future work as completed scope.

---

## Recommended squash commit

When the review is approved, provide one recommended Conventional Commit title.

It must:

- reflect the actual reviewed change;
- follow current repository conventions;
- avoid claiming unrelated scope;
- avoid invented release/version information.

Examples of valid shape:

```text
feat: add deterministic drill verdicts
fix: fail closed on incomplete drill evidence
docs: align BeeDrill security boundaries
```

Do not recommend a version bump unless the approved Issue is explicitly
release-related.

---

## Close decision

When approved, explicitly state:

```text
Merge readiness: ready after commit/push/CI/PR approval
```

when that is accurate.

When blockers remain:

```text
Merge readiness: not ready
```

Do not present a merge-ready close package while blocking findings remain.

---

## Output format

For a completed review return, in order:

1. `Verdict`
2. `Blocking findings`
3. `Acceptance Criteria coverage`
4. `Files reviewed`
5. `Verification evidence`
6. `Unverified limitations`
7. `Close decision`
8. `PR body` when approved
9. `Consolidated correction prompt` when changes are required

For incomplete inspection return only:

1. `REVIEW INCOMPLETE`
2. `Completed inspection`
3. `Missing inspection data`
4. `Reason no code verdict was issued`

Do not mix:

- incomplete-review output;
- completed-review verdict;
- correction prompt;
- PR close package.

One review pass produces one consolidated outcome.
