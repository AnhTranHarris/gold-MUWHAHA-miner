from pathlib import Path
import re

EA = Path("Experts/GoldMuwahahaMiner_R9_STMR_XMonth_001.mq5")
text = EA.read_text(encoding="utf-8")

required = {
    "candidate": "STMR_XMONTH_SUBPHASE_001",
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
    "custom_h4": "InitTf(g_h4, 4L*3600000L);",
    "custom_h1": "InitTf(g_h1, 3600000L);",
    "custom_m15": "InitTf(g_m15,15L*60000L);",
    "custom_m5": "InitTf(g_m5, 5L*60000L);",
    "semantic_seen": "if(si>=0) g_seen[si]=1;",
    "landing_cell": "const long key_cell=(direction>0?cell:g_prevCell);",
    "hedging_gate": "ACCOUNT_MARGIN_MODE_RETAIL_HEDGING",
}

missing = [name for name, needle in required.items() if needle not in text]
if missing:
    raise SystemExit("MISSING REQUIRED CONTRACT: " + ", ".join(missing))

# Legacy HybridGate mechanics must not contaminate the STMR certification port.
forbidden_active = [
    r"iATR\s*\(",
    r"InpMinDirectionalEff",
    r"InpVelocityLookbackSec",
    r"InpTrailingEnabled",
    r"InpMaxSameMinuteRearms",
]
for pat in forbidden_active:
    if re.search(pat, text):
        raise SystemExit(f"FORBIDDEN LEGACY ACTIVE MECHANISM: {pat}")

if text.count("{") != text.count("}"):
    raise SystemExit("brace imbalance")
if text.count("(") != text.count(")"):
    raise SystemExit("paren imbalance")

print("PASS: static STMR MT5 certification contract")
print("bytes:", EA.stat().st_size)
print("required checks:", len(required))
