# ADR-0006: Metric conventions and edge cases

- Status: Accepted (2026-11-09); implemented Day 5

## Decision
- Daily simple returns from end-of-day equity; 252 sessions per year.
- Annualized return = `(final/initial)^(252/n) - 1` (n = number of daily returns).
- Volatility = sample std (ddof=1) of daily returns × √252.
- Sharpe = mean(daily) / std(daily) × √252 with **risk-free rate = 0** (documented, price-return only).
- Sortino = mean(daily) / downside deviation × √252, downside deviation = √mean(min(r,0)²).
- Max drawdown = min over t of equity_t / running_max_t − 1 (reported as a non-positive number).
- Turnover = Σ |traded notional| / mean equity, annualized ×252/n.
- Edge cases: fewer than 2 returns, zero volatility or zero downside deviation ⇒ ratio is `null`
  (never ±inf, never 0 by fabrication); no trades ⇒ trade_count 0, turnover 0, fees 0.
- Metrics are computed in float64 from Decimal equity and serialized with fixed rounding (12 significant
  digits) in canonical JSON so reruns are byte-identical.
