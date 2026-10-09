from pathlib import Path
import sys,json,time,argparse,numpy as np
r=Path(__file__).resolve().parent;sys.path.insert(0,str(r));p=argparse.ArgumentParser();p.add_argument('--q',type=int,required=True);args=p.parse_args()
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_profit_per_heat_highrange_131e as F,jan_session_portfolio_131d as J,jan_session_portfolio_lean_131d as L
F.QMAP=np.array([args.q]*6,np.int32)
t0=time.monotonic();A,layer=F.build_raw();E,X,R,D,P,H=A
idx=np.flatnonzero(layer<=35);acc=idx[F.capsel(E[idx],X[idx],640)];wd=tuple(z[acc] for z in A)
supp=[J.build_coverage(),J.build_coldstart(50,450,64),*[L.build_rule(k,l,stp,cap) for k,l,n,stp,cap in L.LEAN]]
Q,meta=J.merge_preserve_watchdog(wd,supp,512);meta.update(wd_net=float(wd[4].sum()),wd_trades=len(acc))
s,_=J.score(J.DATA[0],*Q,f'Q{args.q}',meta)
s.update(q_raw=args.q,source='ORIGINAL_131E_JAN_IN_SAMPLE_FIXED_QUANTUM_ONLY',elapsed_s=time.monotonic()-t0,not_certified_funded_chain=True)
(r/'output'/f'JAN032_RAW_Q{args.q}_DAILY_WEEKLY.json').write_text(json.dumps(s,indent=2))
print(json.dumps({k:s[k] for k in ('name','net','trades','gross_loss','pf','win','balance_dd','equity_dd','positive_days','beat_days','positive_weeks','beat_weeks','wd_net','wd_trades')},indent=2));print('jan30',s['daily']['2026-01-30']['net'],s['daily']['2026-01-30']['trades'],'elapsed',round(time.monotonic()-t0,2))