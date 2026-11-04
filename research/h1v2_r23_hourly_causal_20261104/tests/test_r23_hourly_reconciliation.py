import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
import r23_hourly_reconciliation as m

def test_nominal_dst_and_unknown():
    jan=m.actual_session('2026-01-15T15:00:00Z')
    jun=m.actual_session('2026-06-15T15:00:00Z')
    assert jan['broker_operating_permission']=='UNKNOWN'
    assert jan['mt5_medium_high_calendar_vintage']=='UNKNOWN'
    assert jan['prop_firm_rule']=='UNKNOWN'
    assert 'EST' in jan['local_clocks']['America/New_York']
    assert 'EDT' in jun['local_clocks']['America/New_York']

def test_best_case_is_future_only():
    rr=[]
    for j in range(12):
        rr.append({'utc_hour':'2026-01-01T00:00:00Z','source':'DUKASCOPY_RAW','month':'01',
        'scenario':'A'+str(j+1),'R9_SYNTH_hour_reference':'10',
        'R23_hindsight_after':str(j)})
    o=m.at_best(rr,'R9_SYNTH_hour_reference','R23_hindsight_after','utc_hour')
    assert o[0]['best_hindsight_selected']==11
    assert o[0]['number_scenarios_meeting_count']==2
    assert o[0]['selection_uses_future']==1
    assert o[0]['causal_accuracy_demonstrated']==0

def test_duplicate_period_failclosed():
    r=[{'utc_hour':'2026-01-01T00:00:00Z','source':'DUKASCOPY_RAW','month':'01',
       'scenario':'A1','R9_SYNTH_hour_reference':'10','R23_hindsight_after':'14'}]
    try:m.at_best(r,'R9_SYNTH_hour_reference','R23_hindsight_after','utc_hour')
    except AssertionError:pass
    else:raise AssertionError('duplicate or missing scenarios accepted')

def test_source_ref_integrity():
    assert sum(m.R9_UTC_REF.values())==117585
    assert m.ACTIVE_UTC_HOURS==1917
    assert m.ACTIVE_UTC_QUARTERS==7521
