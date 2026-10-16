"""Tick-driven retail execution model: bid/ask, latency, margin, fees and drawdown."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from math import inf, isfinite
from collections import defaultdict
from typing import Protocol
from .feeds import Quote
from .bars import Bar, CandleStream

@dataclass(frozen=True)
class BrokerConfig:
    name: str
    initial_balance: float = 100.0
    contract_size: float = 100.0     # explicit research assumption; never inferred from ticks
    leverage: float = 500.0         # explicit research assumption
    min_lot: float = 0.01
    lot_step: float = 0.01
    max_lot: float = 10.0
    commission_per_lot_side: float = 0.0
    adverse_slippage_price: float = 0.0  # quote price units (USD/oz), paid adversely
    order_latency_ms: int = 250
    max_spread_price: float = 2.0
    min_stop_distance_price: float = 0.0
    stopout_margin_ratio: float = 0.50
    max_positions: int = 1

    def __post_init__(self):
        if (self.initial_balance <= 0 or self.contract_size <= 0 or self.leverage <= 0 or
            self.min_lot <= 0 or self.lot_step <= 0 or self.max_lot < self.min_lot or
            self.commission_per_lot_side < 0 or self.adverse_slippage_price < 0 or
            self.order_latency_ms < 0 or self.max_spread_price < 0 or
            self.min_stop_distance_price < 0 or self.stopout_margin_ratio <= 0 or
            self.max_positions != 1):
            raise ValueError('invalid execution / risk configuration')

@dataclass(slots=True)
class Position:
    side: int
    lots: float
    entry: float
    entry_ms: int
    stop: float | None
    target: float | None
    paid_entry_fee: float
    entry_reason: str = 'strategy'
    entry_sequence: int = 0

@dataclass(slots=True)
class Pending:
    kind: str
    side: int
    lots: float
    stop_distance: float | None
    target_distance: float | None
    due_ms: int
    sent_sequence: int
    reason: str
    position_sequence: int = -1

class Strategy(Protocol):
    def on_tick(self, q: Quote, engine: 'Replay') -> None: ...
    def on_bar(self, bar: Bar, q: Quote, engine: 'Replay') -> None: ...

class Replay:
    def __init__(self, config: BrokerConfig, strategy: Strategy, timeframes: tuple[int,...]=(5,15,30,45,60,300,3600)):
        self.cfg=config; self.strategy=strategy; self.bars=CandleStream(timeframes)
        self.balance=config.initial_balance; self.equity=config.initial_balance
        self.peak=config.initial_balance; self.max_dd=0.; self.max_dd_pct=0.
        self.max_margin_used=0.; self.bankrupt=False; self.stopouts=0
        self.quote: Quote | None=None; self.seq=0
        self.position: Position | None=None
        self.pending: list[Pending]=[]; self.trades: list[dict]=[]; self.rejections=defaultdict(int)
        self.events=defaultdict(int); self.max_quote_gap_ms=0; self.last_ms: int | None=None
    def _mark(self,q: Quote):
        self.equity=self.balance
        if self.position:
            p=self.position
            exit_price = q.bid if p.side==1 else q.ask
            self.equity+=(exit_price-p.entry)*p.side*p.lots*self.cfg.contract_size
        self.peak=max(self.peak,self.equity)
        dd=self.peak-self.equity; self.max_dd=max(self.max_dd,dd)
        if self.peak>0: self.max_dd_pct=max(self.max_dd_pct, 100*dd/self.peak)
        self.bankrupt |= self.equity<=0
    def _margin(self, price: float, lots: float) -> float:
        return abs(price*lots*self.cfg.contract_size/self.cfg.leverage)
    def request_entry(self,side:int,lots:float,*,stop_distance:float|None=None,target_distance:float|None=None,reason:str='strategy')->bool:
        if not self.quote: raise RuntimeError('cannot send before first quote')
        if side not in (-1,1): raise ValueError('side must be -1/+1')
        if (stop_distance is not None and stop_distance<=0) or (target_distance is not None and target_distance<=0):
            raise ValueError('protective distances must be positive')
        # This is a strictly single-position research engine. Never let a strategy
        # enqueue a burst of stale entry requests that fill after its signal expires.
        if self.position is not None:
            self.rejections['entry_while_position_open']+=1
            return False
        if any(o.kind=='entry' for o in self.pending):
            self.rejections['duplicate_pending_entry']+=1
            return False
        if self.bankrupt:
            self.rejections['account_ruin']+=1
            return False
        self.pending.append(Pending('entry',side,lots,stop_distance,target_distance,
                                    self.quote.ms+self.cfg.order_latency_ms,self.seq,reason))
        self.events['entry_requests']+=1
        return True
    def request_close(self, reason='strategy'):
        if self.position and self.quote and not any(o.kind=='close' for o in self.pending):
            self.pending.append(Pending('close',0,0,None,None,self.quote.ms+self.cfg.order_latency_ms,self.seq,reason,
                                        self.position.entry_sequence))
    def request_modify_stop(self, new_stop: float, reason: str = 'strategy') -> bool:
        """Queue a broker-constrained protective-stop improvement, never a relaxation.

        Stop changes are acknowledged only on a *later* observed quote (and
        after order_latency_ms). The old protective stop remains active while
        the modification is pending. This models quote-price level legality,
        not actual MT5 order-server responses or freeze levels.
        """
        if self.position is None or self.quote is None:
            self.rejections['modify_no_position'] += 1
            return False
        if not isfinite(new_stop) or new_stop <= 0:
            raise ValueError('new_stop must be a positive finite price')
        p = self.position
        if (p.side == 1 and p.stop is not None and new_stop <= p.stop or
            p.side == -1 and p.stop is not None and new_stop >= p.stop):
            self.rejections['stop_relaxation_or_no_change'] += 1
            return False
        if any(x.kind == 'modify_stop' for x in self.pending):
            self.rejections['duplicate_stop_modification'] += 1
            return False
        self.pending.append(Pending(
            'modify_stop', 0, 0, new_stop, None,
            self.quote.ms + self.cfg.order_latency_ms, self.seq, reason,
            p.entry_sequence))
        self.events['stop_modification_requests'] += 1
        return True

    def _exit(self,q:Quote,price:float,reason:str):
        p=self.position
        if not p:return
        fee=self.cfg.commission_per_lot_side*p.lots
        gross=(price-p.entry)*p.side*p.lots*self.cfg.contract_size
        pnl=gross-p.paid_entry_fee-fee
        # Entry fee was charged when opening; avoid charging it twice in account balance.
        self.balance+=gross-fee
        self.trades.append({'entry_ms':p.entry_ms,'exit_ms':q.ms,'side':p.side,'lots':p.lots,
                            'entry_price':p.entry,'exit_price':price,'gross_pnl':round(gross,8),
                            'net_pnl':round(pnl,8),'reason':reason,'entry_fee':p.paid_entry_fee,
                            'exit_fee':fee,'broker':self.cfg.name,'entry_reason':p.entry_reason})
        self.position=None;self._mark(q);self.events['closed_trades']+=1
        self.pending=[r for r in self.pending if r.kind not in ('close','modify_stop')]
    def _validate_lots(self,lots):
        n=round((lots-self.cfg.min_lot)/self.cfg.lot_step)
        return self.cfg.min_lot<=lots<=self.cfg.max_lot and abs(self.cfg.min_lot+n*self.cfg.lot_step-lots)<1e-8
    def _process_due(self,q:Quote):
        ready=[r for r in self.pending if r.due_ms<=q.ms and r.sent_sequence<self.seq]
        self.pending=[r for r in self.pending if r not in ready]
        for r in ready:
            if r.kind=='close':
                if self.position and self.position.entry_sequence==r.position_sequence:
                    p=self.position; raw=q.bid if p.side==1 else q.ask
                    self._exit(q,raw-p.side*self.cfg.adverse_slippage_price,r.reason)
                else:
                    self.rejections['stale_close_action']+=1
                continue
            if r.kind=='modify_stop':
                p=self.position
                if p is None or p.entry_sequence!=r.position_sequence:
                    self.rejections['stale_stop_modification']+=1
                    continue
                proposed=r.stop_distance  # absolute stop price in this pending action
                quote_side=q.bid if p.side==1 else q.ask
                allowed=((p.side==1 and proposed < quote_side-self.cfg.min_stop_distance_price) or
                         (p.side==-1 and proposed > quote_side+self.cfg.min_stop_distance_price))
                improving=(p.stop is None or
                           (p.side==1 and proposed>p.stop) or
                           (p.side==-1 and proposed<p.stop))
                if not allowed:
                    self.rejections['stop_modify_broker_level']+=1
                elif not improving:
                    self.rejections['stop_modify_no_improvement']+=1
                else:
                    p.stop=proposed
                    self.events['stop_modifications_filled']+=1
                continue
            reason=None
            price=(q.ask if r.side==1 else q.bid)+r.side*self.cfg.adverse_slippage_price
            if self.bankrupt: reason='account_ruin'
            elif self.position is not None: reason='position_limit'
            elif not self._validate_lots(r.lots): reason='invalid_lot'
            elif q.ask-q.bid>self.cfg.max_spread_price: reason='spread'
            elif r.stop_distance is not None and r.stop_distance<self.cfg.min_stop_distance_price:reason='stop_level'
            elif r.target_distance is not None and r.target_distance<self.cfg.min_stop_distance_price:reason='target_level'
            elif self.equity-self._margin(price,r.lots)<0:reason='insufficient_margin'
            if reason:
                self.rejections[reason]+=1;continue
            fee=self.cfg.commission_per_lot_side*r.lots
            self.balance-=fee
            self.position=Position(r.side,r.lots,price,q.ms,
                    price-r.side*r.stop_distance if r.stop_distance is not None else None,
                    price+r.side*r.target_distance if r.target_distance is not None else None,fee,r.reason,self.seq)
            self.events['filled_entries']+=1
            self.max_margin_used=max(self.max_margin_used,self._margin(price,r.lots))
    def _process_stops(self,q:Quote):
        if not self.position: return
        p=self.position; raw=q.bid if p.side==1 else q.ask
        # Server-side protective orders triggered on the observable tradable side.
        if p.stop is not None and (raw<=p.stop if p.side==1 else raw>=p.stop):
            self._exit(q,raw-p.side*self.cfg.adverse_slippage_price,'stop');return
        if p.target is not None and (raw>=p.target if p.side==1 else raw<=p.target):
            self._exit(q,raw-p.side*self.cfg.adverse_slippage_price,'target');return
        if self.equity<self.cfg.stopout_margin_ratio*self._margin(raw,p.lots):
            self.stopouts+=1
            self._exit(q,raw-p.side*self.cfg.adverse_slippage_price,'stopout')
    def on_quote(self,q:Quote):
        if q.broker!=self.cfg.name:raise ValueError('mixed broker feed prohibited')
        if self.last_ms is not None and q.ms<self.last_ms:raise ValueError('noncausal quote order')
        if self.last_ms is not None:self.max_quote_gap_ms=max(self.max_quote_gap_ms,q.ms-self.last_ms)
        self.last_ms=q.ms;self.seq+=1;self.quote=q;self.events['ticks']+=1
        if self.position: self._mark(q);self._process_stops(q)
        if self.pending: self._process_due(q)
        if self.position: self._mark(q)
        # Strategy sees only bars completed before this quote (not the incomplete current bar).
        for bar in self.bars.update(q):self.strategy.on_bar(bar,q,self)
        self.strategy.on_tick(q,self)
        if self.position: self._mark(q)
    def snapshot(self)->dict:
        vals=[float(t['net_pnl']) for t in self.trades]
        gains=sum(max(0,v) for v in vals);losses=sum(max(0,-v) for v in vals)
        wins=sum(v>0 for v in vals); losing=sum(v<0 for v in vals)
        periods={}
        for name,fmt in [('hour','%Y-%m-%dT%H:00Z'),('day','%Y-%m-%d'),('week','%G-W%V'),('month','%Y-%m')]:
            bucket=defaultdict(list)
            for t in self.trades:
                bucket[datetime.fromtimestamp(t['exit_ms']/1000,tz=timezone.utc).strftime(fmt)].append(t['net_pnl'])
            results=[]
            for key,xs in sorted(bucket.items()):
                gp=sum(max(0,v) for v in xs); gl=sum(max(0,-v) for v in xs)
                w=sum(v>0 for v in xs); l=sum(v<0 for v in xs)
                cumulative=0.0;peak=0.0;realized_dd=0.0
                for v in xs:
                    cumulative+=v;peak=max(peak,cumulative)
                    realized_dd=max(realized_dd,peak-cumulative)
                results.append({'period':key,'trades':len(xs),'net_profit':round(sum(xs),6),
                                'gross_profit_net_of_fees':round(gp,6),
                                'gross_loss_net_of_fees':round(gl,6),
                                'profit_factor_net_of_fees':round(gp/gl,6) if gl else None,
                                'win_accuracy_pct':round(100*w/len(xs),4),
                                'wins':w,'losses':l,'win_loss_count_ratio':round(w/l,6) if l else None,
                                'max_closed_trade_drawdown_usd':round(realized_dd,6)})
            periods[name]=results
        hour_by_day=defaultdict(list)
        for h in periods['hour']:
            hour_by_day[h['period'][:10]].append(h['net_profit'])
        profitable_hour_coverage={day:{'trading_hours':len(xs),'positive_trading_hours':sum(v>0 for v in xs),
                                          'positive_fraction_pct':round(100*sum(v>0 for v in xs)/len(xs),3)}
                                  for day,xs in sorted(hour_by_day.items())}
        return {'config':asdict(self.cfg),'status':'RESEARCH_ONLY_NOT_LIVE_CERTIFIED',
                'starting_balance':self.cfg.initial_balance,'ending_balance':round(self.balance,6),
                'open_position_at_end':self.position is not None,'unsettled_orders':len(self.pending),
                'ending_equity':round(self.equity,6),'net_realized':round(sum(vals),6),
                'gross_profit_net_of_fees':round(gains,6),'gross_loss_net_of_fees':round(losses,6),
                'profit_factor_net_of_fees':round(gains/losses,6) if losses else None,
                'trades':len(vals),'accuracy_pct':round(100*wins/len(vals),4) if vals else None,
                'win_loss_count_ratio':round(wins/losing,6) if losing else None,
                'max_equity_drawdown_usd':round(self.max_dd,6),
                'max_equity_drawdown_pct':round(self.max_dd_pct,6),
                'max_margin_used':round(self.max_margin_used,6),'margin_stopouts':self.stopouts,
                'bankruptcy_observed':self.bankrupt,'unfilled_or_rejected':dict(self.rejections),
                'events':dict(self.events),'max_quote_gap_ms':self.max_quote_gap_ms,
                'periods':periods,'positive_hour_coverage_trade_active_only':profitable_hour_coverage}
