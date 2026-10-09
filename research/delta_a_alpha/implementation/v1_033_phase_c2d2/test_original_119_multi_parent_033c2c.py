"""Endogenous 119 per-cell earned parent windows/child lineage tests."""
import unittest
from dataclasses import replace
from v1_funded_core_033c import Quote,Structure,Proposal,Limits,FundedEngine
from original_119_multi_parent_033c2c import Original119MultiParentL4
T=1769191200000

def q(t,bid=100000):return Quote(t,bid+100,bid)
def s(t,side=1):return Structure('NY',side,side,-1,-1,t-1,'grid',0,
    (t-14400001,t-3600001,t-900001,t-300001))
def eng(wd,max_open=40):
 return FundedEngine(replace(Limits(),max_open=max_open,max_layer_open=max_open,max_per_source_open=max_open,
  max_same_direction=max_open,max_per_cell_side=max_open,max_orders_per_tick=1,max_orders_per_second=5),[wd],broker_contract_verified=True)
def parent(t,seq):return Proposal('L3','ORIGINAL_049_UNION_UTC17','grid',1,0,0,120000,source_event_key=f'C2CPARENT:{seq}')

class PaidMultiParent(unittest.TestCase):
 def test_first_parent_needs_4_real_winning_children_then_second_can_enter(self):
  wd=Original119MultiParentL4();e=eng(wd)
  e.process_quote(q(T),s(T),proposals=(parent(T,0),))
  self.assertEqual(wd.admitted_parent_windows,1)
  # Four realized good child closes, not four merely hypothetical targets.
  for k in range(4):
   t=T+1000+k*3000
   e.process_quote(q(t,100000+2000*k),s(t))
   self.assertEqual(len([p for p in e.positions.values() if p.layer=='L4']),1)
   e.process_quote(q(t+1000,102000+2000*k),s(t+1000))
  self.assertEqual(wd.cell_streak[next(iter(wd.cell_streak))],4)
  self.assertTrue(wd.cell_earned[next(iter(wd.cell_earned))])
  self.assertTrue(next(iter(e.campaigns.values())).earned)
  # Close genuinely funded parent; the earned cell can admit the next funded L3
  old_parent=next(p for p in e.positions.values() if p.layer=='L3')
  e.request_reduce(old_parent.id)
  e.process_quote(q(T+13500,106000),s(T+13500))
  e.process_quote(q(T+15000,106000),s(T+15000),proposals=(parent(T+15000,1),))
  self.assertEqual(wd.admitted_parent_windows,2)
  self.assertEqual(wd.earned_parent_admissions,1)
  self.assertEqual(len(wd.windows),2)
  self.assertTrue(next(w for w in wd.windows.values() if w.parent_id!=old_parent.id).active)
 def test_losing_executed_child_relocks_further_parent_admission(self):
  wd=Original119MultiParentL4();e=eng(wd)
  e.process_quote(q(T),s(T),proposals=(parent(T,0),))
  for k in range(4):
   t=T+1000+k*3000;e.process_quote(q(t,100000+2000*k),s(t))
   e.process_quote(q(t+1000,102000+2000*k),s(t+1000))
  p=next(p for p in e.positions.values() if p.layer=='L3');e.request_reduce(p.id)
  e.process_quote(q(T+13500,106000),s(T+13500))
  e.process_quote(q(T+15000,106000),s(T+15000),proposals=(parent(T+15000,1),))
  e.process_quote(q(T+16000,106000),s(T+16000))
  self.assertEqual(sum(p.layer=='L4' for p in e.positions.values()),1)
  child=next(p for p in e.positions.values() if p.layer=='L4')
  e.request_reduce(child.id)
  e.process_quote(q(T+17000,102000),s(T+17000))
  self.assertFalse(next(iter(wd.cell_earned.values())))
  self.assertFalse(next(iter(e.campaigns.values())).earned)
  # Existing accepted second parent still funded, but a THIRD parent cannot
  # acquire a Watchdog window while cell is relocked.
  prev=wd.admitted_parent_windows
  # Temporary prevent 119 priority from occupying the only allowed new event
  e.process_quote(q(T+18000,102000),s(T+18000),proposals=(parent(T+18000,2),))
  self.assertEqual(wd.admitted_parent_windows,prev)
 def test_unfunded_parent_never_unlocks_window_even_when_cell_is_earned(self):
  wd=Original119MultiParentL4();e=eng(wd,max_open=1)
  e.process_quote(q(T),s(T),proposals=(parent(T,0),))
  # Any rejected extra parent cannot sponsor a new cell window; no child can
  # be retrospectively credited to that rejected quote.
  e.process_quote(q(T+200),s(T+200),proposals=(parent(T+200,1),))
  self.assertEqual(wd.admitted_parent_windows,1)
  self.assertEqual(wd.eligible_parents,1)
  self.assertGreaterEqual(e.reject_counts['GLOBAL_CAP'],1)
 def test_rearm_not_on_same_price_event_and_requires_paid_source_parent(self):
  wd=Original119MultiParentL4()
  e=FundedEngine(replace(Limits(),max_open=40,max_layer_open=40,max_per_source_open=40,
     max_same_direction=40,max_per_cell_side=40,max_orders_per_tick=2,max_orders_per_second=5),
     [wd],broker_contract_verified=True)
  # A fabricated original-Watchdog scout with NO parent must fail closed.
  orphan=Proposal('L4','ORIGINAL_119_C2C_CHILD','orphan',1,1.19,0,60000,
                  first_scout=True,parent_id=None)
  e.process_quote(q(T),s(T),proposals=(orphan,parent(T,0)))
  self.assertEqual(e.reject_counts['UNFUNDED_OR_UNEARNED_GENEALOGY'],1)
  e.process_quote(q(T+1000),s(T+1000))
  self.assertEqual(sum(p.layer=='L4' for p in e.positions.values()),1)
  # The child exits on this quote. Even if another order could fit within
  # the same quote tick, the next earned/rearm decision waits for NEXT quote.
  e.process_quote(q(T+2000,102000),s(T+2000))
  self.assertEqual(sum(p.layer=='L4' for p in e.positions.values()),0)
  e.process_quote(q(T+3000,102000),s(T+3000))
  self.assertEqual(sum(p.layer=='L4' for p in e.positions.values()),1)
 def test_cell_earned_not_spent_by_admission_until_bad_child_close(self):
  wd=Original119MultiParentL4();e=eng(wd)
  e.process_quote(q(T),s(T),proposals=(parent(T,0),))
  for k in range(4):
   t=T+1000+k*3000;e.process_quote(q(t,100000+2000*k),s(t))
   e.process_quote(q(t+1000,102000+2000*k),s(t+1000))
  self.assertTrue(next(iter(e.campaigns.values())).earned)
  e.process_quote(q(T+14000,106000),s(T+14000))
  self.assertTrue(next(iter(e.campaigns.values())).earned)

if __name__=='__main__':unittest.main()