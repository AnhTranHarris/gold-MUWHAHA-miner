#!/usr/bin/env python3
"""Causal Bayesian + Neyman-Pearson + quote-Hawkes R9 *entry* research candidate.

NOT an MT5 EA, actual trade-volume VWAP, or a certified calibrated probability.
The position management is inherited unchanged from the January-parity R9 replay.
All feature evidence at t uses ticks <=t and COMPLETED subminute buckets only.
Historical training/calibration labels are available solely AFTER the shadow trade closes.
"""
from __future__ import annotations
import argparse, collections, datetime as dt, hashlib, json, math, sys, csv
from dataclasses import dataclass, asdict
from pathlib import Path

from r9_replay import Config, Replay, iter_ticks, sha256

CLOCKS_MS = (250, 500, 1000, 5000, 15000, 30000, 45000)
BINS = 5
FEATURE_KEYS = ('impulse','efficiency','hawkes','vol_regime','rsi','bb_position','twap_position','fib_position','clock_agreement','spread','shock')
TRAIN_END_MS = int(dt.datetime(2026,1,10,tzinfo=dt.timezone.utc).timestamp()*1000)
CAL_END_MS = int(dt.datetime(2026,1,17,tzinfo=dt.timezone.utc).timestamp()*1000)


def clipped(x,lo=-1.0,hi=1.0):
    return min(hi,max(lo,x))

def bin5(x):
    # signed, monotonic, fixed binning; no future-data quantiles.
    return 0 if x<-.6 else 1 if x<-.2 else 2 if x<=.2 else 3 if x<=.6 else 4


