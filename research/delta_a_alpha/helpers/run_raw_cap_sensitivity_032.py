"""January-source 131E allowed Watchdog layer-depth/cap sensitivity with raw quotes.
This is IN-SAMPLE diagnostic, NEVER portable or fully funded live certification.
"""
from pathlib import Path
import json,sys,time
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_profit_per_heat_highrange_131e as F
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
import numpy as np
start=time.monotonic()
A,lay=F.build_raw();E,X,R,D,PNL,H=A
parts=[J.build_coverage(),J.build_coldstart(50,450,64),*[L.build_rule(k,l,stp,cap) for k,l,n,stp,cap in L.LEAN]]
results=[]
for layer in (25,30,35,40):
  elig=np.flatnonzero(lay<=layer)
  for cap in (240,384,512,640,703):
   ii=elig[F.capsel(E[elig],X[elig],cap)]
   wd=tuple(z[ii] for z in A)
   Q,meta=J.merge_preserve_watchdog(wd,parts,512)
   meta.update(max_layer=layer,watchdog_cap=cap,wd_net=float(wd[4].sum()),wd_trades=int(len(wd[4])))
   s,_=J.score(J.DATA[0],*Q,f'RAW_L{layer}_C{cap}',meta)
   results.append({k:s[k] for k in ('name','net','trades','gross_profit','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','wd_net','wd_trades','positive_days','positive_weeks','beat_days','beat_weeks')})
   print('candidate',layer,cap,'net',round(s['net'],2),'trades',s['trades'],'PF',round(s['pf'],3),'grossloss',round(s['gross_loss'],2),'equity_dd',round(s['equity_dd'],2),'days',s['positive_days'],flush=True)
O=P/'output';(O/'JAN032_RAW_131E_CAP_LAYER_SENSITIVITY.json').write_text(json.dumps({'label':'JANUARY_2026_IN_SAMPLE_ORIGINAL_SOURCE_MECHANICS_NOT_PHYSICAL_FUNDING_PARITY','source':'gamma02_jan 131E, actual Bid/Ask, 20 caps/layers','results':results,'elapsed':round(time.monotonic()-start,2)},indent=2))
print('DONE',round(time.monotonic()-start,2),flush=True)