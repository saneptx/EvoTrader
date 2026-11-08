# EvoTrader v0.1 — Implementation Plan

Authoritative spec: [`EvoTrader_v0.1_Implementation_Spec.md`](../EvoTrader_v0.1_Implementation_Spec.md).
This plan only sequences that spec; where they disagree, the spec wins and this file is corrected.

Status legend: `[x]` done and verified by executed checks · `[~]` done but not fully verifiable in the
current environment (reason noted) · `[ ]` not started.

## 0. Repository / environment baseline (inspected 2026-11-09)

- Repository contained only the spec; no code, tests, git history or CI.
- Host: Linux, Python 3.12.3 (system, no `pip`/`ensurepip`). `uv` 0.13.7 installed user-local to
  `~/.local/bin` for this project. **Docker is not installed**, so Compose and PostgreSQL-backed
  checks cannot be executed on this host until Docker is available (see ADR-0002).
- No network market data or LLM keys are used anywhere in Week 1.

## 1. Ground rules carried from the spec

1. One vertical slice per step; run `ruff`, `pyright`, `pytest` after each; report actual output.
2. Research mode only. No broker adapters, no live credentials, no leverage, no shorting.
3. No `eval`/`exec`/shell on model output — declarative DSL only.
4. Determinism: same dataset + config + seed + code ⇒ byte-identical canonical ledger/metrics.
5. Validation thresholds and sealed holdout are never readable by generation agents.
6. Unfinished items are never marked done.

## 2. Milestones

### Week 1 — deterministic research foundation (no LLM, no broker)

**Day 1 — scaffold & toolchain**
- [x] `pyproject.toml` (src layout, Python 3.12, pinned via `uv.lock`)
- [x] Package skeleton `src/evotrader/` matching spec §2 module boundaries
- [x] `core/config.py` (env settings, `RUN_MODE` guard: anything but `research` fails startup), `core/errors.py`
- [x] ruff (lint + format, `eval`/`exec` banned), pyright strict, pytest with `unit`/`integration`/`golden` markers
- [~] GitHub Actions CI (lint, format check, type check, tests; Postgres/Redis services) — YAML parses and
      the same steps pass locally via `scripts/check.sh`; **not yet run on GitHub** (no remote)
- [~] `docker-compose.yml` (postgres+pgvector, redis) — written, **not executed** (no Docker on host)
- [x] `.env.example` (placeholders only), `.gitignore`, README skeleton
- [x] ADRs for the main ambiguities (`docs/adr/`)

**Day 2 — data layer**
- [ ] SQLAlchemy models + Alembic baseline migration for spec §5 core tables (+ CHECKs, FKs, indexes)
- [ ] Immutability guards: repository methods + DB trigger for finalized experiments / strategy versions
- [ ] `MarketDataProvider` protocol, `CsvFixtureProvider`, `BarsBatch`
- [ ] NYSE calendar wrapper (`exchange_calendars`), `available_at` computation (ADR-0004)
- [ ] Strict data checks: duplicates, nonpositive prices, H/L consistency, missing sessions, sort, stale, jumps
- [ ] `SnapshotService.freeze` → content-addressed immutable files + manifest SHA-256 (ADR-0005)
- [ ] Synthetic fixtures: rising, flat, gap-up, gap-down, missing session (split excluded explicitly)
- Tests: validation rejects each defect; snapshot hash stable; source correction ⇒ new snapshot;
  integration: clean migration on empty PostgreSQL (requires Docker/PG).

**Day 3 — Strategy DSL v0.1**
- [ ] Pydantic discriminated unions (SMA, EMA; GT/GTE/LT/LTE/EQ; AND/OR/NOT), `extra="forbid"`
- [ ] Semantic validation: windows, symbols, finite weights, Σw ≤ 1, cycles, future offsets,
      same-close execution, warmup ≥ max lookback
- [ ] Canonical JSON + SHA-256 hash; indicator DAG → typed IR; signal evaluation
- [ ] JSON Schema export + sample strategies
- Tests: invalid DSL / unknown operator / future reference rejected; SMA warmup exact; T signals
  invariant to prices after T.

**Day 4 — execution simulator**
- [ ] Event loop per session (open: fill pending; close: mark, ingest available bars, signal, enqueue)
- [ ] Broker: next-open fills, adverse slippage, commission, integer shares floored, cash check
- [ ] Idempotent order IDs, explicit CANCELED/REJECTED, fills ≤ remaining qty
- [ ] Portfolio ledger (Decimal), position & equity snapshots
- Tests: T close ⇒ ≥ T+1 open fill; gap fills; fees/rounding; no negative cash; missing sessions;
  duplicate IDs; property tests (accounting identity, no negative cash).

