### Summary

What was done in this PR.

Include short, concrete statements:

- what behavior / contract changed;
- what files / modules were touched;
- what was intentionally not changed.

### Related issue

Closes #

If relevant, also reference:

- ROADMAP iteration:
- related docs:
- affected integration:
- follow-up issues:

### Iteration

- Iteration:
- Goal:
- Change level:
  - [ ] low-risk
  - [ ] runtime-risk
  - [ ] security-sensitive

> Use the current iteration from `docs/ROADMAP.md`.
> Change level should match `docs/SDLC.md` / `docs/SECURITY.md`.

### Scope

What is included / excluded.

**Included**

- ...
- ...

**Excluded**

- ...
- ...

### Changes

- ...
- ...
- ...

### Package / Public API / Contract impact

Mark what changed:

- [ ] no package, public API or contract changes
- [ ] top-level public exports changed
- [ ] module integration contract changed
- [ ] scenario / domain contract changed
- [ ] evidence contract changed
- [ ] metrics / verdict contract changed
- [ ] artifact / report contract changed
- [ ] BeeAgent compatibility changed
- [ ] BeeSDK compatibility changed
- [ ] package metadata / build behavior changed
- [ ] runtime dependency surface changed
- [ ] backward compatibility / migration behavior changed
- [ ] docs updated

If applicable, specify:

**New / changed public exports**

- `...`

**New / changed contracts**

- `...`

**New / changed package metadata**

- `...`

**Compatibility / migration impact**

- `...`

### Verification level

Required checks for this PR.

**Base checks**

- [ ] `uv run pytest -q`
- [ ] `uv build` when package / build behavior is affected
- [ ] package import smoke completed when applicable
- [ ] public / module API behavior checked when applicable

**Integration / regression checks**

- [ ] BeeSDK compatibility checked when required
- [ ] BeeAgent module compatibility checked when required
- [ ] scenario / fixture behavior checked when required
- [ ] deterministic replay checked when required
- [ ] runtime / external integration smoke completed when required

**Quality / security checks**

Mark only what is required for this PR:

- [ ] SAST completed
- [ ] SCA completed
- [ ] DAST completed
- [ ] IAST completed
- [ ] fuzzing completed
- [ ] not applicable (explained in Notes)

> Only mark checks that are required for this change level.
> Use `docs/SDLC.md` and `docs/SECURITY.md` as source of truth.

#### Test details

Commands / scenarios used:

- `...`
- `...`

Include automated, integration, replay, and compatibility verification when relevant.

#### Manual scenarios checked

- ...
- ...
- ...

### Artifacts

What was created or verified:

- ...
- ...
- ...

If applicable, list exact files, for example:

- `tests/...`
- `src/beedrill/...`
- `README.md`
- `CHANGELOG.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/SPEC.md`
- `docs/SECURITY.md`
- `docs/DEV_GUIDE.md`
- `pyproject.toml`
- `uv.lock`
- built wheel / source distribution
- bounded scenario / evidence / report artifacts

### Security review

Fill only if relevant for this PR:

- execution / authority boundary affected:
- isolated environment / RPC boundary affected:
- scenario or untrusted input affected:
- serialization / parsing changed:
- external integration affected:
- secret / private-key handling affected:
- runtime dependency surface changed:
- cross-repository compatibility required:

### Checklist

#### SDLC / scope

- [ ] change stays within current iteration / declared standalone scope
- [ ] Issue, code, tests, docs, and PR are aligned
- [ ] `docs/ROADMAP.md` updated if roadmap status or planned contract changed
- [ ] related docs updated if needed (`DEV_GUIDE`, `README.md`, `SPEC`, `SDLC`, `SECURITY`, `ARCHITECTURE`)

#### Package / public API / contracts

- [ ] public exports remain explicit when applicable
- [ ] BeeDrill / BeeAgent / BeeSDK ownership remains consistent with repository contracts
- [ ] backward compatibility is preserved or migration is documented
- [ ] scenario / evidence / verdict boundaries remain explicit when affected
- [ ] runtime dependencies remain unchanged unless explicitly approved
- [ ] package builds and imports as expected when applicable

#### Security

- [ ] no secrets, production private keys, or unrelated private data committed
- [ ] dependency changes were reviewed when applicable
- [ ] security checks required for this PR were completed
- [ ] execution / authority changes were reviewed when applicable

#### Code quality

- [ ] change follows KISS
- [ ] no unnecessary abstraction / refactor was added
- [ ] public / module API remains minimal
- [ ] project style respected

#### Version / release

- [ ] no version change required
- [ ] version / changelog change is intentional and release-related
- [ ] breaking compatibility impact is explicitly documented if applicable

### Limitations / follow-ups

Anything intentionally left out of scope:

- ...
- ...

### Notes

Anything important for reviewer.

Examples:

- why some checks are marked not applicable;
- known limitations;
- compatibility notes;
- migration / deprecation notes;
- what to inspect first during review.
