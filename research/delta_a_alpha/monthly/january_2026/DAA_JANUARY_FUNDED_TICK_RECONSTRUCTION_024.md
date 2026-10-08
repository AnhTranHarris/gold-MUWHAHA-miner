# DAA January 2026 — Actual Dukascopy Quote Funded-Execution Reconstruction 024

**Status:** COMPLETE for the *new, disclosed reconstructed engine*, **NOT COMPLETE** for exact frozen January-131E vertical-grid economic parity. The latter requires reinstating the precise original profit-funded 049→051 parent scheduler, 075/119 renewal ownership, 131D coverage/coldstart rules and 131E per-layer cap arbitration, plus bounded L7 recovery. This is a scientifically useful financial baseline but **not an accepted replacement for the original V1**.

## Source and execution

- Source: `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5` — **9,135,062** time-ordered XAUUSD raw Dukascopy Bid/Ask ticks; 5,766 observed five-minute bars. **August/September never opened.**
- Fixed **0.01 lot** throughout. One $1.00 gold price move is modeled as $1 P/L (assuming 0.01 lot = 1 troy ounce of XAUUSD). Actual broker contract details must be confirmed. Actual quote spread is embedded by buying at Ask/selling at Bid; separate **$0.02 round-trip transaction-cost assumption** per ticket. No commissions/swap/market impact/slippage calibration beyond that assumed cost; no real Coinexx margin certification.
- Completed H4/H1/M15/M5 EMAs8/21 use prior **completed** bars, never the current unfinished bar. L2 auction-tail state uses only the last 12 and 48 (with at least 144 available) *completed* M5 ranges. No month/date inputs in the entry signals. January file lacks December 2025 warmup so the full model cannot certify the owner-required five-minute startup SLA from Jan 1; early actionable state is absent.
- Real tick first-touch TP/SL/timed exits; every filled trade reconciles to contemporaneous actual quote integer values. Trading P/L and full-tick floating-equity are simulated simultaneously; no reuse of unfunded shadow outcomes. One additional physical order maximum per unique source tick. A single absolute cap is applied to **all sources** (16/64/128/256).
- Source code: `jan024_reconstructed_full_portfolio.py`. Operational audit: `build_checkpoint_024.py`.

## Original V1 mechanisms recovered as prototypes

- **L0:** exact ordered raw executable Bid/Ask entry/exit arithmetic, quote chronology and ledger.
- **L1:** independent observed UTC session/hour routing. Does not yet reproduce *all* original 131E grid genealogy / DST transition / separate geometry adjustments.
- **L2:** completed H4/H1/M15/M5 and completed-M5 spread/opportunity-awareness; January warmup limitations explicit.
- **L3:** reconstructed source-selected January 131D London/overlap/NY hourly ownership cells (with source-defined heartbeat and lifecycles). The initially attempted **broad** harvester was rejected for destroying gross loss and PF; archived Jan coverage differs in some density and cap handling.
- **L4:** original-structure Asia02 continuation cell with TP $12/SL $4 / 300 s hold, fixed 0.01.
- **L5:** Watchdog-style child renewals, TP quantum 1.19 / 1.10, but **wrong parent selection** compared with exact original 049/051/075. This reconstruction generates only tens of Watchdog funded children versus many thousands in original 131E. **Not parity-certified and the principal fidelity blocker.**
- **L6:** additional January 131D native cells UTC10/13/21 with causal completed-HTF selection and original TP/SL/time profiles.
- **L7:** recovery diagnosis/observation only; original independent funded conditional recovery **not reconstructed here**. No substitute blind loss-reversal is promoted.
- **L8:** global portfolio cap, full floating-equity and closed-balance DD; **broker margin, maintenance margin/stopout, gaps/slippage, and account-size ladder not certified**.

## Eight funded-execution scenarios (not original 131E replay)

| Physical global cap | Config | Net $ | Trades | Gross loss $ | PF | Win % | Full-tick equity DD $ | Positive days | Positive weeks |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | Source-selected V1 reconstruction | 3,848.77 | 1,995 | -2,055.99 | 2.87 | 63.91 | 452.56 | 15 | 4/4 |
| 16 | + April-awareness renewal gate | 3,861.19 | 1,985 | -2,036.94 | 2.90 | 63.88 | 452.56 | 15 | 4/4 |
| 64 | Source-selected V1 reconstruction | 12,496.98 | 5,240 | -6,098.86 | 3.05 | 66.24 | 1,761.11 | 18 | 4/4 |
| 64 | + April-awareness renewal gate | 12,509.40 | 5,230 | -6,079.81 | 3.06 | 66.23 | 1,761.11 | 18 | 4/4 |
| 128 | Source-selected V1 reconstruction | 20,469.05 | 7,213 | -7,883.05 | 3.60 | 69.06 | 3,246.53 | 18 | 4/4 |
| 128 | + April-awareness renewal gate | 20,481.46 | 7,203 | -7,864.00 | 3.60 | 69.05 | 3,246.53 | 18 | 4/4 |
| 256 | Source-selected V1 reconstruction | 34,944.45 | 9,914 | -10,410.51 | 4.36 | 72.07 | 5,574.91 | 17 | 4/4 |
| 256 | + April-awareness renewal gate | 34,956.86 | 9,904 | -10,391.46 | 4.36 | 72.07 | 5,574.91 | 17 | 4/4 |

