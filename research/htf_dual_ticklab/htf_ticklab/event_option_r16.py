"""R16 research-only event option: continuation | improved entry | exhaustion flip.
Only prior observed executable bid/ask can trigger. All actual fills/rejections,
fees, margin and stops belong to SharedSignalArbiter/Replay. No profitability claim.
"""
from dataclasses import dataclass,replace
from .signal_bus import SignalIntent
from .quote_flow import ClosedQuoteFlow
@dataclass(frozen=True)
class Options:
    ttl:int=3500
    improvement:float=.25
    rebound:float=.12
    continuation:float=.45
    exhaustion:float=.70
    reversal_confirm:float=.20
    max_spread:float=1.5
    flow_threshold:float=.2
    def __post_init__(self):
        if self.ttl<=0 or min(self.improvement,self.rebound,self.continuation,
          self.exhaustion,self.reversal_confirm,self.max_spread)<=0:
            raise ValueError('invalid execution path geometry')
        if not 0<=self.flow_threshold<=1:
            raise ValueError('invalid flow evidence threshold')
class EventOptionSource:
    def __init__(self,source,opts=None):
        self.source=source;self.o=opts or Options();self.flow=ClosedQuoteFlow()
        self.broker=None;self.last_ms=-1;self.intent=None
        self.start=0;self.executable=0.;self.middle=0.;self.original_spread=0.
        self.best=None;self.flip=None
        self.counts=dict(armed=0,continuation=0,improved=0,reversal=0,
                         expired=0,busy=0,duplicates=0,spread=0)
    def _time(self,q):
        if self.broker is not None and q.broker!=self.broker:
            raise ValueError('broker tape contamination')
        if q.ms<self.last_ms:raise ValueError('noncausal quote order')
        self.broker=q.broker;self.last_ms=q.ms
    def _capture(self,signals,q,account):
        immediate=[]
        for s in signals or ():
            if not isinstance(s,SignalIntent):raise TypeError('invalid source intent')
            if s.kind!='entry':immediate.append(s);continue
            if s.observed_ms!=q.ms:raise ValueError('future/stale source intent')
            if self.intent or account.position_side or account.pending_entry:
                self.counts['duplicates']+=1;continue
            if q.ask-q.bid>self.o.max_spread:self.counts['spread']+=1;continue
            self.intent=s;self.start=q.ms
            self.executable=q.ask if s.side==1 else q.bid
            self.middle=(q.bid+q.ask)/2;self.original_spread=q.ask-q.bid
            self.best=None;self.flip=None;self.counts['armed']+=1
        return tuple(immediate)
    def on_bar(self,bar,q,account):
        self._time(q)
        if bar.end_ms>q.ms:raise ValueError('future bar')
        return self._capture(self.source.on_bar(bar,q,account),q,account)
    def on_tick(self,q,account):
        self._time(q);self.flow.update(q)
        urgent=self._capture(self.source.on_tick(q,account),q,account)
        if urgent:return urgent
        p=self.intent
        if p is None:return ()
        if account.position_side or account.pending_entry:
            self.intent=None;self.counts['busy']+=1;return ()
        if q.ms-self.start>self.o.ttl:
            self.intent=None;self.counts['expired']+=1;return ()
        if q.ask-q.bid>self.o.max_spread:
            self.intent=None;self.counts['spread']+=1;return ()
        if q.ms<=self.start:return ()
        side=p.side;mid=(q.bid+q.ask)/2
        executable=q.ask if side==1 else q.bid
        favorable=side*(executable-self.executable)
        adverse=side*(self.middle-mid)
        newside=side;reason=None;sl=0.;tp=0.
        if self.flip is None and adverse>=self.o.exhaustion:self.flip=mid
        if self.flip is not None and (-side)*(mid-self.flip)>=self.o.reversal_confirm:
            newside=-side;reason='reversal';sl=1.6;tp=4.5
        else:
            if self.best is None or side*(executable-self.best)<0:
                self.best=executable
            gained=side*(executable-self.best)
            price_improved=side*(self.executable-self.best)
            if (price_improved>=self.o.improvement and gained>=self.o.rebound
                and self.flip is None):
                reason='improved';sl=1.5;tp=4.0
            elif favorable>=self.o.continuation and q.ask-q.bid<=self.original_spread:
                f=self.flow.snapshot()
                if f and f.total_updates>=2 and side*f.normalized_flow>=self.o.flow_threshold:
                    reason='continuation';sl=1.8;tp=5.0
        if reason is None:return ()
        self.intent=None;self.counts[reason]+=1
        return (replace(p,side=newside,observed_ms=q.ms,
               stop_distance=sl,target_distance=tp,
               reason='r16_'+reason),)
