"""Clean V1 single vertically integrated research architecture (not certified profitable).
One tick chain: UTC clock -> four simultaneous session states -> completed MTF
opportunity/volume -> microgrid candidate -> regime QA -> trend QA -> bounded
failure recovery -> one portfolio capital/execution controller. Sessions can
NEVER issue orders. Broker execution is research SIMULATED ONLY. Never imports
contaminated Jan/Feb implementation code.
"""
from __future__ import annotations
from collections import Counter,deque
from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Optional
import math
from v1_vertical_grid import Quote,CleanV1Engine,ClosedBar
from v1_grid_136b_cooperative_adapter import CooperativeGridGenesis
from v1_grid_admission_arbiter import GridQuoteArbiter
from v1_paid_close_watchdog import PaidCloseWatchdog
from v1_session_broker_clock import local_clocks

PRICE_SCALE=1000

@dataclass(frozen=True)
class DeskSpec:
    name:str
    # Four competing, RECONSTRUCTIBLE hypotheses on the same vertical spine.
    l1_opportunity:str
    l2_structure_role:str
    l3_geometry:str
    l4_regime_quality:str
    l5_trend_quality:str
    l6_failure_management:str
    l7_risk_profile:str
    gap_usd:float
    spread_max_usd:float
    stop_usd:float
    target_usd:float
    max_horizon_ms:int
    min_m5_range_usd:float
    min_activity_5s:int
    cap:int
    trail_trigger_usd:float
    trail_distance_usd:float

DESKS={
 "SYDNEY":DeskSpec("SYDNEY","open/close rotational & spread-aware","H4 envelope + H1 location; M15 compression M5 rejection","low-density rotation after M5 excursion","spread-qualified rotational state","failed-edge reclaim quality","early exit and state-aware reassessment","low one-position heat",1.20,.65,3.4,2.8,240000,.55,4,1,2.1,2.0),
 "TOKYO":DeskSpec("TOKYO","Tokyo local opening range and Sydney overlap","H4 context H1 range M15 phase M5 transfer","opening-range break/retest only after completion","activity+spread regime","H1/M15 compatible reversal-or-continuation","failed ignition exit, no generic hedge","one-position heat",1.00,.62,3.2,3.1,180000,.55,5,1,1.8,1.9),
 "LONDON":DeskSpec("LONDON","Asia-range transition to London volatility","H4 direction H1 structure M15 pullback M5 transfer","Asia sweep/continuation into directional microgrid","trend activity confirmed not just clock","HTF continuation/pullback capture","structure invalidation and no-loss scaling","overlap-aware heat cap",1.25,.70,4.0,4.2,240000,.75,8,2,2.2,2.3),
 "NEW_YORK":DeskSpec("NEW_YORK","London-NY overlap / US impulse / later NY phase","H4 environment H1 alignment M15 phase M5 transfer","pullback/retest after high-liquidity impulse","fast tape plus spread and event control","trend-in-trend momentum quality","stop warning + bounded directional re-evaluation","volatility-limited shared heat",1.45,.78,4.5,4.7,210000,.85,10,2,2.4,2.4)
}

@dataclass(frozen=True)
class Opportunity:
    time_ms:int
    desk:str
    side:int
    current_bid:float
    current_ask:float
    source:str
    proposed_expiry_ms:int
    geometry:str
    level:float

@dataclass
class Position:
    side:int; desk:str; entry_price:float; entry_ms:int; stop:float; target:float
    peak_favorable:float=0.0
    warning:bool=False

@dataclass
class Pending:
    opportunity:Opportunity
    arrival_ms:int
    expiry_ms:int

