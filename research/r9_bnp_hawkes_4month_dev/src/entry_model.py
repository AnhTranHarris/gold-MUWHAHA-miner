#!/usr/bin/env python3
"""R9 BNP-Hawkes causal *entry* candidate, v1.0. No automatic trade authorization.

Only observed quotes and completed bucket bars can contribute. Frozen offline model is
required to issue ENTER; default status is SHADOW_ONLY (abstains). Every input quote
retains its original order, including equal millisecond timestamps.
"""
from __future__ import annotations
import collections
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

CLOCK_MS = (250, 500, 1000, 5000, 15000, 30000, 45000)
FEATURES = ("impulse", "efficiency", "hawkes_direction", "hawkes_pressure", "atr_acceleration",
            "rsi", "bollinger", "qwap_dislocation", "fib_location", "clock_agreement", "spread_score")
BIN_EDGES = (-0.6, -0.2, 0.2, 0.6)
GAP_RESET_MS = 15000
VERSION = "r9_bnp_hawkes_entry_v1_20261101"


def clamp(x: float, low: float = -1., high: float = 1.) -> float:
    return min(high, max(low, x))


def bins5(values):
    return tuple(sum(x > edge for edge in BIN_EDGES) for x in values)


@dataclass(frozen=True)
class Quote:
    time_ms: int
    bid: float
    ask: float
    native_ms: int | None = None


class Clock:
    """Fixed-time buckets of observed ticks, never interpolating missing intervals."""
    __slots__ = ("width", "bucket", "o", "h", "l", "c", "n", "bars", "cached", "dirty")
    def __init__(self, width: int):
        self.width = width
        self.reset()

    def reset(self):
        self.bucket = None
        self.o = self.h = self.l = self.c = 0.
        self.n = 0
        self.bars = collections.deque(maxlen=64)
        self.cached = None
        self.dirty = True

    def add(self, ms: int, mid: float):
        bucket = ms // self.width * self.width
        if self.bucket is None:
            self.bucket = bucket
            self.o = self.h = self.l = self.c = mid
            self.n = 1
        elif bucket != self.bucket:
            if bucket < self.bucket:
                raise ValueError("non-monotone clock")
            self.bars.append((self.bucket, self.o, self.h, self.l, self.c, self.n))
            self.bucket = bucket
            self.o = self.h = self.l = self.c = mid
            self.n = 1
            self.cached = None
            self.dirty = True
        else:
            self.h = max(self.h, mid)
            self.l = min(self.l, mid)
            self.c = mid
            self.n += 1

    def summary(self, now_ms: int):
        if self.cached is not None and not self.dirty:
            return self.cached
        seq = list(self.bars)
        if len(seq) < 34 or now_ms - (seq[-1][0] + self.width) > 3 * self.width:
            return None
        closes = [b[4] for b in seq]
        highs = [b[2] for b in seq]
        lows = [b[3] for b in seq]
        diffs = [closes[i] - closes[i-1] for i in range(1, len(seq))]
        trs = [max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
               for i in range(1, len(seq))]
        atr = sum(trs[-14:]) / 14 + 1e-8
        atr_old = sum(trs[-28:-14]) / 14 + 1e-8
        impulse = sum(diffs[-4:]) / atr
        efficiency = abs(sum(diffs[-4:])) / (sum(abs(x) for x in diffs[-4:]) + 1e-9)
        up = sum(max(0, x) for x in diffs[-14:])
        down = sum(max(0, -x) for x in diffs[-14:])
        rsi = (up - down) / (up + down + 1e-9)  # signed RSI, -1..1
        mean = sum(closes[-20:]) / 20
        sd = math.sqrt(sum((x-mean)**2 for x in closes[-20:]) / 20)
        boll = (closes[-1] - mean) / (2 * sd + 1e-8)
        # Quote-Update Weighted Average Price (QWAP), not actual volume VWAP.
        qcount = sum(x[5] for x in seq[-20:])
        qwap = sum(x[4]*x[5] for x in seq[-20:]) / max(1, qcount)
        qwap_disp = (closes[-1] - qwap) / atr
        lo = min(lows[-34:]); hi = max(highs[-34:])
        fib = 2 * (closes[-1] - lo) / (hi - lo + 1e-9) - 1
        self.cached = (impulse, efficiency, atr/atr_old - 1, rsi, boll, qwap_disp, fib, atr)
        self.dirty = False
        return self.cached


