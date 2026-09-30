# BeeDrill — Security Regression Testing for Solana

**BeeDrill runs reproducible Solana attacks and verifies that your defenses actually detect and contain them.**

> Audits test your code. BeeDrill tests your defenses.

```text
Attack → Detect → Contain → Measure → PASS / FAIL
```

BeeDrill is designed to answer one question:

> If this attack happens now, do the deployed security controls actually protect the protocol?

The result is based on machine evidence, not a security score or an AI opinion.

## Why BeeDrill?

Having a security control does not prove that it works.

| You have               | BeeDrill verifies                                      |
| ---------------------- | ------------------------------------------------------ |
| Audit                  | whether defenses still work after the audit            |
| Alert                  | whether a real attack actually triggers it             |
| Pause / freeze control | whether it actually stops the next malicious action    |
| Incident procedure     | whether the technical control works before an incident |
| Security assumption    | machine-verifiable evidence                            |

BeeDrill turns security controls into regression tests:

```text
working defense
→ PASS

broken defense
→ FAIL
```

## Quick start

BeeDrill is a module for [BeeAgent](https://github.com/beesyst/beeagent).

It does not run its own runtime. BeeAgent owns Solana execution, Surfpool, RPC,
timeouts, cleanup and artifacts.

### 1. Requirements

- Linux
- Git
- Python 3.14+
- Rust
- Solana CLI
- `cargo-build-sbf`
- Surfpool

### 2. Install

Create the current Bee workspace with one copy/paste command:

```bash
git clone https://github.com/beesyst/beeagent.git && \
git clone https://github.com/beesyst/beedrill.git && \
git clone https://github.com/beesyst/beesdk.git && \
git clone https://github.com/beesyst/beeagent-rop.git
```

The repositories must remain next to each other:

```text
workspace/
├── beeagent/
├── beedrill/
├── beesdk/
└── beeagent-rop/
```

You do not install BeeDrill separately.

### 3. Enable BeeDrill

Open:

```text
beeagent/config/settings.yml
```

Find:

```yaml
- id: "beedrill"
  package: "beedrill.module"
  entry: "BeeDrillModule"
  enabled: false
  install_extra: "beedrill"
```

Change:

```yaml
enabled: true
```

BeeAgent will install and load the BeeDrill module automatically.

### 4. Run

```bash
cd beeagent
./start.sh beedrill check
```

That's the normal BeeDrill interface.

You do not need to manually start Surfpool, install Python packages or run
BeeDrill as another service.

## What does `beedrill check` run?

BeeDrill currently runs three security regressions:

| Drill                                  | Attack                                    | Defensive control        |
| -------------------------------------- | ----------------------------------------- | ------------------------ |
| `reference_target_containment_replay`  | repeated vault withdrawal                 | vault containment        |
| `reference_oracle_manipulation_replay` | oracle manipulation followed by borrowing | oracle containment       |
| `spl_token_freeze_containment_replay`  | repeated SPL Token transfer               | SPL Token account freeze |

The SPL Token drill uses the canonical SPL Token program inside the isolated
Solana environment.

Each drill compares equivalent attacks against two defensive conditions:

```text
BROKEN DEFENSE
same attack
→ containment fails
→ higher residual loss
→ FAIL
```

```text
FIXED DEFENSE
same attack
→ containment works
→ lower residual loss
→ PASS
```

The attack stays equivalent.

The defense changes.

That is the security regression.

## What happens when I run it?

```text
./start.sh beedrill check
        │
        ▼
     BeeAgent
        │
        ├── creates isolated Solana state
        ├── runs the attack
        ├── applies the defensive control
        └── collects evidence
                 │
                 ▼
              BeeDrill
                 │
                 ├── validates evidence
                 ├── checks detection
                 ├── checks containment
                 ├── measures loss
                 └── returns PASS / FAIL
```

BeeAgent owns execution.

BeeDrill owns scenario semantics, evidence validation, metrics and verdicts.

## Result

A completed run returns one of three states:

| Result       | Meaning                                           |
| ------------ | ------------------------------------------------- |
| `PASS`       | all required security controls worked             |
| `FAIL`       | the test completed, but a security control failed |
| `INCOMPLETE` | the test could not safely complete                |

Example:

```text
BeeDrill Security Regression

PASS: reference_target_containment_replay
PASS: reference_oracle_manipulation_replay
PASS: spl_token_freeze_containment_replay

Scenarios: passed=3 failed=0 incomplete=0
Suite status: PASS
```

A security regression is different from an infrastructure error.

```text
valid evidence + broken defense
→ FAIL

missing / invalid evidence
→ INCOMPLETE
```

Missing evidence never becomes PASS.

## What is measured?

| Metric        | Meaning                                              |
| ------------- | ---------------------------------------------------- |
| Detection     | did the expected detector observe the attack?        |
| Containment   | did the defensive control actually stop or limit it? |
| MTTD          | slots from attack start to detection                 |
| MTTC          | slots from detection to containment                  |
| Gross loss    | damage caused by the attack                          |
| Residual loss | damage remaining after containment                   |
| Capital saved | loss prevented by the control                        |
| Verdict       | deterministic PASS / FAIL                            |

The same validated evidence always produces the same result.

## CI

The same command is the CI gate:

```bash
./start.sh beedrill check
```

Exit codes:

| Exit | Meaning                      |
| ---: | ---------------------------- |
|  `0` | PASS                         |
|  `1` | completed security FAIL      |
|  `2` | invalid command              |
|  `3` | INCOMPLETE / runtime failure |

Example:

```yaml
- name: BeeDrill security regression
  run: ./start.sh beedrill check
```

CI only needs the process exit code.

## Evidence

Every run produces machine-readable evidence.

Individual drill results:

```text
beeagent/storage/runs/<run-id>/module-beedrill/
```

Aggregate result:

```text
beeagent/storage/runs/<suite-run-id>/module-beeagent/
└── beedrill_security_regression.json
```

This makes failures reproducible and inspectable instead of leaving only a
console message.

## Individual drills

Most users only need:

```bash
./start.sh beedrill check
```

For debugging, a single drill can be run directly:

```bash
./start.sh beedrill run --scenario reference_target_containment_replay
```

```bash
./start.sh beedrill run --scenario reference_oracle_manipulation_replay
```

```bash
./start.sh beedrill run --scenario spl_token_freeze_containment_replay
```

These are additional CLI commands, not the primary product flow.

## Safety

BeeDrill runs against approved isolated environments.

```text
mainnet mutation              prohibited
production credentials       not required
arbitrary RPC                prohibited
arbitrary subprocess         prohibited
arbitrary transaction input  prohibited
AI verdict authority         prohibited
```

BeeDrill remains `READ_ONLY`.

Critical PASS / FAIL results come only from validated machine evidence.

## Architecture

```text
BeeDrill
scenarios
evidence validation
metrics
verdicts
    │
    │ BeeSDK contracts
    ▼
BeeAgent
runtime
Surfpool
Solana RPC
execution
artifacts
```

| Component | Responsibility                                |
| --------- | --------------------------------------------- |
| BeeDrill  | what is tested and whether the defense passed |
| BeeAgent  | how bounded execution happens                 |
| BeeSDK    | shared contracts                              |

## Current status

The MVP loop works end to end:

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

Available now:

- isolated Solana attack execution;
- deterministic detection and containment checks;
- economic loss measurement;
- reproducible PASS / FAIL;
- three security regression drills;
- real SPL Token freeze containment;
- machine-readable evidence;
- aggregate regression gate;
- CI exit semantics;
- fail-closed runtime behavior.

BeeDrill is currently Solana-first and deliberately focused on
**security-control validation**, not generic vulnerability scanning.

## Documentation

- [`docs/DEV_GUIDE.md`](docs/DEV_GUIDE.md) — toolchain and development setup
- [`docs/SPEC.md`](docs/SPEC.md) — scenario and evidence contracts
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — BeeDrill / BeeAgent boundary
- [`docs/SECURITY.md`](docs/SECURITY.md) — execution and safety rules
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — product roadmap

## In one sentence

> **Run the attack before an attacker does, prove your defenses work, and keep that proof as a regression test.**

```bash
./start.sh beedrill check
```
