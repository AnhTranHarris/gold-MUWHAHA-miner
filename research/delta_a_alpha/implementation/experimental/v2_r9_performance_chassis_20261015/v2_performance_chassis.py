"""Delta-A-alpha V2 PERFORMANCE CHASSIS RESEARCH CHILD — NOT PROMOTED.

Inherited owner-frozen vertical order: L0 tick -> L1 session-specific geometry ->
L2 completed H4/H1/M15/M5 -> L3 hourly high-velocity harvesting -> L4 renewal
-> L5 trend-within-trend -> L6 bounded wrong-way recovery -> L7 shared capital.

Original V1 clean tick/HTF engine + cumulative native G0 router stay intact.
Distinct R9 native microcycle generates source proposals, NOT independent orders.
Uses no calendar-month trade rules or future-completed bars. Research execution
uses real original Bid/Ask, configurable assumed contract, spread/fee, >=250ms.

This is an architectural/integration prototype, NOT a broker parity certificate,
accepted breakthrough, or result of a complete Jan funded month replay.
"""
from __future__ import annotations
from collections import Counter,deque
from dataclasses import dataclass
from typing import Optional
from math import isfinite
from datetime import datetime,timezone
from v1_vertical_grid import CleanV1Engine,Quote
from v1_grid_cumulative_source_adapter_0264 import CumulativeCreatorAdapter

SCALE=1000

@dataclass(frozen=True)
class V2OrderPolicy:
    symbol:str='XAUUSD'
    lot:float=0.01
    contract_oz_per_lot:float=100.0 # assumption, requires verified broker contract
    leverage:float=500.0 # research assumption
    fee_per_close:float=0.20 # research assumption
    spread_limit_usd:float=0.55
    latency_ms:int=250
    signal_ttl_ms:int=2_000
    max_quote_drift_usd:float=1.50
    margin_reserve:float=0.35
    physical_max_open:int=1
    failure_fraction:float=0.60
    def __post_init__(self):
        if self.symbol!='XAUUSD' or self.lot!=.01 or self.contract_oz_per_lot<=0 or self.leverage<=0:raise ValueError('invalid protected capital model')
        if self.physical_max_open!=1 or self.latency_ms<250:raise ValueError('V2 research may not secretly add leverage/capacity or zero-delay fills')
        if self.fee_per_close<0 or self.spread_limit_usd<=0 or self.signal_ttl_ms<self.latency_ms:raise ValueError('unsafe cost model')

@dataclass(frozen=True)
class Proposal:
    time_ms:int
    side:int
    source:str
    owner:str
    regime:str
    session:str
    level:float
    entry_bid:float
    entry_ask:float
    native_parent_id:Optional[int]=None
    source_rank:int=0 # architectural priority only; not optimized profitability score
    def __post_init__(self):
        if self.side not in (-1,1) or self.time_ms<0 or self.entry_ask<self.entry_bid or self.entry_bid<=0:raise ValueError('invalid causal proposal')

@dataclass
class FundedPosition:
    proposal:Proposal
    entry_ms:int
    entry_price:float
    side:int
    hard_stop:float
    stop:float
    trail_on:float
    trail_gap:float
    target:float
    max_hold_ms:int
    favorable_peak:float=0.

class IntraminuteSensor:
    """Completed-observed-second Bid OHLC ring. No future minute extrema."""
    def __init__(self):
        self.sec=None;self.o=self.h=self.l=self.c=0.
        self.completed=deque(maxlen=12)
    def update(self,q:Quote):
        sec=q.time_ms_utc//1000;price=q.bid_raw/SCALE
        if self.sec is None or sec!=self.sec:
            if self.sec is not None:self.completed.append((self.sec,self.o,self.h,self.l,self.c))
            self.sec=sec;self.o=self.h=self.l=self.c=price
        else:
            self.h=max(self.h,price);self.l=min(self.l,price);self.c=price
    def quality(self):
        if len(self.completed)<10:return (0,0.,0.,0)
        a=list(self.completed)[-10:]
        prev=a[0][4];travel=0.;last_sign=0;turns=0
        for v in a[1:]:
            diff=v[4]-prev;travel+=abs(diff)
            sign=1 if diff>0 else -1 if diff<0 else 0
            if sign and last_sign and sign!=last_sign:turns+=1
            if sign:last_sign=sign
            prev=v[4]
        disp=a[-1][4]-a[0][4]
        eff=abs(disp)/(travel+1e-9)
        span=max(v[2] for v in a)-min(v[3] for v in a)
        return disp,eff,span,turns

