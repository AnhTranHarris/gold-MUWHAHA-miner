# Delta-A-alpha V1 — Gate 033, Phase C2A: original 049/051 capital and funded 119 source contracts

**Status:** PARTIAL ENGINEERING; **NOT complete C2**, NOT complete eight-layer V1, NOT an MT5 EA, NOT a successful monthly backtest. Original immutable owner L0–L7 full whitepaper: `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`, Git blob `1b92b3c89159681a7181508de158af685cf5780c`. Keep original permanent spine and Jan039/Feb045/Feb047 source-model references unchanged. March held; August sealed; September reserved.

## Original source lineage and non-equivalence

- **049** `gamma02_profit_funded_surge_049.py` selects a union/deduplicated S16/S17 candidate stream from 024 (intrinsic pulse), 017 (latency/union), and 019 (heartbeat), using two profit-conditioned capacity components. `049` original function `select_funded_surge` operates on precomputed child closes and PnL.
- **051** `gamma02_profit_funded_surge_equity_051.py::select_idx` is the original *index* selector, same 049 source+capacity economics; it exposes the admitted upstream parent indices to later helpers.
- **075** `gamma02_ny17_quantum_minute_window_075.py` is **offline research that studies** NY17 minute windows, favorable minute displacement and a quantum. It is **not** itself the generic live parent generator. Do not silently force a 075 discovered window into the production 119 parent rule.
- **084** `gamma02_083_heat_parent_ownership_084.py::renewal_owned` creates child first-touch events for PREKNOWN selected parent start/end ticks, with a winning-exit reference and 0 rearm; this uses a future parent end for historical research and therefore cannot be copied blindly as live execution.
- **119** `gamma02_dynamic_watchdog_router_119.py` groups eligible parent candidates into NY-local 12/13 hours with completed H4/H1 macro agreement and signed parent direction. It admits first chronological parent per cell, then other parents only after 4 actually **realized**, <=60 s, profitable child closes; bad/slow child relocks. Original offline version **precomputes every child's outcome** and applies a separate final capacity cap. We must re-execute paid children and cells endogenously; precomputed rejected children do not earn credit.
- **131A** `gamma02_jan_watchdog119_grid_layer_refinement_131a.py` sets 0–4 completed NY ten-minute subphases to 1.19 USD and last subphase to 1.10 USD for Watchdog children (fixed 0.01 lot, no Martingale). It uses the same NY macro parent cell grouping as 119 and changes only permitted q/funding geometry.
- **131E and 134K full native structure are still incomplete**. The prior 033 C1 adapter only implements *first cell parent* and paid L4 relocks, not original 119 successive **earned new parent windows** or the complete 049 union. This C2A port does not claim otherwise.

## Actual implementation in this checkpoint

`original_funded_lineage_033c2.py` adds:

1. `Original049Settings` and `Original049FundedCapacity`: exact historical 049/051 base/surge cap geometry. Only genuine *executed* 049-funded L3 closes feed the surge bank; rejected or hypothetical source outcomes never do.
2. `Original049OnlineSource`: a composable quota applied to source `ORIGINAL_HB_019_UTC16/17` proposals. **This wrapper currently delegates to the source-verified ORIGINAL 019 heartbeat**, not the full source 024+017+019 union. All other L3 sleeves share L7 but are not incorrectly counted as 049 capacity. Source-specific capacity denial must precede general L7 funding.
3. `Original119FundedParentSource`: original 119 completed NY-local/macro cell identity restricted to truly funded 049 L3 positions, with literal 131A subphase quantum; after an actually realized good child, new entry is additionally gated by original 084 favorable quote reference (Bid for long; Ask for short). First child may scout on next observed quote (no same-quote duplicate). The earliest funded source parent per cell still owns the C1 finite window; **second/third earned parents in the same cell remain a C2B gap**.
4. Six newly added C2A regression tests compare selected indices of the archived original 051 offline function against causal arrival/close simulation, ensure denied parents cannot pay the surge bank or create L4 children, verify last observed executable favorable rearm and 1.19/1.10 qmap. Inherited 40 Phase C1 tests also pass; **46/46 passing**.

## Genuine Feb Bid/Ask diagnostic and exposed limits

Authentic January 10-day context (3,900,880 quotes) and 1,136,212 consecutive February quote events. Dukascopy January/February raw `.csv.gz` sha256 verified before reading, no August or September. Original completed-EMA sign source is a **diagnostic proxy, NOT exact owner H4 environmental / H1 location / M15 phase / M5 transfer**, and the model account is idealized $100K, 32 positions, 4/s, fixed 0.01 lots.

| Scenario | 049 upstream cap | 049 physical parent candidates | Funded 119 windows | Funded L4 children | Closed trades | Research net | All-quote DD |
|---|---|---:|---:|---:|---:|---:|---:|
| C2A normal 049 settings | default at least 576 | 64 | 4 | 14 | 1,443 | -$903.658 | $2,343.763 |
| C2A causal 049 cap stress | 2 concurrent funded source positions | 4 | 2 | 10 | 1,438 | -$1,287.472 | $1,561.471 |

The tight cap rejects 26,597 out of 26,619 S16/S17 original-019 proposals before L7; source 119 parent windows and funded child trade count change. No claims of true original 049 admitted proposal count or full original 119 131A event-by-event *source parity*. Both runs lost money and cannot be compared to Jan039 or Feb047 full month results.

## Outstanding mandatory C2B/C2C work before full gate 033

1. Recover 017/019/022/024 original multi-source L3 proposal manufacture and merge/dedup identical to `049.build`; compare exact ordered, state-qualified parent-entry candidate indices on January and February (not only tested synthetic 049 capacity fixtures).
2. Integrate that candidate union with actual L7 fills. Reconstruct original 049/051 admitted physical parent index stream on genuine tick windows and document divergences caused by funding, margin, and true exited PnL.
3. Implement complete `119` multi-parent-per-cell earned admission, not merely first-parent C1 window. Confirm exact deterministic intra-quote parent tie handling, first physical child at next quote, all 084 child first-touch/late residual behavior and 131A subphase rearm semantics without future parent exits. Denied children cannot affect unlocks.
4. Recover complete native L1 session/Asia and L2 role-separated H4/H1/M15/M5, L3 fast source sleeves, original L5 routing, independent failure-owned L6 and shared L7 stopout/margin/broker order rules.
5. Re-run entire Jan 9,135,062+Feb 7,538,339 quotes and both approved months in *one* fully endogenous funded architecture. Source-model profits cannot be assumed to survive. MT5 original EA v1.05 remains observe-only; Coinexx broker real-tick/MetaEditor validation mandatory afterward.

**Failure mode explicitly prohibited:** No automatic date/month switch; no phantom Watchdog profit credit, no Martingale/DCA, no frozen future child tape, no intratick fills on nonexistent quote, no delayed exit assumed executed when over rate.

### Reproduce

```
cd DAA_033_phase_c2
python -m unittest -v test_v1_funded_core_033 test_original_heartbeat_parity_033 \
 test_scorecard_033 test_broker_context_safety_033b test_original_online_sources_033c \
 test_original_funded_lineage_033c2
python real_integrated_033c2_smoke.py --root /mnt/data --max-quotes 1136212
python real_integrated_033c2_smoke.py --root /mnt/data --max-quotes 1136212 --low-surge --out REAL_CAPPED_049_033C2_SMOKE.json
```

The compressed JAN037 original-source ZIP and January/February `.csv.gz` original Dukascopy files must exist; hashes are validated. All source snapshots are archived for future exact function extraction. No external broker trading was performed.