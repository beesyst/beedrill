# SECURITY — BeeDrill

## Purpose

This document defines practical security rules for `beedrill`.

BeeDrill intentionally works with adversarial scenarios and security-control
validation, so its security boundary is stricter than that of a normal domain
library.

BeeDrill itself does not own generic execution infrastructure.

BeeAgent remains responsible for:

- runtime authority;
- policy;
- credentials;
- subprocess execution;
- Surfpool lifecycle;
- Solana RPC execution;
- external egress;
- storage implementation.

BeeDrill is responsible for ensuring its domain inputs and outputs cannot be used
to bypass those host controls.

Use this document with:

- `docs/SPEC.md`;
- `docs/ARCHITECTURE.md`;
- `docs/SDLC.md`;
- `docs/ROADMAP.md`.

## Core security principle

BeeDrill may describe an attack.

It must not grant itself permission to execute arbitrary attacks.

The host/runtime owns:

- identity;
- authority;
- policy;
- execution;
- credentials;
- target approval;
- egress;
- lifecycle.

## What we protect

At minimum BeeDrill protects:

- isolated execution boundary;
- module/host trust boundary;
- scenario/host trust boundary;
- target selection boundary;
- Solana RPC boundary;
- process execution boundary;
- credential boundary;
- evidence integrity;
- verdict integrity;
- artifact boundary;
- dependency integrity;
- package integrity.

## Trust boundaries

Primary trust flow:

```text
scenario / external drill input
    ↓ untrusted
BeeDrill validation
    ↓ bounded intent
BeeAgent host policy
    ↓ approved execution
isolated Solana environment
    ↓ evidence
BeeAgent / integration boundary
    ↓ bounded evidence
BeeDrill deterministic evaluation
```

No step may silently convert untrusted data into host authority.

## Import safety

Importing:

```python
import beedrill
```

must not unexpectedly:

- access the network;
- start Surfpool;
- execute subprocesses;
- load production credentials;
- mutate Solana state;
- start services;
- connect to external systems;
- create runtime storage;
- change host policy.

Package import should remain side-effect free.

## Initial authority

Initial BeeDrill module authority:

```text
read_only
```

This authority is assigned and enforced by the host.

BeeDrill must not escalate it.

A scenario, fixture, model or module result must not change host authority.

## Scenario input is untrusted

Treat scenario-controlled input as untrusted.

Scenario data must not directly control:

```text
arbitrary executable
arbitrary shell command
arbitrary command arguments without validation
arbitrary filesystem path
arbitrary RPC endpoint
production credential
runtime identity
module identity
host authority
host policy
```

A scenario describes domain intent.

It is not a generic execution program.

## Execution boundary

Generic execution belongs to BeeAgent.

Correct model:

```text
scenario intent
    ↓
BeeAgent-owned bounded executor
    ↓
approved isolated environment
```

Forbidden model:

```text
scenario.command
    ↓
subprocess.run(...)
```

unless a future approved architecture defines a narrowly constrained and
security-reviewed execution contract.

## Surfpool isolation

The current MVP uses an isolated Solana environment.

Current rule:

```text
production/mainnet mutation = prohibited
```

A drill must fail closed or refuse execution when the host cannot establish an
approved isolated target.

Do not silently fall back to another RPC environment.

## Solana RPC target control

RPC target selection is host-controlled.

Scenario input must not be able to replace an approved RPC endpoint with an
arbitrary endpoint.

Where RPC execution exists, verify:

- endpoint comes from an approved host source;
- target is the expected isolated environment;
- timeout is bounded;
- failures are explicit;
- no fallback to mainnet occurs.

## Process safety

Process execution is security-sensitive.

Host implementations should provide bounded:

- executable selection;
- arguments;
- environment;
- timeout;
- lifecycle;
- cleanup.

BeeDrill must not widen those controls through scenario payload.

Unexpected process failure must not leave an unmanaged long-running test process
when the host contract requires cleanup.

## Credentials and private keys

BeeDrill does not own production credentials.

Do not commit real:

- Solana private keys;
- seed phrases;
- API tokens;
- RPC credentials;
- service credentials;
- customer secrets.

Fixtures and examples must use synthetic values.

Host/runtime is responsible for credential injection.

Scenario and evidence objects should refer to bounded identities where necessary
without containing production secret material.

## Evidence is not authority

Evidence may describe:

