from __future__ import annotations
import collections
import datetime as dt
from dataclasses import asdict, dataclass
from .bars import CompletedM5Atr, SecondBarBuilder
from .models import Tick, Trade

@dataclass(frozen=True, slots=True)
class R9Config:
    lots: float = 0.01
    gap_pips: int = 30
    stop_loss_pips: int = 30
    trailing_enabled: bool = True
    trail_pips: int = 3
    trail_activation_pips: int = 10
    max_hold_seconds: int = 30
    max_same_minute_rearms: int = 3
    magic: int = 5559
    velocity_lookback_sec: int = 10
    min_velocity_pips: int = 15
    min_directional_eff: float = 0.70
    range_lookback_sec: int = 10
    min_range_pips: int = 50
    max_turns: int = 9
    use_regime_gate: bool = True
    atr_period: int = 14
    max_spread_points: int = 25
    fail_closed_on_no_atr: bool = True
    use_session_adaptive_atr: bool = True
    quote_utc_offset_minutes: int = 0
    atr_london_price: float = 2.00
    atr_overlap_price: float = 1.75
    atr_new_york_price: float = 1.75
    atr_off_session_price: float = 2.50
    hunter_pip_price: float = 0.01
    respect_broker_stops: bool = True
    broker_stops_points: int = 0
    tick_size_points: int = 1

    def validate(self) -> None:
        if self.hunter_pip_price != 0.01:
            raise ValueError("Coinexx R9 integer-point engine currently requires InpHunterPipPrice=0.01")
        if self.tick_size_points <= 0:
            raise ValueError("tick_size_points must be positive")
        if self.velocity_lookback_sec < 2 or self.range_lookback_sec < 2:
            raise ValueError("lookbacks must be >=2")
        if max(self.velocity_lookback_sec, self.range_lookback_sec) >= 128:
            raise ValueError("lookbacks must remain below MICRO_CAPACITY=128")


def _nth_sunday(year: int, month: int, nth: int) -> int:
    first = dt.datetime(year, month, 1, tzinfo=dt.timezone.utc)
    return 1 + (6 - first.weekday()) % 7 + (nth - 1) * 7


def _last_sunday(year: int, month: int) -> int:
    if month == 12:
        nxt = dt.datetime(year + 1, 1, 1, tzinfo=dt.timezone.utc)
    else:
        nxt = dt.datetime(year, month + 1, 1, tzinfo=dt.timezone.utc)
    last = nxt - dt.timedelta(days=1)
    return last.day - (last.weekday() + 1) % 7


def _session_code_minute(source_native_minute: int, quote_utc_offset_minutes: int) -> int:
    utc_s = source_native_minute - quote_utc_offset_minutes * 60
    utc = dt.datetime.fromtimestamp(utc_s, dt.timezone.utc)
    y = utc.year
    london_start = dt.datetime(y, 3, _last_sunday(y, 3), 1, tzinfo=dt.timezone.utc)
    london_end = dt.datetime(y, 10, _last_sunday(y, 10), 1, tzinfo=dt.timezone.utc)
    ny_start = dt.datetime(y, 3, _nth_sunday(y, 3, 2), 7, tzinfo=dt.timezone.utc)
    ny_end = dt.datetime(y, 11, _nth_sunday(y, 11, 1), 6, tzinfo=dt.timezone.utc)
    lo_offset = 60 if london_start <= utc < london_end else 0
    ny_offset = -240 if ny_start <= utc < ny_end else -300
    l = utc + dt.timedelta(minutes=lo_offset)
    n = utc + dt.timedelta(minutes=ny_offset)
    lm = l.hour * 60 + l.minute
    nm = n.hour * 60 + n.minute
    in_l = 8 * 60 <= lm < 16 * 60 + 30
    in_n = 8 * 60 <= nm < 17 * 60
    if in_l and in_n:
        return 2
    if in_l:
        return 1
    if in_n:
        return 3
    return 0


def session_code(source_native_s: int, quote_utc_offset_minutes: int = 0) -> int:
    """Mirror CurrentSession() on source-native server time, cached per minute.

    R9 v1.90 compares only hour/minute session boundaries, so all seconds inside a
    source minute have the same result. The cache changes no formula or timestamp.
    """
    source_native_minute = source_native_s - source_native_s % 60
    return _session_code_minute(source_native_minute, quote_utc_offset_minutes)


@dataclass(slots=True)
class _Position:
    side: int
    entry_ordinal: int
    entry_time_msc: int
    entry_time_s: int
    entry_price_u: int
    initial_sl_u: int
    sl_u: int
    rearm_number: int


