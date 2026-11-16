# R9 V16 — Profit-first clean-continuation / recovery lifecycle audit

**Research only · 2026-11-15 · Original Coinexx XAUUSD Jan–Sep 2026 · No MT5 order changes**

## Objective and frozen source

The user requires **positive modeled complete-system net expectancy**, **a majority of trades profitable**, and **continued high trade volume**. A negative complete-system outcome is a **failed qualification**, even when a research comparison identifies a positive incremental improvement. We will not describe development tests as production success.

Inputs were the existing nine original SHA-256 pinned Coinexx monthly `*.csv.gz` quote files, the original V12 source-exact 338,065-entry / 338,064-completed-trade **derived ledgers**, and the V14 map of **128,203 positive historical trades**. No raw tick archive was rebuilt, recompressed or uploaded. The original V9 execution policy and MT5 EA remain unchanged.

Historical winner hypotheses are explicitly separated by the information clock:
- **Clean momentum**: no adverse 10-cent liquidation-side movement through the *already observed* original cash-harvest event.
- **Recovery**: adverse-first movement already observed by the current 250ms/1s clock, not selected retrospectively from eventual profitable outcomes.

All prospective actions execute at a later observed original source quote, never on a future OHLC extremum, and model BUY liquidation at Bid, SELL liquidation at Ask, plus the existing additional $0.20/trade cost assumption. Source ordinal is preserved when different quotes share a millisecond. Decisions require actual quote chronology, with a 2.5-second gap acting as a first-available safety exit/abstention rather than a fabricated fill.

## Tested profit-capture modifications

The unmodified, governor-disabled V9 research benchmark on all 338,064 completed trades is **−$135,317.63** modeled net, with **128,203 positive trades (37.923%)**. Its profit-cohort wins are real *simulator* gains but not evidence of overall profitability.

| Original V9 harvest modification | Trade opportunities retained | Estimated winning share | Modeled net, all nine months | Increment over V9 | Positive incremental months |
|---|---:|---:|---:|---:|---:|
| **5s clean-momentum capture** (target +$1.50, floor +$0.10, hard risk unchanged) | **332,218 / 338,064 (98.271%)** | **32.383%** | **−$131,492.37** | **+$3,825.26** | **9/9** |
| 3s clean-momentum capture (target +$1.00, floor +$0.05) | 335,403 (99.213%) | 30.692% | −$132,829.39 | +$2,488.24 | 9/9 |
| 1s clean-momentum capture (target +$0.60, floor +$0.02) | 338,064 (100%) | 32.391% | −$134,132.32 | +$1,185.31 | 7/9 |
| **Fast protected** (only already-observed harvest ≥+$0.20 within 3s, 1.5s follow-on target +$0.60, floor +$0.12) | **338,064 (100%)** | **37.043%** | −$134,808.43 | **+$509.20** | **8/9** |
| 3s recovery-harvest extension | 337,193 (99.742%) | 34.620% | −$134,505.92 | +$811.71 | 8/9 |

**Interpretation:** The positive incremental amounts are encouraging **cash-capture improvements versus the same historical baseline**, not positive total net returns or a majority-winning complete trading system. The 5-second variant sacrifices some cash-harvest winning events to pursue larger payoffs and therefore **reduces the percentage of profitable trades**. Under the owner's two-part objective, this candidate is NOT QUALIFIED. The fast protected variant better preserves entry throughput and profitable-trade frequency but also fails the required complete-system profitability gate.

**Overlap accounting limitation:** The 3–5-second extension model conservatively suppresses original later V9 entries whose times overlap the extended position. This is a *collision-aware matched original signal schedule*, **not an independently rearmed full V9 state machine**. The V9 entry engine's behavior, cash-governor conditions and cooldowns would have to be recomputed after changed exits to determine true new opportunity flow. The 98.271% retention is consequently preliminary, not deployment-certifiable throughput. The fixed-entry cash uplift for the 5s variant is only +$1,545.90; the remainder of the +$3,825.26 matched-calendar difference comes from not taking overlapping original trades. Do not mistakenly attribute this entire sum to better exit pricing.

## The recovery specialist is NOT a universal early stop

Among the 128,203 historical V9 winners, approximately 45,083 developed after an observed 10-cent adverse move; 31,116 had adverse-first quote movement. An automatic adverse-10c stop would sacrifice real historically positive events.

Three **prospective 250ms/1s adverse-first cut policies** preserved all 338,064 entry opportunities in the fixed-entry comparison but improved modeled total net by only +$26–45 over nine months. Three proposed smaller recovery cash targets were additionally tested in January, May and September only; they produced marginal cash improvements and did **not** increase profitable-trade count. These mechanisms are not approved as V9 exit overrides.

## Separate independent entry checks (bounded development months)

Completed-second breakout continuation, single-second sweep/reclaim, and their mirror/contrarian hypotheses were evaluated prospectively on January, May and September, with entries filled on a later source quote, one active position, per-minute rearm limit, spread cap and immutable stop. These mechanisms generate meaningful new candidate event flow but **none produced positive after-cost total net** in the selected months. Rather than search dozens of stop/target/Fibonacci/EMA variants on reused history, these hypotheses are closed for now and retained only in research code and local results. In particular, **high signal count by itself is not a profitable edge**.

## Current evidence-backed direction

The winner cohorts imply two *different execution lifecycles*: rapid, clean quote continuation and adverse-first reclaim/recovery. The V16 study validates that the former can improve **cash capture while retaining at least 98% of the matched-entry calendar**, but not that it can make the entire strategy profitable. The next entry breakthrough must add **incremental positive directional/price-location advantage** exceeding the typical observed spread plus explicit additional trade fees. Do not manufacture a high winning rate by labelling only favorable post-entry events as if they were known before entry.

**Narrow next implementation gate:** use the unchanged V9 entry router with a shadow state machine that measures online at 250ms and at the existing harvest event; distinguish clean-protected harvest vs recovery without looking ahead; rearm the V9 router *after every changed exit*, not just skip conflicted baseline signals. Freeze a single exit rule on early development chronology, then validate on later, genuinely untouched data. Maintain **≥95% of the 338,064 original trade-volume benchmark** along with **majority profitable trades** and **positive cash net after executable spread, fees and stressed slippage**. The latter two remain **unsatisfied**; no MT5 EA version or indicator default is promoted.

## Verification and retention

- Nine source compressed-file hashes rechecked against the original pinned V12 `V12_MONTHLY_SOURCE_PROOF.csv`.
- Original 338,064 completed V9 trades reconciled to V12 trade-entry/exit ordinals, timestamps, executable Bid/Ask and entry-side cash.
- Synthetic, no-download causal checks verify source-ordinal first crossings, next-quote execution, SELL Ask vs BUY Bid, quote-gap abstention and no intervention after the frozen original exit.
- The downloaded artifacts are **only small derived JSON and changed-trade comparisons**, executable audit scripts, and the aggregate. No original Coinexx tick stream is redistributed.
- **All nine months have been repeatedly used as development data.** No claim of untouched OOS, live brokerage fills, or working MT5 native parity.