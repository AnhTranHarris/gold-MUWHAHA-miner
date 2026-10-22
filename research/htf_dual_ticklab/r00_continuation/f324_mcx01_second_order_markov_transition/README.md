# F324 M-CX-01 second-order bid/ask marked quote research — 2026-10-22

**RESEARCH ONLY / OWNER UNAPPROVED / ORIGINAL CHECKLIST REMAINS 17/39 HISTORICAL ACCEPTED, 22 OPEN.** M-CX-01 Coinexx January teacher still open, no MT5 trading authorization.

## Verified lineage and causal source

Parent F323 branch `carson/htf-r00-054-f323-mcx01-marked-regime-hazard-20261022`, commit `c929393be106e886404f66ddc313ffc5de9849fb`. Reuses accepted baseline UTC tick readers `ca4b58aec597174b6f6d18ab2f36cba6836e4f4c`; original F234 event t/side/truth/parent, no source or replay engine reconstruction. Current original source policy Coinexx Jan/Feb raw minus120min and Jun/Jul minus180min to UTC; Dukascopy native UTC. Only original eight registered 2026 Jan/Feb/Jun/Jul broker-month cells, frozen side and original 30–32s outcome. No new price data. April/March/May unopened in F324.

Original same-month fitted Coinexx January teacher: 345,365 events, 181,869 correct; 86,336 wrong/neutral vetoes, 5 correct losses (binary q .250), original 450-tree 255-leaf 93-feature model. **This is hindsight overfit, NOT a deployable target prediction.**

## Distinct F324 mechanistic pilot

31 added source-native **2nd-order marked quote transition** features (8 revision classes with short/long 8×8 decayed transitions, reversal age, self/cross-excitation proxies), eight as-of side×completed M15/H1 interactions; total 163-dimensional input with 124 frozen F323 as-of inputs. Two separately trained Coinexx LightGBM 511-leaf 180-round opponent-vs-rest and neutral-vs-rest heads, reusing previously frozen F323 correct-guardian. Fit Jan first70% + Feb first60%, 40-second purge. Four PREDECLARED policies (two architectures × q .995/.99) screened Feb last40 only; 48 causal UTC-hour veto cap. Three causal unit tests PASS, identical source event quote indices PASS.

Best February held-back (development) policy was transition×completed-HTF q .995, **345 additional bad / 220 good loss = 1.568:1**, selected threshold 1.9806536299532174. Frozen and evaluated unchanged Jun/Jul, which are already historically exposed.

F324 original Coinexx months (additional bad / additional good relative F234 ALONE):
- Jan fitted 3,731/123 =30.33 (TRAIN/FITTED, not forecasting)
- Feb full fit+calibration 6,980/285 =24.49 (CONTAMINATED)
- June distinct-fit historical 797/533 =1.495
- July distinct-fit historical 819/510 =1.606
- June+July **1,616/1,043 =1.549**, insufficient selectivity volume, cannot qualify as M-CX-01 replacement. Full original R9 source corrected-UTC 4,178/4,178 quota rows PASS when Dukascopy frozen original F234 unchanged; **not actual fills/trades**. Same-hour fixed-count placebo 100 replicates: June actual 797 vs mean765.48±17.47 incorrect, July actual819 vs782.21±17.63 incorrect; better than 97/100 synthetic resamples EACH but not multiple-trial-adjusted predictive proof. DK July 71% preservation floor still fails under the unchanged original control. No combined exact F17 P05 mask exists; do NOT add F324 increments to F17.

**DO NOT APPROVE**: fails 5:1 meaningful held-back screen, full 71%/90% eight-cell system gates, independent forward predictive test, native MetaEditor compile, and $100/$200 after-cost survivability. Original Python and weights remain reproducible research components only, NOT EA source promoted.

## Exact source code, full artifacts, positive/negative evidence

- **MT5_EXPAND full executable Python, 2 fitted model text weights, 4 original Coinexx event masks, frozen guardian, 3 unit tests, original readers, configs, outputs, exact per-member SHA manifest and research receipt:** https://drive.google.com/file/d/1wKTDlSkD6LP8nNGVTgTQEzg9qOiQzGb8/view
- ZIP size **14,213,914 bytes**, SHA256 `80e8074e6bbad066c40f2a9b8df28a3bda0abf6077ee8ac837789016e4e98b43`; 26 members CRC and all 25 member SHA PASS, cloud raw-download SHA readback PASS.
- The PRIMARY account ZIP upload returned HTTP 403; **the full ZIP is not in PRIMARY and is not committed to GitHub**, only the source-identical independently readback-verified MT5_EXPAND backup. Log/handoff PRIMARY is authoritative: https://docs.google.com/document/d/1cYkw43LC5Ot-V686onwQS5cDZRKPyw1T1T6MvbFVSCA/edit
- Original checklist, do not mutate: https://docs.google.com/document/d/1i2GyLfwVFvyjxB-sNaOwkS6kzZLSWTsijGXaA9qJou0/edit
- Original source/audit: https://drive.google.com/file/d/17YePE46goX2ChbL89LLNbqS5ddYDkms_/view (52-member original source, only accessible from MT5_EXPAND via connector); June fitted weights FILTER07 original https://drive.google.com/file/d/1dOUVcoK-Po_vF3TCUcCAAcWM5KNZOwo5/view (PRIMARY account).

## Next research path (F325 unexecuted)

Exploit high-selectivity original F293 historical class/side/hour stratification, and F323 fixed positive Dukascopy guardian, rather than copy fitted ratios as prediction. Test independently trained original F234-rejected **correct rescue vs wrong reentry**, conditioned on source-native second-order quotes, completed HTF/regime and strictly matured prior outcomes. Require original F234 vs F324-only vs rescue-only vs conditional parallel arbiter side-by-side, without summing unmeasured mask unions. Protect Dukascopy July correct floor (needs ≥4,247 rescued correct under original F234 before added losses). Predeclare one Jan/Feb development gate and June/July exposed transfer. Preserve March/April/May outside scoring pending clean holdout authorization. Do not endlessly repeat failed F315–F324 percentile thresholds.
