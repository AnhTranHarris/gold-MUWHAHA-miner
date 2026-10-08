from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EA = ROOT / "Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5"
src = EA.read_text(encoding="utf-8")

required_routes = [
    "ASIA_LOWER_TAKEOVER",
    "ASIA_M15_DIVERGE_M5_RECLAIM",
    "LONDON_M5_TAKEOVER",
    "LONDON_M5_RECLAIM",
    "OVERLAP_LOWER_TAKEOVER",
    "OVERLAP_ALIGNED_COUNTERCROSS",
    "NY_LOWER_TRANSFER",
    "NY_LOWER_COUNTERCROSS",
    "LATE_ALIGNED_MOMENTUM",
    "LATE_MACRO_SPLIT_TRANSFER",
    "LATE_M5_REJECTION",
    "LATE_LOWER_TAKEOVER",
]
for route in required_routes:
    assert route in src, route

for token in [
    "void SetRoute",
    "void AttachRouteToLatestEvent",
    "int UtcHour",
    "int UtcSubphase10m",
    "void ApplyHourlyHarvest",
    "c.route_hour_utc=UtcHour(c.utc_ms)",
    "c.route_subphase_10m=UtcSubphase10m(c.utc_ms)",
]:
    assert token in src, token

body = src[src.index("void OrchestrateV1"):src.index("bool InitMtfHandles")]
order = [
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
pos = [body.index(x) for x in order]
assert pos == sorted(pos), pos

for forbidden in (
    "g_trade.Buy(",
    "g_trade.Sell(",
    "g_trade.PositionOpen(",
    "trade.Buy(",
    "trade.Sell(",
):
    assert forbidden not in src, forbidden


@dataclass(frozen=True)
class C:
    session: str
    d: int
    h4: int
    h1: int
    m15: int
    m5: int
    hour: int
    event: bool = True
    mtf_ready: bool = True


def route(c: C) -> str | None:
    if not c.event or not c.mtf_ready:
        return None
    if c.session in {"LONDON_OPEN", "ROLLOVER"} or c.d == 0:
        return None

    macro = c.h4 != 0 and c.h4 == c.h1

    if c.session == "ASIA":
        if macro and c.m15 == c.m5 == -c.h1 and c.d == c.m5 and c.hour == 23:
            return "ASIA_LOWER_TAKEOVER"
        if macro and c.m15 == -c.h1 and c.m5 == c.h1 and c.d == c.m5:
            return "ASIA_M15_DIVERGE_M5_RECLAIM"

    if c.session == "LONDON":
        if macro and c.m15 == c.h1 and c.m5 == -c.h1 and c.d == c.m5 and c.hour == 11:
            return "LONDON_M5_TAKEOVER"
        if macro and c.m15 == -c.h1 and c.m5 == c.h1 and c.d == c.m5:
            return "LONDON_M5_RECLAIM"

    if c.session == "OVERLAP":
        if macro and c.m15 == c.m5 == -c.h1 and c.d == c.m5:
            return "OVERLAP_LOWER_TAKEOVER"
        if macro and c.m15 == c.m5 == c.h1 and c.d == -c.m5:
            return "OVERLAP_ALIGNED_COUNTERCROSS"

    if c.session == "NEW_YORK":
        if c.h4 != 0 and c.h1 != 0 and c.h4 != c.h1 and c.m15 != 0 and c.m5 == -c.m15 and c.d == c.m5:
            return "NY_LOWER_TRANSFER"
        if c.h4 != 0 and c.h1 != 0 and c.h4 != c.h1 and c.m15 == c.m5 and c.m15 != 0 and c.d == -c.m5:
            return "NY_LOWER_COUNTERCROSS"

    if c.session == "LATE_NY":
        if c.h4 == c.h1 == c.m15 == c.m5 and c.h4 != 0 and c.d == c.m5:
            return "LATE_ALIGNED_MOMENTUM"
        if c.h4 != 0 and c.h1 != 0 and c.h4 != c.h1 and c.m15 != 0 and c.m5 == -c.m15 and c.d == c.m5:
            return "LATE_MACRO_SPLIT_TRANSFER"
        if macro and c.m15 == c.h1 and c.m5 == -c.h1 and c.d == -c.m5:
            return "LATE_M5_REJECTION"
        if macro and c.m15 == c.m5 == -c.h1 and c.d == c.m5:
            return "LATE_LOWER_TAKEOVER"

    return None


cases = [
    (C("ASIA", -1, 1, 1, -1, -1, 23), "ASIA_LOWER_TAKEOVER"),
    (C("ASIA", -1, 1, 1, -1, -1, 1), None),
    (C("ASIA", 1, 1, 1, -1, 1, 2), "ASIA_M15_DIVERGE_M5_RECLAIM"),
    (C("LONDON", -1, 1, 1, 1, -1, 11), "LONDON_M5_TAKEOVER"),
    (C("LONDON", -1, 1, 1, 1, -1, 10), None),
    (C("LONDON", 1, 1, 1, -1, 1, 10), "LONDON_M5_RECLAIM"),
    (C("OVERLAP", -1, 1, 1, -1, -1, 14), "OVERLAP_LOWER_TAKEOVER"),
    (C("OVERLAP", -1, 1, 1, 1, 1, 14), "OVERLAP_ALIGNED_COUNTERCROSS"),
    (C("NEW_YORK", -1, 1, -1, 1, -1, 17), "NY_LOWER_TRANSFER"),
    (C("NEW_YORK", 1, 1, -1, -1, -1, 17), "NY_LOWER_COUNTERCROSS"),
    (C("LATE_NY", 1, 1, 1, 1, 1, 21), "LATE_ALIGNED_MOMENTUM"),
    (C("LATE_NY", -1, 1, -1, 1, -1, 21), "LATE_MACRO_SPLIT_TRANSFER"),
    (C("LATE_NY", 1, 1, 1, 1, -1, 21), "LATE_M5_REJECTION"),
    (C("LATE_NY", -1, 1, 1, -1, -1, 21), "LATE_LOWER_TAKEOVER"),
    (C("ROLLOVER", 1, 1, 1, 1, 1, 22), None),
    (C("LONDON_OPEN", 1, 1, 1, 1, 1, 8), None),
    (C("LONDON", -1, 1, 1, 1, -1, 11, event=False), None),
]
for c, expected in cases:
    got = route(c)
    assert got == expected, (c, got, expected)

print("DAA V1 MT5 unit 003 hourly/Asia route QA: PASS")
