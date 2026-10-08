# Delta-A-Alpha / Unit 027 — Complete Whitepaper Enforcement and February 1 Deployment Cutover

**Owner directive:** use the entire frozen Delta-A-Alpha Vertical Grid System V1 whitepaper, not a selection of independent source strategies. Treat **2026-02-01 00:00 UTC** as the *first simulated as-of deployment date*. January historical market context may initialize the EA; it cannot use January 2026 prices after deployment or any February outcome not yet realized. If February 1 is closed, initialize and measure qualified trading readiness from the **first valid tradable broker quote**, not from midnight. **No force-filled tickets.**

**State of this checkpoint:** VERIFIED TICK CUTOVER AND PRESTART HTF BOOTSTRAP; **FULL V1 FUNDED ECONOMIC FEBRUARY REPLAY NOT YET CERTIFIED**. Partial historical runs remain partial. This is not a positive profit claim. Do not confuse contractual architecture compliance with executable parity.

## Primary whitepaper source

Repository branch `delta-A-alpha`: `research/delta_a_alpha/whitepapers/DAA_VERTICAL_GRID_SYSTEM_V1_WHITEPAPER.md`. The permanent nine runtime layers are L0 ordered ticks; L1 independent session-specific grid; L2 role-separated completed H4/H1/M15/M5; L3 London/overlap/NY hourly high-volume; L4 Asia; L5 Watchdog/scout/funded renewal; L6 native trend-within-trend; L7 bounded wrong-direction recovery; L8 global physical equity, heat, layer capacity and margin. The original order must be retained, not treated as optional independent advisors.

## Deficiencies found in Jan 024 and Jan 026 rebuilt prototype

| Layer | Required whitepaper behavior | Actual 024–026 status |
|--|--|--|
| L0 | Ordered executable bid/ask first touch, funded fills, tick floating marks | Implemented only for reconstructed subset; actual portfolio source differed from original |
| L1 | Separate Asia/London/overlap/NY/late session geometries, price crossing ownership | M1 anchor and partial time-window cells, not full original lattice |
| L2 | H4 environment; H1 location; M15 phase; M5 transfer/opportunity | Completed EMA signs, but not full role-based contexts; some votes collapsed into direct entry filters |
| L3 | All high-volume accepted hour/subphase/parent/continuation engines | Selected 131D cells and simplified hourly heartbeat, missing complete source ownership |
| L4 | Truly independent Asia multi-regime grid engine | One selected Asia02 specialist; fails full-family parity |
| L5 | 049→051 parent funding, 075→084 owned child engine, 119→131A/B/E depth/4 funded-win unlock | Simplified one-cell parent; `streak` updated but **not consulted for renewal admission**; no exact owner genealogy |
| L6 | Causal trend-within-trend native routing | Select native cells only; full native portfolio not recovered |
| L7 | Bounded funded wrong-direction recovery with independent invalidation | **Not physically coded in 024**: observe-only loss markers; no separate funded recovery exits |
| L8 | One physical global governor, session/layer slots, floating equity, margin, stopout, duplicates | Global cap and floating marks only; **no broker-margin / stopout or complete per-layer capacity model** |

**MANDATORY LABEL GATE:** these Jan024/026 results are *partial strategy reconstructions*, never 'complete V1 backtest'. The Python static fail-closed audit confirms this. No increase in historical P/L can override that gate.

## Real January→February market-data cutover (completed unit test)

- Jan 2026: 9,135,062 Dukascopy Bid/Ask ticks; SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`.
- Feb 2026: 7,538,339 Dukascopy Bid/Ask ticks; SHA256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`.
- Both verified: no crossed Bid/Ask, disordered timestamps or rows outside the January/February partition.
- February 1 is **Sunday**. Earliest recorded Feb quote: **2026-02-01 23:06:26.655 UTC**, initial **$5.904** spread. Normalized $0.20 execution assumption is not acceptable as raw-quote certification.
- With **only Jan prices**, at first February quote pre-existing completed-bar EMA8/21 structural inputs initialize without new live hours: M5 5,766 completed bars, M15 1,922, H1 481, H4 131. Their latest quoted bar is about 47–49 hours old due to weekend closure; a cold-start EA should initially preserve core scout availability but treat short lookback opportunity signals as **stale**, not assume they describe the first tradable Sunday quote.
- Prehistory sufficiency is not an order-readiness pass: five-minute runtime quote/eligible-signal/first-order and broker margin remain untested on the **full system**.

