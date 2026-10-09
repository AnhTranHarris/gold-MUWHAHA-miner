# FEB046 — Integrated Loss Prevention + Funded-Failure Recovery Research

**Research status:** Completed exploratory FEB046 diagnostic; **no strategy upgrade or full-V1/MT5 certification**. Original owner *unabridged* eight-layer V1 whitepaper governs all work and remains unchanged. February is a known in-sample optimization month, not a blind forecast.

## Why portfolio repair is an original V1 responsibility

The owner's original L0→L1→L2→L3→L4→L5→L6→L7 design already demands fully cooperative session-specific grid opportunity manufacture, completed H4/H1/M15/M5 structure, dense London/overlap/NY hourly harvesting, separate Asia geometry, realized-child Watchdog renewal, native trend-within-trend routing, failure-conditioned recovery, and unified funded heat and margin risk. **Combined portfolio repair is not a new layer.** The missing engineering part is a fully endogenous source and funding/exit feedback loop. This checkpoint tests candidate risk mechanisms around the archived FEB045 accepted portfolio; it does not claim to reconstruct the missing entire V1.

## Frozen February baseline

| February source-model accepted portfolio | Net USD | Realized gross loss USD | PF | Complete trades | All-quote equity DD USD | Max modeled open |
|---|---:|---:|---:|---:|---:|---:|
| FEB045 nine-pocket profit cushion | +206,528.578 | -7,616.383 | 28.116 | 25,443 | 19,308.087 | 1,536 |
| FEB045 capped prevention | +200,982.522 | -8,721.152 | 24.045 | 25,313 | 16,458.447 | 1,536 |

Underlying February original Bid/Ask 7,538,339 quotes plus 3,900,880 January context quotes = 11,439,219. Verified January and February gzip SHA256 values in `FEB046_FINAL_QA.json`. Modeled $100k initial account, fixed 0.01 lots, $0.02 roundtrip fee, unreconstructed Coinexx fills and margin. Order admission cap is 1 per tick, up to 10 per second.

## Research families and observed results

### 1. L6 post-*realized*-loss recovery overlay

After a genuinely accepted predecessor closed at a loss, enter **only on a later observed quote** if completed M5, H1, or both support a chosen continuation/reversal direction. Model independent entry, first-touched executable Bid/Ask TP/SL, timeout, own recovery cap and the inherited baseline account capacity and 10/s rate at entry. Test 18 configurations (`recovery_experiments.py`, JSON ledger). Every new recovery trial with actual trades showed *negative incremental net*; best net-preserving screened result was a negative $43.785 with 38 recovery trades, with baseline exact DD unchanged for the independently fully checked leading variants. Because original accepted upstream entries are frozen, this is **an overlay diagnostic**, not an endogenous V1 funded simulation.

### 2. Strict pre-close L6 structural recovery overlay

Require that an *actually funded and still-open* S22 or S25 predecessor has failed after an already-elapsed 60/180/300 seconds, exhibits an entry-known adverse price displacement of $3/$6/$10, and BOTH completed M5 and H1 structural slopes support the prospective corrective trade. One fixed-lot recovery at most per observed predecessor, separate TP/SL, eight-or-sixteen own-risk capacity with the baseline account order rate. Eighteen screens (`structural_recovery_overlay.py`) rarely identified sufficiently confirmed failures; the 300s/$3 threshold allowed 16 additional trades and produced -$33.608 net at $3 TP/$2 SL. More permissive 180s/$1 thresholds generated additional trades but negative incremental profit. These are not original-L6 native geometry or a certified anti-hedge.

### 3. Prevention-only vs combination ablations

The same 5 L6 overlays were applied separately to the original FEB045 profit cushion and to its lower-DD *prevention* portfolio (`combined_test.py`). **All ten combinations reduced net and increased realized gross loss; exact maximum equity DD remained unchanged** at 19,308.087 or 16,458.447 respectively. The overlays do not regenerate future source proposals or consume broker-correct future capacity as a true active engine would. All new recovery prices/settlements are quote-side reconciled.

### 4. Pre-close structure/stop experiments

A structurally permissioned reduce-only exit requires an actual still-open position, already-elapsed failure window, first observed adverse price threshold, and *completed* M5 trend against the position. The cloned source engine re-runs chronological admissions with altered first-touch exits, not a retroactive classification of accepted trades. Six focused threshold combinations and 13 initial screens completed. The S25 180-second/$18 adverse-exit case dropped model net to $184,888 and raised gross loss to -$22,404; **true max equity DD stayed at $19,308** despite lower sampled entry-event DD. Exit timing can prematurely crystallize recoverable temporary loss.

