import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from sequential_entry import SequentialRouter,StrictPath
from router_v2_features import Quote

def q(t,b,a):return Quote(utc_ms=t,native_ms=t,bid=b,ask=a)
def test_delayed_quote_is_observed_before_enter():
    r=SequentialRouter()
    # Synthetic controlled ready clock: no trading can occur at future event
    r.clock.ready=lambda:True
    r.clock.features=lambda x:{'w':{1000:{'disp':.1},5000:{'disp':.2,'range':.2,'boll':.1},45000:{'disp':.2},300000:{'vol':.2}},'h':{500:{'dir':.6},1000:{'dir':.6,'sp':.3},5000:{'dir':.6}},'geo':{},'spread':x.spread,'events':()}
    r.on_quote(q(0,100,100.1))
    r.on_quote(q(250,100.01,100.11))
    assert r.count['pending_started']>=1 and r.active is None
    r.on_quote(q(500,100.015,100.115))
    assert r.active is None
    r.on_quote(q(750,100.05,100.15))
    assert r.count['confirmed_entries']>=1 and r.active is not None

def test_three_labels_separate():
    p=StrictPath(q(0,100,100.10),1)
    # For buying executable move +.25 is favorable and positive
    out=p.update(q(500,100.30,100.40))
    if out is None:out=p.update(q(600,100.26,100.36))
    assert out is not None and p.strict_label(out)=='CORRECT'
    x=StrictPath(q(0,100,100.10),1)
    out=x.update(q(500,99.70,99.80))
    assert out is not None and x.strict_label(out)=='INCORRECT'
    y=StrictPath(q(0,100,100.10),1)
    out=y.update(q(30000,100,100.10))
    assert out is not None and y.strict_label(out)=='NEUTRAL'

def test_no_oracle_features_and_no_simultaneous_positions():
    r=SequentialRouter()
    assert not hasattr(r,'teacher') and not hasattr(r,'oracle')
    assert r.pending is None and r.active is None

def test_teacher_only_postexit_updates():
    from sequential_entry import OnlineThreeClass
    b=OnlineThreeClass()
    assert b.predict((0,)*7) is None
    b.observe((0,)*7,'NEUTRAL')
    assert b.nclass==[0,0,1]
    for _ in range(201):b.observe((2,)*7,'CORRECT')
    p=b.predict((2,)*7)
    assert p is not None and p[0]>p[1] and abs(sum(p)-1)<1e-9

def test_monthly_floor_and_zero_day_does_not_pass():
    from acceptance import inspect
    e={'status':'RESEARCH_ONLY_NOT_TRAINED_OR_APPROVED','month':{'closed':24000,'CORRECT30':20000,'CORRECT15':19000,'net_microdollar':400000},
      'byday':{'a':{'closed':20000,'CORRECT30':19000,'CORRECT15':19000},'b':{'closed':4000,'CORRECT30':1000,'CORRECT15':0}},
      'byweek':{'a':{'closed':24000,'CORRECT30':20000,'CORRECT15':19000}}}
    q=inspect(e,'coinexx','01')
    assert q['passes']['volume'] and q['passes']['monthly30']
    assert not q['passes']['daily30']
    assert q['accept'] is False