class Hawkes2:
    """Bivariate exponential-kernel *candidate* Hawkes intensity, not fitted params.

    lambda = baseline + A @ exp(-beta * age) event history.
    A/beta spectral radius < 1; event sign derived solely from observed quote movement.
    """
    __slots__ = ("last_ms", "last_mid", "exc_up", "exc_down")
    baseline = 0.5
    beta = 4.0                 # per-second exponential decay
    alpha_same = 0.7           # self-excitation
    alpha_cross = 0.2          # cross-excitation
    event_min_move = 0.005     # price units

    def __init__(self):
        self.reset()

    def reset(self):
        self.last_ms = None
        self.last_mid = None
        self.exc_up = self.exc_down = 0.

    def add(self, ms: int, mid: float):
        if self.last_ms is None:
            self.last_ms = ms
            self.last_mid = mid
            return False
        elapsed = (ms-self.last_ms)/1000
        if elapsed < 0:
            raise ValueError("out-of-order tick")
        if elapsed * 1000 > GAP_RESET_MS:
            self.reset()
            self.last_ms = ms
            self.last_mid = mid
            return True
        decay = math.exp(-self.beta*elapsed)
        self.exc_up *= decay
        self.exc_down *= decay
        signed_move = mid - self.last_mid
        if signed_move > self.event_min_move:
            self.exc_up += self.alpha_same
            self.exc_down += self.alpha_cross
        elif signed_move < -self.event_min_move:
            self.exc_down += self.alpha_same
            self.exc_up += self.alpha_cross
        self.last_ms = ms
        self.last_mid = mid
        return False

    def pressure(self):
        up = self.baseline+self.exc_up
        down = self.baseline+self.exc_down
        return (up-down)/(up+down), (up+down-2*self.baseline)/(up+down)


class CausalEntryFeatures:
    """Tick + complete 250/500ms,1/5/15/30/45s horizons. No M1 geometric bracket."""
    def __init__(self):
        self.clocks = [Clock(w) for w in CLOCK_MS]
        self.hawkes = Hawkes2()
        self.last_ms = None
        self.ticks = 0
        self.gap_resets = 0

    def add(self, quote: Quote):
        if quote.ask < quote.bid or quote.bid <= 0:
            raise ValueError("invalid bid/ask")
        if self.last_ms is not None and quote.time_ms < self.last_ms:
            raise ValueError("nonmonotone input quotes")
        midpoint = (quote.bid+quote.ask)*0.5
        reset = self.hawkes.add(quote.time_ms, midpoint)
        if reset:
            for c in self.clocks:
                c.reset()
            self.gap_resets += 1
        for c in self.clocks:
            c.add(quote.time_ms, midpoint)
        self.last_ms = quote.time_ms
        self.ticks += 1

    def candidate(self, quote: Quote, max_spread: float = .25):
        spread = quote.ask-quote.bid
        if spread < 0 or spread > max_spread+1e-9:
            return None
        entries = [c.summary(quote.time_ms) for c in self.clocks]
        if any(x is None for x in entries):
            return None
        pressure, burst = self.hawkes.pressure()
        # Direction inferred from shortest completed windows + observed quote-event pressure.
        direction_score = sum(weight*x[0] for weight,x in zip((.32,.24,.18,.12,.07,.045,.025),entries)) + .6*pressure
        if abs(direction_score) < .35:
            return None
        side = 1 if direction_score > 0 else -1
        weights = (.4,.3,.2,.1)
        agg = lambda i: sum(w*x[i] for w,x in zip(weights,entries[:4]))
        vote = sum(1 if side*x[0]>0 else -1 for x in entries)/len(entries)
        # ATR normalizes each market/timeframe; spread remains in executable price units.
        signed = (
            clamp(side*agg(0)/3),
            clamp(2*agg(1)-1),
            clamp(side*pressure),
            clamp(burst*2-1),
            clamp(agg(2)/2),
            clamp(side*agg(3)),
            clamp(side*agg(4)/2),
            clamp(side*agg(5)/3),
            clamp(side*agg(6)),
            clamp(side*vote),
            clamp((.12-spread)/.12),
        )
        return {"side": side, "time_ms": quote.time_ms, "spread": round(spread,6),
                "features": dict(zip(FEATURES, signed)), "bins": bins5(signed),
                "horizons_ms": CLOCK_MS}


