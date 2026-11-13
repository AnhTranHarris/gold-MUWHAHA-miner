"""Chronological streaming 2-channel path-signature features for Coinexx XAUUSD.

All input observations preserve their original order, including equal-millisecond rows.
No future return, candle high or future quote is referenced by this module.
"""
from __future__ import annotations
from collections import deque
from math import log1p

WINDOWS_MS = (500, 2000, 10000)

class Window:
    __slots__ = ('width','steps','x','y','area2','vb','va','bid_only','ask_only','both','up','down')
    def __init__(self, width: int):
        self.width = width
        self.steps = deque()
        self.x = self.y = self.area2 = self.vb = self.va = 0
        self.bid_only = self.ask_only = self.both = self.up = self.down = 0

    def reset(self):
        self.steps.clear()
        self.x = self.y = self.area2 = self.vb = self.va = 0
        self.bid_only = self.ask_only = self.both = self.up = self.down = 0

    def add(self, time_msc:int, dx:int, dy:int):
        # The depth-2 antisymmetric signature for Bid/Ask is order-sensitive:
        # 2*A = sum_(i<j) [dBid_i*dAsk_j - dAsk_i*dBid_j].
        self.area2 += self.x * dy - self.y * dx
        self.x += dx
        self.y += dy
        self.vb += abs(dx)
        self.va += abs(dy)
        only_b = int(dx != 0 and dy == 0)
        only_a = int(dy != 0 and dx == 0)
        both = int(dx != 0 and dy != 0)
        up = int(dx + dy > 0)
        down = int(dx + dy < 0)
        self.bid_only += only_b
        self.ask_only += only_a
        self.both += both
        self.up += up
        self.down += down
        self.steps.append((time_msc, dx, dy, only_b, only_a, both, up, down))
        self.expire(time_msc)

    def expire(self, now:int):
        boundary = now - self.width
        q = self.steps
        while q and q[0][0] < boundary:
            _,dx,dy,b,a,both,up,down = q.popleft()
            # Remove first step while preserving the ordered-path area.
            self.area2 -= dx * self.y - dy * self.x
            self.x -= dx
            self.y -= dy
            self.vb -= abs(dx)
            self.va -= abs(dy)
            self.bid_only -= b
            self.ask_only -= a
            self.both -= both
            self.up -= up
            self.down -= down

    def features(self, prefix:str) -> dict[str,float]:
        n=len(self.steps)
        travel=self.vb+self.va
        return {
            f'{prefix}_bid_disp': float(self.x),
            f'{prefix}_ask_disp': float(self.y),
            f'{prefix}_spread_disp': float(self.y-self.x),
            f'{prefix}_sig_area2': float(self.area2),
            f'{prefix}_sig_area_norm': self.area2/(1.0+travel*travel),
            f'{prefix}_eff': abs(self.x+self.y)/(1.0+travel),
            f'{prefix}_churn': float(travel),
            f'{prefix}_events': float(n),
            f'{prefix}_bid_only': float(self.bid_only),
            f'{prefix}_ask_only': float(self.ask_only),
            f'{prefix}_both': float(self.both),
            f'{prefix}_up': float(self.up),
            f'{prefix}_down': float(self.down),
            f'{prefix}_intensity_log': log1p(n*1000.0/self.width),
        }

class CausalQuotePath:
    __slots__=('windows','last_time','last_bid','last_ask','prev_gap')
    def __init__(self):
        self.windows = {w:Window(w) for w in WINDOWS_MS}
        self.last_time = None
        self.last_bid = None
        self.last_ask = None
        self.prev_gap = 0

    def observe(self, time_msc:int, bid_u:int, ask_u:int):
        if self.last_time is None:
            self.prev_gap=0
        else:
            delta_t=time_msc-self.last_time
            if delta_t < 0:
                raise ValueError('source timestamp moved backwards')
            self.prev_gap=delta_t
            if delta_t > max(WINDOWS_MS):
                for w in self.windows.values():
                    w.reset()
            else:
                db=bid_u-self.last_bid
                da=ask_u-self.last_ask
                for w in self.windows.values():
                    w.add(time_msc,db,da)
        self.last_time=time_msc
        self.last_bid=bid_u
        self.last_ask=ask_u

    def snapshot(self, side:int) -> dict[str,float]:
        d={'quote_gap_ms':float(self.prev_gap)}
        for width,w in self.windows.items():
            w.expire(self.last_time)
            d.update(w.features(f'w{width}'))
            d[f'w{width}_signed_mid_disp'] = side * (w.x+w.y)*0.5
            d[f'w{width}_signed_bid_ask_agreement'] = min(w.x,w.y) if side>0 else -max(w.x,w.y)
        return d
