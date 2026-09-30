# BeeDrill — Security Regression Testing for Solana

**BeeDrill tests whether your security controls actually stop an attack.**

> Audits test your code. BeeDrill tests your defenses.

BeeDrill runs reproducible attacks against an isolated Solana environment,
checks whether detection and containment worked, measures the result, and returns
a deterministic **PASS / FAIL**.

```text
Attack
→ Detect
→ Contain
→ Measure
→ PASS / FAIL
```

No security score.  
No AI deciding the verdict.  
No mainnet execution.

## What problem does BeeDrill solve?

A protocol can have:

- audits;
- monitoring;
- alerts;
- circuit breakers;
- pause/freeze controls;
- emergency authorities.

That still does not prove those controls will work during a real attack.

BeeDrill turns the question into a regression test:

```text
Did the attack execute?
Did the detector see it?
Did containment activate?
Did containment actually stop the next action?
How much value was lost?
```

Then BeeDrill returns a machine-verifiable result:

```text
PASS
```

or:

```text
FAIL
```

The same way application tests catch code regressions, BeeDrill catches
**security-control regressions**.

## One command

The normal way to use BeeDrill is:

```bash
./start.sh beedrill check
```

That is the product interface.

BeeAgent handles the runtime, dependencies, isolated Solana environment,
execution, cleanup and artifacts.

You do **not** need to manually run `uv`, start Surfpool separately, or launch
BeeDrill as another service.

## Quick start

### 1. Requirements

You need:

- Linux
- Git
- Python 3.14+
- Solana CLI tooling
- `cargo-build-sbf`
- Surfpool
- Rust toolchain required by Solana

BeeAgent bootstraps `uv` automatically when needed.

