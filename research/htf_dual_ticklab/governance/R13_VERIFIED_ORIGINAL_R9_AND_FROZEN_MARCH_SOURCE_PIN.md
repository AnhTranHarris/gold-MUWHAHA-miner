# R13 — Validated R9 benchmark, frozen March original-tick evaluation, and whole-account continuation
**Date 2026-10-17 · RESEARCH ONLY · no MT5 live execution · no investor-qualified EA**

## Full immutable original-source archive
https://drive.google.com/file/d/1Gbj9Gl7BDSiK_RJEB4ZfyabKLw0kOGT4/view
**48,097,462 bytes · SHA-256 `4207734eb65b46d6cfb6a4f612c723a5572700a6b8ef1237d8579836e536239b` · 75 ZIP members · full member CRC PASS.**
MT5_EXPAND `04_EXPERIMENT_RESULTS_AND_VALIDATION`. Google Drive download readback size and local SHA matched.

R9 SYNTH original 123681909 byte MT5 workbook SHA `f9315c35bde962135785a0fb8fd268251086e9bebe27f5789757c69cfb38819d`:
https://docs.google.com/spreadsheets/d/1jASxs5gn3e1rzwGxlE-178aN07_5ksHE/edit.
Extracted **all 544704 deals**, precisely paired to **272352 closed synthetic tester trades**, reconciled **+$360693.05** all-in across 9 monthly, 40 ISO-week, 192 daily and 4361 entry-hour rows. R9 positives 192/192 days, 40/40 weeks, 4350/4361 entry-hour blocks; 187/192 active days in 710–2127 volume band. **R9 server clock NOT proven UTC**. Source R9 original and R9 report are synthetic and MUST NOT be claimed retail-executable profit.

## Source pinned March (pre-frozen before March downloads)
The preregistration source milestone is commit `9ebda7602f5c43ec2c2b013398a318d1f040c380` in this branch, proving choice of March 3–6 window and candidate before reading March original tapes. Source SHA of Coinexx Mar gzip `3e9a03d97c6403036c4f5731e2e9eff43b8c4c9b25ac61adc6cc2147e3e79112` (Coinexx UTC offset −120 minutes Mar3–6); Dukascopy Mar gzip `814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177` (native UTC). Historical March source had been exposed in earlier project research; this is **within-R13 frozen chronology**, NOT an untouched prospective blind holdout.

March 3–6 window original records: Coinexx 1,559,344 bid/ask updates; Dukascopy 1,681,212, sources not merged. Three predeclared complete-system policies × 2 brokers × 2 balances ($100/$200) × 3 latencies (0/250/1000ms) = **36 independent funded account scenarios**. All account trade ledgers reconcile to reported after-cost realized net and period scorecard.

Original R12 delayed-profit runner versus same-entry fixed exit:
**12/12 March matched pairs increased P&L and lowered marked-equity drawdown**; net change **+$9.28 to +$14.233** each paired account and marked DD saved **$10.06 to $13.167**. Earlier R12 samples Jan/Feb 24/24 same paired direction: 36/36 across three four-day samples, NOT independent markets or a guaranteed profitable strategy. All 36 March configurations still showed negative realized net, zero modeled stopout, and min marked account equity ~$30.385, so investor survival and profit NOT achieved. High throughput also not achieved. Preserve the runner but seek new high-frequency entry economics rather than another static stop change.

Frozen worst-account-policy `aggression=2, specialist=6 price_acceptance, exit_lifecycle=2` from Jan/Feb grid SHA `4ea1514603cd46728065cdd8bb6331a378ddad64eba78430c788bf10f1e055d0`; it traded less in March. Lower trade count is NOT an investment success.

## New executable research interfaces and future procedure
`htf_ticklab/whole_system_kpi_r13.py` and `tests/test_whole_system_kpi_r13.py` grade full executed UTC month/week/day/hour outcomes, 12-slot broker×equity×latency, unrealized risk and prevent R9 server-clock laundering. These are contract/regression tools, NOT independent trading P&L parity. Production baseline untouched. Standalone original-tick Numba R12/R13 replay and integrated GitHub CLI require numerical parity tests.

**Next solution-specific experiment (R14, still unexecuted):** dynamic entry-price acquisition (marketable vs quote-trade-through limit vs structural Fibonacci pullback + reacceleration), quote-flow/ATR/RSI/QWAP and Donchian/sweep event archetypes, coupled to the R12 runner and an optional rapid profit harvester; govern min-lot-funded capital and cost hurdle, audit entire Jan–Jul portfolios per UTC period and trade count, plus retrospective R9 server-date comparator. Test S vs S′ on same original broker tapes with 12 funded scenarios and account equity paths. No assumption of guaranteed spreads/fills, no R9 timestamp anomaly exploitation, and no claim of a profitable total EA until actual proof.
