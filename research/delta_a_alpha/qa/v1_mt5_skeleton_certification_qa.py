from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[3]
EA=ROOT/"Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"
STATE=ROOT/"CURRENT_STATE.json"

src=EA.read_text(encoding="utf-8")
state=json.loads(STATE.read_text(encoding="utf-8"))

assert '#property version   "1.05"' in src
assert 'input double InpLots=0.01;' in src
assert 'input bool   InpExecutionEnabled=false;' in src

required_functions=[
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
body=src[src.index("void OrchestrateV1"):src.index("bool InitMtfHandles")]
positions=[body.index(x) for x in required_functions]
assert positions==sorted(positions), positions

for token in [
    "struct DAAV1GridCycle",
    "struct DAAV1GridEventRecord",
    "struct DAAV1WatchdogCell",
    "struct DAAV1RecoveryWatch",
    "BuildProposalArbiter",
    "DIRECTION_CONFLICT",
    "FAILED_IGNITION_SHADOW",
    "NATIVE_MACRO_CONTINUATION",
    "ASIA_LOWER_TAKEOVER",
    "LONDON_M5_TAKEOVER",
    "OVERLAP_LOWER_TAKEOVER",
    "NY_LOWER_TRANSFER",
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

expected_spine=[
    "ordered ticks",
    "session-specific grid geometry",
    "completed H4/H1/M15/M5 structure",
    "London/overlap/NY hourly high-volume harvesting + separate Asia geometry",
    "Watchdog/regime renewal",
    "trend-within-trend native routing",
    "wrong-direction recovery",
    "portfolio heat/capital governor",
]
assert state["permanent_spine_v1"]["order"]==expected_spine
assert state["first_incomplete_unit"]=="DAA_VERTICAL_GRID_SYSTEM_V1_MT5_SKELETON_CERTIFICATION_007"

for rel in [
    "research/delta_a_alpha/mt5/DAA_VERTICAL_GRID_SYSTEM_V1_MT5_IMPLEMENTATION_001_REPORT.md",
    "research/delta_a_alpha/mt5/DAA_VERTICAL_GRID_SYSTEM_V1_MT5_SESSION_GEOMETRY_AND_EVENT_GENEALOGY_002_REPORT.md",
    "research/delta_a_alpha/mt5/DAA_VERTICAL_GRID_SYSTEM_V1_MT5_HOURLY_HARVEST_AND_ASIA_GEOMETRY_003_REPORT.md",
    "research/delta_a_alpha/mt5/DAA_VERTICAL_GRID_SYSTEM_V1_MT5_WATCHDOG_REGIME_RENEWAL_004_REPORT.md",
    "research/delta_a_alpha/mt5/DAA_VERTICAL_GRID_SYSTEM_V1_MT5_NATIVE_ROUTING_AND_RECOVERY_005_REPORT.md",
    "research/delta_a_alpha/mt5/DAA_VERTICAL_GRID_SYSTEM_V1_MT5_PROPOSAL_ARBITER_AND_HEAT_GOVERNOR_006_REPORT.md",
]:
    assert (ROOT/rel).exists(), rel

print("DAA V1 MT5 skeleton certification 007: PASS")
