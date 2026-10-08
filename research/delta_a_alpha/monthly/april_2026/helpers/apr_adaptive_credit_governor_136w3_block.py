from __future__ import annotations
import json,heapq,sys,itertools,time,argparse
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/april_vertical_work')
import apr_vertical_portfolio_136g as A
ap=argparse.ArgumentParser();ap.add_argument('--maxd',type=int,required=True);ap.add_argument('--scout',type=int,required=True);args=ap.parse_args()
O=Path('/mnt/data/april_vertical_work')
SYN=dict(net=38353.96,trades=31758,gross_loss=-2414.22,pf=16.886688,win=.86759242,expectancy=1.207694)
BEN=json.loads((O/'r9_synth_apr_daily_weekly_136.json').read_text())
z0=np.load(O/'apr_native_conviction_refine_streams_136h.npz');N=tuple(z0[f'WIN87_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
z1=np.load(O/'apr_session_grid_streams_136b.npz');HV=tuple(z1[f'HIGHVOL_PF8_{k}'] for k in ['E_MS','X_MS','R','D','P','H']);AS=tuple(z1[f'ASIA_PF8_{k}'] for k in ['E_MS','X_MS','R','D','P','H'])
CORE,_,_=A.caprec(A.dedup([('NATIVE',N),('HIGHVOL',HV),('ASIA',AS),('RECOVERY',A.REC)]),176);CS=A.score(CORE)
z=np.load(O/'apr_renewal_owner_stream_136s0.npz')
def daykey(ms): return int(ms//86400000)
def build(credit_gain,max_credit):
 out=[];diag={}
 for ri in range(7):
  E,X,R,D,P,H,L,OWN=[np.asarray(z[f'R{ri}_{k}']) for k in ['E_MS','X_MS','R','D','P','H','LAYER','OWNER']]
  owners={}
  for c in np.unique(OWN):
   idx=np.flatnonzero(OWN==c);idx=idx[np.argsort(E[idx],kind='stable')];idx=idx[L[idx]<=args.maxd]
   if len(idx): owners[int(c)]=idx
  parent_events=sorted((int(E[idx].min()),daykey(int(E[idx].min())),c) for c,idx in owners.items())
  byday={}
  for pe,d,c in parent_events:byday.setdefault(d,[]).append((pe,c))
  admitted=skipped=unlocks=relocks=fastwins=0; maxcred=0
  for d,plist in byday.items():
   streak=0;credits=0;gate=False;parents_seen=0;q=[];seq=0
   for pe,c in plist:heapq.heappush(q,(pe,0,seq,('P',c)));seq+=1
   while q:
    tm,kind,_,ev=heapq.heappop(q)
    if ev[0]=='P':
     c=ev[1];parents_seen+=1;allow=(parents_seen<=args.scout) or (gate and credits>0)
     if not allow:skipped+=1;continue
     admitted+=1
     if parents_seen>args.scout and gate:credits-=1
     for i in owners[c]:
      heapq.heappush(q,(int(X[i]),1,seq,('X',int(i))));seq+=1
      out.append((int(E[i]),int(X[i]),int(R[i]),int(D[i]),float(P[i]),float(H[i]),f'RENEW_R{ri}_L{int(L[i])}'))
    else:
     i=ev[1];good=(float(P[i])>0 and float(H[i])<=60.0);old=gate
     if good:
      streak+=1;fastwins+=1
      if streak>=4:gate=True;credits=min(max_credit,credits+credit_gain);maxcred=max(maxcred,credits)
     else:streak=0;credits=0;gate=False
     if gate and not old:unlocks+=1
     if old and not gate:relocks+=1
  diag[str(ri)]={'parents':len(parent_events),'admitted':admitted,'skipped':skipped,'unlocks':unlocks,'relocks':relocks,'fastwins':fastwins,'max_credit':maxcred}
 out.sort(key=lambda r:(r[0],r[6]));return out,diag
def capov(rr,cap):
 hp=[];out=[];sk=0;mo=0
 for i,r in enumerate(rr):
  while hp and hp[0][0]<=r[0]:heapq.heappop(hp)
  if len(hp)>=cap:sk+=1;continue
  out.append(r);heapq.heappush(hp,(r[1],i));mo=max(mo,len(hp))
 return out,mo,sk
def allm(s):return s['net']>=SYN['net'] and s['gross_loss']>=SYN['gross_loss'] and s['pf']>=SYN['pf'] and s['win']>=SYN['win'] and s['expectancy']>=SYN['expectancy']
rows=[];t0=time.time()
for cg,mc in itertools.product([1,2,4],[4,8,16]):
 rr,diag=build(cg,mc)
 for cap in [256,448,512,600,703,819]:
  ov,mo,sk=capov(rr,cap);rec=sorted(CORE+ov,key=lambda r:(r[0],0 if r[6].startswith('RENEW') else 1));s=A.score(rec)
  s.update(max_depth=args.maxd,scout_parents=args.scout,credit_gain=cg,max_credit=mc,cap=cap,renewal_candidates=len(rr),renewal_trades=len(ov),renewal_maxopen=mo,renewal_skips=sk,diag=diag,all_metrics=allm(s),all_plus_trades=allm(s) and s['trades']>=SYN['trades'],beat_synth_days=sum(s['daily'].get(d,0)>v for d,v in BEN['daily'].items()),beat_synth_weeks=sum(s['weekly'].get(w,0)>v for w,v in BEN['weekly'].items()))
  rows.append(s)
out={'unit':'DAA_APRIL_ADAPTIVE_CREDIT_GOVERNOR_136W3_BLOCK','status':'COMPLETE_ATOMIC_BLOCK','max_depth':args.maxd,'scout_parents':args.scout,'rows':rows,'runtime_s':time.time()-t0}
fn=O/f'apr_adaptive_credit_governor_136w3_d{args.maxd}_s{args.scout}.json';fn.write_text(json.dumps(out,indent=2))
print(json.dumps({'file':fn.name,'rows':len(rows),'all':sum(r['all_metrics'] for r in rows),'plus':sum(r['all_plus_trades'] for r in rows),'runtime_s':out['runtime_s'],'max_trades':max(r['trades'] for r in rows),'max_net':max(r['net'] for r in rows)}))