# V2 F1 — MT5 EA BUILD CAPSULE & SOURCE-TO-BROKER PARITY CONTRACT (BLOCKED)

**Research date:** 2026-10-15 | **Repo:** `AnhTranHarris/gold-MUWHAHA-miner` | **EXISTING working branch ONLY:** `v2-f1-january-research` | **State:** `BLOCKED_FOR_MT5_TRANSLATION`; retained infrastructure only, no investor-qualified strategy. **No new branch, no reset, no MQL5 build, no deployment.**

This technical capsule is a *preliminary fixed-source interface contract* for later exact translation. It does not fill unknown broker data or claim that the eight research specialists are accepted. MUST be developed further with exact source-method capsules before any code is ported to MQL5. It is subordinate to full user whitepaper, January QC law, master protocol Section 100 and original actual code.

## Canonical identity/unchanged source chain

- Parent frozen `delta-A-alpha` original V1 full source at [GitHub](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/delta-A-alpha/research/delta_a_alpha/implementation). `CURRENT_STATE.json` `J0183`, trading OFF.
- Existing V2 [source](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/v2-f1-january-research/research/delta_a_alpha/implementation/v2_f1), 7 original source files exact Git blobs pinned in read-only verification helper. Current pipeline is self-contained experimental research, not original `FourSessionV1` exact built strategy.
- Immutable January actual quote input: SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, 9,135,062 UTC ordered `(timestamp_ms_utc,bid_raw,ask_raw)` rows; raw scale 1000 XAUUSD research-dollar. Copy of binary is private Drive source; no open August.
- Exact older V2 chassis and Python original sources archived in Drive `18_dpekq8GS7sySUZiXjhSdXyoiWbkq1h` and new canonical F1 ZIP in Drive `1oDoDjPefjreY_cH60vDkIJ5FVeYxHmep`; SHA pinned in full companion handoff.
- Original R9 Coinexx $100 generated *Every tick* teacher: M1, M5, H1 and M1 logger report same 27,980 January close cycles / +$41,520.82 cash / -$1,827.87 gross losers. This is a behavioral research comparator, NOT Dukascopy actual broker fill performance. The uploaded M1 logger XLSX supports trade-level Deal inspection but the uploaded `SingleTestCache` binary is NOT itself decoded raw logger CSV. NEVER hallucinate or build a live oracle signal from it.

## Research state machine: exact existing code ownership, not imagined MQL5 semantics

| State/stage | Current V2 original source implementation | Exact future MT5 responsibility | Unverified requirement |
|---|---|---|---|
| L0 raw quote root | `v2_f1_integrated.py:load_source`, `v2_streaming_chassis.py:StreamingF1.on_quote` | timestamp-ordered Bid/Ask quote stream and catch-up | MT5 `CopyTicks` idempotent catch-up, OnTick coalescence, symbol tick size, broker quote duplicates |
| S1 fast micro features | `micro_features` (previous completed observed seconds), `StreamingF1._micro_quality` | ring of *closed observed seconds*, paths/efficiency/range/turns | exact time/clock rollover and floating-point operation equivalence |
| MTF state | `prev_frames` for M1/M5/M15/H1/H4, plus research 1s/5s/15s/30s clocks | reconstruct last COMPLETE HTF candles, not final current M1 close | gap/weekend/bar-close event order, DST and stale-candle TTL |
| L1 sessions | `load_source` via `tz_convert` and `_session_policy` | Sydney/Tokyo/London/NewYork concurrent ownership flags | IANA DST ↔ server GMT offset mapping, broker holiday and market-open schedule |
| L2/L3 virtual grids | `generate_sources` eight experimental virtual families; R9 minute bracket in `execute` | original V1 full router + R9 source-reconstruction proposed entries; immutable ancestry | V1 `GridStrategySourceRouter`, native 136A/136B/H4/J179F source geometry parity NOT yet achieved |
| L4/L5 quality | `_permit`, S1 `qua`, `m5dir/h1dir/h4dir/m15dir`, source mask/session policy | causal completed HTF ownership and tick quality | original V1 full L1–L5 admission/reason fingerprints still missing |
| L6 lifecycle | `execute` float stop/target/trail/favor/timeout; no actual broker | protective SL/TP/trailing, bounded loss responses and closure | real broker min stop/freeze/slippage/order partial fills, fees |
| L7 funded governor | `execute` singleton slot, simulated 250ms pending latency, assumed $100 account/0.01 nominal | single broker funded account reconciliation, open/pending reservations, margin, commissions and max DD | real Coinexx contract_oz, margin, dynamic commission, MT5 transaction receipts, account currency |
| Paid-close renewal | V1 `PaidCloseWatchdog`, `V1BrokerEvidencePort`; not yet exact-source ported into new F1 | full observed order/check/send/DEAL_ADD/balance close proof; only then paid parent/child | actual MQL5 OnTradeTransaction idempotent link and execution event ordering, not yet implemented |
| Accounting | `output_ledgers`, `v2_source_and_r9_audit.py` | per-trade and every H1/UTC day/ISO week including zero; separate tester server day | Coinexx server time offset (+2 inferred, NOT verified), reconciliation of deals, costs, floating DD |

