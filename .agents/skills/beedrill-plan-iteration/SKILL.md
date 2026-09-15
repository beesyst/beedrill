---
name: beedrill-plan-iteration
description: Inspect the current BeeDrill implementation through Bee Dev MCP, critically validate task necessity, product fit and repository ownership, reconcile the correct roadmap, and prepare a compact roadmap item or standalone task plus complete copy-ready Issues without modifying repositories.
---

# BeeDrill iteration planning workflow

## Purpose

Use this workflow when:

- a BeeDrill task or product idea has not yet been approved;
- an existing roadmap item must be validated, refined or replaced;
- a proposed iteration may be stale relative to current implementation;
- the next meaningful BeeDrill increment must be selected;
- ownership between BeeDrill, BeeAgent, BeeSDK or another repository is unclear;
- coordinated repository changes may be required;
- a complete Issue must be prepared from repository evidence;
- a proposed security feature may duplicate an existing implementation;
- the task may expand BeeDrill beyond the approved Solana security-control-validation product boundary.

Do not use this workflow when a complete Issue has already been approved and the task is ready for `.agents/prompts/02-implementation-tests.md`.

Planning must determine:

- what exists now;
- what is actually missing;
- whether the work is necessary now;
- whether the proposed solution is correct;
- whether it advances the BeeDrill product thesis;
- whether a smaller complete solution exists;
- which roadmap owns the increment;
- which repository owns each required implementation;
- whether a BeeAgent or BeeSDK change is actually necessary;
- what must remain excluded;
- what context prompt 02 needs.

This workflow is read-only.

Use only Bee Dev MCP for repository inspection.

Do not:

- modify files;
- switch branches;
- run shell or Git commands;
- run tests;
- create Issues, branches, commits or PRs;
- prepare implementation, verification, correction or review prompts;
- prepare PR bodies.

## Repository guidance

Read and follow `AGENTS.md`.

`AGENTS.md` owns stable repository-wide rules, including:

- Bee Dev MCP usage;
- exact target resolution;
- complete reading;
- BeeDrill product boundary;
- architecture and repository ownership;
- security and execution boundaries;
- sources of truth;
- implementation rules;
- verification policy;
- dependency and version restrictions.

Do not repeat all of `AGENTS.md`, `docs/SDLC.md` or `docs/SECURITY.md` in planning output or Issues.

This skill owns only:

- the planning decision algorithm;
- roadmap reconciliation;
- product and necessity validation;
- repository ownership decisions;
- roadmap and Issue output contracts;
- the planning handoff.

## Required inputs

The external prompt `.agents/prompts/01-planning.md` provides:

- `MAIN_WORKTREE`;
- `MODE`;
- `ROADMAP_CONTEXT`;
- `TASK_OR_IDEA`;
- `CONTEXT_OR_NONE`;
- `ADDITIONAL_PROJECTS_OR_NONE`;
- declared project;
- expected branch;
- base branch.

Treat paths, project names, branches, modes and repository roles as exact input values.

Pass `MODE` unchanged to applicable Bee Dev MCP calls.

Do not silently substitute another:

- worktree;
- repository;
- branch;
- roadmap;
- mode.

## Core planning rules

### Evidence before agreement

Treat the user's task, roadmap reference, architectural assumption, proposed security model and implementation report as hypotheses.

Validate material assumptions against current:

- code;
- tests;
- package metadata;
- public contracts;
- type signatures;
- package contents;
- fixtures;
- scenario models;
- evidence models;
- verdict logic;
- host integration;
- BeeSDK usage;
- repository documentation;
- dirty changes;
- relevant related-repository implementation where required.

Current repository files and contracts are authoritative.

Reports, screenshots, previous planning outputs and product descriptions are supporting evidence only.

Do not automatically accept:

- the proposed iteration ID;
- the proposed roadmap or stage;
- the proposed repository;
- the proposed solution;
- the proposed urgency;
- the proposed dependency;
- the proposed host/runtime change;
- the assumption that new work is required;
- the assumption that BeeSDK must change;
- the assumption that BeeAgent must change;
- the assumption that a new abstraction belongs in BeeDrill.

### Critical planning

Answer:

