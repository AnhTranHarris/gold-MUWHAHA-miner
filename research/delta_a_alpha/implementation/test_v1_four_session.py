import sys,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from v1_vertical_grid import Quote, ClosedBar
from v1_session_broker_clock import BrokerClock,ClockNotCalibrated,local_clocks,server_wall_quote_to_utc_ms,mt5_tick_utc_ms
from v1_four_session_architecture import FourSessionV1,DESKS,Pending,Opportunity,Position

UTC=timezone.utc
def ms(s): return int(datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()*1000)
def q(t,price=4400,spread=.20):return Quote(t,int(price*1000),int((price+spread)*1000))
class TestClocks(unittest.TestCase):
 def test_4_distinct_civil_clocks(self):
  local=local_clocks(ms('2026-03-16T13:00:00Z'))
  self.assertEqual(set(local),set(DESKS))
  self.assertEqual(local['LONDON'].hour,13)
  self.assertEqual(local['NEW_YORK'].hour,9)
  self.assertEqual(local['TOKYO'].hour,22)
 def test_us_uk_dst_mismatch(self):
  a=local_clocks(ms('2026-03-16T13:00:00Z'))
  b=local_clocks(ms('2026-04-06T13:00:00Z'))
  self.assertEqual(a['LONDON'].hour,13)
  self.assertEqual(b['LONDON'].hour,14)
  self.assertEqual(a['NEW_YORK'].hour,b['NEW_YORK'].hour)
 def test_server_utc_plus2_and_plus3_recalibrates(self):
  c=BrokerClock()
  t=datetime(2026,1,20,12,tzinfo=UTC)
  with self.assertRaises(ClockNotCalibrated):c.as_utc(datetime(2026,1,20,14),t)
  for i in range(3):
   stamp=t+timedelta(seconds=i)
   c.observe((stamp+timedelta(hours=2)).replace(tzinfo=None),stamp)
  self.assertEqual(c.as_utc(datetime(2026,1,20,14,0,3),t+timedelta(seconds=3)),t+timedelta(seconds=3))
  nexttime=t+timedelta(days=90)
  c.observe((nexttime+timedelta(hours=3)).replace(tzinfo=None),nexttime)
  with self.assertRaises(ClockNotCalibrated):c.as_utc((nexttime+timedelta(hours=3)).replace(tzinfo=None),nexttime)
  for i in (1,2):
   st=nexttime+timedelta(seconds=i)
   c.observe((st+timedelta(hours=3)).replace(tzinfo=None),st)
  self.assertEqual(c.state.offset_seconds,10800)
 def test_stale_or_wrong_clock_is_rejected(self):
  c=BrokerClock(max_age_ms=1000);t=datetime(2026,1,20,12,tzinfo=UTC)
  for i in range(3):
   st=t+timedelta(milliseconds=200*i)
   c.observe((st+timedelta(hours=2)).replace(tzinfo=None),st)
  with self.assertRaises(ClockNotCalibrated):c.as_utc(datetime(2026,1,20,14,1),t+timedelta(minutes=1))
  with self.assertRaises(ClockNotCalibrated):c.as_utc(datetime(2026,1,20,15),t+timedelta(milliseconds=500))
 def test_server_shift_never_shifts_true_session(self):
  t=datetime(2026,3,16,13,tzinfo=UTC)
  values=[]
  for off in (2,3):
   c=BrokerClock()
   for i in range(3):
    u=t+timedelta(seconds=i)
    c.observe((u+timedelta(hours=off)).replace(tzinfo=None),u)
   u=t+timedelta(seconds=3)
   wall=(u+timedelta(hours=off)).replace(tzinfo=None)
   values.append(server_wall_quote_to_utc_ms(c,wall,u))
  self.assertEqual(values[0],values[1])
  self.assertEqual(local_clocks(values[0])['NEW_YORK'].hour,9)
 def test_mt5_epoch_is_not_double_converted(self):
  t=ms('2026-04-06T15:00:00Z')
  self.assertEqual(mt5_tick_utc_ms(t),t)

 def test_unpaired_high_uncertainty_rejected(self):
  with self.assertRaises(ClockNotCalibrated):BrokerClock().observe(datetime(2026,2,10),datetime(2026,2,10,tzinfo=UTC),uncertainty_ms=800)

