"""Original FEB041->FEB044->FEB045 *entry-known* quality/cap gate, NOT a V1 source generator.

Mechanism authority: FEB044/feb044_screen.py and FEB045/run_pocket_screens.py,
FEB045/engine_statecaps.py, using raw original source numeric IDs and exact
frozen February-fitted first-nine pocket exclusion rules. None is a month
selector. The original source proposals, four L2 roles and all physical L7
fills MUST come from independent V1 adapters, not from this module.

Crucially, this component must NOT be promoted as replicating FEB045 economics:
the frozen FEB045 source ledger itself cannot regenerate after funded exits.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Iterable
from v1_funded_core_033c import Quote, Proposal, Structure, FundedEngine, Close

TEN_MIN_MS = 600_000
SOURCE_PREFIX = 'ORIGINAL_F045_S'  # lineage ID, NOT calendar label


@dataclass(frozen=True)
class CausalFeatures045:
    observed_quote_ms: int
    completed_prior_10m_end_ms: int
    prior_10m_range_usd: float
    directional_impulse_20s_usd: float   # raw signed mid-price impulse; multiply by direction
    prior_bucket_observed_quotes: int

    def valid_for(self, q: Quote) -> bool:
        return (self.observed_quote_ms == q.time_ms and
                0 < self.completed_prior_10m_end_ms <= q.time_ms and
                self.prior_bucket_observed_quotes > 0 and
                self.prior_10m_range_usd >= 0)


class CompletedFEB045Features:
    """One active original 10-minute Bid/Ask-mid bucket and trailing 20s ticks.

    FEB041_COMPLETED_10M_CONTEXT.csv uses max(mid)-min(mid), not a guessed
    trading-range definition; FEB042 feature_attribution.py selected latest
    completed bucket using searchsorted(bucket_end_ms,event_time,'right')-1.
    Impulse is matching prior actual mid at earliest observed tick >= now-20s.
    The first truncated bucket is never certified complete for new funding.
    """
    def __init__(self) -> None:
        self.last_ms = -1
        self.first_bucket = True
        self.bucket_start: int | None = None
        self.bucket_lo = self.bucket_hi = 0
        self.bucket_quotes = 0
        self.completed: tuple[int, float, int] | None = None
        self.recent: deque[tuple[int,int]] = deque()
        self.current: CausalFeatures045 | None = None
        self.gaps = 0

    def on_market_quote(self, q: Quote, engine: FundedEngine | None = None) -> None:
        if q.time_ms < self.last_ms:
            raise ValueError('FEB045 feature chronology must be tick-monotonic')
        midpoint = (q.ask_raw + q.bid_raw)  # doubled raw midpoint avoids rounding loss
        b = q.time_ms // TEN_MIN_MS * TEN_MIN_MS
        if self.bucket_start is None:
            self.bucket_start = b
            self.bucket_lo = self.bucket_hi = midpoint
            self.bucket_quotes = 1
        elif b != self.bucket_start:
            if b < self.bucket_start:
                raise ValueError('FEB045 completed bucket moved backwards')
            self.gaps += (b-self.bucket_start)//TEN_MIN_MS - 1
            if not self.first_bucket:
                self.completed = (self.bucket_start+TEN_MIN_MS,
                    (self.bucket_hi-self.bucket_lo)/2000.0, self.bucket_quotes)
            self.first_bucket = False
            self.bucket_start = b
            self.bucket_lo = self.bucket_hi = midpoint
            self.bucket_quotes = 1
        else:
            self.bucket_lo = min(self.bucket_lo, midpoint)
            self.bucket_hi = max(self.bucket_hi, midpoint)
            self.bucket_quotes += 1
        while self.recent and self.recent[0][0] < q.time_ms - 20_000:
            self.recent.popleft()
        # Original exact left-search needs observed quote no earlier than now-20s.
        self.recent.append((q.time_ms,midpoint))
        if self.completed is None:
            self.current = None
        else:
            end,ran,n = self.completed
            self.current = CausalFeatures045(q.time_ms,end,ran,
                             (midpoint-self.recent[0][1])/2000.0,n)
        self.last_ms = q.time_ms


def original_quality_allows(src: int, phase: int, prior: float, signed_imp20: float, *, cut: int=9) -> bool:
    """Literal FEB044 base + FEB045 allowed overrides + pocket order[:cut].

    cut9 is the frozen February profit research frontier. The *same* predicates
    must apply in any later year or month when identical causal states recur.
    This is a policy-selected-in-February research approximation, not a claim
    of blind out-of-sample economic validity.
    """
    if not 0 <= phase <= 5 or not 0 <= cut <= 10:
        raise ValueError('invalid original 10m phase or pocket count')
    if prior != prior:  # nan
        return False
    allowed = ((src in (17,21,23,25)) or
               (src == 27 and 16 <= prior < 32) or
               (src == 22 and 0 <= prior < 4) or
               (src == 19 and 0 <= prior < 8) or
               (src == 24 and 0 <= prior < 4))
    # Original FEB044 screen early phase exclusions.
    if (src,phase) in ((25,0),(23,5),(21,0)):
        allowed=False
    # FEB045 fixed extra quality rejects.
    reject=((src==19 and phase in (0,1,5,4)) or
            (src==17 and phase in (1,5)) or
            (src==25 and 12<=prior<16) or
            (src==21 and 4<=prior<6) or
            (src==23 and 12<=prior<16))
    allowed = allowed and not reject
    if ((src==22 and 24<=prior<48) or (src==24 and 0<=prior<12)
            or (src==26 and 8<=prior<16)):
        allowed=True
    # Exact original base=(allowed | source<17)&~isin(S,[0,2,3,4,6,27]);
    # Scope here is the original L3 S17...S27 family only.
    if src not in (17,19,21,22,23,24,25,26) or not allowed:
        return False
    pockets=(
       src==25 and phase==2 and 8<=prior<10,
       src==25 and phase==1 and 16<=prior<20,
       src==23 and phase==1 and 8<=prior<10,
       src==17 and phase==3 and 6<=prior<8,
       src==17 and phase==4 and 6<=prior<8,
       src==19 and 2<=prior<4 and 1<=signed_imp20<2,
       src==25 and phase==3 and 16<=prior<20,
       src==23 and phase==2 and 16<=prior<20,
       src==17 and phase==2 and 6<=prior<8,
       src==25 and phase==4 and 20<=prior<24)
    return not any(pockets[:cut])


class FEB045NativeQualityL3:
    """L3 admission adapter for original Sxx proposals; never source-manufactures.

    Only proposal SOURCE lineage must say ORIGINAL_F045_Sxx. S26/S27 from JAN039
    remain unmodified and share the same global funded L7 engine. The February
    policy's source-specific restrictions use physical current portfolio tickets,
    not shadow / frozen-ledger opens. Funded core always remains ultimate gate.
    """
    def __init__(self, upstream, *, cut: int=9, features=None,
                 s22_state_cap: int=512, s25_state_cap: int=512,
                 source22_cap: int=768, source25_cap: int=4096,
                 source26_cap: int=432, phase3_cap: int=448,
                 phase4_cap: int=448, phase5_cap: int=128,
                 s25phase1_cap: int=896, s25phase34_cap: int=1024):
        self.upstream = upstream
        self.features = features or CompletedFEB045Features()
        self.cut = cut
        self.s22_state_cap=s22_state_cap
        self.s25_state_cap=s25_state_cap
        self.source_caps={22:source22_cap,25:source25_cap,26:source26_cap}
        self.phase_caps={3:phase3_cap,4:phase4_cap,5:phase5_cap}
        self.s25phase1_cap=s25phase1_cap
        self.s25phase34_cap=s25phase34_cap
        self.shadow_candidates=0
        self.admitted_candidates=0
        self.denials: dict[str,int]={}

    def _deny(self, why: str) -> None:
        self.denials[why]=self.denials.get(why,0)+1

    def on_market_quote(self,q:Quote,engine:FundedEngine)->None:
        self.features.on_market_quote(q,engine)
        cb=getattr(self.upstream,'on_market_quote',None)
        if cb is not None: cb(q,engine)

    @staticmethod
    def source_id(p: Proposal) -> int | None:
        if p.layer != 'L3' or not p.source.startswith(SOURCE_PREFIX):
            return None
        tail=p.source[len(SOURCE_PREFIX):]
        return int(tail) if tail.isdecimal() else None

    def propose(self,q:Quote,s:Structure,engine:FundedEngine)->Iterable[Proposal]:
        ft=self.features.current
        output=[]
        for p in self.upstream.propose(q,s,engine):
            src=self.source_id(p)
            if src is None:
                # Never apply FEB045 admission masks to other original V1 layers.
                output.append(p)
                continue
            self.shadow_candidates+=1
            if ft is None or not ft.valid_for(q):
                self._deny('MISSING_COMPLETED_CAUSAL_FEB042_CONTEXT')
                continue
            phase=(q.time_ms//TEN_MIN_MS)%6
            if not original_quality_allows(src,phase,ft.prior_10m_range_usd,
                                           p.side*ft.directional_impulse_20s_usd,cut=self.cut):
                self._deny('ORIGINAL_FEB045_QUALITY_POCKET')
                continue
            phys=[x for x in engine.positions.values() if self.source_id(x)==src]
            if src in self.source_caps and len(phys)>=self.source_caps[src]:
                self._deny('ORIGINAL_FEB045_SOURCE_FUNDED_CAP')
                continue
            if src==22 and phase==5 and ft.prior_10m_range_usd>=32 and len(phys)>=self.s22_state_cap:
                self._deny('ORIGINAL_FEB045_S22_COMPLETED_RANGE_CAP')
                continue
            if src==25:
                this_phase=lambda x:(x.entry_ms//TEN_MIN_MS)%6
                if phase==1:
                    in1=sum(this_phase(x)==1 for x in phys)
                    if ft.prior_10m_range_usd>=64 and in1>=self.s25_state_cap:
                        self._deny('ORIGINAL_FEB045_S25_COMPLETED_RANGE_CAP');continue
                    if in1>=self.s25phase1_cap:
                        self._deny('ORIGINAL_FEB045_S25_PHASE1_CAP');continue
                if phase in (3,4) and sum(this_phase(x) in (3,4) for x in phys)>=self.s25phase34_cap:
                    self._deny('ORIGINAL_FEB045_S25_PHASE34_CAP');continue
            if phase in self.phase_caps and src==27:
                # Frozen model gates numeric S27 separately; source 27 is
                # intentionally excluded by the cut9 base policy above.
                if len(phys)>=self.phase_caps[phase]:
                    self._deny('ORIGINAL_FEB045_S27_PHASE_CAP');continue
            self.admitted_candidates+=1
            output.append(p)
        return tuple(output)

    def on_funded_close(self, close: Close, engine: FundedEngine) -> None:
        cb=getattr(self.upstream,'on_funded_close',None)
        if cb is not None: cb(close,engine)

    def on_funded_entry(self,*args)->None:
        cb=getattr(self.upstream,'on_funded_entry',None)
        if cb is not None:cb(*args)