- What is the current behavior?
- What gap remains?
- Does the gap matter to the current BeeDrill product thesis?
- Is it important now?
- Is it already implemented?
- Does another roadmap item already cover it?
- Is the proposed repository correct?
- Is a smaller complete solution available?
- Does the task preserve deterministic security validation?
- Does it preserve host-owned execution and authority?
- Does it require real execution evidence or only mocked behavior?
- What must not be built?
- What should BeeDrill prioritize next?

When the user's framing is wrong:

1. show the mismatch using repository evidence;
2. preserve the underlying product intent where possible;
3. correct roadmap, scope, numbering or ownership;
4. reject unnecessary architecture;
5. provide a usable corrected planning result.

### Product thesis gate

Before approving substantial BeeDrill work, verify that it supports the approved product thesis:

```text
current protocol state
→ isolated Solana environment
→ deterministic attack scenario
→ real attack execution
→ detection observation
→ containment observation
→ economic outcome measurement
→ deterministic PASS / FAIL
```

BeeDrill is primarily:

```text
continuous security-control validation for Solana
```

BeeDrill is not primarily:

```text
generic vulnerability scanner
generic AI pentester
incident-response chatbot
generic Solana simulator
wallet firewall
runtime platform
multi-chain security framework
SIEM
SOC platform
marketplace
```

Do not approve adjacent functionality merely because it is related to security.

### Ground-truth gate

Prefer tasks that improve objective, reproducible validation.

Critical security outcomes should remain based on evidence such as:

```text
attack executed?
detector fired?
when did detection occur?
containment executed?
when did containment occur?
what state changed?
what economic loss occurred?
what capital was preserved?
```

Do not introduce subjective LLM-based PASS/FAIL when deterministic evidence is available.

### Execution-boundary gate

BeeDrill must not become a second BeeAgent runtime.

Canonical responsibility split:

```text
BeeDrill
→ domain intent
→ scenario semantics
→ expected controls
→ evidence interpretation
→ metrics
→ verdicts

BeeAgent
→ execution
→ orchestration
→ authority
→ credentials
→ process lifecycle
→ Surfpool lifecycle
→ RPC access
→ policy
→ storage implementation
```

Do not approve a BeeDrill-local execution path merely because it is easier to implement.

### Isolation gate

For the hackathon MVP:

```text
production/mainnet mutation
= out of scope
```

Attack execution must remain in explicitly approved isolated environments.

A scenario must never gain arbitrary execution authority from scenario-controlled input.

### KISS

Recommend the smallest complete increment that closes the verified gap.

Avoid:

- optional polish;
- unrelated cleanup;
- broad refactoring;
- speculative architecture;
- unnecessary runtime implementation;
- second sources of truth;
- premature abstractions;
- generic frameworks;
- unnecessary dependencies;
- unnecessary cross-repository changes;
- future work hidden inside current scope;
- broad integration support before the central product thesis is proven.

### Roadmap and Issue separation

The roadmap is a compact iteration-level contract.

The Issue is the detailed execution contract.

Do not turn the roadmap into a full implementation specification.

Do not make the Issue so vague that implementation must repeat planning.

## ROADMAP_CONTEXT

`ROADMAP_CONTEXT` is a hypothesis to validate, not an instruction to approve the referenced item.

### Known numbered iteration

Example:

```text
Iteration BD-4 in docs/ROADMAP.md
```

Validate:

- roadmap existence and ownership;
- iteration existence and uniqueness;
- stage;
- status;
- scope;
- Excluded section;
- neighbouring completed and unfinished items;
- prerequisite completion;
- implementation evidence;
- overlapping or duplicate scope;
- whether the task still belongs to that item;
- whether the implementation order remains valid.

If the referenced iteration is `DONE`:

- preserve completed history;
- never return it to `PLANNED`;
- never create another item with the same ID;
- determine whether the request is already implemented;
- use a new unique ID only for genuine follow-up work.

Use a decimal ID only for a direct continuation when the repository already permits that convention.

Prefer the next appropriate independent `BD-` ID for independent work.

The absence of a proposed item from the roadmap is not itself an error.

### Proposed standalone task

Standalone is appropriate only when the work:

