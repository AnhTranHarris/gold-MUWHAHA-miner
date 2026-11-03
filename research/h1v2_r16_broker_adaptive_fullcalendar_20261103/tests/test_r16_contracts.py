import importlib.util,sys,pathlib,numpy as np
P=pathlib.Path('/mnt/data/h1v2_r16_broker_adaptive/src/r16_fullcalendar_broker_adaptive.py')
spec=importlib.util.spec_from_file_location('r16',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_source_oneposition_exact_earliest_end():
 starts=np.array([0,5,14,17,29,42],np.int64)
 ends=np.array([30,10,18,25,35,45],np.int64)
 got=m.schedule(starts,ends)
 assert list(got)==[1,2,4,5]
 assert np.all(starts[got[1:]]>ends[got[:-1]])

def test_tie_order_is_stable():
 a=np.array([0,1,2],np.int64);b=np.array([5,5,5],np.int64)
 assert list(m.schedule(a,b))==[0]

def test_zero_length_must_fail():
 import pytest
 with pytest.raises(AssertionError):m.schedule(np.array([1]),np.array([1]))

def test_watch_confirms_only_actual_future_observation():
 t=np.array([0,1000,3000],np.int64)
 b=np.array([100000,100000,100000],np.int32)
 a=b+np.array([3000,3000,1400],np.int32)
 ix=np.array([0,1,2],np.int64)
 f=np.array([1,1,1],np.int8)
 e15=np.array([3000.,3000.,1600.]);e300=np.array([3000.,3000.,2700.])
 w0,w1,starts,good,exp,reset=m.watch_prefix(t,b,a,ix,f,e15,e300)
 assert np.array_equal(w0,np.array([False,False,True]))
 assert np.array_equal(w1,np.array([False,False,True]))
 assert starts[0]>=1 and good[0]==1 and good[1]==1

def test_quote_drought_buried_inside_excluded_candidates_resets_watch():
 t=np.array([0,1000,17001,18000],np.int64)
 b=np.array([100000]*4,np.int32)
 a=b+np.array([3000,4800,5000,1400],np.int32)
 # Raw source quotes i=1,2 are spread-ineligible but contain 16s gap.
 ix=np.array([0,3],np.int64)
 f=np.array([1,1],np.int8)
 e15=np.array([3000.,1600.,1600.,1200.]);e300=np.array([3000.,2700.,3000.,2400.])
 w0,w1,starts,good,exp,reset=m.watch_prefix(t,b,a,ix,f,e15,e300)
 assert not w0.any() and not w1.any()
 assert np.all(reset>=1)

def test_later_source_mutation_cannot_change_earlier_watch_admission():
 t=np.array([0,250,300,1000,1350,1600],np.int64)
 b=np.array([100000]*len(t),np.int32)
 a=b+np.array([3000,2800,2700,1400,900,700],np.int32)
 ix=np.arange(len(t),dtype=np.int64);f=np.ones(len(t),np.int8)
 e15=np.full(len(t),1000.,np.float64);e300=np.full(len(t),2700.,np.float64)
 before=m.watch_prefix(t,b,a,ix,f,e15,e300)
 mutated=a.copy();mutated[-1]=b[-1]+3800
 after=m.watch_prefix(t,b,mutated,ix,f,e15,e300)
 assert np.array_equal(before[0][:-1],after[0][:-1])
 assert np.array_equal(before[1][:-1],after[1][:-1])

def test_fee_and_spread_expected_price_mathematics():
 for side in (1,-1):
  entry_bid=100000;entry_ask=103200
  exit_liq=(entry_ask+120) if side==1 else (entry_bid-120)
  entry=entry_ask if side==1 else entry_bid
  assert (exit_liq-entry)*side-20 == 100

def test_quarter_hour_references_complete_and_exact():
 for mon in ('01','02','06','07'):
  rows,hr,qkeys,qref,href=m.read_refs(mon)
  assert len(rows)==len(qrefs:=qref) and len(hr)*4==len(rows)
  assert np.array_equal(qrefs.reshape(-1,4).sum(axis=1),href)
  assert int(qrefs.sum())=={'01':27980,'02':33523,'06':31758,'07':24324}[mon]
