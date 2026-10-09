# FEB045 — Original-V1 source-proposal February research: portfolio heat + fixed-lot finite-grid experiments

**Status:** COMPLETED FEBRUARY-FITTED RESEARCH; NOT accepted as full owner's V1/MT5 EA/broker-funded economic result. **Original complete owner V1 L0–L7 whitepaper remains binding and unchanged.**

## Research question
Starting from FEB044 in-sample February original-source proposal-tape system, can combining a genuinely funded-*within-the-model* directional/campaign heat governor, fixed 0.01-lot finite-grid geometry and entry-known source-quality gates meet all of: monthly net >= $200,000; 12,000 <= completed trades <30,000; PF>15; realized gross loss magnitude < $10,000; exact full-tick equity DD < $10,000?

**Result: four quantitative gates passed; $10,000 exact-DD gate FAILED.** No research candidate is certified as owner full V1; a favorable market-state filter selected by February outcomes has **selection/look-ahead risk at the research/policy-selection level** even when its decision-time inputs are historical.

## Frozen comparison (all numbers USD, fixed 0.01 lot, original February Dukascopy Bid/Ask; $100,000 research initial capital)

| Configuration | Net | Gross loss | PF | Trades | Exact full-tick equity DD | Max concurrent tickets | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| FEB044 prior | +212710.922 | -23464.931 | 10.0651 | 30923 | 23272.669 | 1536 | Original reference |
| FEB045 nine-pocket quality selection, no new state caps | **+206528.578** | **-7616.383** | **28.1164** | **25443** | **19308.087** | 1536 | **Preferred research frontier: profit cushion** |
| FEB045 eight-pocket quality selection + S22/S25 state-owned caps | **+200982.522** | **-8721.152** | **24.0454** | **25313** | **16458.447** | 1536 | **Risk frontier: lower DD, very weak net cushion** |
| FEB045 nine-pocket quality selection + state caps | +200053.013 | -7616.383 | 27.2661 | 24619 | 16458.447 | 1536 | DD risk frontier, effectively zero extra-cost margin |

All three FEB045 finalists independently revalued at every observed quote over 11,439,219 Jan-context+Feb quote indices and passed exact price-side P&L, <=1 accepted entry/tick, <=10/sec and global cap tests (`FEB045_INDEPENDENT_EQUITY_AUDIT.json`). Exit quote side is Bid for longs and Ask for shorts, with original research fee $0.02. Trade net already includes that modeled fee. Fixed-ledger extra-cost sensitivity: nine-pocket candidate would fall under the $200k objective after about $0.257 extra cost/trade; eight-pocket capped candidate after about **$0.039** extra cost/trade. These are *not* broker slippage simulations.

13 of 14 days with completed positions showed positive net in the primary quality frontier. Month is February 2026; comparison dates only for grading, not executable signals. February evaluation is exposed **in-sample** (multiple tests; do not claim blind transfer).

## Candidate mechanism / architectural provenance

- L0: original chronological Dukascopy true Bid/Ask first touches, original frozen source-proposal quote tape, fixed 0.01 lot, explicit per-tick cumulative floating P&L.
- L1: original Asia vs London/NY grid-event generators are preserved upstream; FEB045 admission experiments do not replace their proposal logic.
- L2: existing frozen completed H4/H1/M15/M5 structural permissions from upstream proposals are consumed, but **live native parity not separately certified**; no completed-role flattening or naive new EMA vote.
- L3: fixed first-touch S25 subphase 1,2,5 TP target of $10 per 0.01 research ticket, original source-specific proposal identity, market-state gates on **previous fully completed** ten-minute range and observed entry-side 20-second impulse. The new source-quality masks exclude subsets of FEB042/043 original source proposals after original permissions, not inventing new trades. The nine-pocket quality candidate preserves original source intelligence in shadow while denying select **physical** entries.
- L4: actual accepted funded-child closures within the fixed original proposal tape can drive renewal permission, but upstream hypothetical proposal descendants are **not regenerated** after changed admissions. This is a **major unresolved mandatory parity blocker**.
- L5: original trend-within-trend interface is not fully reconstructed/validated in this prototype.
- L6: original wrong-direction failure-conditioned recovery not fully reconstructed/validated; no generic inversion, DCA or Martingale.
- L7: all source proposals compete in one physically admitted model account; stress heat versus net conflict tested; source S22 PH5 with previous-completed 10m range >=32 and S25 PH1 with previous-completed 10m range >=64 can be given independently financed, realized-close-decremented concurrent caps of 512 each. Whole-system model max = 1536 positions, <=10 entries per second; broker margin/slippage/latency/stopouts and small $100-$300 funded account **not certified**.