- is narrow and local;
- creates no significant product behavior;
- introduces no substantial public contract;
- does not materially change package/public API behavior;
- does not alter execution or authority boundaries;
- does not add a new Solana execution surface;
- does not introduce a new scenario class;
- does not create a new compatibility or dependency contract;
- does not require coordinated repository releases.

Reject standalone classification when the task creates:

- a meaningful BeeDrill product capability;
- a new security-control validation primitive;
- a new execution boundary;
- a new cross-repository integration;
- a new public contract;
- a new attack scenario class with product-level impact;
- a material artifact/verdict contract.

### No known iteration

Canonical value:

```text
none
```

Determine independently:

- whether work is required;
- whether an existing item should be reused;
- whether an unfinished item should be refined or replaced;
- whether a new iteration is justified;
- whether the task is standalone;
- which roadmap and stage own it;
- which unique ID fits;
- whether the idea should be deferred;
- whether the idea should be rejected as unnecessary.

Do not require `unknown`.

## Resolve repositories

Resolve the exact primary worktree before planning.

For each declared repository:

1. call `list_worktrees`;
2. match the exact absolute worktree path;
3. use the returned MCP target;
4. call `get_project_context` with the supplied mode;
5. verify project, path, branch, HEAD and dirty state.

Do not:

- infer targets from branch names;
- substitute a main worktree;
- inspect a similar-looking unrelated worktree;
- assume repositories share numbering;
- assume repositories share release cadence;
- assume an additional project is an implementation target merely because it is supplied.

If the primary worktree cannot be resolved, return:

```text
PLANNING INCOMPLETE
```

Explain the mismatch and stop.

If a required additional repository cannot be resolved, return `PLANNING INCOMPLETE` when ownership or contract decisions depend on it.

If the actual branch differs from the expected branch:

- report both values;
- do not prepare an implementation Issue for that target;
- continue only with read-only analysis that remains valid.

## Dirty worktrees

A dirty worktree is not automatically a blocker.

When relevant, inspect and distinguish:

- committed state;
- staged changes;
- unstaged changes;
- untracked files;
- deleted or renamed files.

Do not present uncommitted work as merged history.

State when a conclusion depends on uncommitted content.

When dirty work overlaps the task:

- identify the overlap;
- avoid duplicate planning;
- determine whether the task should incorporate, replace or wait for it;
- add reconciliation constraints to the Issue when needed.

Do not plan duplicate implementation over existing uncommitted work.

## Complete reading

Inspection is incomplete while mandatory content is truncated, omitted or paginated.

For files:

- continue with exact `next_line` and `next_column`;
- finish only when both are null.

For manifests and review bundles:

- continue with exact `next_cursor`;
- keep the same `snapshot_id`;
- finish only when `has_more=false`;
- treat `truncated=true` as incomplete.

Read relevant omitted files directly with `read_project_file`.

If mandatory evidence cannot be read, return:

```text
PLANNING INCOMPLETE
```

State:

- what is missing;
- why it is required;
- which decision cannot be made.

Do not invent repository facts.

## Discovery workflow

Use this sequence:

1. parse `TASK_OR_IDEA`;
2. resolve declared worktrees;
3. inspect relevant dirty state;
4. identify candidate roadmaps;
5. read the referenced iteration and neighbours;
6. read repository guidance and applicable SDLC/security rules;
7. inspect relevant architecture and product contracts;
8. inspect current implementation and tests;
9. inspect relevant scenario/evidence/verdict behavior;
10. inspect package metadata and dependency surface when relevant;
11. inspect additional repositories only as required;
12. compare roadmap, code, contracts, tests and repository ownership;
13. identify the actual gap;
14. determine whether the gap belongs to BeeDrill, BeeAgent, BeeSDK or another repository;
15. determine whether companion changes are genuinely necessary;
16. assess necessity and timing;
17. compare valid solution options;
18. choose the planning decision;
19. prepare roadmap output, Issues and handoff.

Do not read repositories indiscriminately.

## Required inspection

Read at minimum in the primary BeeDrill repository:

- `AGENTS.md`;
- the candidate roadmap and neighbouring items;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- `.github/ISSUE_TEMPLATE/issue.md`;
- relevant architecture or product-contract documentation;
- relevant implementation;
- relevant tests.

Read as applicable:

- `README.md`;
- `README.ru.md` if it exists;
- `docs/ARCHITECTURE.md`;
- `docs/DEV_GUIDE.md`;
- `docs/SPEC.md`;
- `pyproject.toml`;
- `CHANGELOG.md` if present;
- `src/beedrill/__init__.py`;
- module entrypoint;
- domain models;
- scenario models;
- evidence models;
- verdict engine;
- fixtures;
- artifact contracts;
- integration adapters;
- package/build configuration;
- top-level public exports;
- BeeSDK contract usage;
- BeeAgent integration contract.

### For module-contract work

Inspect:

- BeeDrill module entrypoint;
- BeeSDK public module contracts;
- BeeAgent module runtime/registry contracts as required;
- relevant tests;
- artifact port compatibility;
- authority semantics.

### For scenario/domain work

Inspect:

- `docs/SPEC.md`;
- relevant scenario/domain models;
- fixtures;
- validators;
- serialization;
- verdict expectations;
- current scenario tests.

### For verdict/metrics work

Inspect:

- evidence contracts;
- metric definitions;
- verdict rules;
- missing/inconsistent evidence behavior;
- deterministic tests;
- replay fixtures.

### For Surfpool/execution work

Inspect BeeDrill and the relevant BeeAgent host implementation.

Determine:

- which repository owns process lifecycle;
- which repository owns RPC configuration;
- how execution authority is bounded;
- whether target allowlisting exists;
- whether timeouts and cleanup exist;
- whether current BeeAgent capabilities are sufficient;
- whether a BeeAgent change is actually required.

Do not move execution into BeeDrill because host integration is inconvenient.

### For package/build work

Inspect:

- `pyproject.toml`;
- package layout;
- package data;
- relevant build/import tests;
- dependency declarations;
- version source of truth.

### For BeeSDK-related work

Inspect only enough BeeSDK context to determine:

- whether an existing public contract already covers the need;
- whether BeeDrill can solve the requirement consumer-side;
- whether a new stable shared contract is genuinely required;
- compatibility and sequencing.

BeeSDK is contract-only until a shared gap is proven.

### For BeeAgent-related work

Inspect only enough BeeAgent context to determine:

- whether the required host capability already exists;
- whether existing module/runtime boundaries are sufficient;
- whether execution belongs in BeeAgent;
- whether a dedicated BeeAgent Issue is required;
- compatibility and implementation order.

An additional repository is context-only until a required change is proven.

## Current state and actual gap

Determine:

- current stage;
- current roadmap iteration;
- completed neighbouring items;
- active planned work;
- prerequisite status;
- future and deferred scope;
- stale or duplicate roadmap items;
- current implementation;
- current public contracts;
- current scenario coverage;
- current evidence/verdict behavior;
- tests;
- package behavior;
- blockers and limitations;
- implementation-roadmap drift;
- whether the task is already delivered;
- whether another item covers it.

Roadmap status is not implementation evidence.

Classify relevant drift as:

```text
implementation ahead of roadmap
roadmap ahead of implementation
stale future scope
duplicated scope
duplicated iteration ID
completed-history documentation debt
blocking contract gap
host integration gap
BeeSDK compatibility gap
security-boundary gap
scenario/evidence gap
intentional sequencing difference
separate follow-up
```

Do not create a feature solely to repair stale documentation.

State the verified gap using:

- current behavior;
- required behavior;
- evidence of absence or insufficiency;
- product impact;
- architecture impact;
- security impact;
- compatibility impact when applicable;
- why it matters now.

Separate real gaps from:

- documentation drift;
- local defects;
- contract mismatches;
- BeeAgent-local implementation needs;
- BeeSDK-shared contract needs;
- future ideas;
- optional polish;
- hackathon optics without product value.

## Necessity verdict

Return exactly one:

```text
necessary now
necessary after prerequisite
useful but defer
already covered
already implemented
standalone maintenance
not justified
```

Consider:

- direct contribution to BeeDrill product thesis;
- roadmap sequencing;
- prerequisite readiness;
- security value;
- objective evidence value;
- current contracts;
- implementation ownership;
- architecture debt;
- compatibility;
- cross-repository cost;
- hackathon delivery window;
- risk of displacing higher-priority product proof.

