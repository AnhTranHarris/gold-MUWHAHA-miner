# AR1 JANUARY R2 — ATLAS-DRIVEN REVERSE-ENGINEERED OBSERVATIONAL ACCOUNT-RISK POLICY AND FULL JANUARY SELF-PROOF
**18 November 2026 | JANUARY 2026 ONLY | R9 FIXED TRADES × ORIGINAL COINEXX REAL TICKLOGGER | OWNER-FROZEN S100 UNCHANGED**

**Certification conclusion:** Source replay, quoted-position risk telemetry, S100 tiers, original R9 booked accounting, and serialized quantitative market-pressure model are **self-tested**. The market-pressure channel demonstrates January historical discriminatory ability; the R9 losing-trade prediction channel demonstrates insufficient discriminatory ability and is **NOT authorized as a protective trading rule**. No account-wide actual Coinexx equity protection, trade veto, alternative stop-execution or live deployment is claimed. This is a **completed January observational-policy build and self-proof**, NOT a certified execution-risk governor.

## 1. Source-custody contract and source exactness
- **R9 SYNTH fixed and unmodified:** all 27,980 January trade identities, entry/exit second marks, chronological cycle relationship, direction, fee-inclusive original realized results, original $100 book. **Never use R9 synthetic intraday movement or synthetic interim equity.**
- **Coinexx REAL TickLogger:** all 7,699,274 original January timestamped REAL Bid/Ask updates in the 21 original gzip source files, used read-only; 2,272,602 real quote observations are attributed to the conservative January R9 fixed observation windows. Research surrounding windows outside an open trade are market state only, **never attributed to that trade’s intratrade MAE/DD**.
- **Source-index millisecond convention:** the R9 tester reports seconds, not exact fill milliseconds. We reuse the original existing AR1 R3 mapped `open_ms` and inclusive `close_ms` windows, which are conservative source-defined trade observation intervals, not asserted exact fills. At coincident boundary timestamps the original scanner assigns a quote to the earlier still-open position, not both. A first Python pass correctly failed quote-count parity on this ambiguity; corrected by matching the original window ownership rule and independently confirming all rows. No R9 entry or exit was moved.
- **Full Python tick parity:** 27,980 original trades, 27,947 with at least one inside-window quote, 33 with none, 27,752 strict; **zero mismatches** in actual quote counts, price MFE, price MAE or price high-water DD against the original independent C++ scanner across the entire January set; not just six hand-picked witnesses.
- **Original booked accounts:** $100.00 + $41,520.82 R9 fee-inclusive historical net = $41,620.82 historical ending BOOK; all six pre-entry original R9 realized gross-negative rolling windows (1/5/15/60/240/1440 minutes) exactly reverified, no future exit included in an entry-state metric.

## 2. ATLAS FIRST: what the surrounding 3,030 real-tick windows actually showed
The 240 existing Atlas witness rows selected the targets before formula fitting. All witness types—including account peaks, loss clusters, source quality exceptions, highly exposed profitable R9 legs, early capital stress, 27-family first examples and S100 tier transitions—remain represented. The C++ scanner then traversed the same original January 7,699,274 ticks and calculated 3,030 10-to-60-second market-context intervals around 505 source row/entry or DD-trough anchors (240 paired target/control records; some target rows have several distinct Atlas types). Matched low-DD controls are **retrospective diagnostic contrasts only**; their later outcome is NEVER an online predictor.

**Peak Intrahold Dd:**
- `mean_spread_USD_bin2` median REAL target **1.163** versus matched control **0.708**, target greater in **85.0%** of pairs (n=20).
- `mid_range_USD_bin1` median REAL target **28.038** versus matched control **9.758**, target greater in **90.0%** of pairs (n=20).
- `quote_count_bin1` median REAL target **466.000** versus matched control **419.000**, target greater in **75.0%** of pairs (n=20).

**Original Negative Leg Highest Coinexx Dd:**
- `mean_spread_USD_bin2` median REAL target **0.497** versus matched control **0.551**, target greater in **55.0%** of pairs (n=20).
- `mid_range_USD_bin1` median REAL target **10.410** versus matched control **7.022**, target greater in **70.0%** of pairs (n=20).
- `quote_count_bin1` median REAL target **431.000** versus matched control **399.000**, target greater in **75.0%** of pairs (n=20).

**Loss Cluster 60Min Preentry:**
- `mean_spread_USD_bin2` median REAL target **0.191** versus matched control **0.193**, target greater in **30.0%** of pairs (n=20).
- `mid_range_USD_bin1` median REAL target **2.310** versus matched control **2.375**, target greater in **50.0%** of pairs (n=20).
- `quote_count_bin1` median REAL target **285.000** versus matched control **283.000**, target greater in **70.0%** of pairs (n=20).

