"""C2D3K: entry-only original FEB042/JAN037-FEB041 research oracle.

Authority: FEB042/prepare.py loads FEB041_EXPANDED_L3_50MS_PROPOSALS.npz,
then writes E, X, R, D, P, H, S, C, O, N and later feature arrays.
This diagnostic bridge reads strictly E (quote index), S (source), D (side)
from the exact archived FEB042 prepared tape. In particular it NEVER reads
X, R, P, H, C, O, N or any optimized future outcomes from the source tape.

This is a REFERENCE-ORACLE ENTRY TAPE, not an online native signal generator.
It MUST NOT be used as a funded trading source in the deployed Python engine.
"""
from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import hashlib
import zipfile
import numpy as np

ARCHIVE_MEMBER = 'FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz'
ORIGINAL_MEMBER_SHA256 = '64339d0e70dfdb9e85fbb90fb446f96ac1190da681b5e9520a442e3958daa29e'

@dataclass(frozen=True, slots=True)
class SourceOffer:
    quote_ordinal: int
    offer_ordinal: int
    source: int
    side: int
    observed_quote_ms: int
    # identity uses original *proposal* ordinal even when many proposals
    # share one physical quote tick (do not collapse shadow intelligence).
    @property
    def source_event_key(self) -> str:
        return f'ORIGINAL_SOURCE_ONLY:{self.offer_ordinal}:{self.quote_ordinal}:{self.source}:{self.side}'


class OriginalSourceEntryTapeOracle:
    """Quote-clock-indexed, fail-closed source replay for offline parity only."""
    def __init__(self, entry_quote_index, source_id, side):
        e=np.asarray(entry_quote_index)
        s=np.asarray(source_id)
        d=np.asarray(side)
        if e.ndim!=1 or s.ndim!=1 or d.ndim!=1 or not (len(e)==len(s)==len(d)):
            raise ValueError('E, S, D must be 1D equal-length original arrays')
        if e.dtype.kind not in 'iu' or s.dtype.kind not in 'iu' or d.dtype.kind not in 'iu':
            raise TypeError('Original E,S,D arrays must be integral source columns')
        if np.any(e<0) or np.any(e[1:]<e[:-1]) or np.any((d!=1)&(d!=-1)):
            raise ValueError('Invalid quote chronology or direction in original source')
        self._e=e.astype(np.int64,copy=True)
        self._s=s.astype(np.int16,copy=True)
        self._d=d.astype(np.int8,copy=True)
        self._e.flags.writeable=False
        self._s.flags.writeable=False
        self._d.flags.writeable=False
        self._next=0
        self._last_quote=-1
        self._last_quote_ms=-1
        self.source_offer_count=0
        self.same_tick_extra_count=0
        self.max_offers_in_quote=0
        self.observed_unique_offer_quotes=0

    @classmethod
    def from_frozen_archive(cls, archive_path: str | Path):
        with zipfile.ZipFile(archive_path) as z:
            raw=z.read(ARCHIVE_MEMBER)
        if hashlib.sha256(raw).hexdigest()!=ORIGINAL_MEMBER_SHA256:
            raise ValueError('Frozen original FEB042 prepared source archive member hash mismatch')
        with np.load(BytesIO(raw),allow_pickle=False) as source:
            # Strictly whitelist ENTRY-KNOWN research labels. X, R, P, H,
            # future outcomes, and prepared price-feature masks are excluded.
            return cls(source['E'],source['S'],source['D'])

    @property
    def total_source_offers(self)->int:
        return len(self._e)

    @property
    def next_entry_quote_ordinal(self)->int|None:
        return int(self._e[self._next]) if self._next<len(self._e) else None

    def on_observed_quote(self, quote_ordinal:int, timestamp_ms:int, bid_raw:int, ask_raw:int)->tuple[SourceOffer,...]:
        """Allow jumping across quotes only if there are NO skipped source offers.

        Real market event time is supplied by caller from already observed quote;
        a future quote cannot be inspected or requested through this interface.
        """
        if quote_ordinal<=self._last_quote or timestamp_ms<self._last_quote_ms:
            raise ValueError('Original quote chronology must strictly increase by ordinal')
        if bid_raw<=0 or ask_raw<bid_raw:
            raise ValueError('Invalid observed executable quote')
        nxt=self.next_entry_quote_ordinal
        if nxt is not None and nxt<quote_ordinal:
            raise ValueError(f'Unconsumed original source offer at quote {nxt}; cannot skip causal event')
        self._last_quote=quote_ordinal
        self._last_quote_ms=timestamp_ms
        if nxt!=quote_ordinal:
            return ()
        start=self._next
        while self._next<len(self._e) and self._e[self._next]==quote_ordinal:
            self._next+=1
        n=self._next-start
        self.source_offer_count+=n
        self.observed_unique_offer_quotes+=1
        self.same_tick_extra_count+=n-1
        self.max_offers_in_quote=max(self.max_offers_in_quote,n)
        return tuple(SourceOffer(quote_ordinal,j,int(self._s[j]),int(self._d[j]),timestamp_ms)
                     for j in range(start,self._next))

    def assert_exhausted(self):
        if self._next!=len(self._e):
            raise AssertionError(f'{len(self._e)-self._next} original source offers not visited')

    def emit_live_trade(self,*_args,**_kwargs):
        raise NotImplementedError('Original JAN037/FEB041 endogenous source generator NOT YET reconstructed; do not fund future-outcome tape')
