# AGENTS.md — BeeDrill repository guidance

## Purpose

This file contains stable repository-wide rules for AI agents working with
`beedrill`.

Task-specific requirements belong in the approved Issue.

Detailed workflows belong in `.agents/skills/`.

Prompts should normally contain only:

- selected workflow;
- exact target information;
- approved Issue;
- implementation or verification evidence;
- task-specific constraints.

BeeDrill is a Solana security-control validation module for BeeAgent.

Its primary product responsibility is to validate whether technical defenses
actually detect and contain reproducible attacks under controlled conditions.

BeeDrill is not a second BeeAgent runtime.

## Instruction precedence

Use this order:

1. Current explicit task instructions and approved Issue.
2. This `AGENTS.md`.
3. Selected repository skill.
4. Current repository contracts and documentation.
5. Implementation reports and previous comments as supporting evidence only.

The actual target worktree, current files, diff, tests, package metadata,
runtime evidence and integration evidence take precedence over stale reports.

When instructions materially conflict, stop and report the conflict.

## Agent role separation

Tool, authority and read-only restrictions apply only to the current task and
agent.

When producing a prompt for another agent, do not copy the current agent's tool
restrictions unless they are explicitly required for that executor.

Planning, prompt-preparation and final-review tasks may use Bee Dev MCP in
read-only mode.

Implementation and correction prompts are executed by Copilot or Codex.

They must instruct the executor to work in the exact local worktree using its
available repository tools.

They must not require:

- Bee Dev MCP;
- MCP target identifiers;
- MCP Mode;
- review mode;
- read-only behavior.

## Bee Dev MCP rules

These rules apply only when the current task explicitly selects Bee Dev MCP for
read-only planning, prompt preparation or review.

Bee Dev MCP is read-only.

Available Bee Dev MCP tools include:

- `list_projects`;
- `list_worktrees`;
- `get_project_context`;
- `get_review_manifest`;
- `get_review_bundle_page`;
- `get_review_bundle` — compatibility only;
- `read_project_file`;
- `search_project`;
- `get_github_context`.

Do not refer to nonexistent tools such as `get_file`.

Use:

- `get_review_manifest`;
- `get_review_bundle_page`;

for complete reviews.

Do not repeatedly call `get_review_bundle` expecting pagination.

### GitHub context resolution

When any supplied input contains a supported GitHub Issue or Pull Request URL,
call `get_github_context` before interpreting that input.

For an Issue, read and consider:

- title;
- body;
- all available Issue comments.

For a Pull Request, read and consider:

- title;
- body;
- all available conversation comments;
- reviews;
- inline review comments.

A GitHub URL is an instruction to load its complete available context, not
merely a reference to include in the output.

When pasted content and a GitHub URL are supplied together, consider both.

If they materially conflict, report the conflict instead of silently choosing
one.

Comments provide context and do not automatically expand the approved scope.

Explicit accepted clarifications may refine the Issue or PR contract.

If mandatory GitHub context is unavailable, incomplete or reported as
truncated, return the applicable incomplete-workflow result instead of
proceeding from partial context.

### Exact target resolution

Before planning or review:

1. call `list_worktrees`;
2. match the requested worktree by exact `path`;
3. use the returned MCP `target`;
4. call `get_project_context`;
5. verify project, path, branch, HEAD and dirty state.

For final review, verify the expected base branch from the complete review
manifest.

Do not infer a target from a branch name.

Do not substitute the main worktree for a requested feature worktree.

### Complete reading

Repository inspection is incomplete while required data is:

- paginated;
- truncated;
- omitted;
- accompanied by continuation metadata.

For manifests and diffs, continue with the exact `next_cursor` while
`has_more=true`.

For files, continue with the exact `next_line` and `next_column` until both are
null.

Read required files listed under `omitted_files` or `related_omitted_files`
directly with `read_project_file`.

Treat `truncated=true` as incomplete review data.

Failure to retrieve mandatory MCP data is not a code defect.

When mandatory final-review inspection cannot be completed, return:

