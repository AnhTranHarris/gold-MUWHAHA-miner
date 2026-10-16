"""R04 cost-aware protective exit supervisor around the existing shared-account bus.

Causal, deterministic, research-only. Every stop modification goes through Replay,
which enforces next-quote latency and broker-quote stop levels. No simulated broker
acknowledgment may be represented as an actual MT5 fill.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from math import isfinite

from .bars import Bar
from .feeds import Quote
from .signal_bus import SharedSignalArbiter


@dataclass(frozen=True)
class ExitProfile:
    max_hold_ms: int = 30000
    min_locked_net_usd: float = 0.10
    activate_net_usd: float = 0.35
    trail_floor_price: float = 0.30
    atr_trail_fraction: float = 0.05

    def __post_init__(self):
        if (self.max_hold_ms <= 0 or not all(isfinite(x) and x >= 0 for x in
            (self.min_locked_net_usd, self.activate_net_usd,
             self.trail_floor_price, self.atr_trail_fraction))):
            raise ValueError('invalid specialist exit profile')


class CostAwareLifecycle:
    """Delegates multi-signal entries to the arbiter; centralizes funded exits.

    A stop must protect the full entry/exit commissions + estimated next-stop
    exit slippage plus a nonnegative dollar cushion *before* trailing begins.
    Favorable mark does not equal executable P&L until exit is actually filled.
    """
    def __init__(self, router: SharedSignalArbiter,
                 default: ExitProfile | None = None,
                 by_specialist: dict[str, ExitProfile] | None = None):
        self.router=router
        self.default=default or ExitProfile()
        self.by_specialist=by_specialist or {}
        self._last_m5_close: float | None = None
        self._atr: float | None = None
        self._m5_history=0
        self.metrics={'profile_evaluations':0,'economic_exit_arms':0,
                      'stop_requests':0,'max_hold_requests':0,
                      'below_cost_floor':0}

    def on_bar(self,bar: Bar,q:Quote,engine:object):
        if bar.end_ms>q.ms:
            raise ValueError('future candle prohibited')
        if bar.seconds==300:
            last=self._last_m5_close
            tr=max(bar.bid_high-bar.bid_low,
                   abs(bar.bid_high-last),abs(bar.bid_low-last)) if last is not None else bar.bid_high-bar.bid_low
            self._atr=tr if self._atr is None else (13*self._atr+tr)/14
            self._last_m5_close=bar.bid_close
            self._m5_history+=1
        self.router.on_bar(bar,q,engine)

    def on_tick(self,q:Quote,engine:object):
        p=engine.position
        if p is not None:
            self.metrics['profile_evaluations']+=1
            # Entry reason format is 'arbiter:<source_id>:<specialist name>'.
            family=p.entry_reason.split(':')[-1]
            profile=self.by_specialist.get(family,self.default)
            if q.ms-p.entry_ms>=profile.max_hold_ms:
                if not any(o.kind=='close' for o in engine.pending):
                    engine.request_close('specialist_max_hold:'+family)
                    self.metrics['max_hold_requests']+=1
            else:
                price=q.bid if p.side==1 else q.ask
                unit=p.lots*engine.cfg.contract_size
                exit_fee=engine.cfg.commission_per_lot_side*p.lots
                # Full modeled charges: entry fee has already been deducted from
                # account balance, but must be counted in total trade economics.
                cost_usd=p.paid_entry_fee+exit_fee+unit*engine.cfg.adverse_slippage_price
                signed_movement=p.side*(price-p.entry)
                expected_net=signed_movement*unit-cost_usd
                required_net=max(profile.min_locked_net_usd,profile.activate_net_usd)
                if expected_net >= required_net:
                    self.metrics['economic_exit_arms']+=1
                    atr_gap=(self._atr*profile.atr_trail_fraction
                             if self._atr is not None and self._m5_history>=14 else 0.0)
                    gap=max(profile.trail_floor_price,atr_gap,
                            engine.cfg.min_stop_distance_price)
                    desired=price-p.side*gap
                    economic_stop=p.entry+p.side*(cost_usd+profile.min_locked_net_usd)/unit
                    if p.side==1:
                        new_stop=max(desired,economic_stop)
                        feasible=new_stop<q.bid-engine.cfg.min_stop_distance_price
                        improvement=p.stop is None or new_stop>p.stop+1e-9
                    else:
                        new_stop=min(desired,economic_stop)
                        feasible=new_stop>q.ask+engine.cfg.min_stop_distance_price
                        improvement=p.stop is None or new_stop<p.stop-1e-9
                    if feasible and improvement and not any(
                            z.kind=='modify_stop' for z in engine.pending):
                        if engine.request_modify_stop(new_stop,
                            reason='cost_floor:'+family):
                            self.metrics['stop_requests']+=1
                else:
                    self.metrics['below_cost_floor']+=1
        self.router.on_tick(q,engine)
