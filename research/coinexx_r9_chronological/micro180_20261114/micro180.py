"""Experimental R9 micro180 quote-executable, millisecond-ordered lifecycle.

No high-AUC model, no real-volume/order-book inference, no tick regeneration.
Separate experimental code path: original R9 and dual-OR baselines are unchanged.
All thresholds are FROZEN ENGINEERING HYPOTHESES, not trained optima.
"""
from __future__ import annotations

import math
from collections import Counter, deque
from dataclasses import dataclass
from typing import Optional

from coinexx_r9.models import Tick
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ManagedR9, ResearchCash


@dataclass(frozen=True)
class Micro180Spec:
    window_ms: int = 180_000
    basket5_ms: int = 5_000
    basket15_ms: int = 15_000
    breakout15_ms: int = 15_000
    breakout30_ms: int = 30_000
    min_5s_mid_move_u: int = 10
    min_15s_confirm_u: int = 6
    breakout_buffer_u: int = 1
    min_complete_15s: int = 10
    min_complete_30s: int = 18
    max_second_age_ms: int = 2_500
    max_quote_gap_ms: int = 2_500
    min_efficiency_15s: float = .55
    min_normalized_breakout: float = .25
    # Strict pre-existing control, plus explicit UNVALIDATED throughput alternatives.
    breakout_router: str = "strict_30s"
    s1_mode: str = "strict_r9"
    structural_confirmation: str = "completed_only"
    min_buy_strong_15s_z: float = .55
    min_sell_strong_15s_z: float = .55
    max_adverse_30s_z: float = .10
    spread_shock_ratio: float = 1.35
    min_quote_updates_5s: int = 5
    max_entries_per_source_minute: int = 4
    max_lifetime_ms: int = 30_000
    min_net_cash: float = .10
    preferred_max_net_cash: float = 1.75
    hard_risk_cash: float = 2.00
    # A runner is NOT assumed profitable: disabled until first-passage results justify it.
    experimental_runner: bool = False
    runner_trail_cash: float = .25
    min_runner_trend_score: float = .45
    # EMA/DI are quote-derived replicas; native MT5 parity is a separate release gate.
    use_m1_directional_veto: bool = True

    def __post_init__(self):
        if (self.window_ms != 180_000 or self.basket5_ms != 5_000
            or self.basket15_ms != 15_000 or self.breakout15_ms != 15_000
            or self.breakout30_ms != 30_000):
            raise ValueError('The frozen 180s/5s/15s/15s/30s grid cannot silently change')
        if (self.min_complete_15s < 2 or self.min_complete_30s < self.min_complete_15s
            or self.min_5s_mid_move_u <= 0 or self.min_15s_confirm_u < 0
            or self.breakout_buffer_u < 0 or self.max_second_age_ms <= 0
            or self.max_quote_gap_ms <= 0 or self.min_quote_updates_5s < 1
            or not 0.0 < self.min_efficiency_15s <= 1.0
            or self.min_normalized_breakout < 0.0 or self.spread_shock_ratio < 1.0
            or self.breakout_router not in ("balanced_30s_veto", "strict_30s")
            or self.s1_mode not in ("micro_only", "strict_r9")
            or self.structural_confirmation not in ("causal_active_or_completed", "completed_only")
            or min(self.min_buy_strong_15s_z,self.min_sell_strong_15s_z) < 0
            or self.max_adverse_30s_z < 0
            or not 1 <= self.max_entries_per_source_minute <= 4
            or not 0.0 < self.min_net_cash < self.preferred_max_net_cash
            or self.hard_risk_cash <= self.min_net_cash or self.max_lifetime_ms < 1_000):
            raise ValueError('Invalid micro180 trading geometry / cash controls')


