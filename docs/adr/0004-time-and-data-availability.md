# ADR-0004: Time zones, session dates and data availability

- Status: Accepted (2026-11-09); implemented Day 2

## Context
Spec §6/§7 require UTC event times, NYSE session dates, and that signals use only bars with
`available_at <= decision_time`.

## Decision
- `session_date` is the NYSE session (a `date`, America/New_York). All timestamps are tz-aware UTC.
- Default `available_at` for a daily bar = that session's actual close (from `exchange_calendars`,
  early closes respected) + `availability_delay` (default **0 min** for fixtures; configurable per provider).
- `decision_time` for `signal_at = SESSION_CLOSE` = the session close. If a bar's `available_at` exceeds
  the decision time (delay > 0), that bar is not visible and the signal effectively lags one session.
- Orders produced at decision time T fill at the open of the next NYSE session after T; never same-close.
- Missing sessions in data (calendar session without a bar) are reported by validation; the engine
  produces no fills and no fabricated bars for that symbol on that session.

## Consequences
A "zero delay" assumption is optimistic for real vendors; it is listed in `KNOWN_LIMITATIONS.md`.
