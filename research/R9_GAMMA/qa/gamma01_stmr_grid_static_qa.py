from pathlib import Path
import hashlib
import re

BASE = Path("Experts/GoldMuwahahaMiner_R9_HybridGate.mq5")
EA = Path("Experts/GoldMuwahahaMiner_R9_GAMMA_01_STMRGrid.mq5")

base = BASE.read_bytes()
text = EA.read_text(encoding="utf-8")
base_text = base.decode("utf-8")

# Git blob identity of the exact Gamma parent EA.
git_blob_sha = hashlib.sha1(f"blob {len(base)}\0".encode() + base).hexdigest()
EXPECTED_BASE_BLOB = "7eecb5f1947017a01ce85b2520725de54749e523"
if git_blob_sha != EXPECTED_BASE_BLOB:
    raise SystemExit(f"BASE R9 BLOB DRIFT: {git_blob_sha} != {EXPECTED_BASE_BLOB}")

required = {
    "candidate": "STMR_XMONTH_SUBPHASE_001",
    "base_blob_note": "Base EA blob SHA: 7eecb5f1947017a01ce85b2520725de54749e523",
    "core_switch": "input bool   InpCoreEnabled              = true;",
    "grid_switch": "input bool   InpGridEnabled              = true;",
    "grid_magic": "input ulong  InpGridMagic                = 5593001;",
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
    "core_first": "if(InpCoreEnabled) Reconcile(tick);",
    "grid_second": "if(InpGridEnabled) GridReconcile(tick);",
    "grid_trade_magic": "gridTrade.SetExpertMagicNumber(InpGridMagic);",
    "hedging_gate": "ACCOUNT_MARGIN_MODE_RETAIL_HEDGING",
}
missing = [name for name, needle in required.items() if needle not in text]
if missing:
    raise SystemExit("MISSING CONTRACT: " + ", ".join(missing))

# Extract full function bodies with brace matching.
def fn(src: str, name: str):
    m = re.search(r"(?:bool|void|int|double|datetime|ENUM_GMM_SESSION|string)\s+" + re.escape(name) + r"\s*\([^\)]*\)\s*\{", src)
    if not m:
        raise SystemExit(f"FUNCTION NOT FOUND: {name}")
    start = m.start()
    brace = src.index("{", start)
    depth = 0
    for i in range(brace, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i+1]
    raise SystemExit(f"UNTERMINATED FUNCTION: {name}")

# These are the behavior-bearing R9 functions. They must remain byte-identical
# to the Gamma parent. Only OnInit/OnDeinit/OnTick are intentionally wrapped.
core_functions = [
    "DaysInMonth","DayOfWeekUtc","NthSunday","LastSunday","MakeUtc",
    "IsLondonDstUtc","IsNewYorkDstUtc","LocalMinuteOfDay","CurrentSession",
    "SessionAtrMinimum","GetCompletedAtr","GateAllowsEntry",
    "PushCompletedSecond","RingIndexFromNewest","UpdateSecondBucket",
    "S1QualityForSide","FindOurPosition","OpenTrade","ManagePosition",
    "StartMinuteCycle","ArmOppositeAfterExit","ProcessEntries","Reconcile",
]
drift = [name for name in core_functions if fn(base_text, name) != fn(text, name)]
if drift:
    raise SystemExit("R9 CORE FUNCTION DRIFT: " + ", ".join(drift))

# Grid execution functions must never use the core CTrade or core magic.
grid_functions = [
    "OurPositionCount","FindNewestOurPosition","ManageAgeExits",
    "OpenSleeveTrade","GridInit","GridDeinit","GridReconcile",
]
for name in grid_functions:
    body = fn(text, name)
    if re.search(r"(?<!grid)\btrade\.", body):
        raise SystemExit(f"GRID FUNCTION READS CORE CTRADE: {name}")

# Position/trade lifecycle must never use the core magic. GridInit is allowed to
# read InpMagic only for the explicit collision guard.
for name in ["OurPositionCount","FindNewestOurPosition","ManageAgeExits","OpenSleeveTrade","GridDeinit","GridReconcile"]:
    if re.search(r"\bInpMagic\b", fn(text, name)):
        raise SystemExit(f"GRID LIFECYCLE READS CORE MAGIC: {name}")
if "InpGridMagic==InpMagic" not in fn(text, "GridInit"):
    raise SystemExit("MISSING CORE/GRID MAGIC COLLISION GUARD")

# Core behavior functions must not depend on gridTrade.
for name in core_functions:
    if "gridTrade." in fn(text, name):
        raise SystemExit(f"CORE FUNCTION CONTAMINATED BY GRID CTRADE: {name}")

if text.count("int OnInit()") != 1 or text.count("void OnTick()") != 1:
    raise SystemExit("MULTIPLE ENTRYPOINTS")
if text.count("CTrade trade;") != 1 or text.count("CTrade gridTrade;") != 1:
    raise SystemExit("TRADE OBJECT DECLARATION ERROR")

# Cheap structural sanity. Not a MetaEditor substitute.
if text.count("{") != text.count("}"):
    raise SystemExit("BRACE IMBALANCE")
if text.count("(") != text.count(")"):
    raise SystemExit("PAREN IMBALANCE")

for forbidden in ["gridgridTrade.", "InpGridGrid", "GRID_GRID_TAG"]:
    if forbidden in text:
        raise SystemExit(f"TRANSFORM ARTIFACT: {forbidden}")

print("PASS: R9 GAMMA-01 STMR Grid static integration QA")
print("parent_git_blob:", git_blob_sha)
print("core_functions_byte_equal:", len(core_functions))
print("required_contract_checks:", len(required))
print("ea_bytes:", EA.stat().st_size)
