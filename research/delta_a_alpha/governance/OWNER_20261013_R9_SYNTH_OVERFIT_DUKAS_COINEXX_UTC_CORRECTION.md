# Owner correction — R9 reference roles and original-tick UTC alignment (verbatim)

**Owner's exact instruction, 2026-10-13:**

> Please correct, fix. R9 syth as ideal performance metrics for (monthly, weekly, daily). R9 overfit is perferred trading performance per trade (entry, hold, exit, profit, drawdown, gross loss) dukascopy tick-level is the python backtest for reasearch/refinement. Align dukascopy with coinexx utc to ensure no timeframe issues.

**This is an original instruction and implementation amendment, NOT a summary replacing the owner's full frozen V1 whitepaper or entire ratified conversation.**

Original authority:
- [V1 OWNER-FROZEN FULL WHITEPAPER](../whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt) (immutable owner architecture authority)
- [Entire owner-governing conversation](https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit)
- [Current exact machine state](../../../CURRENT_STATE.json) and original accepted source/experimental files; summaries are never executable source truth.

## Required roles implemented in current Python engine

- **R9 SYNTH:** ideal whole-portfolio **daily / weekly / monthly** net cash, completed trade count, gross loss and balance/equity drawdown performance. Research targets; never real-tick executable profit claims. Original MT5 tester deal timestamps must be normalized to the chosen verified calendar convention before numeric side-by-side period comparisons; no daily target invented.
- **R9 OVERFIT:** preferred **per-trade** offline research teacher for entry, hold, exit, profit, drawdown and gross loss. Post-entry outcome labels may be used for retrospective diagnostics/model training but never as causal action features or execution permissions.
- **Original Dukascopy Jan–Jul ordered Bid/Ask tick-level:** authoritative **Python research/refinement backtest** engine input. Cannot mix future ticks, use R9 generated-tick Bid/Ask prices for actual Dukascopy executions, or silently substitute Coinexx prices/spreads.
- **Coinexx R9 REAL/SYNTH logs:** independent historical tester execution environment / benchmark diagnostic; distinct time and pricing source. Matching UTC is not matching quotes or proving broker fills.
- **UTC invariant:** both historical formats preserve raw UTC epoch milliseconds and original row ordinal. The entire original Coinexx April 15 REAL daily file (365,469 rows, SHA256 `b2e4cac86bd0ce5255699b39d4ee1b43649deb25fd3d6608b9a297fa95f43441`) was checked against `time`, `minute_start`, `minute_second`; all matched epoch UTC without offset. January Dukascopy source SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- **Derived bar clocks:** UTC research candle anchoring is explicitly default; H4/D1 MT5 broker-server **chart candle phase still needs direct independently observed CopyRates/chart bar-opening proof** before declaring complete MT5 parity. Optional evidence-scoped chart-clock injection is fail-closed, no guessed timezone, DST offset, price shift, or backdated signal.
- **Benchmark reporting:** the actual V1 Python result now carries reference roles and UTC day/ISO week/month realized closed-trade cash ledgers separately from original R9 SYNTH numerical reference. Closed-trade ledgers do not establish intraperiod floating drawdown.
- **Do not delete/restart research:** Earlier frozen owner whitepaper January/February frontier figures remain historical source evidence, not overwritten by GRID0267 $300 engineering test. J0183 official cursor and original GRID0258 control remain unchanged, August sealed, trading disabled.

## Source and verification

Current active files inside `research/delta_a_alpha/implementation/`:
`v1_grid_r9_benchmark_utc_0268.py`, `v1_vertical_grid.py`, `v1_grid_dual_feed_replay_0266.py`, `v1_four_session_architecture.py`, `test_v1_grid_r9_benchmark_utc_0268.py`.

**Verification:** 13 new tests passed including original 365,469-row Coinexx April day, 72 inherited tests passed; 120,000 exact January Dukascopy ticks were replayed with original versus corrected V1 and all preexisting economic/result fields were identical (elapsed clock runtime ignored). This is *not* the full monthly economic certification.

[Complete runnable exact GitHub-file SHA-aligned ZIP, inputs represented by verified original hashes](https://drive.google.com/file/d/1DmiCfr1KI6lW0djGr2GQDyPKN0c0wGs-/view) (29,106 bytes; SHA-256 `3e39b7664d2e8448c8bc3d68a3ed2f553d2e774a784371fd4b5e56d48e3ef42c`).
[Full GRID0268 original-source technical QA report](https://drive.google.com/file/d/1hpxw0zGOuc5pQMyjmh670A_DPQpNDsET/view).

**Nonclaims:** no original R9 overfit optimum profits reconstructed as executable real fills; no current Coinexx EA MQL5/bar-clock MT5 certification; no strategy performance breakthrough, no new branch, no changes to original whitepaper or J0183.