def binomial_tail(n: int, p: float, k: int) -> float:
    """P[Binomial(n,p) >= k] stable for typical NP calibration counts."""
    if k<=0: return 1.
    if k>n: return 0.
    logs = [math.lgamma(n+1)-math.lgamma(j+1)-math.lgamma(n-j+1)
            +j*math.log(p)+(n-j)*math.log1p(-p) for j in range(k,n+1)]
    mx = max(logs)
    return min(1., math.exp(mx)*sum(math.exp(x-mx) for x in logs))


class BNPModel:
    """Shrinkage Naive Bayes likelihood ratios + held-out NP order statistic.

    For negative calibration scores, finds first rank k where a Binomial(n, 1-alpha)
    upper tail is <=delta. Accepts score STRICTLY > threshold score[k].
    Strict inequality avoids accepting ties. Requires independent calibration from
    fitting data. Exchangeability assumptions can fail in clustered markets: these
    are sample-level risk controls, not guaranteed live false-entry bounds.
    """
    def __init__(self, alpha=.15, delta=.05, min_neg=200):
        self.alpha = alpha; self.delta = delta; self.min_neg=min_neg
        self.count = [0,0]
        self.table = [[[0]*5 for _ in FEATURES] for __ in range(2)]
        self.threshold = None
        self.ready = False
        self.n_cal_negative=0
        self.weights=[]
        self.prior=0.

    def fit(self, examples: Iterable[tuple[tuple[int,...],int]]):
        if self.count != [0,0]: raise ValueError("fit once: start fresh")
        for b,y in examples:
            if y not in (0,1) or len(b)!=len(FEATURES) or any(x not in range(5) for x in b):
                raise ValueError("invalid training example")
            self.count[y]+=1
            for i,bi in enumerate(b): self.table[y][i][bi]+=1
        if min(self.count)<10: raise ValueError("insufficient class samples")
        self.prior=math.log((self.count[1]+2)/(self.count[0]+2))
        self.weights = []
        for i in range(len(FEATURES)):
            self.weights.append([math.log((self.table[1][i][b]+2)/(self.count[1]+10))
                               -math.log((self.table[0][i][b]+2)/(self.count[0]+10))
                               for b in range(5)])

    def score(self,bins):
        if not self.weights: raise ValueError("unfitted model")
        # Temper multiple correlated horizon-indicators: probabilities are uncalibrated.
        return self.prior+.25*sum(self.weights[i][b] for i,b in enumerate(bins))

    def calibrate(self, negative_scores):
        if self.ready: raise ValueError("cannot recalibrate frozen policy")
        if not self.weights: raise ValueError("fit before calibration")
        scores=sorted(float(x) for x in negative_scores)
        n=len(scores);self.n_cal_negative=n
        if n<self.min_neg: return False
        lo,hi=1,n+1
        while lo<hi:
            k=(lo+hi)//2
            if binomial_tail(n,1-self.alpha,k)<=self.delta:hi=k
            else:lo=k+1
        k=lo
        if k>n:return False
        self.threshold=scores[k-1]
        self.ready=True
        return True

    def decision(self,candidate):
        if candidate is None: return "NO_CANDIDATE",None
        if not self.ready: return "SHADOW_UNTRAINED",None
        s=self.score(candidate['bins'])
        return ("ENTER" if s>self.threshold else "ABSTAIN_NP"),s

    def write_mt5_policy(self, path, *, real_validated=False):
        """Promote only an independently verified real-tick policy; no auto-promotion."""
        if not self.ready or not real_validated:
            raise ValueError("frozen NP and explicit independent real-tick validation required")
        with open(path, 'w', newline='') as stream:
            wr=csv.writer(stream)
            wr.writerow(["version",VERSION]);wr.writerow(["prior",format(self.prior,'.17g')])
            wr.writerow(["threshold",format(self.threshold,'.17g')])
            wr.writerow(["real_validated",1])
            for i,row in enumerate(self.weights):
                for b,w in enumerate(row):wr.writerow([f"w{i:02d}{b:02d}",format(w,'.17g')])

    def export(self):
        return {"version":VERSION,"features":FEATURES,"clock_ms":CLOCK_MS,
                "alpha":self.alpha,"delta":self.delta,"fit_counts":self.count,
                "cal_negative":self.n_cal_negative,"prior":self.prior,
                "weights":self.weights,"threshold":self.threshold,"ready":self.ready,
                "probability_calibrated":False,"teacher_training_completed":False}

    @classmethod
    def load(cls, data):
        if data.get('version')!=VERSION or tuple(data.get('features',[]))!=FEATURES or tuple(data.get('clock_ms',[]))!=CLOCK_MS:
            raise ValueError("feature/version mismatch")
        obj=cls(alpha=data['alpha'],delta=data['delta'])
        if not data.get('ready') or data.get('threshold') is None:raise ValueError("model not NP-frozen")
        obj.prior=float(data['prior']);obj.weights=data['weights'];obj.threshold=float(data['threshold']);obj.ready=True
        if len(obj.weights)!=len(FEATURES) or any(len(row)!=5 for row in obj.weights):raise ValueError("bad weights")
        return obj


