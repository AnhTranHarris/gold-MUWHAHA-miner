#!/usr/bin/env python3
"""Causal multiscale feature engine for R9 Probabilistic Entry Router v2.

Design contract:
- Runtime features use only quotes observed at or before the decision timestamp.
- time_msc / millisecond chronology is the base event clock.
- Subminute execution state comes from completed 250 ms buckets plus current tick event state.
- 5 minute rolling state is the local market brain.
- 15m / 1h / 4h geometry is context/prior information only, never a hard entry trigger.
- Quote-weighted/time-weighted anchors are NOT called centralized VWAP.
- No SYNTH teacher field is present in runtime features.
"""
from __future__ import annotations

import collections
import datetime as dt
import math
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo=None
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Optional, Tuple

VERSION = "r9_probabilistic_entry_router_v2_20261101"
BASE_BUCKET_MS = 250
LOCAL_HORIZONS_MS = (250, 500, 1000, 5000, 15000, 30000, 45000, 60000, 300000)
HAWKES_TAUS_MS = (250, 500, 1000, 5000, 15000, 45000, 240000)
EVENT_NAMES = ("BU", "BD", "AU", "AD", "SW", "SN")
MARKET_STATES = (
    "compression", "ignition", "continuation", "pullback", "exhaustion",
    "reversal", "volatility_shock", "chop", "spread_toxicity", "quote_drought",
)
SESSIONS = ("sydney", "tokyo", "london", "overlap", "new_york", "rollover", "off")


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return min(hi, max(lo, x))


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-min(60.0, x))
        return 1.0 / (1.0 + z)
    z = math.exp(min(60.0, x))
    return z / (1.0 + z)


def softmax(d: Dict[str, float]) -> Dict[str, float]:
    if not d:
        return {}
    m = max(d.values())
    ex = {k: math.exp(min(60.0, v - m)) for k, v in d.items()}
    s = sum(ex.values()) or 1.0
    return {k: v / s for k, v in ex.items()}


@dataclass(frozen=True)
class Quote:
    utc_ms: int
    bid: float
    ask: float
    native_ms: Optional[int] = None
    flags: int = 0
    last: float = 0.0
    volume: float = 0.0
    volume_real: float = 0.0

    @property
    def mid(self) -> float:
        return 0.5 * (self.bid + self.ask)

    @property
    def spread(self) -> float:
        return self.ask - self.bid


@dataclass
class Bucket:
    start_ms: int
    end_ms: int
    open: float
    high: float
    low: float
    close: float
    bid_open: float
    bid_close: float
    ask_open: float
    ask_close: float
    spread_sum: float
    spread_min: float
    spread_max: float
    ticks: int
    quote_mid_sum: float

    @property
    def spread_mean(self) -> float:
        return self.spread_sum / max(1, self.ticks)

    @property
    def quote_weighted_mid(self) -> float:
        return self.quote_mid_sum / max(1, self.ticks)


