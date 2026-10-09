import unittest
from economic_scorecard_033 import reporting_only_scorecards
from v1_funded_core_033 import Close
class Report(unittest.TestCase):
    def test_hour_day_week_month_year_are_post_trade_only(self):
        def c(ts,p):return Close(1,ts,100000,p,1200,'TIME','SRC','L3',None)
        from datetime import datetime,timezone
        def ms(t):return int(datetime.fromisoformat(t).replace(tzinfo=timezone.utc).timestamp()*1000)
        r=reporting_only_scorecards([c(ms('2026-01-31T23:59:00'),1.0),c(ms('2026-02-01T00:02:00'),-.2)])
        self.assertEqual(r['trade']['trades'],2)
        self.assertEqual(len(r['day']),2);self.assertEqual(len(r['month']),2)
        self.assertEqual(len(r['year']),1);self.assertEqual(r['trade']['gross_loss'],-.2)
        self.assertAlmostEqual(r['trade']['profit_factor'],5.0)
if __name__=='__main__':unittest.main()