For detailed toolchain setup, see
[`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md).

### 2. Install the workspace

BeeDrill is a **BeeAgent module**, not a standalone runtime.

The current MVP uses sibling repositories:

```text
workspace/
├── beeagent/
├── beedrill/
├── beesdk/
└── beeagent-rop/
```

From an empty directory, this single copy/paste command creates the workspace:

```bash
git clone https://github.com/beesyst/beeagent.git && \
git clone https://github.com/beesyst/beedrill.git && \
git clone https://github.com/beesyst/beesdk.git && \
git clone https://github.com/beesyst/beeagent-rop.git
```

Why sibling repositories?

BeeAgent currently uses local editable module sources during the MVP.
BeeDrill does not run its own process or maintain a second runtime.

### 3. Enable BeeDrill

Open:

```text
beeagent/config/settings.yml
```

Find the BeeDrill module:

```yaml
- id: "beedrill"
  package: "beedrill.module"
  entry: "BeeDrillModule"
  enabled: false
  install_extra: "beedrill"
```

Change only:

```yaml
enabled: true
```

Result:

```yaml
- id: "beedrill"
  package: "beedrill.module"
  entry: "BeeDrillModule"
  enabled: true
  install_extra: "beedrill"
```

That is the BeeDrill installation switch inside BeeAgent.

You do not install or start BeeDrill separately.

### 4. Run the security regression suite

Go to BeeAgent:

```bash
cd beeagent
```

Run:

```bash
./start.sh beedrill check
```

BeeAgent prepares the environment and runs the complete approved BeeDrill suite.

The final result is one of:

```text
Suite status: PASS
```

```text
Suite status: FAIL
```

or:

```text
Suite status: INCOMPLETE
```

## What does `beedrill check` run?

Today BeeDrill contains three approved security regressions.

| Drill | Attack | Defensive control |
| -- | -- | |
| `reference_target_containment_replay` | repeated vault withdrawal | vault containment |
| `reference_oracle_manipulation_replay` | oracle manipulation followed by borrowing | oracle containment |
| `spl_token_freeze_containment_replay` | repeated SPL Token transfer | SPL Token account freeze |

The SPL Token drill uses the real canonical SPL Token program inside the
isolated environment.

Each drill compares two conditions:

```text
BROKEN DEFENSE
same attack
→ containment fails
→ higher residual loss
→ FAIL
```

against:

```text
FIXED DEFENSE
same attack
→ containment works
→ lower residual loss
→ PASS
```

The attack stays equivalent.

The defense changes.

That is the regression test.

## What happens when I run it?

```text
./start.sh beedrill check
        │
        ▼
     BeeAgent
        │
        ├── creates isolated Solana state
        ├── starts bounded runtime
        ├── executes approved attack operations
        ├── executes approved defensive controls
        └── returns machine evidence
                 │
                 ▼
              BeeDrill
                 │
                 ├── validates evidence
                 ├── checks detection
                 ├── checks containment
                 ├── calculates loss
                 ├── calculates MTTD / MTTC
                 └── produces deterministic verdict
                         │
                         ▼
                    PASS / FAIL
```

BeeAgent owns **execution**.

BeeDrill owns **security meaning and verdicts**.

## What is measured?

BeeDrill evaluates observable evidence.

| Metric        | Meaning                                              |
| ------------- | ---------------------------------------------------- |
| Detection     | Did the expected detector observe the attack?        |
| Containment   | Did the defensive control actually stop or limit it? |
| MTTD          | Slots from attack start to first detection           |
| MTTC          | Slots from detection to containment                  |
| Gross loss    | Damage caused by the attack                          |
| Residual loss | Damage remaining after controls acted                |
| Capital saved | Difference between uncontrolled and contained loss   |
| Verdict       | Deterministic PASS / FAIL                            |

Example:

```text
Attack executed      PASS
Detection            PASS
Containment          FAIL
MTTD                  4 slots
MTTC                  unavailable
Residual loss         480000 units
Final verdict         FAIL
```

BeeDrill deliberately does **not** produce subjective results such as:

```text
Security score: 82/100
```

## PASS, FAIL and INCOMPLETE

These states have different meanings.

#### PASS

```text
attack executed
+
required evidence is valid
+
security control worked
=
PASS
```

#### FAIL

```text
attack executed
+
required evidence is valid
+
security control did not protect the target
=
FAIL
```

A FAIL is a **completed security test**.

It is not an infrastructure error.

#### INCOMPLETE

```text
runtime unavailable
or
timeout
or
invalid/missing evidence
or
execution could not safely complete
=
INCOMPLETE
```

BeeDrill fails closed: missing evidence never silently becomes PASS.

## CI usage

The same command can be used as a CI security gate:

```bash
./start.sh beedrill check
```

Exit codes:

| Exit | Meaning                               |
| :--- | ------------------------------------- |
| `0`  | all security regressions passed       |
| `1`  | completed security regression failed  |
| `2`  | invalid command                       |
| `3`  | test was incomplete or runtime failed |

A CI system only needs to use the process exit code.

Example:

```yaml
- name: BeeDrill security regression
  run: ./start.sh beedrill check
```

No stdout parsing is required.

## Evidence

BeeDrill does not return only a green/red console line.

Every run produces machine-readable evidence.

Individual drill artifacts live under:

```text
beeagent/storage/runs/<run-id>/module-beedrill/
```

The aggregate suite produces:

```text
beeagent/storage/runs/<suite-run-id>/module-beeagent/
└── beedrill_security_regression.json
```

The suite artifact contains bounded references to the canonical individual
results rather than duplicating raw runtime evidence.

This makes a regression:

```text
reproducible
+
inspectable
+
CI-visible
```

## Optional CLI

Most users only need:

```bash
./start.sh beedrill check
```

Individual drills are available for debugging or development.

#### Reference vault

```bash
./start.sh beedrill run --scenario reference_target_containment_replay
```

#### Oracle manipulation

```bash
./start.sh beedrill run --scenario reference_oracle_manipulation_replay
```

#### SPL Token freeze containment

```bash
./start.sh beedrill run --scenario spl_token_freeze_containment_replay
```

These are advanced commands.

The normal product flow remains:

```bash
./start.sh beedrill check
```

## Why BeeDrill?

| Traditional security | BeeDrill |
| - | |
| Audit says the code looked safe | Replay proves the defense works now |
| Alert exists | Attack verifies the alert actually fires |
| Pause/freeze mechanism exists | Replay verifies it actually contains the attack |
| Incident procedure exists | Control behavior is exercised before an incident |
| Security assumption | Machine evidence |
| Manual validation | Repeatable regression |
| Subjective score | Deterministic PASS / FAIL |

BeeDrill complements audits.

It does not replace them.

The difference is simple:

```text
audit
→ can this code be exploited?

BeeDrill
→ if an attack happens, do our defenses actually stop it?
```

## Safety model

BeeDrill is designed for isolated security validation.

Current invariants:

```text
mainnet mutation              prohibited
production credentials       not required
arbitrary RPC                prohibited
arbitrary subprocess         prohibited
arbitrary transaction input  prohibited
AI verdict authority         prohibited
```

BeeDrill itself remains:

```text
READ_ONLY
```

Execution authority stays inside BeeAgent.

BeeAgent owns:

- Surfpool lifecycle;
- Solana RPC;
- subprocesses;
- transactions;
- ephemeral test keys;
- timeouts;
- cleanup;
- artifact storage.

BeeDrill cannot turn scenario input into unrestricted host execution.

## AI

Critical security truth is deterministic.

AI does not decide:

```text
Detection
Containment
MTTD
MTTC
Loss
PASS / FAIL
```

AI may later help explain evidence or suggest remediation.

The deterministic verdict remains authoritative.

## Architecture in one picture

There are only three pieces to understand:

```text
BeeDrill
security scenarios
evidence validation
metrics
PASS / FAIL
        │
        │ BeeSDK contracts
        ▼
BeeAgent
runtime
Surfpool
RPC
execution
artifacts
```

**BeeDrill says what must be proven.**

**BeeAgent performs the bounded execution required to prove it.**

**BeeSDK provides the shared contract between them.**

## Current status

The complete MVP security-regression loop works:

```text
Define
→ Isolate
→ Attack
→ Detect
→ Contain
→ Measure
→ Verdict
→ Replay
```

Available today:

- isolated Solana execution;
- reproducible attacks;
- independent detection evidence;
- real containment;
- deterministic metrics;
- deterministic PASS / FAIL;
- economic loss measurement;
- replayable artifacts;
- aggregate regression suite;
- CI exit semantics;
- real SPL Token containment validation;
- fail-closed runtime behavior.

Current focus is intentionally narrow:

```text
Solana
+
real attacks
+
real controls
+
objective evidence
+
deterministic regression testing
```

BeeDrill is not trying to become a generic scanner, generic pentest agent,
SIEM, SOC platform or multi-chain framework.

## Repository layout

BeeDrill is part of the Bee ecosystem:

| Repository                                      | Responsibility                                             |
| ----------------------------------------------- | ---------------------------------------------------------- |
| [BeeDrill](https://github.com/beesyst/beedrill) | security scenarios, evidence validation, metrics, verdicts |
| [BeeAgent](https://github.com/beesyst/beeagent) | runtime, execution, Surfpool, RPC, policy, artifacts       |
| BeeSDK                                          | shared contracts                                           |

For normal use, start from BeeAgent and run BeeDrill through:

```bash
./start.sh beedrill check
```

## Documentation

The README is intentionally focused on using and understanding the product.

For implementation details:

- [`docs/SPEC.md`](docs/SPEC.md) — scenario and product contracts
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — component boundaries
- [`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md) — development and toolchain setup
- [`docs/SECURITY.md`](docs/SECURITY.md) — security boundaries
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — delivery roadmap
- [`docs/SUBMISSION.md`](docs/SUBMISSION.md) — demo and submission material

## The idea in one sentence

> **Run the attack before an attacker does, prove your defenses work, and keep that proof as a regression test.**

```bash
./start.sh beedrill check
```