def iter_source(path,source,limit=None):
    """Source-native time and canonical UTC. Coinexx 2026 DST is observed, not guessed."""
    with gzip.open(path, 'rt', newline='') as stream:
        for i,r in enumerate(csv.DictReader(stream)):
            if limit is not None and i>=limit:break
            if source=='coinexx':
                native=int(r['time_msc']);offset=(180 if 20260309<=int(dt.datetime.fromtimestamp(native/1000,dt.timezone.utc).strftime('%Y%m%d'))<20261102 else 120)
                ms=native-offset*60000
                bid=float(r['bid']);ask=float(r['ask'])
            elif source=='dukascopy':
                ms=native=int(r['timestamp_ms_utc']);bid=int(r['bid_raw'])/1000;ask=int(r['ask_raw'])/1000
            else:raise ValueError("unknown source")
            if ask>=bid>0:
                yield Quote(time_ms=ms,bid=bid,ask=ask,native_ms=native)


def replay_shadow(path,source,out,limit=None,scan_interval_ms=500):
    """Only emits feature/opportunity rows. No trades, no training and no future labels."""
    engine=CausalEntryFeatures();policy=BNPModel();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    counts=collections.Counter();last_scan=None;first=None;last=None
    with (out/'shadow_candidates.csv').open('w',newline='') as stream:
        wr=csv.writer(stream)
        wr.writerow(['utc_ms','native_ms','side','spread','score','decision',*FEATURES,*['bin_'+k for k in FEATURES]])
        for t in iter_source(path,source,limit):
            if first is None:first=t.time_ms
            last=t.time_ms
            engine.add(t)
            counts['ticks']+=1
            if last_scan is not None and t.time_ms//scan_interval_ms==last_scan:continue
            last_scan=t.time_ms//scan_interval_ms
            counts['scans']+=1
            cand=engine.candidate(t)
            decision,score=policy.decision(cand)
            counts[decision]+=1
            if cand is None:continue
            wr.writerow([t.time_ms,t.native_ms,cand['side'],cand['spread'],'',decision,
                        *[round(v,7) for v in cand['features'].values()],*cand['bins']])
    digest=hashlib.sha256(Path(path).read_bytes()).hexdigest()  # source identity
    summary={"version":VERSION,"source":source,"input":Path(path).name,
             "source_sha256":digest,"ticks":engine.ticks,"gap_resets":engine.gap_resets,
             "first_utc_ms":first,"last_utc_ms":last,"counts":dict(counts),
             "training":"NOT RUN","trade_execution":"NOT RUN",
             "probability_calibrated":False,"NP_frozen":False,
             "limits":"Untrained feature probe; no performance or profitability claims"}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'untrained_model.json').write_text(json.dumps(policy.export(),indent=2))
    return summary


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ticks',required=True);p.add_argument('--source',choices=('coinexx','dukascopy'),required=True)
    p.add_argument('--out',required=True);p.add_argument('--limit',type=int)
    args=p.parse_args()
    print(json.dumps(replay_shadow(args.ticks,args.source,args.out,args.limit),indent=2))

if __name__=='__main__':main()