class CompletedBucketStore:
    """Completed fixed-width buckets only; missing intervals are never synthesized."""
    def __init__(self, width_ms: int = BASE_BUCKET_MS, keep_ms: int = 4 * 3600_000 + 15 * 60_000):
        self.width_ms = width_ms
        self.keep_ms = keep_ms
        self.completed: Deque[Bucket] = collections.deque()
        self.cur: Optional[Bucket] = None

    def reset(self) -> None:
        self.completed.clear()
        self.cur = None

    def add(self, q: Quote) -> None:
        start = (q.utc_ms // self.width_ms) * self.width_ms
        if self.cur is None:
            self.cur = Bucket(start, start + self.width_ms, q.mid, q.mid, q.mid, q.mid,
                              q.bid, q.bid, q.ask, q.ask, q.spread, q.spread, q.spread, 1, q.mid)
            return
        if start < self.cur.start_ms:
            raise ValueError("non-monotone quote stream")
        if start != self.cur.start_ms:
            self.completed.append(self.cur)
            self.cur = Bucket(start, start + self.width_ms, q.mid, q.mid, q.mid, q.mid,
                              q.bid, q.bid, q.ask, q.ask, q.spread, q.spread, q.spread, 1, q.mid)
            cutoff = start - self.keep_ms
            while self.completed and self.completed[0].end_ms < cutoff:
                self.completed.popleft()
            return
        b = self.cur
        b.high = max(b.high, q.mid)
        b.low = min(b.low, q.mid)
        b.close = q.mid
        b.bid_close = q.bid
        b.ask_close = q.ask
        b.spread_sum += q.spread
        b.spread_min = min(b.spread_min, q.spread)
        b.spread_max = max(b.spread_max, q.spread)
        b.ticks += 1
        b.quote_mid_sum += q.mid

    def window(self, now_ms: int, horizon_ms: int) -> List[Bucket]:
        cutoff = now_ms - horizon_ms
        out=[]
        for b in reversed(self.completed):
            if b.end_ms > now_ms:
                continue
            if b.end_ms <= cutoff:
                break
            out.append(b)
        out.reverse()
        return out


class MinuteStore:
    """Completed one-minute bars retained for causal 15m/1h/4h context."""
    def __init__(self, keep_minutes: int = 360):
        self.keep_minutes = keep_minutes
        self.completed: Deque[Bucket] = collections.deque(maxlen=keep_minutes)
        self.cur: Optional[Bucket] = None

    def reset(self) -> None:
        self.completed.clear(); self.cur = None

    def add(self, q: Quote) -> None:
        width = 60_000
        start = (q.utc_ms // width) * width
        if self.cur is None:
            self.cur = Bucket(start, start+width, q.mid, q.mid, q.mid, q.mid,
                              q.bid,q.bid,q.ask,q.ask,q.spread,q.spread,q.spread,1,q.mid)
            return
        if start < self.cur.start_ms:
            raise ValueError("non-monotone minute stream")
        if start != self.cur.start_ms:
            self.completed.append(self.cur)
            self.cur = Bucket(start, start+width, q.mid, q.mid, q.mid, q.mid,
                              q.bid,q.bid,q.ask,q.ask,q.spread,q.spread,q.spread,1,q.mid)
            return
        b=self.cur
        b.high=max(b.high,q.mid);b.low=min(b.low,q.mid);b.close=q.mid
        b.bid_close=q.bid;b.ask_close=q.ask;b.spread_sum+=q.spread
        b.spread_min=min(b.spread_min,q.spread);b.spread_max=max(b.spread_max,q.spread)
        b.ticks+=1;b.quote_mid_sum+=q.mid

    def last(self, n: int) -> List[Bucket]:
        if n <= 0: return []
        return list(self.completed)[-n:]


class MarkedHawkesBank:
    """Marked multivariate exponentially decayed quote-event intensity bank.

    This is a causal state machine, not a fitted Hawkes model yet. Each decay bank
    retains event excitation for BU/BD/AU/AD/SW/SN. Parameters are intentionally
    explicit and can later be fitted on development data without changing runtime API.
    """
    def __init__(self, taus_ms: Iterable[int] = HAWKES_TAUS_MS, baseline: float = 0.25):
        self.taus_ms = tuple(int(x) for x in taus_ms)
        self.baseline = float(baseline)
        self.values = {tau: {e: 0.0 for e in EVENT_NAMES} for tau in self.taus_ms}
        self.cross_values = {tau: collections.defaultdict(float) for tau in self.taus_ms}
        self.last_q: Optional[Quote] = None
        self.last_ms: Optional[int] = None
        self.last_event: Optional[str] = None
        self.last_event_ms: Optional[int] = None
        self.cross_follow = collections.Counter()

    def reset(self) -> None:
        for d in self.values.values():
            for e in EVENT_NAMES: d[e] = 0.0
        for d in self.cross_values.values(): d.clear()
        self.last_q = None; self.last_ms = None; self.last_event = None; self.last_event_ms = None
        self.cross_follow.clear()

    @staticmethod
    def classify(prev: Quote, q: Quote, eps: float = 1e-12) -> List[str]:
        events: List[str] = []
        db=q.bid-prev.bid; da=q.ask-prev.ask; ds=q.spread-prev.spread
        if db > eps: events.append("BU")
        elif db < -eps: events.append("BD")
        if da > eps: events.append("AU")
        elif da < -eps: events.append("AD")
        if ds > eps: events.append("SW")
        elif ds < -eps: events.append("SN")
        return events

    def add(self, q: Quote) -> List[str]:
        if self.last_ms is not None and q.utc_ms < self.last_ms:
            raise ValueError("out-of-order Hawkes quote")
        if self.last_ms is not None:
            elapsed = q.utc_ms - self.last_ms
            for tau, d in self.values.items():
                decay = math.exp(-elapsed / max(1.0, tau))
                for e in EVENT_NAMES: d[e] *= decay
                for pair in list(self.cross_values[tau]): self.cross_values[tau][pair] *= decay
        events: List[str] = []
        if self.last_q is not None:
            events = self.classify(self.last_q, q)
            for e in events:
                for tau in self.taus_ms: self.values[tau][e] += 1.0
            # causal cross-follow diagnostic within one second
            if self.last_event and events and self.last_event_ms is not None and q.utc_ms-self.last_event_ms <= 1000:
                for e in events:
                    self.cross_follow[(self.last_event,e)] += 1
                    for tau in self.taus_ms:self.cross_values[tau][(self.last_event,e)] += 1.0
            if events:
                self.last_event=events[-1];self.last_event_ms=q.utc_ms
        self.last_q=q;self.last_ms=q.utc_ms
        return events

    def features(self) -> Dict[str,float]:
        out: Dict[str,float] = {}
        for tau,d in self.values.items():
            bu=d['BU']+self.baseline;bd=d['BD']+self.baseline
            au=d['AU']+self.baseline;ad=d['AD']+self.baseline
            sw=d['SW']+self.baseline;sn=d['SN']+self.baseline
            up=bu+au;down=bd+ad
            out[f'hawk_dir_{tau}']=clamp((up-down)/(up+down+1e-12))
            out[f'hawk_bid_{tau}']=clamp((bu-bd)/(bu+bd+1e-12))
            out[f'hawk_ask_{tau}']=clamp((au-ad)/(au+ad+1e-12))
            out[f'hawk_spread_{tau}']=clamp((sn-sw)/(sn+sw+1e-12))
            out[f'hawk_burst_{tau}']=math.log1p(max(0.0, up+down+sw+sn-6*self.baseline))
            cv=self.cross_values[tau]
            up_follow=cv.get(('BU','AU'),0.)+cv.get(('AU','BU'),0.)
            down_follow=cv.get(('BD','AD'),0.)+cv.get(('AD','BD'),0.)
            total_follow=up_follow+down_follow
            out[f'hawk_cross_dir_{tau}']=clamp((up_follow-down_follow)/(total_follow+1e-9)) if total_follow else 0.0
            supportive=sum(cv.get((a,'SN'),0.) for a in ('BU','AU','BD','AD'))
            toxic=sum(cv.get((a,'SW'),0.) for a in ('BU','AU','BD','AD'))
            out[f'hawk_cross_spread_{tau}']=clamp((supportive-toxic)/(supportive+toxic+1e-9)) if supportive+toxic else 0.0
        return out


class CausalImpulseTracker:
    """Causal impulse anchor: starts only after observed displacement+efficiency.

    No future swing high/low is used. Once started, extreme updates only when observed.
    Retracement is measured from the observed extreme back toward the frozen start.
    """
    def __init__(self):
        self.side=0;self.start=0.0;self.extreme=0.0;self.start_ms=0;self.last_ms=0

    def reset(self) -> None:
        self.side=0;self.start=self.extreme=0.0;self.start_ms=self.last_ms=0

    def update(self, now_ms:int, mid:float, displacement:float, efficiency:float, scale:float) -> None:
        scale=max(scale,1e-8)
        if self.side==0:
            z=displacement/scale
            if abs(z)>=1.25 and efficiency>=0.65:
                self.side=1 if z>0 else -1
                self.start=mid-displacement
                self.extreme=mid
                self.start_ms=now_ms;self.last_ms=now_ms
            return
        self.last_ms=now_ms
        if self.side>0:self.extreme=max(self.extreme,mid)
        else:self.extreme=min(self.extreme,mid)
        total=(self.extreme-self.start)*self.side
        retr=(self.extreme-mid)*self.side
        if total<=1e-8:return
        if retr/total>0.80 or now_ms-self.start_ms>300_000:
            self.reset()

    def features(self, mid:float, now_ms:int) -> Dict[str,float]:
        if self.side==0:return {'impulse_side':0.0,'fib_retracement':0.0,'impulse_age':0.0,'impulse_extension':0.0}
        total=max(1e-9,(self.extreme-self.start)*self.side)
        retr=max(0.0,(self.extreme-mid)*self.side)/total
        age=min(1.0,(now_ms-self.start_ms)/300_000)
        return {'impulse_side':float(self.side),'fib_retracement':clamp(retr,0.0,1.5),
                'impulse_age':age,'impulse_extension':total}


def _window_stats(bars: List[Bucket], horizon_ms: int) -> Optional[Dict[str,float]]:
    if len(bars)<1:return None
    first,last=bars[0],bars[-1]
    closes=[b.close for b in bars]
    diffs=[closes[i]-closes[i-1] for i in range(1,len(closes))]
    disp=last.close-first.open
    if not diffs and last.close!=first.open: diffs=[last.close-first.open]
    path=sum(abs(x) for x in diffs)
    eff=abs(disp)/(path+1e-12)
    hi=max(b.high for b in bars);lo=min(b.low for b in bars);rng=hi-lo
    rv=math.sqrt(sum(x*x for x in diffs)/max(1,len(diffs)))
    tr=[]
    prev=first.open
    for b in bars:
        tr.append(max(b.high-b.low,abs(b.high-prev),abs(b.low-prev)));prev=b.close
    atr=sum(tr)/len(tr)
    up=sum(max(0.0,x) for x in diffs);down=sum(max(0.0,-x) for x in diffs)
    rsi=(up-down)/(up+down+1e-12)
    mean=sum(closes)/len(closes)
    sd=math.sqrt(sum((x-mean)**2 for x in closes)/len(closes))
    boll=(last.close-mean)/(2*sd+1e-12)
    qw=sum(b.quote_weighted_mid*b.ticks for b in bars)/max(1,sum(b.ticks for b in bars))
    # fixed-time bucket average approximates quote-time weighted anchor without trade-volume claim
    tw=sum(b.close for b in bars)/len(bars)
    lw=0.5*(qw+tw)
    spread_mean=sum(b.spread_sum for b in bars)/max(1,sum(b.ticks for b in bars))
    spread_max=max(b.spread_max for b in bars)
    tick_rate=sum(b.ticks for b in bars)/(horizon_ms/1000)
    signs=[1 if x>0 else -1 if x<0 else 0 for x in diffs]
    nonzero=[s for s in signs if s]
    turns=sum(nonzero[i]!=nonzero[i-1] for i in range(1,len(nonzero)))
    entropy=0.0
    if nonzero:
        p=sum(s>0 for s in nonzero)/len(nonzero)
        if 0<p<1:entropy=-(p*math.log(p)+(1-p)*math.log(1-p))/math.log(2)
    coverage=(last.end_ms-first.start_ms)/max(1,horizon_ms)
    return {'disp':disp,'range':rng,'rv':rv,'atr':atr,'eff':eff,'rsi':rsi,'boll':boll,
            'lw_anchor':lw,'anchor_dist':last.close-lw,'spread_mean':spread_mean,'spread_max':spread_max,
            'tick_rate':tick_rate,'turn_rate':turns/max(1,len(nonzero)-1),'entropy':entropy,
            'coverage':coverage,'last_close':last.close,'bb_width':4*sd}


def _geometry(bars: List[Bucket]) -> Dict[str,float]:
    if len(bars)<3:return {'trend':0.0,'range_pos':0.0,'eff':0.0,'vol':0.0,'extension':0.0}
    closes=[b.close for b in bars];hi=max(b.high for b in bars);lo=min(b.low for b in bars)
    diffs=[closes[i]-closes[i-1] for i in range(1,len(closes))]
    path=sum(abs(x) for x in diffs);disp=closes[-1]-closes[0]
    vol=math.sqrt(sum(x*x for x in diffs)/len(diffs))
    trend=disp/(path+1e-12)
    rp=2*(closes[-1]-lo)/(hi-lo+1e-12)-1
    mean=sum(closes)/len(closes);sd=math.sqrt(sum((x-mean)**2 for x in closes)/len(closes))
    ext=(closes[-1]-mean)/(2*sd+1e-12)
    return {'trend':clamp(trend),'range_pos':clamp(rp),'eff':clamp(abs(trend),0,1),'vol':vol,'extension':clamp(ext)}


def session_utc(ms:int)->str:
    utc=dt.datetime.fromtimestamp(ms/1000,dt.timezone.utc)
    def local(zone,fixed_hours):
        if ZoneInfo is not None:
            try:return utc.astimezone(ZoneInfo(zone))
            except Exception:pass
        return utc+dt.timedelta(hours=fixed_hours)
    sy=local('Australia/Sydney',10);tk=local('Asia/Tokyo',9);lo=local('Europe/London',0);ny=local('America/New_York',-5)
    def mins(x):return x.hour*60+x.minute
    sm,tm,lm,nm=map(mins,(sy,tk,lo,ny))
    sydney=8*60<=sm<17*60
    tokyo=8*60<=tm<17*60
    london=8*60<=lm<16*60+30
    newyork=8*60<=nm<17*60
    rollover=16*60+55<=nm<17*60+15
    if rollover:return 'rollover'
    if london and newyork:return 'overlap'
    if london:return 'london'
    if newyork:return 'new_york'
    if tokyo:return 'tokyo'
    if sydney:return 'sydney'
    return 'off'


class RouterV2FeatureEngine:
    def __init__(self, gap_reset_ms:int=15_000):
        self.gap_reset_ms=gap_reset_ms
        self.buckets=CompletedBucketStore()
        self.minutes=MinuteStore()
        self.hawkes=MarkedHawkesBank()
        self.impulse=CausalImpulseTracker()
        self.last_q:Optional[Quote]=None
        self.last_ms:Optional[int]=None
        self.gap_resets=0
        self.ticks=0
        self.last_events:List[str]=[]

    def reset_local(self)->None:
        self.buckets.reset();self.hawkes.reset();self.impulse.reset();self.last_q=None;self.last_events=[]

    def add(self,q:Quote)->None:
        if not (q.bid>0 and q.ask>=q.bid):raise ValueError('invalid quote')
        if self.last_ms is not None and q.utc_ms<self.last_ms:raise ValueError('non-monotone quote')
        if self.last_ms is not None and q.utc_ms-self.last_ms>self.gap_reset_ms:
            # preserve long-horizon minute context, reset microstructure state after quote drought.
            self.buckets.reset();self.hawkes.reset();self.impulse.reset();self.gap_resets+=1
        self.last_events=self.hawkes.add(q)
        self.buckets.add(q);self.minutes.add(q)
        self.last_q=q;self.last_ms=q.utc_ms;self.ticks+=1
        bars=self.buckets.window(q.utc_ms,5_000)
        s=_window_stats(bars,5_000)
        if s:self.impulse.update(q.utc_ms,q.mid,s['disp'],s['eff'],max(s['atr'],.01))

    def ready(self,now_ms:int)->bool:
        w=self.buckets.window(now_ms,300_000)
        # Require a complete rolling 5-minute local brain plus 15m completed context.
        return bool(w and now_ms-w[0].start_ms>=299_000 and len(self.minutes.completed)>=15)

    def snapshot(self,q:Quote)->Optional[Dict[str,float]]:
        if not self.ready(q.utc_ms):return None
        f:Dict[str,float]={}
        states={}
        for h in LOCAL_HORIZONS_MS:
            s=_window_stats(self.buckets.window(q.utc_ms,h),h)
            if s is None:continue
            states[h]=s
            tag={250:'250ms',500:'500ms',1000:'1s',5000:'5s',15000:'15s',30000:'30s',45000:'45s',60000:'1m',300000:'5m'}[h]
            # normalized/signed features; raw ATR/range/spread retained too.
            norm=max(s['atr'],0.01)
            f[f'disp_{tag}']=s['disp']/norm
            f[f'eff_{tag}']=s['eff']
            f[f'rsi_{tag}']=s['rsi']
            f[f'boll_{tag}']=clamp(s['boll'],-3,3)/3
            f[f'anchor_{tag}']=s['anchor_dist']/norm
            f[f'atr_{tag}']=s['atr']
            f[f'rv_{tag}']=s['rv']
            f[f'bb_width_{tag}']=s['bb_width']
            f[f'tick_rate_{tag}']=math.log1p(s['tick_rate'])
            f[f'entropy_{tag}']=s['entropy']
            f[f'turn_{tag}']=s['turn_rate']
            f[f'spread_mean_{tag}']=s['spread_mean']
        # volatility surface ratios
        def ratio(a,b,key='atr'):
            if a in states and b in states:return math.log((states[a][key]+1e-8)/(states[b][key]+1e-8))
            return 0.0
        f['vol_ratio_5s_5m']=ratio(5000,300000)
        f['vol_ratio_45s_5m']=ratio(45000,300000)
        f['vol_ratio_1s_45s']=ratio(1000,45000)
        f['bb_ratio_5s_5m']=ratio(5000,300000,'bb_width')
        f.update(self.hawkes.features())
        f.update(self.impulse.features(q.mid,q.utc_ms))
        # current executable quote/event state
        f['raw_spread']=q.spread
        f['volume_real_valid']=1.0 if q.volume_real>0 or q.last>0 else 0.0
        f['raw_volume_real']=math.log1p(max(0.0,q.volume_real)) if q.volume_real>0 else 0.0
        f['raw_tick_volume']=math.log1p(max(0.0,q.volume)) if q.volume>0 else 0.0
        f['spread_vs_5m']=q.spread/(states.get(300000,{'spread_mean':max(q.spread,1e-8)})['spread_mean']+1e-8)
        f['event_bid_up']=float('BU' in self.last_events);f['event_bid_down']=float('BD' in self.last_events)
        f['event_ask_up']=float('AU' in self.last_events);f['event_ask_down']=float('AD' in self.last_events)
        f['event_spread_widen']=float('SW' in self.last_events);f['event_spread_narrow']=float('SN' in self.last_events)
        # completed-minute geometry; no current unfinished minute included.
        for n,tag in ((15,'15m'),(60,'1h'),(240,'4h')):
            ready=len(self.minutes.completed)>=n
            g=_geometry(self.minutes.last(n)) if ready else {'trend':0.,'range_pos':0.,'eff':0.,'vol':0.,'extension':0.}
            f[f'geo_{tag}_ready']=1.0 if ready else 0.0
            for k,v in g.items():f[f'geo_{tag}_{k}']=v
        sess=session_utc(q.utc_ms)
        for s in SESSIONS:f[f'session_{s}']=1.0 if s==sess else 0.0
        # latent state probabilities, deterministic causal initialization for model context.
        s5=states.get(5000,{});s45=states.get(45000,{});s5m=states.get(300000,{})
        h5=f.get('hawk_burst_5000',0.0);hdir=f.get('hawk_dir_5000',0.0);hsp=f.get('hawk_spread_5000',0.0)
        vol5=f.get('vol_ratio_5s_5m',0.0);eff5=s5.get('eff',0.0);eff45=s45.get('eff',0.0)
        ext5m=abs(f.get('geo_15m_extension',0.0));short=f.get('disp_5s',0.0);medium=f.get('disp_45s',0.0)
        spr=f['spread_vs_5m'];entropy=s45.get('entropy',0.0)
        logits={
            'compression': -1.2*vol5-0.8*h5+0.8*(1-eff45),
            'ignition': 1.5*vol5+0.8*h5+0.5*abs(hdir),
            'continuation': 0.9*eff5+0.7*eff45+0.8*(1 if short*medium>0 else -0.5)+0.5*abs(hdir),
            'pullback': 0.9*(1 if short*medium<0 else -0.3)+0.5*eff45+0.4*(1-abs(short)),
            'exhaustion': 0.9*abs(short)+0.7*ext5m-0.8*h5+0.4*entropy,
            'reversal': 0.8*(1 if short*medium<0 else -0.2)+0.7*abs(hdir)+0.4*eff5,
            'volatility_shock': 1.4*max(0.0,vol5)+0.8*max(0.0,spr-1.0)+0.8*max(0.0,-hsp),
            'chop': 1.1*entropy+0.8*(1-eff5)+0.5*(1-eff45),
            'spread_toxicity': 1.8*max(0.0,spr-1.0)+1.0*max(0.0,-hsp),
            'quote_drought': -1.0*h5-0.4*math.log1p(s5.get('tick_rate',0.0)),
        }
        probs=softmax(logits)
        for k,v in probs.items():f[f'state_{k}']=v
        f['session_code']=float(SESSIONS.index(sess))
        return f

    def oriented(self, features:Dict[str,float], side:int)->Dict[str,float]:
        """Return side-relative feature view; invariants remain unchanged."""
        if side not in (-1,1):raise ValueError('side must be -1/+1')
        out=dict(features)
        directional_prefixes=('disp_','rsi_','boll_','anchor_','hawk_dir_','hawk_bid_','hawk_ask_','geo_15m_trend','geo_1h_trend','geo_4h_trend',
                              'geo_15m_range_pos','geo_1h_range_pos','geo_4h_range_pos','geo_15m_extension','geo_1h_extension','geo_4h_extension')
        for k in list(out):
            if any(k.startswith(p) for p in directional_prefixes):out[k]=out[k]*side
        out['side']=float(side)
        return out


__all__=['VERSION','Quote','RouterV2FeatureEngine','MarkedHawkesBank','CausalImpulseTracker','session_utc',
         'MARKET_STATES','SESSIONS','LOCAL_HORIZONS_MS','EVENT_NAMES']
