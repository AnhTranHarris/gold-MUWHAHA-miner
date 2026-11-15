"""R9 V10: bounded, source-chronological structure attribution; NO order execution.

Only closed observed bars create structure. An active quote may test a PREVIOUSLY
confirmed boundary. All price integers are Coinexx 0.01 XAU units; native MT5
zone parity is NOT assumed. No tick regeneration, commercial model or PnL logic.
"""
from __future__ import annotations
from collections import deque, Counter
from dataclasses import dataclass, asdict
from typing import Optional

TF = (1000, 5000, 15000, 30000, 60000, 300000, 900000, 3600000, 14400000)
NAMES = {1000:"S1",5000:"S5",15000:"S15",30000:"S30",60000:"M1",
         300000:"M5",900000:"M15",3600000:"H1",14400000:"H4"}


@dataclass
class Bar:
    start_ms: int
    first_ms: int
    last_ms: int
    o: float
    h: float
    l: float
    c: float
    bid_c: int
    ask_c: int
    spread: int
    n: int = 1

    @classmethod
    def tick(cls, t):
        m = (t.bid_u + t.ask_u) / 2.
        return cls(t.time_msc // 1000 * 1000, t.time_msc, t.time_msc,
                   m, m, m, m, t.bid_u, t.ask_u, t.ask_u - t.bid_u)

    def add_tick(self, t):
        m = (t.bid_u + t.ask_u) / 2.
        self.last_ms = t.time_msc
        self.h = max(self.h, m)
        self.l = min(self.l, m)
        self.c = m
        self.bid_c = t.bid_u
        self.ask_c = t.ask_u
        self.spread = t.ask_u - t.bid_u
        self.n += 1

    @classmethod
    def from_child(cls, b, width):
        return cls(b.start_ms // width * width, b.first_ms, b.last_ms,
                   b.o, b.h, b.l, b.c, b.bid_c, b.ask_c, b.spread, b.n)

    def add_child(self, b):
        self.last_ms = b.last_ms
        self.h = max(self.h, b.h)
        self.l = min(self.l, b.l)
        self.c = b.c
        self.bid_c = b.bid_c
        self.ask_c = b.ask_c
        self.spread = b.spread
        self.n += b.n


@dataclass
class Zone:
    id: int
    kind: str
    center: float
    half: float
    sources: tuple[str, ...]
    confirmed_ms: int
    last_ms: int
    touches: int = 1
    last_test_ms: int = -1

    @property
    def low(self): return self.center - self.half
    @property
    def high(self): return self.center + self.half


@dataclass(frozen=True)
class StructureSnapshot:
    time_msc: int
    pattern: str
    regime: str
    micro_direction: int
    parent_direction: int
    nested: str
    change_alarm: bool
    directional_change: int
    breakout_side: int
    breakout_phase: str
    support: Optional[tuple[float, float, int]]
    resistance: Optional[tuple[float, float, int]]
    quote_gap_ms: int
    source: str = "Coinexx_quote_only_past_observed"

    def as_record(self):
        return asdict(self)


