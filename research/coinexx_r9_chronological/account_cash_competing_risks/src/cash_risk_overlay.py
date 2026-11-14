"""Coinexx-only account-currency competing-risk outcome overlay on ORIGINAL R9.

No new tick engine: delegates the entire position lifecycle to the pinned
coinexx_r9.R9HybridGateBaseline one source-ordered quote at a time.
The extra hypothetical favorable cash goal is OBSERVED, not traded.
Do NOT interpret the overlay as an executable counterfactual portfolio: an
early goal exit would change subsequent R9 occupancy and opposite re-arms.

Only genuine Bid/Ask liquidation sides are valued (BUY Ask->Bid,
SELL Bid->Ask). Raw ticks have no fills, commission or account currency.
Those are explicit user-provided cost/profit calibration assumptions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil, isfinite
from typing import Iterable

from coinexx_r9.models import Tick, Trade
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline, session_code

CAUSE_TARGET = "GOAL_BEFORE_R9_EXIT"
CAUSE_STOP = "R9_STOP_BEFORE_GOAL"
CAUSE_TIMEOUT = "R9_TIMEOUT_BEFORE_GOAL"
CAUSE_GAP = "CENSORED_QUOTE_GAP"
CAUSE_EOF = "CENSORED_SOURCE_END"
EVENT_CAUSES = (CAUSE_TARGET, CAUSE_STOP, CAUSE_TIMEOUT)
CENSORED = (CAUSE_GAP, CAUSE_EOF)


@dataclass(frozen=True)
class CashAssumptions:
    """Monetary parameters in MT5 ACCOUNT currency for the configured lot size."""
    account_currency: str
    cash_per_one_xau_price_dollar: float
    round_trip_cost_cash: float
    goal_net_cash: float = 1.75
    max_hold_ms: int = 30000
    max_quote_gap_ms: int = 10000

    def __post_init__(self):
        if (not self.account_currency or len(self.account_currency) != 3
                or not self.account_currency.isalpha()):
            raise ValueError("Specify the real 3-letter MT5 account currency")
        for name in ("cash_per_one_xau_price_dollar", "round_trip_cost_cash", "goal_net_cash"):
            val = getattr(self, name)
            if not isfinite(val) or val < 0:
                raise ValueError(f"{name} must be finite nonnegative account currency")
        if self.cash_per_one_xau_price_dollar <= 0 or self.goal_net_cash <= 0:
            raise ValueError("Cash conversion and goal must be strictly positive")
        if self.max_hold_ms <= 0 or self.max_quote_gap_ms <= 0:
            raise ValueError("Positive horizon/gap required")

    @property
    def required_favorable_cents(self) -> int:
        """From the ASK/ BID entry to opposing liquidation quote, spread included once."""
        exact = (self.goal_net_cash + self.round_trip_cost_cash) * 100.0
        return max(1, ceil(exact/self.cash_per_one_xau_price_dollar - 1e-10))

    def net_cash(self, net_price_cents: int) -> float:
        return (net_price_cents / 100.0) * self.cash_per_one_xau_price_dollar - self.round_trip_cost_cash


@dataclass
class Episode:
    entry_ordinal: int
    entry_time_msc: int
    source_hour: int
    session: int
    side: int
    entry_price_cents: int
    entry_spread_cents: int
    cause: str | None = None
    event_time_ms: int | None = None
    observed_goal_cash: float | None = None
    exit_ordinal: int | None = None
    exit_time_msc: int | None = None
    exit_reason: str | None = None
    baseline_net_cash: float | None = None
    overlay_net_cash: float | None = None
    max_favorable_net_cash: float | None = None
    max_adverse_net_cash: float | None = None

    def as_row(self) -> dict:
        return asdict(self)


class R9CashRiskOverlay:
    """Source-ordinal stream observer for the original unchanged R9 base policy.

    Each episode's competing event is first target quote, first original R9 stop,
    first original R9 timeout, or right censor. No feature uses future quotes.
    """

    def __init__(self, cash: CashAssumptions, config: R9Config | None = None):
        self.cash = cash
        self.base = R9HybridGateBaseline(config or R9Config())
        if self.base.cfg.max_hold_seconds*1000 != cash.max_hold_ms:
            raise ValueError("Research horizon must match unmodified R9 timeout")
        self.completed: list[Episode] = []
        self.current: Episode | None = None
        self._last_ordinal = -1
        self._last_time_msc = -1
        self._latest_quote_for_position: int | None = None
        self.ticks_seen = 0

    def _open(self, tick: Tick) -> None:
        p = self.base.position
        if p is None:
            raise RuntimeError("R9 position was expected at entry")
        if self.current is not None:
            raise RuntimeError("Multiple active positions: baseline parity broken")
        self.current = Episode(
            entry_ordinal=p.entry_ordinal,
            entry_time_msc=p.entry_time_msc,
            source_hour=(tick.time_s // 3600) % 24,
            session=session_code(tick.time_s, self.base.cfg.quote_utc_offset_minutes),
            side=p.side,
            entry_price_cents=p.entry_price_u,
            entry_spread_cents=tick.ask_u-tick.bid_u,
        )
        self._latest_quote_for_position = tick.time_msc
        # Immediate liquidation at entry incurs spread; there is no free mid fill.
        self._observe_cash(self.cash.net_cash(-(tick.ask_u-tick.bid_u)))

    def _observe_cash(self, value: float) -> None:
        e = self.current
        if e is None:
            return
        e.max_favorable_net_cash = (value if e.max_favorable_net_cash is None
                                    else max(value, e.max_favorable_net_cash))
        e.max_adverse_net_cash = (value if e.max_adverse_net_cash is None
                                  else min(value, e.max_adverse_net_cash))

    def _observe_before_base_tick(self, tick: Tick) -> None:
        e = self.current
        p = self.base.position
        if e is None or p is None:
            raise RuntimeError("Position/cash observation state desynchronized")
        if e.entry_ordinal != p.entry_ordinal:
            raise RuntimeError("Entry ordinal mismatch")
        if self._latest_quote_for_position is None:
            raise RuntimeError("No prior position quote timestamp")
        age = tick.time_msc-e.entry_time_msc
        if age < 0:
            raise ValueError("Backward quote timestamp inside R9 position")
        gap = tick.time_msc-self._latest_quote_for_position
        if gap > self.cash.max_quote_gap_ms and e.cause is None:
            # Do NOT score the first quote after a long undocumented gap as
            # if it were continuously observed executable liquidity.
            e.cause = CAUSE_GAP
            e.event_time_ms = min(self.cash.max_hold_ms,
                                  self._latest_quote_for_position-e.entry_time_msc)
        self._latest_quote_for_position = tick.time_msc
        price_cents = ((tick.bid_u-e.entry_price_cents) if e.side>0
                       else (e.entry_price_cents-tick.ask_u))
        net_cash = self.cash.net_cash(price_cents)
        if age <= self.cash.max_hold_ms:
            self._observe_cash(net_cash)
        if e.cause is not None or age > self.cash.max_hold_ms:
            return

        # Conservative tie priority: server-side original protective stop
        # already hit at this same quote -> do not call it a target-first fill.
        was_stop_triggered = ((e.side > 0 and tick.bid_u <= p.sl_u)
                              or (e.side < 0 and tick.ask_u >= p.sl_u))
        if (not was_stop_triggered and
                price_cents >= self.cash.required_favorable_cents):
            e.cause = CAUSE_TARGET
            e.event_time_ms = age
            e.observed_goal_cash = net_cash

    def _close(self, t: Tick, trade: Trade) -> None:
        e = self.current
        if e is None or e.entry_ordinal != trade.entry_ordinal:
            raise RuntimeError("Trade close does not match active episode")
        e.exit_ordinal = trade.exit_ordinal
        e.exit_time_msc = trade.exit_time_msc
        e.exit_reason = trade.reason
        e.baseline_net_cash = self.cash.net_cash(trade.net_price_u)
        if e.cause is None:
            if trade.reason == "stop":
                e.cause=CAUSE_STOP
            elif trade.reason == "timeout":
                e.cause=CAUSE_TIMEOUT
            else:
                raise RuntimeError(f"Unknown original exit reason: {trade.reason}")
            # Observed timeout can exceed 30s in illiquid quote gaps;
            # model it at the 30s deadline but retain actual exit timestamp.
            e.event_time_ms=min(self.cash.max_hold_ms,
                                max(0,trade.exit_time_msc-e.entry_time_msc))
        if e.cause == CAUSE_TARGET:
            e.overlay_net_cash=e.observed_goal_cash
        elif e.cause in EVENT_CAUSES:
            e.overlay_net_cash=e.baseline_net_cash
        self.completed.append(e)
        self.current=None
        self._latest_quote_for_position=None

    def on_tick(self, tick: Tick) -> None:
        if tick.ordinal <= self._last_ordinal or tick.time_msc<self._last_time_msc:
            raise ValueError("Coinexx stream is not source-ordinal monotonic")
        if tick.ask_u < tick.bid_u or tick.bid_u <= 0 or tick.time_s != tick.time_msc//1000:
            raise ValueError("Invalid source quote")
        self._last_ordinal=tick.ordinal
        self._last_time_msc=tick.time_msc
        self.ticks_seen+=1

        prior_position=self.base.position
        prior_trades=len(self.base.trades)
        if prior_position is not None:
            self._observe_before_base_tick(tick)
        self.base.on_tick(tick)
        newly_closed=self.base.trades[prior_trades:]
        if len(newly_closed)>1:
            raise RuntimeError("Multiple baseline closes on single source quote")
        if newly_closed:
            self._close(tick,newly_closed[0])
        after=self.base.position
        if after is not None:
            if prior_position is None or after.entry_ordinal!=prior_position.entry_ordinal:
                self._open(tick)
        elif self.current is not None:
            raise RuntimeError("Lost original R9 position without a closure")

    def finish(self) -> list[Episode]:
        """Right-censor the unmatched last episode, never invent a close."""
        e=self.current
        if e is not None:
            if e.cause is None:
                e.cause=CAUSE_EOF
                e.event_time_ms=min(self.cash.max_hold_ms,
                                    max(0,self._last_time_msc-e.entry_time_msc))
            if e.cause == CAUSE_TARGET:
                e.overlay_net_cash=e.observed_goal_cash
            self.completed.append(e)
            self.current=None
            self._latest_quote_for_position=None
        return self.completed


def _mean(values: list[float]) -> float | None:
    return sum(values)/len(values) if values else None


def summarize(episodes: Iterable[Episode]) -> dict:
    """Descriptive only: overlay is NOT an on-policy portfolio backtest."""
    es=list(episodes)
    by={}
    for e in es:
        key=f"{e.source_hour:02d}"
        by.setdefault(key,[]).append(e)
    def one(rows):
        baseline=[e.baseline_net_cash for e in rows if e.baseline_net_cash is not None]
        matched=[e for e in rows if e.baseline_net_cash is not None
                 and e.overlay_net_cash is not None and e.cause in EVENT_CAUSES]
        overlay=[e.overlay_net_cash for e in matched]
        corresponding_base=[e.baseline_net_cash for e in matched]
        return {
            "original_r9_episodes":len(rows),
            "cause_counts":{c:sum(e.cause==c for e in rows)
                            for c in (*EVENT_CAUSES,*CENSORED)},
            "baseline_completed_count":len(baseline),
            "matched_comparable_count":len(matched),
            "mean_baseline_completed_cash":_mean(baseline),
            "mean_matched_baseline_cash":_mean(corresponding_base),
            "mean_hypothetical_early_target_cash":_mean(overlay),
            "matched_per_episode_delta_cash":_mean(
                [float(e.overlay_net_cash)-float(e.baseline_net_cash)
                 for e in matched]),
            "warning":"Hypothetical target overlay preserves original R9 occupancy. No on-policy profit inference.",
        }
    # Actual individual (source-native day, hour) cells, not merely pooling
    # all Mondays or all 16:00 entries across nine months. Using the integer
    # source hour index avoids claiming that the broker clock is UTC.
    cells={}
    for e in es:
        key=str(e.entry_time_msc//3600000)
        cells.setdefault(key,[]).append(e)
    hourly=[]
    for idx,rows in cells.items():
        realized=[float(e.baseline_net_cash) for e in rows
                  if e.baseline_net_cash is not None]
        if realized:
            hourly.append({
                "source_hour_index":int(idx),
                "completed_baseline_trades":len(realized),
                "simulated_baseline_net_account_cash":sum(realized),
                "gross_losing_cash":-sum(min(0.,x) for x in realized),
                "mean_net_cash_per_trade":_mean(realized),
            })
    hourly.sort(key=lambda x:x["source_hour_index"])
    by_pnl=sorted(hourly,key=lambda x:x["simulated_baseline_net_account_cash"])
    return {
        "total":one(es),
        "by_source_entry_hour":{k:one(v) for k,v in sorted(by.items())},
        "individual_active_source_hours":len(hourly),
        "individual_positive_source_hours":sum(x["simulated_baseline_net_account_cash"]>0
                                               for x in hourly),
        "individual_negative_source_hours":sum(x["simulated_baseline_net_account_cash"]<0
                                               for x in hourly),
        "individual_flat_source_hours":sum(x["simulated_baseline_net_account_cash"]==0
                                           for x in hourly),
        "worst_five_source_hour_cells":by_pnl[:5],
        "best_five_source_hour_cells":by_pnl[-5:][::-1],
        "source_hour_warning":"Hour indices use Coinexx source timestamps, NOT independently verified UTC or local timezone.",
    }


def run_stream(ticks: Iterable[Tick], cash: CashAssumptions,
               config: R9Config | None = None) -> R9CashRiskOverlay:
    sim=R9CashRiskOverlay(cash,config)
    for t in ticks:
        sim.on_tick(t)
    sim.finish()
    return sim
