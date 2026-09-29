# BETA035 — Gold Hunter V8 source archaeology, OCO/rearm microstructure and original R9 REAL/SYNTH cross-feed experiment

**Date:** 2026-09-29 | Independent BETA | **No strategy promoted; no official MQL5 code authorized** | August SEALED.

## Investor-level result

A **single identical, reconstructed Gold Hunter V8-style M1 stop-bracket/OCO/opposite-boundary rearm rule** on two genuinely different original Coinexx R9 historical tester quote streams produced opposite economics in a one-day diagnostic:

| Identical V8-style rules, two different archived R9 ticklogger feeds on January 2, 2026 | Original R9 REAL tester quote stream | Original R9 SYNTH generated-tick stream |
|---|---:|---:|
| Logger tick rows independently replayed | 341,569 | 330,217 |
| Literal 50 Hunter-pip / $0.50 dual STOP bracket, $0.50 stop, $0.20 activation/trail, old opposite-level same-M1 rearm; replay closes | 2,662 | 1,693 |
| Winning replay closes | 960 (36.06%) | 1,186 (70.05%) |
| Realized net, $0.02 roundtrip assumed for 0.01 lot = 1 oz | **−$539.42** | **+$921.62** |
| Gross profit / loss | +$401.13 / −$940.55 | +$1,173.84 / −$252.22 |
| Mean hold | 11.28 seconds | 27.01 seconds |
| Old-opposite rearm attempts | 2,408 | 1,332 |
| Original R9 logger's own entry events (OFFLINE comparator only) | 1,525 | 1,083 |
| Median source quote spread | $0.19 | $0.19 |

**This is a diagnostic independent simplified V8-style execution approximation, not actual Gold Hunter V8 or original R9 trade replication.** Its 2,662/1,693 replay trade populations differ from the archived R9 logger's 1,525/1,083 original entry events, since reconstructed historical V8 inputs and old R9's specific quality filters/timing are different. The high-level finding is **the same transparent STOP/OCO/rearm/trailing logic turns profitable on one historic GENERATED synthetic tick path and loses money on the distinct historic REAL quote path**. This makes a purely mysterious hidden-indicator explanation unnecessary to explain *some* of the synthetic/real discrepancy. It does **not** establish what caused the source feed differences, quantify full seven-month edge, or make the synthetic profits executable in a broker.

More important control: five identically specified alternate stop/rearm neighborhoods were rerun independently on both archives; **all five REAL-path net results negative, all five SYNTH-path net results positive**. One entry per minute removes rearm churn but remains REAL −$254.78 versus SYNTH +$502.33, changing trade opportunity populations. This is mechanics × tick-path interaction, not proof of a causal alpha or portfolio winner.

## Original authenticated user-project Gold Hunter V8 behavior (READ-ONLY)

The preserved owner original MT5 tester order observations in [V8 clean-room reconstruction](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/v8-cleanroom-baseline/docs/V8_RECONSTRUCTION.md) at blob `18a4a429616bdfd867cb05de53035c756a5083c0` contain source prices/times:

- XAUUSD M1, 0.01 lot, input GapPips=50 ≈ $0.50 *TOTAL dual stop band*, StopLossPips=50 ≈ $0.50, TrailPips=20 ≈ $0.20, trailing ON, Magic=5555; DailyProfitTarget=100 semantics **not established**.
- At `2026-01-02 01:00:00`, SELL STOP 4324.12/SL 4324.62 and BUY STOP 4324.62/SL 4324.12. On sell execution the other is canceled. After the short exit 01:00:06, only the original 4324.62 BUY boundary is rearmed, and fills at 01:00:20; no recentered bracket.
- At 01:01, fresh BUY 4329.31, SELL 4328.81; first buy fills, then after its exit the original sell bound is rearmed. 01:02 resets to a NEW bracket. This supports an **M1 boundary owner and within-minute alternating finite-state machine**, not an empirically proven EMA/RSI/VWAP/ATR secret.
- Historical owner's V8 MT5 reference summary: 308,763 trades Jan–Aug 2026, 75.72% winning, PF ~8.45, average hold ~25s. The archived tester *fingerprint* is not live, REAL Coinexx proof or independently replicated by BETA. August market ticks **never opened** for BETA.
- Historical reconstructed V8-style MQL5 source [V8 baseline](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/v8-cleanroom-baseline/Experts/GoldMuwahahaMiner_V8_Baseline.mq5), blob `628f128d728531f8d80a01858777d167450f69b5`, is a clean-room educational historical implementation, NOT the proprietary source. R9 later incorporated an observable S1 efficiency/volatility/session/spread detector and tighter 30 Hunter-pip band, 3-pip trail, 10-pip trail activation, 30sec max hold, 3 rearm max in [old R9 source](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/mt5-r9-hybrid-gate-certification/Experts/GoldMuwahahaMiner_R9_HybridGate.mq5), blob `7eecb5f1947017a01ce85b2520725de54749e523`. These read-only sources establish research ancestry, **not** endorsement or immediate code imports to BETA.

