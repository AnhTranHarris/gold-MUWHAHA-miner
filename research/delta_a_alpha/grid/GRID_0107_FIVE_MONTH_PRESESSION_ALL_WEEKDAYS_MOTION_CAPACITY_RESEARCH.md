# GRID-0107 — Five-month pre-session creator-grid high-motion validation

**Date:** 2026-10-10  
**Scope:** only creator-derived shadow **grid event genesis**; no Sydney/Tokyo/London/NY session settings, H4/H1/M15/M5/other vertical quality layers, or funded execution.  
**Strategy status:** **NO PROFITABLE DIRECTIONAL TRADING EDGE VALIDATED.** High-motion tier is a *causal opportunity-quality feature*, not an actionable trading strategy. Frozen March and May verifications completed after preregistration.

## A substantive reproducible advance

One virtual price-ladder source, already frozen in GRID0104: produce unique tick-observed grid crossing events, with a moving price anchor, minimum 7 seconds per emitted event, and dynamic cell width `max($0.75, 1.5 * EWMA_0.001(Ask-Bid))`. All are source-native Bid/Ask quotes; all rungs are **virtual memory** rather than adverse funded position additions or Martingale volume scaling.

At an event timestamp `t`, calculate `K5 = abs(mid(t)-last source-available mid at/before t-300 seconds) / max(Ask(t)-Bid(t), $0.10)`. A broad **K5>=2** stream preserves quantity; a subset **K5>=4** carries higher empirical 120-second price-movement capacity. Recalculate the future labels ONLY for offline evaluation, never for the event generator.

**New evidence:** this simple, locked pre-session mechanism exhibited positive relative capacity uplift on **105/105 eligible Monday–Friday UTC days** spanning original January, February, March, April, May. Full UTC-date accounting (including partial Sunday quote days): **120/123 positive, one zero, two negative**. The two negatives were partial Sundays May 17 and May 24; the tie was January 25 (Sunday). Eligibility for paired day measure: >=100 future-valid baseline events and a nonempty K4 tier. Weekend exclusions apply *only to the described regular-weekday diagnostic*, NEVER to the complete daily accounting or selection. No calendar clock is a live grid input.

### Exact original source and unchanged R9 SYNTH monthly trade-count reference

| Original native Dukascopy month | Chronological source quotes | Raw virtual grid events | Broad K5>=2 (raw) | Strict K5>=4 (raw) | Original R9 SYNTH completed entries |
|---|---:|---:|---:|---:|---:|
| January | 9,135,062 | 55,732 | 42,782 | 31,674 | 27,980 |
| February | 7,538,339 | 53,958 | 41,233 | 30,190 | 33,523 |
| March **new locked validation** | 9,433,179 | 79,343 | 63,870 | 49,826 | 40,985 |
| April | 7,470,570 | 51,781 | 38,774 | 27,536 | 31,758 |
| May **independent locked verification** | 8,333,165 | 51,402 | 39,185 | 28,345 | 28,913 |
| **TOTAL** | **41,910,315** | **292,216** | **225,844** | **167,571** | **163,159** |

These are stage-zero **RAW** events. They do NOT satisfy the owner's ≥75% **daily qualified and broker-executable** R9 SYNTH opportunity constraint: no full L0–L7 risk/account checks, no broker latency or fills, and daily original R9 trade tapes have not been certified for every month. The separate ≤175% R9 SYNTH *monthly mean* actual completed trade ceiling is not tested since no positions were opened.

### Future 120-second two-spread price movement discrimination

At each event, take only the first original quote at or after t+120s, with no more than 10 seconds' quote lateness, and ask whether `abs(mid_future-mid_now) > 2*spread_now`.

| Month | Unfiltered grid (%) | K5>=4 tier (%) | Positive regular-weekday paired days | All eligible UTC quote days |
|---|---:|---:|---:|---|
| Jan | 62.17 | 67.67 | **21/21** | 22 improve, 1 tie |
| Feb | 61.80 | 66.37 | **20/20** | 22 improve |
| Mar | 67.99 | 71.30 | **22/22** | 27 improve |
| Apr | 58.99 | 64.32 | **21/21** | 25 improve |
| May | 59.29 | 63.95 | **21/21** | 24 improve, 2 decline (both partial Sundays) |

All five months also show aggregate improvement in an **unselectable hindsight oracle**: the maximum of BUY and SELL fixed-120s bid/ask markouts greater than $0.02, applied to the *better* direction known only in hindsight. The ORACLE improved on 102 of 105 regular weekdays. **This is a diagnostic upper bound, not win rate, entry accuracy, or executable P&L.**