**Resulting mechanism selection:** observed major intratrade giveback clusters coincide strongly with elevated *previous* real quote travel/range, tick bursts, and wider spread. Booked-loss clustering is a different mechanism: the same price-state contrasts are weak at its R9 loss-cluster witnesses. Therefore the resulting research policy **separates real-tick market pressure from deterministic original realized account-loss pressure** and explicitly refuses a single generic ATR/stop/sell filter.

## 3. January AR1 numerical policy actually constructed
**Causal market-pressure forecast (fitted January history, not predictive certification beyond January):**
\[ p_{U25}(t)=\sigma\left(\beta_0 + \sum_{j=1}^{12}\beta_j\frac{f_j(t)-\mu_j}{s_j}\right),\quad \sigma(x)=1/(1+e^{-x}). \]
The event used to fit this *observational* model is a directly observed real Coinexx high-water-to-trough giveback using at least 25% of that trade’s **unchanged S100 dollar gap**. All 12 features are causal at the original entry:
`log1p(10s quote updates)`, `log1p(60s mean spread)`, `log1p(10s midquote travel)`, `log1p(60s travel)`, completed M1/M5 ATR14, `log1p(S100 gap)`, quote-intensity×spread interaction, last-quote age, as-of prior R9 60-minute booked gross losses, original booked HWM deficit, and completed M5 ATR/S100 ratio. The exact **12 coefficients, 12 standardization means/variances, training medians and intercept** are serialized in `JAN_AR1_REVERSE_ENGINEERED_NUMERIC_FORMULA_AND_CROSSDAY_DIAGNOSTICS.json` and reproduced without sklearn by `07_ar1_january_observational_policy.py` to probability error below 7×10^-16 across **all 27,980** January R9 rows.

**January parameter audit — standardized coefficient magnitudes** (these are fitted model parameters, NOT stop thresholds):
- `ln_S100_gap`: **-1.3165**
- `ln_10s_travel`: **+0.9174**
- `ln_60s_travel`: **+0.6256**
- `ln_M1_ATR14`: **+0.3592**
- `ln_60s_spread`: **+0.2694**
- `spread_times_quote_intensity`: **-0.2036**
- `ln_asof_60m_gross_losses`: **-0.1421**
- `ln_M5_ATR14`: **+0.1247**
- `ln_10s_quote_updates`: **-0.1246**
- `ln_quote_staleness`: **-0.0951**
- `R9_preentry_hwm_drawdown_pct`: **+0.0580**
- `ln_M5_ATR_per_gap`: **-0.0021**

**MT5 context proxy audit:** completed-M5 Heikin-Ashi direction/run/body and Fibonacci position/range were evaluated in a full augmented 17-feature model, **not assumed useful**. Both combined out-of-day mean Brier and mean average precision worsened compared with the 12-input baseline; therefore HA/Fib are **research diagnostics but are not selected inputs** to January R2. Likewise the R9-negative-leg forecast is retained only as a *falsification diagnostic*, not a deployed risk score. No unmeasured or future fib pivot is an input.

**Independent booked-capital module:** `booked_drawdown(t)=max(0,HWM_booked_so_far−B_before_entry)/HWM_booked_so_far`; `gross_losses_delta(t)=sum max(0,−net_j_R9)` for original R9 trade exits strictly before entry and inside the prior delta window, delta ∈ {1,5,15,60,240,1440} minutes; `prior_negative_run` derived only from previously realized R9 outcomes. Original R9 recorded money is never replaced by Coinexx quote-side shadow book. This detects *already realized* capital damage without pretending to forecast future booked losses.

**Intrahold observation states (no actions):** `U(t)=Coinexx_quoted_high_water_giveback(t) / frozen_S100_gap`; record first real-tick crossings at 25%, 50%, 75%, and 90% of the existing approved S100 gap; a full-gap comparison is **only** an observed threshold witness, not a broker stop fill. Before entry, score risk probability; during the original fixed hold, update quote pressure at each original tick; at the original R9 exit, book only its unchanged R9 original fee-inclusive net. Unquoted windows have `UNKNOWN_REAL_TICK_PATH`, never zero risk. No order-opening, closing or entry suppression method exists in the policy module.