class CausalMarketStructure:
    """Bounded memory: one active second, fixed completed rings, <=40 zones.

    O(1) per source quote. Higher-frame aggregation, zones and context advance
    only at observed 1s changes; no fabricated empty seconds. Pivots have two
    COMPLETED bars on their right and never backdate the confirmation time.
    """
    def __init__(self, zone_cap=40, pivot_right=2, max_gap_ms=2500):
        if not 8 <= zone_cap <= 128 or pivot_right != 2:
            raise ValueError("V10 frozen bounds: 8..128 zones, right=2")
        self.zone_cap, self.max_gap_ms = zone_cap, max_gap_ms
        self.closed = {tf:deque(maxlen=128) for tf in TF}
        self.active = {}
        self.vol = {tf:None for tf in TF}
        self.swings = {tf:{"SUPPORT":deque(maxlen=8),"RESISTANCE":deque(maxlen=8)}
                       for tf in TF}
        self.zones = []
        self.next_zone = 1
        self.nearest = {"SUPPORT":None, "RESISTANCE":None}
        self.now_ms = None
        self.last_bid = None
        self.last_ask = None
        self.gap_ms = 0
        self.spread = 0
        self.breakout = None
        self.last_zone_attempt = {}
        self.dc_direction = 0
        self.dc_extreme = None
        self.dc_last_change_ms = -1
        self.change_alarm_ms = -1
        self.change_cusum_pos = 0.
        self.change_cusum_neg = 0.
        self.change_scale = 1.
        self.counters = Counter()

    def on_quote(self, t):
        now = int(t.time_msc)
        if now < 0 or t.bid_u <= 0 or t.ask_u < t.bid_u:
            raise ValueError("Invalid observed Bid/Ask")
        if self.now_ms is not None and now < self.now_ms:
            raise ValueError("Nonmonotonic original quote chronology")
        self.gap_ms = 0 if self.now_ms is None else now - self.now_ms
        if self.gap_ms > self.max_gap_ms:
            self.breakout = None
            self.dc_extreme = None
            self.dc_direction = 0
            self.change_cusum_pos = self.change_cusum_neg = 0.
            self.counters["quote_gap_reset"] += 1
        sec = now // 1000 * 1000
        cur = self.active.get(1000)
        if cur is None:
            self.active[1000] = Bar.tick(t)
        elif cur.start_ms == sec:
            cur.add_tick(t)
        else:
            self._complete(1000, cur, now)
            self.active[1000] = Bar.tick(t)
            self._refresh_nearest((t.bid_u+t.ask_u)/2., now)
        self._directional_change(t)
        if self.gap_ms <= self.max_gap_ms:
            self._breakout_step(t)
        self.now_ms = now
        self.last_bid, self.last_ask = t.bid_u, t.ask_u
        self.spread = t.ask_u - t.bid_u
        self.counters["quotes"] += 1

    def _complete(self, tf, b, observed_at):
        q = self.closed[tf]
        previous = q[-1] if q else None
        tr = (b.h-b.l if previous is None else
              max(b.h-b.l,abs(b.h-previous.c),abs(b.l-previous.c)))
        a = self.vol[tf]
        self.vol[tf] = tr if a is None else (13.*a+tr)/14.
        q.append(b)
        self.counters["closed_"+NAMES[tf]] += 1
        if tf == 1000:
            self._update_change(b, previous, observed_at)
            self._breakout_completed_second(b, observed_at)
        self._confirm_pivot(tf, observed_at)
        idx = TF.index(tf)
        if idx+1 >= len(TF): return
        width = TF[idx+1]
        parent = self.active.get(width)
        if parent is None:
            self.active[width] = Bar.from_child(b,width)
        elif b.start_ms//width*width == parent.start_ms:
            parent.add_child(b)
        else:
            self._complete(width,parent,observed_at)
            self.active[width] = Bar.from_child(b,width)

    def _confirm_pivot(self, tf, observed_at):
        if tf < 5000:return  # no unstable 1s pivot S/R
        q = self.closed[tf]
        if len(q)<5:return
        w = list(q)[-5:]
        if any(w[i+1].start_ms-w[i].start_ms!=tf for i in range(4)):
            return
        pivot = w[2]  # shift=3; the two right-hand bars are already closed
        highs = [x.h for x in w]
        lows = [x.l for x in w]
        if all(highs[2]>highs[i] for i in (0,1,3,4)):
            self._add_zone("RESISTANCE",tf,pivot.h,observed_at)
        if all(lows[2]<lows[i] for i in (0,1,3,4)):
            self._add_zone("SUPPORT",tf,pivot.l,observed_at)

    def _add_zone(self, kind, tf, price, now):
        atr = self.vol[tf] or 0.
        half = min(500., max(2.,float(self.spread)*.5,atr*.16))
        src = NAMES[tf]
        self.swings[tf][kind].append((price,now))
        candidates = [z for z in self.zones if z.kind==kind
                      and abs(z.center-price)<=max(z.half,half)*1.5]
        if candidates:
            z = min(candidates,key=lambda x:abs(x.center-price))
            old = z.touches
            z.center=(z.center*min(old,8)+price)/(min(old,8)+1)
            z.half=max(z.half,half)
            z.sources=tuple(sorted(set(z.sources+(src,))))
            z.touches+=1
            z.last_ms=now
        else:
            self.zones.append(Zone(self.next_zone,kind,price,half,(src,),now,now))
            self.next_zone+=1
        if len(self.zones)>self.zone_cap:
            self.zones.sort(key=lambda z:(len(z.sources)*2+min(z.touches,8),
                                          z.last_ms))
            self.zones.pop(0)
        self.counters["confirmed_"+kind]+=1

    def _refresh_nearest(self, mid, now):
        for kind in self.nearest:
            # Never label ancient zones as active; HTF zones can live for days.
            valid=[z for z in self.zones if z.kind==kind
                   and now-z.last_ms <= 14*86400000]
            self.nearest[kind]=(min(valid,key=lambda z:abs(z.center-mid))
                                if valid else None)

    def _directional_change(self,t):
        mid=(t.bid_u+t.ask_u)/2.
        theta=max(5.,2.*(t.ask_u-t.bid_u),.35*(self.vol[60000] or 0.))
        if self.dc_extreme is None:
            self.dc_extreme=mid
            return
        if self.dc_direction==0:
            if mid-self.dc_extreme>=theta:self.dc_direction=1
            elif self.dc_extreme-mid>=theta:self.dc_direction=-1
            else:
                self.dc_extreme=mid if abs(mid-self.dc_extreme)>theta/2 else self.dc_extreme
                return
            self.dc_extreme=mid
            self.dc_last_change_ms=t.time_msc
            return
        if self.dc_direction>0:
            self.dc_extreme=max(self.dc_extreme,mid)
            if self.dc_extreme-mid>=theta:
                self.dc_direction=-1
                self.dc_extreme=mid
                self.dc_last_change_ms=t.time_msc
                self.counters["directional_change"]+=1
        else:
            self.dc_extreme=min(self.dc_extreme,mid)
            if mid-self.dc_extreme>=theta:
                self.dc_direction=1
                self.dc_extreme=mid
                self.dc_last_change_ms=t.time_msc
                self.counters["directional_change"]+=1

    def _update_change(self,b,prev,now):
        if prev is None or b.start_ms-prev.start_ms!=1000:return
        d=b.c-prev.c
        self.change_scale=.94*self.change_scale+.06*abs(d)
        k=max(1.,.5*self.change_scale)
        h=max(6.,4.*self.change_scale)
        self.change_cusum_pos=max(0.,self.change_cusum_pos+d-k)
        self.change_cusum_neg=min(0.,self.change_cusum_neg+d+k)
        if self.change_cusum_pos>h or self.change_cusum_neg< -h:
            self.change_alarm_ms=now
            self.change_cusum_pos=self.change_cusum_neg=0.
            self.counters["change_alarm"]+=1

    def _breakout_completed_second(self,b,now):
        e=self.breakout
        if not e or e["phase"]!="PROBE":return
        passed = b.bid_c>e["boundary"] if e["side"]>0 else b.ask_c<e["boundary"]
        e["confirm"] = e["confirm"]+1 if passed else 0
        if e["confirm"]>=2 and now>=e["start_ms"]+1000:
            e["phase"]="ACCEPTED"
            self.counters["breakout_accepted"]+=1

    def _breakout_step(self,t):
        e=self.breakout
        if e:
            age=t.time_msc-e["start_ms"]
            if e["phase"] in ("FAILED","EXPIRED"):
                if age>10000:self.breakout=None
                else:return
            elif age>30000:
                self.breakout=None
            elif e["phase"]=="PROBE":
                failed=(t.bid_u<e["zone_low"] if e["side"]>0
                        else t.ask_u>e["zone_high"])
                if failed:
                    e["phase"]="FAILED"
                    self.counters["false_break_detected"]+=1
                    return
                if age>15000:
                    e["phase"]="EXPIRED";return
        if self.breakout is not None or self.last_bid is None:return
        for kind,side in (("RESISTANCE",1),("SUPPORT",-1)):
            z=self.nearest[kind]
            if z is None:continue
            boundary=(z.high if side>0 else z.low)
            # One tick size buffer, never use midpoint for executable breakout.
            boundary+=1 if side>0 else -1
            was=self.last_bid if side>0 else self.last_ask
            is_now=t.bid_u if side>0 else t.ask_u
            crossed=(was<=boundary<is_now if side>0 else
                     was>=boundary>is_now)
            if crossed and t.time_msc-self.last_zone_attempt.get((z.id,side),-10**12)>=10000:
                self.breakout=dict(side=side,phase="PROBE",start_ms=t.time_msc,
                                   boundary=boundary,zone_low=z.low,zone_high=z.high,
                                   zone_id=z.id,confirm=0)
                self.last_zone_attempt[(z.id,side)]=t.time_msc
                self.counters["breakout_probed"]+=1
                return

    def _direction(self,tf):
        s=self.swings[tf]
        highs=s["RESISTANCE"]
        lows=s["SUPPORT"]
        if len(highs)>=2 and len(lows)>=2:
            up=highs[-1][0]>highs[-2][0] and lows[-1][0]>lows[-2][0]
            dn=highs[-1][0]<highs[-2][0] and lows[-1][0]<lows[-2][0]
            if up:return 1
            if dn:return -1
        q=self.closed[tf]
        if len(q)<8:return 0
        w=list(q)[-8:]
        if any(w[i+1].start_ms-w[i].start_ms!=tf for i in range(7)):
            return 0
        travel=sum(abs(w[i+1].c-w[i].c) for i in range(7))
        delta=w[-1].c-w[0].c
        if abs(delta)/max(1.,travel)<.62:return 0
        if abs(delta)<max(3.,(self.vol[tf] or 0.)*.8):return 0
        return 1 if delta>0 else -1

    def snapshot(self,t):
        if self.now_ms!=t.time_msc:
            raise ValueError("Call on_quote first; decision is as-of-source-tick")
        micro=self._direction(15000)
        parent=self._direction(300000) or self._direction(60000)
        if parent and micro:
            nested="ALIGNED" if parent==micro else "COUNTERTREND"
        else:nested="UNRESOLVED"
        q=self.closed[15000]
        consolidation=False
        if len(q)>=8:
            w=list(q)[-8:]
            if all(w[i+1].start_ms-w[i].start_ms==15000 for i in range(7)):
                travel=sum(abs(w[i+1].c-w[i].c) for i in range(7))
                net=abs(w[-1].c-w[0].c)
                compression=(max(x.h for x in w)-min(x.l for x in w))
                consolidation=(net/max(1.,travel)<.34 and
                               compression<=max(12.,3.*(self.vol[15000] or 0.)))
        alert=self.change_alarm_ms>=0 and t.time_msc-self.change_alarm_ms<15000
        e=self.breakout
        phase=e["phase"] if e else "NONE"
        side=e["side"] if e else 0
        if self.gap_ms>self.max_gap_ms:
            pattern="UNKNOWN_STALE"
        elif phase=="PROBE":pattern="BREAKOUT_PROBE"
        elif phase=="ACCEPTED":pattern="BREAKOUT_ACCEPTED"
        elif phase=="FAILED":pattern="FAILED_BREAKOUT"
        elif phase=="EXPIRED":pattern="BREAKOUT_UNCONFIRMED"
        elif parent and micro and parent!=micro and alert:
            pattern="REVERSAL_CANDIDATE"
        elif parent and micro and parent!=micro:
            pattern="NESTED_PULLBACK"
        elif consolidation:pattern="CONSOLIDATION"
        elif parent and parent==micro:pattern="TREND_CONTINUATION"
        elif alert:pattern="REGIME_TRANSITION"
        else:pattern="UNKNOWN"
        regime=("COMPRESSION" if consolidation else
                "TRANSITION" if alert else
                "DIRECTIONAL" if micro else "UNDETERMINED")
        def zt(kind):
            z=self.nearest[kind]
            return (round(z.low,3),round(z.high,3),z.id) if z else None
        return StructureSnapshot(t.time_msc,pattern,regime,micro,parent,nested,
                                 alert,self.dc_direction,side,phase,
                                 zt("SUPPORT"),zt("RESISTANCE"),self.gap_ms)

    @staticmethod
    def entry_advice(snap,side):
        if side not in (-1,1):raise ValueError("side")
        if snap.pattern=="UNKNOWN_STALE":return "WAIT_STALE"
        if snap.breakout_phase=="ACCEPTED" and side==snap.breakout_side:
            return "BREAKOUT_ACCEPTANCE"
        if snap.breakout_phase=="PROBE" and side==snap.breakout_side:
            return "PENDING_CONFIRMATION"
        if snap.pattern=="FAILED_BREAKOUT" and side==snap.breakout_side:
            return "AVOID_FAILED_BREAK"
        if snap.parent_direction==side and snap.micro_direction==side:
            return "ALIGNED_CONTINUATION"
        if snap.parent_direction==-side and snap.micro_direction==side:
            return "COUNTERTREND_SPECIALIST"
        if snap.pattern=="CONSOLIDATION":return "RANGE_SPECIALIST"
        return "UNCLASSIFIED_OPPORTUNITY"

    @staticmethod
    def hold_advice(snap,entry_side,entry_pattern):
        if snap.pattern=="UNKNOWN_STALE":return "RISK_REVIEW_STALE"
        if snap.breakout_phase=="FAILED" and snap.breakout_side==entry_side:
            return "THESIS_INVALIDATION_REVIEW"
        if snap.parent_direction==-entry_side and snap.micro_direction==-entry_side:
            return "PARENT_OPPOSED_REVIEW"
        if snap.pattern=="REVERSAL_CANDIDATE" and snap.micro_direction==-entry_side:
            return "REVERSAL_DEFENSE_REVIEW"
        return "HOLD_STRUCTURE_OBSERVE"
