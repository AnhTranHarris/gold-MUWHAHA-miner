# GRID0224 — Standalone Grid Native Vertical Coding + Local CPU AI Research (NOT PROMOTED)

**Completed research: 2026-10-12 | active delta-A-alpha | frozen owner V1 NOT MODIFIED | trading OFF | August SEALED | J0183 remains authoritative.**

## Original SOURCE and complete code/replay archive

[**GRID0224 full runnable GRID-ONLY standalone research ZIP, 65 entries, source, 11 unit tests, local LightGBM model, native Bid/Ask ledgers, 5-month scorecards, original source SHA manifests**](https://drive.google.com/file/d/1-goCFpYbBDw4mPx30aGr-PY357iWPBi7/view). Archived file bytes 836602, SHA256 `2a7beb42116d828737d8d9321e850e0d5b3be203087d7670ff0f26ea6fd5f8a3`, all zipped members verified.

**READ ORIGINAL GOVERNING MATERIAL IN FULL** before any continuation: [frozen complete V1 whitepaper](../whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt), [complete owner ratified governing conversation](https://docs.google.com/document/d/17gS0nyzwGIsvx0wI_rhx7gSpIOQpvNzywHgMdoVopRk/edit), [original owner PRE-L1 lock](../governance/OWNER_PRESESSION_GRID_GENESIS_RESEARCH_UNLOCK_L1_ONLY_AFTER_QUANT_ACCEPTANCE_20261010.md), and [OmegaFX creator Python source](https://github.com/MegaJoctan/omegafx-youtube-shared-files/tree/main/Python%20Grid%20Bot). This research pointer is NOT a compressed replacement for original law.

## What engineering ACTUALLY happened (full Python in Drive ZIP)
- New CLEAN GRID-ONLY research stages: `G0` original Bid/Ask → `G1` UTC and four IANA regional time **observations only**, not optimization / desk strategies → `G2` reconstructed OmegaFX 48-completed-H1 + completed M5 virtual grid rung event tape → `G3` strictly past-only native quote/rung/flow features → `G4` tiny LOCAL LightGBM regression models for long and short expected terminal bid/ask cash equivalent → `G5` quote freshness admission, model and contract approval fail-closed → `G6` SINGLE position no averaging or lot escalation, delayed observed quote fill, 4-price unit stops, 6.5 target, 600sec max, full native quote-side floating equity → `G7` actual source closure NY17 DAY / ISO WEEK / source MONTH evidence.
- **11/11 offline native vertical invariant tests** passed. Strong as-of future-leakage tests alter future quote prices/exit availability and assert entry-known features + entry eligibility unchanged. Initial research prototype improperly gated admission on availability of future exits; this is INVALIDATED. Corrected `entry_valid` and future-label-only `label_valid` used to rerun all tests.
- Training data: **76,393** Jan+Feb ORIGINAL raw Dukascopy tick event label observations (NOT owner-invalidated Jan/Feb DERIVED trading model imports). Frozen threshold calibrated March (all forecast-slice means **negative**). April–July same unchanged fit/threshold for out-of-training diagnostics, but months have been inspected by previous project research so NOT pristine unseen holdout.
- 1oz USD-price cash proxy only; hypothetical +$0.05 slippage per side and +$0.02 roundtrip, original quote spread included, 250ms delay/<=2s max price. **No verified Coinexx contract/tickvalue/margin/spread parity**, and monthly simulations independently initialize $100k before reporting monthly economics; cannot assert a genuinely continuously broker-funded account or accurate original MT5 tester report clock bridge.
- Source-event ancestry is previous GRID0223 RECONSTRUCTED GRID0221 helper, **not byte-identical** original committed grid module. The GRID0221 prior 6%-ish count mismatch is NOT fixed by this ML experiment. Reconstruct exact source before using counts for success gate. Raw original January-July hash pointers and prerequisites in the ZIP; no raw source modified/duplicated; August unopened.

## Results: full April–July quote-side, genuinely one-position-tick-priced source sandbox — ALL NEGATIVE

| Policy | closed source tickets | quoted source net (USD/oz equiv) | PF | NY17 positive/active days |
|---|---:|---:|---:|---:|
| grid-only March-frozen local LightGBM expected after-cost choice | 2,718 | -2,278.559 | 0.6964 | 14/80 |
| stricter Local model threshold | 798 | -884.488 | 0.6302 | 18/72 |
| original direction blind creator fade baseline | 15,447 | -11,848.813 | 0.6598 | 1/82 |

Thus local intelligent selection reduces loss AMOUNT by refusing most tickets, **does NOT achieve positive expectation, trade-frequency goals or 80% original R9 SYNTH daily/weekly/monthly full metrics**. Positive-hour recovery 75% NOT demonstrated. No model promoted; G5 denies unvalidated source even when predicted positive. Never mistake fewer losing trades for a profitable GRID or describe as R9 dollars.

Original R9 SYNTH closed 2026 monthly targets: Apr 31758; May 28913; Jun 31801; Jul 24382. March-frozen local model counts Apr 788 / May 696 / Jun 859 / Jul 375, **~1.5–2.7% of R9 monthly completed count** (not 75% qualified DAILY trade coverage). MT5 report server-clock not independently bridged to native original source timestamp.

## Other people's reproducible mechanisms surveyed — no blind copier model
- [StockSharp Advanced Adaptive Grid code/README](https://github.com/StockSharp/AlgoTrading/blob/main/API/0401-0500/0498_Advanced_Adaptive_Grid/README.md), ATR-relative spacing, grid trend/range conditional paths, bounded risk, but depends on StockSharp `clr`/.NET environment and requires checking original LICENSE/NOTICE; conceptually inspired only.
- [MQL5 reconstructed finite restartable grid research](https://www.mql5.com/en/articles/21833), useful limited campaigns/regime gating, not evidence of live profit and no escalating losing lots.
- [Chinese MQL5 quantitative grid and Martingale mathematical risks](https://www.mql5.com/zh/articles/8390), reject no-stop close-win-rate distortion.
- [Japanese MQL5 ATR volatility design](https://www.mql5.com/ja/articles/10748), causal volatility-based gap hypothesis, not proof.
- [Passivbot exposure and hard drawdown risk documentation](https://github.com/enarjord/passivbot/blob/master/docs/risk_management.md), reduce stuck inventory; crypto-perpetual leverage/margin specific, do not reuse averaging/lot-scaling mechanics.
- [Official local CPU LightGBM](https://github.com/lightgbm-org/LightGBM/blob/main/python-package/README.rst). Reconstructed LOCAL prediction experiment instead of treating pretrained universal financial models as credible alpha; `.joblib` is unsafe to deserialize from untrusted parties.

## Required follow-up (not yet completed)
1. Restore exact active GitHub grid genesis byte equivalence vs original helper and rerun strict per-event source DAG parity.
2. Genuine broker Coinexx 0.01 contract/margin/commission and MT5 REAL tick/report clock parity, no synthetic quote-side source ≡ broker US$ assertions.
3. Research a NEW independent entry-known predictive signal, not another broader threshold/time-horizon tuning of already invalidated regressions, perhaps original quote quantity conditional replenishment vs spread compression, price acceptance, rate-conditioned competing risks.
4. Train against *constrained* multi-horizon cash, max equity DD, gross loss, PF, wins/losses and daily actual physically feasible trade count, rather than in-sample future quote markout accuracy alone; maintain ONE source-time global position ledger.
5. Owner previous PRE-L1 law keeps SESSION BASED optimization and V1 quality layers LOCKED until independent grid profitability / explicit owner review. Clock readings may be added as diagnostics, not market-entry magic.

The complete **research only** source exists in verified Drive archive above; active `implementation/v1_creator_grid_genesis.py`, L1–L7 `v1_four_session_architecture.py`, original owner law, and current state not changed. **No live EA orders.**