## 4. Full chronological January Python source-replay self-proof (not just a selected witness test)
| Acceptance / metric | Verified result | Status |
|---|---:|---|
| Unmodified original January trades | 27,980 / 27,980 | PASS |
| Observed original Coinexx REAL quotes | 7,699,274 | PASS |
| Attributed Coinexx quotes within original R9 source windows | 2,272,602 | PASS |
| Quoted vs unquoted exact windows | 27,947 / 33 | PASS — missing retained |
| Python vs prior C++ count, MAE, MFE and DD mismatches | 0 across all 27,980 | PASS |
| Booked R9 net and final balance | +$41,520.82 / $41,620.82 | PASS |
| Pre-entry rolling booked-loss as-of window mismatches | 0 across 6 windows | PASS |
| Frozen S100 tier mismatch across all January source rows | 0 | PASS |
| Serialized Python formula vs sklearn numeric differences | < 7e-16 | PASS |
| Observed 25% S100 utilization transitions | 930 | PASS — detected |
| Observed 50% S100 utilization transitions | 110 | PASS — detected |
| Observed 90% S100 utilization transitions | 7 | PASS — detected |
| Observed full frozen S100 touches | 0 | PASS — observed only |
| Originally R9-profitable trades preserved | 24,368 / 24,368 | PASS — no actions |
| Original positive-cycle companion legs preserved | 26,148 / 26,148 | PASS — no actions |
| Atlas witness rows with status and model score | 240 / 240 | PASS |
| 27×10 Atlas reporting cells | 270 / 270 | PASS |
| Live/paper capital protection effect | Not simulated | NOT CERTIFIED; outside observation scope |

**Historical day-blocked internal crosschecks (5 folds grouped by calendar day, without training on that held-out day; NOT a prospective forward test):**
- **Coinexx S100 utilization ≥25%:** 0.3008 average precision versus 0.0333 event rate (**9.02× baseline**); ROC-AUC 0.8882; Brier 0.0273. These are *retrospective January internal* scores; January full-fit is less independent.
- **Original R9 losing-leg probability:** average precision **0.1790** versus event rate **0.1289**, ROC-AUC **0.6032**. This is too weak to justify a trading veto or claim reliable loss forecasting. The **direct booked-capital-loss module** is retained instead.
- In the day-blocked January comparison, prioritizing the highest-scored 10% of strict traded windows identifies **575 of 925** observed U≥25% events (**62.2%** sensitivity), but the 2,776 prioritized windows include **2,539 originally R9-profitable trades**. This is a **high false-action cost** if anyone were to convert a monitoring score to an entry veto. No veto was implemented.
- The first *within-position* tick crossing U=25% preceded the final observed position DD trough by a median **1.101 seconds** across 930 quotes-qualified or flagged observations. This is useful detection but may be too late for execution protection in fast trades.

## 5. Atlas key historical zones — self-tested witnesses, before any trade action
- **R9 row 2** (`2026-01-02 01:01:18`, `A1__prior1_same`, S100 $4): original R9 booked net **$+3.05**, Coinexx observed DD **$3.32**
  - Fitted pre-entry pressure **0.5260**; source-quote U25 first crossing `1767315696207`; U50 first crossing `1767315697700`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.
- **R9 row 6433** (`2026-01-09 15:30:21`, `C2__second`, S100 $9): original R9 booked net **$+10.26**, Coinexx observed DD **$8.48**
  - Fitted pre-entry pressure **0.4600**; source-quote U25 first crossing `1767972623313`; U50 first crossing `1767972631011`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.
- **R9 row 11364** (`2026-01-15 13:54:41`, `N2__second`, S100 $9): original R9 booked net **$-0.54**, Coinexx observed DD **$0.74**
  - Fitted pre-entry pressure **0.0041**; source-quote U25 first crossing `-1`; U50 first crossing `-1`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.
- **R9 row 13930** (`2026-01-20 05:40:04`, `A1__other`, S100 $9): original R9 booked net **$+1.52**, Coinexx observed DD **$0.32**
  - Fitted pre-entry pressure **0.0006**; source-quote U25 first crossing `-1`; U50 first crossing `-1`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.
- **R9 row 26464** (`2026-01-29 17:28:03`, `B1__prior1_same`, S100 $23): original R9 booked net **$+8.35**, Coinexx observed DD **$0.00**
  - Fitted pre-entry pressure **0.9750**; source-quote U25 first crossing `-1`; U50 first crossing `-1`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.
- **R9 row 26488** (`2026-01-29 17:40:18`, `B2__second`, S100 $30): original R9 booked net **$+39.94**, Coinexx observed DD **$28.05**
  - Fitted pre-entry pressure **0.6520**; source-quote U25 first crossing `1769708423171`; U50 first crossing `1769708440303`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.
