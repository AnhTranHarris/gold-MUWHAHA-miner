import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from r23h7_quote_grammar import quote_path_features
from r23h7_clock_news import clock_features,asof_news_state
from r23h7_broker_hazards import day_balanced_sample,split_censored_gap,FEAT_COUNT


def test_ordinal_prefix_future_invariance_same_ms():
 t=np.array([0,50,100,100,100,102,110,120],np.int64)
 b=np.array([100,110,115,114,110,111,111,120],np.int32)
 a=b+10
 ix=np.array([2,3,5],np.int32)
 reference=quote_path_features(t,b,a,ix)
 b2=b.copy();a2=a.copy();b2[6:]=b2[6:]+900;a2[6:]=a2[6:]+910
 np.testing.assert_allclose(quote_path_features(t,b2,a2,ix),reference)
 b3=b.copy();a3=a.copy();b3[4:]=b3[4:]-3;a3[4:]=a3[4:]+8
 np.testing.assert_allclose(quote_path_features(t,b3,a3,ix[:2]),reference[:2])
 assert not np.array_equal(quote_path_features(t,b3,a3,ix[2:]),reference[2:])


def test_timezones_change_at_real_dst_boundaries():
 def t(s):return int(np.datetime64(s,'ms').astype('int64'))
 jan=clock_features(np.array([t('2026-01-12T13:00:00')]))[0]
 jul=clock_features(np.array([t('2026-07-13T13:00:00')]))[0]
 assert jan[9]==0 and jul[9]==1  # London winter/summer
 assert jan[10]==0 and jul[10]==1  # New York winter/summer
 assert jan[8]==1 and jul[8]==0  # Sydney summer/winter


def test_news_requires_provider_snapshot_and_asof_vintage():
 base=100_000_000
 assert asof_news_state(base,None)['status'].startswith('UNKNOWN')
 state={'provider':'MT5','coverage_complete':True,'utc_offsets_verified':True,
   'captured_utc_ms':base-100,'coverage_from_utc_ms':base-10_000_000,'coverage_to_utc_ms':base+10_000_000,
   'events':[{'currency':'USD','impact':'HIGH','known_at_utc_ms':base-200,'event_utc_ms':base+30_000},
             {'currency':'USD','impact':'MODERATE','known_at_utc_ms':base+1,'event_utc_ms':base+55_000}]}
 assert asof_news_state(base,[state])['status']=='UNKNOWN_MALFORMED_EVENT_VINTAGE'
 state['events'][1]['known_at_utc_ms']=base-200
 assert asof_news_state(base,[state])['next60m_medium_high']==2
 assert asof_news_state(base,[state])['broker_tradable'] is None


def test_day_balanced_sampling_and_quote_gap_end_censor():
 t=np.r_[np.arange(0,50)*1000,np.arange(86400000,86400000+90_000,1000)].astype(np.int64)
 ix=day_balanced_sample(t,10,14)
 assert len(ix)==20 and np.sum(ix<50)==10 and np.sum(ix>=50)==10
 quotes=np.array([0,1000,2000,21000,22000,23000],np.int64)
 label=np.full((2,2,3),3,np.int8)
 actual=split_censored_gap(label,np.array([1,5],np.int32),quotes)
 assert actual[0,0,0]==3 and actual[1,0,0]==4
 assert FEAT_COUNT==89
