# GRID0246 — Grid-first recover-and-integrate scientific checkpoint (2026-10-12)

Status: **engineering/research only, NOT SCIENTIFIC PROMOTION**. Active and ONLY branch: `delta-A-alpha`. Immutable scientific checkpoint: **J0183**. **No Vertical L1–L7 source modified. EA trading OFF. August 2026 SEALED.** No Martingale, DCA, increasing losing lot, static month/date strategy selectors, fabricated fills or future quote information. Owner-frozen original 10-section V1 whitepaper and ratified owner chat retain authority. Later owner instruction directs **grid strategy first** until grid profitability and R9 daily/monthly performance are meaningfully progressing.

## Concrete current-turn changes

1. `v1_grid_strategy_source_router.py`: one coherent PRE-L1 grid-source router combining existing `MultiSpeedGridGenesis` (actual original rolling 48 completed active H1 parent + M5/S1/M1 virtual first-touch) with `FundedGridCampaign` (last **acknowledged** fill anchor). Earlier multiscale source receives priority; no canonical source is replaced. One emitted quote candidate per UTC millisecond, paid proposal collision canceled rather than silently earning fill credit; frozen grid gap per completed H1; state is continuous. **No downstream Vertical entry authorization or invented funding.**
2. `v1_grid_renewal_signature.py`: **original** `apr_campaign_transition_map_136t0_fast.py` causal previous-child research buckets restored exactly as pure functions. `PBU`: missing -1; <=0 0; (0,.5) 1; [.5,1) 2; [1,2) 3; >=2 4. `HBU`: missing -1; <=30 0; <=60 1; <=120 2; <=180 3; <=300 4; >300 5. **Critically, original P is April136 normalized research P, NOT automatically broker cash USD**. This implementation refuses to bucket BROKER_USD_CASH under original P thresholds; recorded actual cash and hold bucket are independent. No April outcome-derived whitelist is copied.
3. `test_v1_grid_strategy_source_router.py`, `test_v1_grid_renewal_signature.py`: **16 new deterministic QA tests** (9 router, 7 buckets) plus **13 prior funded-campaign tests = 29/29 PASS**, including H1 turnover without losing filled inventory, no duplicate quote, paid-before-child timing, frozen levels, no ghost fills, wrong profit units and bucket boundaries.

## Original immutable real-source April replay

Input `/mnt/data/XAUUSD_DUKAS_2026_04_ticks.csv(3).gz` read-only. First **2,400,000** ordered original Bid/Ask quotes, with **913,931 warmup quotes** until actual 48 *completed active H1* bars. 1,486,069 post-warmup quotes. Local recovered GRID0241 parent source used for this exact replay and had a **known earlier byte mismatch** with live GitHub `v1_creator_grid_genesis.py` (source local Git blob `650f34e05a7f918c10d79292f38ee77a061db439`, canonical `df651bb7f98b48453636a2a773cf528ad0dd9bb8`); this replay **does not certify canonical repository all-module parity**.

| Stage | First 2.4m April source quotes |
|---|---:|
| Previous original S1/M1/M5/native raw G0 offered | **74,856** |
| Previous raw G0 preserved after router | **74,856** |
| Additional independent creator fill-anchor virtual proposals selected | **57** |
| Creator fill-anchor proposals seen before priority arbiter | 98 |
| Creator proposals colliding with old G0 | 41 |
| Deduplicated selected grid source total | **74,913** |
| Incremental supply | **+0.0761%** |
| Broker-ACKed paid fills/closes | **0 / 0** |
| Certified account-cash net, PF, daily and monthly R9 ratios | **NOT ESTABLISHED** |

The 57 are **unfunded G0 source offers**, not execution proceeds. The router is currently an **additive pre-L1 research module only**, not wired to the original production `v1_four_session_architecture.py`. Never mark 75% same-day qualified count or 80% same-day/month broker net as passed. This tiny improvement is an engineering preservation outcome, **NOT a material research breakthrough**.

## Research history recovered over multiple distinct passes

