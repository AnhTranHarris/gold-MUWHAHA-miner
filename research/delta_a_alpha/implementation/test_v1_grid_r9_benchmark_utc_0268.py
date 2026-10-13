"""Regression: R9 roles, authentic Coinexx/Dukas UTC ticks, no fabricated chart offsets."""
import unittest,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).parent))
from v1_grid_r9_benchmark_utc_0268 import (
 CandleClock, utc_partition_labels,verify_coinexx_utc_text,
 require_runtime_feature_names,R9_SYNTH_IDEAL_PERIODS,R9_OVERFIT_PER_TRADE_TEACHER)
from v1_vertical_grid import CompletedBars,CleanV1Engine,Quote
from v1_four_session_architecture import FourSessionV1
from v1_grid_dual_feed_replay_0266 import stream_coinexx_r9_original,FeedKind

MS=lambda y,m,d,h,minute=0,sec=0:int(datetime(y,m,d,h,minute,sec,tzinfo=timezone.utc).timestamp()*1000)

class CanonicalUTCAlignmentTest(unittest.TestCase):
 def test_r9_reference_roles_not_swapped(self):
  self.assertEqual(R9_SYNTH_IDEAL_PERIODS,('UTC_DAY','UTC_ISO_WEEK','UTC_MONTH'))
  self.assertEqual(R9_OVERFIT_PER_TRADE_TEACHER,('entry','hold','exit','profit','drawdown','gross_loss'))
  self.assertTrue(require_runtime_feature_names(['spread','prev_H1_close']))
  with self.assertRaises(ValueError):require_runtime_feature_names(['spread','future_mfe'])
 def test_utc_prices_ticks_not_chart_offset(self):
  t=MS(2026,4,15,1,13,5)+666
  a=CandleClock()
  self.assertEqual(a.start_ms(t,'M1'),MS(2026,4,15,1,13))
  self.assertEqual(a.start_ms(t,'H1'),MS(2026,4,15,1))
  self.assertEqual(a.start_ms(t,'H4'),MS(2026,4,15,0))
  self.assertEqual(a.start_ms(t,'D1'),MS(2026,4,15,0))
 def test_nondivisor_M7_resets_utc_midnight(self):
  a=CandleClock()
  self.assertEqual(a.start_ms(MS(2026,4,15,0,5),'M7'),MS(2026,4,15,0))
  self.assertEqual(a.start_ms(MS(2026,4,15,23,59),'M7'),MS(2026,4,15,23,55))
  self.assertEqual(a.end_ms(MS(2026,4,15,23,59),'M7'),MS(2026,4,16,0))
 def test_explicit_chart_phase_requires_actual_evidence(self):
  with self.assertRaises(ValueError):CandleClock(mode='MT5_CHART_PARITY',offset_minutes=120)
  with self.assertRaises(ValueError):CandleClock(mode='UTC_RESEARCH',offset_minutes=120)
  with self.assertRaises(ValueError):CandleClock(mode='MT5_CHART_PARITY',offset_minutes=121,evidence_id='proof',valid_from_ms=1,valid_until_ms=1)
 def test_chart_phase_is_separate_from_raw_tick_time(self):
  t=MS(2026,4,15,1,13)
  e=CandleClock(mode='MT5_CHART_PARITY',offset_minutes=120,
     evidence_id='test_observed_mt5_h4',valid_from_ms=t-1000,valid_until_ms=t+3600000)
  self.assertEqual(e.start_ms(t,'H4'),MS(2026,4,14,22))
  self.assertEqual(e.start_ms(t,'M1'),MS(2026,4,15,1,13))
  with self.assertRaises(ValueError):e.start_ms(t+7200000,'H4')
 def test_real_DST_session_clock_unchanged(self):
  from v1_vertical_grid import session_frame
  before=session_frame(MS(2026,3,8,6,59));after=session_frame(MS(2026,3,8,7,1))
  self.assertEqual(before.local_clocks['NEW_YORK'].hour,1)
  self.assertEqual(after.local_clocks['NEW_YORK'].hour,3)
 def test_coinexx_schema_timestamp_fields_strict(self):
  t=MS(2026,4,15,1,13,5)+666
  verify_coinexx_utc_text(t,'2026.04.15 01:13:05','2026.04.15 01:13','5')
  for pair in [('2026.04.15 03:13:05','2026.04.15 01:13','5'),
               ('2026.04.15 01:13:05','2026.04.15 03:13','5'),
               ('2026.04.15 01:13:05','2026.04.15 01:13','6')]:
   with self.assertRaises(ValueError):verify_coinexx_utc_text(t,*pair)
 def test_one_completed_H4_research_bar_zero_utc(self):
  c=CompletedBars()
  a=MS(2026,4,15,3,59,59);b=MS(2026,4,15,4)
  c.on_quote(Quote(a,4800000,4800100));c.on_quote(Quote(b,4801000,4801100))
  self.assertEqual(c.snapshot(Quote(b,4801000,4801100))['H4'].start_ms,MS(2026,4,15,0))
 def test_engine_current_source_clock_and_roles(self):
  x=FourSessionV1();r=x.result()
  self.assertEqual(r['candle_clock_mode'],'UTC_RESEARCH')
  self.assertEqual(r['research_benchmark_roles']['python_tick_execution_source'],'DUKASCOPY_ORIGINAL')
  self.assertFalse(r['research_benchmark_roles']['overfit_as_live_execution_feature'])
 def test_real_Coinexx_complete_day_source_if_available(self):
  p=Path('/mnt/data/R9_REAL_2026-04-15_ticks.csv.gz')
  if not p.exists():self.skipTest('not bundled in GitHub checkout')
  rows=0
  for q in stream_coinexx_r9_original(p,kind=FeedKind.COINEXX_REAL):
   if rows==0:self.assertEqual(q.utc_ms,MS(2026,4,15,1)+666)
   rows+=1
  self.assertEqual(rows,365469)
 def test_jan_dukas_source_if_available(self):
  import glob
  p=glob.glob('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv*.gz')
  if not p:self.skipTest('raw Jan not mounted on GitHub CI')
  from v1_grid_dual_feed_replay_0266 import stream_dukas_original
  q=next(stream_dukas_original(p[0],maximum=1))
  self.assertEqual(CandleClock().start_ms(q.utc_ms,'M1')%60000,0)
 def test_partition_labels_are_utc_not_pc(self):
  d=utc_partition_labels(MS(2026,3,1,0,0))
  self.assertEqual(d['UTC_DAY'],'2026-03-01')
  self.assertEqual(d['UTC_MONTH'],'2026-03')
  self.assertTrue(d['UTC_ISO_WEEK'].startswith('2026-W'))
if __name__=='__main__':unittest.main()