class Candle:
    __slots__ = ('start_ms', 'first_ms', 'last_ms', 'n', 'bid_open', 'bid_hi',
                 'bid_lo', 'bid_close', 'ask_open', 'ask_hi', 'ask_lo', 'ask_close',
                 'spread_close')

    def __init__(self, t: Tick, start_ms: int):
        self.start_ms = start_ms
        self.first_ms = self.last_ms = t.time_msc
        self.n = 1
        self.bid_open = self.bid_hi = self.bid_lo = self.bid_close = t.bid_u
        self.ask_open = self.ask_hi = self.ask_lo = self.ask_close = t.ask_u
        self.spread_close = t.spread_points

    def update(self, t: Tick):
        self.n += 1
        self.last_ms = t.time_msc
        self.bid_hi = max(self.bid_hi, t.bid_u)
        self.bid_lo = min(self.bid_lo, t.bid_u)
        self.bid_close = t.bid_u
        self.ask_hi = max(self.ask_hi, t.ask_u)
        self.ask_lo = min(self.ask_lo, t.ask_u)
        self.ask_close = t.ask_u
        self.spread_close = t.spread_points

    @property
    def mid_anchor2(self) -> int:
        return self.bid_open + self.ask_open

    @property
    def mid_displacement2(self) -> int:
        return self.bid_close + self.ask_close - self.mid_anchor2


class M1QuoteIndicators:
    """Bounded closed-Bid-M1 context, NOT certified bitwise MT5 indicator parity.

    EMA(20), 14-period Wilder ATR and +/-DI from completed real observed M1 bars.
    Thin gaps do not synthesize zero-volume OHLC. No look-ahead in forming bar.
    """
    def __init__(self):
        self.bar: Optional[Candle] = None
        self.closed = 0
        self.ema: Optional[float] = None
        self.ema_previous: Optional[float] = None
        self.atr: Optional[float] = None
        self.plus_dm: Optional[float] = None
        self.minus_dm: Optional[float] = None
        self.plus_di: Optional[float] = None
        self.minus_di: Optional[float] = None
        self._prev_hlc: Optional[tuple[int,int,int]] = None
        self._tr_seed: list[float] = []
        self._p_seed: list[float] = []
        self._n_seed: list[float] = []
        self._last_closed_ms = -1

    def update(self, t: Tick):
        start = t.time_msc // 60_000 * 60_000
        if self.bar is None:
            self.bar = Candle(t, start)
            return
        if start == self.bar.start_ms:
            self.bar.update(t)
            return
        if start < self.bar.start_ms:
            raise ValueError('Nonmonotonic M1 minute')
        p = self.bar
        # Reject a closed M1 that is isolated from the previous active minute:
        # its indicators remain stale until a continuous sequence becomes available.
        if self._last_closed_ms >= 0 and p.start_ms - self._last_closed_ms > 60_000:
            self.ema = self.atr = self.plus_dm = self.minus_dm = None
            self._tr_seed.clear(); self._p_seed.clear(); self._n_seed.clear()
            self._prev_hlc = None
        close = p.bid_close
        self.ema_previous = self.ema
        self.ema = float(close) if self.ema is None else (2.0 / 21.0) * close + (19.0 / 21.0) * self.ema
        if self._prev_hlc is not None:
            ph, pl, pc = self._prev_hlc
            tr = max(p.bid_hi-p.bid_lo,abs(p.bid_hi-pc),abs(p.bid_lo-pc))
            up, dn = p.bid_hi-ph, pl-p.bid_lo
            pdm = float(up) if up>dn and up>0 else 0.0
            ndm = float(dn) if dn>up and dn>0 else 0.0
            if self.atr is None:
                self._tr_seed.append(float(tr));self._p_seed.append(pdm);self._n_seed.append(ndm)
                if len(self._tr_seed)==14:
                    self.atr=sum(self._tr_seed)/14.0
                    self.plus_dm=sum(self._p_seed)/14.0
                    self.minus_dm=sum(self._n_seed)/14.0
                    self._tr_seed.clear();self._p_seed.clear();self._n_seed.clear()
            else:
                self.atr=(13*self.atr+tr)/14.0
                self.plus_dm=(13*self.plus_dm+pdm)/14.0  # type: ignore[operator]
                self.minus_dm=(13*self.minus_dm+ndm)/14.0  # type: ignore[operator]
            if self.atr is not None and self.atr>0:
                self.plus_di=100*self.plus_dm/self.atr  # type: ignore[operator]
                self.minus_di=100*self.minus_dm/self.atr  # type: ignore[operator]
        self._prev_hlc=(p.bid_hi,p.bid_lo,close)
        self.closed += 1
        self._last_closed_ms = p.start_ms
        self.bar = Candle(t,start)

    def bias(self, side:int)->Optional[float]:
        if self.atr is None or self.plus_di is None or self.ema_previous is None or self.ema is None:
            return None
        dmi = (self.plus_di - self.minus_di) if side>0 else (self.minus_di-self.plus_di)
        slope = side*(self.ema-self.ema_previous)/max(1.0,self.atr)
        return max(-1.0,min(1.0,.7*dmi/20.0+.3*slope/0.05))


