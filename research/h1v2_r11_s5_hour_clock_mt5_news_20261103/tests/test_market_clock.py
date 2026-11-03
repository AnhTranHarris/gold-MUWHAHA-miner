from datetime import datetime,timezone
import pytest
from market_clock import clock_hour,utc_hour,SESSIONS,next_session_open

def test_exact_utc_required():
    with pytest.raises(ValueError): utc_hour('2026-01-01T00:30:00Z')
    with pytest.raises(ValueError): utc_hour('2026-01-01T08:00:00-06:00')

def test_ny_summer_winter_session_shift():
    january=clock_hour('2026-01-14T13:00:00Z')
    july=clock_hour('2026-07-14T12:00:00Z')
    assert january['nominal_NEW_YORK_minutes']==60
    assert july['nominal_NEW_YORK_minutes']==60
    assert clock_hour('2026-01-14T12:00:00Z')['nominal_NEW_YORK_minutes']==0
    assert clock_hour('2026-07-14T11:00:00Z')['nominal_NEW_YORK_minutes']==0

def test_london_summer_winter_session_shift():
    assert clock_hour('2026-01-14T08:00:00Z')['nominal_LONDON_minutes']==60
    assert clock_hour('2026-07-14T07:00:00Z')['nominal_LONDON_minutes']==60
    assert clock_hour('2026-01-14T07:00:00Z')['nominal_LONDON_minutes']==0

def test_new_york_spring_transition_sunday_closed():
    d=clock_hour('2026-03-08T13:00:00Z')
    assert d['nominal_NEW_YORK_minutes']==0
    assert d['market_actual_broker_permission'].startswith('UNKNOWN')

def test_sydney_summer_and_winter_and_weekend():
    assert clock_hour('2026-01-12T21:00:00Z')['nominal_SYDNEY_minutes']==60
    assert clock_hour('2026-07-12T22:00:00Z')['nominal_SYDNEY_minutes']==60
    assert clock_hour('2026-01-10T21:00:00Z')['nominal_SYDNEY_minutes']==0

def test_chicago_fall_fold_is_distinct_hour():
    a=clock_hour('2026-11-01T06:00:00Z')
    b=clock_hour('2026-11-01T07:00:00Z')
    assert a['chicago_wall_hour'][:13]==b['chicago_wall_hour'][:13]
    assert a['chicago_fold']==0 and b['chicago_fold']==1

def test_no_broker_holiday_inferred():
    d=clock_hour('2026-07-03T14:00:00Z')
    assert d['market_actual_broker_permission'] != 'OPEN'
    assert d['prop_firm_operating_permission'].startswith('UNCONFIGURED')
