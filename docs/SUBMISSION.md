# BeeDrill submission package

## Product in one sentence

BeeDrill is continuous security-control validation for Solana: it replays a
bounded attack in isolation, observes detection and containment, measures
residual loss, and derives a deterministic security verdict.

## Evidence map

The implementation, tests, and host-produced artifacts are authoritative. This
document indexes them; it is neither a verdict engine nor an execution API.

| Material claim                                                   | Evidence                                                                                                                                              |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Broken `fail` → fixed `pass` replay and fixed `security_verdict` | `src/beedrill/module.py`; replay tests in `tests/test_bootstrap.py`; fresh runs below                                                                 |
| Vault containment limits a second withdrawal                     | `docs/SPEC.md` section 17.3; `reference_target_containment_replay.json`                                                                               |
| Oracle containment blocks a second borrow                        | `docs/SPEC.md` section 17.4; `reference_oracle_manipulation_replay.json`                                                                              |
| One external Solana component is validated                       | `docs/SPEC.md` section 17.5; [`evidence/spl_token_freeze_containment_replay.example.json`](evidence/spl_token_freeze_containment_replay.example.json) |
| Verdict is deterministic and fail closed                         | `src/beedrill/evaluator.py`; `tests/test_evaluator.py`; negative replay tests                                                                         |
| BeeDrill is read-only; host and SDK ownership remain separate    | `docs/ARCHITECTURE.md`; `docs/SPEC.md` sections 6–10                                                                                                  |
| No production/mainnet mutation                                   | `docs/SECURITY.md`; `docs/SPEC.md` sections 4–5                                                                                                       |

Fresh final runs from the supported sibling workspace state:

| Replay                       | Host run ID        | Result                                               |
| ---------------------------- | ------------------ | ---------------------------------------------------- |
| reference containment        | `run-e871afd3bb79` | `broken=fail`, `fixed=pass`, `security_verdict=pass` |
| oracle manipulation          | `run-75f3f1230f36` | `broken=fail`, `fixed=pass`, `security_verdict=pass` |
| SPL Token freeze containment | `run-2b7207274688` | `broken=fail`, `fixed=pass`, `security_verdict=pass` |

The committed SPL JSON is a bounded projection of the last scenario artifact.
It excludes session IDs, raw logs, transaction signatures, keys, credentials,
environment values, and unrelated diagnostics. Re-run the documented command
to produce the authoritative artifact for a new run.

## External-validation limit

The external claim is deliberately narrow: one canonical SPL Token account-freeze
containment pattern, with two identical transfers, in host-controlled isolated
Surfpool. It does not claim arbitrary Solana protocol compatibility, generic
SPL Token adapter support, mainnet mutation safety, autonomous response, or
coverage of other controls.

## Functional positioning

- Audits ask whether code can be broken.
- Monitoring and incident detection report signals from a running system.
- BeeDrill validates whether configured detection and containment limit
  measurable damage under a reproducible attack.

These are category-level distinctions; this repository makes no named-competitor
claims.

## Submission copy

BeeDrill is security regression testing for Solana defenses. It runs a bounded
attack in an isolated environment, checks whether detection and containment
actually occur, measures residual loss, and returns a deterministic verdict.

Our external proof replays one canonical SPL Token freeze-containment pattern.
Broken containment permits the second transfer and fails. Freezing the target
account rejects the identical second transfer, lowers residual loss, and passes.
BeeDrill remains read-only: BeeAgent owns execution, Surfpool, RPC, credentials,
timeouts, and cleanup.

## 60–90 second core demo

Target duration: 75 seconds.

| Time   | Demo action                                                                                       |
| ------ | ------------------------------------------------------------------------------------------------- |
| 0–10s  | State the product question: do defenses limit damage under attack?                                |
| 10–20s | Show the three bounded replay names and the ownership boundary.                                   |
| 20–30s | Run `./start.sh beedrill run --scenario spl_token_freeze_containment_replay`; do not edit output. |
| 30–45s | Show the JSON summary with `security_verdict: pass`, then its generated artifact.                 |
| 45–60s | Show broken `fail` / 200000 residual units and fixed `pass` / 100000 residual units.              |
| 60–70s | Show the deterministic evaluator and bounded evidence contract.                                   |
| 70–75s | State the one-pattern SPL limitation.                                                             |

## Demo-video script

“BeeDrill is a security-control regression test for Solana. This canonical SPL
Token replay runs broken and fixed containment from fresh isolated state. Broken
containment allows the second transfer, leaving 200,000 residual base units and
a fail. Fixed containment freezes the target account, rejects the same second
transfer, leaves 100,000 residual base units, and produces a deterministic pass.
BeeDrill is read-only; BeeAgent owns execution, keys, RPC, timeouts, and cleanup.
This is one real SPL Token containment pattern, not every Solana protocol.”

## Pitch-video script

“Security teams can have audits, alerts, and emergency controls without knowing
whether those controls will limit damage in an attack. BeeDrill turns that
assumption into a repeatable regression: isolate, attack, detect, contain,
measure, and deterministically decide. Our MVP proves the loop on Solana with a
canonical SPL Token freeze-containment replay. The same attack fails when
containment is broken and passes with lower measured residual loss once the
account is frozen. BeeDrill does not mutate mainnet or make autonomous response
decisions.”