Do not approve work only because it is technically possible.

Do not approve work only because it would look impressive in a demo.

Provide concise evidence-based project-development advice when useful.

## Roadmap ownership

### BeeDrill roadmap

Use:

```text
docs/ROADMAP.md
```

for:

- BeeDrill product behavior;
- security-control validation semantics;
- scenario models and scenario classes;
- evidence contracts owned by BeeDrill;
- deterministic metrics;
- verdict behavior;
- scenario corpus;
- BeeDrill package/public API;
- BeeDrill artifact/report semantics;
- BeeDrill-specific integrations;
- regression-suite behavior;
- BeeDrill product hardening.

### BeeAgent roadmap

Use BeeAgent's roadmap for:

- orchestration;
- module registry;
- runtime context creation;
- process execution;
- Surfpool lifecycle;
- RPC execution;
- runtime state;
- credentials;
- policy;
- authority enforcement;
- capability execution;
- storage implementation;
- external connectors;
- execution/egress;
- host-level timeouts and cleanup.

Do not move host runtime implementation into BeeDrill.

### BeeSDK roadmap

Use BeeSDK's roadmap for:

- reusable shared public contracts;
- shared protocols/enums/data shapes;
- shared module boundary;
- shared artifact port;
- shared capability caller/result contracts;
- public typing compatibility;
- package/build compatibility.

Do not add BeeDrill-specific:

```text
Solana models
scenario semantics
attack semantics
detector semantics
containment semantics
metrics
verdicts
```

to BeeSDK.

### BeeUI roadmap

Use BeeUI's own roadmap only for generic reusable presentation capabilities.

Do not introduce BeeUI work merely because a dashboard could be useful.

The current hackathon product proof does not require a large web UI.

### BeeScan roadmap

BeeScan owns scanning/pentesting capabilities specific to BeeScan.

Do not move BeeScan implementation into BeeDrill.

Do not make BeeDrill wait for BeeScan unless a real shared dependency is approved.

## Repository ownership

Apply the full architecture rules from `AGENTS.md`.

Verify that:

### BeeDrill owns

- security-control-validation domain models;
- scenario identity and semantics;
- target semantics specific to drills;
- attack expectations;
- expected-control semantics;
- evidence interpretation;
- MTTD/MTTC semantics;
- economic outcome metrics;
- deterministic verdict rules;
- scenario corpus;
- BeeDrill-specific report semantics;
- BeeDrill package/public behavior.

### BeeAgent owns

- orchestration;
- module registry;
- runtime and session state;
- runtime context creation;
- process execution;
- Surfpool lifecycle;
- RPC access;
- credentials and secrets;
- policy and approvals;
- execution authority;
- storage/artifact implementation;
- connectors;
- timeouts;
- host-level cleanup;
- runtime logging;
- external-system execution.

### BeeSDK owns

- shared public contracts;
- shared protocols;
- reusable enums and bounded data shapes;
- shared module boundary;
- shared artifact/capability boundary;
- typing/public compatibility.

### BeeUI owns

- generic rendering;
- layouts;
- reusable presentation components;
- generic UI behavior.

### BeeScan owns

- BeeScan-specific security scanning;
- scan orchestration;
- findings taxonomy;
- scan-tool integration;
- BeeScan security workflows.

Do not:

- move BeeAgent runtime into BeeDrill;
- move BeeDrill domain semantics into BeeSDK;
- duplicate BeeSDK contracts in BeeDrill;
- duplicate BeeAgent host behavior in BeeDrill;
- use scenario-controlled data as runtime authority;
- create a second source of truth;
- introduce reverse dependency from BeeSDK to BeeDrill;
- make BeeDrill depend on BeeROP;
- hide multiple repository implementations inside one Issue.

## Security-planning rules

### Scenario data is untrusted

Treat scenario and fixture data as untrusted input.

Do not plan contracts that permit scenario data to directly control:

```text
arbitrary executable
arbitrary command line
arbitrary filesystem path
arbitrary RPC endpoint
production credential
runtime authority
host identity
policy override
```

### Execution remains host-owned

If a BeeDrill scenario requires execution, describe the bounded execution intent.

The host owns the actual execution boundary.

### Mainnet safety