class FourSessionV1:
    """Entire staged funnel; no model path exists for session-only trades."""
    def __init__(self,*,starting_cash=300.0,lot=0.01,contract_oz=100.0,
                 leverage=None,commission_per_roundtrip_usd=0.20,
                 latency_ms=250,broker_session_confirmed=False,
                 margin_reserve_fraction=.35,global_max_open=2,
                 require_all_htf=True):
        self.root=CleanV1Engine()
        # Pre-L1 creator-grid crossing SOURCE ONLY; no direct physical orders.
        self.creator_genesis=CooperativeGridGenesis()
        self.cash=float(starting_cash);self.equity=self.cash;self.initial=self.cash
        self.lot=lot;self.contract_oz=contract_oz
        self.leverage=leverage
        self.commission=commission_per_roundtrip_usd
        self.latency_ms=latency_ms
        self.broker_session_confirmed=broker_session_confirmed
        self.reserve=margin_reserve_fraction
        self.global_max_open=global_max_open
        self.require_all_htf=require_all_htf
        self.positions=[];self.pending=[]
        self.events=Counter();self.desk_events=Counter();self.realized=[]
        self.last_mid_by_desk={};self.grid_arbiter=GridQuoteArbiter();self.last_order_tick=None
        self.last_tick=None;self.tick_rate=deque();self.peak_equity=self.cash
        self.drawdown_max=0.0;self.max_open=0;self.hard_fail=False
        # G0 source and L7 request arbitration are distinct chronological stages
        self.daily=Counter()
        self.watchdog_closed={k:deque(maxlen=8) for k in DESKS}
        self.paid_watchdog=PaidCloseWatchdog(expected_lot=lot)
        self.watchdog_relock_until={k:0 for k in DESKS}
        self.recovery_intent=None # a bounded, L2-confirmation-dependent correction proposal
    def _mark(self,q):
        eq=self.cash
        for p in self.positions:
            px=q.bid_raw/PRICE_SCALE if p.side==1 else q.ask_raw/PRICE_SCALE
            eq+=(px-p.entry_price)*p.side*self.contract_oz*self.lot-self.commission
        self.equity=eq
        self.peak_equity=max(self.peak_equity,eq)
        self.drawdown_max=max(self.drawdown_max,self.peak_equity-eq)
        if eq<self.initial*.65:self.hard_fail=True
    def _complete_close(self,p,q,reason):
        if self.last_order_tick==q.time_ms_utc:
            raise RuntimeError('more than one simulated execution at same UTC millisecond')
        self.last_order_tick=q.time_ms_utc
        px=q.bid_raw/PRICE_SCALE if p.side==1 else q.ask_raw/PRICE_SCALE
        pnl=(px-p.entry_price)*p.side*self.contract_oz*self.lot-self.commission
        self.cash+=pnl
        self.realized.append((q.time_ms_utc,p.desk,pnl,reason))
        self.watchdog_closed[p.desk].append(pnl)
        if len(self.watchdog_closed[p.desk])>=2 and all(x<0 for x in list(self.watchdog_closed[p.desk])[-2:]):
            self.watchdog_relock_until[p.desk]=q.time_ms_utc+60_000
            self.events['l4_watchdog_relock']+=1
        if pnl>0:self.events['l4_earned_result']+=1
        day=datetime.fromtimestamp(q.time_ms_utc/1000,tz=timezone.utc).date().isoformat()
        self.daily[(day,'funded_closes')]+=1
        self.positions.remove(p);self.events['closed']+=1
    def _life(self,q,fr):
        for p in list(self.positions):
            sp=DESKS[p.desk];px=q.bid_raw/PRICE_SCALE if p.side==1 else q.ask_raw/PRICE_SCALE
            favorable=(px-p.entry_price)*p.side
            p.peak_favorable=max(p.peak_favorable,favorable)
            if p.peak_favorable>=sp.trail_trigger_usd:
                guarded=p.entry_price+p.side*(p.peak_favorable-sp.trail_distance_usd)
                p.stop=max(p.stop,guarded) if p.side==1 else min(p.stop,guarded)
            # L6: independent management quality, warning is not automatic reverse order.
            if favorable<-sp.stop_usd*.45 and not p.warning:
                p.warning=True;self.events['l6_warning']+=1
            if self.last_order_tick==q.time_ms_utc:
                self.events['l7_exit_deferred_quote_budget']+=1
                continue
            if p.warning and favorable<-sp.stop_usd*.65:
                # Same-side position closes; no loss-dependent rescue positions.
                self._complete_close(p,q,'L6_INVALIDATION')
                if self.recovery_intent is None:
                    self.recovery_intent=(q.time_ms_utc+10_000,p.desk,-p.side)
                    self.events['l6_bounded_recovery_watch']+=1
            elif (p.side==1 and px<=p.stop) or (p.side==-1 and px>=p.stop):
                self._complete_close(p,q,'L7_TRAILING_OR_HARD_STOP')
            elif (p.side==1 and px>=p.target) or (p.side==-1 and px<=p.target):
                self._complete_close(p,q,'L3_TARGET')
            elif q.time_ms_utc-p.entry_ms>=sp.max_horizon_ms:
                self._complete_close(p,q,'L7_TIME_EXPIRY')
    def _execute_pending(self,q):
        for p in list(self.pending):
            if q.time_ms_utc<p.arrival_ms:continue
            if q.time_ms_utc>p.expiry_ms:
                self.pending.remove(p)
                self.events['expired_latency']+=1;continue
            if self.last_order_tick==q.time_ms_utc:
                self.events['one_order_per_tick']+=1
                self.events['l7_pending_deferred_next_quote']+=1
                continue
            self.pending.remove(p)
            self._mark(q)
            if self.hard_fail: self.events['capital_halt']+=1;continue
            if len(self.positions)>=self.global_max_open:
                self.events['global_capacity']+=1;continue
            if len([z for z in self.positions if z.desk==p.opportunity.desk])>=DESKS[p.opportunity.desk].cap:
                self.events['desk_capacity']+=1;continue
            if self.leverage is None or self.leverage<=0:
                self.events['unverified_broker_margin']+=1;continue
            spread=(q.ask_raw-q.bid_raw)/PRICE_SCALE
            if spread>DESKS[p.opportunity.desk].spread_max_usd:
                self.events['spread_drift']+=1;continue
            actual=q.ask_raw/PRICE_SCALE if p.opportunity.side==1 else q.bid_raw/PRICE_SCALE
            original=p.opportunity.current_ask if p.opportunity.side==1 else p.opportunity.current_bid
            if abs(actual-original)>DESKS[p.opportunity.desk].gap_usd:
                self.events['slippage_guard']+=1;continue
            required=actual*self.contract_oz*self.lot/self.leverage
            locked=sum(z.entry_price*self.contract_oz*self.lot/self.leverage for z in self.positions)
            if required+locked>self.equity*(1-self.reserve):
                self.events['margin_denied']+=1;continue
            sp=DESKS[p.opportunity.desk]
            self.last_order_tick=q.time_ms_utc
            self.positions.append(Position(p.opportunity.side,p.opportunity.desk,actual,q.time_ms_utc,
                                           actual-p.opportunity.side*sp.stop_usd,
                                           actual+p.opportunity.side*sp.target_usd))
            self.events['filled']+=1;self.desk_events[(sp.name,'fills')]+=1
            day=datetime.fromtimestamp(q.time_ms_utc/1000,tz=timezone.utc).date().isoformat()
            self.daily[(day,'funded_entries')]+=1
            self.max_open=max(self.max_open,len(self.positions))
    def _structure(self,bars,mid,sp):
        # L2 roles are NOT naive H4/H1/M15 voting: H4 is environment,
        # H1 location/direction, M15 phase, M5 transfer evidence.
        if any(bars[k] is None for k in ('H4','H1','M15','M5')):
            return None,'L2_WARMUP'
        h4,h1,m15,m5=(bars[x] for x in ('H4','H1','M15','M5'))
        m5_span=(m5.high_raw-m5.low_raw)/PRICE_SCALE
        if m5_span<sp.min_m5_range_usd:return None,'L2_NO_MICRO_TRANSFER'
        h4_span=max(.01,(h4.high_raw-h4.low_raw)/PRICE_SCALE)
        env_directionality=abs(h4.close_raw-h4.open_raw)/PRICE_SCALE/h4_span
        h1_span=max(.01,(h1.high_raw-h1.low_raw)/PRICE_SCALE)
        h1_open=h1.open_raw/PRICE_SCALE;h1_close=h1.close_raw/PRICE_SCALE
        parent=1 if h1_close>h1_open else (-1 if h1_close<h1_open else 0)
        h1_position=(mid-h1.low_raw/PRICE_SCALE)/h1_span
        phase=1 if m15.close_raw>m15.open_raw else(-1 if m15.close_raw<m15.open_raw else 0)
        transfer=1 if m5.close_raw>m5.open_raw else(-1 if m5.close_raw<m5.open_raw else 0)
        if sp.name=='SYDNEY':
            # H4 environment needs rotation; H1 relative location defines side;
            # M15 exhaustion and M5 exhaustion/transfer refine opportunity.
            if env_directionality>.50:return None,'L2_SYDNEY_H4_TRENDING'
            if h1_position<.30 and phase==-1 and transfer==-1:
                return 1,'L2_SYDNEY_RANGE_LOWER_EDGE'
            if h1_position>.70 and phase==1 and transfer==1:
                return -1,'L2_SYDNEY_RANGE_UPPER_EDGE'
            return None,'L2_SYDNEY_NOT_RANGE_EDGE'
        if sp.name=='TOKYO':
            # Context: H4 activity; H1 structural location; M15 phase;
            # M5 transfer must agree with prospective continuation.
            if parent==0 or phase==0 or transfer==0:
                return None,'L2_TOKYO_UNRESOLVED'
            if phase==parent and transfer==parent and .15<=h1_position<=.85:
                return parent,'L2_TOKYO_CONFIRMED_TRANSFER'
            return None,'L2_TOKYO_PHASE_NOT_TRANSFERRED'
        if sp.name=='LONDON':
            if parent==0 or transfer!=parent:
                return None,'L2_LONDON_M5_NOT_TRANSFERRED'
            if env_directionality<.10:
                return None,'L2_LONDON_H4_LOW_DIRECTIONAL_CONTEXT'
            if not 0.05<=h1_position<=.95:
                return None,'L2_LONDON_H1_EXHAUSTED_LOCATION'
            if phase==parent:
                return parent,'L2_LONDON_CONTINUATION'
            if phase==-parent:
                return parent,'L2_LONDON_PULLBACK_TRANSFER'
            return None,'L2_LONDON_M15_PHASE_UNRESOLVED'
        # NEW_YORK: HTF directional environment with separate H1 parent and
        # M15 impulse/pullback stage, M5 fresh transfer; no triple vote.
        if parent==0 or transfer!=parent:
            return None,'L2_NY_M5_NOT_TRANSFERRED'
        if env_directionality<.08 or h4_span<2.0:
            return None,'L2_NY_H4_UNFAVORABLE'
        if not .07<=h1_position<=.93:
            return None,'L2_NY_H1_EXHAUSTED_LOCATION'
        if phase==-parent:
            return parent,'L2_NY_PULLBACK_TRANSFER'
        if phase==parent:
            return parent,'L2_NY_TREND_WITHIN_TREND'
        return None,'L2_NY_PHASE_UNRESOLVED'
    def on_tick(self,q:Quote,*,broker_tradable=None,regional_holidays=(),simulate_broker=False):
        # No silent conversion of raw UTC ticks to Coinexx chart clock.
        if broker_tradable is None:broker_tradable=self.broker_session_confirmed
        frame=self.root.on_tick(q,broker_trading_confirmed=broker_tradable,known_holidays=regional_holidays)
        self.events['ticks']+=1
        # True creator-derived 48 completed-H1 parent grid + completed-M5
        # single-rung-per-direction child lattice. These are virtual
        # opportunity hypotheses, never direct entry authorizations.
        genesis_opportunities=self.creator_genesis.on_tick(
            q,frame.l2_completed_bars.get('H1'),
            frame.l1_session.suggested_geometry,
            last_completed_m5=frame.l2_completed_bars.get('M5'),
            last_completed_h4=frame.l2_completed_bars.get('H4'),
            broker_tradable=True)  # observed source tick, NOT broker fill authority
        self.events['prel1_creator_grid_raw']+=len(genesis_opportunities)
        if not simulate_broker or not broker_tradable:
            self.events['l7_pending_cancelled_permission_loss']+=len(self.pending)
            self.pending.clear()
        if simulate_broker and broker_tradable:
            self._life(q,frame)
            self._execute_pending(q)
        elif self.positions:
            self.events['l7_position_lifecycle_deferred_permission_loss']+=len(self.positions)
        self._mark(q)
        now=q.time_ms_utc
        self.tick_rate.append(now)
        while self.tick_rate and self.tick_rate[0]<now-5000:self.tick_rate.popleft()
        self.grid_arbiter.start_quote(now)
        for desk in frame.l1_session.open_desks:
            sp=DESKS[desk];self.events['l1_windows']+=1
            mid=(q.bid_raw+q.ask_raw)/(2*PRICE_SCALE)
            prev=self.last_mid_by_desk.get(desk)
            self.last_mid_by_desk[desk]=mid
            if prev is None:continue
            # L2 structural opportunity density and permission
            direction,tag=self._structure(frame.l2_completed_bars,mid,sp)
            if direction is None:self.events[tag]+=1;continue
            self.events['l2_opportunity_windows']+=1
            # Structural permission CANNOT manufacture a trade without
            # an actual chronological creator-grid price-level CROSSING.
            eligible_grid=[z for z in genesis_opportunities if z.side==direction or z.source.startswith('APR136B_')]
            if not eligible_grid:
                self.events['l3_no_creator_grid_crossing']+=1
                continue
            candidate_grid=eligible_grid[0]
            if candidate_grid.source.startswith('APR136B_'):
                self.events['l3_136b_mom' if candidate_grid.side==direction else 'l3_136b_rev']+=1
            if not self.grid_arbiter.can_request(desk,now):
                self.events['l3_arbiter_not_available']+=1;continue
            self.events['l3_proposals']+=1
            day=datetime.fromtimestamp(now/1000,tz=timezone.utc).date().isoformat()
            self.daily[(day,'l3_proposals')]+=1
            # L3 cannot place an order: must clear entire quality funnel.
            # L4 regime: frequency/spread and market event context.
            spread=(q.ask_raw-q.bid_raw)/PRICE_SCALE
            if len(self.tick_rate)<sp.min_activity_5s:self.events['l4_regime_weak']+=1;continue
            if now<self.watchdog_relock_until[desk]:self.events['l4_relocked']+=1;continue
            if self.paid_watchdog.permit_ready(desk,now,broker_tradable=broker_tradable):
                self.events['l4_broker_paid_parent_context']+=1
            elif self.watchdog_closed[desk] and self.watchdog_closed[desk][-1]>0:
                self.events['l4_simulated_positive_close_NOT_PAID']+=1
            else:self.events['l4_scout_eligible']+=1
            if regional_holidays:self.events['calendar_caution']+=1;continue
            # L5 native trend/range route is already evidence-selected by L2;
            # L5 independently vetoes stale or too broad excursion near M5 boundary.
            m5=frame.l2_completed_bars['M5']
            if m5 is None:self.events['l5_missing_m5']+=1;continue
            extended=abs(mid-m5.close_raw/PRICE_SCALE)
            if extended>sp.stop_usd*2:self.events['l5_overextended']+=1;continue
            m15=frame.l2_completed_bars['M15']
            # Additional L5 trend-within-trend quality distinct from L2 opportunity:
            # fresh price must not contradict completed M15 environment by extreme.
            if m15 and ((direction==1 and q.bid_raw>m15.high_raw+int(sp.stop_usd*PRICE_SCALE)) or
                        (direction==-1 and q.ask_raw<m15.low_raw-int(sp.stop_usd*PRICE_SCALE))):
                self.events['l5_exhausted_phase']+=1;continue
            # L6: a failed old trade cannot generate an opposite order on its own.
            # Only a new full L1→L5 candidate with matching corrected direction
            # can be called a bounded recovery; no size escalation.
            if self.recovery_intent:
                expiry,own,correct_side=self.recovery_intent
                if now>expiry:self.recovery_intent=None
                elif own==desk and correct_side==direction:
                    self.events['l6_state_confirmed_recovery_candidate']+=1
                    self.recovery_intent=None
            # L6: no independent fresh entry; only assesses existing inventory
            # warnings and directional collision when new candidate arrives.
            if any(z.side==-direction and z.warning for z in self.positions):
                self.events['l6_collision']+=1;continue
            self.events['qualified_quality_chain']+=1
            self.daily[(day,'quality_chain')]+=1
            opp=Opportunity(now,desk,direction,q.bid_raw/PRICE_SCALE,q.ask_raw/PRICE_SCALE,
                            f'{tag}|{candidate_grid.source}|r{candidate_grid.rung}',
                            now+sp.max_horizon_ms,frame.l1_session.suggested_geometry,
                            candidate_grid.crossing_level_usd)
            # L7: IMPORTANT no order unless explicitly enabled and broker-tradable
            if not simulate_broker or not broker_tradable:
                self.events['l7_execution_disabled']+=1;continue
            if spread>sp.spread_max_usd:self.events['l7_spread_denied']+=1;continue
            if self.hard_fail:self.events['l7_capital_halt']+=1;continue
            if self.leverage is None or self.leverage<=0:
                self.events['l7_no_margin_config']+=1;continue
            if len(self.positions)+len(self.pending)>=self.global_max_open:
                self.events['l7_prequeue_global_capacity_denied']+=1;continue
            desk_occupied=sum(z.desk==desk for z in self.positions)
            desk_occupied+=sum(z.opportunity.desk==desk for z in self.pending)
            if desk_occupied>=sp.cap:
                self.events['l7_prequeue_desk_capacity_denied']+=1;continue
            # Research-only margin reservation, not verified Coinexx margin.
            unit=self.contract_oz*self.lot/self.leverage
            entry=q.ask_raw/PRICE_SCALE if direction==1 else q.bid_raw/PRICE_SCALE
            locked=sum(z.entry_price*unit for z in self.positions)
            reserved=sum((z.opportunity.current_ask if z.opportunity.side==1
                          else z.opportunity.current_bid)*unit for z in self.pending)
            if (entry*unit+locked+reserved)>self.equity*(1-self.reserve):
                self.events['l7_prequeue_margin_denied']+=1;continue
            if not self.grid_arbiter.claim_eligible_request(desk,now):
                self.events['l7_quote_claimed']+=1;continue
            self.pending.append(Pending(opp,now+self.latency_ms,now+min(2000,sp.max_horizon_ms)))
            self.events['l7_risk_eligible_requests']+=1
            self.daily[(day,'risk_requested')]+=1
        self.last_tick=q
        return frame
    # These methods must be called only from actual observed MT5 DEAL_ADD
    # and verified broker history, never from this simulator's _complete_close.
    def on_broker_parent_intent(self,position_id,desk,observed_ms):
        return self.paid_watchdog.register_parent(position_id,desk,self.lot,observed_ms)

    def on_broker_deal_add(self,**transaction):
        return self.paid_watchdog.on_deal_add(**transaction)

    def on_broker_settlement(self,position_id,*,observed_ms,
                             verified_broker_history,confirmed_net_cash):
        return self.paid_watchdog.confirm_settlement(position_id,
            observed_ms=observed_ms,verified_broker_history=verified_broker_history,
            confirmed_net_cash=confirmed_net_cash)

    def result(self):
        gross_plus=sum(max(x[2],0) for x in self.realized)
        gross_minus=sum(min(x[2],0) for x in self.realized)
        winners=sum(x[2]>0 for x in self.realized)
        desk_pnl={d:round(sum(v[2] for v in self.realized if v[1]==d),4) for d in DESKS}
        desk_closes={d:sum(v[1]==d for v in self.realized) for d in DESKS}
        return dict(starting_balance=self.initial,realized_cash=self.cash,
                    net_realized=self.cash-self.initial,gross_profit=gross_plus,gross_loss=gross_minus,
                    pf=(gross_plus/(-gross_minus) if gross_minus else None),
                    closed=len(self.realized),win_rate=winners/max(1,len(self.realized)),
                    open_positions=len(self.positions),max_open=self.max_open,
                    max_quote_equity_dd=self.drawdown_max,counters=dict(self.events),
                    desk_counters={str(k):v for k,v in self.desk_events.items()},
                    desk_realized_pnl=desk_pnl,desk_closed_trades=desk_closes,
                    day_counters={f'{k[0]}:{k[1]}':v for k,v in self.daily.items()},
                    grid_genesis_stats=self.creator_genesis.stats(),
                    broker_paid_watchdog_stats=self.paid_watchdog.stats(),
                    status='SIMULATION_ONLY_NOT_MT5_BROKER_CERTIFIED')
