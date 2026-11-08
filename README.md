# EvoTrader v0.1

Research-first, reproducible, **non-live** trading research platform. It studies whether external
episodic memory and controlled strategy evolution improve out-of-sample, net-of-cost performance
versus matched baselines. It does not trade, connect to brokers, or make profitability claims.

- Specification: [`EvoTrader_v0.1_Implementation_Spec.md`](EvoTrader_v0.1_Implementation_Spec.md)
- Plan & progress: [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md)
- Architecture decisions: [`docs/adr/`](docs/adr/)

## Status

Week 1 Day 1: scaffold, toolchain, CI, Compose, configuration. No data layer, DSL or backtest yet.

## Quickstart (development)

Requirements: Python 3.12, [`uv`](https://docs.astral.sh/uv/), Docker (for PostgreSQL/Redis).

```bash
uv sync --locked
cp .env.example .env
docker compose up -d postgres redis
scripts/check.sh            # ruff, ruff format --check, pyright, pytest
```

Unit tests need no network, database or API keys. Tests marked `integration` need the Compose
services and are skipped with a reason when they are unreachable.

## Safety constraints (v0.1)

- `RUN_MODE=research` is the only accepted mode; anything else fails at startup.
- No broker adapters, live credentials, leverage or shorting.
- LLM output is never executed as code; strategies are a validated declarative DSL.