class R9MinuteCycle:
    """MQL5-inspired minute-frozen price bracket + opposite rearm ONLY on actual funded close.

    Research model has distinct actual account fill semantics; does not assert MT5 parity.
    """
    def __init__(self):
        self.minute=None;self.buy=self.sell=0.;self.mode=0;self.rearms=0;self.sensor=IntraminuteSensor()
        self.current_parent_token=None;self.counts=Counter()
    def observe(self,q:Quote):
        mm=q.time_ms_utc//60_000
        if mm!=self.minute:
            self.minute=mm;self.rearms=0;self.mode=2
            mid=(q.bid_raw+q.ask_raw)/(2*SCALE)
            self.buy=mid+.15;self.sell=mid-.15
            self.current_parent_token=None
            self.counts['minute_reset']+=1
        self.sensor.update(q)
        disp,eff,rng,turns=self.sensor.quality()
        ask=q.ask_raw/SCALE;bid=q.bid_raw/SCALE
        if eff<.70 or turns>9 or rng<.50:return 0
        if self.mode in (1,2) and ask>=self.buy and disp>=.15:return 1
        if self.mode in (-1,2) and bid<=self.sell and disp<=-.15:return -1
        return 0
    def offered(self):
        self.mode=0 # prevent infinite proposals before fill/close
        self.counts['offered']+=1
    def funded_close(self,proposal:Proposal,exit_ms:int):
        if proposal.source!='R9_M1_BRACKET_S1':return
        if exit_ms//60_000==self.minute and self.rearms<3:
            self.rearms+=1;self.mode=-proposal.side
            self.counts['funded_opposite_rearms']+=1
        else:self.mode=0

class MultiTimeframeOwner:
    """H4 context; H1 location; M15 phase; M5 transfer. Does NOT demand naive agreement.

    Hard requirement is only as-of complete and fresh bars before funded execution.
    """
    roles=('H4','H1','M15','M5')
    widths={'H4':14_400_000,'H1':3_600_000,'M15':900_000,'M5':300_000}
    def classify(self,bars,now_ms):
        if any(bars.get(k) is None for k in self.roles):return ('WARMUP',False)
        if any(bars[k].end_ms>now_ms or now_ms-bars[k].end_ms>2*self.widths[k] for k in self.roles):return ('STALE',False)
        def sign(v):return 1 if v.close_raw>v.open_raw else -1 if v.close_raw<v.open_raw else 0
        h4,h1,m15,m5=[bars[k] for k in self.roles]
        a,b,c,d=map(sign,[h4,h1,m15,m5])
        # A high-speed source can produce countertrend entries when an explicitly
        # owned H1/M5 pullback regime exists; false triple-vote veto avoided.
        if b and d and b==d:return ('TREND_TRANSFER' if c==b else 'PULLBACK_TRANSFER',True)
        if b and d and b!=d:return ('OPPOSED_HTF_TRANSITION',True)
        return ('RANGE_OR_NEUTRAL',True)