**Day 5 — metrics & golden tests**
- [ ] Total/annualized return, vol, Sharpe, Sortino, MDD, turnover, fees, trade count (ADR-0006)
- [ ] Buy-and-hold benchmark through the same fill/cost model
- [ ] `tests/golden/`: hand-calculated orders, fees, ending equity
- [ ] Lookahead mutation test (perturb future bars ⇒ past signals/fills unchanged)
- Tests: zero-vol / no-trade edge cases; byte-identical canonical outputs on rerun.

**Day 6 — experiments & API**
- [ ] Experiment persistence, lifecycle state machine, immutable finalized results
- [ ] Artifact writer: equity CSV, fills, orders, metrics JSON, manifest (code revision, hashes, seed)
- [ ] FastAPI `/api/v1`: health, strategies, versions, compile, experiments (202 + poll), metrics
- [ ] Synchronous local worker behind an async-compatible `TaskQueue` interface (Redis impl later)
- Tests: POST /experiments → GET completed; immutability; structured error codes.

**Day 7 — demo & hardening**
- [ ] `scripts/run_demo.py` (experiment ID, data hash, strategy hash, net metrics, artifact paths)
- [ ] README quickstart, `docs/KNOWN_LIMITATIONS.md`, reproducibility check (run twice, diff)
- [ ] Full Week-1 acceptance command list from spec §14 executed and recorded

### Weeks 2–3 — research agents
- [ ] Typed LLM gateway, fake provider for CI, versioned prompts + hashes under `agents/prompts/`
- [ ] Tool permission manifests per agent; budget caps (calls/tokens/USD/time); ≤2 DSL retries
- [ ] Orchestrator (LangGraph only after deterministic pipeline is stable), idempotent checkpointed nodes
- [ ] Research task API with idempotency keys; `AgentRun` audit
- Acceptance: fake-agent pipeline creates and evaluates a valid DSL unattended.

### Weeks 4–5 — memory & reflection
- [ ] Experience model, statuses, visibility; ACL + as-of cutoff applied before ranking
- [ ] Reflection schema, evidence linkage, retrieved-ID logging; pgvector optional (model/dim chosen first)
- Acceptance: holdout-access tests prove no leakage.

### Weeks 6–8 — evolution & validation
- [ ] `EvolutionService.propose_variants`, mutation operators, immutable lineage, full trial count
- [ ] Walk-forward folds, purge/embargo, cost stress, perturbation, bootstrap, deflated Sharpe
- [ ] Deterministic preregistered verdict policy; one-shot holdout
- Acceptance: reproducible rankings, no leakage.

### Weeks 9–10 — paper simulation
- [ ] Paper adapter (simulated only), order state machine, restart/replay, reconciliation, kill switch

### Weeks 11–12 — controlled study
- [ ] A/B/C/D arms with matched budgets, paired fold-level comparisons, report with limitations

## 3. Architecture decisions

| ADR | Title | Status |
|---|---|---|
| [0001](adr/0001-modular-monolith-src-layout.md) | Modular monolith, src layout, module boundaries | Accepted |
| [0002](adr/0002-toolchain-and-environment.md) | Toolchain, dependency pinning, environment gaps | Accepted |
| [0003](adr/0003-numeric-and-rounding-policy.md) | Decimal boundaries, rounding, integer shares | Accepted |
| [0004](adr/0004-time-and-data-availability.md) | Time zones, session dates, `available_at` | Accepted |
| [0005](adr/0005-immutable-snapshot-storage.md) | Content-addressed immutable data snapshots | Accepted |
| [0006](adr/0006-metric-conventions.md) | Metric conventions and edge cases | Accepted |
| [0007](adr/0007-memory-arm-b-intervention.md) | Arm B (fixed strategy + memory) definition | Proposed — decide in Week 4 |

## 4. Open questions (need a decision before the listed milestone)

- Real market data provider + license (only needed after Week 1; fixtures suffice until then).
- Embedding model and vector dimension (Week 4; no `VECTOR(N)` column before that).
- Redis queue library (RQ vs. arq vs. hand-rolled) — Day 6 keeps a sync worker behind an interface.
- Split handling: v0.1 fixtures exclude splits explicitly until a corporate-action engine exists.
