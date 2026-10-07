from pathlib import Path
from datetime import datetime, timezone
import re

WRAPPER = Path("Experts/GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid_ClockFix.mq5")
BASE = Path("Experts/GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid.mq5")

w = WRAPPER.read_text(encoding="utf-8")
b = BASE.read_text(encoding="utf-8")

required = {
    "include_exact_gamma01": '#include "GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid.mq5"',
    "rename_init": "#define OnInit          Gamma01_LegacyOnInit",
    "rename_deinit": "#define OnDeinit        Gamma01_LegacyOnDeinit",
    "rename_tick": "#define OnTick          Gamma01_LegacyOnTick",
    "rename_grid_reconcile": "#define GridReconcile   Gamma01_LegacyGridReconcile",
    "rename_to_utc": "#define ToUtcMs         Gamma01_LegacyToUtcMs",
    "default_auto": "InpGridClockMode = STMR_GRID_CLOCK_COINEXX_AUTO",
    "fixed_diag": "InpGridFixedQuoteUtcOffsetMinutes = 120",
    "standard_offset": "return (server_time>=dst_start_server && server_time<dst_end_server) ? 180 : 120;",
    "corrected_time": "const long utc_ms=GridToUtcMs(tick.time_msc);",
    "core_first": "if(InpCoreEnabled) Reconcile(tick);",
    "grid_second": "if(InpGridEnabled) GridReconcile(tick);",
    "legacy_init": "const int rc=Gamma01_LegacyOnInit();",
}
missing = [k for k,v in required.items() if v not in w]
if missing:
    raise SystemExit("CLOCKFIX CONTRACT MISSING: " + ", ".join(missing))

# The wrapper must not replace or duplicate scientific sleeve geometry.  All
# TP/SL/session/sleeve constants must still live exclusively in the audited base.
for forbidden in [
    "g_tpRaw[STMR_SLEEVE_COUNT]",
    "g_slRaw[STMR_SLEEVE_COUNT]",
    "g_gapRaw[7]",
    "bool DetermineSleeve(",
    "bool SleevePhaseAllowed(",
]:
    if forbidden in w:
        raise SystemExit(f"SCIENTIFIC GRID LOGIC DUPLICATED IN CLOCK WRAPPER: {forbidden}")

# Confirm the included base is still the intended GAMMA-01 cumulative build.
base_contract = [
    'const double STMR_LOTS = 0.01;',
    'const int STMR_MAX_POSITIONS = 3;',
    'sleeve==0 || sleeve==2 || sleeve==4 || sleeve==8 || sleeve==9 || sleeve==11',
    'if(sleeve==4) return (minute>=900 && minute<960);',
    'if(sleeve==11) return (minute>=1260 && minute<1320);',
    'if(InpCoreEnabled) Reconcile(tick);',
    'if(InpGridEnabled) GridReconcile(tick);',
]
missing_base = [x for x in base_contract if x not in b]
if missing_base:
    raise SystemExit("INCLUDED GAMMA-01 BASE CONTRACT DRIFT")

# Mirror the wrapper's historical Coinexx switch rule and sanity-check 2026.
def nth_sunday(year: int, month: int, nth: int) -> int:
    d = datetime(year, month, 1, tzinfo=timezone.utc)
    # Python Monday=0; Sunday=6.
    first = 1 + ((6 - d.weekday()) % 7)
    return first + (nth - 1) * 7

def offset_minutes(server_dt: datetime) -> int:
    start = datetime(server_dt.year, 3, nth_sunday(server_dt.year, 3, 2), 9, 0, tzinfo=timezone.utc)
    end = datetime(server_dt.year, 11, nth_sunday(server_dt.year, 11, 1), 9, 0, tzinfo=timezone.utc)
    return 180 if start <= server_dt < end else 120

assert offset_minutes(datetime(2026,1,15,12,tzinfo=timezone.utc)) == 120
assert offset_minutes(datetime(2026,3,7,12,tzinfo=timezone.utc)) == 120
assert offset_minutes(datetime(2026,3,9,12,tzinfo=timezone.utc)) == 180
assert offset_minutes(datetime(2026,7,15,12,tzinfo=timezone.utc)) == 180
assert offset_minutes(datetime(2026,11,2,12,tzinfo=timezone.utc)) == 120

# Entry points should exist once in wrapper source. Renamed legacy entrypoints
# come from the textual include only after preprocessing.
if len(re.findall(r"\bint\s+OnInit\s*\(", w)) != 1:
    raise SystemExit("WRAPPER OnInit COUNT ERROR")
if len(re.findall(r"\bvoid\s+OnTick\s*\(", w)) != 1:
    raise SystemExit("WRAPPER OnTick COUNT ERROR")
if len(re.findall(r"\bvoid\s+GridReconcile\s*\(", w)) != 1:
    raise SystemExit("WRAPPER GridReconcile COUNT ERROR")

# Guard against reintroducing the invalid v1 clock as default.
if re.search(r"InpGridClockMode\s*=\s*STMR_GRID_CLOCK_RAW_TESTER", w):
    raise SystemExit("RAW TESTER CLOCK MUST NOT BE DEFAULT")

print("PASS: R9 GAMMA-01 STMR clock-fix static QA")
print("wrapper_bytes:", WRAPPER.stat().st_size)
print("base_bytes:", BASE.stat().st_size)
print("2026 offset sanity: Jan=120 Mar-after-DST=180 Jul=180 Nov-after-DST=120")
