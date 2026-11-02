"""Causal sub-minute quote-path geometry; diagnostics ONLY until retrained.

Consumes every ordered bid/ask event, including same-ms events. Does not infer
trade volume or a profitable side. Preserves last five minutes without M1 OHLC
compression. Runtime learned model remains the frozen 103-feature contract.
"""
from __future__ import annotations
import bisect
from collections import deque
import numpy as np

WINDOWS_MS = (250,500,1000,5000,15000,30000,45000,60000,300000)
FIELDS = ('range','first_extreme','extreme_age_ms','terminal_location',
          'max_favorable_up','max_favorable_down','bid_only','ask_only',
          'bid_leads_ask','ask_leads_bid','path_efficiency')
GEOMETRY_NAMES=tuple(f'{name}_{h}ms' for h in WINDOWS_MS for name in FIELDS)

class OrderedQuoteGeometry:
    """Bounded ordered quote tape. Feature snapshots use [now-window,now].

    Same timestamp quotes retain arrival order. The tape is a research feature
    source, not an order executor; O(number of tick updates in the window) per
    snapshot. Do not enable on production MT5 without a throughput benchmark.
    """
    def __init__(self):
        self._events=deque()
        self._last_time=None

    def append(self,t_ms,bid,ask):
        t=int(t_ms);b=float(bid);a=float(ask)
        if not np.isfinite([b,a]).all() or a<b:raise ValueError('invalid bid/ask')
        if self._last_time is not None and t<self._last_time:raise ValueError('nonchronological quote')
        self._last_time=t
        self._events.append((t,b,a))
        while len(self._events)>1 and self._events[0][0]<t-WINDOWS_MS[-1]:
            self._events.popleft()

    def snapshot(self):
        if not self._events:raise ValueError('uninitialized quote geometry')
        events=list(self._events)
        now=events[-1][0]
        times=[e[0] for e in events]
        out=[]
        for h in WINDOWS_MS:
            first=bisect.bisect_left(times,now-h)
            span=events[first:]
            mids=np.asarray([(e[1]+e[2])*.5 for e in span],np.float64)
            n=len(span)
            hi=int(np.argmax(mids));lo=int(np.argmin(mids))
            rng=float(mids[hi]-mids[lo]);start=float(mids[0]);end=float(mids[-1])
            # Signed extremum ordering distinguishes rise-then-fall from fall-then-rise.
            extreme_order=float(np.sign(lo-hi)) if hi!=lo else 0.
            last_extreme=hi if hi>lo else lo
            max_up=float(np.max(mids-start));max_down=float(np.max(start-mids))
            bid_only=ask_only=bid_leads=ask_leads=0
            pending_bid=pending_ask=0
            path=0.
            for k in range(1,n):
                old=span[k-1];cur=span[k]
                db=cur[1]-old[1];da=cur[2]-old[2]
                b_change=abs(db)>1e-10;a_change=abs(da)>1e-10
                if b_change and not a_change:
                    bid_only+=1;pending_bid+=1
                    if pending_ask:ask_leads+=1;pending_ask-=1
                elif a_change and not b_change:
                    ask_only+=1;pending_ask+=1
                    if pending_bid:bid_leads+=1;pending_bid-=1
                elif b_change and a_change:
                    pending_bid=pending_ask=0
                path+=abs(mids[k]-mids[k-1])
            out.extend((rng,extreme_order,float(now-span[last_extreme][0]),
                        float((end-mids[lo])/(rng+1e-10)),max_up,max_down,
                        float(bid_only),float(ask_only),float(bid_leads),
                        float(ask_leads),float(abs(end-start)/(path+1e-10))))
        x=np.asarray(out,dtype=np.float32)
        assert len(x)==len(GEOMETRY_NAMES) and np.isfinite(x).all()
        return x