```text
REVIEW INCOMPLETE
```

Do not return `CHANGES REQUIRED` solely because MCP inspection is incomplete.

## Mandatory reading

Read documents required by the selected skill.

Common documents include:

- `AGENTS.md`;
- approved Issue;
- relevant `docs/ROADMAP.md` section;
- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- `docs/DEV_GUIDE.md`;
- `README.md`.

When relevant, also read:

- `docs/ARCHITECTURE.md`;
- `docs/SPEC.md`;
- `pyproject.toml`;
- `CHANGELOG.md` if present;
- BeeDrill public/module contracts;
- scenario contracts;
- evidence contracts;
- verdict/metrics contracts;
- BeeSDK public contracts;
- relevant BeeAgent host/runtime contracts;
- related repository ROADMAPs and public contracts.

ROADMAP status does not prove implementation.

Compare roadmap claims with current:

- code;
- contracts;
- tests;
- package metadata;
- runtime behavior;
- integration evidence.

## Product boundary

BeeDrill validates technical security controls protecting Solana protocols.

Target product flow:

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

Core principle:

```text
Audits test whether code can be broken.
BeeDrill tests whether defenses actually stop the damage.
```

BeeDrill is not primarily:

- a vulnerability scanner;
- a generic AI pentester;
- a generic blockchain simulator;
- an incident-response chatbot;
- a SIEM;
- a SOC platform;
- a generic workflow engine;
- a multi-chain framework.

Do not expand the product into adjacent categories without an approved product
and roadmap decision.

## Architecture boundary

Canonical responsibility direction:

```text
BeeSDK
→ shared contracts

BeeAgent
→ host runtime
→ orchestration
→ controlled execution

BeeDrill
→ security-control-validation domain behavior
```

Canonical execution flow:

```text
BeeDrill scenario / domain intent
→ approved shared or host boundary
→ BeeAgent-controlled runtime
→ isolated Solana environment / detector / control
→ bounded evidence
→ BeeDrill validation
→ deterministic verdict
```

### BeeDrill owns

- drill-specific domain models;
- target semantics specific to drills;
- scenario identity and semantics;
- attack expectations;
- expected-control semantics;
- evidence validation and interpretation;
- MTTD semantics;
- MTTC semantics;
- economic outcome metrics;
- deterministic verdict rules;
- scenario corpus;
- BeeDrill-specific artifacts and reports;
- BeeDrill package/public behavior.

### BeeAgent owns

- orchestration;
- runtime and session state;
- module registry and loading;
- runtime context creation;
- process/subprocess execution;
- Surfpool lifecycle;
- Solana RPC execution;
- credentials and secrets;
- approvals;
- execution authority;
- policy enforcement;
- runtime timeouts;
- host-level cleanup;
- artifact/storage implementation;
- connectors;
- execution and egress;
- runtime logging and observability.

### BeeSDK owns

- proven reusable shared public contracts;
- shared protocols;
- reusable enums and bounded data shapes;
- shared module boundary semantics;
- artifact port contracts;
- capability caller/result contracts where applicable;
- shared type compatibility.

BeeSDK must not acquire BeeDrill-specific:

- Solana attack semantics;
- scenario models;
- detector semantics;
- containment semantics;
- metrics;
- verdict rules.

### BeeUI owns

- generic rendering;
- reusable presentation components;
- generic layouts;
- generic UI/session/presentation behavior.

BeeUI integration is not required merely because a visual dashboard would be
useful.

### BeeScan owns

- BeeScan-specific scanning behavior;
- scan orchestration;
- finding taxonomy;
- security-tool execution;
- BeeScan-specific workflows.

BeeDrill does not depend on BeeScan for the hackathon MVP unless an approved
future contract explicitly requires it.

## Architecture prohibitions

Do not:

