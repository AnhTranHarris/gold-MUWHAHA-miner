import sys, numpy as np, pytest
sys.path[:0]=['/mnt/data/h1v2_r24s4_entry_specialists/src','/mnt/data/h1v2_r24_asof/source','/mnt/data/h1v2_r24_asof/calendar']
from r24s4_broker_hazard_specialist import enhanced_prefix,EXTRA_NAMES
import r24_firstpass_engine as r

def demo():
 a=np.zeros((6,len(r.FEATURE_NAMES)),np.float32)
 k={v:i for i,v in enumerate(r.FEATURE_NAMES)}
 a[:,k['spread_raw']]=[100,200,800,1000,50,7000]
 a[:,k['quotes_3s']]=[5,3,1,90,4,11]
 a[:,k['quotes_15s']]=[20,50,6,400,17,40]
 a[:,k['quotes_60s']]=[100,150,10,800,80,80]
 a[:,k['bid_move_3s']]=[50,-150,0,250,50,7000]
 a[:,k['ask_move_3s']]=[50,-100,0,350,50,6950]
 a[:,k['bid_move_60s']]=[200,-300,0,800,100,7000]
 a[:,k['ask_move_60s']]=[210,-280,0,700,105,6930]
 a[:,k['spread_ema15s']]=[105,300,500,500,65,7000]
 a[:,k['spread_ema300s']]=[115,160,250,400,60,7300]
 a[:,k['lagged_quote_age_ms']]=1000
 a[:,k['epoch_age_s']]=300
 return a

def test_derived_feature_count_and_finite():
 y=enhanced_prefix(demo());assert y.shape==(6,len(EXTRA_NAMES)) and np.isfinite(y).all()

def test_prefix_purity_does_not_mutate_original():
 x=demo();before=x.copy();y=enhanced_prefix(x);assert np.array_equal(before,x)
 assert np.array_equal(y,enhanced_prefix(before))

def test_schema_fails_closed():
 with pytest.raises(ValueError):enhanced_prefix(np.ones((2,len(r.FEATURE_NAMES)+1),np.float32))

def test_nonfinite_fails_closed():
 a=demo();a[0,0]=np.nan
 with pytest.raises(ValueError):enhanced_prefix(a)

def test_distinct_broker_regimes_not_collapsed():
 a=demo();b=a.copy();b[0,r.FEATURE_NAMES.index('spread_raw')]=8000
 assert not np.array_equal(enhanced_prefix(a)[0],enhanced_prefix(b)[0])

def test_no_research_future_or_quota_columns_in_new_schema():
 allfields=list(r.FEATURE_NAMES)+list(EXTRA_NAMES)
 assert not any('future' in x.lower() or 'r9' in x.lower() or 'outcome' in x.lower() or 'target' in x.lower() for x in allfields)

def test_unverified_calendar_not_silently_zero_events():
 from r24_mt5_calendar_contract import calendar_quarter_diagnostic
 assert calendar_quarter_diagnostic(None,0)['impact_state']=='UNKNOWN_UNVERIFIED_MT5_EXPORT'
 assert calendar_quarter_diagnostic(None,0)['event_count'] is None
