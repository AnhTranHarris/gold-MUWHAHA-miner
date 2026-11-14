"""Coinexx-only ON-POLICY R9 adaptive hold/trail research; no new tick engine.

Reuses the original coinexx_r9.R9HybridGateBaseline event order and state
machine. Every changed exit changes subsequent minute rearm and later entries.
Only *previous completed* 1-second and M1 Bid/Ask-derived state is used;
the decision may also consume the current executable quote. No trades, L2,
true volume, future quote labels, unrealized promised profits or MT5 code.

All cash metrics require an EXPLICIT account-unit contract coefficient K
and EXPLICIT roundtrip charges C (not supplied by Coinexx quote history).
The previous 155-feature AUC classifier is NOT treated as cash P&L or an exit
hazard. Predeclared modes are hypotheses, not trained/approved optimizers.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import ceil, isfinite, sqrt, tanh
from statistics import median
from typing import Iterable

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config, R9HybridGateBaseline
from cash_risk_overlay import CashAssumptions

POLICIES=("baseline","cost_trail","staged_harvest","experimental_wide_stop")


@dataclass(frozen=True)
class ExitPolicy:
    mode: str = "cost_trail"
    alpha_spread: float = 0.75
    beta_noise: float = 1.25
    activation_cash_buffer: float = 0.06
    minimum_harvest_cash: float = 0.10
    harvest_after_seconds: int = 4
    continuation_floor: float = -0.10
    m1_std_regime_weight: float = 0.20
    m1_ema_trend_weight: float = 0.10
    maximum_trail_cents: int = 75
    maximum_initial_stop_cents: int = 60
    maximum_initial_risk_cash: float = 1.50
    max_quote_gap_ms: int = 2500

    def __post_init__(self) -> None:
        if self.mode not in POLICIES:
            raise ValueError(f"Unknown research mode: {self.mode}")
        vals=(self.alpha_spread,self.beta_noise,
              self.activation_cash_buffer,self.minimum_harvest_cash,
              self.continuation_floor,self.m1_std_regime_weight,
              self.m1_ema_trend_weight,self.maximum_initial_risk_cash)
        if not all(isfinite(v) for v in vals):
            raise ValueError("Non-finite research parameters")
        if (self.alpha_spread<0 or self.beta_noise<0
            or self.activation_cash_buffer<0
            or self.maximum_initial_risk_cash<=0
            or self.minimum_harvest_cash<0
            or self.m1_std_regime_weight<0 or self.m1_std_regime_weight>1
            or self.m1_ema_trend_weight<0 or self.m1_ema_trend_weight>1
            or self.maximum_trail_cents<=0
            or self.maximum_initial_stop_cents<=0
            or self.harvest_after_seconds<0
            or self.max_quote_gap_ms<=0):
            raise ValueError("Invalid research price/holding/risk controls")


class QuoteContext:
    """O(1) streaming completed-second and completed-M1 state (no future bars)."""
    def __init__(self) -> None:
        self.last_ms=-1
        self.second: int | None=None
        self.mid2=0
        self.spread=0
        self.second_count=0
        self.completed_sec=deque(maxlen=16)  # (sec, mid2, spread, updates)
        self.minute: int | None=None
        self.minute_last_bid=0
        self.m1_closed_bid=deque(maxlen=25)
        self.m1_ema20:float|None=None
        self.m1_prior_ema20:float|None=None

    def update(self,t:Tick) -> None:
        if t.time_msc<self.last_ms:
            raise ValueError("Quote timestamps cannot move backward")
        self.last_ms=t.time_msc
        sec=t.time_s
        minute=sec//60
        if self.minute is None:
            self.minute=minute
        elif minute!=self.minute:
            if self.minute_last_bid>0:
                v=float(self.minute_last_bid)
                self.m1_closed_bid.append(v)
                self.m1_prior_ema20=self.m1_ema20
                self.m1_ema20=(v if self.m1_ema20 is None
                               else self.m1_ema20+2.0/21.0*(v-self.m1_ema20))
            self.minute=minute
        self.minute_last_bid=t.bid_u
        if self.second is None:
            self.second=sec
            self.second_count=0
        elif sec!=self.second:
            self.completed_sec.append((self.second,self.mid2,self.spread,
                                       self.second_count))
            self.second=sec
            self.second_count=0
        self.mid2=t.bid_u+t.ask_u
        self.spread=t.ask_u-t.bid_u
        self.second_count+=1

    def diagnostics(self,t:Tick) -> dict:
        """As-of metrics. Missing/old periods abstain instead of fabricating zeros."""
        recent=list(self.completed_sec)
        last=recent[-5:]
        fresh=(bool(last) and 0 <= t.time_s-last[-1][0] <= 2)
        spread_ref=float(median([r[2] for r in last])) if fresh else None
        noise=None
        trend=None
        efficiency=None
        if len(last)>=4 and fresh and all(
            b[0]-a[0]==1 for a,b in zip(last[-4:-1],last[-3:])
        ):
            mid=[q[1]/2.0 for q in last[-4:]]
            revisions=[z-y for y,z in zip(mid,mid[1:])]
            noise=sqrt(sum(d*d for d in revisions)/len(revisions))
            gross=sum(abs(x) for x in revisions)
            direction=(t.bid_u+t.ask_u)/2.0-mid[0]
            trend=direction
            efficiency=direction/max(gross+abs((t.bid_u+t.ask_u)/2-mid[-1]),1)
        m1std=None
        if len(self.m1_closed_bid)>=10:
            v=list(self.m1_closed_bid)[-10:]
            mean=sum(v)/len(v)
            m1std=sqrt(sum((x-mean)**2 for x in v)/len(v))
        return dict(spread_ref=spread_ref,noise_1s_cents=noise,
                    trend_cents=trend,efficiency=efficiency,
                    completed_m1_std_cents=m1std,
                    completed_m1_ema_slope_cents=(
                        self.m1_ema20-self.m1_prior_ema20
                        if self.m1_ema20 is not None and
                        self.m1_prior_ema20 is not None else None),
                    quote_fresh=fresh)

    def continuation_index(self,side:int,t:Tick) -> float|None:
        d=self.diagnostics(t)
        if (not d["quote_fresh"] or d["noise_1s_cents"] is None
            or d["trend_cents"] is None or d["efficiency"] is None):
            return None
        noise=max(1.0,d["noise_1s_cents"])
        signed=side*d["trend_cents"]
        z=tanh(signed/(2.0*noise))
        directional=side*d["efficiency"]
        shock=max(0.0,(
            (t.ask_u-t.bid_u)-(d["spread_ref"] or 0.0)
        )/max(1.0,d["spread_ref"] or 1.0))
        # Dimensionless causal momentum/reversion index, NOT a calibrated
        # hazard probability. Parameters fixed before experimental evaluation.
        return 0.60*z+0.40*directional-0.20*min(shock,2.0)


class AdaptiveR9(R9HybridGateBaseline):
    """Only overrides management/entry hooks: baseline event engine unchanged."""
    def __init__(self,cfg:R9Config,cash:CashAssumptions,policy:ExitPolicy):
        super().__init__(cfg)
        if cfg.max_hold_seconds*1000!=cash.max_hold_ms:
            raise ValueError("Research cash horizon must match original R9 maximum hold")
        self.cash=cash
        self.policy=policy
        self.quotes=QuoteContext()
        self.last_tick:Tick|None=None

    def on_tick(self,t:Tick) -> None:
        self.quotes.update(t)
        self.last_tick=t
        super().on_tick(t)

    def _noise(self,t:Tick) -> float|None:
        d=self.quotes.diagnostics(t)
        if d["quote_fresh"] and d["noise_1s_cents"] is not None:
            return float(d["noise_1s_cents"])
        # Completed original M5 ATR is an explicitly slower fallback, not a
        # fabricated tick volatility reading. No ATR? retain original policy.
        return (self.atr.atr_u/sqrt(300.0) if self.atr.ready
                and self.atr.atr_u is not None else None)

    def _indicator_scaled_noise(self,t:Tick,noise:float) -> float:
        """Native iStdDev(PERIOD_M1,10,0,MODE_SMA,PRICE_CLOSE) proxy.

        Uses completed Bid M1 closes only; exact native broker history/chart
        parity must be confirmed before translating this to MQL5.
        The original iATR(PERIOD_M5,14) is the slower normalization anchor.
        """
        if (self.policy.m1_std_regime_weight<=0 or not self.atr.ready
            or self.atr.atr_u is None or self.atr.atr_u<=0):
            return noise
        m1=self.quotes.diagnostics(t)["completed_m1_std_cents"]
        if m1 is None:
            return noise
        ratio=min(2.0,m1/self.atr.atr_u)
        return noise*(1.0+self.policy.m1_std_regime_weight*ratio)

    def _open_trade(self,t:Tick,side:int) -> None:
        super()._open_trade(t,side)
        if self.policy.mode!="experimental_wide_stop":
            return
        p=self.position
        noise=self._noise(t)
        if p is None or noise is None:
            return
        spread=t.ask_u-t.bid_u
        requested=max(self.cfg.stop_loss_pips,
                      ceil(2.0*spread+1.25*noise))
        # Experimental only: separate cash-loss-risk capacity must be
        # evaluated; never silently allow unlimited initial stop widening.
        requested=min(self.policy.maximum_initial_stop_cents,requested)
        broker=self.cfg.broker_stops_points+self.cfg.tick_size_points
        requested=max(requested,broker)
        stop=t.bid_u-requested if side>0 else t.ask_u+requested
        # Explicit pessimistic stop-fill cash risk, including spread once and
        # additional assumed brokerage costs. Never widen without cash cap.
        potential_loss=self.cash.net_cash(side*(stop-p.entry_price_u))
        if potential_loss < -self.policy.maximum_initial_risk_cash:
            self.stats["experimental_initial_risk_cap_refusals"]+=1
            return
        if (side>0 and stop<p.sl_u) or (side<0 and stop>p.sl_u):
            p.sl_u=stop
            p.initial_sl_u=stop
            self.entries[-1]["sl_u"]=stop
            self.stats["experimental_wider_initial_sl"]+=1

    def _manage_position(self,t:Tick) -> None:
        if self.policy.mode=="baseline":
            super()._manage_position(t)
            return
        p=self.position
        if p is None:
            return
        c=self.cfg
        # Preserve original timeout quote boundary and same-minute rearm order.
        if t.time_s-p.entry_time_s>=c.max_hold_seconds:
            self._record_close(t,"timeout",
                               t.bid_u if p.side>0 else t.ask_u)
            return
        available=t.bid_u if p.side>0 else t.ask_u
        pnl_cents=p.side*(available-p.entry_price_u)
        net_cash=self.cash.net_cash(pnl_cents)
        noise=self._noise(t)
        if noise is None:
            # Fail back to original management when no fresh proxy is known.
            super()._manage_position(t)
            self.stats["adaptive_fallback_to_original"]+=1
            return

        noise=self._indicator_scaled_noise(t,noise)
        elapsed=t.time_s-p.entry_time_s
        if (self.policy.mode in ("staged_harvest","experimental_wide_stop")
            and elapsed>=self.policy.harvest_after_seconds
            and net_cash>=self.policy.minimum_harvest_cash):
            score=self.quotes.continuation_index(p.side,t)
            if score is not None:
                ema_slope=self.quotes.diagnostics(t)["completed_m1_ema_slope_cents"]
                if (ema_slope is not None and self.atr.atr_u is not None
                    and self.atr.atr_u>0):
                    score+=self.policy.m1_ema_trend_weight*tanh(
                        p.side*ema_slope/max(1.0,self.atr.atr_u))
            if score is not None and score<self.policy.continuation_floor:
                self._record_close(t,"adaptive_harvest",available)
                return

        if not c.trailing_enabled or c.trail_pips<=0:
            return
        spread=t.ask_u-t.bid_u
        # A cost-paid + minimum realized-gain buffer must precede trail
        # activation. The original $0.10 quote activation remains a floor.
        cost_cents=ceil(100.0*self.cash.round_trip_cost_cash/
                        self.cash.cash_per_one_xau_price_dollar)
        min_gain_cents=ceil(100.0*self.policy.activation_cash_buffer/
                            self.cash.cash_per_one_xau_price_dollar)
        activation=max(c.trail_activation_pips,cost_cents+min_gain_cents,
                       ceil(self.policy.beta_noise*noise))
        if pnl_cents<activation:
            return
        buffer=max(c.trail_pips,
                   ceil(self.policy.alpha_spread*spread),
                   ceil(self.policy.beta_noise*noise))
        buffer=min(self.policy.maximum_trail_cents,buffer)
        min_legal=(c.broker_stops_points+c.tick_size_points
                   if c.respect_broker_stops else c.tick_size_points)
        buffer=max(buffer,min_legal)
        candidate=available-buffer if p.side>0 else available+buffer
        if (p.side>0 and candidate>p.sl_u) or (
            p.side<0 and candidate<p.sl_u
        ):
            p.sl_u=candidate
            self.stats["adaptive_trail_updates"]+=1


def summarize_account_cash(
    sim:R9HybridGateBaseline,cash:CashAssumptions
) -> dict:
    """Full on-policy trade ledger statistics for ONE EA without governor.

    No source timestamps are reinterpreted as UTC. No open position PnL
    fabrication. All outcomes include spread once via original quote-side.
    """
    from collections import defaultdict
    trades=sim.trades
    per_day=defaultdict(float)
    per_hour=defaultdict(float)
    vals=[]
    holds=[]
    for trade in trades:
        net=cash.net_cash(trade.net_price_u)
        vals.append(net)
        holds.append((trade.exit_time_msc-trade.entry_time_msc)/1000.0)
        per_hour[trade.entry_time_msc//3_600_000]+=net
        per_day[trade.entry_time_msc//86_400_000]+=net
    equity=0.0; peak=0.0; dd=0.0
    for trade in trades:
        equity+=cash.net_cash(trade.net_price_u)
        peak=max(peak,equity)
        dd=max(dd,peak-equity)
    def percentile(values,p):
        if not values:
            return None
        z=sorted(values);ix=int(ceil(p*len(z))-1)
        return z[max(0,min(len(z)-1,ix))]
    negative=sorted(x for x in vals if x<0)
    bottom=negative[:max(1,ceil(.05*len(vals)))] if negative else []
    return dict(
        classification="ON_POLICY_COINEXX_QUOTE_SIMULATION_NOT_BROKER_FILLS",
        trades=len(trades),entries=len(sim.entries),
        open_at_end=int(sim.position is not None),
        total_net_cash=sum(vals),mean_net_cash_per_trade=(
            sum(vals)/len(vals) if vals else None),
        mean_hold_seconds=(sum(holds)/len(holds) if holds else None),
        hold_p95_seconds=percentile(holds,.95),
        hold_p99_seconds=percentile(holds,.99),
        stop_coded=sum(x.reason=="stop" for x in trades),
        adaptive_harvest_count=sum(x.reason=="adaptive_harvest" for x in trades),
        timeout_count=sum(x.reason=="timeout" for x in trades),
        gross_realized_loss_cash=-sum(min(0.0,v) for v in vals),
        win_fraction=(sum(v>0 for v in vals)/len(vals) if vals else None),
        worst_trade_cash=(min(vals) if vals else None),
        observed_trade_loss_cvar95_cash=(
            max(0.0,-sum(sorted(vals)[:max(1,ceil(.05*len(vals)))])/
              max(1,ceil(.05*len(vals)))) if vals else None),
        source_entry_day_net_cash={str(k):v for k,v in sorted(per_day.items())},
        source_entry_hour_cash={str(k):v for k,v in sorted(per_hour.items())},
        positive_entry_hour_cells=sum(v>0 for v in per_hour.values()),
        negative_entry_hour_cells=sum(v<0 for v in per_hour.values()),
        completed_entry_hour_cells=len(per_hour),
        peak_to_trough_closed_trade_drawdown_cash=dd,
        rearm_count=int(sim.stats.get("rearms",0)),
        adaptive_trail_updates=int(sim.stats.get("adaptive_trail_updates",0)),
        experimental_wider_initial_sl=int(sim.stats.get(
            "experimental_wider_initial_sl",0)),
        account_governor_simulated=False,
        trader_broker_fee_calibration_verified=False,
        no_actual_order_fills=True,
    )
