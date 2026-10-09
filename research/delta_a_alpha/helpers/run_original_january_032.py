"""Re-run original archived January 131E helper, with either exact legacy P75 or raw quotes.

CRITICAL LIMITATIONS:
- historical Gamma parent stream computes hypothetical children then admits/caps; not funded genealogy parity.
- account modeled $100000, one 0.01 lot=1oz, no Coinexx margin/fees/slippage.
- raw mode is one explicit override of original stmr_base.materialize, not a new alpha algorithm.
- lack Dec2025 context makes Jan1 first five-minute readiness uncertified.
"""
import os,sys,time,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--mode',required=True,choices=['p75','raw']);ap.add_argument('--cap',type=int,default=640);ap.add_argument('--layer',type=int,default=35)
args=ap.parse_args()
os.chdir(ROOT);sys.path.insert(0,str(ROOT))
start=time.monotonic()
if args.mode=='raw':
 import stmr_base as st
 # Return the actual original-Dukascopy Bid and Ask (integers at 0.001 price precision).
 # This skips archived normalized P75 synthetic spread, keeps all original entry/exit mechanics.
 st.materialize=lambda t,sa,sb: (sa.copy(),sb.copy())
import jan_profit_per_heat_highrange_131e as F
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
import numpy as np
print('DATA_LOADED',args.mode,'quotes',len(J.DATA[0]),'elapsed',round(time.monotonic()-start,2),flush=True)
A,layer=F.build_raw();E,X,R,D,P,H=A
print('WD_STREAM_RAW',len(E),'elapsed',round(time.monotonic()-start,2),flush=True)
base=np.flatnonzero(layer<=args.layer)
kk=F.capsel(E[base],X[base],args.cap);idx=base[kk]
wd=tuple(z[idx] for z in A)
print('WD_CAP',len(idx),'WD_NET',round(float(wd[4].sum()),2),'elapsed',round(time.monotonic()-start,2),flush=True)
cov=J.build_coverage();print('COVERAGE',len(cov[0]),'elapsed',round(time.monotonic()-start,2),flush=True)
cold=J.build_coldstart(50,450,64);print('COLD',len(cold[0]),'elapsed',round(time.monotonic()-start,2),flush=True)
rules=[L.build_rule(k,l,st,cap) for k,l,n,st,cap in L.LEAN]
print('FOUR_SESSION_RULES',[len(z[0]) for z in rules],'elapsed',round(time.monotonic()-start,2),flush=True)
Q,meta=J.merge_preserve_watchdog(wd,[cov,cold,*rules],512)
meta.update(max_layer=args.layer,watchdog_cap=args.cap,cold_cap=64,wd_net=float(wd[4].sum()),wd_trades=int(len(wd[4])))
s,ledger=J.score(J.DATA[0],*Q,f'JAN032_ORIGINAL_{args.mode.upper()}_L{args.layer}_C{args.cap}',meta)
s.update(mode=args.mode,source='ORIGINAL_GAMMA_131E_JAN_SOURCE_WITH_REAL_QUOTE_MATERIALIZE' if args.mode=='raw' else 'EXACT_ARCHIVE_REPLAY_REFERENCE',physical_funding_chain_certified=False,jan1_five_min_ready_certified=False,data_month='2026-01',elapsed_seconds=round(time.monotonic()-start,2))
out=ROOT/'output'/f'JAN032_ORIGINAL_{args.mode.upper()}_L{args.layer}_C{args.cap}.json';out.write_text(json.dumps(s,indent=2))
# record source-original equivalent QUOTE-SIDE ledger for causal audit, entry/exit raw indices, no invented events
import csv
lp=ROOT/'output'/f'JAN032_ORIGINAL_{args.mode.upper()}_L{args.layer}_C{args.cap}_EXECUTIONS.csv'
t=J.DATA[0];a=J.DATA[1];b=J.DATA[2]
with lp.open('w',newline='') as f:
 w=csv.writer(f);w.writerow(('entry_index','exit_index','entry_ms','exit_ms','entry_side_price','exit_side_price','direction','pnl_usd','hold_seconds'))
 for ei,xi,ep,di,pnl,hold in zip(*ledger):
  ex=int(b[xi] if di>0 else a[xi]);w.writerow((int(ei),int(xi),int(t[ei]),int(t[xi]),int(ep),ex,int(di),round(float(pnl),6),round(float(hold),3)))
print('FINISHED',json.dumps({k:s.get(k) for k in ['name','mode','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','beat_weeks','wd_net','wd_trades','elapsed_seconds']}),flush=True)