- what happened;
- when it happened;
- what state changed;
- what detector fired;
- what containment happened;
- economic outcome.

Evidence must not grant:

- execution authority;
- new credentials;
- new target access;
- policy overrides;
- approval for a future action.

Security distinction:

```text
evidence != authority
result != approval
payload != trusted identity
```

## Evidence integrity

Critical verdicts depend on evidence quality.

BeeDrill must distinguish:

- valid evidence;
- missing evidence;
- malformed evidence;
- contradictory evidence;
- incomplete evidence.

Missing or invalid critical evidence must not silently produce PASS.

The approved domain contract may represent this as:

```text
FAIL
INCOMPLETE
REFUSED
DEGRADED
```

but a false successful verdict is not acceptable.

## Deterministic verdicts

Critical security verdicts must remain deterministic.

Required property:

```text
same valid evidence
→ same metrics
→ same verdict
```

Do not base critical PASS/FAIL on:

- LLM confidence;
- free-form prose;
- undocumented heuristic judgment;
- reviewer mood;
- hidden manual override.

AI may assist with:

- explanations;
- scenario drafting;
- summaries;
- remediation suggestions.

AI is not the final security authority.

## Detector boundary

BeeDrill may define what detector signal is required.

Detector execution or connection belongs to the approved integration/host
boundary.

When detector evidence is required:

- identify the expected signal;
- validate it deterministically;
- do not treat absence of detector evidence as successful detection;
- reject malformed or contradictory evidence according to the contract.

## Containment boundary

BeeDrill may define expected containment behavior.

Actual control invocation must remain within an approved host/runtime path.

Containment evidence must identify enough state to verify that the intended
control actually acted.

A planned or requested pause is not equivalent to a confirmed containment
effect.

## Economic outcome integrity

Residual-loss calculations influence security verdicts.

Inputs must be explicit and deterministic.

Do not replace measurable economic outcome with a subjective risk score when the
required state is available.

Boundary and arithmetic cases should be tested.

## Artifact boundary

BeeDrill may write structured evidence through a host-owned artifact port.

BeeDrill must not assume unrestricted filesystem access.

Do not introduce arbitrary path APIs from scenario input.

Artifacts must not contain:

- production secrets;
- private keys;
- unbounded environment dumps;
- unrelated customer data.

The host remains responsible for:

- storage root;
- filename/path policy;
- permissions;
- retention;
- operator access.

## External input

Treat external input as untrusted.

Examples:

- scenario definitions;
- RPC responses;
- detector output;
- containment output;
- serialized evidence;
- external tool output.

Validation should be proportional to the contract.

If BeeDrill introduces a parser or complex deserializer, the change becomes
security-sensitive.

## External execution and egress

BeeDrill must not silently introduce:

- HTTP calls;
- arbitrary RPC endpoints;
- shell execution;
- plugin downloads;
- package installation;
- remote code loading.

Any new execution or egress path requires explicit approved scope and security
review.

## Dependency direction

Expected dependency direction:

```text
beedrill -> beesdk
```

BeeSDK must not depend on BeeDrill.

Avoid private implementation imports across repository boundaries.

A reverse or circular dependency can create:

- authority ambiguity;
- hidden runtime coupling;
- duplicated contracts;
- deployment coupling.

## Runtime dependencies

Keep dependencies minimal.

Any runtime dependency addition requires review for:

- necessity;
- maintenance quality;
- vulnerability surface;
- transitive dependencies;
- licensing;
- whether the capability belongs in BeeAgent instead.

Never add a dependency "just in case".

## No hidden host configuration

BeeDrill should not create its own hidden host configuration source.

Do not add:

```text
production .env ownership
credential loader
RPC secret loader
host policy config
```

without an explicit architecture decision.

Host/runtime configuration belongs to BeeAgent.

## Logging

Do not introduce a dedicated logging framework unless real BeeDrill behavior
requires it.

If diagnostics are added:

- do not log secrets;
- do not log private keys;
- do not log unrestricted scenario payload;
- do not log complete environment dumps;
- keep messages bounded.

## Public API as a security boundary

Public/domain contracts define who controls which values.

Review:

- who creates each field;
- who validates each field;
- whether it is untrusted data;
- whether it is evidence;
- whether it could influence execution;
- whether it could influence verdict;
- whether a default weakens fail-closed behavior.

A field should not simultaneously represent:

