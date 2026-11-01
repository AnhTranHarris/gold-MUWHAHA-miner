#!/usr/bin/env python3
"""R9 v2 event-first fast entry / single-position real-tick chronology.

Research implementation, not approved trading model. All decisions use only data
at or before their timestamp; one active position, never overlapping outcomes.
No forced trades or quota-filling. Original R9 ActivePath exit rules are unchanged.
This is the high-volume *experimental lane*, not the original frozen BNP/NP
policy; a volume success alone does not validate profitability or NP calibration.
"""
from __future__ import annotations
import argparse,collections,csv,gzip,hashlib,json,math,sys,time
from dataclasses import dataclass
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'r9_entry_router_v2'/'src'))
from router_v2_dataset import iter_ticks
from router_v2_features import Quote,MinuteStore,session_utc
from router_v2_labels import ActivePath

WINDOWS=(250,500,1000,5000,15000,30000,45000,60000,300000)
TAUS=(250,500,1000,5000,15000,45000,240000)
NAMES=('BU','BD','AU','AD','SW','SN')

class RollingWindow:
    """Amortized O(1) completed-slot values and quote activity, no lookahead."""
    def __init__(self,duration:int):
        self.duration=duration;self.entries=collections.deque()
        self.sum=0.;self.sum2=0.;self.path=0.;self.count=0;self.spr=0.;self.spr2=0.;self.activity=0
        self.high=collections.deque();self.low=collections.deque()
    def add(self,t:int,px:float,spread:float,nquotes:int):
        if self.entries:
            self.path+=abs(px-self.entries[-1][1])
        self.entries.append((t,px,spread,nquotes));self.sum+=px;self.sum2+=px*px;self.spr+=spread;self.spr2+=spread*spread;self.activity+=nquotes;self.count+=1
        while self.high and self.high[-1][1]<=px:self.high.pop()
        self.high.append((t,px))
        while self.low and self.low[-1][1]>=px:self.low.pop()
        self.low.append((t,px))
        cutoff=t-self.duration
        while self.entries and self.entries[0][0]<=cutoff:
            old=self.entries.popleft();self.sum-=old[1];self.sum2-=old[1]*old[1]
            self.spr-=old[2];self.spr2-=old[2]*old[2];self.activity-=old[3];self.count-=1
            if self.entries:self.path-=abs(self.entries[0][1]-old[1])
        while self.high and self.high[0][0]<=cutoff:self.high.popleft()
        while self.low and self.low[0][0]<=cutoff:self.low.popleft()
        if self.path<0 and self.path>-1e-7:self.path=0.
    def snapshot(self):
        if not self.count:return {'ready':0.,'range':0.,'vol':0.,'disp':0.,'eff':0.,'boll':0.,'spread':0.,'rate':0.,'pos':0.}
        a=self.entries[0][1];b=self.entries[-1][1]
        mean=self.sum/self.count
        sd=math.sqrt(max(0.,self.sum2/self.count-mean*mean))
        hi=self.high[0][1];lo=self.low[0][1]
        return {'ready':float(self.entries[-1][0]-self.entries[0][0]>=self.duration-500),
                'range':hi-lo,'vol':sd,'disp':b-a,'eff':abs(b-a)/(self.path+1e-10),
                'boll':(b-mean)/(2*sd+1e-8),'spread':self.spr/self.count,
                'rate':self.activity/(self.duration/1000),
                'pos':(b-lo)/(hi-lo+1e-8)}

class SlotHawkes:
    """250ms causal aggregation of all tick-event marks, O(7*6) / slot.
    The aggregation preserves counts but approximates within-slot event times;
    explicitly NOT identical to the original per-tick Hawkes parametrization.
    """
    def __init__(self):
        self.v={tau:[0.]*6 for tau in TAUS};self.last=None
    def update(self,t,marks):
        if self.last is not None:
            delta=t-self.last
            if delta<0:raise ValueError('nonchronological')
            for tau in TAUS:
                d=math.exp(-delta/tau)
                self.v[tau]=[x*d+m for x,m in zip(self.v[tau],marks)]
        else:
            for tau in TAUS:self.v[tau]=list(marks)
        self.last=t
    def snapshot(self,tau):
        v=self.v[tau]
        up=v[0]+v[2]+.5;down=v[1]+v[3]+.5
        sn=v[5]+.25;sw=v[4]+.25
        return {'dir':(up-down)/(up+down),'sp':(sn-sw)/(sn+sw),
                'burst':math.log1p(max(0.,sum(v))),'bid':(v[0]-v[1])/(v[0]+v[1]+.5),
                'ask':(v[2]-v[3])/(v[2]+v[3]+.5)}

