# DAA V1 — 033 PHASE C2B: Original 049 NY16/17 multi-source ENTRY union source parity

**Status: C2B SOURCE-ENTRY PARITY PASS; PHASE C2 ENDOGENOUS ORIGINAL 119 MULTI-PARENT CAMPAIGN PARITY NOT COMPLETE.** Not full V1, not broker certified, not a profitable-month backtest. Full owner-frozen eight-layer V1 whitepaper remains the authority at `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`; its Git blob is `1b92b3c89159681a7181508de158af685cf5780c`.

## Upstream source reconstruction

The predecessor Phase C2A `original_funded_lineage_033c2.py` implemented the archived `049/051` *capacity* geometry against actual funded closes, but its upstream source was only the `019` standalone heartbeat. Phase C2B now ports **the actual eligible S16/S17 ENTRY universe of `049.build(120)`**, using original `001/014` New York extension, `017` NY17 rebreak, `019` NY16/17 120-millisecond heartbeat and `017.union_dedup` source+tick priority. The source's earlier London/E18 components are intentionally omitted **only because** the historical `049.build` filters all candidate entries to S16/S17 at the end. All event generation is online from past/current observed ticks and current completed-as-of structural signs; **no future exits, PnL, or unfinished bars** are used to manufacture new source candidates.

Original source snapshots in the archive come from `JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip` and its nine SHA-256-verified original files (see Phase C2A QA). Historical candidate-source identity for this scoped NY16/NY17 entry universe is independently checked against the **untouched functions themselves** in `test_original_ny049_union_033c2b.py` and `real_049_union_parity_033c2b.py`.

### Genuine February source entry parity

With 3,900,880 genuine January pre-window context quotes and 1,136,212 ordered February original Dukascopy Bid/Ask ticks, both with archived monthly SHA-256 verification, the untouched original `001/017/019` generators and the new quote-causal candidate adapter generate **exactly 13,063 deduplicated NY16/NY17 event indices**, matching **every tick index, direction and original source hour**. The per-source breakdown of the online generator is 1,305 extension / 14 rebreak / 11,744 heartbeat = 13,063. This is an **entry-source parity statement**, not an original funded parent or original 119 downstream child/exit parity statement. The completed H4/H1/M15/M5 states for this test are the *original historical completed EMA sign* helper's output, **not** proof of the full owner L2 environment/location/phase/transfer semantics.

### Causal funded downstream sensitivity, same February quotes

The new NY source generator `Original049NYSourceL3` feeds the Phase C2A `Original049FundedCapacity` as original source L3 tickets, in one shared L7 mock account with original 131D research sleeves and C2A's first-parent-only `119` adapter. The parent is created only after an L7 accepted L3 fill; a hypothetical denied parent gives no Watchdog credit. Simulated account is an explicit **$100K / max32 / 4 total orders per second / fixed 0.01 lots**, **not Coinexx**.

| Source model | NY16/17 exact underlying entry events | Funded 119 first-parent windows | Executed L4 child entries | Closed positions | Net | Exact full-tick equity DD |
|---|---:|---:|---:|---:|---:|---:|
| Original 049/051 surge geometry | 13,063 | 5 | 20 | 210 | +$23.849 | $2,339.194 |
| Counterfactual fixed 2 funded NY source slots | 13,063 | 2 | 10 | 26 | -$57.074 | $223.503 |

The constrained `049` quota denied 13,042 out of 13,063 original NY source opportunities; **funded downstream parent and child activity changed**, as it should when the portfolio cannot physically fund all upstream opportunities. **Neither line is full-month February or a performance improvement claim.** The full February JAN039/FEB045/FEB047 historical reference scorecards remain untouched and remain provisional source-model research.

### Tests

The inherited 40 C1 + six C2A contract tests and new NY049 001/017/019 entry comparison pass: **47/47 Python tests**. `real_049_union_parity_033c2b.py` independently reconstructs both original and online entry sequences on real February ticks, checks **13,063/13,063**, throws if a single index/direction/source differs, and records evidence to `REAL_049_UNION_PARITY_033C2B.json`.

```
cd DAA_033_phase_c2
python -m unittest -q test_v1_funded_core_033 test_original_heartbeat_parity_033 test_scorecard_033 test_broker_context_safety_033b test_original_online_sources_033c test_original_funded_lineage_033c2 test_original_ny049_union_033c2b
python real_049_union_parity_033c2b.py
python real_integrated_033c2b_smoke.py --max-quotes 1136212
python real_integrated_033c2b_smoke.py --max-quotes 1136212 --low-surge --out REAL_CAPPED_049_033C2B_SMOKE.json
```

### OPEN — remaining source parity required for C2C / full 033

- Historical source `049/051` **physical funded cap** equivalence with all true original admitted union candidates, including quote-side fills, recognized prior realized costs and actual 049 order-denials, not merely synthetic capacity-index parity. Already-written code is causal but source-wide proof is open.
- Full `119` admission of additional **earned funded parents** in an original cell after four actual <=60 second winning child closes. Current C1-derived adapter only owns the first parent of each cell, a documented deviation. Reconstruct original 084 child residuals, 131A qmap and relock behavior with actual quote-side Bid/Ask order queues and **never** pay for a nonexistent or rejected child. Historic 119 precomputed child tapes cannot be directly transplanted.
- Complete native V1 L1 Asia and all sessions, role-distinct completed L2 H4/H1/M15/M5, native L5 specialist and L6 true failure-conditioned proposal engines, and Coinexx broker-realistic L7 margin, stopout, slippage and account hedging constraints. Original MQL5 V1.05 remains observe-only.
- Full January/February online funded L0–L7 regression before March research; parameter selection must be based on causal market states, **never** calendar-month identities. August sealed, September reserved.

**This is original source-engine implementation progress, not a new trading strategy or proof that prior >$200K source-model monthly profits will survive full funded physics.**