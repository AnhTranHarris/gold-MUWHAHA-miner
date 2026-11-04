"""Isolated new-policy source contracts; does not rerun frozen R23H24 experiments."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from r23h7_jan_week_replay import actions
from r23h7_clock_news import asof_news_state


def test_policy_no_future_outcome_or_r9_quota_input():
 n=4
 # Mock 5 independent outcome causes; no future labels or R9 quotas exist here.
 cause=np.zeros((n,2,3,5),np.float32)
 cause[:,:,:,0]=0.5;cause[:,:,:,1]=0.2;cause[:,:,:,2]=0.3
 held=np.full((n,2,3),0.35,np.float32)
 wait=np.full(n,0.3,np.float32)
 s,h,z=actions(cause,held,wait,-1)
 assert s.shape==(n,) and h.shape==(n,) and z.shape==(n,)
 ss,hh,_=actions(cause,held,wait,2)
 assert np.all(hh==2)
 assert np.all(np.isfinite(z))


def test_calendar_rejects_retrospective_snapshot_as_historic_prediction():
 decision=1_000_000
 snap={'provider':'FOREX_FACTORY','captured_utc_ms':decision+1,
       'coverage_complete':True,'utc_offsets_verified':True,
       'coverage_from_utc_ms':0,'coverage_to_utc_ms':20_000_000,'events':[]}
 x=asof_news_state(decision,[snap])
 assert x['status']=='UNKNOWN_NO_ASOF_COVERAGE'
 assert x['next60m_medium_high'] is None
 assert x['prop_authorized'] is None
