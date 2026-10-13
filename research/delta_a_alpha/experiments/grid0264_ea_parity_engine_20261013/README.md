# GRID0264 — Concrete Python Engine Repairs / EA-Parity Candidate

**Status:** Validated independent research execution engine and separate broker-event specification, **NOT** approved for translation of the complete active V1 into MT5. No trade activation or strategy profitability claim.

**Source code is committed in this directory on the pre-existing `delta-A-alpha` branch**, alongside its actual unit tests. The complete fully self-contained *dependency and evidence package* is [GRID0264 executable ZIP in the established Drive handoff folder](https://drive.google.com/file/d/1vWRtFiXyA-g0wi1Iw_q7VljBKqZ1CxI7/view) (171,055 bytes; SHA256 `17e161fd821806f1a1fb1805d849aa08afd15ec85dd739f8d268292241793c8a`).

Read the [full 2026-10-13 remediation and MT5 conversion contract](./GRID0264_ENGINE_REMEDIATION_AND_MT5_TRANSLATION_CONTRACT_20261013.md) **before** merging anything active.

## What actually changed and was tested

1. `v1_grid_cumulative_source_adapter_0264.py`: chronological G0 cumulative router adapter; real completed H4/M1 history feed, no filled-parent auto-credit, no unsigned/retroactive signals.
2. `v1_grid_python_source_to_shadow_port_0264.py`: one causal source→lifecycle→full shared shadow funding path; explicit per-source research quality/exit policy; no broker-fill inventions.
3. `v1_grid_ea_parity_shadow_risk_0264.py`: modeled outstanding roundtrip exit fee reserved in marked equity and funding availability.
4. `v1_grid_mt5_position_ledger_0264.py`: distinct order tickets and `DEAL_POSITION_ID`, independently observed entry/exit deals, partial fills, duplicate and out-of-order staging, full broker-history/account-cash reconciliation.
5. `v1_grid_paid_source_position_bridge_0264.py`: strict proposal/order/position/side/time lineage and .01-lot broker-confirmed paid anchors only; no fabricated funded parent.
6. `v1_grid_mt5_stop_ack_0264.py`: stop modification requires externally verified bid/ask, symbol tick/stops/freeze constraints, broker acceptance and actual position SL readback.
7. `grid0264_integrated_replay.py`: real Jan–Jul Dukascopy original tick / frozen first-observed-one-second deterministic engineering replay, no August source, explicit simulation-only broker assumptions.

Tests in this directory, plus retained inherited GRID0246–GRID0263 code under `recovered/` in ZIP. Do **not** assume standalone clone of only this source subdirectory contains those frozen previous-version dependencies.

### Independent verification already executed

- Inherited tests: **231 run, one skipped**.
- Newly introduced GRID0264 regressions: **63 passed**.
- Original unresampled Jan–Jul raw tick smoke: **175,000** rows (7 × 25,000).
- Original first-second Jan–Jul observation samples: **1,435,000** (7 × 205,000), **37,943 G0 candidates**, **1,589 hypothetical shadow closes**; ledger cash reconciled; **ZERO** fabricated broker-paid anchors.
- January and July complete sampled replay results repeated with exact same SHA-256 settlement digest.
- Results are in the ZIP's `results/`, verified with `GRID0264_SHA256_SOURCE_AND_TEST_MANIFEST.json`. No 60%-of-R9 economic breakthrough has been certified.

### Still blocks truthful EA coding of complete live V1

- The tested router inside inherited ZIP is actual recovered **GRID0257**. GitHub latest active `research/delta_a_alpha/implementation/v1_grid_strategy_source_router.py` SHA `14e4c449b64c745c745e62c99d71be9fb0694257` additionally contains GRID0258 micro-research renewal; this newest exact router has **not yet** been end-to-end verified under GRID0264's current bridge.
- Current `research/delta_a_alpha/implementation/v1_four_session_architecture.py` SHA `ab2a623f2ee8c1aec37fee4894abd5e0f9d3302c` still uses `CooperativeGridGenesis`, not the new adapter; completed full L0–L7 current V1 permissions are not silently replaced or assumed equivalent.
- Actual Coinexx hedging account, XAUUSD broker contract, server trading calendar, order rejections, stops/freeze, commissions, real `OnTradeTransaction` and broker account cash have not been furnished.
- GRID0258 original quote-only accepted mechanism and official scientific J0183 are preserved, August remains SEALED, and `engine.trading_enabled=false`.

**Do not create a new branch, alter GRID0258 source, promote speculative shadow cash, turn on trading, or begin MQL5 conversion from incomplete broker facts.**

## Official platform semantics used

- [MQL5 OnTradeTransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction): asynchronous order/deal/position chain, potentially unordered callbacks.
- [MQL5 Deal Properties](https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties): `DEAL_ORDER`, `DEAL_POSITION_ID`, `DEAL_ENTRY`, `DEAL_TIME_MSC`, profit/commission/swap/fee.
- [MQL5 Symbols](https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants): actual supported filling types and broker-enforced stops/freeze levels.
