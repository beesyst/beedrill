# BeeDrill reproduction evidence

## Release-backed bootstrap

On 2026-10-07, a clean BeeAgent copy in `/tmp` with no sibling `beesdk` or `beedrill` directory ran the normal bootstrap command. The locked bootstrap resolved `beesdk==0.2.0` from revision `e6629f6ceb4ad58a711c5a7f640db712ce00106a`, then resolved the enabled `beedrill==0.14.0` extra from revision `ba4401c4186ae5723ab6ac46741b5b3518f000c7`.

The module registry loaded `beedrill.module.BeeDrillModule`; the disabled ROP module was not loaded. The clean copy completed `./start.sh beedrill run --scenario spl_token_freeze_containment_replay` with exit `0`, `execution_status: ok`, and `security_verdict: pass`. Its bounded per-scenario evidence is at:

```text
storage/runs/run-47c0953e6087/module-beedrill/
```

`./start.sh beedrill unexpected` returned exit `2` in the same copy.

## Clean-room three-scenario evidence

On 2026-10-07, the same clean copy completed `./start.sh beedrill check` with exit `0`. Its host-owned aggregate artifact is:

```text
storage/runs/beedrill-suite-7fc59446f2ff/module-beeagent/beedrill_security_regression.json
```

It records `suite_status: pass`, `passed: 3`, `failed: 0`, and `incomplete: 0` with valid bounded per-scenario artifact references:

- `reference_target_containment_replay`: `run-a1241fb3cc71` PASS;
- `reference_oracle_manipulation_replay`: `run-249eff59808e` PASS;
- `spl_token_freeze_containment_replay`: `run-95d092fb148b` PASS.

## Independent developer validation

No independent external-developer dogfood session was available. Consequently, time-to-first-result, blockers, and confusing steps are not claimed as external evidence.

## One-day recovery gate — 2026-10-08

A new local main-based BeeAgent clone at `/tmp/bee-rescue-20261008-gate/standalone/beeagent` had no virtual environment, copied environment file or sibling repositories. The clone received the uncommitted generic recovery runtime snapshot; it is not evidence that published main already includes these fixes. `./start.sh beedrill check` created the Python environment from the unchanged lockfile and completed three real isolated Solana scenarios with exit `0`. This run reused the existing user native-tool cache.

Its aggregate artifact is `storage/runs/beedrill-suite-1d724132b0b7/module-beeagent/beedrill_security_regression.json`; the scenario runs are `run-8926738178fa`, `run-b9cea6af1e29` and `run-434e12507d54`. The locked BeeDrill release was revision `ba4401c4186ae5723ab6ac46741b5b3518f000c7`.

A second command, `PYTHONPATH=/tmp/bee-rescue-20261008-gate/work/beedrill/src ./start.sh beedrill check`, selected the recovered BeeDrill source and also completed three scenarios with exit `0`. Its aggregate artifact is `storage/runs/beedrill-suite-7f50b69c5141/module-beeagent/beedrill_security_regression.json`; scenario runs are `run-33a5e5e65594`, `run-07476746a865` and `run-b899a2030057`. In the SPL scenario, broken containment allowed two transfers and lost 200,000 base units; effective freeze rejected the repeat and limited loss to 100,000 base units. Detection here is the bounded local balance monitor, not an integrated production detector.

Separately, `ensure_native_tools(needs_sbf=True, root=...)` provisioned and verified native tools in an initially absent directory in 298.59 seconds. A second call took 1.82 seconds and preserved all 3,365 file modification times. This proves cold native readiness and idempotent reuse separately from the fresh-clone three-scenario run.

The full recovery sources passed BeeDrill 586 tests, BeeAgent 2,225 tests and BeeAgent-ROP 483 tests. Backups, command logs, immutable artifact copies, SHA-256 provenance, recovery patches and the gate assessment are preserved under `/home/bee/Pro/beeagent/storage/mvp-rescue-20261008-gate`. External protocol onboarding is NO-GO for this gate; no external transaction proof or independent developer clean-clone validation is claimed.