## Current actual transition semantics (from original V2 F1 code, not guarantee of successful execution)

1. Raw quote `(millisecond UTC, bid_raw, ask_raw)` is read in chronological order; invalid crossed quotes and source SHA mismatch abort.
2. Completed 1-second observed-second summaries are generated without invented idle ticks; MTF bars use last completed observed frame. New M1 minute origin is frozen at first actually received bid/ask midpoint of that minute.
3. EIGHT generic experimental `generate_sources` produce virtual signals; `execute` also has a separate native-inspired source-ID 1 bracket test with last **completed** S1 direction and threshold `.15` price dollars on the minute-frozen midpoint. Only previously observed signals can enter; no future R9 teacher markout influences the signal.
4. Admission: actual current quote, spread must meet configurable price-USD cap (research sweep used 1.20), intraminute phase, local session policy, regime policy, pending queue and non-overlap. Existing native control uses stop $0.30, arm $0.10, trailing gap $0.03 and max-hold 30s; these are RESEARCH settings and a simplified R9 proxy, not proof of broker order-stop handling.
5. Simulated order proposal consumes source ID and timestamp, first possible quote fill is at least +250ms, request expires after 4 seconds, fill uses Ask on Buy / Bid on Sell, verified spread/drift/margin cash checks. Fixed experiment `0.01 lot` assumed 1 oz, leverage assumed 1:500 and cash fee assumed $.20; original broker contract unknown.
6. With position active, on each observed quote compute mark to opposing Bid/Ask and irreversible equity halt below 60% of initial account. Evaluate existing hard/trailing stop before target then max-hold. Record realized cash once, enter rearm state only after actual simulated close; one position max. When irrevocable halt and no open/pending, early-break main loop but remaining 744h and 31d scorecards explicitly zero-fill.
7. The **source V2 use of simulated cash never implies observed broker `DEAL_ADD`**. Valid paid-close ancestry must never be faked from local PnL. The exact native original V1 parent-child state contract must be read and ported with tests.
8. Each source event must have independent unique ID, side, source origin, rung/price, as-of time, parent paid authorization, session/HTF ownership, rejected/won arbitration and exit/fee/margin ancestry. The present V2 output stores `source_id` but NOT yet complete original V1 native source ID genealogy. Buildability is blocked until restored.

## Missing original V1 source integration — explicit next phase

- **V2-F1-INTEGRATION-001** native complete creator/strategy router parity: V1 `GridStrategySourceRouter` and `CumulativeCreatorAdapter`, 136A/136B native grids, genuine H4 retest/second acceptance, earlier J179F earned permission, original completed-M1 progress and score. Preserve all original source events, not just 8 analogous synthetic families. Exact V1 method signatures and imported helper contracts in original file versions, read rather than assume.
- **V2-F1-INTEGRATION-002** paid-settlement & capital flow parity: V1 `V1BrokerEvidencePort` order check/send, entry DEAL_ADD, closing DEAL_ADD, partial/complete position settlement; `PaidCloseWatchdog` unverified vs verified PnL states; no broker credit from Python simulated closes; shared position governor.
- **V2-F1-INTEGRATION-003** full original quote real money assumptions / independent Jan QA: original R9 per-hour/day/ISO-week benchmark, loss/drawdown, all zero time buckets, pay/no-pay and source genealogy, $100/$200 scenario, no offline overfit leakage.
- **V2-F1-INTEGRATION-004** authorized later MT5 transaction execution parity only after successful original source/QC and explicit owner approval. This stage is NOT authorized now.

