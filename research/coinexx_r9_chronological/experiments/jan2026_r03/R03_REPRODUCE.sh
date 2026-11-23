#!/usr/bin/env bash
set -euo pipefail
# Run from extracted r03 source-kit directory. Original tick and R9 manifest are EXTERNAL READ-ONLY sources.
RAW="${R9_REAL_TICKS:-/mnt/data/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz}"
REF="${R9_REFERENCE_MANIFEST:-/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv}"
cd "$(dirname "$0")"
python - "$RAW" <<'PY'
import sys,hashlib
path=sys.argv[1];h=hashlib.sha256()
with open(path,'rb') as f:
 for b in iter(lambda:f.read(1<<20),b''):h.update(b)
assert h.hexdigest()=='1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8','SOURCE HASH MISMATCH'
print('SOURCE ORIGINAL SHA256 VERIFIED')
PY
g++ -std=c++17 -O3 -Wall -Wextra -Werror -o r03_phase_stream r03_phase_stream.cpp -lz
g++ -std=c++17 -O3 -Wall -Wextra -Werror -o r03_phase_replay r03_phase_replay.cpp -lz
g++ -std=c++17 -O3 -Wall -Wextra -Werror -o r03_chronological_teacher r03_chronological_teacher.cpp -lz
# Causal observed-second feature stream from ORIGINAL source. No raw-tick copy or tick database.
./r03_phase_stream "$RAW" r03_phase_seconds.csv.gz
# Deliberate January IN-SAMPLE refit; the fit script reads original immutable reference ONLY for labels/risk sets.
# Original scientific fit may have different LightGBM versions; packaged frozen model weights are authoritative for published grades.
# python r03_hazard_fit.py prep
# python r03_hazard_fit.py fit
# Partition full January model inference to keep each Python invocation below resource limits.
python r03_hazard_score_part.py 0 3
python r03_hazard_score_part.py 3 6
python r03_hazard_score_part.py 6 9
python r03_hazard_score_part.py 9 12
cat r03_hazard_part_0_3.csv.gz r03_hazard_part_3_6.csv.gz r03_hazard_part_6_9.csv.gz r03_hazard_part_9_12.csv.gz > r03_hazard_predictions.csv.gz
# Model-generated signals have NO original target labels; live replay decisions use as-of source quote features.
./r03_phase_replay "$RAW" r03_hazard_predictions.csv.gz r03_repro_profit_v02.csv --f=0.24 --s=0.23 --spread=80 --pt=14 --sl=180 --hold=30 --clock=0 --second=1 --opp=1 2>r03_repro_profit_v02_receipt.json
./r03_phase_replay "$RAW" r03_hazard_predictions.csv.gz r03_repro_clock_v03.csv --f=0.24 --s=0.23 --spread=80 --pt=14 --sl=180 --hold=30 --clock=1 --second=1 --opp=1 2>r03_repro_clock_v03_receipt.json
# OFFLINE labels-only grading. Does not feed reference into execution.
R9_REFERENCE_MANIFEST="$REF" python r03_grade_replay.py r03_repro_profit_v02.csv r03_repro_clock_v03.csv
# Source-only teacher is noncausal, per-reference-row optimistic evidence and cannot be deployed.
# ./r03_chronological_teacher "$RAW" "$REF" r03_teacher_5sec.csv 5
