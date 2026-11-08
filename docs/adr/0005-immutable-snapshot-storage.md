# ADR-0005: Content-addressed immutable data snapshots

- Status: Accepted (2026-11-09); implemented Day 2

## Context
Spec §5 forbids snapshots that merely point at mutable bars; a source correction must create a new snapshot.

## Decision
- `SnapshotService.freeze` writes bars to `ARTIFACT_ROOT/snapshots/<sha256>/bars.csv` in a canonical
  form: sorted by (symbol, session_date), fixed column order, Decimal strings normalized, LF endings, UTF-8.
- `dataset_hash` = SHA-256 of that canonical file content; the manifest (symbols, date range, source,
  ingestion version, cutoff, row counts, per-symbol hashes) is stored in `data_snapshots.manifest`.
- CSV (not Parquet) for v0.1 because byte-level determinism across library versions is easy to guarantee;
  Parquet may be added later as a derived cache, never as the hashed source of truth.
- Files are written once (write to temp, fsync, atomic rename; refuse to overwrite a differing file).

## Consequences
Backtests read snapshot files, not live tables, so results are reproducible from `dataset_hash` alone.
