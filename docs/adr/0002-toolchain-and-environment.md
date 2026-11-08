# ADR-0002: Toolchain, dependency pinning and environment gaps

- Status: Accepted (2026-11-09)

## Context
Spec §3 requires Python 3.12, `uv`, `ruff`, `pyright`, `pytest`, Docker Compose with PostgreSQL 16+
(pgvector in phase 2) and Redis. The development host had Python 3.12.3 without pip and without Docker.

## Decision
- `uv` manages the virtualenv and `uv.lock`; CI uses `uv sync --locked`. `requires-python = ">=3.12,<3.13"`.
- `pyproject.toml` declares lower bounds; exact versions live only in `uv.lock` (committed).
- All Week 1 runtime libraries are declared on Day 1 so the lock is reviewed once; agent/LLM libraries
  (LangGraph, provider SDKs) are **not** added until Weeks 2–3.
- `ruff` for lint and format; `pyright` in strict mode for `src/`, `tests/` and `scripts/`.
- Tests marked `integration` need PostgreSQL/Redis (`DATABASE_URL`) and are skipped with an explicit
  reason when the service is unreachable; CI provides the services so they always run there.
- Compose uses `pgvector/pgvector:pg16` from the start (PostgreSQL 16 with the extension available but
  not enabled) to avoid an image swap in Week 4; Redis 7. Ports bind to `127.0.0.1` only.

## Consequences
- On the current host, Compose and DB integration tests cannot be executed until Docker is installed.
  This is reported as an environment gap, never as a pass.
