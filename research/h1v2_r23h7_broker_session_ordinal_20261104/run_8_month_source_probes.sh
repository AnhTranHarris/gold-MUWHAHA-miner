#!/usr/bin/env bash
set -u
ROOT=/mnt/data/r23h7_work
export R23H24_WORKSPACE=/mnt/data/r23h24_workspace
export PYTHONPATH="$ROOT/src"
: > "$ROOT/results/R23H7_PROBE_EXECUTION_REGISTER.tsv"
printf 'feed\tmonth\tmode\tday\tstatus\tlog\n' >> "$ROOT/results/R23H7_PROBE_EXECUTION_REGISTER.tsv"
for M in 01 02 06 07; do
  for S in DUKASCOPY_RAW MT5_BROKER_EXPORT; do
    F="$ROOT/results/fit_${S}_${M}.log"
    if python "$ROOT/src/r23h7_broker_hazards.py" --source "$S" --month "$M" --mode fit --cap-per-day 320 --rounds 35 >"$F" 2>&1; then
      printf '%s\t%s\tFIT\tNA\tPASS\t%s\n' "$S" "$M" "$F" >> "$ROOT/results/R23H7_PROBE_EXECUTION_REGISTER.tsv"
    else
      printf '%s\t%s\tFIT\tNA\tFAIL\t%s\n' "$S" "$M" "$F" >> "$ROOT/results/R23H7_PROBE_EXECUTION_REGISTER.tsv";continue
    fi
    D=2
    if [[ "$M" == "06" || "$M" == "07" ]];then D=1;fi
    L="$ROOT/results/score_${S}_${M}_$(printf %02d "$D").log"
    if python "$ROOT/src/r23h7_broker_hazards.py" --source "$S" --month "$M" --mode score_day --day "$D" >"$L" 2>&1;then
      printf '%s\t%s\tSCORE_DAY\t%s\tPASS\t%s\n' "$S" "$M" "$D" "$L" >> "$ROOT/results/R23H7_PROBE_EXECUTION_REGISTER.tsv"
    else
      printf '%s\t%s\tSCORE_DAY\t%s\tFAIL\t%s\n' "$S" "$M" "$D" "$L" >> "$ROOT/results/R23H7_PROBE_EXECUTION_REGISTER.tsv"
    fi
  done
done
