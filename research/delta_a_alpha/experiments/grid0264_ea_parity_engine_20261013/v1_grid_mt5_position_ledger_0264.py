"""GRID0264: EA-portable, evidence-only MT5 position/deal ledger.

Broker HistoryDealGet( ... DEAL_POSITION_ID, DEAL_ENTRY, DEAL_ORDER,
DEAL_TIME_MSC, DEAL_PROFIT, DEAL_COMMISSION, DEAL_SWAP, DEAL_FEE) are
required for a certified event. The broker may use a DIFFERENT closing order.
OnTradeTransaction notifications may arrive in arbitrary order; no DEAL_ADD
is turned into a paid settlement until all needed evidence exists.

No MT5 connected. Offline observations must be explicitly marked historical
and verified. No market quotes synthesize a DEAL_ADD event.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal

LOT = Decimal('0.01')

def D(x):
    d = Decimal(str(x))
    if not d.is_finite():
        raise ValueError('finite decimal amount required')
    return d

@dataclass(frozen=True)
class OrderRequest:
    order_id: str
    request_ms: int
    side: int
    lots: Decimal
    source_id: str
    intent: str  # IN or OUT
    position_id: int|None = None
    def __post_init__(self):
        if not self.order_id or not isinstance(self.request_ms,int) or self.request_ms < 0:
            raise ValueError('invalid request evidence')
        if self.side not in (-1,1) or D(self.lots)<=0 or self.intent not in ('IN','OUT'):
            raise ValueError('invalid order side, volume, or intent')
        if self.intent=='IN' and (not self.source_id or self.position_id is not None):
            raise ValueError('entry must have source and no predicted position id')
        if self.intent=='OUT' and (self.position_id is None or self.position_id<=0):
            raise ValueError('close must name observed position identifier')

@dataclass(frozen=True)
class ObservedDeal:
    deal_id: str
    order_id: str
    position_id: int
    time_ms: int
    kind: str    # DEAL_ENTRY_IN or DEAL_ENTRY_OUT
    side: int
    lots: Decimal
    price_raw: int
    profit: Decimal=Decimal(0)
    commission: Decimal=Decimal(0)
    swap: Decimal=Decimal(0)
    fee: Decimal=Decimal(0)
    reason: str='EXPERT'  # SL, TP, SO can have server-created closing order
    history_verified: bool=False
    def __post_init__(self):
        if not self.deal_id or not self.order_id or self.position_id<=0 or not isinstance(self.time_ms,int) or self.time_ms<0:
            raise ValueError('missing deal/order/position or time')
        if self.kind not in ('IN','OUT') or self.side not in (-1,1) or D(self.lots)<=0 or self.price_raw<=0:
            raise ValueError('bad deal shape')
        if not isinstance(self.history_verified,bool):raise TypeError('history verification must be explicit')
        for x in (self.profit,self.commission,self.swap,self.fee):D(x)
        if self.reason not in ('EXPERT','SL','TP','SO','MANUAL','SERVER'):
            raise ValueError('unsupported broker event origin')
    @property
    def net(self):
        return sum((D(self.profit),D(self.commission),D(self.swap),D(self.fee)),Decimal(0))

@dataclass
class OpenPosition:
    position_id:int
    side:int
    source_id:str
    first_entry_ms:int
    opened:Decimal=Decimal(0)
    closed:Decimal=Decimal(0)
    price_times_lots:Decimal=Decimal(0)
    net_cash:Decimal=Decimal(0)
    last_event_ms:int=0
    entry_order_ids:set[str]=field(default_factory=set)
    exit_order_ids:set[str]=field(default_factory=set)
    paid_ack_entry:bool=False
    paid_ack_close:bool=False
    @property
    def complete(self):return self.opened>0 and self.closed==self.opened
    @property
    def vwap_price_raw(self):return self.price_times_lots/self.opened if self.opened else None

class VerifiedMT5PositionLedger0264:
    """Deal-evidence contract; NOT Dukascopy replay fills or broker certification.

    Asynchronous DEAL_ADD may arrive before REQUEST acknowledgements. Such
    records remain staged until the corresponding request is accepted, never
    counted twice. Server-origin SL/TP/SO/other history-confirmed closings
    are accepted on a different order ticket and matched by position ID.
    """
    def __init__(self, *, account_mode='UNKNOWN', symbol_verified=False,
                 account_cash_verified=False):
        if account_mode not in ('UNKNOWN','HEDGING','NETTING'):raise ValueError('account mode')
        self.account_mode=account_mode
        self.symbol_verified=bool(symbol_verified)
        self.account_cash_verified=bool(account_cash_verified)
        self.requests:dict[str,OrderRequest]={}
        self.checks:dict[str,bool]={}
        self.sent:dict[str,bool]={}
        self.staged:dict[str,ObservedDeal]={}
        self.applied:dict[str,ObservedDeal]={}
        self.positions:dict[int,OpenPosition]={}
        self.cash=Decimal(0)
        self.waiting_reasons:dict[str,str]={}
        self._last_applied_ms:int|None=None
    def _verified(self):
        if self.account_mode!='HEDGING' or not self.symbol_verified:
            raise ValueError('broker account/contract NOT verified HEDGING')
    def add_request(self,x:OrderRequest):
        if x.order_id in self.requests:raise ValueError('duplicate request')
        self.requests[x.order_id]=x
        return self.drain()
    def acknowledge_check(self,order_id,approved):
        if type(approved) is not bool or order_id not in self.requests or order_id in self.checks:
            raise ValueError('invalid duplicate OrderCheck')
        self.checks[order_id]=approved
        return self.drain()
    def acknowledge_send(self,order_id,accepted):
        if type(accepted) is not bool or self.checks.get(order_id) is not True or order_id in self.sent:
            raise ValueError('invalid OrderSend acknowledgment')
        self.sent[order_id]=accepted
        return self.drain()
    def stage_history_deal(self,x:ObservedDeal):
        self._verified()
        if not x.history_verified:raise ValueError('externally confirmed HistoryDeal evidence required')
        prior=self.applied.get(x.deal_id) or self.staged.get(x.deal_id)
        if prior is not None:
            if prior!=x:raise ValueError('conflicting duplicate DEAL_ADD')
            return ()  # idempotent duplicate OnTradeTransaction notification
        self.staged[x.deal_id]=x
        return self.drain()
    def _eligibility(self,x):
        # No guessed request or execution confirmation. Exit transactions from
        # broker SL/TP/SO are independently observable even without EA order.
        o=self.requests.get(x.order_id)
        if o is None:
            if x.kind=='OUT' and x.reason in ('SL','TP','SO','SERVER'):
                p=self.positions.get(x.position_id)
                return (p is not None, 'waiting opening position')
            return False,'missing client request'
        if x.time_ms<o.request_ms:raise ValueError('deal precedes request')
        if o.intent!=x.kind or o.side!=x.side:raise ValueError('request/deal side or entry conflict')
        if o.intent=='OUT' and o.position_id!=x.position_id:
            raise ValueError('close references different position')
        if self.checks.get(x.order_id) is not True or self.sent.get(x.order_id) is not True:
            return False,'missing positive check and accepted send'
        if x.kind=='OUT' and x.position_id not in self.positions:
            return False,'waiting opening position'
        return True,''
    def _apply(self,x):
        o=self.requests.get(x.order_id)
        lots=D(x.lots)
        p=self.positions.get(x.position_id)
        if x.kind=='IN':
            if o is None:raise ValueError('unowned entry')
            if p is None:
                p=OpenPosition(x.position_id,x.side,o.source_id,x.time_ms,last_event_ms=x.time_ms)
                self.positions[x.position_id]=p
            if p.side!=x.side or p.source_id!=o.source_id or p.closed:
                raise ValueError('position ownership/side conflict')
            if p.opened+lots>LOT:
                raise ValueError('funded source exceeds standard .01 parent')
            p.opened+=lots
            p.price_times_lots+=lots*Decimal(x.price_raw)
            p.entry_order_ids.add(x.order_id)
        else:
            if p is None:raise ValueError('cannot close unseen position')
            if p.side!=-x.side or p.closed+lots>p.opened:
                raise ValueError('closing side or overclose')
            p.closed+=lots
            p.exit_order_ids.add(x.order_id)
        if x.time_ms<p.first_entry_ms:
            raise ValueError('closing event predates position entry')
        p.last_event_ms=max(p.last_event_ms,x.time_ms)
        p.net_cash+=x.net
        self.cash+=x.net
        self.applied[x.deal_id]=x
    def drain(self):
        self._verified()
        newly=[]
        changed=True
        while changed:
            changed=False
            for d in sorted(self.staged.values(),key=lambda x:(x.time_ms,x.deal_id)):
                ready,why=self._eligibility(d)
                if not ready:
                    self.waiting_reasons[d.deal_id]=why;continue
                # No chronological oracle backdating once a later transaction
                # has irrevocably been applied. Require replay/reconciliation.
                if self._last_applied_ms is not None and d.time_ms<self._last_applied_ms:
                    raise ValueError('late historical transaction requires full sorted history reconciliation')
                self._apply(d)
                self._last_applied_ms=d.time_ms
                newly.append(d.deal_id)
                del self.staged[d.deal_id]
                self.waiting_reasons.pop(d.deal_id,None)
                changed=True
                break
        return tuple(newly)
    def reconcile_broker_history(self, *, observed_deals, observed_cash_delta, broker_snapshot_verified:bool):
        """Atomically replay a full broker-history snapshot in DEAL_TIME_MSC order.

        This is the explicit resolution for late/out-of-order OnTradeTransaction.
        Incremental stream cannot rewrite an already credited paid-source
        parent: in that case require manual escrow/reset of parent ancestry.
        Broker-provided all-deal net must match the recomputed value exactly.
        """
        self._verified()
        if broker_snapshot_verified is not True:
            raise ValueError('a broker-verified full history snapshot is required')
        if any(p.paid_ack_entry or p.paid_ack_close for p in self.positions.values()):
            raise ValueError('cannot rewrite funded ancestry after acknowledged paid anchors')
        uniq={}
        for d in observed_deals:
            if not isinstance(d,ObservedDeal) or not d.history_verified:
                raise ValueError('only externally verified broker deal history is accepted')
            old=uniq.get(d.deal_id)
            if old is not None and old!=d:
                raise ValueError('conflicting duplicate broker deal in snapshot')
            uniq[d.deal_id]=d
        clone=VerifiedMT5PositionLedger0264(account_mode=self.account_mode,
                   symbol_verified=self.symbol_verified,account_cash_verified=False)
        clone.requests=self.requests.copy()
        clone.checks=self.checks.copy()
        clone.sent=self.sent.copy()
        for x in sorted(uniq.values(),key=lambda z:(z.time_ms, 0 if z.kind=='IN' else 1,z.deal_id)):
            clone.stage_history_deal(x)
        if clone.staged:
            raise ValueError('missing order or position evidence in broker history snapshot')
        if clone.cash!=D(observed_cash_delta):
            raise ValueError('history net does not match observed broker account cash delta')
        self.positions=clone.positions
        self.applied=clone.applied
        self.staged={}
        self.waiting_reasons={}
        self.cash=clone.cash
        self._last_applied_ms=clone._last_applied_ms
        self.account_cash_verified=True
        return {'deals':len(self.applied),'reconciled_cash':str(self.cash),
                'account_cash_verified_from_history_snapshot':True}

    def audited_paid_position(self,position_id:int):
        self._verified()
        if not self.account_cash_verified:
            raise ValueError('actual account cash/commission reconciliation missing')
        p=self.positions[position_id]
        if not p.complete or p.opened!=LOT:
            raise ValueError('position not completely opened/closed at verified .01 lots')
        if self.staged:
            raise ValueError('unprocessed broker deal evidence cannot certify paid result')
        return p
    def summary(self):
        return {'position_cash_from_history':str(self.cash),
                'observed_deals':len(self.applied),'unresolved_deals':len(self.staged),
                'positions':len(self.positions),
                'broker_metadata_verified':self.symbol_verified,
                'broker_account_cash_reconciled':self.account_cash_verified,
                'actual_mt5_connection':False,
                'quote_price_never_proves_fill':True}