- create a second BeeAgent runtime inside BeeDrill;
- move generic runtime orchestration into BeeDrill;
- move unrestricted process execution into BeeDrill;
- move host policy or authority decisions into BeeDrill;
- move production credential ownership into BeeDrill;
- move generic storage implementation into BeeDrill;
- duplicate BeeSDK public contracts;
- move BeeDrill domain semantics into BeeSDK;
- import private BeeAgent internals when a public/shared boundary exists;
- use scenario-controlled input to grant runtime authority;
- bypass host-owned approval, capability or policy boundaries;
- create a second source of truth;
- introduce speculative abstractions without demonstrated product need.

## Dependency direction

BeeDrill may depend on BeeSDK public contracts.

BeeDrill must not require BeeSDK to depend on BeeDrill.

Shared contract direction:

```text
beedrill
→ beesdk
```

Host/module integration must preserve architecture ownership.

Do not introduce circular dependencies merely to simplify integration.

A related repository is not an implementation target unless the approved Issue
explicitly assigns changes to it.

## Sources of truth

Use:

- package metadata and package version:
  - `pyproject.toml`;

- package dependency declarations:
  - `pyproject.toml`;

- resolved development environment:
  - `uv.lock`;

- public import surface:
  - `src/beedrill/__init__.py`;

- BeeDrill implementation:
  - `src/beedrill/`;

- product specification:
  - `docs/SPEC.md`;

- architecture and ownership boundaries:
  - `docs/ARCHITECTURE.md`;

- development and integration guidance:
  - `docs/DEV_GUIDE.md`;

- security and trust boundaries:
  - `docs/SECURITY.md`;

- development/change workflow:
  - `docs/SDLC.md`;

- iteration scope:
  - approved Issue aligned with `docs/ROADMAP.md`;

- behavior and compatibility evidence:
  - tests;
  - deterministic fixtures;
  - runtime evidence;
  - verified BeeAgent/BeeSDK integration where applicable.

Rules:

- no hidden defaults for required security behavior;
- no duplicate source of truth;
- package metadata must remain internally consistent;
- public exports must be explicit;
- type and protocol contracts are compatibility surfaces;
- scenario data is not execution authority;
- evidence is not execution authority;
- runtime identity and policy remain host-owned;
- preserve compatibility unless the approved Issue explicitly permits a
  breaking change.

## Implementation rules

- Stay inside the approved Issue.
- Prefer the smallest complete solution.
- Follow KISS.
- Do not perform unrelated refactoring.
- Do not add speculative architecture.
- Reuse existing contracts and implementation before creating new abstractions.
- Do not duplicate existing contracts or logic.
- Do not create generic frameworks for future scenarios, chains or providers
  without demonstrated current need.
- Preserve BeeDrill/BeeAgent/BeeSDK ownership boundaries.
- Follow PEP 8.
- Keep public identifiers, data fields, artifacts and documentation in English.
- Treat external/scenario values as untrusted.
- Keep security-sensitive authority explicit.
- Preserve deterministic behavior where required by the product contract.
- Fail closed when critical security evidence is missing or invalid.
- Do not change `pyproject.toml.version` for ordinary feature, fix, docs or
  chore work.

When a requested behavior actually belongs to BeeAgent or BeeSDK, do not create
a BeeDrill-local workaround merely to avoid cross-repository ownership.

## KISS rules

Do not add functionality only because it may be useful later.

Examples of speculative scope that require explicit evidence and approval:

- multi-chain abstractions;
- generic plugin frameworks;
- generic scenario DSLs;
- generic process frameworks;
- SaaS scheduler;
- hosted runner fleet;
- marketplace;
- reputation systems;
- generic security scoring;
- large dashboard/UI;
- x402 integration unrelated to the current product proof.

The correct solution may be:

```text
no change
```

when existing contracts and implementation already satisfy the requirement.

## Documentation and contracts

Update relevant documentation when implementation changes:

- public/module API;
- scenario contract;
- evidence contract;
- metrics/verdict semantics;
- artifact/report contract;
- package/build behavior;
- compatibility guarantee;
- BeeAgent integration boundary;
- BeeSDK integration boundary;
- authority or security boundary;
- dependency direction;
- execution/isolation assumptions.

