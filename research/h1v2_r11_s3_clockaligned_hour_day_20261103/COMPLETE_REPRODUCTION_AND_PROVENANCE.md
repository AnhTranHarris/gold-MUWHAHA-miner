# H1V2-R11S3 — Complete source-exact UTC hourly, daily and monthly survivability reconciliation

Date 2026-11-03 UTC / 2026-11-02 America/Chicago. This is a distinct append-only research experiment, not an edited replacement of any historical H1V2/R11/S1/S2 artifact. No holding, trailing, exit, account economics or real broker behavior is optimized here. NO promotion to a causal or MT5 model is permitted.

## Exact scientific goals and data sources

The owner requested separate, exhaustive Jan/Feb/June/July 2026 deliberately in-sample initial entry study and R9 SYNTH *hourly*, *daily*, *monthly* volume matching, without sacrificing the full original 15-to-30-second entry survival conditions. The direct R11S1 full quote-side label is GOOD only if favorable +$0.10 net reached no later than 15s AND no adverse liquidation movement of -$0.10 occurred in any quote through full 30s. Source-end/gap censor is not favorable. The original single-position reservation of >30000ms separates successive entries, retained in all meaningful primary bounds. The 100% strict oracle is explicitly future-informed, not predictive; the prior within-month LightGBM R11S2 student is a different experiment and is never mislabeled an oracle.

Four authoritative clock-corrected source ZIPs are named `R11S_{01|02|06|07}_COMPLETE_CLOCK_CORRECTED_SOURCE_EXACT_FAV15_SURV30_SYNTH_HOURLY_QUOTA_ALL_ADVERSE_BUDGETS_20261103.zip`, each with 32 members and an exact SHA manifest, containing source code, 15s/30s original oracle, source matched R9 SYNTH UTC hourly/daily data, independent-hour lower and optimistic crossing upper bounds, four 15/20/25/30-second reserve counterfactuals, six adverse excursion budgets from $0.10 through $1.00 and unsafe favorable-only no-veto bounds. All 4 source ZIP CRC and all 31 pinned members each verified during R11S3, including original quote-ordinal traces. 4 historical R11S2 original within-month fitted models per side are in separate month-specific artifacts; 36 exact selection traces and all four receipt JSON files were rechecked, not refitted.

Original H1V2 and repaired v5 live architecture remain untouched; R11S1 full source labels preserved by original ZIP. The main project progress log is `https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit`. Complete original H1V2 audit `https://docs.google.com/document/d/1KhPl9eZqUJZM8vh7W8n93tUQWwbLXhMhcPZDXEN909E/edit`. Original 4-month full-source provenance `https://drive.google.com/file/d/1dc7oNf38xZ0Vm_P_K7xkZ46_CY5ctzWe/view`. R9 SYNTH direct source date/hour index `https://docs.google.com/spreadsheets/d/1VIx7mDN-sHBj2kQ5-JueV4V-sIHnFhPadOYClgLG_I8/edit`.

## Clock conversion

R9 SYNTH recorded quote timestamps are in a server clock, whereas Dukascopy quotes are in UTC. Independent matched quote-mid-price series support server-to-UTC shifts January -2h, February -2h, June -3h, July -3h. These corrections change the exact row/day/hour quota, and shift some June/July source-native monthly events across adjacent UTC month boundaries. R9 SYNTH UTC monthly references in this source-aligned research: Jan 27980, Feb 33523, June 31758 (native report 31801), July 24324 (native 24382). Historical earlier raw-server-UTC assumptions are retained only as SUPERSEDED controls. ALL source-calendar hours, including no-trade hours, included.

## All source-exact outputs (no omitted hour or model)

`ALL_2880_UTC_HOURLY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv`: 744 Jan +672 Feb +720 June +744 July source UTC hours; exact matched reference, global strict oracle count, independent-hour constructive lower and cross-boundary optimistic upper, impossible-hour witness, 4 occupancy variants, six adverse stop thresholds and deliberately unsafe no-stop counterfactual, all 0-hour rows retained.

