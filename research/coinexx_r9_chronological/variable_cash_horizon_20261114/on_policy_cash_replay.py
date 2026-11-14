"""Cash-ladder whole-system chronological research integration for original Coinexx quotes.

Not MetaTrader fills or a profitability-certified EA. Reuses original v1.90
R9HybridGateBaseline events for v1.94 entrance/SL/rearm research. No MQL5 changes.
This explicitly exposes unverified account K/C, position-only fills, missing
model evidence and quote-only liquidity proxies. Full source baseline parity
against original frozen trade ledger is mandatory.
"""
from __future__ import annotations
from collections import deque, defaultdict
from dataclasses import dataclass
from math import tanh, sqrt, isfinite
from statistics import median
from typing import Any

from coinexx_r9.r9_baseline import R9HybridGateBaseline, R9Config, session_code
from coinexx_r9.models import Tick
from cash_ladder import (CashLadderSpec, CurrentPosition, AccountSnapshot,
                         VariableCashHorizonPolicy, ConditionalEvidence)


@dataclass(frozen=True)
class ResearchCash:
    k: float = 1.0  # illustrative $ per $1 XAU price at 0.01 lot
    cost: float = 0.20  # illustrative additional roundtrip cash beyond spread
    initial_capital: float = 100_000.0
    governor: bool = False
    def __post_init__(self):
        if any(not isfinite(z) for z in (self.k,self.cost,self.initial_capital)) or self.k<=0 or self.cost<0 or self.initial_capital<=0:
            raise ValueError('Invalid unverified cash/account assumptions')


class CashAccount:
    """Research proxy for one account, not multi-EA deal-server state."""
    def __init__(self, cash: ResearchCash):
        self.cash=cash
        self.equity=cash.initial_capital
        self.peak=cash.initial_capital
        self.day=None
        self.day_start_cash=cash.initial_capital
        self.day_gross_loss=0.0
        self.day_gross_profit=0.0
        self.day_charges=0.0
        self.day_lock=False
        self.permanent_lock=False
        self.rejections=defaultdict(int)
        self.halts=defaultdict(int)
        self.max_drawdown_cash=0.0
        self.gross_total=0.0
        self.fees_total=0.0
        self.day_records=[]
        self.max_open_mark_loss=0.0
        self.last_mark=cash.initial_capital
        self.closed_count=0

    def begin_tick(self, t: Tick, floating_cash=0.0):
        day=t.time_s//86400  # ORIGINAL source-native calendar, not inferred UTC
        if day!=self.day:
            if self.day is not None:
                self.day_records.append(dict(day=self.day, gross_losses=self.day_gross_loss,
                                             fees=self.day_charges, realized_equity=self.equity,
                                             halted=self.day_lock))
            self.day=day
            self.day_start_cash=max(0.01,self.equity)
            self.day_gross_loss=0.0
            self.day_gross_profit=0.0
            self.day_charges=0.0
            self.day_lock=False
        net_equity=self.equity+floating_cash
        self.last_mark=net_equity
        self.peak=max(self.peak,net_equity)
        self.max_drawdown_cash=max(self.max_drawdown_cash,self.peak-net_equity)
        self.max_open_mark_loss=max(self.max_open_mark_loss,max(0,-floating_cash))
        if not self.cash.governor:return
        if net_equity<=0.75*self.cash.initial_capital:
            if not self.permanent_lock:self.halts['25pct_absolute']+=1
            self.permanent_lock=True
        if net_equity<=0.90*self.peak:
            if not self.permanent_lock:self.halts['10pct_peak']+=1
            self.permanent_lock=True
        if self.consumed(floating_cash)>=self.allowed_budget():
            if not self.day_lock:self.halts['daily_gross']+=1
            self.day_lock=True

    def allowed_budget(self):
        return min(.12*self.day_start_cash,
                   .04*self.day_start_cash+.25*self.day_gross_profit)

    def consumed(self, floating_cash=0.):
        return self.day_gross_loss+self.day_charges+max(0.,-floating_cash)

    def equity_after_close(self, trade):
        gross=trade.net_price_u/100.0*self.cash.k
        net=gross-self.cash.cost
        self.equity+=net
        self.closed_count+=1
        self.day_gross_loss+=max(0.,-gross)
        self.day_gross_profit+=max(0.,gross)
        self.day_charges+=self.cash.cost
        self.gross_total+=max(0.,-gross)
        self.fees_total+=self.cash.cost
        return net

    def mark_cash(self,side,entry,t):
        liq=t.bid_u if side>0 else t.ask_u
        return (side*(liq-entry)/100.0)*self.cash.k-self.cash.cost

    def risk_acceptable(self, new_loss_cash:float):
        if not self.cash.governor: return True
        if self.permanent_lock or self.day_lock:
            self.rejections['governor_locked']+=1;return False
        if self.consumed()+max(0,-new_loss_cash)>self.allowed_budget():
            self.rejections['gross_risk_capacity']+=1;return False
        return True

    def snapshot(self):
        return AccountSnapshot(self.cash.initial_capital,
                               max(self.peak,self.cash.initial_capital),
                               max(0.,self.last_mark),
                               self.consumed(),
                               self.allowed_budget())


