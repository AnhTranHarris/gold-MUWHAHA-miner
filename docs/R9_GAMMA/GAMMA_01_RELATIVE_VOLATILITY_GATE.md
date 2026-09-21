# R9 GAMMA-01 — Session-Normalized Relative-Volatility Gate

**Status:** PYTHON VALIDATED / MT5 REAL-TICK CERTIFICATION PENDING  
**Parent:** `carson/r9-gamma-00-baseline`  
**Child:** `carson/r9-gamma-01-relative-volatility-gate`  
**EA:** `Experts/GoldMuwahahaMiner_R9_GAMMA_01_RelVolGate.mq5`  
**Instrument:** XAUUSD only  
**Research window:** January–July 2026  
**August 2026:** SEALED

## 1. Promotion decision

GAMMA-01 adds one mechanism to certified R9: a session-normalized M5 ATR gate.

The candidate is promoted to **MT5-testable GAMMA status**, not MT5 certification, because it:

- improves the fresh Jan–Jul R9-like Dukascopy replay in every month;
- improves net loss and gross loss simultaneously by more than the project's 5% meaningful-improvement threshold;
- preserves approximately 92.8% of baseline trade count;
- improves continuous Jan–Jul drawdown;
- survives a 1.40–1.60 parameter neighborhood;
- survives modeled spread stress from $0.18 through $0.25;
- is causal, deterministic, and directly reproducible in MQL5;
- changes no R9 entry geometry, S1 definition, stop, trail, hold time, rearm rule, or position size.

The next required gate is Coinexx MT5 **Every tick based on real ticks** testing against the same January–July interval.

## 2. Hypothesis

R9 already requires completed M5 ATR(14) to clear a session-specific absolute minimum:

- London: 2.00
- London/New York overlap: 1.75
- New York: 1.75
- off-session: 2.50

The fresh R9 REAL-like replay showed that simply clearing this floor still admits a large population of low-participation breakouts that repeatedly stop before useful favorable excursion develops.

The GAMMA-01 hypothesis is:

> A breakout should be eligible only when completed M5 ATR is materially above the volatility floor that R9 already considers minimally tradable for the current session.

This preserves R9's session model but turns the existing floor into a relative regime reference.

## 3. Causal formula

Let:

- `ATR_t` = ATR(14) from the **most recently completed M5 bar**;
- `A_s` = the existing R9 minimum ATR for the current session;
- `R_t` = session-normalized volatility ratio.

```text
R_t = ATR_t / A_s
```

GAMMA-01 requires:

```text
ATR_t >= A_s
AND
R_t >= 1.50
```

Since `A_s > 0`, this is equivalent to:

```text
ATR_t >= 1.50 * A_s
```

No unfinished M5 bar is used. The EA continues to call `CopyBuffer(..., shift=1, ...)`, as R9 did, so the feature is causal.

## 4. Why this is publicly reconstructible

The implementation is a clean-room integration of public ATR-regime ideas into R9's already-publicly-expressible ATR/session gate. No opaque commercial logic is required.

Primary reproducible references:

1. MetaQuotes MQL5 `iATR` reference:  
   https://www.mql5.com/en/docs/indicators/IATR

2. MetaQuotes MQL5 Wizard ATR article, which explicitly discusses ATR thresholds for breakout confirmation and gives 1.5×/2× ATR-style confirmation examples:  
   English: https://www.mql5.com/en/articles/16213  
   Chinese: https://www.mql5.com/zh/articles/16213  
   Japanese: https://www.mql5.com/ja/articles/16213

3. MetaQuotes volatility-breakout article explaining that low-volatility/noisy conditions are a major source of false breakouts and using ATR as a volatility qualification layer:  
   English: https://www.mql5.com/en/articles/19459  
   Japanese: https://www.mql5.com/ja/articles/19459

4. Chinese MQL5 Opening Range Breakout article using an ATR filter and a causal OnTick state machine around breakout/retest confirmation:  
   https://www.mql5.com/zh/articles/18486

5. Open-source TradingView ATR volatility-regime filter using relative/percentile ATR state rather than one fixed absolute volatility number:  
   https://www.tradingview.com/script/6he9Wwoe-Volatility-Regime-Filter-ATR-based/

Supporting community cross-checks, **not implementation sources**:

- Korean MQL5 public Gold Flash description combines an ATR adaptive volatility gate with session filtering for XAUUSD:  
  https://www.mql5.com/ko/market/product/180978
- Reddit systematic-trading discussions repeatedly describe ATR-based regime gating as a simple way to prevent trend/breakout systems from operating in incompatible low-volatility states. These are anecdotal community observations and were not used to choose the GAMMA threshold.

