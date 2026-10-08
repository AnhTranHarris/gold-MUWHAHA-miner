from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3]
EA=ROOT/"Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"
STATE=ROOT/"CURRENT_STATE.json"
MANIFEST=ROOT/"research/delta_a_alpha/artifacts/DAA_VERTICAL_GRID_SYSTEM_V1_MANIFEST.json"

src=EA.read_text(encoding="utf-8")
state=json.loads(STATE.read_text(encoding="utf-8"))
manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))

required=[
    "void ApplySessionGeometry",
    "void RefreshCompletedMTF",
    "void ApplyHourlyHarvest",
    "void ApplyWatchdogRegime",
    "void ApplyTrendWithinTrend",
    "void ApplyWrongDirectionRecovery",
    "void ApplyCapitalGovernor",
    "void OrchestrateV1",
    "input double InpLots=0.01",
    "input bool   InpExecutionEnabled=false",
]
for token in required:
    assert token in src, token

body=src[src.index("void OrchestrateV1"):src.index("bool InitMtfHandles")]
order=[
    "TickToUtcMs",
    "ApplySessionGeometry",
    "RefreshCompletedMTF",
    "ApplyHourlyHarvest",
    "ApplyWatchdogRegime",
    "ApplyTrendWithinTrend",
    "ApplyWrongDirectionRecovery",
    "ApplyCapitalGovernor",
    "WriteDiagnostic",
]
pos=[body.index(x) for x in order]
assert pos==sorted(pos), pos

# Unit 001 must remain observe-only: no trade.Buy/Sell/PositionOpen calls.
for forbidden in ("g_trade.Buy(", "g_trade.Sell(", "g_trade.PositionOpen(", "trade.Buy(", "trade.Sell("):
    assert forbidden not in src, forbidden

assert state["permanent_spine_v1"]["status"]=="OWNER_FROZEN_PERMANENT_ARCHITECTURE"
assert state["mt5_v1"]["status"]=="IMPLEMENTATION_STARTED"
assert manifest["mt5"]["authorized"] is True
assert manifest["permanent_spine"][0]=="ordered_ticks"
assert manifest["permanent_spine"][-1]=="portfolio_heat_capital_governor"

print("DAA V1 MT5 architecture static QA: PASS")
