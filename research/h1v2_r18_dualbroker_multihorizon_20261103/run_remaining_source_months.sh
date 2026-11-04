#!/usr/bin/env bash
set -euo pipefail
cd /mnt/data/h1v2_r18_dualbroker
for mon in 02 06 07; do
  for feed in DUKASCOPY_RAW MT5_BROKER_EXPORT; do
    name="R18_${feed}_${mon}"
    echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') BEGIN ${name}" >> results/R18_FULL_RESEARCH_EXECUTION_LEDGER.log
    env OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1 python src/r18_broker_multihorizon.py --source "$feed" --month "$mon" --root /mnt/data --output results > "results/${name}_full_run.log" 2>&1 || { code=$?; echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') FAILED ${name} code ${code}" >> results/R18_FULL_RESEARCH_EXECUTION_LEDGER.log; exit "$code"; }
    test -s "results/${name}_SOURCE_VERIFIED_RECEIPT.json"
    echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') COMPLETE ${name}" >> results/R18_FULL_RESEARCH_EXECUTION_LEDGER.log
  done
done
echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') ALL_EIGHT_SOURCE_MONTH_RESEARCH_COMPLETE" >> results/R18_FULL_RESEARCH_EXECUTION_LEDGER.log