## Proper as-of baseline and historical results (source-derived, NOT a new rerun)

Historical Gamma `GAMMA_02_FEB_UNCHANGED_JAN_MILESTONE_REPLAY_132A.md` retained *the unchanged January 131E architecture*, with the necessary February target-window exclusion of January warmup entries. Historical, normalized-spread **balanced L35/C640**: +$46,343.38; 26,025 trades; GL -$17,728.59; PF3.61; win89.18%; equity DD ~$17,725; max up to 640 positions. Aggressive unchanged L35/C703: +$48,224.26; 27,484 trades; GL -$17,728.59; PF3.72; win89.75%; equity DD ~$19,450; 10/20 positive days. These are the **proper source lineage** for an unchanged January strategy entering February. They are *not* broker-realistic executable-quote proof or a new unit027 portfolio run.

Feb `134J/134K` source documents later announced +$189,956.68 / 32,054 trades / PF14.70 / GL -$13,862.15 for Feb-specific improved V1—but those rules were **selected using February outcomes**, and cannot be retroactively deployed on Feb 1 as if February were still unseen. Likewise April-discovered profit-lock or spread thresholds cannot be retroactively shown as genuine Feb1 blind profits.

## Binding February-first experimental partition

- PRE-DEPLOYMENT: January only. Original January complete accepted helper lineage must be reconstructed and made executable on raw Bid/Ask. Parameter/model policies and all nine layers must be frozen to a commit/hash before Feb1.
- Feb1 T0: calendar deployment timestamp `2026-02-01T00:00Z`, no orders while market closed; `first_tradable_quote` measured from actual broker market/quotes. Use only pre-T0 completed bars and pre-T0 funded trade state. On opening Sunday quote at $5.904 spread, do not force a costly entry to meet startup SLA.
- POST-DEPLOYMENT: an EA may adjust from newly completed quote/bar/trade outcomes without knowing the calendar month. Never pass future MFE, future labels, or hypothetical shadow trade profits as actual funding credit.
- REVIEW: no full-strategy performance claims unless all nine passes, globally funded entry→exit parent-child execution, one authoritative tick ledger, and per-layer reconciliation. Show daily, weekly, month, cumulative net/gross P/L, PF, win, expectancy, velocity, DD floating vs balance, max open, layer source attribution, margin/survivability for $100k→$1k→$500→$300→$100, and startup eligibility time.
- SCIENTIFIC LIMITATION: February has already been studied extensively in 2026 research, so its retrospective replay is **chronological as-of/out-of-training**, not a pristine untouched holdout. August remains sealed, September owner-reserved. Do not borrow subsequent discovered rules while naming Feb a blind proof.

## Proper next reconstruction dependency chain

Read and reproduce exact bytes in order, retaining state/exit ownership: `GAMMA02_[019 hourly harvesting → 024 CUSUM → 049 causal profit-funded NY parent → 051 real-funded surge → 075 parent subphase → 084 owned sequential renewal → 119 Watchdog scout/gate → 131A/B/E January layer/heat]`. Compose with January 131D entire coverage+cold-start+session-native, full Asia geometry and L7 conditional recovery; all pass L8 physical global governor. Each accepted original rule must have (source_sha, timeframe, source_state, entry_tick, position_id, owner_id, funded, close_reason, exit_tick, realized P/L, original_v1_candidate). Track both funded and shadow separately. **Full V1 real-spread executable gate is open** until all modules match; do not use 026 profit-lock alone as a replacement architecture.

## Artifact files

- `verify_feb1_cutover_fast.py`: raw gzip SHA and chronological/month check.
- `feb1_cutover_tick_integrity.json`: Jan/Feb checksum and recorded first executable quote.
- `feb1_bootstrap_asof.py` and `feb1_predeployment_htf_bootstrap.json`: January-only completed-bar initialization proof.
- `whitepaper_fullspine_gate.py` and `feb1_whitepaper_layer_gate.json`: explicit fail-closed audit on Jan024 code (8 layers incomplete).

**No change to permanent V1 spine, frozen January fallback, production EA or paused May cursor. August and September data not opened in this checkpoint.**