class FundedGovernor:
    """Shared broker-shadow funded account. No virtual PnL; one physical slot.
    All fills and exit marks use opposing original quote side.
    """
    def __init__(self,cash=100.,policy=None):
        self.policy=policy or V2OrderPolicy();self.initial=float(cash);self.cash=float(cash)
        self.peak_equity=self.cash;self.equity=self.cash;self.max_dd=0.
        self.pos:Optional[FundedPosition]=None;self.pending:Optional[Proposal]=None
        self.last_trade_ms=-1;self.settlements=[];self.counts=Counter();self.fail=False
    @property
    def multiplier(self):return self.policy.contract_oz_per_lot*self.policy.lot
    def _quote_side(self,q,side,entry):
        return (q.ask_raw if side>0 else q.bid_raw)/SCALE if entry else (q.bid_raw if side>0 else q.ask_raw)/SCALE
    def mark(self,q):
        eq=self.cash
        if self.pos: eq+=self.pos.side*(self._quote_side(q,self.pos.side,False)-self.pos.entry_price)*self.multiplier-self.policy.fee_per_close
        self.equity=eq;self.peak_equity=max(eq,self.peak_equity);self.max_dd=max(self.max_dd,self.peak_equity-eq)
        if self.equity<self.initial*self.policy.failure_fraction:self.fail=True
    def funded(self,q):
        """Return funded closure (proposal, timestamp, pnl), else None."""
        self.mark(q)
        if not self.pos:return None
        p=self.pos;now=q.time_ms_utc;price=self._quote_side(q,p.side,False)
        favorable=(price-p.entry_price)*p.side
        p.favorable_peak=max(p.favorable_peak,favorable)
        if favorable>=p.trail_on:
            candidate=price-p.side*p.trail_gap
            p.stop=max(candidate,p.stop) if p.side>0 else min(candidate,p.stop)
        stop=(p.side>0 and price<=p.stop) or (p.side<0 and price>=p.stop)
        target=favorable>=p.target
        expired=now-p.entry_ms>=p.max_hold_ms
        if not(stop or target or expired):return None
        pnl=(price-p.entry_price)*p.side*self.multiplier-self.policy.fee_per_close
        self.cash+=pnl;self.pos=None;self.last_trade_ms=now;self.mark(q)
        rec={'entry_ms':p.entry_ms,'exit_ms':now,'net':pnl,'source':p.proposal.source,'session':p.proposal.session,'regime':p.proposal.regime,'side':p.side,'entry':p.entry_price,'exit':price,'reason':'STOP' if stop else 'TARGET' if target else 'MAX_HOLD'}
        self.settlements.append(rec);self.counts['closed']+=1
        return (p.proposal,now,pnl)
    def request(self,p,q):
        if self.fail or self.pos or self.pending:return False
        if p.time_ms!=q.time_ms_utc:raise AssertionError('candidate cannot travel backward/forward')
        self.pending=p;self.counts['proposed']+=1;return True
    def execute(self,q):
        p=self.pending
        if not p or self.pos:return False
        now=q.time_ms_utc;pol=self.policy
        if now-p.time_ms>pol.signal_ttl_ms:
            self.pending=None;self.counts['proposal_timeout']+=1;return False
        if now-p.time_ms<pol.latency_ms:return False
        self.pending=None
        if self.fail:return False
        spread=(q.ask_raw-q.bid_raw)/SCALE
        px=self._quote_side(q,p.side,True)
        old=p.entry_ask if p.side>0 else p.entry_bid
        if spread>pol.spread_limit_usd or abs(px-old)>pol.max_quote_drift_usd:
            self.counts['spread_or_drift_reject']+=1;return False
        # Margin USD = price * notional ounces / leverage. No fee double booking.
        required=px*self.multiplier/pol.leverage
        if required>self.equity*(1-pol.margin_reserve):
            self.counts['margin_reject']+=1;return False
        # Distinct exit policies: R9 fast cycle versus V1 native structural,
        # session volatility applies to the slow structural sleeve, not R9 fast.
        if p.source=='R9_M1_BRACKET_S1':
            stop,arm,gap,target,hold=.30,.10,.03,99.,30_000
        else:
            stop,arm,gap,target,hold=3.5,2.5,1.75,4.5,180_000
        hard=px-p.side*stop
        self.pos=FundedPosition(p,now,px,p.side,hard,hard,arm,gap,target,hold)
        self.counts['filled']+=1;self.last_trade_ms=now
        self.mark(q)
        return True

