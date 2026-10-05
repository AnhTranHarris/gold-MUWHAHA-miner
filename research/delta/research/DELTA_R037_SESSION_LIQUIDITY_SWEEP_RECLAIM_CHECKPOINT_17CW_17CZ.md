# DELTA R037 — Session Liquidity Sweep/Reclaim Harvest — Checkpoint 17CW–17CZ

**Status:** COMPLETE / NO STAGE-A SURVIVOR  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The frozen London-only Asia-range reclaim family failed for supply and economics, without tuning.

| Lane | Trades | Days | Wins | Net | Gate |
|---|---:|---:|---:|---:|---|
| 17CW strict M5 | 4 | 4 | 2 | -$0.48 | FAIL |
| 17CX strict M15 | 4 | 4 | 3 | -$0.64 | FAIL |
| 17CY 5%-depth M5 | 0 | 0 | 0 | $0.00 | FAIL |
| 17CZ 5%-depth M15 | 0 | 0 | 0 | $0.00 | FAIL |

The strict grammar was too sparse; the Gold 5%-depth version produced no events under the preregistered clock. No session/timeframe/depth rescue is permitted.

**Decision:** retire both exact grammars unchanged.  
**Next:** independent high-value entry-source harvest.
