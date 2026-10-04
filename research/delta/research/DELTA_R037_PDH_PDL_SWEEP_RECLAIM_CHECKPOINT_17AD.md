# DELTA R037 — Previous-Day High/Low Sweep → Reclaim Stage-A Screen — Checkpoint 17AD

**Status:** COMPLETE / STRONG STAGE-A SURVIVOR  
**Unit:** R037_PDH_PDL_SWEEP_RECLAIM_STAGE_A_SCREEN_CHECKPOINT_17AD  
**Parent:** R037_COMEX_15M_OPENING_RANGE_STAGE_A_SCREEN_CHECKPOINT_17AC  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Question

Can a structurally distinct previous-trading-day liquidity event outperform the recently retired London/COMEX opening-range families under the exact same frozen 30-second execution economics?

The preregistered sequence was:
1. construct the prior available UTC trading-day high/low from causal P75 Bid;
2. observe the first strict breach of either level on the current trading day;
3. reverse only after one of three fixed confirmation semantics;
4. one accepted trade/day; <=25-point spread; no session/side/weekday filters.

## Provenance and crash safety

- prereg commit: `e37857a09553454b4477a6bc00003288ce3fd775`
- producer commit: `1d286c88583b7c3208bd338d734749df439c2897`
- producer blob: `4a30f52c33d86120940b7b6f6fa7cc7c908982fc`
- producer SHA-256: `008cf1c703037e3a864560a3753ab8a1b7ab97b05152aa45d73691f5458f101e`
- canonical January SHA: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- official runtime: **3.544 s**
- official raw result SHA-256: `2696aa72d77f3a13811a20ab223feb238ebfcc9813cd5ba3a3d0d4cbf0ad6233`

The first local execution copy failed the exact git-blob comparison and was rejected before compute. The exact committed producer was reconstructed locally, matched GitHub blob `4a30f52c...`, compiled cleanly, then executed once under a 60-second hard timeout.

## Results

| Lane | Trades | Wins | Gross profit | Gross loss | Direct net | Decision |
|---|---:|---:|---:|---:|---:|---|
| C01 strict tick reclaim | 12 | 5 | +$2.47 | -$4.74 | **-$2.27** | FAIL |
| **C02 completed S5 reclaim** | **10** | **4** | **+$4.55** | **-$2.97** | **+$1.58** | **STRONG PASS** |
| C03 S5 reclaim + five-bar MSS | 7 | 3 | +$0.84 | -$1.90 | **-$1.06** | prescreen only |

C02 had 12 source proposals, 10 eligible executions, and 2 causal `RELOST_AT_EXEC` rejections.

## Breakthrough interpretation

The evidence does **not** support indiscriminate prior-day sweep fading: the immediate tick reclaim loses money. It also does not reward additional preregistered micro-structure complexity: C03 reduces supply and economics.

The only strong survivor is the middle causal semantic:

> **first PDH/PDL sweep → completed 5-second close back inside the prior-day boundary → enter reversal if the execution quote still remains reclaimed.**

That is a clean timing/confirmation effect, not a post-result threshold fit.

## Decision

**FREEZE C02_S5_CLOSE_RECLAIM unchanged and advance it to independent later-January validation.**

Do not change:
- PDH/PDL definition,
- sweep definition,
- S5 reclaim timing,
- spread gate,
- 30-second lifecycle,
- stop/trail constants,
- side/session/day filters.

No MQL5. No August.

## Next bounded unit

`R037_PDHSR_C02_INDEPENDENT_LATER_JAN_VALIDATION`

The next test must use the frozen C02 logic on the later-January holdout, with prior data allowed only for causal warm-up/context and no economic entries before the holdout boundary.
