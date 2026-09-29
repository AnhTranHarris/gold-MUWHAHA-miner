"""Independent unit tests; intentionally no market data and no brokerage orders."""
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory
from BETA_015_PROP_POLICY_V1 import Policy,PropRiskGuard,PolicyViolation

ROOT=Path(__file__).parent
POLICY=ROOT/'BETA_015_PROP_POLICY_V1.json'
def utc(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
class TestPolicy(unittest.TestCase):
    def setUp(self):self.p=Policy.from_json(POLICY);self.g=PropRiskGuard(self.p);self.t=utc('2026-01-05T16:00:00Z')
    def test_load_and_lock(self):
        self.assertEqual(self.p.fixed_lots,.01);self.assertEqual(self.p.fee_side,.01)
        raw=json.loads(POLICY.read_text());raw['daily_hard_loss_usd']=5500
        with TemporaryDirectory() as td:
            path=Path(td)/'policy.json';path.write_text(json.dumps(raw))
            with self.assertRaises(PolicyViolation):Policy.from_json(path)
    def test_naive_time_disallowed(self):
        with self.assertRaises(PolicyViolation):self.g.on_tick(datetime(2026,1,5),3999,4000)
    def test_bad_spread_disallowed(self):
        with self.assertRaises(PolicyViolation):self.g.on_tick(self.t,4100,4099)
    def test_one_position_and_fixed_lot(self):
        self.g.enter(self.t,4000,4000.2,1,3999.8,broker_trading_enabled=True)
        self.assertFalse(self.g.can_enter(self.t,4000,4000.2,1,3999.8,broker_trading_enabled=True)[0]);self.assertEqual(self.g.position.lots,.01)
    def test_reject_wrong_lot(self):
        self.assertEqual(self.g.can_enter(self.t,4000,4000.2,1,3999.8,lots=.02,broker_trading_enabled=True)[1],'FIXED_LOT_ONLY')
    def test_fee_profit_calibration(self):
        self.g.enter(self.t,4000,4000.2,1,3999.8,broker_trading_enabled=True)
        pnl=self.g.close_position(self.t+timedelta(seconds=1),4001.2,4001.3)
        self.assertAlmostEqual(pnl,.98,places=8)
        self.assertAlmostEqual(self.g.balance,100000.98,places=8)
        self.assertEqual(self.g.audit()['wins'],1)
    def test_cost_mark_on_entry(self):
        self.g.enter(self.t,4000,4000.2,1,3999.8,broker_trading_enabled=True)
        self.assertAlmostEqual(self.g.equity,99999.79,places=6)
    def test_stop_risk_veto(self):
        self.assertEqual(self.g.can_enter(self.t,4000,4000.2,1,3700,broker_trading_enabled=True)[1],'PLANNED_RISK_LIMIT')
    def test_news_when_verified_only(self):
        self.assertTrue(self.g.can_enter(self.t,4000,4000.2,1,3999.8,is_high_impact_window=True,broker_trading_enabled=True)[0])
        self.assertEqual(self.g.can_enter(self.t,4000,4000.2,1,3999.8,economic_calendar_certified=True,is_high_impact_window=True,broker_trading_enabled=True)[1],'VERIFIED_HIGH_IMPACT_NEWS_WINDOW')
    def test_broker_closed(self):
        self.assertEqual(self.g.can_enter(self.t,4000,4000.2,1,3999.8,broker_trading_enabled=False)[1],'BROKER_SESSION_UNAVAILABLE')
    def test_friday_pause_and_weekend(self):
        self.assertEqual(self.g.can_enter(utc('2026-01-09T21:56:00Z'),4000,4000.2,1,3999.8,broker_trading_enabled=True)[1],'ROLLOVER_OR_FRIDAY_CLOSE')
        self.assertEqual(self.g.can_enter(utc('2026-01-10T10:00:00Z'),4000,4000.2,1,3999.8,broker_trading_enabled=True)[1],'WEEKEND_OR_SUNDAY_PREOPEN')
    def test_sunday_after_open_is_eligible_when_broker_is_open(self):
        allow,reason=self.g.can_enter(utc('2026-01-11T22:06:00Z'),4000,4000.2,1,3999.8,broker_trading_enabled=True)
        self.assertTrue(allow,reason)
    def test_sunday_before_open_blocked(self):
        self.assertEqual(self.g.can_enter(utc('2026-01-11T21:00:00Z'),4000,4000.2,1,3999.8,broker_trading_enabled=True)[1], 'WEEKEND_OR_SUNDAY_PREOPEN')
    def test_dst_17_ny_reset(self):
        self.g.on_tick(utc('2026-03-09T20:59:59Z'),4000,4000.2);b=self.g.current_day
        self.g.on_tick(utc('2026-03-09T21:00:00Z'),4000,4000.2);self.assertNotEqual(b,self.g.current_day)
    def test_winter_17_ny_reset(self):
        self.g.on_tick(utc('2026-01-05T21:59:59Z'),4000,4000.2);b=self.g.current_day
        self.g.on_tick(utc('2026-01-05T22:00:00Z'),4000,4000.2);self.assertNotEqual(b,self.g.current_day)
    def test_soft_pause_daily_persists_then_resets(self):
        self.g.on_tick(self.t,4000,4000.2)
        self.g.balance=95999.;res=self.g.on_tick(self.t+timedelta(seconds=5),4000,4000.2)
        self.assertTrue(res.soft_locked);self.assertFalse(res.hard_locked)
        self.assertFalse(self.g.can_enter(self.t+timedelta(seconds=6),4000,4000.2,1,3999.8,broker_trading_enabled=True)[0])
        self.g.on_tick(utc('2026-01-05T22:00:00Z'),4000,4000.2)
        self.assertFalse(self.g.soft_locked)
    def test_hard_loss_forces_close(self):
        self.g.enter(self.t,4000,4000.2,1,3999.8,broker_trading_enabled=True)
        self.g.balance=94999.99
        v=self.g.on_tick(self.t+timedelta(seconds=1),4000,4000.2)
        self.assertTrue(v.hard_locked);self.assertTrue(v.closed_by_risk);self.assertIsNone(self.g.position);self.assertFalse(v.terminated)
    def test_overall_loss_permanent(self):
        self.g.on_tick(self.t,4000,4000.2)
        self.g.balance=89999.;v=self.g.on_tick(self.t+timedelta(seconds=1),4000,4000.2)
        self.assertTrue(v.terminated);self.assertEqual(self.g.can_enter(utc('2026-02-02T16:00:00Z'),4000,4000.2,1,3999.8,broker_trading_enabled=True)[1],'OVERALL_TERMINATED')
    def test_short_pnl(self):
        self.g.enter(self.t,4000,4000.2,-1,4000.6,broker_trading_enabled=True)
        p=self.g.close_position(self.t+timedelta(seconds=1),3999.0,3999.2)
        self.assertAlmostEqual(p,.78,places=8)
    def test_monotonic(self):
        self.g.on_tick(self.t,4000,4000.2)
        with self.assertRaises(PolicyViolation):self.g.on_tick(self.t-timedelta(seconds=1),4000,4000.2)
    def test_broker_session_must_be_explicitly_authorized(self):
        self.assertEqual(self.g.can_enter(self.t,4000,4000.2,1,3999.8)[1],"BROKER_SESSION_UNAVAILABLE")
    def test_zero_trades_after_floor(self):
        self.g.balance=89000;self.g.on_tick(self.t,4000,4000.2)
        self.assertFalse(self.g.can_enter(self.t+timedelta(seconds=1),4000,4000.2,1,3999.8,broker_trading_enabled=True)[0]);self.assertEqual(self.g.trades,0)
if __name__=='__main__':unittest.main(verbosity=2)