class V2PerformanceChassis:
    """Research orchestration: current native V1 G0 PLUS fast R9; all share L2-L7.

    Outputs separate original-native and proposed fast-cycle shadow events,
    one shared funded account, never merged hypothetical profit streams.
    """
    def __init__(self,starting_cash=100.,policy=None,enable_r9=True,enable_native=True):
        self.root=CleanV1Engine();self.native=CumulativeCreatorAdapter() if enable_native else None
        self.r9=R9MinuteCycle();self.struct=MultiTimeframeOwner()
        self.account=FundedGovernor(starting_cash,policy);self.enable_r9=enable_r9
        self.counts=Counter();self.last_ms=None;self.last_frame=None
        self.native_event_log=[]
    def _session(self,frame):
        names=frame.l1_session.open_desks
        if 'LONDON' in names and 'NEW_YORK' in names:return 'LONDON_NY_OVERLAP'
        if 'LONDON' in names:return 'LONDON'
        if 'NEW_YORK' in names:return 'NEW_YORK'
        if 'TOKYO' in names or 'SYDNEY' in names:return 'ASIA'
        return 'TRANSITION'
    def on_tick(self,q:Quote,*,broker_tradable=True):
        if not broker_tradable:raise ValueError('fail closed: explicit simulator quote permission required')
        if self.last_ms is not None and q.time_ms_utc<self.last_ms:raise ValueError('out of sequence L0')
        self.last_ms=q.time_ms_utc
        # Shared physical lifecycle BEFORE candidate generation; released slot
        # cannot be simultaneously re-entered on its own exit tick.
        closed=self.account.funded(q)
        if closed:self.r9.funded_close(closed[0],closed[1]);self.counts['funded_closes']+=1
        if not closed:self.account.execute(q)
        frame=self.root.on_tick(q,broker_trading_confirmed=True)
        self.last_frame=frame;self.counts['ticks']+=1
        bars=frame.l2_completed_bars
        regime,ready=self.struct.classify(bars,q.time_ms_utc)
        session=self._session(frame)
        self.counts['regime_'+regime]+=1
        # Original V1 cumulative router must receive every actual tick,
        # even while the portfolio is halted/occupied (shadow continues).
        native=()
        if self.native is not None:
            signs=tuple((1 if bars[k].close_raw>bars[k].open_raw else -1 if bars[k].close_raw<bars[k].open_raw else 0) if bars[k] is not None else None for k in ('H4','H1','M15','M5'))
            native=self.native.on_tick(q,bars.get('H1'),frame.l1_session.suggested_geometry,
                 last_completed_m5=bars.get('M5'),last_completed_h4=bars.get('H4'),
                 broker_tradable=True,completed_grid_signs=signs)
            if native:self.counts['native_source_proposals']+=len(native)
        side=self.r9.observe(q) if self.enable_r9 else 0
        if side:self.counts['r9_raw_candidates']+=1
        if self.account.fail or not ready:
            self.counts['not_funded_'+('halt' if self.account.fail else regime)]+=1
            return
        options=[]
        for n in native:
            options.append(Proposal(q.time_ms_utc,n.side,n.source,'ORIGINAL_V1_G0',regime,session,n.crossing_level_usd,q.bid_raw/SCALE,q.ask_raw/SCALE,n.paid_proposal_id,2))
        if side and self.enable_r9:
            # R9 native counterpart: retains same vertical process/HTF observation,
            # but does not impose false H1=M5 vote or require original G0 rung crossing.
            options.append(Proposal(q.time_ms_utc,side,'R9_M1_BRACKET_S1','R9_FAST_FINITE_GRID',regime,session,(self.r9.buy if side>0 else self.r9.sell),q.bid_raw/SCALE,q.ask_raw/SCALE,None,1))
        if not options:return
        self.counts['asof_eligible_proposals']+=len(options)
        if self.account.pos or self.account.pending:
            self.counts['capacity_blocked']+=len(options);return
        # Preserve original native-grid priority when both sources compete,
        # no hindsight R9 source-profit labels in arbitration.
        options.sort(key=lambda p:(-p.source_rank,p.source,p.side))
        chosen=options[0]
        if self.account.request(chosen,q):
            self.counts['selected_'+chosen.owner]+=1
            if chosen.source=='R9_M1_BRACKET_S1':self.r9.offered()
    def result(self):
        p=self.account
        return {'source':'V2_RESEARCH_SIMULATION_NOT_MT5_PARITY','cash':p.cash,'net':p.cash-p.initial,'trades':len(p.settlements),
                'gross_profit':sum(max(0,x['net']) for x in p.settlements),
                'gross_loss':sum(min(0,x['net']) for x in p.settlements),
                'max_tick_equity_dd':p.max_dd,'capital_halt':p.fail,'position_open':p.pos is not None,
                'order_pending':p.pending is not None,'events':dict(self.counts),'funding':dict(p.counts),
                'r9':dict(self.r9.counts),'native':self.native.stats() if self.native else None}
