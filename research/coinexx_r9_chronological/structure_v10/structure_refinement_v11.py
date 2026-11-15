"""V11: source-exact, read-only structural refinement of V10.

No changes to V9 execution, stop placement, holding, governor, tick history,
or V10 baseline. Quote data cannot reveal unobserved institutional orders.
Prices are Coinexx integer cents (100 units per $1 XAUUSD).
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from typing import Optional

from causal_structure import CausalMarketStructure

# Frames M5..H4 have isolated capacity. S5/M1 churn cannot evict them.
QUOTAS = {300_000:12, 900_000:12, 3_600_000:16, 14_400_000:16}
LIFETIMES = {300_000:2*86_400_000, 900_000:7*86_400_000,
             3_600_000:21*86_400_000, 14_400_000:45*86_400_000}
TF_NAMES = {300_000:"M5",900_000:"M15",3_600_000:"H1",14_400_000:"H4"}


@dataclass
class PersistentZone:
    key: str
    tf_ms: int
    kind: str
    center: float
    half: float
    confirmed_ms: int
    last_confirmed_ms: int
    confirmations: int = 1
    # Observations, not executed-order liquidity or directional strength.
    @property
    def low(self): return self.center-self.half
    @property
    def high(self): return self.center+self.half

    def record(self):
        return {"key":self.key,"tf":TF_NAMES[self.tf_ms],
                "kind":self.kind,"low":round(self.low,3),
                "high":round(self.high,3),
                "confirmations":self.confirmations,
                "confirmed_ms":self.confirmed_ms,
                "last_confirmed_ms":self.last_confirmed_ms}


@dataclass(frozen=True)
class EvidenceProfile:
    primary: str
    subtype: str
    reason: str
    evidence_sources: tuple[str,...]
    micro_efficiency: Optional[float]
    parent_efficiency: Optional[float]
    quote_gap_ms: int
    support_zones: int
    resistance_zones: int

    def record(self):return asdict(self)


class ProtectedZoneBank:
    def __init__(self):
        self.buckets={tf:[] for tf in QUOTAS}
        self.serial=0
        self.counters=Counter()

    def _live(self,z,now):
        return z.confirmed_ms<=now and now-z.last_confirmed_ms<=LIFETIMES[z.tf_ms]

    def add(self,tf,kind,price,atr,spread,now):
        if tf not in QUOTAS or kind not in ("SUPPORT","RESISTANCE"):
            raise ValueError("Unsupported confirmed HTF zone")
        half=min(500.,max(2.,spread*.5,.16*max(0.,atr)))
        bucket=self.buckets[tf]
        # Retain a separate bank for each HTF; update only the same-kind
        # confirmed swings at the same timeframe, never shift confirmation back.
        valid=[z for z in bucket if self._live(z,now)]
        if len(valid)!=len(bucket):
            self.counters["expired_"+TF_NAMES[tf]]+=len(bucket)-len(valid)
        bucket[:]=valid
        near=[z for z in bucket if z.kind==kind and
              abs(z.center-price)<=1.5*max(z.half,half)]
        if near:
            z=min(near,key=lambda item:abs(item.center-price))
            weight=min(8,z.confirmations)
            z.center=(z.center*weight+price)/(weight+1)
            z.half=max(z.half,half)
            z.last_confirmed_ms=now
            z.confirmations+=1
            self.counters["zone_merged_"+TF_NAMES[tf]]+=1
            return z
        self.serial+=1
        z=PersistentZone(f"{TF_NAMES[tf]}:{self.serial}",tf,kind,
                         price,half,now,now)
        if len(bucket)>=QUOTAS[tf]:
            # Within its OWN timeframe, weak/stale zones are displaced.
            # A S5/M1 pivot can never evict M15/H1/H4 zones.
            evict=min(bucket,key=lambda p:(min(p.confirmations,8),
                                      p.last_confirmed_ms))
            bucket.remove(evict)
            self.counters["evicted_"+TF_NAMES[tf]]+=1
        bucket.append(z)
        self.counters["created_"+TF_NAMES[tf]]+=1
        return z

    def active(self,now,kind=None):
        return [z for tf in QUOTAS for z in self.buckets[tf]
                if self._live(z,now) and (kind is None or z.kind==kind)]

    def counts(self,now):
        return {TF_NAMES[tf]:sum(self._live(z,now) for z in self.buckets[tf])
                for tf in QUOTAS}

    def protective_candidates(self,side,liquidation,spread,now,
                              base_zones=()):
        """A buy must use SUPPORT *fully below* current bid; sell RESISTANCE
        *fully above* current ask. Never choose an opposite-side reference.
        """
        if side not in (-1,1):raise ValueError("Invalid side")
        if liquidation<=0 or spread<0:raise ValueError("Invalid quote")
        margin=max(2.,2.*spread)
        kind="SUPPORT" if side>0 else "RESISTANCE"
        pool=[(z.key,z.low,z.high,z.tf_ms,z.confirmations)
              for z in self.active(now,kind)]
        for z in base_zones:
            if z.kind!=kind or z.confirmed_ms>now:continue
            if now-z.last_ms>180_000:continue  # micro levels need recency
            # Low-timeframe fallback only; high timeframes live in their
            # own protected bank. Avoid duplicate unversioned HTF entries.
            if set(z.sources).intersection(TF_NAMES.values()):continue
            pool.append((f"micro:{z.id}",z.low,z.high,5_000,z.touches))
        eligible=[]
        for key,low,high,tf,n in pool:
            if side>0:
                if high>=liquidation-margin:continue
                distance=liquidation-high
            else:
                if low<=liquidation+margin:continue
                distance=low-liquidation
            # Reject spatially irrelevant faraway anchors: no fake
            # structural stop simply because an old zone exists somewhere.
            eligible.append((distance,-tf,-min(n,8),key,low,high,tf))
        return sorted(eligible)

    def frozen_reference(self,side,bid,ask,now,base_zones=(),max_span=None):
        liq=bid if side>0 else ask
        spread=ask-bid
        candidates=self.protective_candidates(side,liq,spread,now,base_zones)
        if not candidates:return None
        # Max-span is explicitly an information-quality constraint;
        # it never changes real risk controls.
        for dist,_,_,key,low,high,tf in candidates:
            buffered=max(2.,spread,.10*(high-low))
            stop=low-buffered if side>0 else high+buffered
            span=liq-stop if side>0 else stop-liq
            if span<=0:continue
            if max_span is not None and span>max_span:continue
            return (key,tf,low,high,stop)
        return None


class RefinedStructure(CausalMarketStructure):
    """V10 geometry is unchanged; its event flow also feeds protected HTF zones."""
    def __init__(self):
        super().__init__()
        self.bank=ProtectedZoneBank()
        self.profile_counts=Counter()
        self.subtype_counts=Counter()

    def _add_zone(self,kind,tf,price,now):
        # Preserve the V10 research observations and exact confirmed pivot times.
        super()._add_zone(kind,tf,price,now)
        if tf in QUOTAS:
            self.bank.add(tf,kind,price,self.vol[tf] or 0.,
                          float(self.spread),now)

    def _efficiency(self,tf,need=8):
        q=self.closed[tf]
        if len(q)<need or self.now_ms is None:return None
        w=list(q)[-need:]
        if any(w[i+1].start_ms-w[i].start_ms!=tf
               for i in range(need-1)):return None
        if self.now_ms-w[-1].last_ms>max(3*tf,2_500):return None
        travel=sum(abs(w[i+1].c-w[i].c) for i in range(need-1))
        return (w[-1].c-w[0].c)/max(1.,travel)

    def profile(self,snap,side):
        """Subtype UNKNOWN without manufacturing a strong directional label."""
        if side not in (-1,1):raise ValueError("side")
        micro=self._efficiency(15_000)
        parent=self._efficiency(300_000)
        sources=[]
        if micro is not None:sources.append("COMPLETED_S15")
        if self._efficiency(60_000) is not None:sources.append("COMPLETED_M1")
        if parent is not None:sources.append("COMPLETED_M5")
        for tf,name in TF_NAMES.items():
            q=self.closed[tf]
            if q and self.now_ms is not None and self.now_ms-q[-1].last_ms<3*tf:
                sources.append("COMPLETED_"+name)
        if snap.pattern!="UNKNOWN" and snap.pattern!="UNKNOWN_STALE":
            subtype="PREVIOUSLY_RESOLVED"
            reason="Original V10 specialist classification retained"
        elif snap.pattern=="UNKNOWN_STALE":
            subtype="QUOTE_DISCONTINUITY"
            reason="Current quote gap violates original V10 observation clock"
        elif micro is None:
            subtype="INSUFFICIENT_MICRO_EVIDENCE"
            reason="Insufficient contiguous completed S15 observations"
        elif parent is None:
            if abs(micro)>=.62:
                subtype="MICRO_IMPULSE_UNCONFIRMED_PARENT"
                reason="Directional micro displacement but no continuous M5 parent vote"
            else:
                subtype="INSUFFICIENT_PARENT_EVIDENCE"
                reason="M5 parent unconfirmed; no supported multiframe label"
        elif abs(micro)<.20 and abs(parent)<.20:
            subtype="CROSS_SCALE_ROTATION_CANDIDATE"
            reason="Low efficiency at both S15 and M5; not proven consolidation"
        elif abs(micro)>.62 and abs(parent)>.55 and micro*parent<0:
            subtype="CROSS_SCALE_CONFLICT"
            reason="Completed directional paths oppose across scales"
        elif abs(micro)>.62 and abs(parent)>.55 and micro*parent>0:
            subtype="UNCONFIRMED_ALIGNED_IMPULSE"
            reason="Directional path agrees but V10 swing acceptance absent"
        elif abs(micro)<.22 and abs(parent)>.55:
            subtype="MICRO_PULLBACK_OR_PAUSE"
            reason="Parent directional evidence; micro shows low net displacement"
        elif abs(micro)>.62 and abs(parent)<.22:
            subtype="MICRO_EXPANSION_PARENT_BALANCED"
            reason="Directional micro evidence inside a balanced M5 parent"
        else:
            subtype="MIXED_STRUCTURE_INSUFFICIENT"
            reason="Confirmed observations do not isolate a single mechanism"
        self.profile_counts[snap.pattern]+=1
        self.subtype_counts[subtype]+=1
        return EvidenceProfile(snap.pattern,subtype,reason,tuple(sources),
                               None if micro is None else round(micro,4),
                               None if parent is None else round(parent,4),
                               snap.quote_gap_ms,
                               len(self.bank.active(snap.time_msc,"SUPPORT")),
                               len(self.bank.active(snap.time_msc,"RESISTANCE")))


@dataclass(frozen=True)
class FrozenStructuralThesis:
    side:int
    entry_ms:int
    entry_liquidation:float
    entry_execution:float
    zone_key:Optional[str]
    zone_tf_ms:Optional[int]
    frozen_low:Optional[float]
    frozen_high:Optional[float]
    invalidation_level:Optional[float]
    version:str="V11_READ_ONLY"
    @property
    def anchored(self):return self.zone_key is not None
    def record(self):return asdict(self)


class InvalidationObserver:
    """Two consecutive COMPLETED observed 1-second closes beyond frozen
    invalidation. No tick-count shortcuts or across-gap confirmation.
    Only an observation, never an MT5 stop/close action.
    """
    def __init__(self,thesis:FrozenStructuralThesis,max_gap_ms=2500):
        self.thesis=thesis
        self.max_gap_ms=max_gap_ms
        self.current_second=None
        self.current_liquidation=None
        self.current_last_ms=None
        self.consecutive_closed=0
        self.confirmed=False
        self.first_breach_ms=None
        self.reasons=Counter()

    def observe(self,t):
        if self.confirmed:return "CONFIRMED_INVALIDATION"
        if not self.thesis.anchored:
            self.reasons["UNANCHORED"]+=1
            return "NO_VALID_STRUCTURAL_STOP"
        now=t.time_msc
        second=now//1000
        value=t.bid_u if self.thesis.side>0 else t.ask_u
        if self.current_last_ms is not None:
            if now<self.current_last_ms:raise ValueError("Nonmonotone quote")
            if now-self.current_last_ms>self.max_gap_ms:
                self.current_second=second
                self.current_liquidation=value
                self.current_last_ms=now
                self.consecutive_closed=0
                self.first_breach_ms=None
                self.reasons["GAP_RESET"]+=1
                return "QUOTE_GAP_RESET"
        if self.current_second is None:
            self.current_second=second
        if second!=self.current_second:
            if second-self.current_second!=1:
                self.consecutive_closed=0
            elif self._breached(self.current_liquidation):
                self.consecutive_closed+=1
            else:
                self.consecutive_closed=0
            self.current_second=second
            if self.consecutive_closed>=2:
                self.confirmed=True
                self.reasons["CONFIRMED"]+=1
                self.current_last_ms=now
                self.current_liquidation=value
                return "CONFIRMED_INVALIDATION"
        self.current_last_ms=now
        self.current_liquidation=value
        if self._breached(value):
            if self.first_breach_ms is None:self.first_breach_ms=now
            return "BREACH_PENDING_CLOSED_CONFIRMATION"
        self.first_breach_ms=None
        return "STRUCTURE_INTACT"

    def _breached(self,liq):
        s=self.thesis
        return (liq<s.invalidation_level if s.side>0 else
                liq>s.invalidation_level)


def freeze_thesis(structure:RefinedStructure,side,t):
    if side not in (-1,1):raise ValueError("side")
    # Research-zone reference is not broker SL: ignore far, nonlocal levels.
    # Normalize the maximum plausible structural reference by completed M1
    # volatility without searching hyperparameters on realized PnL.
    atr_m1=structure.vol[60_000] or 0.
    max_span=min(300.,max(20.,3.*atr_m1))
    ref=structure.bank.frozen_reference(side,t.bid_u,t.ask_u,t.time_msc,
                                        structure.zones,max_span=max_span)
    liq=t.bid_u if side>0 else t.ask_u
    execution=t.ask_u if side>0 else t.bid_u
    if ref is None:
        return FrozenStructuralThesis(side,t.time_msc,liq,execution,
                                      None,None,None,None,None)
    key,tf,low,high,invalid=ref
    assert (invalid<liq and high<liq if side>0 else
            invalid>liq and low>liq)
    return FrozenStructuralThesis(side,t.time_msc,liq,execution,
                                  key,tf,low,high,invalid)