class TestFullFunnel(unittest.TestCase):
 def test_four_profiles_each_complete_layer(self):
  for desk, sp in DESKS.items():
   self.assertEqual(sp.name,desk)
   self.assertTrue(all(isinstance(getattr(sp,k),str) and getattr(sp,k) for k in ('l1_opportunity','l2_structure_role','l3_geometry','l4_regime_quality','l5_trend_quality','l6_failure_management','l7_risk_profile')))
   self.assertEqual(sp.cap>=1,True)
 def test_session_only_never_places_order(self):
  e=FourSessionV1(leverage=500,broker_session_confirmed=True)
  t=ms('2026-06-02T13:00:00Z')
  for i in range(20):e.on_tick(q(t+i*500,4400+i*.2),simulate_broker=True,broker_tradable=True)
  self.assertEqual(e.events['filled'],0)
  self.assertEqual(e.events['l3_proposals'],0) # MTF warmup missing
 def test_unknown_broker_is_never_funded(self):
  e=FourSessionV1(leverage=500)
  t=ms('2026-06-02T13:00:00Z')
  for i in range(10):e.on_tick(q(t+i*1000),simulate_broker=True)
  self.assertEqual(e.events['filled'],0)
 def test_no_lot_scaling(self):
  e=FourSessionV1(leverage=500)
  self.assertEqual(e.lot,.01)
  self.assertEqual(e.global_max_open,2)
 def test_delayed_fill_never_at_signal_price(self):
  e=FourSessionV1(leverage=500,broker_session_confirmed=True,latency_ms=1000)
  t=ms('2026-06-02T13:00:00Z');o=Opportunity(t,'LONDON',1,4400,4400.2,'TEST',t+5000,'LONDON',4400)
  e.pending.append(Pending(o,t+1000,t+5000))
  e.on_tick(q(t,4400),simulate_broker=False,broker_tradable=True)
  self.assertEqual(e.events['filled'],0)
  e.on_tick(q(t+1200,4400.7),simulate_broker=False,broker_tradable=True)
  # 0.7 slippage within London's gap 1.25
  self.assertEqual(e.events['filled'],1)
  self.assertAlmostEqual(e.positions[0].entry_price,4400.9,places=5)
 def test_late_gap_rejected(self):
  e=FourSessionV1(leverage=500,broker_session_confirmed=True)
  t=ms('2026-06-02T13:00:00Z');o=Opportunity(t,'LONDON',1,4400,4400.2,'TEST',t+1000,'LONDON',4400)
  e.pending.append(Pending(o,t+2000,t+1000))
  e.on_tick(q(t+5000,4405),simulate_broker=False,broker_tradable=True)
  self.assertEqual(e.events['filled'],0)
  self.assertEqual(e.events['expired_latency'],1)
 def test_pending_margin_fail_close(self):
  e=FourSessionV1(starting_cash=100,leverage=None,broker_session_confirmed=True)
  t=ms('2026-06-02T13:00:00Z');o=Opportunity(t,'SYDNEY',1,4400,4400.2,'TEST',t+5000,'ASIA',4400)
  e.pending.append(Pending(o,t,t+5000))
  e.on_tick(q(t,4400),simulate_broker=True,broker_tradable=True)
  self.assertEqual(e.events['filled'],0)
  self.assertEqual(e.events['unverified_broker_margin'],1)
 def test_one_funded_order_per_tick(self):
  e=FourSessionV1(leverage=500,broker_session_confirmed=True)
  t=ms('2026-06-02T13:00:00Z')
  for d in ('LONDON','NEW_YORK'):
   o=Opportunity(t,d,1,4400,4400.2,'TEST',t+3000,d,4400)
   e.pending.append(Pending(o,t,t+3000))
  e.on_tick(q(t,4400),simulate_broker=False,broker_tradable=True)
  self.assertEqual(e.events['filled'],1)
  self.assertEqual(e.events['one_order_per_tick'],1)
 def test_L6_warning_only_after_funded_bad_move(self):
  e=FourSessionV1(leverage=500,broker_session_confirmed=True)
  t=ms('2026-06-02T13:00:00Z')
  e.positions.append(Position(1,'SYDNEY',4400,t,4396.6,4402.8))
  e.on_tick(q(t+2000,4398),simulate_broker=False)
  self.assertEqual(e.events['l6_warning'],1)
  self.assertTrue(e.positions[0].warning)
 def test_out_of_order_rejected(self):
  e=FourSessionV1();t=ms('2026-06-02T13:00:00Z')
  e.on_tick(q(t))
  with self.assertRaises(ValueError):e.on_tick(q(t-1))
 def test_no_future_completed_bar(self):
  e=FourSessionV1();t=ms('2026-06-02T13:00:00Z')
  e.root.bars.completed['H1']=ClosedBar('H1',t,t+3600000,4400000,4400000,4400000,4400000,1)
  with self.assertRaises(AssertionError):e.on_tick(q(t))

if __name__=='__main__': unittest.main()
