"""C2D3Q deterministic gate for fully paid BidAsk ledger audits; no raw gzip in CI."""
import unittest
from types import SimpleNamespace
from datetime import datetime, timezone
from audit_full_jan_feb_native_source_funded_033 import ledger_monthly,validate_closed_account,EXPECTED_QUOTE_TOTAL,EXPECTED_SOURCE_ENTRIES


def exit_(id, day,net,source='ORIG_SOURCE_26'):
    return SimpleNamespace(position_id=id,time_ms=int(datetime(2026,1 if day==1 else 2,3,tzinfo=timezone.utc).timestamp()*1000),exit_raw=100000,net_usd=float(net),source=source)

class DummyAccount:
    def __init__(self,closes=None,events=EXPECTED_SOURCE_ENTRIES,pd=3):
        self.closes=closes if closes is not None else [exit_(1,1,4),exit_(2,2,-2),exit_(3,2,5)]
        self.closed=self.closes
        self.positions={}
        self.total_quotes=EXPECTED_QUOTE_TOTAL
        self.feed=SimpleNamespace(bridge=SimpleNamespace(source_events=events,physical_callbacks=pd))
        self.engine=SimpleNamespace(closed=self.closes,positions=self.positions,score=self.score)
    def score(self):
        pnl=[c.net_usd for c in self.closes]
        gross=sum(max(x,0) for x in pnl)
        loss=sum(min(x,0) for x in pnl)
        return dict(net=round(sum(pnl),3),gross_profit=round(gross,3),gross_loss=round(loss,3),
          profit_factor=gross/(-loss) if loss else None,month_blind=True,combined_max_orders_sec=10,
          funded_recovery_count=0,model='DETERMINISTIC_BIDASK_IDEALIZED_RESEARCH_KERNEL_NOT_V1_SOURCE_PARITY')

class SourcePaidLedgerGate(unittest.TestCase):
    def test_close_utc_post_trade_only(self):
        a=ledger_monthly([exit_(1,1,4),exit_(2,2,-2),exit_(3,2,5)])
        self.assertEqual(list(a),['2026-01','2026-02'])
        self.assertEqual(a['2026-01']['net'],4)
        self.assertEqual(a['2026-02']['gross_loss'],-2)
        self.assertEqual(a['2026-02']['trades'],2)
    def test_exact_paid_source_and_gross(self):
        score,m=validate_closed_account(DummyAccount())
        self.assertEqual(score['net'],7)
        self.assertEqual(m['2026-02']['net'],3)
    def test_source_event_loss_detected(self):
        with self.assertRaises(AssertionError):validate_closed_account(DummyAccount(events=EXPECTED_SOURCE_ENTRIES-1))
    def test_double_closed_position_detected(self):
        with self.assertRaises(AssertionError):validate_closed_account(DummyAccount([exit_(1,1,4),exit_(1,2,-2)],pd=2))
    def test_unfunded_close_rejected(self):
        with self.assertRaises(AssertionError):validate_closed_account(DummyAccount(pd=2))
    def test_non_monthblind_rejected(self):
        x=DummyAccount(); f=x.engine.score;x.engine.score=lambda:{**f(),'month_blind':False}
        with self.assertRaises(AssertionError):validate_closed_account(x)
    def test_over_budget_rejected(self):
        x=DummyAccount(); f=x.engine.score;x.engine.score=lambda:{**f(),'combined_max_orders_sec':11}
        with self.assertRaises(AssertionError):validate_closed_account(x)
    def test_quote_truncation_detected(self):
        x=DummyAccount();x.total_quotes-=1
        with self.assertRaises(AssertionError):validate_closed_account(x)
    def test_actual_funded_open_retained_as_incomplete(self):
        x=DummyAccount();x.positions[99]=object();x.feed.bridge.physical_callbacks+=1
        with self.assertRaises(AssertionError):validate_closed_account(x)
    def test_no_month_attribution_outside_original_data(self):
        x=DummyAccount([exit_(1,1,4),SimpleNamespace(position_id=2,time_ms=int(datetime(2026,3,3,tzinfo=timezone.utc).timestamp()*1000),exit_raw=1,net_usd=-1,source='x')],pd=2)
        with self.assertRaises(AssertionError):validate_closed_account(x)

if __name__=='__main__':unittest.main()
