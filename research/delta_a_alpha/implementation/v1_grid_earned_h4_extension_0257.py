"""GRID0257 verified additional original H4 sniper source-owned positions.

R9 SYNTH: performance goals, R9 OVERFIT: retrospective optimal trades,
months differ; grid near multi-HTF/multi-scalping/sniper and high-volume target.
This is research-only source OWNERSHIP / PERMISSION, never a trading order.

A separate 2-paid-position H4 base ledger must first have its LAST FIVE
actually settled BASE positions net POSITIVE after the modeled execution costs.
Only then may an original completed-H4 second-acceptance source offer a fixed
one-ounce third/fourth position. Additional positions do not grant themselves
credit; only independently acknowledged BASE closes do. No lot changes,
recovery escalation, unpaid/fabricated fills, current-month lookup, lookahead.
"""
from dataclasses import dataclass
from collections import deque
from typing import Optional

ORIGINAL_BASE_SLOTS=2
MAX_H4_SOURCE_SLOTS=4
MAX_GLOBAL_SLOTS=16
REQUIRED_PAID_BASE_CLOSES=5

@dataclass(frozen=True)
class ConfirmedBaseClose:
    owner_id:int
    ticket_id:int
    close_ms:int
    pnl_raw:int
    source:str='GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE'
    actually_paid:bool=False
    quote_reconciled:bool=False

@dataclass(frozen=True)
class H4EarnedExtensionPermission:
    owner_id:int
    signal_known_ms:int
    previous_five_paid_base_net_raw:int
    direction:int
    source:str='GRID0257_H4_EARNED_EXTENSION_RESEARCH_ONLY'

class H4EarnedExtensionPermission0257:
    """Read-only eligibility using settled BASE closes; source events downstream.

    The caller tracks real confirmations, existing source positions and global
    capacity. Do not conflate quote-reconciled backtest with broker account cash.
    """
    def __init__(self):
        self._last_five=deque(maxlen=REQUIRED_PAID_BASE_CLOSES)
        self._closed_tickets=set()
        self._used_source_events=set()
        self._last_close_ms:Optional[int]=None
        self.accepted=0
        self.denied=0

    def record_base_close(self,c:ConfirmedBaseClose):
        if not c.actually_paid or not c.quote_reconciled:
            raise ValueError('no synthetic or unacknowledged BASE close credit')
        if c.source!='GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE':
            raise ValueError('only original BASE H4 sniper closes earn capacity')
        if c.ticket_id in self._closed_tickets:
            raise ValueError('duplicate paid closed ticket')
        if c.close_ms<0 or c.owner_id<0:
            raise ValueError('invalid BASE close clock/owner')
        if self._last_close_ms is not None and c.close_ms<self._last_close_ms:
            raise ValueError('out-of-order settled BASE close')
        self._closed_tickets.add(c.ticket_id)
        self._last_close_ms=c.close_ms
        self._last_five.append(c)

    def request(self,*,source_owner:int,source_invite_id:int,
                source_time_ms:int,direction:int,
                active_base_positions:int,active_h4_positions:int,
                active_global_positions:int,source_verified:bool,
                observed_tradable_quote_ms:int)->Optional[H4EarnedExtensionPermission]:
        if (source_owner<0 or source_invite_id<0 or source_time_ms<0
                or direction not in (-1,1)
                or active_base_positions<0 or active_h4_positions<0
                or active_global_positions<0):
            raise ValueError('bad source/side/source-position inputs')
        if active_base_positions>ORIGINAL_BASE_SLOTS:
            raise ValueError('BASE sleeve may never exceed 2 constant positions')
        if active_h4_positions<active_base_positions:
            raise ValueError('H4 positions must include BASE positions')
        if active_global_positions<active_h4_positions:
            raise ValueError('global positions must include H4 positions')
        # Non-retroactive: a quote can only be used when it is genuinely seen.
        if observed_tradable_quote_ms<source_time_ms or observed_tradable_quote_ms>source_time_ms+1000:
            return self._deny()
        if not source_verified or (source_owner,source_invite_id) in self._used_source_events:
            return self._deny()
        if (active_base_positions!=ORIGINAL_BASE_SLOTS
                or active_h4_positions>=MAX_H4_SOURCE_SLOTS
                or active_global_positions>=MAX_GLOBAL_SLOTS):
            return self._deny()
        # NO source wins, oracle teacher scores, or portfolio future outcome.
        if (len(self._last_five)<REQUIRED_PAID_BASE_CLOSES
                or self._last_close_ms is None
                or self._last_close_ms>observed_tradable_quote_ms):
            return self._deny()
        paid_net=sum(x.pnl_raw for x in self._last_five)
        if paid_net<=0:return self._deny()
        self._used_source_events.add((source_owner,source_invite_id))
        self.accepted+=1
        return H4EarnedExtensionPermission(source_owner,source_time_ms,paid_net,direction)

    def _deny(self):
        self.denied+=1
        return None

    def stats(self):
        return {'stage':'G0_SHADOW_PERMISSION_ONLY',
                'accepted':self.accepted,'denied':self.denied,
                'last_five_confirmed_base_closes':len(self._last_five),
                'last_five_base_quote_net_raw':sum(x.pnl_raw for x in self._last_five),
                'original_base_slots':2,'max_h4_slots':4,'max_global_slots':16,
                'broker_cash_verified':False,'trading_enabled':False}
