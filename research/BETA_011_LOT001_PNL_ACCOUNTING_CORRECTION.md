# BETA 011 — 0.01-Lot P&L Accounting Audit and Commission Correction

**Purpose:** Re-audit R09_BETA_001 Jan–Jul economics at the exact 0.01-lot scale before accepting/rejecting the entry candidate.

## Finding

The prior Python candidate correctly treated a $1.00 XAUUSD price move as $1.00 price P&L at 0.01 lot, but it incorrectly charged **$0.20 round-trip commission**. The actual Coinexx R9 REAL Strategy Tester deal ledger shows:

- EA input `InpLots=0.01`.
- Sample entry deal volume `0.01`, commission `-$0.01`.
- Matching exit deal volume `0.01`, commission `-$0.01`.
- Example buy 4332.34 -> sell 4331.68 produces tester Profit `-$0.66`, exactly the -$0.66 price change at 0.01 lot.

This empirically validates the effective P&L multiplier for this report as:

`0.01 lot × 100 oz/lot = 1 oz`, therefore `$1/oz price move = $1 trade price P&L`.

Correct 0.01-lot closed-trade model used here:

`price_pnl_usd = side × (exit_price - entry_price) × 100 × 0.01`

`roundtrip_commission_usd = $0.01 entry + $0.01 exit = $0.02`

`net_trade_pnl_usd = price_pnl_usd - $0.02`

The previous simulation used the correct implicit price multiplier (=1.0), but a 10x excessive commission (`$0.20` instead of `$0.02`).

## Corrected Jan–Jul R09_BETA_001

| Month | Net P&L | Gross Loss | Cumulative Max DD | Trades | Wins | Win rate |
|---|---:|---:|---:|---:|---:|---:|
| Jan | -$21,026.53 | -$23,496.48 | $21,026.53 | 31,250 | 8,606 | 27.54% |
| Feb | -$21,488.91 | -$24,438.06 | $42,515.43 | 27,117 | 7,278 | 26.84% |
| Mar | -$37,586.67 | -$42,581.33 | $80,102.60 | 49,444 | 13,607 | 27.52% |
| Apr | -$21,198.48 | -$23,534.21 | $101,300.58 | 30,134 | 8,032 | 26.65% |
| May | -$18,993.58 | -$21,231.68 | $120,294.16 | 31,178 | 8,787 | 28.18% |
| Jun | -$21,400.43 | -$23,909.88 | $141,694.59 | 34,522 | 9,763 | 28.28% |
| Jul | -$15,521.76 | -$16,800.89 | $157,216.35 | 23,051 | 5,577 | 24.19% |

Aggregate:
- Trades: **226,696**
- Winning trades: **61,650**
- Win rate: **27.195%**
- Gross profit: **+$18,776.18**
- Gross loss: **-$175,992.53**
- Net P&L: **-$157,216.35**
- Max drawdown: **$157,216.35**

## Corrected same-feed R9 control

- Trades: **246,404**
- Wins: **58,279**
- Win rate: **23.652%**
- Gross profit: **+$16,701.11**
- Gross loss: **-$208,514.22**
- Net P&L: **-$191,813.12**
- Max drawdown: **$191,813.12**

Candidate versus same-feed R9 control after correcting commission:
- Winning-trade count: **+5.78%** (not >10%)
- Relative win-rate improvement: **+14.98%** (+3.54 percentage points absolute)
- Net-loss reduction: **18.04%**
- Gross-loss reduction: **15.60%**
- Max-DD reduction: **18.04%**

## Scientific consequence

The candidate should **not** be discarded. The corrected 0.01-lot accounting makes its economics materially better than previously reported. However, the formal statement that it improved absolute winning-trade count by >10% is withdrawn: after applying the correct broker commission to both candidate and control, winning-count improvement is +5.78% because many small R9-control trades also become profitable when the excessive fee is removed.

The entry candidate still clears >10% on entry accuracy (relative win rate), net-loss reduction, gross-loss reduction, and drawdown reduction. It remains loss-making and is not an approved EA. The owner/MQL5 gate remains separate.

## Caveat

MT5 exposes commission as separate deal fields. This Python audit groups the full round-trip commission into closed-trade P&L for consistent same-feed comparisons. The eventual Coinexx MT5 Strategy Tester report remains authoritative for exact broker-native report presentation.

August was not read.