class QuoteRegime:
    """Single shared online quote-only market sketch, no OHLC reconstruction.

    Subsecond bid/ask quote arrivals do not represent executed volume/order book.
    Completed observed second records are used at selection; no future bars.
    """
    def __init__(self):
        self.second=-1
        self.updates=0
        self.mid2=0
        self.spread=0
        self.completed=deque(maxlen=180) # (second, mid*2, spread, quote-count)
        self.last_ms=None
        self.last_gap_ms=0
        self.count=0

    def update(self,t:Tick):
        if self.last_ms is not None and t.time_msc<self.last_ms:
            raise ValueError('Noncausal Coinexx timestamp')
        self.last_gap_ms=(t.time_msc-self.last_ms) if self.last_ms is not None else 0
        self.last_ms=t.time_msc
        if t.time_s!=self.second:
            if self.second>=0:
                self.completed.append((self.second,self.mid2,self.spread,self.updates))
            self.second=t.time_s;self.updates=0
        self.updates+=1
        self.mid2=t.bid_u+t.ask_u
        self.spread=t.ask_u-t.bid_u
        self.count+=1

    def state(self,side:int,t:Tick,atr_m5_cents:float|None=None)->dict:
        q=list(self.completed)
        if not q or t.time_s-q[-1][0]>2 or self.last_gap_ms>2500:
            return {'available':False,'reason':'stale_or_no_completed_quote_second'}
        # Only completed second signals; choice of at-or-before old anchors
        # is marked as missing when no quote exists near target wallclock.
        def anchor(seconds):
            target=t.time_s-seconds
            for sec,mid,sp,cnt in reversed(q):
                if sec<=target and target-sec<=2:return (sec,mid,sp,cnt)
            return None
        a3,a10,a30,a120=(anchor(x) for x in (3,10,30,120))
        if a3 is None or a10 is None or a30 is None or a120 is None:
            return {'available':False,'reason':'incomplete_nested_trend'}
        curr=self.mid2
        s=lambda anchor: side*(curr-anchor[1])/2.0
        d3,d10,d30,d120=(s(a) for a in (a3,a10,a30,a120))
        if len(q)<30:return {'available':False,'reason':'insufficient_quote_liquidity_history'}
        last30=q[-30:]
        n30=sum(x[3] for x in last30)/len(last30)
        spreads=[x[2] for x in last30]
        med_sp=max(1.,median(spreads))
        spread_stress=self.spread/med_sp
        quote_stress=n30/max(1.,self.updates)
        deltas=[(b[1]-a[1])/2.0 for a,b in zip(last30,last30[1:]) if b[0]-a[0]==1]
        if len(deltas)<15:return {'available':False,'reason':'incomplete_second_volatility'}
        sigma=sqrt(sum(x*x for x in deltas)/len(deltas))
        denom=max(1.,sigma,med_sp/2.)
        e3=tanh(d3/(sqrt(3.)*denom))
        e10=tanh(d10/(sqrt(10.)*denom))
        e30=tanh(d30/(sqrt(30.)*denom))
        e120=tanh(d120/(sqrt(120.)*denom))
        # Predeclared NON-CALIBRATED confidence index, never call it P(win).
        persistence=.25*e3+.35*e10+.30*e30+.10*e120
        disagreement=(min(e3,e10,e30,e120)<0 < max(e3,e10,e30,e120))
        stress=max(0.,spread_stress-1.) + .15*max(0.,quote_stress-2.)
        strength=persistence-.20*stress-.15*int(disagreement)
        return dict(available=True, strength=strength, spreads_relative=spread_stress,
                    quote_count_relative=n30/max(1.,self.updates),
                    sigma_1s_quote_cents=sigma,
                    signed_trend_cents={'3s':d3,'10s':d10,'30s':d30,'120s':d120},
                    nested_disagreement=disagreement,
                    atr_m5_quote_cents=atr_m5_cents,
                    liquidity_proxy_only=True)


