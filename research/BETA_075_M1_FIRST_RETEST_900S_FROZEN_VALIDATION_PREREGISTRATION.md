# BETA075 — Frozen M1 First-Retest 900s Validation

**Status:** PREREGISTERED / DIAGNOSTIC NOT YET OPENED  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

BETA074 CAL discovery identified one minimum-count positive candidate:

- mechanism: FIRST_RETEST
- structural timeframe: M1
- fixed hold: 900 seconds
- CAL one-position trades: 51
- CAL wins: 26
- CAL net: +$26.266
- CAL PF: 1.37224
- CAL average: +$0.5150/trade
- CAL max drawdown: $25.50

This did not satisfy BETA074's neighboring-cell robustness rule, so BETA074 remains unpromoted. BETA075 is a separate validation unit: it freezes this exact single candidate and opens the previously unread DIAGNOSTIC span. There is no threshold, horizon, timeframe, session, or mechanism selection after diagnostic results are seen.

Pass criteria for human-facing QA candidacy:
1. >=50 diagnostic one-position trades;
2. diagnostic net > 0;
3. PF > 1;
4. positive average trade;
5. deterministic replay and quote-side accounting QA pass.

If it passes, BETA075 becomes a research candidate for **human-facing QA**, not automatic MQL5 approval. August remains sealed.