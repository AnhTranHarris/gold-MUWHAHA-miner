# GRID-0108 — Grid-only dual hourly/daily opportunity research
**Date:** 10 October 2026 | **Branch:** `delta-A-alpha` | **Scope:** Creator-grid virtual opportunity clock only; NO session/MTF/Vertical Grid funded execution

## Verified in original raw XAUUSD tick replay

Original Dukascopy Jan–Jul 2026 raw Bid/Ask replay source **57,527,562 chronological ticks** (Jan 9,135,062; Feb 7,538,339; Mar 9,433,179; Apr 7,470,570; May 8,333,165; Jun 8,201,406; Jul 7,415,841), no rewriting native spreads; source GZ input hash June `34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2`, July `e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7`. Source hashes for Jan–May remain fixed in J0107.

Two NEW research validation pre-registrations committed to GitHub **before examining June and July source inputs**, respectively:
- `research/delta_a_alpha/grid/GRID_0108_JUNE_LOCKBOX_PREREG_HOURLY_VS_DAILY_GRID_ONLY_20261010.md` GitHub commit `7aa1b17757b1552653e39ad2bde28d188363f0c7`.
- `research/delta_a_alpha/grid/GRID_0108_JULY_PREREG_INTRINSIC_PRECISION_TIER_20261010.md` GitHub commit `50e20a3c9bad6001492acf2d5b2e0af001e235ec`.

## Original fixed grid vs high-motion vs new precision roles
At every **as-of** observed quote event, source spread `s=Ask-Bid`, virtual grid gap `G=max($0.75, 1.5*EWMA_spread_alpha_0.001)`; grid anchor moves on physical tick quote crossing and emits no more than one virtual event per 7 seconds. No actual position, account, martingale/risk exposure or session-based decision is involved.

- **Broad supply lane**: K5≥2, with `K5=|mid_now−mid_prior_known_at_or_before_t−300sec|/max(s,$0.10)`, retains event quantity. July 28,593 shadow events, January–July **297,947 raw shadow events**, compared against frozen 219,342 *monthly summed* R9 SYNTH positions. This does NOT establish daily QUALIFIED executable 75% coverage.
- **High-motion lane**: K5≥4 (subset), January–July **218,132 raw events**. This improves *chance of a sufficiently large future price movement*, not signed profitable direction.
- **New hourly precision overlay**: K5≥4 **AND** observed `s/G≤0.65`. Jan–Jun DEVELOPMENT selected the .65 threshold, July newly frozen holdout. July overlay 7,140 events, Jan–Jul 80,565; it must be an OPTIONAL annotation to the broad lane, never a replacement. It is quote-friction normalization, not a prediction of BUY vs SELL and not permission for a funded grid.

## Seven-month paired metrics — what "all days" actually means
Outcome only for **offline scoring** at the first native Dukascopy quote at/after +120sec (max 10sec late): `|future mid−event mid|>2×event spread`. Daily paired comparison: >=100 future-valid original-grid events and >=1 selected event. Hourly baseline: >=20 future-valid original-grid events, precision-tier support additionally >=5 events, UTC source hour grouping; **no time-of-day behavior in the grid itself**.

- Fixed original **K5≥4** improved the above **relative-spread future-motion** percentage on **150/150 eligible Monday–Friday UTC dates**, Jan–Jul, *including July 23/23 from a genuinely independent pre-registered source*. This is NOT 150 profitable days or a certified 75% daily funded opportunity rate.
- Original high tier across 3,332 baseline-eligible weekday UTC hours: 3,214 supported hours; **1,943 showed higher future motion capacity**, 60.45% among its supported hours, and 58.31% of all eligible baseline hours.
- New .65 precision overlay: **2,780 supported weekday hours** of **3,332 baseline-eligible hours**; **2,044 improved**, 73.53% *among supported* or **61.34% of all baseline-eligible hours**, counting 552 unsupported hours as NOT achieved. On the pre-registered July holdout specifically: **239/361** supported hours improved (66.21%), but only **239/492** baseline-eligible hours, 48.58%. **It did not achieve all-hours success.**
- Both fixed K4 and precision overlay passed **150/150 weekday daily relative-spread motion-capacity tests**, not trading/PnL days.