## Exact minimum golden regression fingerprint file schema (to IMPLEMENT, not already produced)

Store daily/timeframe outputs in an append-only `V2_F1_GOLDEN_PARITY_*` file with these identities:

```
source_git_commit, original_file_git_blob, source_sha256, original_tick_time_ms,
original_bid_raw, original_ask_raw, observed_second_end_ms,
completed_m1_end_ms, completed_m5_end_ms, completed_m15_end_ms,
completed_h1_end_ms, completed_h4_end_ms, completed_s1_micro_quality,
session_bitmask, broker_tradable_flag, virtual_creator_source_id,
original_level_price, original_rung, original_parent_paid_id,
g0_event_timestamp, l1_owner, l2_geometry, l3_candidate_id,
l4_quality_reason, l5_trend_reason, l6_manage_action,
l7_capacity_decision, earliest_fill_ms, requested_side,
actual_fill_quote_timestamp, filled_entry_bid_ask, broker_order_ticket_id,
broker_deal_ticket_id, simulated_cash_booked, verified_broker_cash,
stop_before_target_order, trailing_state_before_after,
max_favorable_since_entry, max_adverse_since_entry,
closed_trade_id, actual_close_bid_ask, close_reason, fee,
ending_cash, mark_to_market_equity, worst_intratrade_drawdown,
funded_positions_total, pending_positions_total, rejected_reason
```

At each test boundary, SHA256 the trace and original source, and compare exact deterministic outputs with original V1 source parity, V2 batch/streaming, and (later, separately) MQL5 tester raw transaction events. Never present overlapping hypothetical sub-strategy markouts as funded combined-account PnL. Golden fingerprints must include accepted and rejected candidates, not winning deals alone.

## Blocking issues and acceptance tests

**BLOCKED_01:** No verified Coinexx broker `SYMBOL_TRADE_CONTRACT_SIZE`, `SYMBOL_POINT`, `SYMBOL_TRADE_TICK_SIZE`, tick-value, leverage margin tier, `SYMBOL_TRADE_STOPS_LEVEL`, `SYMBOL_TRADE_FREEZE_LEVEL`, spreads, commissions / swap, account mode and server timezone for identical historical test. All 1 oz, 1:500 and $.20 are explicit simplifying scenario assumptions. 

**BLOCKED_02:** Original native grid G0 source/router and original paid-after-close source renewal not integrated/QA-proven in V2. No source-on-source full January event parity. 

**BLOCKED_03:** MQL5 asynchronous transaction evidence absent. `OnTick` NewTick events may be coalesced; `OnTradeTransaction` events may be delivered in arbitrary order across stages, and heavy handlers can risk queue overflow. Need idempotent transaction journal, observed request/order/deal chronology, fixed ticket IDs, timeout/compensation and catch-up from tick history. Official documentation: https://www.mql5.com/en/docs/event_handlers/ontick , https://www.mql5.com/en/docs/event_handlers/ontradetransaction , https://www.mql5.com/en/docs/series/copyticks . 

**BLOCKED_04:** January V2 income objective not met: full 1,921 `$100` trials 0 at owner's R9 period-matched net+velocity target; native control halted. Source/feature QA and the 12 high-capacity probes are not trading profit. 

**BLOCKED_05:** No owner acceptance, no completed true full V1 `L0–L7` funded parity across first month. No MQL5 consent.

**Potential broker semantic change:** optional session/DST changes, tick-coalescence catch-up, stop distance normalization, slippage guards, lot/hedge mode, cash headroom or position capacity modifications can materially alter source/economic semantics. Each needs a NEW source-linked research identity and counterfactual full funded replay; safeguards are not assumed neutral by construction.

## Status / source precedence

**BUILDABILITY STATE = `BLOCKED`**. Test suite currently: source SHA and 55-member archive integrity, original stream/candle parity 0 discrepancy on 180k quotes, 5 V2 tests, 27 native control trade quote matches, original 1,921-case trial CSV exact replay. There is no broker equivalence, no production MQL5 EA build, and no accepted economic edge. Full detailed continuation: `V2_F1_CONTINUE_ONLY_SOURCE_LOCKED_NON_SUMMARY_HANDOFF_20261015.md` on same existing branch, with complete original Drive checkpoint and a separate source-preserving handoff evidence archive.
