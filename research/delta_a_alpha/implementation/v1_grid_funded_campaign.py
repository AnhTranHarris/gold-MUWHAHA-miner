"""GRID0245: grid-only, fail-closed OmegaFX fill-anchored research source.
Original creator uses last CONFIRMED fill, not last unfilled G0 quote. This is
experimental and NOT wired into L1-L7 or any real orders. Fixed 0.01 lot only.
No Martingale or loss-dependent scaling; all prices integer USD*1000.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SourceProposal:
    id:int
    quote_ms:int
    side:int
    rung:int
    threshold_raw:int
    observed_bid_raw:int
    observed_ask_raw:int
    prior_paid_close_id:Optional[int]

@dataclass(frozen=True)
class PaidClose:
    ticket_id:int
    side:int
    close_ms:int
    realized_net_cash:float
    duration_ms:int

class FundedGridCampaign:
    """Generates grid-source opportunities; only external ACKs create paid state."""
    def __init__(self,*,max_depth=32,max_quote_gap_ms=60000,
                 proposal_lifetime_ms=2000,paid_credit_max_age_ms=300000):
        if min(max_depth,max_quote_gap_ms,proposal_lifetime_ms,paid_credit_max_age_ms)<=0:
            raise ValueError('finite positive limits required')
        self.max_depth=max_depth
        self.max_quote_gap_ms=max_quote_gap_ms
        self.proposal_lifetime_ms=proposal_lifetime_ms
        self.paid_credit_max_age_ms=paid_credit_max_age_ms
        self.last_quote_ms=None
        self.previous_ask_raw=None
        self.window_id=None
        self.frozen_refs=None
        self.last_filled_price_raw={1:None,-1:None}
        self.last_paid_close={1:None,-1:None}
        self.open_tickets={}
        self.depth={1:0,-1:0}
        self.proposals={}
        self.next_id=0
        self.counts={k:0 for k in ('quotes','crossings','proposals','ack_fills',
            'ack_closes','stale','missed_fill','multiple_crossings','expired',
            'earned_child_credit','spread_denied')}
    def observe(self,*,time_ms,bid_raw,ask_raw,completed_h1_window_id,
                completed_h1_high_raw,completed_h1_low_raw,gap_raw,
                broker_tradable=True):
        if self.last_quote_ms is not None and time_ms<self.last_quote_ms:
            raise ValueError('unordered source quotes')
        if (bid_raw<=0 or ask_raw<bid_raw or gap_raw<=0
                or completed_h1_low_raw>completed_h1_high_raw):
            raise ValueError('bad Bid/Ask or completed H1 range / non-executable gap')
        for pid,p in list(self.proposals.items()):
            if time_ms>p.quote_ms+self.proposal_lifetime_ms:
                del self.proposals[pid]
                self.counts['expired']+=1
        gap_reset=self.last_quote_ms is not None and time_ms-self.last_quote_ms>self.max_quote_gap_ms
        new_window=self.window_id!=completed_h1_window_id
        refs=(completed_h1_high_raw,completed_h1_low_raw,gap_raw)
        if not new_window and self.frozen_refs is not None and refs!=self.frozen_refs:
            raise ValueError('intra-auction grid references moved without completed H1')
        self.counts['quotes']+=1
        self.last_quote_ms=time_ms
        if new_window or gap_reset or not broker_tradable:
            self.window_id=completed_h1_window_id
            self.frozen_refs=refs
            self.previous_ask_raw=ask_raw if broker_tradable else None
            self.counts['stale']+=int(gap_reset)
            return ()
        if ask_raw-bid_raw>=gap_raw:
            self.previous_ask_raw=None  # no false crossing through wide-spread quote
            self.counts['spread_denied']+=1
            return ()
        prior=self.previous_ask_raw
        self.previous_ask_raw=ask_raw
        if prior is None or not broker_tradable:return ()
        buy_anchor=self.last_filled_price_raw[1]
        sell_anchor=self.last_filled_price_raw[-1]
        buy_level=(completed_h1_high_raw if buy_anchor is None else buy_anchor)-gap_raw
        sell_level=(completed_h1_low_raw if sell_anchor is None else sell_anchor)+gap_raw
        candidates=[]
        if self.depth[1]<self.max_depth and prior>buy_level>=ask_raw:
            candidates.append((1,buy_level))
        if self.depth[-1]<self.max_depth and prior<sell_level<=ask_raw:
            candidates.append((-1,sell_level))
        if not candidates:return ()
        self.counts['crossings']+=len(candidates)
        if len(candidates)>1:
            self.counts['multiple_crossings']+=len(candidates)-1
            candidates.sort(key=lambda x:(abs(ask_raw-x[1]),-x[0]))
        side,level=candidates[0]
        if any(p.side==side for p in self.proposals.values()):return ()
        self.next_id+=1
        parent=self.last_paid_close[side]
        prior_id=(parent.ticket_id if parent and parent.realized_net_cash>0
                  and 0<time_ms-parent.close_ms<=self.paid_credit_max_age_ms else None)
        p=SourceProposal(self.next_id,time_ms,side,self.depth[side]+1,level,
                         bid_raw,ask_raw,prior_id)
        self.proposals[p.id]=p
        self.counts['proposals']+=1
        self.counts['earned_child_credit']+=int(prior_id is not None)
        return (p,)
    def acknowledge_fill(self,*,proposal_id,ticket_id,time_ms,side,
                         actual_price_raw,actual_lot):
        p=self.proposals.get(proposal_id)
        if (p is None or p.side!=side or time_ms<p.quote_ms
                or time_ms>p.quote_ms+self.proposal_lifetime_ms):
            self.counts['missed_fill']+=1
            raise ValueError('fresh matching proposal required for accepted fill')
        if ticket_id in self.open_tickets or actual_price_raw<=0 or actual_lot!=0.01:
            raise ValueError('invalid ticket, fill price, or 0.01-lot policy')
        del self.proposals[proposal_id]
        self.last_filled_price_raw[side]=actual_price_raw
        self.depth[side]+=1
        self.open_tickets[ticket_id]=(side,time_ms)
        self.counts['ack_fills']+=1
    def acknowledge_close(self,*,ticket_id,close_ms,realized_net_cash):
        if ticket_id not in self.open_tickets:
            raise ValueError('shadow or denied ticket cannot fund a Watchdog child')
        side,opened=self.open_tickets[ticket_id]
        if close_ms<opened:raise ValueError('close precedes accepted entry')
        del self.open_tickets[ticket_id]
        closed=PaidClose(ticket_id,side,close_ms,float(realized_net_cash),close_ms-opened)
        self.last_paid_close[side]=closed
        self.counts['ack_closes']+=1
        if not any(s==side for s,_ in self.open_tickets.values()):
            self.last_filled_price_raw[side]=None
            self.depth[side]=0
        return closed