```text
untrusted input
and
trusted execution authority
```

## Security checks

Use only checks appropriate to the change.

### SAST

Expected for security-sensitive implementation such as:

- execution integration;
- RPC integration;
- path handling;
- scenario validation influencing execution;
- authority boundaries;
- parsers;
- evidence validation with non-trivial logic.

Look for:

- arbitrary command execution;
- unsafe endpoint selection;
- authority escalation;
- hidden I/O;
- path traversal;
- secret exposure;
- ownership bypass;
- false-PASS behavior.

### SCA

Required when dependencies change.

Review:

```text
pyproject.toml
uv.lock
```

Check:

- direct dependencies;
- transitive dependencies;
- known vulnerabilities;
- necessity.

### DAST

Use only if the actual approved change introduces or modifies an externally
reachable runtime surface.

Pure BeeDrill domain logic does not require DAST.

### IAST

Not default.

Use only when a security-sensitive instrumentable runtime path exists.

### Fuzzing

Consider when BeeDrill adds:

- parser;
- deserializer;
- complex untrusted scenario validation;
- normalization engine;
- structured external evidence parser.

Simple deterministic domain objects do not require broad fuzzing.

## Change levels

### low-risk

Examples:

- documentation;
- tests;
- formatting;
- internal contract-neutral cleanup.

Usually:

- normal review;
- applicable tests.

### runtime-risk

Examples:

- scenario semantics;
- evidence validation;
- metrics;
- verdict behavior;
- module/public API;
- fixture/replay changes;
- package/build changes.

Usually:

- targeted tests;
- full tests;
- package/import smoke where applicable;
- deterministic/replay checks;
- compatibility review.

### security-sensitive

Examples:

- subprocess execution;
- Surfpool lifecycle;
- RPC execution;
- target selection;
- credentials;
- authority;
- path/file handling;
- external egress;
- dependency additions;
- security-sensitive parser/deserializer;
- detector/containment execution boundary.

Usually:

- applicable runtime-risk checks;
- SAST;
- SCA when dependencies changed;
- targeted negative/adversarial tests;
- explicit security review.

## Negative security scenarios

For execution-related work, test applicable cases such as:

```text
approved isolated target
→ allowed

forbidden target
→ refused

malformed scenario
→ refused

scenario-selected arbitrary executable
→ impossible or refused

unexpected RPC endpoint
→ refused

timeout
→ bounded failure

failed process
→ cleanup

missing critical evidence
→ cannot PASS
```

Do not add artificial tests that do not correspond to the actual implementation
surface.

## Minimal developer security checklist

Before a significant PR ask:

- can scenario input escalate authority?
- can scenario input select arbitrary execution?
- can scenario input redirect RPC?
- did BeeDrill gain host-owned behavior?
- did production/mainnet mutation become possible?
- can missing evidence become PASS?
- is verdict deterministic?
- are secrets kept out of source/fixtures/artifacts?
- did dependencies change?
- does the change actually belong in BeeDrill?

## Minimal reviewer checklist

Reviewer should verify:

- repository ownership remains clear;
- execution authority remains host-owned;
- target isolation remains explicit;
- scenario input remains untrusted;
- evidence is not authority;
- fail-closed behavior is preserved;
- deterministic verdicts are preserved;
- dependencies are justified;
- required negative tests exist;
- no unrelated execution surface was introduced.

## Supply-chain and release security

Release/package metadata should remain reproducible.

Sources of truth:

```text
pyproject.toml
uv.lock
```

Release automation should use reviewed repository configuration.

Do not:

- commit local virtual environments;
- commit generated package metadata;
- manually upload unreviewed build artifacts;
- add arbitrary release scripts with hidden network behavior;
- bundle unrelated repository source into the package.

## What not to do

Avoid:

- arbitrary "execute anything" APIs;
- scenario-controlled authority;
- arbitrary RPC selection;
- arbitrary filesystem paths;
- production/mainnet fallback;
- hidden credential loading;
- dynamic plugin installation;
- remote code loading;
- AI-controlled critical verdicts;
- dependencies added for convenience only;
- security theater requiring every tool for every change.

## Summary

BeeDrill security is primarily boundary and evidence security.

Keep it safe through:

```text
isolated execution
host-owned authority
bounded targets
bounded execution
untrusted scenarios
evidence != authority
fail-closed evaluation
deterministic verdicts
minimal dependency surface
```
