from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
EA=ROOT/"Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"
src=EA.read_text(encoding="utf-8")

for token in [
    "struct DAAV1WatchdogCell",
    "int FindWatchdogCell",
    "bool RecordWatchdogRealizedOutcome",
    "double WatchdogRenewalGapForBin",
    "void AttachWatchdogToLatestEvent",
    "void ApplyWatchdogRegime",
    "InpWatchdogGoodStreak=4",
    "InpWatchdogGoodHoldSeconds=60",
    "InpWatchdogRenewalGap=1.19",
    "InpWatchdogLastSubphaseGap=1.10",
    "InpWatchdogMaxRenewalLayer=30",
    "ny_hour<12 || ny_hour>13",
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

@dataclass
class Cell:
    streak:int=0
    gate:bool=False
    unlocks:int=0
    relocks:int=0
    parents_seen:int=0
    parents_admitted:int=0

    def parent(self):
        first=self.parents_seen==0
        self.parents_seen+=1
        admitted=first or self.gate
        if admitted:
            self.parents_admitted+=1
        return first, admitted

    def outcome(self,pnl:float,hold:int):
        old=self.gate
        good=pnl>0 and hold<=60
        self.streak=self.streak+1 if good else 0
        self.gate=self.streak>=4
        if self.gate and not old:
            self.unlocks+=1
        if old and not self.gate:
            self.relocks+=1

def gap(bin10:int)->float:
    return 1.10 if bin10==5 else 1.19

c=Cell()
first,admitted=c.parent()
assert first and admitted
first,admitted=c.parent()
assert not first and not admitted

for _ in range(3):
    c.outcome(1.0,30)
    assert not c.gate
c.outcome(1.0,60)
assert c.gate and c.streak==4 and c.unlocks==1

first,admitted=c.parent()
assert not first and admitted

c.outcome(1.0,61)
assert not c.gate and c.streak==0 and c.relocks==1
first,admitted=c.parent()
assert not admitted

for b in range(5):
    assert gap(b)==1.19
assert gap(5)==1.10

# Source must encode New York DST transition UTC hours used by the historical lineage.
assert "NthSunday(d.year,3,2),7,0" in src
assert "NthSunday(d.year,11,1),6,0" in src

print("DAA V1 MT5 unit 004 Watchdog QA: PASS")