| Month | Raw broad K2 events | K4 high-motion | Precision overlay | Original R9 SYNTH entries | K4 weekly-day lift count | Precision supported hourly lift |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 42,782 | 31,674 | 12,118 | 27,980 | 21/21 | 259/363 |
| Feb | 41,233 | 30,190 | 11,449 | 33,523 | 20/20 | 309/391 |
| Mar | 63,870 | 49,826 | 15,391 | 40,985 | 22/22 | 325/450 |
| Apr | 38,774 | 27,536 | 9,175 | 31,758 | 21/21 | 283/378 |
| May | 39,185 | 28,345 | 12,299 | 28,913 | 21/21 | 299/394 |
| Jun | 43,510 | 31,838 | 12,993 | 31,801 | 22/22 | 330/443 |
| Jul **new July lockbox** | 28,593 | 18,723 | 7,140 | 24,382 | 23/23 | 239/361 |

## Anti-tautology falsification control
The quoted-spread outcome `|future change|>2×s` **becomes inherently easier for low-spread events**, so a low-spread overlay can appear strong without underlying price information. Frozen July prereg therefore also required price movement > **fixed $1.50** and **fixed $2.00**, independent of the current spread:
- July baseline fixed-$2 movement: **32.9463%** of events; K4 **39.2872%**; precision **38.8850%**. K4 really does stratify toward larger *absolute* movements. The precision overlay does **not** improve this fixed-dollar metric over K4 in July (and not consistently in development months), even though it raises the relative-spread metric to **60.9189%** vs K4's 57.5016% and baseline's 50.8067%.
- July mean absolute future 120sec move: baseline $1.8539, precision $2.0994. This difference reflects the selected subset; price move does NOT imply trade profitability.
- July precision creator-style directional 120sec after-native Bid/Ask markout averaged **−$0.5037 per virtual signal** *before hypothetical commissions/slippage*. There is no positive signed direction strategy to promote; no broker fills, trailing/hold or portfolio PnL tested. The alternative continuation sign also is not certified profitable.

## Additional causal hypotheses challenged (not promoted)
Jan–May grid-only development searched bounded as-of event flow (30/60-second crossing count), price travel normalized to quote spread, recent short/long price displacement agreement, quoted spread-to-grid ratio, prior mature 60min event outcome feedback with 130sec timestamp embargo, and deduplication. Such hypotheses were evaluated as separate strict precision annotations, never session routers. The June frozen delayed-feedback threshold **did not** improve the percentage of positive UTC hours over original K4: K4 294/474 supported weekdays, dynamic 275/460, despite a higher pooled movement-capacity percentage. The July .65 tier passed the *relative-friction* hourly improvement on 239/361 supported hours (not universal), and failed to improve fixed-$2 capacity beyond the base high tier. All negative evidence retained in daily/hourly CSV, JSON and code: not presented as a profitable discovery.

## Scientific and deployment boundary
Our R9 goal of >=75% **same-day qualified and broker-executable opportunities** is **UNTESTED**: virtual candidate count alone does not satisfy it. Monthly actual filled-trade <=175% cap not assessed as no orders exist. The original seven-month R9 SYNTH reference is 219,342 CLOSED entries, not a target to memorize exact direction. $100,000 only a future **hypothetical** funded research account, not involved here; preferred $100–$300 commercialization later. Zero actual entry orders, no balance/equity/PF, no 0.01-lot fills, no margin, no leverage or stop/exit. Broker UTC/market sessions/MTF and L1–L7 **not activated**. July is now inspected and cannot be reused as blind holdout; August remains SEALED.

**Promotion verdict:** retain original K4 as validated pre-session movement-capacity annotation with high daily consistency; preserve broad K2 for raw event supply; retain spread/gap<=.65 only as an *experimental* friction descriptor because it sacrifices density and does NOT consistently add true fixed-dollar movement quality over K4. Do not promote an hourly-profit system. Future research requires after-fee correct-direction classification and realistic latency/exposure checks before enabling first session-specific quality layer. All seven-month hour- and day-level records, including negative/unsupported periods, are included in packaged evidence.

## Public, reconstructible mechanistic references
- MetaQuotes constrained restartable grid regime study: https://www.mql5.com/en/articles/21833 ; borrow bounded state-cycle ideas for future research only, not its variable/martingale sizing.
- MQL5 market microstructure regime diagnostics: https://www.mql5.com/en/articles/22940 ; features are not evidence of XAUUSD edge.
- Event-based labeling/meta-labeling caveats: https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy-triple-barrier-method/ ; precision filters cannot conjure positive expectancy absent profitable direction.
