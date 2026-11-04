#!/usr/bin/env bash
set -Eeuo pipefail
export OMP_NUM_THREADS=3
ROOT=/mnt/data/h1v2_r24s4_entry_specialists
BASE=/mnt/data/h1v2_r24_asof/source
LOG=$ROOT/R24S4_LOCAL_PHASE_CHECKPOINTS.tsv
[[ -e "$LOG" ]] || printf 'utc_epoch\tsource\tmonth\tphase\tstatus\tpath\n' > "$LOG"
phase(){ printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%s)" "$1" "$2" "$3" "$4" "$5" >> "$LOG"; }
for m in 01 02 06 07; do
 for s in DUKASCOPY_RAW MT5_BROKER_EXPORT; do
  d=$ROOT/results/$s/$m
  mkdir -p "$d" "$ROOT/logs"
  z=$ROOT/logs/${s}_${m}
  pre=/mnt/data/h1v2_r24_asof/results/$s/$m/R24_${s}_${m}_SOURCE_PREPARATION_ATOMIC_receipt.json
  # Old recovery ZIP can contain a COMPLETE historic receipt without mounting the original
  # large candidate arrays. A JSON receipt alone must never certify local readiness.
  dat=/mnt/data/h1v2_r24_asof/results/$s/$m/R24_${s}_${m}_1000MS
  if [[ ! -s "$pre" || ! -s "${dat}_features.npy" || ! -s "${dat}_labels_2SIDE_3HORIZON.npy" || ! -s "${dat}_signal_utc_ms.npy" || ! -s "${dat}_fill_source_quote_ordinal.npy" || ! -s "${dat}_first_event_source_quote_ordinal.npy" ]]; then
   if [[ -s "$pre" ]];then cp -n "$pre" "$d/R24_ORIGINAL_ARCHIVED_SOURCE_RECEIPT_BEFORE_RESTORATION.json";fi
   phase "$s" "$m" "source_prep" "START" "$z.prep.log"
   python -u "$BASE/r24_prepare_month.py" --source "$s" --month "$m" > "$z.prep.log" 2>&1
   phase "$s" "$m" "source_prep" "PASS" "$pre"
  else
   phase "$s" "$m" "source_prep" "EXISTING_WITH_THIS_RUN_01_ONLY_OR_VERIFIED_COPY" "$pre"
  fi
  clock=/mnt/data/h1v2_r24_asof/results/$s/$m/R24_${s}_${m}_ACTUAL_BROKER_QUOTE_CLOCK_RECEIPT.json
  if [[ ! -s "$clock" || ! -s "${dat}_actual_fill_utc_ms.npy" || ! -s "${dat}_first_barrier_2SIDE_utc_ms.npy" || ! -s "${dat}_true_timeout_first_observed_utc_ms.npy" ]];then
   if [[ -s "$clock" ]];then cp -n "$clock" "$d/R24_ORIGINAL_ARCHIVED_CLOCK_RECEIPT_BEFORE_RESTORATION.json";fi
   phase "$s" "$m" "true_tick_clocks" "START" "$z.clock.log"
   python -u "$BASE/r24_restore_actual_event_clock.py" --source "$s" --month "$m" > "$z.clock.log" 2>&1
   phase "$s" "$m" "true_tick_clocks" "PASS" "$clock"
  else
   phase "$s" "$m" "true_tick_clocks" "EXISTING_WITH_THIS_RUN_01_ONLY_OR_VERIFIED_COPY" "$clock"
  fi
  report="$d/R24S4_${s}_${m}_FULL_60_CASES_ATOMIC_RECEIPT.json"
  if [[ ! -s "$report" ]];then
   phase "$s" "$m" "separate_hazard_wait_fit_60_replay" "START" "$z.specialist.log"
   python -u "$ROOT/src/r24s4_broker_hazard_specialist.py" --source "$s" --month "$m" --sample-count 120000 --rounds 62 > "$z.specialist.log" 2>&1
   [[ -s "$report" ]] || { echo MISSING_ATOMIC_RECEIPT:"$report";exit 2; }
   phase "$s" "$m" "separate_hazard_wait_fit_60_replay" "PASS" "$report"
  else
   phase "$s" "$m" "separate_hazard_wait_fit_60_replay" "PREVIOUSLY_COMPLETED_SAME_SHA_GUARD" "$report"
  fi
  echo COMPLETE_SOURCE_MONTH:"$s":"$m" >> "$ROOT/logs/BATCH_COMPLETIONS.log"
 done
done
phase "ALL_8" "ALL" "replay" "COMPLETE" "$ROOT"
