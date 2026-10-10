"""Clean owner-law L0/L1/L2 and L7 safe-idle contract tests, no P&L claims."""
import unittest
from datetime import datetime,timezone
from v1_vertical_grid import Quote,CleanV1Engine,session_frame

def ms(x):return int(datetime.fromisoformat(x).astimezone(timezone.utc).timestamp()*1000)

class V1CleanContracts(unittest.TestCase):
    def test_utc_and_local_clocks_all_present(self):
        f=session_frame(ms('2026-03-20T13:00:00+00:00'))
        self.assertEqual(set(f.local_clocks),{'SYDNEY','TOKYO','LONDON','NEW_YORK'})
        self.assertEqual(f.utc.hour,13)
        self.assertEqual(f.local_clocks['LONDON'].hour,13)
        self.assertEqual(f.local_clocks['NEW_YORK'].hour,9)
        self.assertEqual(f.suggested_geometry,'LONDON_NEW_YORK_OVERLAP')
        self.assertFalse(f.broker_trading_confirmed)
    def test_us_europe_mismatched_dst_weeks(self):
        before=session_frame(ms('2026-03-06T12:30:00+00:00'))
        between=session_frame(ms('2026-03-20T12:30:00+00:00'))
        after=session_frame(ms('2026-04-03T12:30:00+00:00'))
        self.assertEqual(before.local_clocks['NEW_YORK'].hour,7)
        self.assertEqual(between.local_clocks['NEW_YORK'].hour,8)
        self.assertEqual(after.local_clocks['LONDON'].hour,13)
        self.assertEqual(between.local_clocks['LONDON'].hour,12)
        self.assertNotIn('NEW_YORK',before.open_desks)
        self.assertIn('NEW_YORK',between.open_desks)
    def test_sydney_dst_tokyo_constant(self):
        march=session_frame(ms('2026-03-20T00:00:00+00:00'))
        june=session_frame(ms('2026-06-19T00:00:00+00:00'))
        self.assertEqual(march.local_clocks['TOKYO'].hour,june.local_clocks['TOKYO'].hour)
        self.assertEqual(march.local_clocks['SYDNEY'].hour,11)
        self.assertEqual(june.local_clocks['SYDNEY'].hour,10)
        self.assertEqual(march.suggested_geometry,'SYDNEY_TOKYO_OVERLAP')
    def test_calendar_label_does_not_invent_broker_closed(self):
        f=session_frame(ms('2026-12-25T13:00:00+00:00'),holiday_labels=('CHRISTMAS',))
        self.assertEqual(f.status,'OBSERVED_QUOTE')
        self.assertFalse(f.broker_trading_confirmed)
        self.assertIn('CHRISTMAS',f.regional_holiday_labels)
    def test_completed_bars_do_not_repaint_or_leak(self):
        e=CleanV1Engine()
        f0=e.on_tick(Quote(ms('2026-03-20T12:59:59+00:00'),4500000,4500100))
        self.assertIsNone(f0.l2_completed_bars['M5'])
        f1=e.on_tick(Quote(ms('2026-03-20T13:00:00+00:00'),4500010,4500110))
        m5=f1.l2_completed_bars['M5']
        self.assertIsNotNone(m5)
        self.assertLessEqual(m5.end_ms,f1.quote.time_ms_utc)
        self.assertEqual(m5.close_raw,4500000)
        self.assertEqual(m5.quote_count,1)
    def test_l0_out_of_order_and_crossed_bidask_blocked(self):
        e=CleanV1Engine()
        e.on_tick(Quote(1000,4320000,4320100))
        with self.assertRaises(ValueError):e.on_tick(Quote(999,4320000,4320100))
        with self.assertRaises(ValueError):e.on_tick(Quote(1000,4320100,4320000))
    def test_missing_downstream_sources_fail_closed_no_funded_orders(self):
        e=CleanV1Engine()
        for i in range(5):
            f=e.on_tick(Quote(1767500000000+i*300000,4320000,4320100),broker_trading_confirmed=True)
            self.assertEqual(f.l7_governor_state,'DENY_ALL_NEW_RISK')
            self.assertEqual(f.broker_order_count,0)
            self.assertEqual(f.l5_native_route,'NO_CERTIFIED_ROUTE')
        self.assertEqual(e.num_quotes,5)
        self.assertEqual(e.funded_orders,0)

if __name__=='__main__':unittest.main()