class CompletedClock:
    """No fabricated bars. Empty intervals are skipped; freshness is explicit."""
    __slots__=('period','bucket','o','h','l','c','turns','ts','bars','features','dirty')
    def __init__(self,period):
        self.period=period;self.bucket=None
        self.o=self.h=self.l=self.c=0.
        self.turns=0;self.ts=0
        self.bars=collections.deque(maxlen=64);self.features=None;self.dirty=True
    def update(self,ms,mid):
        b=(ms//self.period)*self.period
        if self.bucket is None:
            self.bucket=b;self.o=self.h=self.l=self.c=mid;return
        if b!=self.bucket:
            self.bars.append((self.bucket,self.o,self.h,self.l,self.c))
            self.bucket=b;self.o=self.h=self.l=self.c=mid
            self.ts=ms
            self.dirty=True
        else:
            if mid>self.h:self.h=mid
            if mid<self.l:self.l=mid
            self.c=mid
    def calc(self):
        bars=self.bars
        if len(bars)<34:return None
        seq=list(bars)
        last=seq[-1]
        cls=[x[4] for x in seq]
        highs=[x[2] for x in seq]
        lows=[x[3] for x in seq]
        changes=[cls[i]-cls[i-1] for i in range(1,len(cls))]
        momentum=sum(changes[-4:]);path=sum(abs(d) for d in changes[-4:])+1e-9
        trs=[max(highs[i]-lows[i],abs(highs[i]-cls[i-1]),abs(lows[i]-cls[i-1])) for i in range(1,len(seq))]
        atr=sum(trs[-14:])/14
        atr_earlier=sum(trs[-28:-14])/14+1e-6
        up=sum(max(0,x) for x in changes[-14:]);dn=sum(max(0,-x) for x in changes[-14:])
        rsi=(up-dn)/(up+dn+1e-9)
        mean=sum(cls[-20:])/20
        var=sum((x-mean)**2 for x in cls[-20:])/20
        z=(last[4]-mean)/(2*math.sqrt(var)+1e-6)
        # This is NOT true VWAP: quote prices weighted by bounded observed
        # interarrival durations only. No transactions/volume data are invented.
        weighted=0.;total=0.
        for j in range(-20,-1):
            delta=min(self.period*2, max(1, seq[j+1][0]-seq[j][0]))
            weighted+=cls[j]*delta;total+=delta
        qtwap=weighted/max(1,total)
        lo=min(lows[-34:]);hi=max(highs[-34:]);span=hi-lo+1e-9
        fib=(last[4]-lo)/span*2-1  # causal historical range position, NOT confirmed swing
        return (momentum/(atr+1e-6),abs(momentum)/path,
                atr/atr_earlier-1,rsi,z,(last[4]-qtwap)/(atr+1e-6),fib,
                atr,last[0])


class MultiClockEvidence:
    __slots__=('clocks','prev_mid','prev_ms','hp','hm','tp','tm','last_side','tick_changes','processed','gap_resets')
    def __init__(self):
        self.clocks={k:CompletedClock(k) for k in CLOCKS_MS}
        self.prev_mid=None;self.prev_ms=None
        self.hp=self.hm=self.tp=self.tm=0.
        self.last_side=0
        self.tick_changes=collections.deque(maxlen=96)
        self.processed=0;self.gap_resets=0
    def update(self,t):
        mid=(t.bid+t.ask)*.5;ms=t.native_ms
        if self.prev_ms is not None:
            gap=ms-self.prev_ms
            if gap>15000:
                self.hp=self.hm=self.tp=self.tm=0.
                self.tick_changes.clear()
                # Never carry pre-gap bars into a freshly live microstructure.
                for c in self.clocks.values():
                    c.bucket=None;c.bars.clear();c.features=None;c.dirty=True
                self.gap_resets+=1
            else:
                lag=max(0,gap)/1000
                d_fast=math.exp(-lag/.4);d_slow=math.exp(-lag/2.5)
                self.hp*=d_fast;self.hm*=d_fast;self.tp*=d_slow;self.tm*=d_slow
                change=mid-self.prev_mid
                if change>.005:self.hp+=.65;self.tp+=.18;self.tick_changes.append((ms,change))
                elif change<-.005:self.hm+=.65;self.tm+=.18;self.tick_changes.append((ms,change))
        self.prev_mid=mid;self.prev_ms=ms
        for c in self.clocks.values():c.update(ms,mid)
        self.processed+=1
    def evidence(self,t):
        ms=t.native_ms
        # Every requested clock must contain enough COMPLETED observations,
        # but slow clocks are allowed to be older than one period.
        f=[]
        for k,c in self.clocks.items():
            if c.dirty:
                c.features=c.calc();c.dirty=False
            if c.features is None:return None
            if ms - c.features[8] > 4*k:return None
            f.append((k,c.features))
        # Short clocks determine entry direction. Long clocks are context, not H1 geometry.
        dir_score=sum(v[0] * w for (k,v),w in zip(f,(.9,.8,.7,.4,.25,.15,.1)))
        hawkes_fast=(self.hp-self.hm)/(self.hp+self.hm+1)
        hawkes_slow=(self.tp-self.tm)/(self.tp+self.tm+1)
        direction=1 if dir_score+.75*hawkes_fast>0 else -1
        # A genuine side-independent abstention zone.
        if abs(dir_score+.75*hawkes_fast)<.4:return None
        recent=f[:4];aligned=sum(1 if v[0]*direction>0 else -1 for k,v in f)/7
        spread=(t.ask-t.bid)
        # Candidate must be executable and enough movement exist in fast clocks.
        # Uses latest quote plus completed bars, no M1 threshold or S1 filter.
        if spread>.25+1e-8:return None
        if abs(recent[0][1][0])<.08 and abs(recent[1][1][0])<.08:return None
        # Advanced ATR/RSI/BB, qTWAP and Fibonacci features combine across clocks.
        short=f[:4]
        weighted=lambda i:sum(v[i]*w for (k,v),w in zip(short,(.4,.3,.2,.1)))
        short_atr=max(.01,short[0][1][7]); slow_atr=max(.01,f[-1][1][7])
        impulse=clipped(direction*weighted(0)/2)
        efficiency=clipped((sum(v[1] for k,v in short)/4-.5)*2)
        hawkes=clipped(direction*(hawkes_fast*.7+hawkes_slow*.3)*2)
        vol_regime=clipped(weighted(2)/2)
        rsi=clipped(direction*weighted(3))
        bb_pos=clipped(direction*weighted(4)/2)
        twap=clipped(direction*weighted(5)/2)
        fib=clipped(direction*weighted(6))
        agreement=clipped(direction*aligned)
        spread_b=clipped((.12-spread)/.12)
        shock=clipped((short_atr/slow_atr-1)/3)
        xs=(impulse,efficiency,hawkes,vol_regime,rsi,bb_pos,twap,fib,agreement,spread_b,shock)
        return direction,tuple(bin5(x) for x in xs),xs


class BayesianNP:
    """Fixed-bin shrinkage Naive Bayes likelihood + TWO empirical NP limits.

    NP budget A: reject <= good_reject_budget of observed GOOD in CAL.
    NP budget B: accept <= bad_accept_budget of observed BAD in CAL.
    If constraints conflict the policy ABSTAINS; never reoptimize on scoring set.
    """
    def __init__(self,good_reject_budget=.70,bad_accept_budget=.35):
        self.pseudo=1.5
        self.counts=[[[0]*BINS for _ in FEATURE_KEYS] for _ in (0,1)]
        self.class_count=[0,0]
        self.cal=[];self.threshold=None;self.feasible=False
        self.good_reject_budget=good_reject_budget
        self.bad_accept_budget=bad_accept_budget
        self.train_count=0
        self.calibration_stats={}
    def logit(self,bins):
        c=self.class_count
        prior=math.log((c[1]+2)/(c[0]+2))
        evidence=0.
        for i,b in enumerate(bins):
            p1=(self.counts[1][i][b]+self.pseudo)/(c[1]+BINS*self.pseudo)
            p0=(self.counts[0][i][b]+self.pseudo)/(c[0]+BINS*self.pseudo)
            evidence+=math.log(p1/p0)
        # Temper correlated evidence to avoid naive-Bayes certainty inflation.
        return max(-12.,min(12.,prior+.30*evidence))
    def probability(self,bins):
        score=self.logit(bins)
        return 1/(1+math.exp(-score))
    def learn(self,bins,good):
        y=int(good);self.class_count[y]+=1;self.train_count+=1
        for i,b in enumerate(bins):self.counts[y][i][b]+=1
    def observe_calibration(self,bins,good):
        self.cal.append((self.logit(bins),int(good)))
    def freeze(self):
        good=sorted(score for score,y in self.cal if y)
        bad=sorted(score for score,y in self.cal if not y)
        if not good or not bad:
            self.calibration_stats={'reason':'missing_class','good':len(good),'bad':len(bad)}
            return
        # To accept at most beta of BAD, threshold > upper (1-beta) quantile.
        ix_bad=min(len(bad)-1,max(0,math.ceil((1-self.bad_accept_budget)*len(bad))-1))
        # To reject at most alpha of GOOD, threshold <= alpha quantile.
        ix_good=min(len(good)-1,max(0,math.floor(self.good_reject_budget*len(good))))
        low=bad[ix_bad]+1e-9; high=good[ix_good]
        self.feasible=low<=high
        self.threshold=low if self.feasible else None
        self.calibration_stats={
            'good_cal':len(good),'bad_cal':len(bad),
            'min_threshold_for_bad_budget':low,'max_threshold_for_good_budget':high,
            'feasible':self.feasible,'accepted_bad_fraction':sum(x>=low for x in bad)/len(bad),
            'rejected_good_fraction':sum(x<low for x in good)/len(good),
        }
    def accept(self,bins):
        return self.feasible and self.logit(bins)>=self.threshold
    def export(self):
        return {'feature_keys':FEATURE_KEYS,'clocks_ms':CLOCKS_MS,
                'class_count':self.class_count,'counts':self.counts,
                'good_reject_budget':self.good_reject_budget,
                'bad_accept_budget':self.bad_accept_budget,
                'threshold_log_odds':self.threshold,'feasible':self.feasible,
                'calibration_stats':self.calibration_stats}
    @classmethod
    def load(cls,data):
        p=cls(data['good_reject_budget'],data['bad_accept_budget'])
        p.class_count=data['class_count'];p.counts=data['counts']
        p.threshold=data['threshold_log_odds'];p.feasible=data['feasible']
        p.calibration_stats=data['calibration_stats'];return p


class BayesianEntryReplay(Replay):
    def __init__(self,cfg:Config,policy:BayesianNP,mode:str,cutoff_ms:int):
        super().__init__(cfg)
        self.evidence=MultiClockEvidence();self.policy=policy
        self.mode=mode;self.cutoff_ms=cutoff_ms
        self.sampled=collections.Counter();self.candidates=[]
        self.cal_scores=[];self.last_candidate_ms=-1;self.last_exit_ms=-1
        self.pending_features=None;self.pending_phase=None
        self.end_train_ms=TRAIN_END_MS;self.end_cal_ms=CAL_END_MS
        self.frozen=False;self.candidate_side=0
    def start_cycle(self,s,bid,ask):
        self.cycle_min=s-s%60 # state only; no M1 bracket allowed for entry
    def gate(self,t,s):return True # all entry conditions replaced by new causal policy
    def quality(self,side):return True
    def close(self,t,s,why,exit_price):
        prior=self.position
        super().close(t,s,why,exit_price)
        self.last_exit_ms=t.native_ms
        good=self.closed[-1]['net']>0
        if self.pending_features is not None:
            bins=self.pending_features
            if self.pending_phase=='train':self.policy.learn(bins,good)
            elif self.pending_phase=='calibration':self.policy.observe_calibration(bins,good)
        self.pending_features=None;self.pending_phase=None
    def on_tick(self,t):
        self.evidence.update(t)
        phase='train' if t.utc_ms<self.end_train_ms else 'calibration' if t.utc_ms<self.end_cal_ms else 'eval'
        if self.mode=='transfer':phase='eval'
        if phase=='eval' and not self.frozen:
            if self.mode!='transfer':self.policy.freeze()
            self.frozen=True
        # Keep the original R9 position hold, trail, broker-stop and timeout code.
        if self.position is not None or self.had_position:
            super().on_tick(t);return
        self.pending_mode=0
        ms=t.native_ms
        # evaluate at a maximum of two times per wall-clock second, but only on real ticks.
        if (ms//500)==(self.last_candidate_ms//500) or ms-self.last_exit_ms<1000:
            super().on_tick(t);return
        self.last_candidate_ms=ms
        opportunity=self.evidence.evidence(t)
        if opportunity is None:
            self.sampled['no_candidate']+=1;super().on_tick(t);return
        side,bins,raw=opportunity
        self.sampled['candidates_'+phase]+=1
        score=self.policy.probability(bins)
        if phase=='eval' and not self.policy.accept(bins):
            self.sampled['rejected_np']+=1
            super().on_tick(t);return
        self.pending_mode=side
        self.cycle_buy=t.ask;self.cycle_sell=t.bid
        self.pending_features=bins;self.pending_phase=phase
        self.candidates.append({'utc_ms':t.utc_ms,'native_ms':ms,'phase':phase,'side':side,
                                'probability':round(score,8),'log_odds':round(self.policy.logit(bins),6),
                                'features':list(bins)})
        super().on_tick(t)
        if self.position is None:
            self.pending_features=None;self.pending_phase=None
    def result(self,source,path):
        byphase=collections.defaultdict(lambda:collections.Counter())
        for tr in self.closed:
            # each trade's phase determined by entry UTC timestamp
            x=tr['entry_time_utc_ms'];p='train' if x<TRAIN_END_MS else 'calibration' if x<CAL_END_MS else 'eval'
            if self.mode=='transfer':p='eval'
            byphase[p]['trades']+=1
            byphase[p]['wins']+=int(tr['net']>0)
            byphase[p]['net_cents']+=round(tr['net']*100)
        return {'source':source,'file':Path(path).name,'source_sha256':sha256(path),
                'model':'BNP-Hawkes-subminute-v0.1-research-only',
                'mode':self.mode,'clocks_ms':['tick',*CLOCKS_MS],
                'ticker_count':self.evidence.processed,'quote_gap_resets':self.evidence.gap_resets,
                'samples':dict(self.sampled),'trades_by_phase':{
                    p:{'trades':s['trades'],'wins':s['wins'],'win_rate':round(s['wins']/max(1,s['trades']),5),
                       'net_usd':round(s['net_cents']/100,2)} for p,s in byphase.items()},
                'total_net':round(self.balance-self.cfg.initial_balance,2),
                'policy':self.policy.export(),
                'limitations':['inherited R9 Python stop fill approximation','fixed 0.01 lot and $100k capital',
                    'no true transaction volume VWAP','no certified probability calibration',
                    'no live MQL5 execution or compile verification']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ticks',required=True);ap.add_argument('--source',required=True,choices=('coinexx','dukascopy'))
    ap.add_argument('--out',required=True);ap.add_argument('--model',help='frozen model JSON for transfer replay')
    ap.add_argument('--limit',type=int)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    policy=BayesianNP.load(json.loads(Path(args.model).read_text())) if args.model else BayesianNP()
    mode='transfer' if args.model else 'walk_forward'
    replay=BayesianEntryReplay(Config(),policy,mode,CAL_END_MS)
    for i,t in enumerate(iter_ticks(args.ticks,args.source,args.limit)):
        replay.on_tick(t)
    result=replay.result(args.source,args.ticks)
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    (out/'frozen_policy.json').write_text(json.dumps(policy.export(),indent=2))
    for name,data in [('trades.csv',replay.closed),('entry_decisions.csv',replay.candidates)]:
        if data:
            with (out/name).open('w',newline='') as f:
                wr=csv.DictWriter(f,fieldnames=list(data[0]));wr.writeheader();wr.writerows(data)
    print(json.dumps({k:v for k,v in result.items() if k not in ('policy','limitations')},indent=2))
if __name__=='__main__':main()