**Interpretation:** The stronger K5 tier retains a smaller number of more displacement-capable price events. Some of the discriminating power arises from conditional volatility clustering by design. Labels overlap at seven-second event cadence. Paired daily-block resampling intervals are descriptive and cannot eliminate research-selection bias. This remains a real reproducible *movement-capacity stratification* across frozen-month validation (March, May) rather than a newly validated directional trading edge.

## Direction reliability status — high target preserved without invented success

A separate frozen Jan–Feb trained, April-selected, nonlinear grid-feature-only LightGBM regressor did produce a positive *April developmental* 600-second quote-side markout (+$0.80 for the signal confidence gate ≥1×spread; 6,354 shadow entries, ~20% of April R9 SYNTH monthly count). **Its subsequently registered raw-March evaluation was negative**: 15,892 primary shadow events, mean first-executable-quote 600-second markout **−$1.313**, or **−$1.333 after assumed $0.02 round-trip fee**, with positive mean on only **11/27** eligible March quote-active days. A stricter confidence gate was also negative. It was **not promoted**. This numerical fact is included solely to prevent a false claim of all-day profitable grid prediction; failure archaeology is retained in reproducible evidence, not as an investor-facing strategy.

Other grid-only controls screened event-flow momentum, acceleration, contrarian sign, quote-size imbalance (quoted liquidity, **not executed order flow**), and optimistic posted-limit cross-quote witnesses. None established stable positive net quote-side direction across the available native sources; source volumes and maker queue behavior cannot be presumed equivalent to future Coinexx fills. Literature on quote imbalance and adverse selection supports the questions, not our eventual profit hypothesis.

## Status and next research logic

- **PROMOTE ONLY AS A STAGE-ZERO FEATURE:** broad virtual price grid (K5>=2) plus stronger probability-of-substantial-movement annotation (K5>=4). No funded orders, no session adaptation or grid-only sign decision yet.
- **RETAIN:** a single non-martingale, fixed-size eventual 0.01 lot design; original $100k discovery portfolio capital assumption for future integrated funded simulation; $100–$300 future preferred path. Original R9 REAL/SYNTH are reference controls not future direction labels; August still sealed.
- **Next question:** Can a new pre-session, as-of **signed** price-path or liquidity response mechanism select *the right direction* at substantial density and demonstrate positive after-native-Bid/Ask markouts in a genuinely untouched next month? Do not recycle failed static sign or model as winner; June/July remain available future independent source tests after preregistration.
- **Critical requirement:** Do not call K5 magnitude success **105/105 profitable days** or 105/105 correctly predicted directions. The 105/105 result describes specifically **paired substantial-price-move screening lift** across regular weekdays. Daily quoteactive including Sundays **did** have declines and must remain visible.

## Source chronology and archived reproducibility

- Prior owner laws and active engine remain unchanged; project GitHub branch `delta-A-alpha`.
- 2026-10-10 GRID0107 March lockbox prereg: `research/delta_a_alpha/grid/GRID_0107_PREREG_MARCH_NATIVE_LOCKBOX_NO_RETUNING.md` (committed before March raw was read).
- May predeclared comparison: `research/delta_a_alpha/grid/GRID_0107_MAY_INDEPENDENT_K4_REPLICATION_PREREG.md` (committed before May raw was read).
- Clean source `prepare_events.py`, `grid_event_research.py`, `grid_event_economic_geometry.py`, `evaluate_locked_k4.py`, full five-month daily JSON, tests, signed-research-only scripts and compact results are in `GRID0107_FULL_SOURCE_TESTS_FIVE_MONTH_SHADOW_EVIDENCE.zip`; no raw source quotes included.
- No original Dukascopy source files or original MT5 R9 reports were edited. New original March SHA256: `814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177`; original May SHA256: `3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d`. Other raw source SHA recorded in accompanying JSON.

## Public reconstructible idea references

- [MQL5 adaptive grid risk/regime research](https://www.mql5.com/en/articles/21833) — explains constrained state-adaptive grids, but no lot-scaling mechanics imported.
- [Chen, Chen & Jang, Dynamic Grid Trading Strategy (2025)](https://arxiv.org/abs/2506.11921) — dynamic-resetting grid concepts on crypto minute data, not a XAUUSD certification.
- [Dukascopy quote-volume vs trade distinction](https://github.com/diridevelops/dukascopy-market-data-cli) — best quoted bid/ask size != executed trade volume.
- [MetaTrader limit-order caveats](https://www.metatrader5.com/en/terminal/help/trading/performing_deals), [queue/adverse selection](https://arxiv.org/abs/2409.12721).
