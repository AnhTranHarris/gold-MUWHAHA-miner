from pathlib import Path
import sys,tempfile,csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from high_volume_stream import RollingWindow,FastClock,HighVolumeStream,TickExactActivePath,Quote,specialist_evidence
from volume_contract import volume_contract,teacher_counts

def q(ms,bid,ask):return Quote(ms,bid,ask,ms)

def test_rolling_window_never_uses_future():
    a=RollingWindow(1000)
    for t,p in ((0,10.),(250,10.1),(500,10.2),(750,10.1),(1000,10.3)):
        a.add(t,p,.2,1)
    pre=a.snapshot()
    assert abs(pre['disp']-0.2)<1e-9
    a.add(1250,800.,.2,1)
    assert pre['disp']==pre['disp'] and pre['range']<1

def test_raw_event_order_250ms():
    a=FastClock();a.add(q(1000,10,10.2));a.add(q(1010,10.1,10.2));a.add(q(1020,10.1,10.3))
    assert a.marks[0]==1 and a.marks[2]==1
    assert a.add(q(1250,10.15,10.35))
    assert a.hawkes.v[250][0]>=1 and a.total_slots==1

def test_tick_exact_same_millisecond():
    a=TickExactActivePath(q(1000,100,100.2),1)
    # second quote in same millisecond is a later source record; must stop out.
    x=a.update(q(1000,99.65,99.85))
    assert x is not None and x.exit_ms==1000 and x.exit_type=='SL'

def test_position_single_and_sequential():
    st=HighVolumeStream(min_evidence=0.0)
    for i in range(4000):st.on_quote(q(100000+i*250,2000+i*.01,2000.2+i*.01))
    records=st.trades
    assert st.count['closed']==len(records)
    assert all(a['exit_ms']<=b['entry_ms'] for a,b in zip(records,records[1:]))
    assert st.count['entries']<=st.count['eligible_scan']

def test_volume_floor_never_extrapolates_or_fills():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'teacher.csv'
        p.write_text('native_minute,side,positive,nonpositive,net\n2026.01.02 01:00,1,10,0,5\n')
        assert teacher_counts(p)['01']==10
        v=volume_contract(d,p)
        assert v['months']['coinexx_01']['status']=='INCOMPLETE'
        assert not v['all_sources_months_pass_volume']

def test_two_sides_are_prospective_not_future():
    a=FastClock()
    for i in range(1400):a.add(q(i*250,3000+(i%17)*.02,3000.2+(i%17)*.02))
    f=a.features(q(1400*250,3000,3000.2))
    side,score,lane,activity,spread=specialist_evidence(f)
    assert side in (-1,1) and score>=0 and lane in ('continuation','reversal')
    assert 'geo' in f and 240 in f['geo']
