# Iteration 17 reproduction evidence

## Release-backed bootstrap

On 2026-10-07, a clean BeeAgent copy in `/tmp` with no sibling `beesdk` or
`beedrill` directory ran the normal bootstrap command. The locked bootstrap
resolved `beesdk==0.2.0` from revision
`e6629f6ceb4ad58a711c5a7f640db712ce00106a`, then resolved the enabled
`beedrill==0.14.0` extra from revision
`ba4401c4186ae5723ab6ac46741b5b3518f000c7`.

The module registry loaded `beedrill.module.BeeDrillModule`; the disabled ROP
module was not loaded. The clean copy completed
`./start.sh beedrill run --scenario spl_token_freeze_containment_replay` with
exit `0`, `execution_status: ok`, and `security_verdict: pass`. Its bounded
per-scenario evidence is at:

```text
storage/runs/run-47c0953e6087/module-beedrill/
```

`./start.sh beedrill unexpected` returned exit `2` in the same copy.

## Clean-room three-scenario evidence

On 2026-10-07, the same clean copy completed `./start.sh beedrill check` with
exit `0`. Its host-owned aggregate artifact is:

```text
storage/runs/beedrill-suite-7fc59446f2ff/module-beeagent/beedrill_security_regression.json
```

It records `suite_status: pass`, `passed: 3`, `failed: 0`, and `incomplete: 0`
with valid bounded per-scenario artifact references:

- `reference_target_containment_replay`: `run-a1241fb3cc71` PASS;
- `reference_oracle_manipulation_replay`: `run-249eff59808e` PASS;
- `spl_token_freeze_containment_replay`: `run-95d092fb148b` PASS.

## External developer dogfood

No independent external-developer dogfood session was available. Consequently,
time-to-first-result, blockers, and confusing steps are not claimed as external
evidence.
