import csv
import pytest
from pathlib import Path
from run_hourly_clock import run,validate_inputs,read_csv,EXPECTED_HOUR,EXPECTED_DAY,hash_file

H='/mnt/data/R11S4_ALL_2880_COMPLETE_UTC_HOURLY_SOURCE_QUOTA_RESULTS.csv'
D='/mnt/data/R11S4_ALL_120_COMPLETE_UTC_DAILY_SOURCE_QUOTA_RESULTS.csv'

def test_real_historical_input_sha():
    assert hash_file(H)==EXPECTED_HOUR and hash_file(D)==EXPECTED_DAY

def test_all_2880_source_rows_and_120_days_reconcile():
    validate_inputs(read_csv(H),read_csv(D))

def test_one_month_all_hours_days_are_preserved(tmp_path):
    a=run(H,D,tmp_path,('2026-02',))
    assert a['month_results'][0]['days']==28
    z=read_csv(tmp_path/'2026-02'/'2026-02_ALL_HOURS_R11S5_CLOCK_AND_NEWS.csv')
    assert len(z)==672
    assert sum(int(x['hour_mathematically_impossible']) for x in z)==151
    assert {x['mt5_high_events_in_hour'] for x in z}=={'UNKNOWN'}
    assert not any(x['market_actual_broker_permission']=='OPEN' for x in z)
