"""New L3 all-native-hour comparison; research and selection, not promoted EA."""
import os,sys,time,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/jan_research');sys.path.insert(0,'/mnt/data/jan_research/032/source')
import jan037_funded_screen as M
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_session_portfolio_131d as J
import gamma02_campaign_heartbeat_019 as HB
raw={k:getattr(M,k).copy() for k in ['E','X','R','D','P','H','S','C','O','N']}
rawidx=np.flatnonzero(raw['S']!=1)
T=time.monotonic();out=[];fn=Path('/mnt/data/jan_research/JAN037_EXPANDED_L3.json')
for interval in [250,100,50]:
 et,xt,p,reason,src=HB.heartbeat_events(J.DATA[:8],interval,4)
 e=np.searchsorted(M.t,et,side='left').astype(np.int64);x=np.searchsorted(M.t,xt,side='left').astype(np.int64)
 z=x<len(M.t);e,x,p,src=e[z],x[z],p[z],src[z]
 dr=np.where(src<=15,1,0).astype(np.int8)
 # NY direction comes from causal completed H4/H1/M15/M5 same function source
 # HB.heartbeat_candidates must be used to obtain correct direction for NY.
 ii,dir0,src0,hold,tp,sl=HB.heartbeat_candidates(M.t,J.DATA[3],*J.DATA[4:8],interval,4)
 # Match event order to function's internally sorted time event indices.
 if len(ii)!=len(e) or not np.array_equal(M.t[ii],M.t[e]):
  raise AssertionError(f'Event alignment {len(ii)} vs {len(e)}')
 dr=dir0
 r=np.where(dr>0,M.a[e],M.b[e]).astype(np.int32)
 truep=(np.where(dr>0,M.b[x],M.a[x])-r)*dr/1000.-.02
 diff=float(np.max(np.abs(truep-p))) if len(p) else 0
 print('HEARTBEAT',interval,len(e),'MAX_P_DIFF',diff,'groups',{int(s):int((src==s).sum()) for s in np.unique(src)},'elapsed',round(time.monotonic()-T,1),flush=True)
 if diff>0.1:raise ValueError('Outcome misalignment')
 # Candidate expands original hourly source, preserving untouched original four session cells.
 extras={'E':e,'X':x,'R':r,'D':dr,'P':truep,'H':(M.t[x]-M.t[e])/1000.,'S':(src.astype(np.int16)+10).astype(np.int8),'C':np.full(len(e),-1,np.int32),'O':np.full(len(e),-1,np.int32),'N':np.full(len(e),-1,np.int32)}
 new={k:np.concatenate([raw[k][rawidx],extras[k]]) for k in extras}
 order=np.lexsort((np.arange(len(new['E'])),new['S'],new['E']))
 for k in new:setattr(M,k,new[k][order]);
 M.total=len(M.E);M.spread=(M.a[M.E].astype(np.int64)-M.b[M.E])/1000.
 ii=np.searchsorted(M.t,M.t[M.E]-20000,side='left');M.imp20=((M.a[M.E].astype(np.int64)+M.b[M.E])-(M.a[ii].astype(np.int64)+M.b[ii]))/2000.
 for wd,cap,sec in [(0,512,20),(0,1024,50),(64,768,50),(256,1024,50),(512,1024,50),(512,2048,100)]:
  prm=dict(maxopen=cap,wdcap=wd,per_quote=4,sidecap=cap,cap_cell=max(4,wd//2),spread_max=10,per_second=sec)
  r,ledger=M.run(**prm);r.update(interval_ms=interval,heartbeat_candidates=len(e),params=prm)
  out.append(r)
  print('CASE',interval,'wd',wd,'cap',cap,'net',r['net'],'GL',r['gl'],'PF',r['pf'],'trades',r['trades'],'s',round(time.monotonic()-T,1),flush=True)
 fn.write_text(json.dumps(sorted(out,key=lambda x:x['net'],reverse=True),indent=2))
print('TOP',json.dumps(sorted(out,key=lambda x:x['net'],reverse=True)[:5]),flush=True)