`ALL_120_UTC_DAILY_CAUSAL_STUDENT_ORACLE_QUOTA_AND_RISK.csv`: all 31/28/30/31 source calendar days including weekend and zero-reference days, strict source global oracle count and all risk/occupancy daily counts. Every reference daily count derived from the same corrected hour rows.

`ALL_25920_UTC_HOURLY_STUDENT_REPLAY_36_POLICIES.csv`: all nine within-month R11S2 LightGBM selection fractions for each of four months, every hour including zero, exact original ordinal selected trace outcomes, counts of GOOD/NEUTRAL/BAD/CENSORED, BUY, selection rates versus SYNTH hourly reference, strict 80% hour accuracy and joint quota/accuracy indicators. These are fitted from 400k systematic source examples per side per month and scored on full month, not a full-4million-row training fit and not independent OOS.

`ALL_1080_UTC_DAILY_STUDENT_REPLAY_36_POLICIES.csv`: all nine within-month policies and all 120 source calendar days with hourly reconciled selected count, GOOD/BAD/NEUTRAL/CENSORED and daily 80% strict+actual SYNTH reference indicators.

`ALL_36_MONTHLY_FITTED_POLICY_FULL_SOURCE_RECEIPTS.json`: exact nine research policy JSON objects per month, no collapsed experiment details, SHA of each original NPZ trace. `ALL_FOUR_COMPLETE_ORIGINAL_MANIFESTS_AND_FIT_RESULTS.json`: all original full monthly clock-corrected source manifests and full R11S2 research receipts. `ALL_SOURCE_EXACT_EXECUTION_PARITY_CHECKS.json`: month by month ZIP CRC, all 31 member hashes, full hour counts, 36 policy parity and exact impossible-hour counts. `ALL_PROVEN_30SEC_HOURLY_IMPOSSIBILITY_WITNESSES.json`: individual 246 UTC hours whose own strict 30s optimistic upper bound is less than actual R9 SYNTH reference, with exact counts and unavoidable deficit. `EXECUTION_VERIFICATION_INDEX.json`: exact machine provenance and unqualified scientific status. `NEW_R11S3_ALL_FILE_SHA256_MANIFEST.json`: all published output byte sizes/hashes. Source generator and standalone regression tests included.

## Critical logical boundaries

The original source under fixed 30s reservation cannot meet every hour: 50 Jan, 151 Feb, 27 June, 18 July clock-corrected reference hours are provably impossible under strict $0.10 adverse movement. No heuristic or model could meet those exact hourly quotas within that same market/measurement and reservation contract, including a future-informed oracle. Monthly totals can still exceed R9 SYNTH monthly counts, and most daily volumes can exceed, without satisfying every exact hour.

Increasing the allowable 30s adverse excursion to $0.15/$0.20/$0.30/$0.50/$1.00 changes the risk contract and cannot be described as meeting the original $0.10 survival; a no-veto counterfactual is explicitly unsafe. Shortening reservation to 15/20/25s increases entry count only by permitting another signal while previous observation's 30s horizon remains open: NOT one-position-at-a-time 30s trade logic. These are sensitivity diagnostics, NOT approved repairs.

All reported 100% correct oracle selections are tautological because they are future-selected. The prior trained R11S2 policy 36 full-month source replays produce no joint hourly quota+80% success. Do not hide this failure or blend it with oracle counts.

## Reproduce exactly

`python build_complete_hour_day_month.py` from a runtime with original four corrected source ZIPs at `/mnt/data` and original frozen R11S2 36 NPZ selection traces and 4 receipts at `/mnt/data/h1v2_r11_s2_full_month/replay`. The script hashes every source member, independently constructs the 2,880 UTC hours and 120 calendar days, groups actual R11S2 source ordinals into 25,920 model-hour and 1,080 model-day rows, checks all model outcome totals, source data UTC alignment and original monthly reported counts. It does not access raw gold tick file after source verification because the first-stage source-verified ZIPs already carry full corresponding oracle and trade traces. Preserve full original 32.29M quote archives and 15.30M R11S entry labels separately.

`PYTHONPATH=. pytest -q tests/test_reconstructed_full_calendar.py` checks 6 independent regressions. Original R11 mechanical + S1 + clock alignment test suite `53 passed` in this run. Source zip crc/member hashes checked separately as part of generation.