class ManagedR9(R9HybridGateBaseline):
    """Source-preserving R9 base event order with position/lifecycle action hooks."""
    def __init__(self, cfg: R9Config, cash: ResearchCash, mode: str,
                 regime:QuoteRegime|None=None, original_score_map:dict|None=None):
        super().__init__(cfg)
        if mode not in ('original','cash_harvest','regime_probe'):
            raise ValueError('Unknown on-policy mode')
        self.mode=mode
        self.cash=cash
        self.account=CashAccount(cash)
        self.regime=regime
        self.controllers={}
        self.model_scores=original_score_map or {}
        self.score_covered=0
        self.score_missing=0
        self.score_safe_used=0
        self.regime_checked=0
        self.regime_eligible=0
        self.conditional_runner_eligible=0  # NONE validated to date
        self.reasons=defaultdict(int)
        self.month_summaries={}
        self.original_last_tick=None
        self._last_modeled_quote_ms=None
        self._net_cash_sum=0.0
        self._net_cash_hour=defaultdict(float)
        self._net_cash_month=defaultdict(float)
        self._counts_month=defaultdict(int)
        self._net_cash_day=defaultdict(float)
        self._gross_loss_month=defaultdict(float)
        self._net_values=[] # 300k positions, cheap small output in memory
        self._hold_ms=[]
        self._peaks_by_trade=[]
        self._max_underwater=0.0
        self._last_account_day=None
        self._unbounded_snapshot=AccountSnapshot(1000000.,1000000.,1000000.,0.,1000000.)

    def on_tick(self,t:Tick):
        self.original_last_tick=t
        floating=0.
        if self.position:
            floating=self.account.mark_cash(self.position.side,self.position.entry_price_u,t)
        self.account.begin_tick(t,floating)
        super().on_tick(t)

    def _open_trade(self,t:Tick,side:int):
        c=self.cfg
        stopdistance=max(c.stop_loss_pips,c.broker_stops_points+c.tick_size_points if c.respect_broker_stops else 0)
        entry=t.ask_u if side>0 else t.bid_u
        sl=(t.bid_u-stopdistance) if side>0 else (t.ask_u+stopdistance)
        stopcash=side*(sl-entry)/100.*self.cash.k-self.cash.cost
        if stopcash<-2.:self.reasons['blocked_initial_stop_over_2cash']+=1;return
        if not self.account.risk_acceptable(stopcash):return
        super()._open_trade(t,side)
        if self.mode!='original':
            self.controllers[t.ordinal]=VariableCashHorizonPolicy()
        if t.ordinal in self.model_scores:self.score_covered+=1
        else:self.score_missing+=1

    def _record_close(self,t:Tick,reason:str,exit_u:int):
        pos=self.position
        if pos is None:return
        ctrl=self.controllers.pop(pos.entry_ordinal,None)
        if ctrl is not None:
            self._peaks_by_trade.append(ctrl.peak_observed_cash)
        super()._record_close(t,reason,exit_u)
        trade=self.trades[-1]
        net=self.account.equity_after_close(trade)
        self._net_values.append(net)
        self._hold_ms.append(trade.exit_time_msc-trade.entry_time_msc)
        self._net_cash_sum+=net
        from datetime import datetime, timezone
        src_month=datetime.fromtimestamp(trade.entry_time_msc/1000, timezone.utc).strftime('%Y-%m')
        self._net_cash_month[src_month]+=net
        self._counts_month[src_month]+=1
        self._gross_loss_month[src_month]+=max(0.,-net)
        self._net_cash_day[trade.entry_time_msc//86400000]+=net
        self._net_cash_hour[trade.entry_time_msc//3600000]+=net
        self.reasons['closed_'+reason]+=1

    def _process_entries(self,t:Tick):
        if self.cash.governor and (self.account.day_lock or self.account.permanent_lock):
            self.reasons['governor_blocks_entry']+=1
            return
        super()._process_entries(t)

    def _manage_position(self,t:Tick):
        p=self.position
        if p is None:return
        liq=t.bid_u if p.side>0 else t.ask_u
        cashnow=p.side*(liq-p.entry_price_u)/100.0*self.cash.k-self.cash.cost
        if self.cash.governor and (self.account.day_lock or self.account.permanent_lock):
            self._record_close(t,'governor_halt',liq);return
        if self.mode=='original':
            super()._manage_position(t);return
        ctrl=self.controllers.get(p.entry_ordinal)
        if ctrl is None:raise RuntimeError('Missing position-scoped ladder controller')
        # Pure controller consumes broker quote and observed equity; cannot
        # simply infer true broker account from original raw market quotes.
        min_dist=(self.cfg.broker_stops_points+self.cfg.tick_size_points)/100.0 if self.cfg.respect_broker_stops else self.cfg.tick_size_points/100.0
        # Ungoverned replay isolates the exit mechanism; do not silently
        # apply account locks. Governed runs use the actual simulated state.
        snapshot=(self.account.snapshot() if self.cash.governor else
                  self._unbounded_snapshot)
        cp=CurrentPosition(side=p.side,entry_executed_price=p.entry_price_u/100.0,
             liquidation_bid=t.bid_u/100.0,liquidation_ask=t.ask_u/100.0,
             original_or_current_stop_price=p.sl_u/100.0,
             cash_per_xau_price_dollar=self.cash.k,
             additional_roundtrip_cost_cash=self.cash.cost,
             age_seconds=max(0,t.time_msc-p.entry_time_msc)/1000.0,
             since_last_quote_ms=self.regime.last_gap_ms if self.regime else 0,
             min_legal_stop_distance_xau=min_dist)
        # Model-assisted runner eligibility remains ZERO until a policy-specific
        # earlier-period incremental hold cash advantage is independently validated.
        # 5s P5 cash-event probabilities alone may NOT extend holdings.
        action=ctrl.decide(cp,snapshot,None)
        if (self.mode=='regime_probe' and action.action=='CLOSE_NOW' and
            action.reason=='Take $0.50–$1.75 net; no validated positive continuation value' and
            .50<=cashnow<1.75):
            state=self.regime.state(p.side,t,self.atr.atr_u if self.atr.ready else None) if self.regime else None
            self.regime_checked+=1
            if state and state.get('available') and state['strength']>.55 and state['spreads_relative']<1.25:
                # PURELY EXPLORATORY non-validated market-state control, not
                # claimed AI: only extend if can already legally lock >=$0.50.
                intended=max(.50,ctrl.peak_observed_cash-.35)
                desired=cp.stop_price_at_min_net_cash(intended)
                if cp.stop_is_legal_and_tighter(desired):
                    newstop=round(desired*100)
                    p.sl_u=newstop
                    self.regime_eligible+=1
                    self.reasons['experimental_regime_lock']+=1
                    return
                if cp.net_cash(cp.original_or_current_stop_price)>=intended-1e-7:
                    self.regime_eligible+=1
                    self.reasons['experimental_regime_hold']+=1
                    return
        if action.action=='CLOSE_NOW':
            self._record_close(t,'cash_'+action.reason[:20].replace(' ','_'),liq)
        elif action.action=='TIGHTEN_STOP':
            newstop=round(action.hypothetical_stop_price*100)
            if (p.side>0 and newstop>p.sl_u) or (p.side<0 and newstop<p.sl_u):
                p.sl_u=newstop;self.reasons['cash_stop_tighten']+=1
        elif action.action=='BLOCK_ENTRY':
            self._record_close(t,'controller_invalid_block',liq)

    def report(self):
        vals=self._net_values
        if len(vals)==0:return {'mode':self.mode,'trades':0,'net':0.0}
        n=len(vals)
        worst=sorted(vals)[:max(1,int(n*.05))]
        hold=sorted(self._hold_ms)
        peak=self.account.peak
        return {
          'mode':self.mode,'model_score_covered_on_original_ordinals':self.score_covered,
          'model_score_missing_new_or_unscored_ordinals':self.score_missing,
          'validated_model_assisted_runner_trades':self.conditional_runner_eligible,
          'experimental_quote_state_runner_requests':self.regime_eligible,
          'trades':n, 'net_cash':round(self._net_cash_sum,5),
          'net_per_trade':round(self._net_cash_sum/n,6),
          'net_per_active_entry_hour':round(self._net_cash_sum/max(1,len(self._net_cash_hour)),5),
          'active_entry_hours':len(self._net_cash_hour),
          'mean_hold_sec':round(sum(self._hold_ms)/(1000*n),5),
          'p95_hold_sec':hold[int(.95*(n-1))]/1000.0,
          'p99_hold_sec':hold[int(.99*(n-1))]/1000.0,
          'win_fraction':round(sum(v>0 for v in vals)/n,6),
          'target_ge_0_5':sum(v>=.50-1e-9 for v in vals),
          'target_ge_1_75':sum(v>=1.75-1e-9 for v in vals),
          'loss_le_minus_2':sum(v<=-2.0 for v in vals),
          'gross_realized_losses':round(-sum(min(0.,v) for v in vals),5),
          'closed_trade_cvar95_loss':round(-sum(worst)/len(worst),6),
          'max_account_peak_drawdown_cash':round(self.account.max_drawdown_cash,5),
          'account_end_equity':round(self.account.equity,5),
          'governor_halts':dict(self.account.halts),
          'governor_rejections':dict(self.account.rejections),
          'monthly_net':{k:round(v,5) for k,v in sorted(self._net_cash_month.items())},
          'monthly_trades':dict(self._counts_month),
          'monthly_gross_net_losses':{k:round(v,5) for k,v in sorted(self._gross_loss_month.items())},
          'rearms':int(self.stats['rearms']),
          'close_reasons':dict(self.reasons),
          'source_hour_cash_negative_count':sum(v<0 for v in self._net_cash_hour.values()),
          'source_hour_cash_positive_count':sum(v>0 for v in self._net_cash_hour.values()),
          'source_day_cash_negative_count':sum(v<0 for v in self._net_cash_day.values()),
          'source_day_cash_positive_count':sum(v>0 for v in self._net_cash_day.values()),
          'note':'Quote-only modeled account cash, not MT5 fills. Source-native clock; no cross-EA governor.'
        }