### 5. Realized-funded-loss source re-lock

An actual source close at P/L <0 updates that source's loss timestamp; follow-on source proposals can be rejected for 5–15 minutes, optionally until completed M5 structural confirmation. Source S22/S25 accounts for only 39/58 baseline realized losers, respectively; the market-reversal floating losses come mainly from originally winning baskets. Six final 5/15-minute source re-lock screens (`run_loss_relock_focus.py`) confirmed no exact DD reduction. Relocking S17/S19 reduces net by ~$2.2K over five minutes while saving only about $0.45 gross loss. There are earlier broad 13 cases, not all completed due runtime interruption; see original logs.

### 6. L7 portfolio-wide peak-equity admission guard

A cloned portfolio engine computes actual *observed-at-proposal* account net liquidation equity from the currently accepted tickets, updates peak equity causally, and denies NEW admissions above a calibrated floating DD threshold. Twelve configurations over two source-quality policies completed. A $12k admission-event guard on the prevention variant produced +$200,245.212 net, PF 23.9609, gross loss -$8,721.152, 25,490 trades, **$19,308.087 exact all-tick DD** despite its entry-event DD of $11,923.57. The guard prevents future admissions but **does not close already adverse baskets**. This is why sampling equity at entry or throttling new tickets cannot be used as proof of the hard <$10K all-quote DD constraint.

## Important daily January→February adaptive lesson

The February profitable-trade system has **multiple** independent high-DD days: Feb 11 $19,308, Feb 20 $17,184, Feb 4 $14,131, Feb 24 $10,206, Feb 27 $10,053 intraday all-quote DD. The first three nevertheless realized +$33,732, +$50,526 and +$35,030 net respectively. A governor engineered solely to hide Feb 11 will fail on another day. See full daily/weekly data in `DAILY_FORENSICS.json`.

## Core research inference and next engineering unit

**No tested FEB046 candidate simultaneously satisfied all five previously declared targets: $200k net, 12k–<30k trades, PF>15, realized gross loss magnitude<$10k, and true full-tick floating DD<$10k.** Several controls improved snapshots but did not change peak quote DD; others cut recoverable profitable inventory and destroyed net. The observed loss is an *unrealized, correlated portfolio risk* and cannot be fixed by after-the-fact recovery.

The next test needs a **single chronological, causal economic engine**, not a fixed upstream tape and external overlays: native L0 executable ticks; L1 session-specific cell genealogy; completed H4/H1/M15/M5 states; L3 London/NY heartbeat & separate Asia; L4 close-confirmed Watchdog; L5 structural transfer; L6 actually failure-conditioned recovery and independent invalidation; L7 quote-level account/equity/margin and stress-aware incremental admission/reduction. It must feed funded exits back into the next source proposal, permit reduce-only before dangerous concentration develops, and measure capacity opportunity substitution rather than merely suppress future trades. Fix physical-genealogy gate **033** before promoting February risk fixes. Original owner V1 permanently frozen, August sealed, September reserved.

## External reconstructible technical ideas (not imported profits)

- MetaQuotes, *Building a Research-Grounded Grid EA in MQL5*, finite/restartable risk-bounded grid: https://www.mql5.com/en/articles/21833
- MetaQuotes, *Building a Correlation-Aware Multi-EA Portfolio Scorer in MQL5*, portfolio correlation exposure: https://www.mql5.com/en/articles/21955
- MetaQuotes, *Engineering Trading Discipline into Code (Part 7)*, governance state transitions: https://www.mql5.com/en/articles/22833
- MetaQuotes Chinese, *交易机器人风险管理器（第一部分）*, order-approval risk manager: https://www.mql5.com/zh/articles/18918
- Community discussion on overlapping multi-strategy heat risk: https://www.reddit.com/r/algotrading/comments/1rtwnfm/approaches_to_risk_management_and_order_size/

These published mechanisms motivate finite risk limits and heat governance; their claimed performance is not evidence of this user's EA performance. Kelly or dynamic lot escalation is **not allowed**; our experiments retained the owner's fixed 0.01 lot and no Martingale.

## Reproduction and caveats

Run from the original month archives and FEB044/FEB045 bundles whose SHA values are verified. Source scripts include `recovery_experiments.py`, `structural_recovery_overlay.py`, `combined_test.py`, `structural_exit_test_narrow.py`, `run_loss_relock_focus.py`, `run_equity_guard.py`, `daily_forensics.py`, plus cloned prototype engines. All source-model variant selections are February-exposed, **not blind**. Read `FEB046_FINAL_QA.json` and the raw scenario JSON files. No original owner whitepaper, production Delta, or MT5 EA modification is authorized or undertaken.