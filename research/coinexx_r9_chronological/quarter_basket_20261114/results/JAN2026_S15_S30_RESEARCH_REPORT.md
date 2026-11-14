# R9 v1.94 — 15-second basket / 15- and 30-second breakout January Coinexx report

**Date:** 2026-11-14. **Verdict:** FAIL for profitability; no MT5 promotion.

## Control and economic assumptions

All **7,699,274** original January Coinexx quote rows, source gzip SHA256 `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`, were processed ONCE in source order. Unchanged R9 Python control matched ALL **32,179** frozen trade entries and exits on exact ordinals, timestamps, prices, direction, P&L, and cause. Each new basket arm independently recomputed entries, position occupancy, original stops, subsequent exits and **15-second basket-local opposite rearms**.

Financial units are HYPOTHETICAL: Coinexx 0.01 lot, K=1 USD account cash per one XAUUSD price-dollar, and extra C=0.20 account cash per completed trade beyond original Bid/Ask spread. Actual fills, commission, broker contract conversion and stop/freeze rejections are NOT available from ticklogger. Full portfolio governor is **not simulated** in this January experiment; existing stricter original 10% peak and 4–12% daily gross loss remain design controls and are NOT relaxed to 25%.

| Arm | Completed trades | Retention | Full January net | Mean net/trade | Gross losing cash | Mean hold | Trades ≥$0.50 NET | Fraction ≥$0.50 NET |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Original 60s R9 | 32,179 | 100.00% | -$12,488.92 | -$0.3881 | $14,318.70 | 5.82s | 1,010 | 3.14% |
| 15s basket / 15s breakout / ORIGINAL exit | 38,493 | 119.62% | -$14,460.70 | -$0.3757 | $16,795.84 | 5.53s | 1,291 | 3.35% |
| **15s basket / 30s breakout / ORIGINAL exit** | **32,295** | **100.36%** | **-$12,122.08** | **-$0.3754** | **$14,123.71** | **5.52s** | **1,126** | **3.49%** |
| 15s basket / 15s breakout / $0.50 cash harvest | 35,990 | 111.84% | -$14,247.57 | -$0.3959 | $20,271.29 | 10.80s | 9,467 | 26.30% |
| 15s basket / 30s breakout / $0.50 cash harvest | 30,504 | 94.80% | -$12,041.06 | -$0.3947 | $17,134.22 | 10.81s | 8,011 | 26.26% |
| 15s basket / 30s breakout / quote-only nested-trend PROBE | 29,757 | 92.47% | -$11,595.08 | -$0.3897 | $16,722.29 | 11.12s | 4,922 | 16.54% |

The 15/30 breakout with ORIGINAL exits improves relative January net by **+$366.84** while preserving **100.36%** volume and reducing gross losing cash by ~$194.99. It still loses money. At C=0 the same arm is **-$5,663.08** (spread is already paid once in bid/ask entry/exit). The 15/15-only breakout produces more trades but increases aggregate losses.

The 15/30 cash harvest raises the fraction of ≥$0.50 winners to 26.26%, but **increases gross realized cash losses by $2,815.52** and misses the ≥95% volume requirement by ~0.20 percentage points. The nested-trend arm reduces aggregate modeled losses relatively but has worse gross losing cash than baseline, <95% volume and **zero validated original 155-feature model-assisted runner decisions**. The new entry universe has NO verified original 155-feature scores; all missing scores remain missing, never fabricated.

The owner’s **70% trade frequency above $0.50 net** and positive net cash/hour are both missed. These rules are NOT deployable. Modeled cash loss may exceed the intended $2 stop during quote gaps; 25% capital maximum is an emergency ceiling, **not a guaranteed historical account loss bound**.

## Exactly what was changed in Python research

- 15-second basket `B(t)=15 floor(t/15)` anchored at first observed quote midpoint `M_B` in each basket.
- Predeclared midpoint **price-displacement** requirement `|M_t-M_B|>=0.10 XAU price dollars`. This 10-cent displacement is NOT permission to take 10-cent NET trading profit.
- Independently require breakout beyond prior **completed** observed 1-second midpoint CLOSE extrema over h=15 or 30 seconds, by 0.01 price units, with 4/8 observed seconds respectively and most recent completed second ≤2s old. The 30s high/low condition is also stricter than the nested 15s condition when both are available.
- Original ATR M5, S1 directional quality, spread/session gates and stop logic remain in every entry-only arm. Each basket may rearm opposite only if entry and closure both occur inside that same basket; no stale rearm spills into a new basket.
- $0.50 NET harvest / $1.75 NET stretch, tighter original stop, intended maximum $2 loss, 120s stranded-position fallback and original stricter governor design limits are retained in alternative exit arms. A separate ±1e-9 numerical tolerance fixes a floating-point compare at **exactly** half-dollar cash, on this research branch ONLY.
- Nested-trend exploratory arm uses quote-based 3/10/30/120s momentum plus spread/quote-arrival stress, **not** real depth, volume, signed OFI, or any validated 155-feature HOLD utility.

## Native MT5 indicator mapping

15s and 30s are NOT ordinary MT5 native `ENUM_TIMEFRAMES`; future MT5 requires a short bounded completed quote/second ring, not custom fabricated history. Completed native `iATR(PERIOD_M5,14)`, `iADXWilder(PERIOD_M1)` (+DI/−DI), `iMA(...MODE_EMA)`, `iStdDev`/`iBands`, optional `iFrAMA`/`iAMA` are reconstructible from Coinexx Bid-derived OHLC, subject to exact bar warm-up/parity. `iVolumes(VOLUME_TICK)` supplies quote count, NOT executed volume. Real-volume VWAP, depth, VPIN, actual order-flow imbalance and order-book microprice are absent and must not be claimed.

MQL5 `OnTick` coalescing, broker execution costs/rejects, stop/freeze distances, true 155-feature online inference and full account gross-loss governor remain separate release gates; see MetaQuotes https://www.mql5.com/en/docs/event_handlers/ontick and https://www.mql5.com/en/docs/indicators.

## Scientific disposition

**STOP broad sweep after January fails.** Do not retrain the approved 155-feature model on a NEW 15s entry universe and then compare its in-sample AUC to the old model. Do not clone tick archives. The strongest bounded *entry-only* research lead is the 15s basket with the 30s completed-midquote breakout, but it is only **less negative**, not profitable. Any future validation must hold out new dates, verify brokerage K/C and account-level execution, and separately test whether improving entry geometry AND cash-loss distributions yields positive whole-system returns with high throughput.

Research code and compact machine-readable full scorecard are in this branch; owner-compiled v1.94 and critical v1.90 rollback were left unchanged.
