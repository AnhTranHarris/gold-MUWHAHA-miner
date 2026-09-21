# gold-MUWHAHA-miner

Clean-room MT5 research project for the **Gold MUWHAHA Miner** XAUUSD Expert Advisor.

## Authoritative R10 source-audited replacement candidate

Branch:

`carson/r10-from-r9-code-11-source-audited-rebuild`

EA:

`Experts/GoldMuwahahaMiner_R10.mq5`

This R10 is a **cumulative upgrade of R9 HybridGate**. It starts from
`carson/mt5-r9-hybrid-gate-certification` and carries accepted post-R9
breakthroughs forward as executable checkpoints.

The previous checkpoint
`carson/r10-from-r9-code-10-r10-replacement-candidate` is retained for
comparison but has been superseded by the source-audited checkpoint 11.

The older `carson/mt5-r10-session-regime-certification` line is historical and
is not the R10 replacement.

## Cumulative executable lineage

- 00 — exact R9 behavioral port
- 01 — CONTINUE / FADE / ABSTAIN + REAL-path harvest + catastrophe memory
- 02 — P3 failed ignition + P4 rotation + P6 expansion
- 03 — P5 H1/H4 structural trend sleeve
- 04 — P8 sweep/reclaim + P9 acceptance
- 05 — P11/P12/P13 3m/5m/10m/20m hierarchy
- 06 — four-position portfolio knee / one position per scale
- 07 — opposition heat + state-stability priority
- 08 — post-catastrophe KEEP / FLIP / ABSTAIN
- 09 — P7 volatility-normalized compression break
- 10 — per-sleeve lifecycle isolation
- **11 — source-to-code audit: auction-state identity, same-scale KEEP/FLIP,
  causal failed-state flow, successful-stop harvest accounting, and
  position-identifier keyed runtime state**

## Source-audited checkpoint 11 corrections

Checkpoint 11 corrects several implementation details that were not faithful
enough to the research record:

1. **Auction event identity is preserved.** A P8 sweep, P9 acceptance, P11/P12
   3-minute event, P13 multiscale event, P7 compression break, and R9 activity
   event no longer collapse into an anonymous CONTINUE/FADE label before the
   portfolio governor sees them.
2. **State stability is event/action aware.** The known toxic
   1-minute upside-acceptance → CONTINUE state is blocked by default. The
   complete historical top-two-state-per-scale table is not invented; its
   remaining weights stay explicit for Jan-Apr reconstruction.
3. **KEEP/FLIP is same-scale.** The post-catastrophe KEEP/FLIP policy applies
   only to a follow-up event on the scale that produced the catastrophe.
   The separate 10-second same-direction catastrophe memory still propagates
   across the hierarchy.
4. **Harvest protection is real, not attempted.** A position is marked
   harvest-armed only after `PositionModify(ticket,...)` succeeds and the
   trade-server retcode is accepted.
5. **P3 failed ignition is causal and normalized.** The old absolute-dollar
   shortcut is replaced by delayed failure evidence: near-zero MFE,
   ATR-normalized MAE, efficient adverse displacement, and opposing tick flow.
   Exact later fitted coefficients did not survive the research handoff, so the
   thresholds are exposed as reconstructed tester defaults.
6. **Hedging telemetry is position-identifier keyed.** Runtime MFE/MAE,
   harvest state, scale, and entry ATR follow `POSITION_IDENTIFIER` /
   `DEAL_POSITION_ID`. Late trade-transaction notifications therefore cannot
   erase the state of a newer trade on the same scale.
7. **Order comments are compacted.** Full event/action state remains in journal
   logs; broker order comments use a compact <=30-character representation.

## Strongly recovered rules

These are carried with high confidence from the project evidence:

- original R9 minute event geometry and S1 eligibility
- balanced strengthened S1 router:
  - CONTINUE <= -0.255 with completed-S1 range >= 0.285
  - FADE >= +0.275 with completed-S1 tick count >= 5
- defensive S1 profile -0.290 / +0.310
- $5.00 emergency room
- $0.01 favorable ignition
- $0.01 high-water harvest
- 120-second HFT lifecycle ceiling
- 10-second same-direction cross-scale catastrophe memory
- maximum four simultaneous portfolio positions
- one live position per temporal scale
- opposition-aware portfolio control
- H1/H4 P5 structural sleeve family
- P8/P9 and 1m/3m/5m/10m/20m auction hierarchy

## Reconstructed parameters that still require Jan-Jul re-certification

The project history preserves these mechanisms and their research performance,
but not every exact fitted coefficient:

- P3 failed-state severity thresholds
- P4 rotation ATR/efficiency cutoffs
- P6 expansion ATR/efficiency cutoffs
- P7 compression/breakout thresholds
- P8/P9 penetration/reclaim/acceptance distances
- complete state-stability rank table
- exact post-catastrophe KEEP/FLIP scoring coefficients

These parameters are visible inputs. They must not be described as recovered
historical constants until re-derived from Jan-Apr development evidence and
confirmed on May-Jul.

## Community cross-checks used for implementation

- MQL5 CTrade PositionModify:
  https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradepositionmodify
- MQL5 OnTradeTransaction:
  https://www.mql5.com/en/docs/event_handlers/ontradetransaction
- MQL5 Deal properties / DEAL_POSITION_ID:
  https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties
- MQL5 Position properties / POSITION_IDENTIFIER:
  https://www.mql5.com/en/docs/constants/tradingconstants/positionproperties
- MQL5 live MFE/MAE tracking:
  https://www.mql5.com/en/articles/22855
- MQL5 correlation-aware multi-EA portfolio:
  https://www.mql5.com/en/articles/21955
- TradingView Liquidity Sweep & Pivot Reclaim:
  https://www.tradingview.com/script/83NNMfO1-Liquidity-Sweep-Pivot-Reclaim-v2-memo/
- TradingView HTF Liquidity Sweep & Reclaim:
  https://www.tradingview.com/script/FG507Q8S-HTF-Liquidity-Sweep-Reclaim/

Community sources are architecture cross-checks only. They do not override the
project's Jan-Jul research evidence.

## Certification status

This remains a **MetaEditor compile/test candidate**, not a production-certified
EA.

Next gate:

1. compile `Experts/GoldMuwahahaMiner_R10.mq5` in MetaEditor;
2. fix compile defects without altering strategy semantics;
3. run XAUUSD **Every tick based on real ticks**, Jan 1-Jul 31, 2026;
4. report monthly net profit, gross loss, and maximum dollar drawdown;
5. run $100 and $200 marked-equity/margin survivability tests;
6. reconstruct/freeze the missing Jan-Apr state-stability table only from
   Jan-Apr, then verify it on May-Jul;
7. freeze R10;
8. open August 2026 once.

**August 2026 remains sealed.**
