from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping

PRICE_SCALE = 100  # Coinexx XAUUSD: 0.01 price point.


def parse_price_units(text: str, scale: int = PRICE_SCALE) -> int:
    """Parse a decimal price string to exact integer price units without float drift."""
    s = text.strip()
    if not s:
        return 0
    neg = s.startswith("-")
    if neg:
        s = s[1:]
    whole, dot, frac = s.partition(".")
    decimals = len(str(scale)) - 1
    if dot and any(ch != "0" for ch in frac[decimals:]):
        raise ValueError(f"price {text!r} is not exactly representable at scale {scale}")
    frac = (frac + "0" * decimals)[:decimals]
    units = int(whole or "0") * scale + int(frac or "0")
    return -units if neg else units


def format_price_units(units: int, scale: int = PRICE_SCALE) -> str:
    neg = units < 0
    u = abs(units)
    decimals = len(str(scale)) - 1
    s = f"{u // scale}.{u % scale:0{decimals}d}"
    return "-" + s if neg else s


@dataclass(frozen=True, slots=True)
class Tick:
    ordinal: int
    time_s: int
    time_msc: int
    bid_u: int
    ask_u: int
    last_u: int = 0
    volume: int = 0
    volume_real: str = "0"
    flags: int = 0
    source_extras: Mapping[str, str] = field(default_factory=dict, compare=False)

    @property
    def bid(self) -> float:
        return self.bid_u / PRICE_SCALE

    @property
    def ask(self) -> float:
        return self.ask_u / PRICE_SCALE

    @property
    def spread_points(self) -> int:
        return self.ask_u - self.bid_u


@dataclass(frozen=True, slots=True)
class SecondBar:
    second: int
    first_time_msc: int
    last_time_msc: int
    tick_count: int
    bid_open_u: int
    bid_high_u: int
    bid_low_u: int
    bid_close_u: int
    ask_open_u: int
    ask_high_u: int
    ask_low_u: int
    ask_close_u: int
    spread_open: int
    spread_high: int
    spread_low: int
    spread_close: int


@dataclass(frozen=True, slots=True)
class Trade:
    entry_ordinal: int
    entry_time_msc: int
    side: int
    entry_price_u: int
    initial_sl_u: int
    exit_ordinal: int
    exit_time_msc: int
    exit_price_u: int
    reason: str
    net_price_u: int
    rearm_number: int