class R9HybridGateBaseline:
    """Source-faithful Python state machine for GoldMuwahahaMiner_R9_HybridGate v1.90."""
    def __init__(self, config: R9Config | None = None) -> None:
        self.cfg = config or R9Config()
        self.cfg.validate()
        self.second_builder = SecondBarBuilder()
        self.micro = collections.deque(maxlen=128)
        self.atr = CompletedM5Atr(self.cfg.atr_period)
        self.cycle_minute = 0
        self.cycle_buy_u = 0
        self.cycle_sell_u = 0
        self.pending_mode = 0
        self.rearms = 0
        self.had_position = False
        self.last_position_side = 1
        self.position: _Position | None = None
        self.trades: list[Trade] = []
        self.entries: list[dict[str, int]] = []
        self.stats = collections.Counter()
        self._session_cache_minute: int | None = None
        self._session_cache_min_u: float = 0.0

    @staticmethod
    def _round_half_positive(numerator: int, denominator: int = 2) -> int:
        q, r = divmod(numerator, denominator)
        return q + (1 if 2 * r >= denominator else 0)

    def _start_minute_cycle(self, t: Tick) -> None:
        minute = t.time_s - t.time_s % 60
        if minute == self.cycle_minute:
            return
        self.cycle_minute = minute
        self.rearms = 0
        self.pending_mode = 2
        self.cycle_buy_u = self._round_half_positive(t.bid_u + t.ask_u + self.cfg.gap_pips, 2)
        self.cycle_sell_u = self._round_half_positive(t.bid_u + t.ask_u - self.cfg.gap_pips, 2)

    def _push_second(self, t: Tick) -> None:
        completed = self.second_builder.update(t)
        if completed is not None:
            self.micro.append(completed)

    def _quality(self, side: int) -> bool:
        c = self.cfg
        need = max(c.velocity_lookback_sec, c.range_lookback_sec) + 1
        if len(self.micro) < need:
            return False
        arr = list(self.micro)
        recent_vel = arr[-c.velocity_lookback_sec:]
        closes = [x.bid_close_u for x in recent_vel]
        disp = closes[-1] - closes[0]
        travel = sum(abs(b - a) for a, b in zip(closes, closes[1:]))
        eff = abs(disp) / (travel + 1e-9)
        prev_sign = 0
        turns = 0
        for a, b in zip(closes, closes[1:]):
            sign = 1 if b > a else -1 if b < a else 0
            if sign:
                if prev_sign and sign != prev_sign:
                    turns += 1
                prev_sign = sign
        recent_rng = arr[-c.range_lookback_sec:]
        range_u = max(x.bid_high_u for x in recent_rng) - min(x.bid_low_u for x in recent_rng)
        if eff + 1e-12 < c.min_directional_eff:
            return False
        if turns > c.max_turns:
            return False
        if range_u < c.min_range_pips:
            return False
        if side > 0 and disp < c.min_velocity_pips:
            return False
        if side < 0 and disp > -c.min_velocity_pips:
            return False
        return True

    def _session_atr_min_u(self, source_native_s: int) -> float:
        c = self.cfg
        if not c.use_session_adaptive_atr:
            return c.atr_london_price * 100.0
        minute = source_native_s - source_native_s % 60
        if minute == self._session_cache_minute:
            return self._session_cache_min_u
        s = session_code(minute, c.quote_utc_offset_minutes)
        if s == 2:
            value = c.atr_overlap_price * 100.0
        elif s == 3:
            value = c.atr_new_york_price * 100.0
        elif s == 1:
            value = c.atr_london_price * 100.0
        else:
            value = c.atr_off_session_price * 100.0
        self._session_cache_minute = minute
        self._session_cache_min_u = value
        return value

    def _gate(self, t: Tick) -> bool:
        c = self.cfg
        if not c.use_regime_gate:
            return True
        if c.max_spread_points > 0 and t.spread_points > c.max_spread_points:
            self.stats["gate_spread"] += 1
            return False
        if not self.atr.ready:
            self.stats["gate_no_atr"] += 1
            return not c.fail_closed_on_no_atr
        if self.atr.atr_u is not None and self.atr.atr_u + 1e-12 < self._session_atr_min_u(t.time_s):
            self.stats["gate_low_atr"] += 1
            return False
        return True

    def _broker_stop_before_ea(self, t: Tick) -> None:
        p = self.position
        if p is None:
            return
        hit = (p.side > 0 and t.bid_u <= p.sl_u) or (p.side < 0 and t.ask_u >= p.sl_u)
        if hit:
            exit_u = t.bid_u if p.side > 0 else t.ask_u
            self._record_close(t, "stop", exit_u)

    def _record_close(self, t: Tick, reason: str, exit_u: int) -> None:
        p = self.position
        if p is None:
            return
        net_u = (exit_u - p.entry_price_u) * p.side
        self.trades.append(Trade(
            entry_ordinal=p.entry_ordinal,
            entry_time_msc=p.entry_time_msc,
            side=p.side,
            entry_price_u=p.entry_price_u,
            initial_sl_u=p.initial_sl_u,
            exit_ordinal=t.ordinal,
            exit_time_msc=t.time_msc,
            exit_price_u=exit_u,
            reason=reason,
            net_price_u=net_u,
            rearm_number=p.rearm_number,
        ))
        self.stats[f"closed_{reason}"] += 1
        self.position = None

    def _manage_position(self, t: Tick) -> None:
        p = self.position
        if p is None:
            return
        c = self.cfg
        if t.time_s - p.entry_time_s >= c.max_hold_seconds:
            self._record_close(t, "timeout", t.bid_u if p.side > 0 else t.ask_u)
            return
        if not c.trailing_enabled or c.trail_pips <= 0:
            return
        broker = c.broker_stops_points if c.respect_broker_stops else 0
        ts = c.tick_size_points
        if p.side > 0 and t.bid_u - p.entry_price_u >= c.trail_activation_pips:
            cand = t.bid_u - c.trail_pips
            cand = min(cand, t.bid_u - broker - ts)
            if cand > p.sl_u + ts * 0.5:
                p.sl_u = cand
                self.stats["trail_updates"] += 1
        elif p.side < 0 and p.entry_price_u - t.ask_u >= c.trail_activation_pips:
            cand = t.ask_u + c.trail_pips
            cand = max(cand, t.ask_u + broker + ts)
            if cand < p.sl_u - ts * 0.5:
                p.sl_u = cand
                self.stats["trail_updates"] += 1

    def _arm_opposite_after_exit(self) -> None:
        if self.rearms >= self.cfg.max_same_minute_rearms:
            self.pending_mode = 0
            return
        self.rearms += 1
        self.pending_mode = 1 if self.last_position_side < 0 else -1
        self.stats["rearms"] += 1

    def _open_trade(self, t: Tick, side: int) -> None:
        c = self.cfg
        broker_min = c.broker_stops_points + c.tick_size_points if c.respect_broker_stops else 0
        stop_distance = max(c.stop_loss_pips, broker_min)
        sl_u = t.bid_u - stop_distance if side > 0 else t.ask_u + stop_distance
        entry_u = t.ask_u if side > 0 else t.bid_u
        self.position = _Position(
            side=side,
            entry_ordinal=t.ordinal,
            entry_time_msc=t.time_msc,
            entry_time_s=t.time_s,
            entry_price_u=entry_u,
            initial_sl_u=sl_u,
            sl_u=sl_u,
            rearm_number=self.rearms,
        )
        self.entries.append({
            "ordinal": t.ordinal,
            "time_msc": t.time_msc,
            "side": side,
            "price_u": entry_u,
            "sl_u": sl_u,
            "cycle_minute": self.cycle_minute,
            "rearm_number": self.rearms,
        })
        self.pending_mode = 0
        self.stats["entries"] += 1

    def _process_entries(self, t: Tick) -> None:
        if self.pending_mode == 0 or not self._gate(t):
            return
        side = 0
        if self.pending_mode in (2, 1) and t.ask_u >= self.cycle_buy_u:
            side = 1
        elif self.pending_mode in (2, -1) and t.bid_u <= self.cycle_sell_u:
            side = -1
        if side == 0:
            return
        if not self._quality(side):
            self.stats["gate_s1"] += 1
            return
        self._open_trade(t, side)

    def on_tick(self, t: Tick) -> None:
        self._broker_stop_before_ea(t)
        self._push_second(t)
        self.atr.update(t)
        self._start_minute_cycle(t)

        if self.position is not None:
            self.had_position = True
            self.last_position_side = self.position.side
            self._manage_position(t)
            return

        if self.had_position:
            self.had_position = False
            now_minute = t.time_s - t.time_s % 60
            if now_minute == self.cycle_minute:
                self._arm_opposite_after_exit()
            else:
                self.pending_mode = 0
            return

        self._process_entries(t)

    def config_dict(self) -> dict:
        return asdict(self.cfg)
