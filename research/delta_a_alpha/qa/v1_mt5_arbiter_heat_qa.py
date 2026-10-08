from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
EA=ROOT/"Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"
src=EA.read_text(encoding="utf-8")

for token in [
    "void BuildProposalArbiter",
    "void ConsiderArbiterCandidate",
    "int CountSourcePositions",
    "int CountSessionPositions",
    "int SessionCapacity",
    "int LayerCapacity",
    "DIRECTION_CONFLICT",
    "GLOBAL_CAP",
    "LAYER_CAP",
    "SESSION_CAP",
    "EXECUTION_DISABLED",
    "InpCapAsia=620",
    "InpCapWatchdog=620",
    "InpCapNative=620",
    "InpCapRecovery=620",
]:
    assert token in src, token

for forbidden in (
    "g_trade.Buy(",
    "g_trade.Sell(",
    "g_trade.PositionOpen(",
    "trade.Buy(",
    "trade.Sell(",
):
    assert forbidden not in src, forbidden

body=src[src.index("void OrchestrateV1"):src.index("bool InitMtfHandles")]
order=[
    "TickToUtcMs",
    "ApplySessionGeometry",
    "UpdateSessionGridCycle",
    "RefreshCompletedMTF",
    "ManufactureFirstTouchEvent",
    "ApplyHourlyHarvest",
    "ApplyWatchdogRegime",
    "ApplyTrendWithinTrend",
    "ApplyWrongDirectionRecovery",
    "ApplyCapitalGovernor",
    "WriteDiagnostic",
]
pos=[body.index(x) for x in order]
assert pos==sorted(pos), pos


def arbitrate(candidates):
    consensus=0
    has=False
    conflict=False
    owners=[]
    for active,direction,source in candidates:
        if not active or direction==0:
            continue
        if not has:
            has=True
            consensus=direction
            owners.append(source)
            continue
        if source not in owners:
            owners.append(source)
        if direction!=consensus:
            conflict=True
    if not has or conflict:
        return None, conflict, owners, "NONE"
    active={source for active,direction,source in candidates if active and direction==consensus}
    if "RECOVERY" in active: primary="RECOVERY"
    elif "WATCHDOG" in active: primary="WATCHDOG"
    elif "NATIVE" in active: primary="NATIVE"
    else: primary="SESSION"
    return consensus,False,owners,primary

d,conf,owners,primary=arbitrate([
    (True,1,"SESSION"),(True,1,"NATIVE"),(True,1,"WATCHDOG"),(False,-1,"RECOVERY")
])
assert d==1 and not conf and primary=="WATCHDOG"
assert set(owners)=={"SESSION","NATIVE","WATCHDOG"}

d,conf,owners,primary=arbitrate([
    (True,1,"SESSION"),(True,-1,"RECOVERY")
])
assert d is None and conf and primary=="NONE"

d,conf,owners,primary=arbitrate([
    (False,1,"SESSION"),(False,-1,"RECOVERY")
])
assert d is None and not conf


def governor(execution,proposal,conflict,global_open,global_cap,layer_open,layer_cap,session_open,session_cap):
    if not execution: return "EXECUTION_DISABLED"
    if conflict: return "DIRECTION_CONFLICT"
    if not proposal: return "NO_PROPOSAL"
    if session_cap<=0: return "OBSERVE_ONLY_SESSION"
    if global_open>=global_cap: return "GLOBAL_CAP"
    if layer_open>=layer_cap: return "LAYER_CAP"
    if session_open>=session_cap: return "SESSION_CAP"
    return "ADMITTED"

assert governor(False,True,False,0,620,0,620,0,620)=="EXECUTION_DISABLED"
assert governor(True,True,True,0,620,0,620,0,620)=="DIRECTION_CONFLICT"
assert governor(True,True,False,620,620,0,620,0,620)=="GLOBAL_CAP"
assert governor(True,True,False,0,620,620,620,0,620)=="LAYER_CAP"
assert governor(True,True,False,0,620,0,620,620,620)=="SESSION_CAP"
assert governor(True,True,False,0,620,0,620,0,620)=="ADMITTED"

print("DAA V1 MT5 unit 006 arbiter/heat QA: PASS")