### In-sample source quality exclusions (research model, NOT a deployable month-blind policy)

Research base rejects original proposal source IDs `[0,2,3,4,6,27]` for physical admission and preserves surviving native proposal generation. Then selected February-source-state denial pockets:
1. S25 subphase2, prior-completed 10m range [8,10)
2. S25 subphase1, range [16,20)
3. S23 subphase1, range [8,10)
4. S17 subphase3, range [6,8)
5. S17 subphase4, range [6,8)
6. S19, range [2,4), signed observed 20s impulse [1,2)
7. S25 subphase3, range [16,20)
8. S23 subphase2, range [16,20)
9. S17 subphase2, range [6,8) (nine-pocket only)

Additional original proposal filters, source masks and parameters live in executable `run_statecaps.py` / `run_pocket_screens.py`; **do not** rebuild these masks from prose or assert them as native EA logic. Source S25/22/27 IDs are original-source generator labels, not standalone indicator strategies.

### What genuinely failed in this turn

- Source-level pre-admission stress heat budgets reduce sampled floating risk but often starve profitable S25 entries; **they do not themselves liquidate or hedge a subsequently adverse existing basket**. An entry-sampled DD estimate below $10k is **not** the exact tick-equity DD.
- Equal-lot grid minimum spacing $0.25 in a tested same-source configuration reduced net to about $41k: fixed-lot **Martingale-shaped grid geometry cannot guarantee profitability**. No actual Martingale scaling tested/approved and no loss-dependent sizing allowed in V1.
- Locking in profits with first-passage trailing logic commonly truncated profitable recoveries, failing the net target.
- Broad expansion of original S22/S24 volatility opportunity bands reintroduced realized losses or excessive overlapping exposure (S22 >1k funded longs in risk case).
- Tight first-passage stops after temporary adverse moves crystallized profits that would otherwise recover, increasing actual loss / sacrificing net.
- Flat S22 cap exposed next worst DD in S25 PH1; coordinated state-conditional 512/512 caps improved exact DD to $16,458 but **still not <$10k**.

## Exposed risk events and interpretation

- Uncapped lower-gross-loss FEB045 equity DD $19,308 on Feb11, 2026, 09:47→13:18 UTC equity interval, 768 S22 long positions near the worst trough; S22 eventually realized profitable outcomes despite ~$10,859 basket floating loss at trough.
- After limiting S22, a second risk event consists of roughly 510 simultaneous S25 phase-1 longs Feb20 with large temporary adverse excursion (~$14,845 S25-specific float); profit recovery happened later, so forced fixed stops trade down the objective.
- Unified entry-admission heat ownership improves capital scheduling but cannot guarantee mark-to-market DD ceiling under adverse post-entry excursion. Hard DD constraint would require executable reduce-only exits/hedges plus conservative look-ahead-free budget and tested ability to replace lost profit; **none certified**.

## Required next science and certification

(1) Rebuild **full original eight-layer V1 L0–L7** from literal 14,232-character owner whitepaper. Do not replace with shortened derived L0-L8 or leave native trend/conditioned recovery out. (2) Recompute original source event and funded parent-child genealogy endogenously on the actual quote stream after each accepted/rejected physical trade; correctly simulate broker execution margin, fees, spread/slippage, queue and equity/stopout in unified L7. (3) Replay frozen JAN039+FEB043+FEB045 mechanics across previously seen Jan/Feb, then use genuine later development months and sealed August as truly untouched holdout only when authorized; feature selection must use only earlier observations and frozen causal policy. (4) Distinguish high-profit/high-capacity $100k research economics from $100–$300 small accounts; **1536 simultaneous tickets and 10/sec not deployment-ready**. (5) Keep both accepted reference and risk frontier without promotion until validated.

## Reproduction

`FEB045_UNIFIED_HEAT_GRID_RESEARCH_BUNDLE.zip` includes the Python experiments, cap/governor implementation, test ledgers, hashes and independent audit; it **does not** duplicate the raw January/February Dukascopy tick archives or the original FEB044/frozen V1 source dependency. Get these original assets from the project Library and verify hashes.

Use `FEB045_HANDOFF_READ_FIRST.md` and `FEB045_MACHINE_STATE.json` for exact paths/cursor, then `python independent_state_audit.py` once original quote arrays are recovered. Run `python verify_statecaps.py` to regenerate the exact capped finalist from the original unchanged FEB044 proposal tape. No future data may leak into an entry; nevertheless February-informed thresholds remain in-sample.