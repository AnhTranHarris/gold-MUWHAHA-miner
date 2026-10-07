from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Experts" / "GoldMuwahahaMiner_R9_HybridGate.mq5"
LOGGER = ROOT / "Experts" / "GoldMuwahahaMiner_R9_TickLogger.mq5"
EA = ROOT / "Experts" / "GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5"

def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()

expected_blobs = {
    BASE: "7eecb5f1947017a01ce85b2520725de54749e523",
    LOGGER: "5c7655cd3357f9126e8bffd97c34374dfb29f83e",
    EA: "daa754c8fcd035915660ccc00274a6003d135ea9",
}
for path, expected in expected_blobs.items():
    got = git_blob_sha(path)
    if got != expected:
        raise SystemExit(f"BLOB DRIFT {path}: expected {expected}, got {got}")

text = EA.read_text(encoding="utf-8")
required = {
    "candidate": "STMR_XMONTH_SUBPHASE_001",
    "version": '#property version   "9.32"',
    "fixed_lot": "const double STMR_LOTS = 0.01;",
    "max_positions": "const int STMR_MAX_POSITIONS = 3;",
    "max_hold": "const long STMR_MAX_HOLD_MS = 300000;",
    "gaps": "int g_gapRaw[7] = {750,0,1000,750,1500,500,0};",
    "tp": "int g_tpRaw[STMR_SLEEVE_COUNT] = {4000,4000,4000,3000,4000,3000,4000,2500,4000,4000,4000,2500};",
    "sl": "int g_slRaw[STMR_SLEEVE_COUNT] = {1000,1500,750,750,1500,750,1500,1500,1500,1500,1500,1250};",
    "funded": "sleeve==0 || sleeve==2 || sleeve==4 || sleeve==8 || sleeve==9 || sleeve==11",
    "asia_gate": "if(sleeve==0) return (minute>=1380);",
    "london_gate": "if(sleeve==2) return (minute>=660 && minute<720);",
    "overlap_gate": "if(sleeve==4) return (minute>=900 && minute<960);",
    "late_gate": "if(sleeve==11) return (minute>=1260 && minute<1320);",
    "deal_binding": "trade.ResultDeal()",
    "deal_position": "DEAL_POSITION_ID",
    "position_identifier": "POSITION_IDENTIFIER",
    "bind_fail_counter": "g_bindFailures",
    "volume_counter": "g_volumeMismatch",
    "common_files": r"Common\\Files\\%s",
}
missing = [name for name, needle in required.items() if needle not in text]
if missing:
    raise SystemExit("MISSING CONTRACT: " + ", ".join(missing))

for marker in range(8):
    token = f"[EDIT-{marker:02d}]"
    if token not in text:
        raise SystemExit(f"MISSING MAINTENANCE MARKER {token}")

forbidden = [
    r"FindNewestOurPosition\s*\(",
    r"iATR\s*\(",
    r"InpMinDirectionalEff",
    r"InpVelocityLookbackSec",
    r"InpTrailingEnabled",
    r"InpMaxSameMinuteRearms",
]
for pat in forbidden:
    if re.search(pat, text):
        raise SystemExit(f"FORBIDDEN/AMBIGUOUS ACTIVE MECHANISM: {pat}")

if text.count("{") != text.count("}"):
    raise SystemExit("brace imbalance")
if text.count("(") != text.count(")"):
    raise SystemExit("paren imbalance")

print("PASS: R9 base blobs unchanged")
print("PASS: STMR XMonth 001 contract")
print("PASS: exact opening-deal/position binding present")
print("candidate bytes:", EA.stat().st_size)
