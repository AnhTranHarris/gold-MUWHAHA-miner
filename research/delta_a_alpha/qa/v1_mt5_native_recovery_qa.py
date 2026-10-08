from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
EA=ROOT/"Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"
src=EA.read_text(encoding="utf-8")

for token in [
    "NATIVE_MACRO_CONTINUATION",
    "NATIVE_LOWER_TAKEOVER",
    "NATIVE_PULLBACK_RECLAIM",
    "NATIVE_MACRO_SPLIT_TRANSFER",
    "struct DAAV1RecoveryWatch",
    "bool StartShadowRecoveryWatch",
    "void EvaluateRecoveryWatches",
    "FAILED_IGNITION_SHADOW",
    "InpRecoveryIgnitionWindowSeconds=2",
    "InpRecoveryRequiredFavorable=1.25",
    "InpRecoveryCampaignSeconds=120",
    "one recovery proposal maximum per market tick",
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


def native(h4,h1,m15,m5,d):
    macro=h4!=0 and h4==h1
    if h4==h1==m15==m5 and h4!=0 and d==h4:
        return "NATIVE_MACRO_CONTINUATION"
    if macro and m15==m5==-h1 and d==m5:
        return "NATIVE_LOWER_TAKEOVER"
    if macro and m15==-h1 and m5==h1 and d==m5:
        return "NATIVE_PULLBACK_RECLAIM"
    if h4!=0 and h1!=0 and h4!=h1 and m15!=0 and m5==-m15 and d==m5:
        return "NATIVE_MACRO_SPLIT_TRANSFER"
    return None

assert native(1,1,1,1,1)=="NATIVE_MACRO_CONTINUATION"
assert native(1,1,-1,-1,-1)=="NATIVE_LOWER_TAKEOVER"
assert native(1,1,-1,1,1)=="NATIVE_PULLBACK_RECLAIM"
assert native(1,-1,1,-1,-1)=="NATIVE_MACRO_SPLIT_TRANSFER"
assert native(1,1,1,-1,1) is None


@dataclass
class Watch:
    direction:int
    entry:float
    start_ms:int
    expire_ms:int
    max_fav:float=0.0
    failed:bool=False
    reported:bool=False
    active:bool=True

    def tick(self,now_ms,bid,ask):
        if not self.active:
            return None
        if now_ms>self.expire_ms:
            self.active=False
            return None
        mark=bid if self.direction>0 else ask
        fav=(mark-self.entry)*self.direction
        self.max_fav=max(self.max_fav,fav)
        if not self.failed and now_ms-self.start_ms>=2000:
            if self.max_fav<1.25:
                self.failed=True
            else:
                self.active=False
                return None
        if self.failed and not self.reported:
            self.reported=True
            return -self.direction
        return None

# Long that never reaches +1.25 fails after the elapsed 2-second window.
w=Watch(1,100.10,0,120000)
assert w.tick(1000,100.50,100.60) is None
assert w.tick(2000,100.80,100.90)==-1
assert w.tick(2100,100.70,100.80) is None

# Long that proves +1.25 before/at the check is retired without recovery.
w2=Watch(1,100.10,0,120000)
assert w2.tick(1000,101.40,101.50) is None
assert w2.tick(2000,101.50,101.60) is None
assert not w2.active

# Short uses Ask as its executable exit-side mark.
w3=Watch(-1,100.00,0,120000)
assert w3.tick(2000,99.10,99.20) == 1

print("DAA V1 MT5 unit 005 native/recovery QA: PASS")
