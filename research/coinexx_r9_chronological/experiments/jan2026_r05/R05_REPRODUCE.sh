#!/usr/bin/env bash
set -euo pipefail
# Run within the extracted R05 source kit on a system with the external ORIGINAL sources.
# January-only research; no live trade changes. THE ORIGINAL R9 SYNTH LEDGER IS READ-ONLY.
HERE="$(cd "$(dirname "$0")" && pwd)"
RAW="${R9_REAL_TICKS:-/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz}"
R03="${R9_R03_FOLDER:-/mnt/data/r9_jan_r03}"
cd "$HERE"
python - "$RAW" <<'PY'
import hashlib,sys
h=hashlib.sha256()
with open(sys.argv[1],'rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
assert h.hexdigest()=="1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8",'ORIGINAL COINEXX DIGEST DIFFERENT: ABORT'
print('Original Jan source SHA256 pinned and verified')
PY
for x in "$R03/r03_phase_seconds.csv.gz" "$R03/r03_hazard_predictions.csv.gz";do test -s "$x";done
# The original fixed R9 trade manifest is used for JANUARY OFFLINE label fitting, NEVER C++ execution.
# Re-fitting is optional; frozen weights and fitted forests in source ZIP reproduce published trial ledgers.
if [[ "${R05_REFIT:-0}" == '1' ]];then
 python r05_train_episode.py prep
 python r05_train_episode.py fit
 python r05_competing_passage_fit.py
 python r05_protected_entry_fit.py fit
 python r05_protected_entry_fit.py score
 python r05_episode_family_router.py fit
 python r05_episode_family_router.py score
fi
# Score the frozen January family model in label-free INFERENCE mode if score stream is absent.
# This derives only a bounded secondary score stream from external preserved R03 features.
if [[ ! -s "$HERE/r05_episode_predictions.csv.gz" ]];then OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 python r05_episode_family_router.py score;fi
# External original raw ticker is supplied explicitly; this script never writes or regenerates it.
g++ -std=c++17 -O3 -Wall -Wextra -Werror r05_joint_replay.cpp -lz -o r05_joint_replay
run(){ local name="$1" source="$2" mode="$3" early="$4";
 "$HERE/r05_joint_replay" "$RAW" "$R03/r03_phase_seconds.csv.gz" "$source" r05_exit_forest.txt r05_rearm_forest.txt "$name.csv" \
   --mode="$mode" --f=.24 --s=.23 --e=.4 --r=.3 --spread=80 --stop=180 --hold=32 --only_early_rearm="$early" --target=56 --passcut=.6 --passage=r05_competing_passage_forest.txt 2>"${name}_receipt.log"
}
run r05_repro_r03entry "$R03/r03_hazard_predictions.csv.gz" 0 0
run r05_repro_episode_phase "$HERE/r05_episode_predictions.csv.gz" 0 1
run r05_repro_episode_tickordinal "$HERE/r05_episode_predictions.csv.gz" 8 1
# Grade preserved source-exact R05 trials in a distinct offline step.
# Reported R05 18-configuration ledgers are in this source kit; the 3 reproduction outputs use separate names.
# New independent test files above intentionally use distinct names and do not overwrite published ledgers.
python r05_grade.py
python r05_regression.py