Do not update unrelated documentation.

When public fields, signatures, exports or artifact formats change:

- identify the source of truth;
- document compatibility impact;
- preserve existing behavior when required;
- update contract tests;
- verify exports where applicable;
- verify affected BeeAgent/BeeSDK compatibility when required by the Issue.

Implementation convenience is not sufficient reason to broaden a public
contract.

## Determinism rules

Critical security-control outcomes must be deterministic.

Where the product contract requires a verdict:

```text
same valid evidence
→ same metrics
→ same verdict
```

Critical PASS/FAIL must not depend solely on:

- LLM confidence;
- free-form prose;
- undocumented heuristics;
- hidden manual overrides.

AI may:

- explain evidence;
- assist scenario authoring;
- summarize results;
- suggest remediation.

AI must not become the final authority for a deterministic security verdict.

## Evidence rules

Evidence may support:

- detection status;
- containment status;
- timing;
- economic outcome;
- verdict calculation.

Evidence must not grant:

- runtime authority;
- credentials;
- execution identity;
- host policy;
- new RPC permissions;
- new process permissions.

Missing, malformed, incomplete or inconsistent critical evidence must not
silently produce PASS.

Use the explicit behavior defined by the relevant contract, such as:

```text
fail
degraded
refused
incomplete
```

## Execution and isolation rules

For the hackathon MVP:

```text
production/mainnet mutation
= out of scope
```

Attack execution must be restricted to explicitly approved isolated
environments.

Scenario or module-controlled input must not directly grant or override:

- arbitrary executable selection;
- arbitrary command-line execution;
- arbitrary filesystem access;
- arbitrary RPC destination;
- production credentials;
- runtime identity;
- execution authority;
- host policy.

Execution must remain within the approved host/runtime boundary.

A design equivalent to:

```text
scenario input
→ arbitrary subprocess
```

is prohibited unless an explicitly approved future architecture defines and
secures that exact boundary.

## Dependency and lockfile policy

Do not run, request or require:

```text
uv lock --check
```

or another dedicated lockfile validation.

When an approved Issue has no dependency change:

- do not regenerate `uv.lock`;
- do not modify `uv.lock`;
- do not separately validate `uv.lock`.

When an approved dependency change exists:

- make only the necessary dependency change;
- inspect only the relevant lockfile diff;
- justify the dependency;
- perform applicable SCA.

Keep the dependency surface minimal.

Do not add a dependency merely to avoid a small, clear implementation.

## Verification

Determine the actual change level from:

- `docs/SDLC.md`;
- `docs/SECURITY.md`;
- the actual resulting behavior.

Supported levels:

- `low-risk`;
- `runtime-risk`;
- `security-sensitive`.

Run checks proportional to the change.

As applicable, verification may include:

- targeted tests;
- `uv run pytest -q`;
- `uv build`;
- package import smoke;
- public/module API checks;
- BeeSDK contract compatibility;
- BeeAgent module compatibility;
- package metadata inspection;
- dependency-direction checks;
- scenario/fixture validation;
- deterministic serialization tests;
- deterministic metric/verdict tests;
- replay tests;
- artifact verification;
- Surfpool lifecycle smoke;
- Solana RPC smoke;
- detector integration smoke;
- containment integration smoke;
- forbidden-target tests;
- malformed-input tests;
- authority-boundary tests;
- timeout tests;
- cleanup tests;
- secret-leak checks;
- SAST;
- SCA;
- DAST;
- IAST;
- fuzzing where justified by a parser or attack surface.

Do not require every security tool for every change.

Use only checks justified by:

- approved Issue;
- actual change level;
- current security surface.

Review agents using Bee Dev MCP cannot execute commands.

They may use supplied command output as evidence but must:

- identify the supplied command;
- distinguish reported evidence from inspected code;
- verify that required scenarios are covered;
- never claim MCP ran tests.

Missing verification is blocking only when required by:

- approved Issue;
- SDLC;
- security rules.