- **R9 row 27060** (`2026-01-30 04:14:22`, `B2__second`, S100 $30): original R9 booked net **$+17.97**, Coinexx observed DD **$25.92**
  - Fitted pre-entry pressure **0.4043**; source-quote U25 first crossing `1769746463526`; U50 first crossing `1769746467533`; original R9 exit unchanged. Alert classification does **not** rewrite this trade.

The 240-row witness self-proof CSV records *each* Atlas source point, risk type, causal pre-entry score, actual quote-crossing event timestamp, strict/lag/absent-quote status and time from first risk observation to DD trough. All 33 original January no-quote positions are retained; a probability proxy remains an estimate and does not fabricate actual ticks.

## 6. Profit preservation, negative clusters, and family-tier audit
- The entire original January account, all 24,368 individually positive legs, all 26,148 component legs of historically profitable cycles, all 3,606 losing legs and all six zero-result legs are retained. No policy simulation interrupts a first/second-leg recovery.
- Negative profit clusters are represented by the **as-of previous R9 exit ledger** (full original 1/5/15/60/240/1440 minute gross losses, booked high-water and repeated losing sequences), not by treating low Coinexx quote counts as an account-loss estimate. The original January longest consecutive losing-leg run remains **four trades totaling −$2.16**.
- 27 reporting families = 23 exclusive atomic groups + four A/B/C/D overlapping parent rollups; the 270-cell family×S100 policy selfproof table preserves the four parent groups for interpretation but does not double-count them.
- The frozen S100 $74 tier is unpopulated in January; its empty family cells are reported as lacking January evidence, not zero risk. No later-month data was introduced to fit January.

## 7. Quality-control findings and completed corrections
1. Original Python replay initially disagreed with R3 for one shared-timestamp consecutive-trade boundary. We reproduced the original C++ scanner’s ownership convention; the corrected full 27,980-row quote-count, MAE/MFE/DD crosscheck passed at zero mismatches. The original R9 times and TickLogger were never changed.
2. The first full formula code produced a boolean-type exception in an observational alert-label field. That computation was corrected, the full January formula rerun and every serialized probability independently verified without sklearn.
3. The initial Atlas neighborhood script inadvertently collapsed duplicated source rows belonging to different Atlas witness types during reporting. The witness-type mapping was corrected, preserving all 240 Atlas target records; the C++ tick windows were unaffected.
4. HA/Fib additions did not improve both day-blocked calibration and ranking; they were **not** included in the first January numerical model. This is an audited negative result, not a deployed indicator filter.
5. The R9 losing-leg forecast proved weak; it remains only a failed/limited statistical hypothesis. No protective loss-blocking rule was inferred from it. The causal already-booked R9 loss monitor is certified against source ledger instead.

## 8. Freeze and owner governance: exactly what is complete and incomplete
**COMPLETE / self-tested:** January Atlas-zone reverse-engineering, 3,030 surrounding tick intervals, numerical real-tick market-pressure formula, original booked-loss pressure formula, source-exact 7,699,274-quote Python replay, 27,980 trade path-parity checks, real-time quote-state transition detector, 240 Atlas witness selfproof, all 270 family×tier cells, independent formula runtime parity.
**NOT established / not approved:** guaranteed prevention of account ruin; loss forecast precise enough to justify future vetoes; executable Coinexx account equity, broker fills, slippage or portfolio self-funding; preserving all R9 synthetic profit after actual trade-altering risk operations. Such operations are **not** part of this owner-approved historical observation work. No MetaTrader EA files changed, no trade filters, no alternative exits, no forward test, no February+ training.

**Research policy identity:** `AR1_JAN_R2_ORIGINAL_R9_FIXED_COINEXX_REAL_TICK_OBSERVATIONAL_SELFTESTED_20261118`; S100 V2 **owner-frozen, unchanged**; AR1 protection execution **NOT FROZEN**.

### Source references
- Owner Atlas R0: https://drive.google.com/file/d/175yPSkvCBsY6cW0DRtTisjEYaOK3nhAn/view
- Previous January R1: https://drive.google.com/file/d/1uA_CeKCCmCt3YNjUDNwqU_onoaQUBpNH/view
- Frozen S100: https://drive.google.com/file/d/1yOOFHp08kLx4Y0g6qGWgadGcqbB8fLSO/view
- Original Coinexx TickLogger directory: https://drive.google.com/drive/folders/1NGQ15bZ962HuHjada2U-xpnecVudsOwG
- Original R9 fixed teacher archive: https://drive.google.com/file/d/1CC30szLw0_R9UpaRScPJZamgasqGjEsm/view
- GitHub R9 EA read-only source: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/mt5-r9-hybrid-gate-certification
