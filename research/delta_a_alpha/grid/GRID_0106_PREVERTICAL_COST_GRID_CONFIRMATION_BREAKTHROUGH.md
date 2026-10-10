# GRID-0106 — Cost-consistent virtual grid + causal retrace confirmation

**Research result:** A reproducible **pre-session, pre-HTF, pre-Vertical-Grid event-generation improvement**, evaluated on unmodified Dukascopy XAUUSD January–April 2026 Bid/Ask ticks. **No trade direction edge or funded profitability is certified.** No orders, position averaging, martingale lots, account equity or risk governor are invoked.

## Core contribution

The creator's rolling-extreme contrarian grid is retained as the source of *geometric price level opportunities*, but physical losing-inventory accumulation is replaced by **virtual anchors/rung memory**. The new candidate generator combines:

1. **Executable-friction-normalized rung distance**, recomputed from information available at each quote:
   `gap_raw(t) = max(750, floor(1.25 × (ask_raw(t)-bid_raw(t))))` where raw prices are 1/1000 USD. This directly counters the January/February problem where the creator's nominal step was often smaller than Dukascopy's current Bid/Ask spread. The value 1.25 is a research hypothesis, not calibrated broker optimum.
2. **Virtual rung progression without funded averaging**: start at the prior observed midprice anchor, record down/up grid crossings one per tick, carry continuation depth and cross timestamp, update anchors without placing orders. No position ever gets doubled.
3. **Causal direction-change/retrace confirmation**: after a DOWN grid crossing, track the *subsequent observed low*; emit a new shadow BUY hypothesis only after current observed mid has bounced at least 25% of the gap from that low. Reverse this logic after an UP grid crossing. A new crossing supersedes the former pending wave. There is no future-looking swing-high/swing-low detection or backdated event.
4. **10-second minimum spacing between emitted events** and one event per observed input tick. Track the alternative **25%-step continuation confirmation** stream independently, so later research can compare reversion and continuation without altering positions.

This is a **grid-intrinsic event clock**; it uses no sessions, DST labels, HTF charts, trading indicators, account balance, filled positions, stops, exits, or R9 direction matching.

## Source-backed research inspiration

- MegaJoctan source: https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot — source grid crossings, last-entry anchoring, and no-stop/martingale exposition; only its geometric mechanism was reconstructed.
- MetaQuotes `Grid and martingale`: https://www.mql5.com/en/articles/8390 — spacing, gaps and false assumptions about price movement; inspiration, **not evidence of a ready edge**.
- MetaQuotes `Building a Research-Grounded Grid EA`: https://www.mql5.com/en/articles/21833 — bounded restartable grid cycles and regime-aware spacing. Its lot scaling is **not** imported.
- MetaQuotes `A Virtual Order Manager`: https://www.mql5.com/en/articles/88 — separation of software-maintained virtual levels from broker inventory, with important outage/slippage caveats.
- FX directional-change literature: https://link.springer.com/article/10.1007/s10462-022-10307-0 — event/intrinsic-time boundaries rather than purely clock-sampled bars; not a proof of profit for this implementation.

## Quantitative source comparison

| 2026 raw Bid/Ask month | R9 SYNTH trade-count reference | Improved crossing candidates | Confirmed-bounce candidates | Bounce / R9 reference |
|---|---:|---:|---:|---:|
| January | 27,980 | 58,821 | **57,500** | **2.06×** |
| February | 33,523 | 59,386 | **57,415** | **1.71×** |
| March | 40,985 | 81,551 | **79,351** | **1.94×** |
| April | 31,758 | 55,895 | **54,583** | **1.72×** |

Original pristine file SHA256s and all machine outputs are in `GRID_0106_MACHINE_RESULT.json`. The Jan 21 active original R9 report days had at least 75% of each report day's **RAW bounce events** under an **UNCONFIRMED Coinexx UTC+2** mapping. This is a shadow-capacity diagnostic only; it is **not** proof of the owner's final daily *quality-qualified executable opportunity* requirement.

### Verified mechanism-level quality improvements

- **No grid step smaller than contemporaneous spread** across all four months' approximately 249K confirmed-bounce events (integer-rounding floor yielded minimum observed ratio ~1.249). By contrast, the earlier fixed $0.75 grid had spread > step on 37.316% of January and 75% of February events.
- Quote-age sensitivity: fraction of event prices moving at least **half the grid gap** by the first observed quote at or after 250 ms:

| Month | Cost-scaled raw crossing | After 25%-gap retrace confirmation |
|---|---:|---:|
| January | 8.324% | **5.070%** |
| February | 12.042% | **6.791%** |
| March | 12.031% | **7.740%** |
| April | 7.539% | **4.739%** |

At 1,000 ms, the same comparison was 19.359% → **15.143%** (January), 23.435% → **16.624%** (February), 25.987% → **20.772%** (March), and 17.776% → **13.953%** (April). These are **quote-motion diagnostics**, not broker actual fills or slippage. The grids have different trigger timestamps; this is a prospective event-clock comparison, not a matched-trade causal improvement.

The separate **25%-step continuation confirmation** also kept substantial monthly populations: 51,183 / 51,379 / 72,136 / 48,173 raw events. Treat the continuation and reversal hypotheses as alternative research outputs, not two broker tickets.

## Explicit non-claims needed for reproducibility

- These events are **not trade executions**. R9's closed-trade population and grid raw events are different observables; the 75% daily gate and 175% monthly trade ceiling cannot be certified by candidate counts.
- **BUY after confirmed bounce has not shown profitable fixed-horizon quote-side returns on the native Dukascopy feed**, and the continuation alternative has likewise not demonstrated funded positive expectancy. Do not promote or describe as reliable correct-direction prediction.
- A deliberately separate grid-only causal feature forecasting screen likewise did not establish positive quote-side performance in January validation and February; no model or filter from that screen is accepted. We keep the successful *event geometry and latency-resilience engineering* only.
- The favorable-excursion envelope stored in the evidence bundle is hindsight **upper bound** and cannot serve as a pre-entry direction selector or win-rate claim.
- No L1–L7 vertical-session, HTF, Watchdog, recovery or L7 capital governor is activated. No $100,000 funded backtest here; that account balance is reserved for later whole-system research.
- Four-month quote spread differs from Coinexx execution spreads. Quote timestamps come from raw Dukascopy UTC; Coinexx report UTC+2 mapping remains hypothesis.

## Disposition and next research question

**Retain as a source-clean, four-month robust *grid opportunity-clock improvement***: adaptive spread-consistent cells + independently tracked virtual rung progression + confirmed retrace candidate stream. This is a grid-mechanics breakthrough in candidate throughput relative to friction and quote-delay sensitivity, **not yet a trading-edge breakthrough**.

**Do not yet activate sessions:** The user requests session-aware self-adjustment **after** high-volume *directionally credible, quality-qualified* opportunities approach R9 performance. Raw opportunity generation has reached R9-scale density; causal direction and funded economics have not. Next investigate intrinsic-time completed directional changes, grid overshoot state, first-passage adverse/momentum risk, and direction selection without lookahead or Martingale. Preserve later untouched data windows as genuine holdouts.

## How to reproduce

Python 3.11+; numpy, pandas, numba. Run `python -m unittest -v test_cost_grid_research`, then `python cost_grid_research.py 01`, `python cost_grid_research.py 02`, `python cost_grid_research.py 03`, `python cost_grid_research.py 04`, and `python cross_month_acceptance.py`. The input file names are configured in `cost_grid_research.py`. Research runner uses raw CSV.gz in read-only mode. Results are not used as training labels when emitting events; later prices are referenced only in evaluation utilities.
