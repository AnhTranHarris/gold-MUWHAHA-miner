from dataclasses import replace
import pytest
from htf_ticklab.bars import Bar
from htf_ticklab.feeds import Quote
from htf_ticklab.signal_bus import AccountView
from htf_ticklab.six_specialists import SixSpecialists,SixExpertParameters

T=1767315600000

def mkbar(k,t,p,displ=0.12):
 q=p+displ
 return Bar(k,t,t+k*1000,p,max(p,q)+.05,min(p,q)-.05,q,p+.2,max(p,q)+.25,min(p,q)+.15,q+.2,18)

def sample():
 s=SixSpecialists(SixExpertParameters(max_spread=.7))
 for k in range(21):
  for width in (60,300):
   b=mkbar(width,T+k*width*1000,200.0+.1*k, 5.0 if width==300 else .12)
   s.on_bar(b,Quote(b.end_ms+1,b.bid_close,b.ask_close,'coinexx'),AccountView('coinexx',b.end_ms+1,100,100,0,False,0))
 for k in range(70):
  b=mkbar(5,T+10000000+k*5000,202.0+.02*k)
  q=Quote(b.end_ms+1,b.bid_close,b.ask_close,'coinexx')
  s.on_bar(b,q,AccountView('coinexx',q.ms,100,100,0,False,0))
 return s

def test_completed_bar_causal_signal_and_no_position_bypass():
 s=sample();p=203.4
 b=mkbar(5,T+10000000+70*5000,p,1.2);q=Quote(b.end_ms+1,b.bid_close,b.ask_close,'coinexx')
 v=AccountView('coinexx',q.ms,100,100,0,False,0)
 z=s.on_bar(b,q,v)
 assert z and all(x.observed_ms==q.ms and x.source_id==s.p.source_id and x.stop_distance>0 for x in z)
 assert any(x.reason=='pulse_continuation' for x in z)
 assert s.on_tick(q,v)==()
 b2=mkbar(5,b.end_ms,b.bid_close,1.2);q2=Quote(b2.end_ms+1,b2.bid_close,b2.ask_close,'coinexx')
 assert s.on_bar(b2,q2,replace(v,event_ms=q2.ms,position_side=1))==()

def test_stale_completed_s5_does_not_emit():
 s=sample();p=203.4;b=mkbar(5,T+10000000+70*5000,p,1.2)
 q=Quote(b.end_ms+3000,b.bid_close,b.ask_close,'coinexx')
 view=AccountView('coinexx',q.ms,100,100,0,False,0)
 assert s.on_bar(b,q,view)==()
 assert len(s.s5)==0

def test_unfinished_bar_fails_closed():
 s=SixSpecialists();b=mkbar(5,T,100,1);q=Quote(T+100,101,101.2,'coinexx')
 with pytest.raises(ValueError,match='incomplete'):
  s.on_bar(b,q,AccountView('coinexx',q.ms,100,100,0,False,0))