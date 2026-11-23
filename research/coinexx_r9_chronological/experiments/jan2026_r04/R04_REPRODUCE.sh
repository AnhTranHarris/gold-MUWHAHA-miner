#!/usr/bin/env bash
set -euo pipefail
# Use the original, READ-ONLY January Coinexx and the full unchanged R03 parent work environment.
RAW="${R9_REAL_TICKS:-/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz}"
HERE="$(cd "$(dirname "$0")" && pwd)"
R03="${R9_R03_FOLDER:-/mnt/data/r9_jan_r03}"
cd "$HERE"
export R9_R03_FOLDER="$R03"
python - "$RAW" <<'PY'
import hashlib,sys
h=hashlib.sha256()
with open(sys.argv[1],'rb') as f:
 for ch in iter(lambda:f.read(1<<20),b''):h.update(ch)
assert h.hexdigest()=='1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8'
print('Original January Coinexx source SHA PASS')
PY
for required in r03_phase_seconds.csv.gz r03_hazard_predictions.csv.gz r03_repro_profit_v02.csv r03_teacher_5sec.csv;do test -f "$R03/$required";done
# Source compiled only in this experimental folder; original R9/MQL5 remains read-only.
g++ -std=c++17 -O3 -Wall -Wextra -Werror -o r04_quoteordinal_competing_exit r04_quoteordinal_competing_exit.cpp -lz
g++ -std=c++17 -O3 -Wall -Wextra -Werror -o r04_meta_replay r04_meta_replay.cpp -lz
python r04_atlas_witness.py
# Frozen in-sample meta model weights shipped with the ZIP are authoritative for published R04 grades.
# Optional explicit re-fit, which may differ across LightGBM versions: R04_REFIT=1 bash R04_REPRODUCE.sh
if [[ "${R04_REFIT:-0}" == 1 ]];then OPENBLAS_NUM_THREADS=1 python r04_fit_entry_risk.py;fi
OPENBLAS_NUM_THREADS=1 python r04_score_meta.py
# Source-inherited baseline, confidence-admission and evidence-anchored phase-exit variants.
run_meta(){ local name="$1" meta="$2" pt="$3" clock="$4"; ./r04_meta_replay "$RAW" r04_scores.csv.gz "${name}.csv" --meta="$meta" --f=0.24 --s=0.23 --spread=80 --pt="$pt" --sl=180 --hold=30 --clock="$clock" --second=1 --opp=1 2>"${name}_receipt.json"; }
run_meta r04_meta_0 0 14 0
run_meta r04_meta_0p65 .65 14 0
run_meta r04_meta_0p75 .75 14 0
run_meta r04_mfe56 .75 56 0
run_meta r04_book98 .75 98 0
run_meta r04_phase_mfe56 .75 56 2
run_meta r04_phase_mfe56_70 .70 56 2
run_meta r04_phase_mfe56_80 .80 56 2
for m in 0 1 2 3;do ./r04_quoteordinal_competing_exit "$RAW" "$R03/r03_hazard_predictions.csv.gz" "r04_mode_${m}.csv" --mode="$m" --fee=2 --hardstop=30 --hold=30 --second=1 --opp=1 2>"r04_mode_${m}_receipt.json";done
python r04_grade_source_account.py
python -m unittest discover -s "$HERE" -p r04_test_causal_cost.py -v