For the hackathon MVP:

```text
production/mainnet mutation
= excluded
```

Planning must reject hidden production mutation paths.

### Fail-closed verdicts

Missing or inconsistent critical evidence must not silently become PASS.

### AI authority

Do not plan LLM output as final security authority.

AI may:

- explain evidence;
- assist authoring;
- summarize;
- suggest remediation.

AI must not determine critical PASS/FAIL where deterministic evidence is available.

## Planning decision

Choose exactly one:

```text
reuse
refine
replace
insert
standalone
reject as unnecessary
```

### Reuse

Use when an unfinished roadmap item already covers the verified task without material changes.

Identify the exact roadmap, stage and iteration.

Do not generate duplicate roadmap wording.

### Refine

Use when an unfinished item is directionally correct but needs clearer:

- product scope;
- ownership;
- security boundary;
- acceptance criteria;
- sequencing;
- checks.

Do not refine completed history.

### Replace

Use when unfinished future scope is stale, unnecessary or based on the wrong architecture/product boundary.

Show:

- replaced item;
- reason;
- replacement;
- downstream impact.

### Insert

Use when no existing item covers a verified coherent gap.

A new item must:

- close a current product gap;
- have one coherent deliverable;
- respect repository ownership;
- have observable acceptance criteria;
- fit focused repository Issues;
- fit the current delivery window;
- match current BeeDrill direction.

### Standalone

Use only for genuinely small maintenance outside numbered product flow.

### Reject as unnecessary

Use when:

- behavior already exists;
- another task covers it;
- the proposal duplicates a source of truth;
- the functionality belongs entirely to another repository;
- the idea is premature;
- the architecture is speculative;
- it does not materially advance the BeeDrill product thesis;
- it introduces unnecessary risk during the hackathon window.

Explain the simpler alternative where applicable.

## Iteration versus standalone

A numbered BeeDrill iteration is normally required for substantial changes to:

- product behavior;
- scenario contracts;
- attack scenario classes;
- evidence contracts;
- verdict semantics;
- metrics;
- security boundaries;
- execution integration;
- host integration;
- package/public API;
- artifact contracts;
- dependency surface;
- CI/regression behavior;
- external product integrations;
- another testable reusable BeeDrill capability.

Standalone is normally appropriate for:

- typo or formatting fixes;
- narrow documentation alignment;
- small test corrections;
- housekeeping;
- a narrow local bug without product-contract impact;
- small skill/prompt maintenance;
- small packaging fixes without new public behavior.

Documentation should normally accompany technical work rather than become a separate roadmap iteration.

## Solution options

Present no more than three materially valid options.

For each option state:

- repository and roadmap ownership;
- implementation boundary;
- existing contracts or behavior reused;
- contracts changed, if any;
- advantages;
- disadvantages;
- product impact;
- security impact;
- compatibility impact;
- dependency/sequencing impact;
- main risk.

Recommend one using:

- smallest complete solution;
- strongest reuse;
- correct ownership;
- deterministic evidence;
- no second source of truth;
- minimal execution authority;
- minimum coupling;
- proportionate verification;
- no speculative architecture.

Do not manufacture alternatives.

If one valid solution exists, say so.

## Roadmap reconciliation and numbering

Before changing the roadmap:

1. inspect the referenced item;
2. inspect neighbouring completed and unfinished items;
3. check prerequisites;
4. check overlapping and duplicate scope;
5. check duplicate IDs;
6. compare implementation with roadmap claims;
7. select roadmap, stage and insertion point;
8. preserve completed history;
9. decide whether unfinished items need refinement, retirement or renumbering;
10. check downstream dependencies.

Rules:

- never change or renumber `DONE` IDs;
- never reuse a completed ID;
- never leave duplicate IDs;
- preserve established `BD-` prefix;
- use decimal numbering only for direct continuation when justified;
- use the next suitable `BD-` number for independent work;
- renumber unfinished items only when unavoidable;
- prefer retiring stale future scope over mass renumbering;
- do not synchronize IDs across repositories;
- show an exact retirement or renumbering map when required.

Do not automatically append to the end of the roadmap.

### Hackathon-plan protection

The current roadmap intentionally reserves a submission buffer.