class RollingThreeMinute:
    """No synthetic seconds: 1s bars and three REAL 5s/15s/30s OHLC streams.

    Work per quote O(1), memory bounded to ~180 observed second-close points,
    36 completed 5s candles, 12 completed 15s, 6 completed 30s.
    All transitions keyed by millisecond timestamps and source row order.
    """
    def __init__(self):
        self.current: dict[int,Candle] = {}
        self.finished: dict[int,deque[Candle]] = {1000:deque(maxlen=181),
                                                   5000:deque(maxlen=37),
                                                   15000:deque(maxlen=13),
                                                   30000:deque(maxlen=7)}
        self.previous_msc: Optional[int] = None
        self.last_gap_ms = 0
        self.nonzero_last = 0
        self.nonzero_volume = 0
        self.n = 0
        self.m1 = M1QuoteIndicators()
        self._cache_key = None
        self._window_cache = {}

    def update(self, t: Tick):
        if self.previous_msc is not None:
            if t.time_msc < self.previous_msc:
                raise ValueError('Source quote chronology must be preserved')
            self.last_gap_ms = t.time_msc - self.previous_msc
        self.previous_msc=t.time_msc
        self.n+=1
        if t.last_u: self.nonzero_last+=1
        if t.volume or float(t.volume_real): self.nonzero_volume+=1
        for width in (1000,5000,15000,30000):
            start=t.time_msc//width*width
            bar=self.current.get(width)
            if bar is None:
                self.current[width]=Candle(t,start)
            elif start == bar.start_ms:
                bar.update(t)
            else:
                if start<bar.start_ms:raise ValueError('noncausal subminute candle')
                self.finished[width].append(bar)
                self.current[width]=Candle(t,start)
                self._cache_key=None
        self.m1.update(t)

    def closes(self, now_ms:int, lookback_ms:int)->list[Candle]:
        # Use wall-clock completed SECOND windows, not a sliding fractional
        # millisecond cutoff against each candle's last update. This makes
        # cache-by-current-second exact and matches the MQL5 comparator.
        current_s_start = now_ms//1000*1000
        floor_start = current_s_start-lookback_ms
        out=[]
        for bar in reversed(self.finished[1000]):
            if bar.start_ms < floor_start:break
            if bar.start_ms < current_s_start:
                out.append(bar)
        out.reverse()
        return out

    def price_levels(self, now_ms:int, min15:int, min30:int, freshness:int):
        # Cache only across the same CURRENT SECOND; incomplete current-second
        # extrema are never inserted into the previous-close window.
        now_s=now_ms//1000
        if self._cache_key!=now_s:
            self._cache_key=now_s
            q15=self.closes(now_ms,15000)
            q30=self.closes(now_ms,30000)
            def calc(q,minimum):
                if len(q)<minimum or now_ms-q[-1].last_ms>freshness:return None
                return (max(x.bid_close for x in q),min(x.ask_close for x in q),q)
            self._window_cache={15:calc(q15,min15),30:calc(q30,min30)}
        return self._window_cache.get(15),self._window_cache.get(30)

    def last_closed(self, seconds:int, now_ms:int)->Optional[Candle]:
        q=self.finished[seconds*1000]
        if q and now_ms-(q[-1].start_ms+seconds*1000)<=seconds*1000 and q[-1].start_ms+seconds*1000<=now_ms:
            return q[-1]
        return None

    def five_second_updates(self, now_ms:int)->int:
        # Closed observed 1-second bars only; never trading-volume claims.
        return sum(x.n for x in self.closes(now_ms,5000))

    def intensity_and_spread(self, q:list[Candle],spread:int)->tuple[float,float]:
        # Past spread is a quote property; quotes per observed second are NOT true volume.
        spreads=sorted(x.spread_close for x in q)
        med=spreads[len(spreads)//2] if spreads else 0
        shock=spread/max(1,med)
        rate=sum(x.n for x in q)/max(1,len(q))
        return shock,rate


class Micro180R9(ManagedR9):
    """New entry and cash lifecycle, single-position, frozen research-only pilot.

    Account governor and original broker-side SL still execute on every quote.
    No historical model-AUC scores are carried into this different entry universe.
    """
    def __init__(self,cfg:R9Config,cash:ResearchCash,
                 spec:Micro180Spec=Micro180Spec()):
        if not cash.governor:
            # Research-only callers may explicitly disable account simulation;
            # never mislabel such a run as risk-certified.
            self._no_governor=True
        else:
            self._no_governor=False
        super().__init__(cfg,cash,'original')
        self.micro_spec=spec
        self.rolling=RollingThreeMinute()
        self._entry_minute=None
        self._entries_this_minute=0
        self._last_closed_basket=None
        self._last_closed_15s_basket=None
        self._last_exit_ms=None
        self._current_peak_cash:Optional[float]=None
        self._signal_meta:dict[str,float|int|str]={}
        self.indicator_sources=Counter()

    def _push_second(self,t:Tick):
        super()._push_second(t)
        self.rolling.update(t)

    def _start_minute_cycle(self,t:Tick):
        minute=t.time_s//60
        if minute!=self._entry_minute:
            self._entry_minute=minute
            self.cycle_minute=minute*60
            self._entries_this_minute=0
            self.rearms=0
            self.pending_mode=2
        # Rearm only after BOTH clocks have rolled past the last exit and
        # a deliberate 3s cool-down. A 5s reset by itself grants nothing.
        if (self.pending_mode==0 and self.position is None
            and self._last_exit_ms is not None
            and t.time_msc-self._last_exit_ms>=3000
            and self.rolling.current[5000].start_ms!=self._last_closed_basket
            and self.rolling.current[15000].start_ms!=self._last_closed_15s_basket
            and self._entries_this_minute<self.micro_spec.max_entries_per_source_minute):
            self.pending_mode=2
            self.stats['micro_explicit_rearm']+=1
        if self._entries_this_minute>=self.micro_spec.max_entries_per_source_minute:
            self.pending_mode=0

    def _arm_opposite_after_exit(self):
        # A fresh 5s signal can be evaluated, but rearm permission is NOT reset
        # on every 5s bucket. An explicit minimum reset observation is required.
        self.pending_mode=0

    def _quality(self,side:int)->bool:
        # Frozen original R9 S1 plus strict actual wall-clock continuity.
        recent=list(self.micro)[-max(self.cfg.velocity_lookback_sec,self.cfg.range_lookback_sec)-1:]
        if len(recent)<max(self.cfg.velocity_lookback_sec,self.cfg.range_lookback_sec)+1:
            return False
        if any(b.second-a.second>2 for a,b in zip(recent,recent[1:])):
            self.stats['micro_s1_sparse_reject']+=1
            return False
        return super()._quality(side)

    def _process_entries(self,t:Tick):
        s=self.micro_spec
        if self.pending_mode==0 or self._entries_this_minute>=s.max_entries_per_source_minute:return
        if self._last_closed_basket is not None and self.rolling.current[5000].start_ms==self._last_closed_basket:
            return
        if not self._gate(t):return
        if self.rolling.last_gap_ms>s.max_quote_gap_ms:
            self.stats['micro_quote_gap']+=1;return
        # Step 1: 5-second basket is an observation ONLY, no automatic order.
        b5=self.rolling.current[5000]
        move2=t.bid_u+t.ask_u-b5.mid_anchor2
        side=1 if move2>=2*s.min_5s_mid_move_u else -1 if move2<=-2*s.min_5s_mid_move_u else 0
        if not side:return
        if s.s1_mode=="strict_r9" and not self._quality(side):
            self.stats['micro_s1_reject']+=1;return
        # Step 2: a completed 15s candle is the strict control. The optional
        # active candle uses only ticks observed so far and requires >=3s history.
        b15=self.rolling.last_closed(15,t.time_msc)
        active15=self.rolling.current[15000]
        live15=(s.structural_confirmation=="causal_active_or_completed"
                and active15.last_ms-active15.first_ms>=3000
                and active15.n>=5
                and side*active15.mid_displacement2>=2*s.min_15s_confirm_u)
        completed15=(b15 is not None and side*b15.mid_displacement2>=2*s.min_15s_confirm_u)
        if not live15 and not completed15:
            self.stats['micro_15s_structure_reject']+=1;return
        b15_source=active15 if live15 else b15
        # Step 3: BUY checks executable Bid; SELL checks executable Ask.
        # Balanced mode keeps a 30s signed-trend veto if no new 30s extreme.
        p15,p30=self.rolling.price_levels(t.time_msc,s.min_complete_15s,
                                          s.min_complete_30s,s.max_second_age_ms)
        if p15 is None or p30 is None:
            self.stats['micro_incomplete_seconds']+=1;return
        if s.s1_mode=="micro_only" and any(
            b.start_ms-a.start_ms>2000 for a,b in zip(p30[2],p30[2][1:])
        ):
            self.stats['micro_gap_in_completed_seconds']+=1;return
        if side>0:
            exc15=t.bid_u-p15[0]
            exc30=t.bid_u-p30[0]
        else:
            exc15=p15[1]-t.ask_u
            exc30=p30[1]-t.ask_u
        if exc15<s.breakout_buffer_u:
            self.stats['micro_15s_no_executable_breakout']+=1;return
        if s.breakout_router=="strict_30s" and exc30<s.breakout_buffer_u:
            self.stats['micro_30s_no_new_extreme']+=1;return
        # Robust 1s efficiency and normalized breakouts; no current-bar maxima.
        q=p15[2]
        mid=[x.bid_close+x.ask_close for x in q]
        net=mid[-1]-mid[0]
        travel=sum(abs(y-x) for x,y in zip(mid,mid[1:]))
        if len(q)<2 or side*net<=0 or abs(net)/max(1.,travel)<s.min_efficiency_15s:
            self.stats['micro_efficiency_reject']+=1;return
        returns=[(y-x)/2.0 for x,y in zip(mid,mid[1:])]
        sigma=math.sqrt(sum(x*x for x in returns)/max(1,len(returns)))
        sigma=max(1.,sigma)
        z15=exc15/sigma
        z30=exc30/sigma
        z=z30 if s.breakout_router=="strict_30s" else z15
        if z<s.min_normalized_breakout:
            self.stats['micro_z_reject']+=1;return
        if s.breakout_router=="balanced_30s_veto" and exc30<s.breakout_buffer_u:
            threshold=s.min_buy_strong_15s_z if side>0 else s.min_sell_strong_15s_z
            q30=p30[2]
            older_liq=q30[0].bid_close if side>0 else q30[0].ask_close
            latest_liq=q30[-1].bid_close if side>0 else q30[-1].ask_close
            trend30_z=side*(latest_liq-older_liq)/sigma
            if z15<threshold or trend30_z < -s.max_adverse_30s_z:
                self.stats['micro_30s_veto']+=1;return
        # z is a normalized executable-side price statistic, never P(win).
        if self.rolling.five_second_updates(t.time_msc)<s.min_quote_updates_5s:
            self.stats['micro_activity_reject']+=1;return
        spread_stress,quote_intensity=self.rolling.intensity_and_spread(q,t.spread_points)
        if spread_stress>s.spread_shock_ratio:
            self.stats['micro_spread_shock_reject']+=1;return
        # Step 4: completed native-price-bar EMA/Wilder DI where ready; otherwise
        # the causal three-minute price-efficiency proxy is the fallback.
        bias=self.rolling.m1.bias(side)
        if bias is None:
            self.indicator_sources['proxy_bidask_efficiency']+=1
            # Already validated by 15s structure + 30s executable breakout.
        else:
            self.indicator_sources['closed_m1_ema20_wilder_di14']+=1
            if s.use_m1_directional_veto and bias<-.25:
                self.stats['micro_m1_directional_veto']+=1;return
        self._signal_meta=dict(side=side,z=round(z,4),z15=round(z15,4),
                               z30=round(z30,4),router=s.breakout_router,
                               efficiency=round(abs(net)/max(1.,travel),4),
                               spread_stress=round(spread_stress,4),quote_count_per_second=round(quote_intensity,3),
                               indicator_bias=round(bias,4) if bias is not None else 'proxy',
                               first_5s_ms=b5.first_ms,
                               structure_15s_start_ms=b15_source.start_ms,
                               structure_source="active_causal" if live15 else "completed")
        self._open_trade(t,side)

    def _open_trade(self,t:Tick,side:int):
        if self._entries_this_minute>=self.micro_spec.max_entries_per_source_minute:
            self.stats['micro_trade_cap_block']+=1
            return
        before=self.position
        super()._open_trade(t,side)
        if self.position is None or self.position is before:return
        # Exactly one position; preserve original stop and model $2 ceiling.
        self._entries_this_minute+=1
        self._current_peak_cash=-math.inf
        self._last_closed_basket=None
        self._last_closed_15s_basket=None
        self._last_exit_ms=None
        self.entries[-1].update(self._signal_meta)
        self.stats['micro_positions']+=1
        self.pending_mode=0

    def _record_close(self,t:Tick,reason:str,exit_u:int):
        if self.position is not None:
            self._current_peak_cash=None
            self._last_exit_ms=t.time_msc
            self._last_closed_basket=self.rolling.current.get(5000).start_ms if self.rolling.current.get(5000) else None
            self._last_closed_15s_basket=self.rolling.current.get(15000).start_ms if self.rolling.current.get(15000) else None
        super()._record_close(t,reason,exit_u)

    def _signed_trend_score(self,side:int,t:Tick)->float:
        """Asymmetric quote-executable 5/15/30s continuation utility PROXY.

        Uses only real observed previous-second closes; never a calibrated
        probability or proof of positive incremental holding expectancy.
        """
        q5=self.rolling.closes(t.time_msc,5000)
        q15=self.rolling.closes(t.time_msc,15000)
        q30=self.rolling.closes(t.time_msc,30000)
        if len(q5)<3 or len(q15)<8 or len(q30)<15:
            return -1.0
        if t.time_msc-q5[-1].last_ms>2500:
            return -1.0
        now=t.bid_u if side>0 else t.ask_u
        def efficient(q):
            values=[z.bid_close if side>0 else z.ask_close for z in q]
            signed=side*(now-values[0])
            travel=sum(abs(y-x) for x,y in zip(values,values[1:]))
            travel+=abs(now-values[-1])
            return max(-1.,min(1.,signed/max(1.,travel)))
        spread_stress,_=self.rolling.intensity_and_spread(q15,t.spread_points)
        bias=self.rolling.m1.bias(side)
        score=(.45*efficient(q5)+.35*efficient(q15)+.20*efficient(q30)
               +.10*(bias if bias is not None else 0.0)
               -.15*max(0.,spread_stress-1.0))
        return max(-1.0,min(1.0,score))

    def _manage_position(self,t:Tick):
        p=self.position
        if p is None:return
        s=self.micro_spec
        liq=t.bid_u if p.side>0 else t.ask_u
        net=p.side*(liq-p.entry_price_u)*self.cash.k/100.0-self.cash.cost
        self._current_peak_cash=max(net,self._current_peak_cash if self._current_peak_cash is not None else -math.inf)
        age=t.time_msc-p.entry_time_msc
        if self.cash.governor and (self.account.day_lock or self.account.permanent_lock):
            self._record_close(t,'account_halt',liq);return
        if net<=-s.hard_risk_cash:
            # Stops may gap; this is a last available quote, NOT a guaranteed $2 fill.
            self._record_close(t,'risk_first_available',liq);return
        if net>=s.preferred_max_net_cash:
            self._record_close(t,'cash_preferred_cap',liq);return
        if age>=s.max_lifetime_ms:
            self._record_close(t,'micro_timeout',liq);return
        if age<0:
            raise ValueError('Position time travelled backward')
        if self.rolling.last_gap_ms>s.max_quote_gap_ms:
            self._record_close(t,'stale_quote_exit',liq);return
        if net+1e-9<s.min_net_cash:
            return  # Original protective SL remains armed at broker.
        if not s.experimental_runner:
            self._record_close(t,'cash_010_harvest',liq);return
        if self._signed_trend_score(p.side,t)<s.min_runner_trend_score:
            self._record_close(t,'runner_trend_fades',liq);return
        # Stop MUST protect modeled >=$0.10, with broker legal stops distance,
        # without ever widening. This is not a real-world guaranteed fill.
        lock=max(s.min_net_cash,self._current_peak_cash-s.runner_trail_cash)
        lock=min(lock,s.preferred_max_net_cash)
        required_move_u=math.ceil((lock+self.cash.cost)/self.cash.k*100-1e-10)
        desired=p.entry_price_u+p.side*required_move_u
        min_legal=self.cfg.tick_size_points+(self.cfg.broker_stops_points if self.cfg.respect_broker_stops else 0)
        legal=(desired<=t.bid_u-min_legal if p.side>0 else desired>=t.ask_u+min_legal)
        tighter=desired>p.sl_u if p.side>0 else desired<p.sl_u
        stop_net=p.side*(p.sl_u-p.entry_price_u)*self.cash.k/100-self.cash.cost
        if legal and tighter:
            p.sl_u=desired
            self.stats['micro_protected_runner_tighten']+=1
        elif stop_net+1e-9<lock:
            self._record_close(t,'cash_no_legal_protection',liq)
            return
        self.stats['micro_protected_runner_hold']+=1

    def report(self):
        out=super().report()
        out['micro_architecture']='rolling 180s actual ms, completed 5/15/30s quote candles, 1s bid/ask closes'
        out['old_model_auc_used']=False
        out['profit_min_net_cash']=self.micro_spec.min_net_cash
        out['profit_preferred_net_cash']=self.micro_spec.preferred_max_net_cash
        out['hard_risk_cash']=self.micro_spec.hard_risk_cash
        out['experimental_runner_enabled']=self.micro_spec.experimental_runner
        out['native_MQL5_indicator_parity_verified']=False
        out['entry_gate_stats']={k:int(v) for k,v in self.stats.items() if k.startswith(('micro_', 'gate_'))}
        out['indicator_sources']=dict(self.indicator_sources)
        out['last_and_volume_nonzero_quotes']={'last':self.rolling.nonzero_last,'volume':self.rolling.nonzero_volume}
        out['research_account_governor_enabled']=self.cash.governor
        return out
