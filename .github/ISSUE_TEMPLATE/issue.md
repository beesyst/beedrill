---
name: Issue
about: "Use title prefixes: Feature:, Fix:, Docs:, Chore:, Idea:"
title: "Feature: <short title>"
labels: []
assignees: []
---

### Summary

One sentence: what needs to be done or explored.

### Type

Select one primary type:

- [ ] Feature
- [ ] Fix
- [ ] Docs
- [ ] Chore
- [ ] Idea

### Roadmap / iteration

- Iteration:
- Stage:
- Goal from `docs/ROADMAP.md`:

If this is not tied to a roadmap iteration, explain why.

### Context

Why this matters.

Include:

- current problem / limitation;
- why now;
- related Issue / PR / roadmap item if any;
- affected integration if relevant (`beeagent`, `beesdk`, `beeui`, external detector, Solana environment, etc.).

### Scope

What is included / excluded.

**Included**

- ...
- ...

**Excluded**

- ...
- ...

### Deliverable

What should exist when this is done.

Examples:

- new or updated BeeDrill domain contract;
- new scenario behavior;
- updated evidence contract;
- updated metrics or deterministic verdict behavior;
- updated module integration;
- compatibility fix;
- updated artifact / report behavior;
- package / build metadata update;
- documentation update.

### Acceptance Criteria

What must be true for this task to be considered done.

- ...
- ...
- ...

Keep criteria observable and testable.

### Change level

Choose one:

- [ ] low-risk
- [ ] runtime-risk
- [ ] security-sensitive

> Use `docs/SDLC.md` / `docs/SECURITY.md` to classify the task.

### Package / Public API / Contract impact

Mark what is expected:

- [ ] no package, public API or contract change expected
- [ ] top-level public exports may change
- [ ] module integration contract may change
- [ ] scenario / domain contract may change
- [ ] evidence contract may change
- [ ] metrics / verdict contract may change
- [ ] artifact / report contract may change
- [ ] BeeAgent compatibility may change
- [ ] BeeSDK compatibility may change
- [ ] package metadata / build behavior may change
- [ ] runtime dependency surface may change
- [ ] backward compatibility / migration impact expected
- [ ] docs update likely required

If known already, list affected files / exports / contracts:

- `...`
- `...`

### Tests

What must be checked.

**Automated**

- [ ] unit / contract tests
- [ ] `uv run pytest -q`

**Package / integration**

- [ ] `uv build`
- [ ] package import smoke
- [ ] public / module API verification
- [ ] BeeAgent module compatibility smoke if applicable
- [ ] BeeSDK contract compatibility if applicable
- [ ] scenario / fixture verification if applicable
- [ ] deterministic replay verification if applicable
- [ ] runtime / external integration smoke if applicable

**Quality / security**

Mark what is expected for this task:

- [ ] SAST
- [ ] SCA
- [ ] DAST
- [ ] IAST
- [ ] fuzzing
- [ ] some checks are not applicable

Describe the required scenarios briefly:

- ...
- ...
- ...

### Artifacts

What files / outputs should appear or be updated in tests, docs, package metadata, runtime evidence, or build outputs.

Examples:

- `tests/...`
- `src/beedrill/...`
- `README.md`
- `CHANGELOG.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `docs/SPEC.md`
- `docs/DEV_GUIDE.md`
- `pyproject.toml`
- `uv.lock` if an approved dependency change requires it
- built wheel / source distribution when package verification is required
- bounded scenario / evidence / report artifacts when applicable

### Security notes

Fill if relevant:

- execution / authority boundary involved:
- isolated environment / RPC boundary involved:
- scenario or other untrusted input involved:
- serialization / parsing involved:
- external integration involved:
- secret / private-key handling involved:
- runtime dependency changes involved:
- cross-repository compatibility involved:

### Definition of Done

Task is done when:

- [ ] behavior / contract is implemented within the declared scope
- [ ] public / module API remains explicit and documented when affected
- [ ] backward compatibility is preserved or migration is explicitly documented
- [ ] tests are green
- [ ] package builds successfully when package behavior is affected
- [ ] package imports successfully when package behavior is affected
- [ ] no unintended repository ownership or dependency-direction change was introduced
- [ ] runtime dependencies remain unchanged unless explicitly approved
- [ ] no secrets, production private keys, or unrelated private data are committed
- [ ] checks required by `docs/SDLC.md` / `docs/SECURITY.md` are completed
- [ ] docs are updated when product contract, architecture, security boundary, compatibility, or package behavior changed
- [ ] changelog / version decision is recorded when applicable
- [ ] result is ready to be closed through PR

### Notes

Constraints, assumptions, extra links.

Use this section for:

- follow-up ideas;
- explicit non-goals;
- migration notes;
- reviewer hints;
- compatibility notes;
- implementation constraints.
