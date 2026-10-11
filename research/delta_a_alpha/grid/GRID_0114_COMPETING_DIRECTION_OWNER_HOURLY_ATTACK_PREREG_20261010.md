# GRID0114 — source-native competing sign owner / weak-hour attack PREREG
Date: October 10 2026, Chicago. Parent J0113; active branch delta-A-alpha. Frozen original GRID0108 event_scan, K2 >=2 and K4 >=4 movement tiers, 7s cooldown preserved. Original J0111 K2 first-response T1 at 0.40*G, then new actually later quote T2. Source evidence: J0108/0109/0111/0112/0113; full Jan-Jul original Bid/Ask source; no August, no session or higher timeframe trading, no orders, Martingale or EA changes.

**Owner scientific objective:** Month-robust quality FIRST, then daily qualified opportunity supply, then full UTC-hour robustness, aggressively diagnose the original J0109 weak cohort of 1,389 hours among 3,332 original baseline eligible weekday hours. Original 1,943 hourly unsigned wins and 150/150 day unsigned improvement NOT overwritten by new signed quote-outcome screens. No month/day/hour/date indicators may enter a decision; weak hours only retrospective evaluation cohorts.

**Original costs:** At actual new T2, hypothetical BUY opens at source Ask and closes on Bid; SELL vice versa. Use first actual source quote at or after 30,120,600s, <=10s late; deduct hypothetical $0.02 once and add +0.10 / +0.25 cost sensitivity. No real broker fills or qualified completed trades. Do not infer fills at midpoint. No future quote/bar or virtual subsequent outcome may affect T2.

**Predeclared competing mechanisms:**
1. REJECT05: after T1 initial direction, wait until a later quote crosses -0.50*G relative original T0 mid (signed in original T1 direction), before T0+45s. Elect *opposite* sign on that T2; rejection/reclaim hypothesized to expose adverse impulse exhaustion.
2. REJECT10: same with -1.0*G before T0+60s; test stronger rejection vs slower entry.
3. REJECT15: same with -1.5*G before T0+75s; stress noisy failed breaks; no tuning.
4. FALSE_BREAK: following actual initial +0.60*G peak in elected direction after T1, observe first passage back through T0 minus 0.15*G (<=T0+60s); new opposite-sign T2 at confirmed actual quote.
5. FALSE_BREAK_DEEP: same as (4), reclaim reaches -0.50*G, <=T0+75s.
6. ACCEPT_STRONG: if after T1 first actual quote at/after T1+5s remains >= +0.60*G and no earlier opposite breach of -0.15*G, elect original T1 direction at that later actual T2, within T0+45s.
7. ACCEPT_DEEP: at/after T1+10s remains >=+1.0*G with no earlier opposite -0.15*G breach, <=T0+60s.
8. REF_T1 unmodified baseline. Cross five candidates REJECT05, REJECT10, FALSE_BREAK, FALSE_BREAK_DEEP, ACCEPT_STRONG with frozen as-of original event prior-cell count >=2 in floor(mid/1.50) within 120sec (J0113), and also test prior-cell count==0 for FALSE_BREAK and ACCEPT_STRONG. No extra filtering by date/hour.
9. COMPETITION: at most one candidate per original T0: first T2 quote to qualify among REJECT05 and ACCEPT_STRONG (earlier wins), using its own sign; secondary comparison first T2 among FALSE_BREAK and ACCEPT_DEEP. These are as-of temporal races, not oracle selection.

**Mandatory reporting:** full month-by-month and 3,332-row hour denominator with 1,389 historical original weak hours, signed mean/positive/negative, quote validity, counts and % retained, individual unsupported hours, month/day/weak-hour paired economics, first-passage outcome diagnostics only, regret of abstention. Test code determinism, no lookahead, no future label as live input, duplicate decision-tick de-dup and quote side. All Jan-Jul extensively previously used; no pristine holdout. Preserve all failures and never promote on merely reducing loss or trade count. Stage 0 trading_enabled=false, no L1-L7 activated.
