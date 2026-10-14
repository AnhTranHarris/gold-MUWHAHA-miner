"""GRID0272 source lineage 131A: replace child fill kernel ONLY. Research only.
250ms positive latency, real next original quote; $0.20 RT cost, no synthetic prices.
Preserves source parent ancestry and historical cell/Watchdog as-of gate.
COMPARE latency0 and fee.02 to original kernel as a unit-integration control.
"""
import json,sys,time,numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data/GRID0272_JAN_COMBINATIONS/ORIGINAL')
import stmr_base as c
@njit(cache=True)
def renewal_owned_delayed(t,a,b,parent_ei,parent_xi,dirs,quantum_raw,rearm_raw,initial_rearm_raw,desk_code,latency_ms,fee):
 cap=3_000_000
 ent_i=np.empty(cap,np.int64);ex_i=np.empty(cap,np.int64);ent_raw=np.empty(cap,np.int64);out_d=np.empty(cap,np.int8)
 pnl=np.empty(cap,np.float64);hold=np.empty(cap,np.float64);owner=np.empty(cap,np.int32);desk=np.empty(cap,np.int8)
 n=0;wins=0;resid=0
 for k in range(parent_ei.size):
  d=dirs[k];p0=parent_ei[k];end_i=parent_xi[k];ref=int(b[p0] if d>0 else a[p0])
  cur_i=-1;cur_raw=0;open_trade=False
  pending_at=-1;pending_exp=-1
  if initial_rearm_raw<=0:
   if latency_ms==0:
    cur_i=p0;cur_raw=int(a[cur_i] if d>0 else b[cur_i]);open_trade=True
   else:pending_at=t[p0]+latency_ms;pending_exp=t[p0]+2000
  j=p0+1
  while j<end_i:
   fav_px=int(b[j] if d>0 else a[j])
   if pending_at>=0 and not open_trade:
    if t[j]>=pending_at:
     if t[j]<=pending_exp:
      cur_i=j;cur_raw=int(a[j] if d>0 else b[j]);open_trade=True
     pending_at=-1
     j+=1;continue
   if not open_trade:
    if pending_at>=0:j+=1;continue
    need=initial_rearm_raw if cur_i==-1 else rearm_raw
    if (fav_px-ref)*d>=need:
     if latency_ms==0:
      cur_i=j;cur_raw=int(a[j] if d>0 else b[j]);open_trade=True
     else:pending_at=t[j]+latency_ms;pending_exp=t[j]+2000
    j+=1;continue
   fav=(fav_px-cur_raw)*d
   if fav>=quantum_raw:
    ent_i[n]=cur_i;ex_i[n]=j;ent_raw[n]=cur_raw;out_d[n]=d;pnl[n]=fav/1000.-fee;hold[n]=(t[j]-t[cur_i])/1000.;owner[n]=k;desk[n]=desk_code;n+=1;wins+=1
    ref=fav_px;open_trade=False;cur_i=j
   j+=1
  if open_trade:
   px=int(b[end_i] if d>0 else a[end_i]);ent_i[n]=cur_i;ex_i[n]=end_i;ent_raw[n]=cur_raw;out_d[n]=d;pnl[n]=((px-cur_raw)*d)/1000.-fee;hold[n]=(t[end_i]-t[cur_i])/1000.;owner[n]=k;desk[n]=desk_code;n+=1;resid+=1
 return ent_i[:n],ex_i[:n],ent_raw[:n],out_d[:n],pnl[:n],hold[:n],owner[:n],desk[:n],wins,resid

def run(latency_ms,fee,qmap,cap):
 def raw_quote(t,a,b):return np.asarray(a,dtype=np.int32),np.asarray(b,dtype=np.int32)
 c.materialize=raw_quote
 import gamma02_jan_watchdog119_grid_layer_refinement_131a as j
 import gamma02_083_heat_parent_ownership_084 as owner
 source=owner.renewal_owned
 def adapter(t,a,b,pei,pxi,pd,q,r,ri,desk):
  return renewal_owned_delayed(t,a,b,pei,pxi,pd,q,r,ri,desk,latency_ms,fee)
 j.renewal_owned=adapter
 tic=time.perf_counter();res=j.build(qmap,cap)
 res.update(latency_ms=latency_ms,fee=fee,full_original_parent_source=True,execution='raw Ducaskopy BidAsk accepted quote at first >=request+latency; session P75 normalized price removed',source='131A unchanged parent+state+watchdog+cap kernels except child fill replacement',seconds=time.perf_counter()-tic)
 out=f'/mnt/data/GRID0272_JAN_COMBINATIONS/delayed_{latency_ms}_{int(fee*100):02d}_{int(qmap[0])}_cap{cap}.json'
 open(out,'w').write(json.dumps(res,indent=2))
 print(json.dumps({k:res.get(k) for k in ['latency_ms','fee','qmap_raw','net','trades','gross_loss','pf','win','equity_dd','balance_dd','maxopen_exact','unlocks','relocks','seconds']}),flush=True)
if __name__=='__main__':
 run(int(sys.argv[1]),float(sys.argv[2]),[int(v) for v in sys.argv[3].split(',')],int(sys.argv[4]))