## Security

- Never expose secrets, tokens, passwords, private keys or complete environment
  dumps.
- Do not place production credentials or private keys in fixtures.
- Treat scenario/configuration input as untrusted.
- Keep runtime authority host-owned.
- Scenario-controlled payload must not grant, override or escalate authority.
- Evidence must not become authority.
- Production/mainnet mutation is outside the current MVP.
- Restrict attack execution to approved isolated environments.
- Keep RPC targets bounded where execution is involved.
- Keep process execution bounded where execution is involved.
- Require timeout and cleanup for security-sensitive process execution when
  applicable.
- Do not allow arbitrary filesystem paths from untrusted scenario input.
- Do not leak secrets into artifacts, logs or tests.
- Missing critical evidence must not silently become PASS.
- Keep critical verdicts deterministic.
- Preserve dependency direction and repository ownership.
- External execution or egress requires explicit approved scope and security
  review.

## Cross-repository work

Use this rule:

```text
one implementation repository
= one Issue
= one target worktree
= one feature branch
= one PR
```

A BeeDrill task may reveal a requirement in another repository.

Correct flow:

```text
BeeDrill evidence
→ identify repository ownership
→ verify existing capability
→ prove the gap
→ separate Issue in owning repository
→ implementation
→ integration
```

Examples:

```text
scenario/verdict behavior
→ BeeDrill

Surfpool/process/RPC host capability
→ BeeAgent

stable reusable shared contract
→ BeeSDK, only when proven necessary

generic presentation primitive
→ BeeUI
```

Do not hide several repository implementations inside one BeeDrill Issue unless
the approved task explicitly defines coordinated work and separate repository
targets.

## Review rules

Review the exact requested target relative to the declared base branch.

Inspect:

- committed changes;
- staged changes;
- unstaged changes;
- untracked files;
- deleted and renamed files;
- complete changed-file contents;
- relevant unchanged contracts;
- package metadata;
- related BeeAgent/BeeSDK contracts when explicitly required;
- supplied verification evidence.

Prioritize blockers that affect the current Issue:

- unmet Acceptance Criteria;
- incorrect product behavior;
- security or authority violation;
- production/mainnet boundary violation;
- scenario-controlled execution escalation;
- BeeDrill/BeeAgent ownership violation;
- BeeDrill/BeeSDK ownership violation;
- conflicting sources of truth;
- incompatible contracts;
- deterministic-verdict violation;
- invalid evidence handling;
- package/build regressions;
- unintended dependencies;
- missing required verification;
- unrelated changes entering the PR;
- unintended version changes;
- documentation contradicting actual behavior;
- missing required cross-repository dependency.

Do not make blockers from:

- optional polish;
- personal naming preferences;
- speculative architecture;
- unrelated cleanup;
- future product ideas;
- requirements absent from the approved Issue.

Perform one complete review pass and consolidate all real blockers.

Use:

- `.agents/skills/beedrill-plan-iteration/SKILL.md` for planning;
- `.agents/skills/beedrill-implement-issue/SKILL.md` for implementation;
- `.agents/skills/beedrill-verify-and-correct/SKILL.md` for independent
  verification and correction;
- `.agents/skills/beedrill-review-and-close/SKILL.md` for final review and PR
  preparation.

## Required implementation evidence

The implementation report should contain:

1. target verification;
2. files read;
3. roadmap / iteration;
4. change level;
5. source of truth;
6. BeeDrill / BeeAgent / BeeSDK boundary assessment;
7. changed files;
8. Acceptance Criteria coverage;
9. exact test commands and results;
10. runtime/integration smoke where applicable;
11. deterministic/replay evidence where applicable;
12. artifacts/evidence inspected where applicable;
13. public/module API and compatibility evidence;
14. security review;
15. dependency status;
16. known limitations;
17. recommended Conventional Commit;
18. confirmation:

```text
version not changed
```

unless the approved Issue explicitly requires release versioning.

Narrative claims do not replace exact verification evidence.
