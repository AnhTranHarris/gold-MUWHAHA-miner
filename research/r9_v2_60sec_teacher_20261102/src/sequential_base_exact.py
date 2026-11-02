#!/usr/bin/env python3
"""R9 v2 additive sequential quote-response entry specialist; research-only.

Consumes original frozen v2 FastClock + ActivePath via exact source pins.
WAIT is genuine observation of new quote events, NEVER an offline best-delay action.
No synthetic teacher or future price in entry features. Full unchanged R9 style
SL/trail/30s close; distinct CORRECT/INCORRECT/NEUTRAL labels are assigned
only AFTER a position is closed. No claim of fit or calibrated profitability.
"""
from __future__ import annotations
import collections, csv, gzip, json, math, sys
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]/'restore'
sys.path.insert(0,str(ROOT/'repair'/'src'))
sys.path.insert(0,str(ROOT/'original_v2'/'src'))
from high_volume_stream import FastClock, specialist_evidence, TickExactActivePath
from router_v2_dataset import iter_ticks

class OnlineThreeClass:
    """Causal categorical Bayes fitted from completed earlier position outcomes ONLY.

    Shadow prediction; uncalibrated class posterior. No score-based order
    acceptance or 80% guarantee can be claimed before independent calibration.
    """
    CLASSES=('CORRECT','INCORRECT','NEUTRAL')
    def __init__(self,bins=12):
        self.bins=bins;self.n=0;self.nclass=[0]*3
        self.k=19
        self.data=[[[0]*bins for _ in range(3)] for _ in range(self.k)]
    def encode(self,side,pending,q,clock):
        """19 fully causal features across quote response, subsecond Hawkes,
        5m realized geometry, completed 15m/1h/4h priors and UTC session.
        No absent HTF value is silently replaced with a fabricated trend.
        """
        d=q.utc_ms-pending.t
        db=side*(q.bid-pending.bid);da=side*(q.ask-pending.ask)
        mid=(db+da)*.5;spr=q.spread-pending.spread
        f=clock.features(q)
        w=f['w'];h=f['h'];geo=f['geo']
        def bucket(v,scale):return max(0,min(self.bins-1,int(v/scale+self.bins*.5)))
        def signed_geo(n):
            v=geo.get(n)
            return 0 if v is None else max(1,bucket(side*v,.20))
        session=f['session']
        # Session is one non-ordinal category (hash-free fixed lookup).
        code={'sydney':1,'tokyo':2,'london':3,'overlap':4,
              'new_york':5,'rollover':6,'off':7}.get(session,8)
        x=(bucket(db,.02),bucket(da,.02),bucket(min(db,da),.02),
           bucket(spr,.02),bucket(mid,.02),min(self.bins-1,d//250),
           min(self.bins-1,int(q.spread/.15)),
           bucket(side*w[5000]['disp'],.05),
           bucket(side*w[45000]['disp'],.10),
           bucket(side*(w[300000]['pos']-.5),.10),
           min(self.bins-1,int(w[300000]['eff']*self.bins)),
           min(self.bins-1,int(w[300000]['vol']/.10)),
           bucket(side*h[1000]['dir'],.17),
           bucket(side*h[5000]['dir'],.17),
           bucket(h[1000]['sp'],.17),
           signed_geo(15),signed_geo(60),signed_geo(240),min(self.bins-1,code))
        assert len(x)==self.k and all(0<=v<self.bins for v in x)
        return x
    def predict(self,x):
        if self.n<200:return None
        z=[]
        for c in range(3):
            nc=self.nclass[c]
            v=math.log((nc+3)/(self.n+9))
            for j,b in enumerate(x):
                v+=.25*math.log((self.data[j][c][b]+2)/(nc+2*self.bins))
            z.append(v)
        h=max(z);p=[math.exp(a-h) for a in z];s=sum(p)
        return tuple(a/s for a in p)
    def observe(self,x,label):
        k=self.CLASSES.index(label)
        for j,b in enumerate(x):self.data[j][k][b]+=1
        self.nclass[k]+=1;self.n+=1

@dataclass
class Pending:
    t:int; side:int; evidence:float; spread:float; bid:float; ask:float
    lane:str; updates:int=0; quote_t:int=0

class StrictPath(TickExactActivePath):
    def __init__(self,quote,side,fee=.02):
        super().__init__(quote,side,fee=fee)
        self.open_bid=quote.bid;self.open_ask=quote.ask
        self.first=0;self.first_ms=-1
    def update(self,q):
        if q.utc_ms<self.entry_ms:raise ValueError('future tick impossible')
        liq=q.bid if self.side>0 else q.ask
        liq0=self.open_bid if self.side>0 else self.open_ask
        if self.first==0:
            gross=(liq-self.entry_price)*self.side
            displacement=(liq-liq0)*self.side
            if gross-self.fee >= .10-1e-9:
                self.first=1;self.first_ms=q.utc_ms
            elif displacement<=-.10+1e-9:
                self.first=-1;self.first_ms=q.utc_ms
        return super().update(q)
    def strict_label(self,outcome):
        # elapsed >30s (weekend/illiquid gap) never promoted to success
        if outcome.exit_ms-self.entry_ms>30000:return 'NEUTRAL'
        if self.first==1 and outcome.net>0:return 'CORRECT'
        if self.first==-1 or (self.first!=0 and outcome.net<=0):return 'INCORRECT'
        return 'NEUTRAL'

class SequentialRouter:
    def __init__(self,fee=.02,min_evidence=.18,max_spread=1.5,
                 min_echo=.02,max_pending_ms=3000,min_wait_ms=250):
        self.clock=FastClock();self.pending=None;self.active=None
        self.fee=fee;self.min_evidence=min_evidence;self.max_spread=max_spread
        self.min_echo=min_echo;self.max_pending_ms=max_pending_ms;self.min_wait_ms=min_wait_ms
        self.count=collections.Counter();self.byday=collections.defaultdict(lambda:collections.Counter())
        self.byweek=collections.defaultdict(lambda:collections.Counter())
        self.month=collections.Counter();self.writer=None;self.trades=[]
        self.previous_eligible=None
        self.bayes=OnlineThreeClass();self.active_features=None;self.active_prior=None
        self.active_entry_tick_index=None;self.policy=None;self.min_p_correct=0.0
    @staticmethod
    def week(t):
        d=datetime.fromtimestamp(t/1000,timezone.utc).date()
        return f'{d.isocalendar().year}-W{d.isocalendar().week:02d}'
    @staticmethod
    def day(t):return datetime.fromtimestamp(t/1000,timezone.utc).date().isoformat()
    def on_quote(self,q):
        self.count['ticks']+=1
        just_closed=False
        if self.active is not None:
            result=self.active.update(q)
            if result is not None:
                label=self.active.strict_label(result);self.count['closed']+=1
                self.count[label]+=1;self.month['closed']+=1;self.month[label]+=1
                self.count['CORRECT15']+=int(label=='CORRECT' and self.active.first_ms-self.active.entry_ms<=15000)
                self.count['CORRECT30']+=int(label=='CORRECT' and self.active.first_ms-self.active.entry_ms<=30000)
                self.month['CORRECT15']+=int(label=='CORRECT' and self.active.first_ms-self.active.entry_ms<=15000)
                self.month['CORRECT30']+=int(label=='CORRECT' and self.active.first_ms-self.active.entry_ms<=30000)
                self.month['net_microdollar']+=round(result.net*1e6)
                self.bayes.observe(self.active_features,label)
                day=self.day(result.entry_ms);week=self.week(result.entry_ms)
                for b in (self.byday[day],self.byweek[week]):
                    b['closed']+=1;b[label]+=1;b['net_microdollar']+=round(result.net*1e6)
                    b['CORRECT15']+=int(label=='CORRECT' and self.active.first_ms-self.active.entry_ms<=15000)
                    b['CORRECT30']+=int(label=='CORRECT' and self.active.first_ms-self.active.entry_ms<=30000)
                rec={'entry_ms':result.entry_ms,'exit_ms':result.exit_ms,'side':result.side,
                     'entry_price':result.entry_price,'exit_price':result.exit_price,
                     'net':result.net,'class':label,'first_event':self.active.first,
                     'first_event_ms':self.active.first_ms,'exit_type':result.exit_type,
                     'spread':result.spread,'shadow_p_correct':self.active_prior[0] if self.active_prior else None,
                     'prior_finished_trades':self.bayes.n-1,
                     'entry_tick_index':self.active_entry_tick_index,
                     'feature_bins':','.join(str(v) for v in self.active_features),
                     'policy_p_correct':self.policy.predict(self.active_features) if self.policy else None}
                if self.writer:self.writer.writerow(rec)
                else:self.trades.append(rec)
                self.active=None;just_closed=True
        flushed=self.clock.add(q)
        if not flushed or just_closed or self.active is not None:return
        if not self.clock.ready():self.count['warmup']+=1;return
        self.count['eligible_slots']+=1
        if self.pending is not None:
            p=self.pending
            delta=q.utc_ms-p.t
            if delta>self.max_pending_ms:
                self.count['expired']+=1;self.pending=None
            elif delta>=self.min_wait_ms:
                self.count['observed_later_quote']+=1
                if q.spread>self.max_spread:
                    self.count['delayed_spread_reject']+=1;self.pending=None;return
                delta_bid=q.bid-p.bid;delta_ask=q.ask-p.ask
                # Confirm two-sided quote revision, not merely an ask-only lift.
                up_bid=p.side*delta_bid;up_ask=p.side*delta_ask
                echo=min(up_bid,up_ask)
                spread_delta=q.spread-p.spread
                if echo>=self.min_echo and spread_delta<=max(.03,p.spread*.20):
                    # Actual delayed state confirmed; trade NOW at the new quote.
                    self.active_features=self.bayes.encode(p.side,p,q,self.clock)
                    self.active_prior=self.bayes.predict(self.active_features)
                    # Rejected proposals remain pending and can be reconsidered on
                    # later *observed* quotes; no teacher knowledge enters here.
                    if self.policy is not None and self.policy.predict(self.active_features)<self.min_p_correct:
                        self.count['policy_wait']+=1
                        p.updates+=1
                        return
                    self.active_entry_tick_index=self.count['ticks']-1
                    self.active=StrictPath(q,p.side,fee=self.fee)
                    self.count['confirmed_entries']+=1;self.pending=None
                    return
                # An observed adverse, two-sided reversal cancels; this is past-only.
                if max(up_bid,up_ask)<-self.min_echo:
                    self.count['reverse_reject']+=1;self.pending=None
                else:p.updates+=1
            return
        if q.spread>self.max_spread:
            self.count['spread_reject']+=1;return
        f=self.clock.features(q)
        side,evidence,lane,pressure,_=specialist_evidence(f)
        if evidence<self.min_evidence or pressure<.06:
            self.count['candidate_reject']+=1;return
        self.pending=Pending(q.utc_ms,side,evidence,q.spread,q.bid,q.ask,lane)
        self.count['pending_started']+=1
    def run(self,path,source,limit=None,out=None):
        if out is not None:
            out=Path(out);out.mkdir(parents=True,exist_ok=True)
        fh=None
        if out:
            fh=gzip.open(out/'trades.csv.gz','wt',newline='')
            self.writer=csv.DictWriter(fh,fieldnames=['entry_ms','exit_ms','side','entry_price','exit_price','net','class','first_event','first_event_ms','exit_type','spread','shadow_p_correct','prior_finished_trades','entry_tick_index','feature_bins','policy_p_correct']);self.writer.writeheader()
        try:
            for i,q in enumerate(iter_ticks(path,source)):
                if limit is not None and i>=limit:break
                self.on_quote(q)
        finally:
            if fh:fh.close();self.writer=None
        result={'source':source,'input':Path(path).name,'counts':dict(self.count),
                'month':dict(self.month),'byday':{k:dict(v) for k,v in self.byday.items()},
                'byweek':{k:dict(v) for k,v in self.byweek.items()},
                'status':'RESEARCH_ONLY_NOT_TRAINED_OR_APPROVED','future_at_entry_used':False,
                'teacher_runtime_used':False,'strict_success_target':'.10 executable net favorable-first, positive closed net <=30s',
                'idle_days_and_weeks_pass':False,'bayesian_shadow_seen':self.bayes.n,
                'bayesian_shadow_counts':dict(zip(self.bayes.CLASSES,self.bayes.nclass)),
                'policy_min_p_correct':self.min_p_correct,'policy_attached':self.policy is not None}
        if out:(out/'run.json').write_text(json.dumps(result,indent=2))
        return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--ticks',required=True);p.add_argument('--source',required=True,choices=['coinexx','dukascopy']);p.add_argument('--limit',type=int);p.add_argument('--out',required=True)
    a=p.parse_args();r=SequentialRouter().run(a.ticks,a.source,a.limit,a.out)
    print(json.dumps({'counts':r['counts'],'month':r['month'],'status':r['status']},indent=2))
