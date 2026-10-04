# DELTA R037 — COMEX 15-Minute Opening Range Stage-A Screen — Checkpoint 17AC

**Status:** COMPLETE / NO STRONG SURVIVOR / RETIRE  
**Parent:** R037_LONDON_15M_OPENING_RANGE_STAGE_A_SCREEN_CHECKPOINT_17AB  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

The preregistered source used the first 15 minutes after the COMEX gold pit open (**08:20 New York / 13:20 UTC in January**) as the range, with breakout observation from **13:35–15:20 UTC**. Only strict-tick, completed-S5, and completed-S15 confirmation varied; the frozen 30-second execution lifecycle was unchanged.

Official compute used producer commit `c50b16fad12e5f21f43ed6734213590603e6da43`, blob `abc9db4bafa56e244b66237a0d24d6c73c380971`, producer SHA-256 `b86a37df596b75151b562f68bb94fbee5ddc21d8c3a186ce666e6eba1768d19f`, canonical January SHA `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, and completed in about **6.45 seconds**. Result SHA-256: `1ae3119cd1d81ab83b95064f2bd94b8d3feac22cfba97a19fda5294e91ee7f7d`.

Results:
- C01 strict tick: **11 trades / 7 wins / -$0.85**
- C02 completed S5 close: **10 / 4 / -$1.68**
- C03 completed S15 close: **11 / 6 / -$2.82**

C01 leads but remains below the preregistered nonnegative strong-pass gate. The COMEX 15-minute ORB family is therefore **retired without retuning**.

Next: `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`.
