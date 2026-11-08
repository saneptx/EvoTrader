# ADR-0003: Numeric boundaries, rounding and integer shares

- Status: Accepted (2026-11-09); implemented Day 4

## Context
Spec §3 requires `Decimal` for money/positions at order/account boundaries and float64 for indicators,
with conversion boundaries documented.

## Decision
- **float64** only inside indicator/signal computation (`dsl`). Signals are booleans/target weights.
- **Decimal** for prices entering the broker, fills, fees, cash, quantities, equity. Context precision 28.
- Conversion boundary: bar prices are stored as `NUMERIC(20,8)` / parsed from CSV as `Decimal` directly
  (never through float). Indicators receive `float(Decimal)`; the broker never consumes indicator floats.
- Target weights (DSL floats in [0,1]) are converted with `Decimal(str(w))`.
- Fill price = `open * (1 ± slippage_bps/10000)`, quantized to 8 dp, `ROUND_HALF_EVEN`.
- Fee = `|qty * fill_price| * commission_bps/10000`, quantized to 8 dp, `ROUND_HALF_EVEN`.
- Quantity: integer shares, `floor` for buys to the affordable amount *including* fee; sells are limited
  to held shares. No fractional shares, no shorting, no borrowing, cash never negative.
- Sells are processed before buys within a session so released cash can fund buys.

## Consequences
Golden tests (Day 5) hand-compute to 8 dp; any change to these rules is a golden-file change reviewed as code.