These results are **not** the original month-specialized $194,425.92 January 131E result. Its original normalized P75 spread, recovered credit router/Watchdog and 640 open positions are different, and historical 131E was January-outcome-selected. The current reconstruction cannot be used to conclude 131E would earn the above on raw quotes.

## Key interpretation

1. Original January 131E: archived normalized-execution L35_C640, 80,929 tickets, +$194,425.92, -$3,642.86 gross loss, PF54.37, 98.03% win, **640 open** and ~$57,139 full-equity DD. **Not executable raw-quote proof.**
2. This bounded raw-quote reconstruction is **profitable but nowhere near the original quality/velocity**. At cap256 source-selected: about 9,914 trades, PF4.36, -$10.4K gross loss. This exposes missing original opportunity-generation/renewal fidelity.
3. **The April-derived renewal-only gate is not accepted:** approximately +$12.41 net at each cap, slightly fewer funded trades; equity DD unchanged. No compelling alpha or portfolio improvement.
4. Source-specific V1 ownership is necessary. The broad preliminary hourly prototype at cap64 earned +$15,855.91 but incurred -$60,996.05 gross loss and PF1.26; restoring original-selected source cells reduced gross loss to -$6,098.86 and raised PF to 3.05, with lower net and volume. This is source-fidelity correction, not a novel alpha breakthrough.
5. The model still **fails certification** for arbitrary-start five-minute readiness, L7 recovery parity, original 049/051 profit-funded parent admission, broker margin and the $100k→$1k→$500→$300→$100 capital ladder.

## Next blocked exact-fidelity task

Reinstall the actual original helper tree and verified archived scientific code/streams: 019 hourly heartbeat + 024 intrinsic + 049 parent-profit funded surge + 051 causal funding selection + 075 exact parent window + 084 child ownership + 119 gate + 131A/B depth + 131D selected session/coldstart + 131E heat. Patch only execution quote input to original actual Dukascopy Bid/Ask; **do not simultaneously redesign the originally selected signals**. Independently calculate baseline full fundable tape and tick-equity under one owner authority. Then enable independently tested April market-awareness adaptation and record exact daily/weekly/monthly economics. Do **not** promote a partial reconstruction as the canonical V1 economic floor.

In particular, Watchdog at 131E uses many *distinct* admitted parent streams; substituting a first-heartbeat-per-cell single campaign (done in 024) is not scientifically equivalent. The original `renewal_owned` **closes residual child positions at the corresponding original parent end** and tracks funded children. The 024 experimental Watchdog stream has different genealogy and must be replaced, not refined until it fits historical January profits.

## Daily, weekly and reproducible crash-safe outputs

- `comparison_monthly.csv`, `comparison_daily.csv`, `comparison_weekly.csv` — complete per-variant portfolio comparison; active-day and weekly metrics including gross P/L, PF, win and funded ticket velocity.
- `baseline_capN_selected_trades.csv`, `aware_capN_selected_trades.csv` — trade-by-trade entry/exit tick indexes, actual raw quote fills, realized result, direction, exit reason, source, UTC date/week for four global caps.
- `*_score.json`, `QA_FLAGS_024.json` — atomic variant checkpoints and exact quote parity results. No fabricated timestamps or fills.
- `jan024_reconstructed_full_portfolio.py` and `build_checkpoint_024.py` — reproducible code, raw tick source SHA lock, all QA assertions. `SHA256SUMS_024.txt` provides checksums.
- The package is self-contained **except** the 66MB original January Dukascopy gzip, which is held separately and strictly hash-checked. No August data accessed.

**Owner governance remains binding:** complete L0–L8 self-adjusting EA, high net/low gross loss/high PF/win/velocity at daily/weekly/monthly frequency; arbitrary T0 plus five-minute trade readiness from existing prestart broker history; never trade from future data or shadow-funded credit; eventual small-account survivability. January–July development, August and September sealed blind holdouts.