## Public independent evidence and authenticity limits

1. [ForexEALab Myfxbook Gold Hunter V8 demo](https://www.myfxbook.com/members/ForexEALab/gold-hunter-v8-ea-mt5/11981314): JustMarkets 1:500 DEMO system, 12,982 trades, 3s mean hold, displayed PF2.54 and 0.01 lots/trade. Its update is from March 2026. It is a third-party track record, NOT Coinexx fills, source code or a guarantee that it is the same V8 build.
2. [EA settings reseller](https://eafxstore.com/product/gold-hunter-v8-ea-mt5/) corroborates input labels 50/50/20 and trailing, but has no original strategy source.
3. [Another V8 listing](https://yoforex.org/gold-hunter-v8-ea-v1-0-mt5-review/) claims H1 EMA200, M15 pinbars, RSI/ATR20 and VWAP; [another package](https://fxprisma.com/products/gold-hunter-v8-mt5-no-dll) claims discretionary H1/M15 regimen, news shield and few daily trades. They conflict with each other and the owner order sequence. No hidden H1/oscillator system is authenticated, and variant/version conflation is plausible. Do not elevate these vendor statements to BETA rules without genuine transparent reconstruction and tick proof.
4. [Official MQL5 OCO/order-strategy finite-state reference](https://www.mql5.com/en/articles/495), [Japanese trailing/OCO article](https://www.mql5.com/ja/articles/11281), [MQL5 server stop/freeze specifications](https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants), [OnTick coalescing](https://www.mql5.com/en/docs/event_handlers/ontick), [CopyTicksRange](https://www.mql5.com/en/docs/series/copyticksrange) and [OnTradeTransaction](https://www.mql5.com/en/docs/event_handlers/ontradetransaction) provide publicly reproducible implementation principles, NOT V8 proprietary algorithms.

## BETA034 complete initial 17.5-day test and spread/source reason

BETA034 independently processed **4,205,709 ORIGINAL ordered Dukascopy XAUUSD Bid/Ask ticks**, Jan1 00UTC to Jan18 12UTC, **20** modular state-aware lifecycle settings over BETA033 fixed original-event research population AND **15** independent V8-inspired M1 STOP/OCO/rearm FSM settings (distinct entry population). Both five-family sweeps completed as genuine parallel research cases. **Zero out of 35** met the owner's >10% matched-initial economic and risk gate; zero advanced to Jan–Jul, zero were profitable. Research best matched one-position lifecycle PRIORITY_TRAIL_3 realized **−$10,247.41 vs fixed BETA033 −$10,375.74** (1.237% loss reduction); absolute predecessor-winner event preservation only 74.7%, fails other acceptance test. All literal and spread-adjusted original V8-inspired independent FSM cases on Dukascopy net negative.

A **critical execution incompatibility**: at 14,174 BETA033 Dukascopy research candidate entry quotes median original source Ask−Bid ≈ **$0.687**, only **193** (1.36%) had spread <= $0.50. A symmetric $0.50 band centered on mid cannot place *both* valid pending stops above Ask and below Bid when Ask−Bid >= $.50. The literal stop rule on 17.5d Dukascopy quote stream produced only 43 actually closed positions and **14,956** rejected new-minute brackets. A deliberate broker-safe wider band+stop variant produced 47,745 closes at **−$34,921.56**, but it is **not equivalent to the nominal V8 input**. The original Coinexx R9 Jan2 REAL/SYNTH logger entry-spread medians were both about $0.19/$0.18, allowing more feasible nominal bands.

In a matched 13,395-trade prior BETA033 original Dukascopy candidate ledger the exact quote-side PnL accounting identity was: pre-cost signed midpoint path **−$490.70** − actual two-sided spread cost **$9,617.14** − assumed commissions **$267.90** = **−$10,375.74**. Spreads account arithmetically for ~92.69% of that *absolute modeled loss*, but the pre-cost edge is ALREADY NEGATIVE. A hypothetical fixed-$0.20 spread with unchanged historical timestamps is **NOT executable** because real stop triggers, trade selection and account occupancy would differ. Never call a synthetic spread-cost sensitivity a validated profitable backtest.

## The semi-working theory we can independently reconstruct

**Anchor:** the original V8 historical STOP/OCO/opposite-boundary M1-rearm finite state execution mechanism. Do NOT add every seller's unsupported indicator. A BETA adaptation may comprise a *separately validated* state-dependent owner:

1. **BROKER_FEASIBILITY**: true Ask/Bid, min stop/freeze and quote age -> either place a valid bracket or `NO_ORDER`; never impossible bracket filling.
2. **AUCTION/M1 OWNER**: freeze original M1 bracket identifier/levels, confirmed M1/M5 pivot and age, number of touches, accepted-body break vs wick-only first sweep; separate newer M15/H1 context from exact execution direction.
3. **ACTION ROUTER**: `FAST_BREAK` if structurally accepted + short observed impulse, `LEVEL_RETEST` only on true previously confirmed price level acceptance+literal pullback+renewal, `SWEEP_FADE` on failed body acceptance+reclaim/shift, `PENDING` on unresolved event. Owner & specialist conditions may vary by state; NO teacher hindsight.
4. **HOLD POLICY**: probation after new fill, quote/event-time persistence and adverse-price recovery conditional on currently observed state, trend-runner if sustained; no future path labels or universal 1s early cut.
5. **EXIT POLICY**: accepted-trend runner trail, range-rotation profit capture, stop/timeout when confirmed failed ignition, dynamic adaptive trail activation. Preserve full chronological one-position account and own event-specific loss/blocked-opportunity costs.
6. **REARM POLICY**: after server **confirmed** close, only same-minute opposite original level is eligible; conditional rearm requires fresh as-of structural permission and no spread/cost toxicity. Reject unconditional ping-pong until it beats same-feed one-per-minute/lifecycle control.

The most important scientific hypothesis is **not “find the proprietary indicator,” but identify the observed-price-path and lifecycle state under which an M1 stop/OCO/rearm policy is sustainable on genuine broker ticks**. The BETA035 cross-feed result demonstrates raw quote-path dependence *even when the high-level rule and typical spread are nominally similar*; conditional attribution needs a later verified paired event-by-event comparison and exact broker fill constraints. This proposed composite is NOT a tested winner and is not an approved EA.

## Reproduction, QA and acceptance

- Quote replay source `BETA035_COINEXX_JAN02_V8_QUOTE_STREAM_CROSSCHECK.py` / output `BETA035_COINEXX_JAN02_V8_QUOTE_STREAM_CROSSCHECK_RESULTS.json`, **5 identical FSM conditions on REAL and SYNTH**. Each performs full original logged quote sequence **only**, never uses logger `event` as a decision; its own original entries are counted solely as offline comparison. Strict source-order time, `BuyStop` observed Ask crossing, `SellStop` observed Bid crossing, OCO, current real Bid/Ask exits, $0.02 roundtrip, 1 ounce 0.01 lot assumed, no original broker slippage or partial fills. REAL archive SHA256 `6bb8d01f928e5a06f864b87c274f2916c3a6554a2352208191830d685e28655d`; SYNTH SHA256 `8d1d3bb796686b284b1b6136f7fbd22db270b2f5229268c010a68ab6d885b2c7`.
- BETA035 independent QA **81/81** source identities, observed quote timestamps, quote-side GP+GL=Net, timeout vs stops accounting, 5 same configurations per feed; BETA034 QA **222/222** original source and 35 numerical screens. **303 checks from different QA programs; NOT full source-equivalence or MQL5 parity.**
- BETA033 full 17.5d fixed-parent & BETA034 V8-inspired FSM are DISTINCT TRADE POPULATIONS and comparisons cannot legitimately share a percent loss denominator. BETA035 Jan2 REAL/SYNTH feed replay is a diagnostic, not the user's original 17.5d screening admission or 7-month profit result.
- All January source periods previously studied. The complete original R9 REAL/SYNTH unselected 17.5d paired logs are not locally present; source 149-day full original alignment is incomplete. No BETA015 $100k funded account test. Full 17-layer BETA005 feature parity still incomplete. No official BETA `.mq5` written and no owner authorization inferred. August SEALED and no August data opened.

**Decision:** NO PROMOTION. Preserve observed V8 order-state architecture and raw original Coinexx crossfeed contrast as key forensic evidence; stop implying the ~87% R9 SYNTH outcome is reachable by small indicator tweaks on structurally incompatible Dukascopy quote spreads. Future effort should be concentrated on original-feed exact tick action+hold+exit attribution, quote validity, and new state-conditioned owner specialist systems with >10% proper matched original-source test performance before Jan–Jul extension.