| Original primary artifact | Durable insight | GRID0246 state and next action |
|---|---|---|
| Original OmegaFX/MegaJoctan `grid_bot.py`, creator transcript, GRID0220/0238 | Rolling 48 **ACTIVE COMPLETED** H1 highs/lows, last **CONFIRMED FILL** anchors per side, unchanged grid rung until next completed auction; prohibit creator physical averaging and Martingale | **Partially integrated:** 0241 virtual + 0245 paid-anchor now composed, as one grid-source stage. Full original fill/active-inventory parity requires executable order gateway and canonical code replay. |
| GRID0240/0241/0242 | Previous M5 fine and S1/M1 source; quote arbiter prevents rejected proposal blocking a stronger later one | **Preserved existing S1/M1/M5.** GRID0242 is a downstream quality/cooldown fix; defer until grid economics warrant L1–L7 activation. |
| April original 136T0 Python & 136T2, 136M2, 136Q | Previous **closed child** P/H at actual next entry; rule / depth / prior P bucket / prior duration bucket. Exact 136Q plain rule-depth lookback experiment was negative. April positive whitelist was hindsight-selected; high depth potentially toxic | **Exact causal bucketing integrated as research observation**. Seven creator renewal rules, physical source owner IDs, and cost-normalized P conversion still need source recovery. No April whitelist or frozen "max profitable depth" put into live code. |
| March135 original `daa_march_vertical_grid_replay_135.py`, GRID0173/0174/0183 | Original NAT/HV2/ASIA/WDQ parent families, distinct holds and risk. March retained positive selected-source quote repricing and cap16 results, but original cells are retrospectively selected | **NOT recovered as independent entry-time generator**. Need exact original original-source arrays and method implementations, with true real-quote prices at entry and as-of eligibility. No transplant of prior profit cells. |
| April136G and GRID0175/0234/0238 | Original native, HIGHVOL, ASIA, RECOVERY and 136S0 paid renewal family are important; original 72 archived portfolio snapshots reproducible, April selected source cap32 scored positive quote net | **NOT certified clean forward grid strategy**; reconstruct source admission and paid ACK causal genealogy, avoid selected-April outcome leakage or arithmetic stacking independent sleeves. |
| GRID0116, 0186, 0189, 0232, 0243 | Raw signed short-horizon edge below spread+fees; dozens/hundreds of new directional variants and simple source size/burst M1 ideas were negative. Original R9 actual workbook 219,342 closes, +$309,122.85 deal cash | **Failed controls retained**. Avoid another generic fade/continuation 10–180s sweep. Source must show AFTER COST signed displacement before adding complexity. |
| GRID0177J/K | Frozen completed M5 true-range hourly rung can restore weak-hour raw *source* coverage, but associated source-selected after-cost economics were negative | **Potential separately measured source** only if it beats after-cost control, not just more source coverage. Existing G0 first-touch untouched. |
| GRID0185/0191 | Conditional 30/90-minute HARVEST/RUNNER, earned winners, and full quote tick equity; positive quote-proxy but low trade count and not broker cash | **Defer lifecycle/funding to Vertical later**, retain as controls. Does not provide R9-like high-velocity engine. |

### Targeted community-research / creative hypothesis queue — NO performance claims

1. **Independent economic grid permission BEFORE L1:** at a genuine observed crossed rung, compare *completed prior M5/H1 anchored displacement* to the CURRENT half-spread entry burden, plus historically measured exit quote cost and delayed-fill stress; preregister energy-vs-spread bands. Must beat the original GRID0116 fee drag at high volume on untuned contiguous months, no future returns as features. Public source inspiration: [MQL5 finite restartable grid](https://www.mql5.com/en/articles/21833), [MQL5 original grid risk](https://www.mql5.com/en/articles/8390), [MQL5 Japanese ATR range role](https://www.mql5.com/ja/articles/16213). **Hypothesis, not accepted edge**.
2. **Finite creator campaign / sibling lineage:** previous actual acknowledged entry anchor, fully paid close ID, consumed credit, previous paid-duration and verified original rule/depth, current quote and preceding completed H1. No partial close inferred, no loss multiplication. Source `apr_campaign_transition_map_136t0_fast.py` source-P buckets now exact; remaining challenge is reconstructing seven 136S0 source rule identity and normalized P conversion rather than using hindsight-selected April cells.
3. **Unserved-hour source repair (not the same as losing-funded-hour rescue):** compare mature static true-range source's quotes and existing G0 source side-by-side in original hour denominator; require as-of independent quote event, later delayed Bid/Ask entry, no moving thresholds; quote-generating alone is not success (GRID0177 after-cost negative). Preregister real account-level daily/weekly economics before promotion.
4. **Broker parity instead of false model precision:** reassemble original MT5 R9 SYNTH and REAL ticklog parts, verify Coinexx cash contract, spread/slippage/UTC-server clock, map exact original source quote to broker quote and execution; the original MT5 R9 REAL loss vs SYNTH gain warns against using simulated spread assumptions as fills. This is *data/QA work*, not a strategy parameter.
5. **Preexisting public source knowledge is a falsification guide, not predicted profits:** finite grid cycles and time/risk expiration (`mql5.com/en/articles/21833`) cannot by themselves solve bad entries; community r/algotrading quote-side and latency discussions reinforce mandatory slippage/fill sensitivity, not secret profitable entry logic.

**Research falsification/promotion discipline:** Each candidate must be expressed as complete reproducible code, a preregistered original tick dataset, a changing-only-one-mechanism ablation vs unchanged G0 + prior accepted specialist controls; no month as runtime signal, no future label/fill. Test full contiguous active-day performance with 48-H1 warm history, exact broker clock/day, account cash, quote latency, gross loss/PF/DD, fill/capital constraints. New idea that improves raw source 10–20% but not comparable daily/monthly cash outcomes remains RESEARCH FAIL, not promotion. No current GRID0246 funded performance pass.

## Archival and runner instructions

- Live code remains GitHub `delta-A-alpha`, no new branch. Files:
  `research/delta_a_alpha/implementation/v1_grid_strategy_source_router.py`,
  `v1_grid_renewal_signature.py` and both respective test files. Reuses prior `v1_grid_multiscale_stack.py` and `v1_grid_funded_campaign.py` unchanged.
- Original 136 source: historical read-only branch `delta-A-alpha-april-136-complete` under `research/delta_a_alpha/monthly/april_2026/`; older original March under `delta-A-alpha-march-135-complete`.
- Local script `GRID0246_REAL_TICK_G0_PARITY_REPLAY.py` and original raw source present in original ChatGPT environment. `python -m unittest -v test_v1_grid_funded_campaign test_v1_grid_strategy_source_router test_v1_grid_renewal_signature` passed 29.
- **Prioritize missing March135/HV2/ASIA native G0 generation + April136 causal owner ID / paid close ledger**. Do not restart failed simple fade models or activate Vertical L1–L7 without economic proof. The monthly and same-day 80% R9 SYNTH performance question remains FAIL/UNPROVEN.
