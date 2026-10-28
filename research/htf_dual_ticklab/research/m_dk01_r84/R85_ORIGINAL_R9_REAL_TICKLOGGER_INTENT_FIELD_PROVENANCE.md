# F401-R85 original R9 native real tick log: source intent-state discovery (not a trained model)
Date: 2026-10-28. RESEARCH ONLY; 21/39 historical research approved, M-DK-01 OPEN; all whole EA G01-G09 OPEN.
Original PRIMARY REAL_TESTER source https://drive.google.com/file/d/1YZi9XlR8OdPSPkWMLqV4Ek5Ls3O3LU1A/view `GoldMuwahaha_R9_TickLog_REAL_TESTER_20260101_000000_part01_of_10.csv.gz`, 94,307,288B, SHA256 ae07db47b48b49695c6de47927171d7cf8c7bc28a85370d87d48957e2a20506e. This is original R9 REAL source part01 of ten, not the MT5 33MB SingleTestCache binary, and not automatically identical to R00-054 source event population.

Exact 30 fields:
`run_label,time_msc,time,bid,ask,last,tick_volume,volume_real,flags,spread,minute_start,minute_second,cycle_buy,cycle_sell,pending_mode,rearm_number,s1_disp,s1_eff,s1_range,s1_turns,atr,session,gate_open,position_open,position_side,entry_price,mfe,mae,current_sl,trail_armed,event`.

First 650,000 source CSV rows **actually parsed**, timestamp 1767315600480→1767638171616:
QUALITY_REJECT_BUY 262479, QUALITY_REJECT_SELL 241007, ENTRY_BUY_FAIL 32942, ENTRY_SELL_FAIL 28776, MINUTE_START 2429, REARM 410, ENTRY_BUY 209, ENTRY_SELL 207, TRAIL_MOVE 428, EXIT_MAX_HOLD 11, NONE 81102. All 650k sampled `tick_volume=0` and `volume_real=0` -> no authentic traded volume or L2; never infer orderbook queue.

**Distinct information from failed R83/R84**: exact original R9 strategy generator columns `cycle_buy/sell`, `pending_mode`, `rearm_number`, `s1_disp`, `s1_eff`, `s1_range`, `s1_turns`, `atr`, `session`, `gate_open` are genuinely recorded. No guarantee same event value is pre-order: `event` is action like quality rejection, entry or fail, and `position_open, entry_price, mfe, mae` can be post-action; prohibit same-event hindsight leakage until original MQL5 evaluation and snapshot assignment ordering verified. Require exact R00 event-ID/side/UTC join and quote ordinal/broker-month match before feature research. Also note only one Jan log part audited, cannot infer full eight-cell R9 original intent coverage. One plausible new architecture: R9 original pre-action setup-state + completed HTF regime + quote transport + right protective guardian trained on FIT and frozen in predeclared CAL; evaluate separate M-DK-01 and whole EA G gates. NO new R85 trained filter, no authority to disable any demo orders.

Scientific R84 full MT5_EXPAND /01 https://docs.google.com/document/d/1Pc1NJriHCMCX78nMoPYpYcXuZnyVPLKgxN3rpSIjC4k/edit
Updated R85 /00 source-exact handoff https://docs.google.com/document/d/1cnChkkzHnfs_tUPUET-hrfb98DdUVPyIPj5KhTX3gs8/edit
Original engine ca4b58aec597174b6f6d18ab2f36cba6836e4f4c remains untouched.