The value `1.50` was selected from this project's causal Dukascopy tests, not copied from a commercial EA.

## 5. Data and replay model

Canonical independent market path:

- Dukascopy XAUUSD ticks, January–July 2026.
- August remains sealed.
- The fresh engine replays the R9 minute bracket, completed-second S1 gate, completed M5 ATR regime gate, stop/trailing logic, max hold, and same-minute opposite rearm.
- Modeled spread stress: $0.18, $0.20, $0.23, $0.25.
- Fixed commission model used in the fresh engine: $0.02 round trip per 0.01-lot trade.

At $0.20 modeled spread, the fresh R9-like baseline reproduces the R9 REAL pathology closely:

- net: -$48,033.28 when months are evaluated individually;
- gross profit: $29,218.05;
- gross loss: -$77,251.32;
- PF: 0.3782;
- trades: 234,852.

The continuous Jan→Jul replay, which preserves ATR/tick state across month boundaries, produces:

- baseline net: -$48,159.34;
- baseline gross loss: -$77,459.11;
- baseline trades: 235,381;
- baseline max drawdown: $48,159.70.

The slight difference between isolated-month sums and continuous replay is expected because isolated monthly diagnostics reset indicator/state history. Continuous replay is the preferred aggregate representation.

## 6. Monthly results at $0.20 modeled spread

| Month | R9-like baseline net | GAMMA-01 net | Improvement | Baseline trades | GAMMA-01 trades |
|---|---:|---:|---:|---:|---:|
| Jan | -$6,867.47 | -$6,176.20 | +$691.27 | 33,471 | 30,181 |
| Feb | -$6,170.21 | -$6,041.34 | +$128.87 | 34,059 | 33,414 |
| Mar | -$7,617.09 | -$7,466.12 | +$150.97 | 38,340 | 37,665 |
| Apr | -$6,593.02 | -$6,057.68 | +$535.35 | 32,594 | 30,086 |
| May | -$7,060.87 | -$6,392.40 | +$668.47 | 32,383 | 29,357 |
| Jun | -$6,869.98 | -$6,360.89 | +$509.09 | 33,515 | 31,290 |
| Jul | -$6,854.62 | -$5,732.98 | +$1,121.65 | 30,490 | 25,856 |
| **Jan–Jul isolated sum** | **-$48,033.28** | **-$44,227.61** | **+$3,805.67** | **234,852** | **217,849** |

Every month improves.

## 7. Four-objective scorecard

At the $0.20 modeled-spread isolated-month comparison:

### Net profit / loss
- baseline: -$48,033.28
- GAMMA-01: -$44,227.61
- improvement: **$3,805.67 / 7.92%**

### Gross loss
- baseline: -$77,251.32
- GAMMA-01: -$71,952.26
- improvement: **$5,299.06 / 6.86% less gross loss**

### Trade count
- baseline: 234,852
- GAMMA-01: 217,849
- change: **-17,003 / -7.24%**
- retained activity: **92.76%**

### Drawdown
Continuous Jan→Jul:
- baseline max drawdown: $48,159.70
- GAMMA-01 max drawdown: $44,334.38
- improvement: **$3,825.32 / 7.94%**

No category is considered "locked" to the R9 SYNTH reference yet. Therefore the project does **not** introduce the $100/$200 daily-survivability layer at this checkpoint.

## 8. Parameter neighborhood

At $0.20 modeled spread:

| Min ATR/session ratio | Net | Gross loss | PF | Trades | Max monthly DD |
|---:|---:|---:|---:|---:|---:|
| 1.40 | -$45,434.05 | -$73,666.65 | 0.3832 | 223,394 | $7,511.77 |
| 1.45 | -$44,844.62 | -$72,826.47 | 0.3842 | 220,700 | $7,484.81 |
| **1.50** | **-$44,227.61** | **-$71,952.26** | **0.3853** | **217,849** | **$7,467.65** |
| 1.55 | -$43,521.03 | -$70,975.19 | 0.3868 | 214,763 | $7,438.04 |
| 1.60 | -$42,805.16 | -$69,967.45 | 0.3882 | 211,604 | $7,403.50 |

The response is monotonic across the tested neighborhood. The project selects **1.50 as a participation-preserving knee**, not as the threshold with the best in-sample net result.

Higher ratios continue to suppress losing opportunities but progressively sacrifice velocity. GAMMA-01 intentionally stops at 1.50 so later specialists can recover high-quality activity rather than solving losses by simply refusing to trade.

## 9. Spread stress