class FastClock:
    def __init__(self):
        self.windows={h:RollingWindow(h) for h in WINDOWS};self.hawkes=SlotHawkes();self.minutes=MinuteStore()
        self.last=None;self.slot=None;self.mid=0.;self.spread=0.;self.marks=[0.]*6;self.slot_ticks=0
        self.valid_since=None;self.total_slots=0;self.gaps=0;self.last_event=[]
    def add(self,q:Quote):
        if self.last is not None and q.utc_ms<self.last.utc_ms:raise ValueError('out-of-order')
        self.minutes.add(q)
        slot=(q.utc_ms//250)*250
        flushed=False
        if self.slot is not None and slot!=self.slot:
            self._flush();flushed=True
            if slot-self.slot>15000:
                # reset only short-horizon quote excitation; longer HTF remains intact
                self.hawkes=SlotHawkes();self.gaps+=1;self.valid_since=q.utc_ms
            self.slot=slot;self.slot_ticks=0;self.marks=[0.]*6
        if self.slot is None:
            self.slot=slot;self.valid_since=q.utc_ms
        if self.last is not None and (q.utc_ms-self.last.utc_ms)<=15000:
            d1=q.bid-self.last.bid;d2=q.ask-self.last.ask;ds=q.spread-self.last.spread
            idxs=[i for i,d in ((0,d1),(1,-d1),(2,d2),(3,-d2),(4,ds),(5,-ds)) if d>1e-10]
            for i in idxs:self.marks[i]+=1
            self.last_event=idxs
        else:self.last_event=[]
        self.mid=q.mid;self.spread=q.spread;self.slot_ticks+=1;self.last=q
        return flushed
    def _flush(self):
        if not self.slot_ticks:return
        self.hawkes.update(self.slot,self.marks)
        for w in self.windows.values():w.add(self.slot,self.mid,self.spread,self.slot_ticks)
        self.total_slots+=1
    def ready(self):
        return bool(self.windows[300000].count and self.windows[300000].entries[-1][0]-self.windows[300000].entries[0][0]>=299000)
    def features(self,q):
        st={h:self.windows[h].snapshot() for h in WINDOWS}
        hk={h:self.hawkes.snapshot(h) for h in (500,1000,5000,15000,45000)}
        # Completed bars only; context priors never block entry.
        context={}
        for n in (15,60,240):
            if len(self.minutes.completed)>=n:
                a=self.minutes.last(n);context[n]=(a[-1].close-a[0].open)/(max(0.01,max(x.high for x in a)-min(x.low for x in a)))
            else:context[n]=None
        return {'w':st,'h':hk,'geo':context,'session':session_utc(q.utc_ms),'spread':q.spread,'events':tuple(self.last_event)}

def specialist_evidence(f):
    """Competing causal continuation/reversal specialists, no historical futures.
    Any specialist can nominate a direction. No volume-filling or forced entry.
    """
    w=f['w'];h=f['h'];s1=w[1000];s5=w[5000];s45=w[45000];s300=w[300000]
    # direction by quote-response impulse with 1s,5s and 45s state
    flow=0.55*h[1000]['dir']+0.25*h[5000]['dir']+0.2*h[500]['dir']
    speed=(0.65*s1['disp']+0.35*s5['disp'])/max(.05,s300['vol']*2)
    spread_quality=min(1.0,max(-1.,h[1000]['sp']))
    continuation=flow + .40*math.tanh(speed)+.12*spread_quality
    # counter-direction specialist when overextension and flow begins to reverse
    reversion=(-0.52*math.tanh(s5['boll']) + .32*flow
                - .14*math.tanh(s45['disp']/max(.10,s300['vol']*3)))
    # 5m and HTF context vote contributes weak prior, never hard veto
    geo=f['geo'];ctx=sum(.06*math.tanh(v) for v in geo.values() if v is not None)
    continuation+=ctx;reversion+=.5*ctx
    # choose most strongly supported side across specialists
    candidates=[('continuation',continuation),('reversal',reversion)]
    lane,value=max(candidates,key=lambda z:abs(z[1]))
    side=1 if value>0 else -1
    evidence=abs(value)
    # Cost awareness; spread is the executable obstacle, not a disguised rate quota.
    cost=f['spread'];pressure=max(0.,s5['range'])
    return side,evidence,lane,pressure,cost

class TickExactActivePath(ActivePath):
    """R9-style tick-sequence execution including later ticks at the same ms.

    The parent's identical-timestamp guard drops later ticks inside the entry
    millisecond, even though they are chronologically subsequent source records.
    This subclass resolves that correctness defect without shifting timestamps.
    """
    def update(self,q):
        if self.done:return None
        if q.utc_ms<self.entry_ms:raise ValueError('nonchronological')
        px=q.bid if self.side>0 else q.ask
        excursion=(px-self.entry_price)*self.side
        self.mfe=max(self.mfe,excursion);self.mae=min(self.mae,excursion)
        self.loss_tail.append(excursion-self.fee)
        if len(self.loss_tail)>256:self.loss_tail.pop(0)
        for t in (0.10,0.30,0.50):
            key=f'{t:.2f}'
            if self.targets[key] is None and excursion-self.fee>=t-1e-12:
                self.targets[key]=q.utc_ms
        if (self.side>0 and q.bid<=self.stop) or (self.side<0 and q.ask>=self.stop):
            self.stop_ms=q.utc_ms
            return self.finish(q,'SL',px)
        if excursion>=.10-1e-12:
            # R9 trailing stop activation, same original rounding method.
            from router_v2_labels import round_tick
            next_sl=round_tick(px-self.side*.03)
            self.stop=max(self.stop,next_sl) if self.side>0 else min(self.stop,next_sl)
        if q.utc_ms-self.entry_ms>=30000:return self.finish(q,'TIMEOUT',px)
        return None

@dataclass
class Position:
    path:ActivePath
    lane:str
    evidence:float
    entry_native:int

class HighVolumeStream:
    def __init__(self,max_spread=1.5,min_evidence=.18,fee=.02):
        self.clock=FastClock();self.max_spread=max_spread;self.min_evidence=min_evidence;self.fee=fee
        self.position=None;self.count=collections.Counter();self.trades=[];self.last_trade=None;self.trade_writer=None
        self.net=0.;self.wins=0;self.gains=0.;self.losses=0.
    def on_quote(self,q):
        self.count['ticks']+=1
        closed=False
        if self.position:
            result=self.position.path.update(q)
            if result is not None:
                p=self.position;self.position=None;closed=True
                rec={'entry_ms':result.entry_ms,'exit_ms':result.exit_ms,'side':result.side,
                     'entry_price':result.entry_price,'exit_price':result.exit_price,'net':result.net,
                     'exit_type':result.exit_type,'spread':result.spread,'mfe':result.mfe,'mae':result.mae,
                     'lane':p.lane,'evidence':p.evidence}
                if self.trade_writer is not None:self.trade_writer.writerow(rec)
                else:self.trades.append(rec)
                self.net+=rec['net'];self.wins+=int(rec['net']>0)
                self.gains+=max(0.,rec['net']);self.losses+=-min(0.,rec['net'])
                self.count['closed']+=1
                if result.net>0:self.count['wins']+=1
                self.count['net_micro_dollars']+=int(round(result.net*10000))
        flushed=self.clock.add(q)
        if not flushed:return
        self.count['completed_250ms_slots']+=1
        # No same-tick reentry; next 250ms completed quote is earliest possible.
        if self.position is not None or closed:return
        if not self.clock.ready():self.count['warmup']+=1;return
        self.count['eligible_scan']+=1
        if q.spread>self.max_spread:self.count['spread_reject']+=1;return
        f=self.clock.features(q)
        side,evidence,lane,pressure,cost=specialist_evidence(f)
        if evidence<self.min_evidence:self.count['evidence_reject']+=1;return
        # A supportive path should have at least a tiny observable local move.
        if pressure<.06:self.count['activity_reject']+=1;return
        self.count['qualified']+=1
        self.position=Position(TickExactActivePath(q,side,fee=self.fee),lane,evidence,q.native_ms or q.utc_ms)
        self.count['entries']+=1
    def run(self,source_file,source,limit=None):
        t=time.monotonic()
        for i,q in enumerate(iter_ticks(source_file,source)):
            if limit and i>=limit:break
            self.on_quote(q)
        self.count['open_at_eof']=int(self.position is not None)
        elapsed=time.monotonic()-t
        net=self.net;wins=self.wins;gains=self.gains;losses=self.losses
        return {'source':source,'input':Path(source_file).name,'ticks':self.count['ticks'],
                'trades':self.count['closed'],'net':round(net,2),'win_rate':round(wins/self.count['closed'],6) if self.count['closed'] else 0,
                'profit_factor':round(gains/losses,4) if losses else None,
                'counts':dict(self.count),'elapsed_s':round(elapsed,2),
                'status':'HIGH_VOLUME_CAPACITY_EXPERIMENT_NOT_APPROVED','nonoverlapping':True,
                'real_tick_future_only_for_exits':True,'teacher_runtime_used':False,
                'model':'causal_multispecialist_entry_research_not_fitted_NP'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ticks',required=True);ap.add_argument('--source',choices=['coinexx','dukascopy'],required=True)
    ap.add_argument('--out',required=True);ap.add_argument('--limit',type=int,default=None)
    ap.add_argument('--min-evidence',type=float,default=.18);ap.add_argument('--max-spread',type=float,default=1.5)
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    st=HighVolumeStream(max_spread=a.max_spread,min_evidence=a.min_evidence)
    with gzip.open(out/'trades.csv.gz','wt',newline='') as f:
        cols=['entry_ms','exit_ms','side','entry_price','exit_price','net','exit_type','spread','mfe','mae','lane','evidence']
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();st.trade_writer=w
        report=st.run(a.ticks,a.source,a.limit)
    (out/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
