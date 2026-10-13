import unittest
from v1_grid_h4_bounded_sniper_campaign_0255 import *
class TwoSlotSourceTests(unittest.TestCase):
 def o(self,k,t=0,side=1,atr=2000):
  return SniperOffer(k,side,t,atr)
 def tick(self,c,t,b=100000,ask=100200,tradable=True):
  return c.on_quote(time_ms=t,bid_raw=b,ask_raw=ask,broker_session_tradable=tradable)
 def test_two_constant_fixed_positions_not_loss_multiplier(self):
  s=BoundedH4SniperResearch()
  for owner in (0,1,2):s.offer(self.o(owner))
  self.tick(s,0)
  self.assertEqual(len(s.open_positions),2)
  self.assertEqual(s.denied_capacity,1)
  self.assertEqual([p.qty_oz for p in s.open_positions],[1,1])
 def test_observed_quote_stop_and_exact_research_fee(self):
  s=BoundedH4SniperResearch();s.offer(self.o(1))
  self.tick(s,100,b=100000,ask=100200)
  # 2000ATR stop=max(1500,3000,600)=3000 below ASK.
  cs=self.tick(s,300,b=97200,ask=97400)
  self.assertEqual(cs[0].pnl_raw,(97200-100200)-520)
  self.assertEqual(cs[0].reason,'observed-stop')
  self.assertEqual(s.statistics()['closed_quote_positions'],1)
 def test_highwater_175pct_completed_atr(self):
  s=BoundedH4SniperResearch();s.offer(self.o(1))
  self.tick(s,50,b=100000,ask=100200)
  p=s.open_positions[0];self.assertEqual(p.trail_raw,3500)
  self.tick(s,300,b=107000,ask=107200)
  self.assertEqual(p.stop_raw,103500)
 def test_late_source_not_backdated(self):
  s=BoundedH4SniperResearch();self.tick(s,1000)
  with self.assertRaises(ValueError):s.offer(self.o(1,0))
 def test_duplicate_h4_owner_rejected(self):
  s=BoundedH4SniperResearch();s.offer(self.o(3))
  with self.assertRaises(ValueError):s.offer(self.o(3))
 def test_quote_gap_rejects_stale_entry(self):
  s=BoundedH4SniperResearch();s.offer(self.o(0))
  self.tick(s,1500);self.assertEqual(s.expired,1)
  self.assertEqual(len(s.open_positions),0)
 def test_gap_on_open_position_exits_at_actual_bidask(self):
  s=BoundedH4SniperResearch();s.offer(self.o(0))
  self.tick(s,0)
  closes=self.tick(s,250000,b=80000,ask=80300)
  self.assertEqual(closes[0].price_raw,80000)
 def test_off_session_gates_new_source(self):
  s=BoundedH4SniperResearch();s.offer(self.o(1))
  self.tick(s,0,tradable=False);self.assertEqual(len(s.open_positions),0)
  self.tick(s,500,tradable=True);self.assertEqual(len(s.open_positions),1)
 def test_original_completed_h4_source_adapter_and_no_lookahead_labels(self):
  from types import SimpleNamespace
  orig=SimpleNamespace(source='GRID0254_H4_TWO_COMPLETED_M1_ACCEPTANCE',
      owner=27,side=-1,signal_known_at_ms=5000,atr_raw=45000)
  candidate=completed_h4_invitation_to_sniper_offer(orig)
  self.assertEqual((candidate.owner,candidate.side,candidate.known_at_ms,candidate.finished_h4_atr_raw),(27,-1,5000,45000))
  with self.assertRaises(ValueError):
   completed_h4_invitation_to_sniper_offer(SimpleNamespace(source='OVERFIT_WINNER',owner=27,side=1,signal_known_at_ms=5000,atr_raw=45000))
 def test_no_broker_ea_and_no_teacher(self):
  s=BoundedH4SniperResearch()
  x=s.statistics();self.assertFalse(x['trading_enabled']);self.assertFalse(x['broker_cash_verified'])
  self.assertFalse(any(hasattr(s,t) for t in ['overfit_score','source_month_selector','loss_multiplier','broker_order_send']))
 def test_closed_equals_one_slot_can_admit_new_owner(self):
  s=BoundedH4SniperResearch();s.offer(self.o(1,0));self.tick(s,0)
  s.offer(self.o(2,100))
  result=self.tick(s,100,b=97000,ask=97200)
  self.assertEqual(len(result),1);self.assertEqual(len(s.open_positions),1)
  self.assertEqual(s.open_positions[0].owner,2)
if __name__=='__main__':unittest.main()
