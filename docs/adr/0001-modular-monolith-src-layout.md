# ADR-0001: Modular monolith with src layout

- Status: Accepted (2026-11-09)

## Context
Spec §2 mandates a modular monolith and suggests a module tree. Agents, deterministic engines and
persistence must stay separable so the trust boundary (LLM proposes; deterministic services decide)
is enforced by imports, not by convention.

## Decision
- Single installable package `evotrader` under `src/` (prevents tests importing the working tree by accident).
- Top-level subpackages exactly as spec §2: `api, core, data, dsl, backtest, research, memory, agents, workers`.
- Dependency direction (enforced by review now, by an import-linter contract later):
  `core` ← `data` ← `dsl` ← `backtest` ← `research` ← `memory` ← `agents` ← `api`/`workers`.
  `backtest`, `dsl`, `data` must never import `agents`, `memory` or `api`.
- No microservices; Redis is only a job queue, not a service boundary.

## Consequences
- Deterministic core can be tested without DB, network or LLM.
- An import-boundary check should be added once there is enough code to make it meaningful (Day 6).