| Modeled spread | Baseline net | GAMMA-01 net | Net improvement | Baseline GL | GAMMA-01 GL | GL improvement | Trade-count change |
|---:|---:|---:|---:|---:|---:|---:|---:|
| $0.18 | -$43,251.77 | -$39,780.93 | 8.03% | -$73,020.96 | -$68,020.88 | 6.85% | -7.24% |
| $0.20 | -$48,033.28 | -$44,227.61 | 7.92% | -$77,251.32 | -$71,952.26 | 6.86% | -7.24% |
| $0.23 | -$55,324.20 | -$50,969.12 | 7.87% | -$83,686.55 | -$77,914.03 | 6.90% | -7.24% |
| $0.25 | -$60,264.54 | -$55,532.83 | 7.85% | -$88,130.62 | -$82,033.83 | 6.92% | -7.24% |

The effect persists through the complete tested cost range.

## 10. Why GAMMA-01 is not merely trade suppression

The gate does reduce participation, so activity reduction must be treated as a cost. However, it is materially better than the blunt catastrophe-memory experiments:

- the 1.50 gate removes only about 7.2% of trades;
- net loss improves about 7.9%;
- gross loss improves about 6.9%;
- every month improves;
- the result is stable through neighboring thresholds and spread assumptions.

A blunt 60-second same-direction cooldown produced a larger nominal loss reduction, but at approximately twice the activity sacrifice and without identifying a clearly inferior market state. GAMMA-01 instead removes a reproducible **low-relative-volatility regime** before entry.

It therefore qualifies as a regime-selection breakthrough, not a standalone profitable strategy.

## 11. Exact MQL5 change

The cumulative EA remains exact R9 except for:

```mql5
input double InpMinSessionAtrRatio = 1.50;
```

and inside the completed-ATR gate:

```mql5
const double mn=SessionAtrMinimum(CurrentSession());
const double atrRatio=(mn>0.0 ? atr/mn : 1.0);

if(mn>0.0 &&
   (atr+1e-12<mn ||
    atrRatio+1e-12<InpMinSessionAtrRatio))
{
   return false;
}
```

The completed M5 ATR comes from the same R9 `CopyBuffer(..., 1, 1, ...)` path. No current/unclosed M5 candle is read.

## 12. Rejected alternatives preceding this checkpoint

Fresh research rejected or withheld:

- wider stop by itself;
- immediate failed-ignition exits;
- plain persistence delay as standalone alpha;
- fast sweep/reclaim fade without regime ownership;
- absolute 10-second range threshold as a universal gate;
- direct transplantation of historical R10 P3/P4/P6/router constants;
- immediate CONTINUE/FADE classification under the original R9 lifecycle;
- public pullback/reacceleration prototype in its first tested lifecycle;
- blunt catastrophe cooldown as the preferred first GAMMA checkpoint.

These may remain research components, but none is silently bundled into GAMMA-01.

## 13. Known limitations

1. The Dukascopy engine is an independent causal reconstruction, not Coinexx MT5 itself.
2. The Python model uses controlled spread assumptions; Coinexx spread varies tick by tick.
3. Python commission/execution assumptions do not fully reproduce broker execution.
4. GAMMA-01 remains net-negative in the independent replay. Its value is a robust reduction in the R9 REAL failure state, not final profitability.
5. Threshold selection has seen January–July diagnostics during the overall research program. August therefore remains the only sealed future month and is not used here.
6. MT5 compile and real-tick Strategy Tester evidence are still required before this checkpoint can be called MT5-certified.

## 14. Required MT5 certification test

Run:

- EA: `GoldMuwahahaMiner_R9_GAMMA_01_RelVolGate.mq5`
- XAUUSD
- M1 tester chart
- January 1 through July 31, 2026
- fixed 0.01 lot
- first: **Every tick based on real ticks**
- second: **Every tick** for comparison
- same Coinexx terminal/symbol/account settings used for R9 certification

Compare directly against original R9:

- trade count
- net
- gross profit
- gross loss
- PF
- max/equity drawdown
- monthly attribution
- average hold
- stop/trailing/max-hold exit mix

Expected direction from Python, not guaranteed magnitude:

- lower trade count by roughly 5–10%;
- lower gross loss;
- lower drawdown;
- improved net result;
- improvement should not be concentrated in only one month.

## 15. Next cumulative research

If MT5 confirms GAMMA-01, the next checkpoint must branch from this branch.

Current leading GAMMA-02 research candidate is an independent H1/H4 structural-breakout sleeve family. It must be re-evaluated **on top of GAMMA-01**, including combined exposure, gross loss, drawdown, trade overlap and MT5 translatability. Historical R10 portfolio code does not count as certification.

---

**Promotion state:** PYTHON VALIDATED / MT5 REAL-TICK CERTIFICATION PENDING
