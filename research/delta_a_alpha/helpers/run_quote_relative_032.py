"""Explicit ONE LINE original-131E experiment: per first-parent quoted-spread quantum floor.
Computes the quantum only from a quote already available when first parent arrives;
all original Watchdog, HTF, session, cap, coverage, exits remain intact.
This is January development-only, no physical downstream-funded credit certification.
"""
import sys,time,json,inspect,argparse,difflib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));ap=argparse.ArgumentParser();ap.add_argument('--k',type=float,required=True);args=ap.parse_args()
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_profit_per_heat_highrange_131e as F,jan_session_portfolio_131d as J,jan_session_portfolio_lean_131d as L
src=inspect.getsource(F.build_raw)
old='q=int(QMAP[b10]);A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],q,0,0,2);E,X,R,Dd,P,H,O=A[:7]'
new='q=int(max(QMAP[b10], int(kmult * (a[int(pei[jj[0]])]-b[int(pei[jj[0]])]))));A=renewal_owned(t,a,b,pei[jj],pxi[jj],pd[jj],q,0,0,2);E,X,R,Dd,P,H,O=A[:7]'
assert src.count(old)==1,'Original source changed; refuse patch'
modified=src.replace(old,new)
F.kmult=float(args.k);exec(compile(modified,'original_131e_one_line_spread_quantum_variant','exec'),F.__dict__)
(ROOT/'output'/'JAN032_PROPOSED_ONE_LINE_SPREAD_QUANTUM_PATCH.diff').write_text(''.join(difflib.unified_diff(src.splitlines(keepends=True),modified.splitlines(keepends=True),fromfile='original_131e',tofile='original_131e_adaptive_quote_floor')))
t0=time.monotonic();A,layer=F.build_raw();E,X,R,D,P,H=A
idx=np.flatnonzero(layer<=35);acc=idx[F.capsel(E[idx],X[idx],640)];wd=tuple(z[acc] for z in A)
supp=[J.build_coverage(),J.build_coldstart(50,450,64),*[L.build_rule(k,l,step,cap) for k,l,n,step,cap in L.LEAN]]
Q,meta=J.merge_preserve_watchdog(wd,supp,512);meta.update(wd_net=float(wd[4].sum()),wd_trades=len(acc))
s,_=J.score(J.DATA[0],*Q,'quote_spread_floor_k'+str(args.k),meta)
s.update(k=args.k,source='EXPERIMENTAL_ONE_LINE_SOURCE_PATCH_ENTRY_KNOWN_FIRST_PARENT_SPREAD',full_funded_chain_certified=False,elapsed_s=time.monotonic()-t0)
fn=ROOT/'output'/f'JAN032_RAW_ENTRYKNOWN_SPREAD_K{args.k:.2f}.json';fn.write_text(json.dumps(s,indent=2))
print('RESULT',args.k,{k:round(v,3) if isinstance(v,float) else v for k,v in s.items() if k in ('net','trades','gross_loss','pf','win','equity_dd','balance_dd','positive_days','beat_days','beat_weeks','wd_net','wd_trades')},'jan30_net',round(s['daily']['2026-01-30']['net'],2),'elapsed',round(time.monotonic()-t0,2))