Do not consume the buffer with new planned feature work unless:

- the current product cannot be completed without it; or
- new external evidence materially changes the plan.

Do not casually move BD-15 later merely to accommodate scope expansion.

## Cross-repository planning

Use:

```text
one implementation repository
= one Issue
= one target worktree
= one feature branch
= one PR
```

For every implementation target define:

- responsibility;
- public/integration contract;
- dependency direction;
- prerequisites;
- implementation and merge order;
- compatibility requirements;
- verification condition.

Do not assign companion work without proving the current contract or implementation is insufficient.

### When BeeDrill requires BeeAgent work

Use:

```text
BeeDrill requirement
→ verify existing BeeAgent host capability
→ prove gap
→ separate BeeAgent Issue
→ BeeAgent implementation
→ BeeDrill integration
```

Do not implement the BeeAgent capability in BeeDrill.

### When BeeDrill appears to require BeeSDK work

First ask:

```text
Can this remain BeeDrill-local?
Is the existing BeeSDK contract sufficient structurally?
Is the proposed contract truly reusable?
Is the gap stable across consumers?
```

If BeeSDK change is genuinely required:

1. plan a separate BeeSDK Issue;
2. implement and verify BeeSDK;
3. make the approved BeeSDK revision/release available;
4. update BeeDrill to the actual available contract;
5. run compatibility/integration checks.

Do not invent future BeeSDK versions.

### Additional repositories

An additional project supplied for context is not automatically an implementation target.

Prove necessity before assigning changes.

Run `.agents/prompts/02-implementation-tests.md` separately for every implementation repository Issue.

## Implementation plan

For each implementation target provide:

- repository and responsibility;
- current implementation to reuse;
- verified layers likely to change;
- behavior and contracts to change;
- source of truth;
- package/API impact;
- BeeSDK/BeeAgent compatibility where relevant;
- dependency impact;
- security and authority constraints;
- automated scenarios;
- smoke/integration requirements;
- documentation;
- implementation order;
- completion criteria.

Do not invent exact file paths.

When a file is unconfirmed, name the verified layer and require the executor to confirm the concrete location.

Do not turn the plan into an executor prompt.

## Roadmap output contract

For a numbered item, provide a compact copy-ready fragment with exactly these iteration headings:

```text
Goal
Scope
Excluded
Deliverable
Acceptance criteria
Checks
DoD
```

Use this form:

```text
# Stage <number> — <English stage title>

## Iteration <BD-ID> — <English iteration title>

**Status:** PLANNED

### Goal

<English content>

### Scope

<English content>

### Excluded

<English content>

### Deliverable

<English content>

### Acceptance criteria

<English content>

### Checks

<English content>

### DoD

<English content>
```

Rules:

- all BeeDrill roadmap content is English;
- technical identifiers remain unchanged;
- include only iteration-level information;
- put implementation details in the Issue;
- target 40–60 lines;
- absolute maximum 80 lines;
- do not add extra iteration headings;
- do not repeat an existing stage heading when only an iteration block must be inserted.

For `reuse`, do not generate a duplicate fragment.

For `refine` or `replace`, provide the complete replacement fragment.

For `reject as unnecessary`, provide no fake iteration.

## Standalone output contract

For standalone work provide:

```text
Title:
Classification: standalone
Reason:
Scope:
Excluded:
Deliverable:
Checks:
DoD:
Roadmap insertion required: no
```

Use English.

Do not invent an iteration number.

## Issue preparation

Prepare one complete Issue in English per implementation repository.

Read and follow the target repository's actual:

```text
.github/ISSUE_TEMPLATE/issue.md
```

Rules:

- preserve the actual heading order;
- fill relevant sections;
- use the actual roadmap file;
- use observable and testable requirements;
- keep Issue scope aligned with the roadmap;
- do not duplicate all stable rules from `AGENTS.md`;
- include only task-specific implementation and verification constraints.

For standalone work state:

```text
Iteration: none
```

The Issue must cover as applicable:

- current limitation and why now;
- included scope;
- excluded scope;
- deliverable;
- source of truth;
- product behavior;
- module/public contracts;
- BeeAgent/BeeSDK compatibility;
- deterministic behavior;
- evidence semantics;
- artifact behavior;
- execution boundary;
- isolation requirements;
- dependency impact;
- security and authority constraints;
- automated scenarios;
- integration smoke;
- replay requirements;
- documentation;
- sequencing;
- Acceptance Criteria;
- Definition of Done;
- `version not changed`.

Do not use vague requirements such as:

```text
implement as needed
update relevant tests
follow best practices
handle edge cases
make it robust
support Solana
make it secure
```

Use one change level from current SDLC:

```text
low-risk
runtime-risk
security-sensitive
```

Select proportional checks from `docs/SDLC.md` and `docs/SECURITY.md`.

Without an approved dependency change:

- do not plan dependency changes;
- do not plan lockfile changes;
- require final changed-file inventory to confirm they remain untouched when relevant.

Never require:

```text
uv lock --check
```

Do not propose a version bump unless the task is explicitly release-related.

## Planning handoff constraints

Provide concise task-specific implementation constraints, including only applicable:

- product ownership;
- repository ownership;
- existing implementation to reuse;
- source of truth;
- public/module contract;
- BeeSDK compatibility;
- BeeAgent host boundary;
- deterministic evidence/verdict requirement;
- isolation/mainnet restrictions;
- authority restrictions;
- dependency restrictions;
- sequencing;
- release order;
- version restriction;
- dirty-worktree reconciliation.

Provide concise task-specific verification constraints, including only applicable:

- expected change level;
- Acceptance Criteria scenarios;
- targeted and full tests;
- package build/import smoke;
- BeeAgent module compatibility;
- BeeSDK structural compatibility;
- scenario fixture checks;
- deterministic serialization;
- deterministic verdict checks;
- replay checks;
- artifact checks;
- malformed-input checks;
- forbidden-target checks;
- timeout/cleanup checks;
- secret-leak checks;
- security checks;
- dependency status;
- cross-repository integration checks.

Do not prepare implementation, verification or correction prompts.

Record only material executor complexity factors:

- repository count;
- public/module contract surface;
- package/build impact;
- Solana runtime integration;
- Surfpool/process integration;
- deterministic replay;
- security sensitivity;
- dependency changes;
- cross-repository compatibility;
- release sequencing.

Do not select Copilot or Codex.

## Naming

For each implementation repository provide:

- recommended branch name;
- recommended Conventional Commit title.

Follow current repository conventions.

For BeeDrill iteration branches, prefer names that retain iteration identity when practical, for example:

```text
feature/bd-4-surfpool-host-execution
```

Do not propose:

- commit operations;
- push commands;
- tags;
- invented release numbers.

For ordinary work state:

```text
version not changed
```

## Output format

Return these sections in order:

```text
## Executive verdict
## Repository state
## Current implementation and contracts
## Roadmap selection
## Roadmap reconciliation
## Necessity verdict
## Architecture and repository ownership
## Solution options and recommendation
## Implementation plan
## Iteration numbering and insertion
## Copy-ready roadmap iteration or standalone task
## Copy-ready Issue
```

Use:

```text
## Copy-ready Issues
```

for multiple implementation repositories.

Then return:

```text
## Implementation order
## Verification and security
## Branch and commit naming
## Project-development recommendations
## Planning handoff
```

Add:

```text
## Assumptions or blockers
```

only when needed.

Write all output in English.

Keep:

- technical identifiers unchanged;
- repository names unchanged;
- commands and paths unchanged.

Keep analysis concise and avoid repeating the same evidence across sections.

Do not claim Bee Dev MCP ran tests.

## Planning handoff

Return:

```text
Primary product repository:
Primary roadmap:
Stage:
Iteration:
Decision:
Necessity verdict:
Implementation targets:
Issue count:
Execution order:
Required separate prompt-02 runs:
Source of truth:
Public contracts:
Compatibility requirements:
Task-specific implementation constraints:
Task-specific verification constraints:
Executor complexity factors:
Version status:
```

For standalone work:

```text
Iteration: none
```

For rejected work:

```text
Implementation targets: none
Issue count: 0
Required separate prompt-02 runs: 0
```

Do not create:

- planning artifact files;
- automatic roadmap edits;
- automatic Issues;
- branches;
- commits;
- PRs.

Do not modify or execute anything.
