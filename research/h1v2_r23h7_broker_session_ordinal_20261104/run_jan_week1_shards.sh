#!/usr/bin/env bash
set -u
ROOT=/mnt/data/r23h7_work
export R23H24_WORKSPACE=/mnt/data/r23h24_workspace
printf 'feed\tday\tstatus\tlog\n' > "$ROOT/results/R23H7_JAN_WEEK1_DAY_SHARD_REGISTER.tsv"
for S in DUKASCOPY_RAW MT5_BROKER_EXPORT;do
  for D in 1 2 3 4 5 6 7;do
    f="$ROOT/results/score_${S}_01_$(printf '%02d' "$D").log"
    if python "$ROOT/src/r23h7_broker_hazards.py" --source "$S" --month 01 --mode score_day --day "$D" >"$f" 2>&1;then
      printf '%s\t%s\tPASS\t%s\n' "$S" "$D" "$f" >> "$ROOT/results/R23H7_JAN_WEEK1_DAY_SHARD_REGISTER.tsv"
    else
      printf '%s\t%s\tFAIL\t%s\n' "$S" "$D" "$f" >> "$ROOT/results/R23H7_JAN_WEEK1_DAY_SHARD_REGISTER.tsv"
    fi
  done
done
