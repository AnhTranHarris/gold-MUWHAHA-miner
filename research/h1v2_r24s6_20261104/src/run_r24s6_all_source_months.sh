#!/usr/bin/env bash
set -Eeuo pipefail
export PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2
LAB=/mnt/data/h1v2_r24s6
CORE=/mnt/data/h1v2_r24_asof
log=$LAB/logs/R24S6_EIGHT_SOURCE_MONTHS_APPEND_ONLY_EXECUTION.log
for mon in 01 02 06 07; do
 for source in DUKASCOPY_RAW MT5_BROKER_EXPORT; do
  donefile="$LAB/results/$source/$mon/S6_${source}_${mon}_FULL_SHA_MANIFEST.json"
  echo "$(date -u +%FT%TZ) BEGIN ${source} ${mon}" | tee -a "$log"
  prep="$CORE/results/$source/$mon/R24_${source}_${mon}_SOURCE_PREPARATION_ATOMIC_receipt.json"
  feature="$CORE/results/$source/$mon/R24_${source}_${mon}_1000MS_features.npy"
  if [ ! -s "$feature" ]; then
    python "$CORE/source/r24_prepare_month.py" --source "$source" --month "$mon" >> "$log" 2>&1 || { echo "$(date -u +%FT%TZ) PREP_FAIL ${source} ${mon}" | tee -a "$log"; exit 81; }
  fi
  if [ ! -s "$donefile" ]; then
    python "$LAB/source/r24s6_survival_frontier.py" --source "$source" --month "$mon" >> "$log" 2>&1 || { echo "$(date -u +%FT%TZ) FRONTIER_FAIL ${source} ${mon}" | tee -a "$log"; exit 82; }
  fi
  echo "$(date -u +%FT%TZ) COMPLETE ${source} ${mon}: SHA_MANIFEST=$donefile" | tee -a "$log"
 done
 echo "$(date -u +%FT%TZ) COMPLETE CALENDAR MONTH ${mon} TWO_SOURCE PASS" | tee -a "$log"
done
printf '%s\n' "$(date -u +%FT%TZ) FULL EIGHT SOURCE MONTH PASS" | tee -a "$log"
