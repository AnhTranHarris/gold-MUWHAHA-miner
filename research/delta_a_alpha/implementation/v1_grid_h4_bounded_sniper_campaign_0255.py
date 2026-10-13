"""GRID0255: optional RESEARCH-ONLY bounded paid-sized H4 near-sniper campaign.

R9 SYNTH = PERFORMANCE GOAL. R9 OVERFIT = retrospective optimal-trade oracle
ONLY. Monthly conditions vary. Grid edge targets high volume, near-HTF,
near-scalping and sniper timing. This does NOT authorize any real orders.

The input is a separate H4SecondAcceptanceSource event computed from six
fully FINISHED H4 bars and three consecutive FINISHED M1 closes, or an
independent equivalent as-of source. No future price or OVERFIT score may be
part of admission. The sole persistent campaign change from GRID0254's
research rule is a bounded MAXIMUM TWO constant one-ounce shadow positions
(0.01 lot if broker contract size is 100oz), and an H4-ATR-scaled trailing
room of 1.75x. It does not permit extra entries from any loss, position
size multiplier, averaging, or unfinished H4 inference.

Executed source quotes are NOT broker acknowledged fills. MT5 margin, spreads,
slippage, freeze level, dynamic lot limits, and account drawdown remain NOT
certified. The resulting cash is QUOTE USD PER ONE OUNCE only.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

RAW=1000
MAX_SOURCE_POSITIONS=2
RESEARCH_ROUNDTRIP_FEE_RAW=520
MAX_QUOTE_SPREAD_RAW=1000
MAX_HOLD_MS=86_400_000

@dataclass(frozen=True)
class SniperOffer:
    owner: int
    side: int
    known_at_ms: int
    finished_h4_atr_raw: int
    source: str = 'GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE'

@dataclass
class ShadowPosition:
    owner:int
    side:int
    entry_ms:int
    entry_raw:int
    stop_raw:int
    trail_raw:int
    qty_oz:int=1

@dataclass(frozen=True)
class ShadowClose:
    owner:int
    side:int
    entry_ms:int
    exit_ms:int
    price_raw:int
    pnl_raw:int
    reason:str

def completed_h4_invitation_to_sniper_offer(source_event)->SniperOffer:
    """Connect the existing completed H4/M1 G0 event, not an oracle label."""
    if getattr(source_event,'source',None)!='GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE':
        raise ValueError('GRID0255 accepts only validated H4 second-acceptance source')
    return SniperOffer(owner=source_event.owner, side=source_event.side,
                       known_at_ms=source_event.signal_known_at_ms,
                       finished_h4_atr_raw=source_event.atr_raw,
                       source=source_event.source)

class BoundedH4SniperResearch:
    def __init__(self,*,max_source_positions:int=MAX_SOURCE_POSITIONS,
                 trail_permille:int=1750):
        if max_source_positions!=2 or trail_permille!=1750:
            raise ValueError('GRID0255 exact-preserved research configuration only')
        self.open_positions:list[ShadowPosition]=[]
        self.pending:list[SniperOffer]=[]
        self.seen_owners:set[int]=set()
        self.closes:list[ShadowClose]=[]
        self.last_quote_ms:Optional[int]=None
        self.last_bid_raw:Optional[int]=None
        self.last_ask_raw:Optional[int]=None
        self.max_open_observed=0
        self.rejected_spread=0
        self.denied_capacity=0
        self.expired=0
        self.realized_quote_raw=0
    def offer(self,o:SniperOffer)->None:
        if o.source!='GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE':
            raise ValueError('unsupported or retrospective source label')
        if o.side not in (-1,1) or o.owner<0 or o.finished_h4_atr_raw<=0 or o.known_at_ms<0:
            raise ValueError('invalid completed-H4 offer')
        if self.last_quote_ms is not None and o.known_at_ms<self.last_quote_ms:
            # Calling after the signal's as-of event would backdate admission.
            raise ValueError('late source invitation; use known state only')
        if o.owner in self.seen_owners:
            raise ValueError('one source invitation per H4 owner')
        if self.pending and o.known_at_ms<self.pending[-1].known_at_ms:
            raise ValueError('source invitations out of order')
        self.seen_owners.add(o.owner)
        self.pending.append(o)
    def on_quote(self,*,time_ms:int,bid_raw:int,ask_raw:int,
                 broker_session_tradable:bool=True)->tuple[ShadowClose,...]:
        if (time_ms<0 or bid_raw<=0 or ask_raw<bid_raw
                or (self.last_quote_ms is not None and time_ms<self.last_quote_ms)):
            raise ValueError('invalid observed quote chronology')
        self.last_quote_ms=time_ms
        self.last_bid_raw=bid_raw
        self.last_ask_raw=ask_raw
        actual_closes=[]
        # On original source quotes, existing positions close before source
        # admission at the same timestamp, freeing genuinely available room.
        alive=[]
        for p in self.open_positions:
            opposing=bid_raw if p.side==1 else ask_raw
            stop=(opposing<=p.stop_raw if p.side==1 else opposing>=p.stop_raw)
            aged=time_ms-p.entry_ms>=MAX_HOLD_MS
            if stop or aged:
                pnl=(opposing-p.entry_raw)*p.side*p.qty_oz-RESEARCH_ROUNDTRIP_FEE_RAW
                c=ShadowClose(p.owner,p.side,p.entry_ms,time_ms,opposing,pnl,
                              'observed-stop' if stop else '24h-limit')
                actual_closes.append(c);self.closes.append(c)
                self.realized_quote_raw+=pnl
            else:
                # Original path updates the high-water stop regardless of
                # subsequent loss: position quantity is immutable.
                v=opposing-p.side*p.trail_raw
                if ((p.side==1 and v>p.stop_raw)
                        or (p.side==-1 and v<p.stop_raw)):
                    p.stop_raw=v
                alive.append(p)
        self.open_positions=alive
        waiting=[]
        for o in self.pending:
            if o.known_at_ms>time_ms:
                waiting.append(o);continue
            if time_ms-o.known_at_ms>1000:
                self.expired+=1;continue
            if not broker_session_tradable:
                waiting.append(o);continue
            if ask_raw-bid_raw>MAX_QUOTE_SPREAD_RAW:
                self.rejected_spread+=1;continue
            if len(self.open_positions)>=MAX_SOURCE_POSITIONS:
                self.denied_capacity+=1;continue
            price=ask_raw if o.side==1 else bid_raw
            stop_distance=max(1500,3*(ask_raw-bid_raw),
                              o.finished_h4_atr_raw*3//2)
            trail=max(1000,o.finished_h4_atr_raw*1750//1000)
            self.open_positions.append(ShadowPosition(
                o.owner,o.side,time_ms,price,price-o.side*stop_distance,trail))
            self.max_open_observed=max(self.max_open_observed,len(self.open_positions))
        self.pending=waiting
        return tuple(actual_closes)
    def marked_equity_quote_raw(self)->int:
        if self.last_quote_ms is None:return 0
        eq=self.realized_quote_raw
        for p in self.open_positions:
            mark=self.last_bid_raw if p.side==1 else self.last_ask_raw
            eq+=(mark-p.entry_raw)*p.side*p.qty_oz-RESEARCH_ROUNDTRIP_FEE_RAW
        return eq
    def statistics(self)->dict:
        return {'source':'GRID0255_H4_TWO_INDEPENDENT_SHADOW_SLOTS',
                'max_source_slots':2,'max_open_observed':self.max_open_observed,
                'open_shadow_positions':len(self.open_positions),
                'closed_quote_positions':len(self.closes),
                'realized_quote_usd_per_oz':self.realized_quote_raw/1000,
                'capacity_denials':self.denied_capacity,
                'expired':self.expired,'spread_rejects':self.rejected_spread,
                'trading_enabled':False,'broker_cash_verified':False}
