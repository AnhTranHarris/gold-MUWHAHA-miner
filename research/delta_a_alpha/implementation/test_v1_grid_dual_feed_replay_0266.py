"""GRID0266 original feed-provenance and current-V1 replay gates."""
import unittest
from pathlib import Path
from v1_grid_dual_feed_replay_0266 import (
    FeedKind,StampedMarketTick,SourceLockedV1ResearchReplay,
    stream_dukas_original,stream_coinexx_r9_original,_exact_scaled_price,
)
from v1_four_session_architecture import FourSessionV1
from v1_vertical_grid import Quote

UTC=1776214800666

def fake(feed=FeedKind.DUKAS,n=0,ms=UTC,ev=None):
    return StampedMarketTick(feed,n,ms,4839670,4841590,ev)

class DualFeedContracts(unittest.TestCase):
    def test_current_actual_FourSessionV1_binds_real_source_once(self):
        engine=FourSessionV1()
        replay=engine.bind_research_feed(kind=FeedKind.COINEXX_REAL,permission=lambda _:False)
        replay.on_observation(fake(FeedKind.COINEXX_REAL))
        self.assertEqual(engine.events['ticks'],1)
        self.assertEqual(engine.result()['research_feed_provenance']['feed'],
                          'COINEXX_R9_REAL_TESTER')
        self.assertEqual(engine.result()['broker_event_evidence']['confirmed_deals'],0)
        with self.assertRaises(RuntimeError):
            engine.on_tick(Quote(UTC+1,4839670,4841590))
        with self.assertRaises(RuntimeError):
            engine.bind_research_feed(kind=FeedKind.DUKAS,permission=lambda _:False)

    def test_source_cannot_bind_after_raw_quotes(self):
        engine=FourSessionV1()
        engine.on_tick(Quote(UTC,4839670,4841590))
        with self.assertRaises(RuntimeError):
            engine.bind_research_feed(kind=FeedKind.DUKAS,permission=lambda _:False)

    def test_REAL_SYNTH_source_identity_is_separate(self):
        engine=FourSessionV1()
        bound=engine.bind_research_feed(kind=FeedKind.COINEXX_REAL,permission=lambda _:False)
        with self.assertRaises(ValueError):
            bound.on_observation(fake(FeedKind.COINEXX_SYNTH))
        self.assertEqual(engine.events['ticks'],0)

    def test_logged_ENTRY_is_not_broker_DEAL_ADD(self):
        engine=FourSessionV1()
        bound=engine.bind_research_feed(kind=FeedKind.COINEXX_REAL,permission=lambda _:False)
        bound.on_observation(fake(FeedKind.COINEXX_REAL,ev='ENTRY_BUY'))
        self.assertEqual(engine.result()['broker_event_evidence']['confirmed_deals'],0)
        self.assertEqual(engine.events['filled'],0)

    def test_spread_is_actual_quote_not_fixed_calibration(self):
        a=fake()
        self.assertEqual((a.ask_raw-a.bid_raw)/1000,1.92)

    def test_duplicate_same_ms_distinct_order_ok(self):
        engine=FourSessionV1()
        bound=engine.bind_research_feed(kind=FeedKind.DUKAS,permission=lambda _:False)
        bound.on_observation(fake(FeedKind.DUKAS,0,UTC))
        bound.on_observation(fake(FeedKind.DUKAS,1,UTC))
        self.assertEqual(engine.events['ticks'],2)

    def test_order_reversal_rejected(self):
        engine=FourSessionV1()
        bound=engine.bind_research_feed(kind=FeedKind.DUKAS,permission=lambda _:False)
        bound.on_observation(fake(FeedKind.DUKAS,0,UTC))
        with self.assertRaises(ValueError):
            bound.on_observation(fake(FeedKind.DUKAS,1,UTC-1))

    def test_unknown_permission_fails_closed(self):
        engine=FourSessionV1()
        bound=engine.bind_research_feed(kind=FeedKind.DUKAS,permission=lambda _:None)
        with self.assertRaises(TypeError):bound.on_observation(fake())
        self.assertEqual(engine.events['ticks'],0)

    def test_disabled_by_default_even_true_availability(self):
        engine=FourSessionV1(leverage=500)
        bound=engine.bind_research_feed(kind=FeedKind.DUKAS,permission=lambda _:True)
        bound.on_observation(fake())
        self.assertEqual(engine.events['filled'],0)
        self.assertEqual(bound.provenance()['live_mt5_deals_confirmed_by_feed'],0)

    def test_exact_price_rejects_thousandth_excess(self):
        with self.assertRaises(ValueError):_exact_scaled_price('4841.12345','bid')
        with self.assertRaises(ValueError):_exact_scaled_price('NaN','bid')

    def test_no_august(self):
        with self.assertRaises(PermissionError):
            next(stream_dukas_original('/tmp/XAUUSD_DUKAS_2026_08_ticks.csv.gz'))
        with self.assertRaises(PermissionError):
            next(stream_coinexx_r9_original('/tmp/R9_REAL_2026-08-01_ticks.csv.gz',
                                            kind=FeedKind.COINEXX_REAL))

    def test_observed_Coinexx_day_if_mounted(self):
        p=Path('/mnt/data/R9_REAL_2026-04-15_ticks.csv.gz')
        if not p.is_file():self.skipTest('original day not mounted on GitHub CI')
        a=list(stream_coinexx_r9_original(p,kind=FeedKind.COINEXX_REAL,maximum=3000))
        self.assertEqual(len(a),3000)
        self.assertEqual(a[0].utc_ms,UTC)
        self.assertEqual(a[0].ask_raw-a[0].bid_raw,1920)

    def test_observed_Dukascopy_if_mounted(self):
        import glob
        ps=glob.glob('/mnt/data/XAUUSD_DUKAS_2026_04_ticks.csv*.gz')
        if not ps:self.skipTest('original month not mounted on GitHub CI')
        a=list(stream_dukas_original(ps[0],maximum=20))
        self.assertEqual(len(a),20)
        self.assertEqual(a[0].bid_raw,4695965)

if __name__=='__main__':unittest.main()
