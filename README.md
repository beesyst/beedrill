# BeeDrill

BeeDrill is a Solana-first security-control validation module for BeeAgent.
It tests whether technical defenses detect and contain reproducible attacks in
controlled, isolated conditions—not merely whether code contains a vulnerability.

BeeDrill owns scenario, evidence, metric, and deterministic-verdict domain
behavior. BeeAgent owns runtime, orchestration, execution authority, Surfpool,
Solana RPC, credentials, and storage. BeeSDK provides shared contracts when an
approved package source is available.

## Bootstrap status

This repository currently provides the BD-1 package and module foundation only.
It has no execution, RPC, detector, containment, metrics, verdict, replay, UI,
or production/mainnet access.

## Development

```bash
uv sync
uv run pytest -q
uv build
uv run python -c "import beedrill; print(beedrill.__file__)"
```

See [the roadmap](docs/ROADMAP.md), [specification](docs/SPEC.md),
[architecture](docs/ARCHITECTURE.md), [development guide](docs/DEV_GUIDE.md),
and [security guidance](docs/SECURITY.md).
