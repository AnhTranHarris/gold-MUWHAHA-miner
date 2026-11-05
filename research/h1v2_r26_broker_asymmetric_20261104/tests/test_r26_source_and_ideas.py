from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from source import sample_features,source_candidates
from r26_mechanisms import choose_actions,NAME
from r26_replay import replay_quotes,fills,calendar


def test_first_actual_100ms_quote_fill_strict_bidask():
 t=np.array([0,80,100,100,150,1200,1600],np.int64)
 b=np.array([980,982,982,1100,1101,1102,1100],np.int32)
 a=b+20
 ff=fills(t,b,a,np.array([0],np.int32))
 assert ff.tolist()==[2], 'must choose first original quote ordinal at +100ms, not the later same-ms revision'


def test_quote_future_mutation_does_not_change_preentry_features():
 t=np.array([0,500,800,1100,1500,1900,2200,3000,4000,5200],np.int64)
 b=np.array([100,110,120,130,140,145,155,140,150,120],np.int32)
 a=b+100
 s=np.array([6,7],np.int32)
 x=sample_features(t,b,a,s)
 tt=np.r_[t,np.array([5201,5202,5203],np.int64)]
 bb=np.r_[b,np.array([10000000,-50000000,10000000],np.int32)]
 aa=np.r_[a,np.array([10000100,-49999900,10000100],np.int32)]
 xx=sample_features(tt,bb,aa,s)
 for k in x:np.testing.assert_array_equal(xx[k],x[k])


def test_true_target_first_and_exit_known_pnl():
 # BUY at ask 1000, original bid 980; target net 100+fee20 requires bid 1120.
 t=np.array([0,100,101,150,200,260],np.int64)
 b=np.array([980,980,980,1119,1120,800],np.int32)
 a=b+20
 out=replay_quotes(t,b,a,np.array([0],np.int32),np.array([1],np.int32),np.array([1],np.int8),np.array([100],np.int32),np.array([100],np.int32),np.array([8000],np.int32),100000)
 assert len(out)==1
 assert out[0,4]==1 and out[0,2]==4 and out[0,9]==100
 # the bad bid at 260 is AFTER accepted TARGET exit and cannot relabel it STOP


def test_stop_before_future_tp_is_loss_not_hindsight_win():
 t=np.array([0,100,150,200,230],np.int64)
 b=np.array([980,980,870,1200,1210],np.int32);a=b+20
 out=replay_quotes(t,b,a,np.array([0],np.int32),np.array([1],np.int32),np.array([1],np.int8),np.array([80],np.int32),np.array([100],np.int32),np.array([8000],np.int32),100000)
 assert out[0,4]==0 and out[0,2]==2 and out[0,9]==870-1000-20


def test_sell_exit_liquidates_ask_not_bid():
 t=np.array([0,100,150],np.int64)
 b=np.array([980,980,800],np.int32);a=b+20
 out=replay_quotes(t,b,a,np.array([0],np.int32),np.array([1],np.int32),np.array([-1],np.int8),np.array([100],np.int32),np.array([100],np.int32),np.array([8000],np.int32),100000)
 # SELL fill BID 980 then ASK close 820 minus fee20 => +140 net
 assert out[0,4]==1 and out[0,9]==140


def test_quote_gap_censored_not_false_win_and_safe_300s_rewarm():
 t=np.array([0,100,101,17000,17100,318000,318100],np.int64)
 b=np.array([980,980,981,1500,1500,1600,1600],np.int32);a=b+20
 out=replay_quotes(t,b,a,np.array([0,4],np.int32),np.array([1,5],np.int32),np.array([1,1],np.int8),np.array([100,100],np.int32),np.array([100,100],np.int32),np.array([10000,10000],np.int32),400000)
 assert len(out)==1 and out[0,4]==3 and out[0,9]==-2147483647


def test_one_position_no_second_entry_before_previous_exit():
 t=np.array([0,100,1000,1500,1800,2200,2500,3300,3400],np.int64)
 b=np.array([980,980,980,980,985,990,1000,1120,1130],np.int32);a=b+20
 out=replay_quotes(t,b,a,np.array([0,2,3,6],np.int32),np.array([1,3,4,7],np.int32),np.array([1,1,1,1],np.int8),np.array([100]*4,np.int32),np.array([100]*4,np.int32),np.array([10000]*4,np.int32),300000)
 assert len(out)==1 and out[0,4]==1


def test_broker_conditional_six_experts_and_no_quota_argument():
 n=3
 f={'id':np.arange(n,dtype=np.int32),'spread':np.array([700,200,850]),
 'mid500':np.array([500,500,-500]),'mid2000':np.array([1700,1700,-1700]),
 'mid6000':np.array([3700,3700,-3700]),'mid15000':np.array([6000,6000,-6000]),
 'mid60000':np.array([10000,10000,-10000]),
 'bid2000':np.array([840,840,-840]),'ask2000':np.array([860,860,-860]),
 'past_spread2000':np.array([850,850,850]),'past_spread6000':np.array([1000,1000,1000]),
 'count6000':np.array([20,20,20]),'count15000':np.array([60,60,60])}
 a=choose_actions(f,'DUKASCOPY_RAW');b=choose_actions(f,'MT5_BROKER_EXPORT')
 assert a.side.shape==(len(NAME),n)
 assert int(a.net_target[0,0])>int(b.net_target[0,0])
 assert a.side[0,0]==1 and a.side[0,2]==-1
 assert set(np.unique(a.side)).issubset({-1,0,1})


def test_exact_R9_reference_month_calendar_cannot_enter_actions():
 for mon,count,total in [('01',2976,27980),('02',2688,33523),('06',2880,31758),('07',2976,24324)]:
  q,r=calendar(mon)
  assert len(q)==count and r.sum()==total


def test_first_observed_quote_after_horizon_not_target_even_if_price_jumps():
 # First quote at H+10ms has a target price, but it is a TIMEOUT under
 # the frozen R24 first-passage label contract, not an in-horizon TP.
 t=np.array([0,100,1100,1110],np.int64)
 b=np.array([980,980,1200,1210],np.int32);a=b+20
 out=replay_quotes(t,b,a,np.array([0],np.int32),np.array([1],np.int32),np.array([1],np.int8),np.array([100],np.int32),np.array([100],np.int32),np.array([990],np.int32),300000)
 assert out[0,4]==2 and out[0,2]==2 and out[0,9]==200-20


def test_at_exact_horizon_target_remains_target():
 t=np.array([0,100,1100],np.int64)
 b=np.array([980,980,1120],np.int32);a=b+20
 out=replay_quotes(t,b,a,np.array([0],np.int32),np.array([1],np.int32),np.array([1],np.int8),np.array([100],np.int32),np.array([100],np.int32),np.array([1000],np.int32),300000)
 assert out[0,4]==1 and out[0,2]==2
