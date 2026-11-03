from datetime import datetime,timezone
from pathlib import Path
import csv
import pytest
from mt5_news import load_server_intervals,server_to_utc,load_events,hourly_event_features

def offsets(tmp_path):
    p=tmp_path/'offset.csv'
    p.write_text('from_utc,to_utc,server_utc_offset_min,broker,verified_evidence\n'
       '2026-01-01T00:00:00Z,2026-03-01T00:00:00Z,120,TESTBROKER,TEST_FIXTURE_NOT_REAL\n'
       '2026-06-01T00:00:00Z,2026-08-01T00:00:00Z,180,TESTBROKER,TEST_FIXTURE_NOT_REAL\n')
    return load_server_intervals(p)

def test_server_time_utc_conversion_requires_provenance(tmp_path):
    ps=offsets(tmp_path)
    assert server_to_utc('2026.01.15 15:30:00',ps).isoformat()=='2026-01-15T13:30:00+00:00'
    assert server_to_utc('2026.07.15 15:30:00',ps).isoformat()=='2026-07-15T12:30:00+00:00'
    with pytest.raises(ValueError):server_to_utc('2026.04.15 15:30:00',ps)

def test_duplicate_offset_rejected(tmp_path):
    f=tmp_path/'dup.csv'
    f.write_text('from_utc,to_utc,server_utc_offset_min,broker,verified_evidence\n'
        '2026-01-01T00:00:00Z,2026-02-01T00:00:00Z,120,B,A\n'
        '2026-01-15T00:00:00Z,2026-02-15T00:00:00Z,180,B,A\n')
    with pytest.raises(ValueError):load_server_intervals(f)

def test_unknown_calendar_never_becomes_zero():
    d=hourly_event_features(datetime(2026,1,15,13,tzinfo=timezone.utc),None)
    assert d['mt5_high_events_in_hour']=='UNKNOWN'
    assert d['mt5_pre_release_asof_actual_allowed']==0

def test_hourly_news_boundary_and_no_surprise_leak(tmp_path):
    p=tmp_path/'events.tsv'
    p.write_text('value_id\tevent_id\tevent_time_server\timportance\tcurrency\tevent_name\ttime_mode\n'
        '1\t33\t2026.01.15 15:00:00\tCALENDAR_IMPORTANCE_HIGH\tUSD\tCPI\tCALENDAR_TIMEMODE_DATETIME\n'
        '2\t34\t2026.01.15 15:30:00\tCALENDAR_IMPORTANCE_MODERATE\tEUR\tPMI\tCALENDAR_TIMEMODE_DATETIME\n'
        '3\t35\t2026.01.15 16:00:00\tCALENDAR_IMPORTANCE_HIGH\tGBP\tReport\tCALENDAR_TIMEMODE_DATETIME\n')
    events=load_events(p,offsets(tmp_path))
    d=hourly_event_features(datetime(2026,1,15,13,tzinfo=timezone.utc),events,complete=True)
    assert d['mt5_high_events_in_hour']==1 and d['mt5_medium_high_events_in_hour']==2
    assert d['mt5_high_events_post60']==1
    assert d['mt5_pre_release_asof_actual_allowed']==0
    assert d['mt5_news_state'].startswith('RETROSPECTIVE')

def test_tentative_news_is_not_silently_timed(tmp_path):
    p=tmp_path/'events.tsv'
    p.write_text('value_id\tevent_id\tevent_time_server\timportance\tcurrency\tevent_name\ttime_mode\n'
        '1\t33\t2026.01.15 15:00:00\tHIGH\tUSD\tCPI\tCALENDAR_TIMEMODE_TENTATIVE\n')
    with pytest.raises(ValueError):load_events(p,offsets(tmp_path))
