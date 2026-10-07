import sys,json,numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
import stmr_janjul as j, stmr_base as c
from gamma02_feb_native_markout_124 import build_events

TP_LEVELS=np.array([2000,4000,6000,8000,12000,20000,40000,80000],np.int32)
SL_LEVELS=np.array([2000,4000,6000,8000,12000,20000,40000,80000],np.int32)
HOLDS=np.array([15000,30000,60000,120000,300000,600000],np.int64)

@njit(cache=True)
def precompute_hits(t,a,b,idx,d,tp_levels,sl_levels,holds):
 n=idx.size; nt=tp_levels.size; ns=sl_levels.size; nh=holds.size
 tp_t=np.full((n,nt),np.int64(9223372036854775807));tp_p=np.zeros((n,nt),np.float64)
 sl_t=np.full((n,ns),np.int64(9223372036854775807));sl_p=np.zeros((n,ns),np.float64)
 h_t=np.empty((n,nh),np.int64);h_p=np.empty((n,nh),np.float64)
 for k in range(n):
  i0=idx[k];dd=int(d[k]);er=int(a[i0] if dd>0 else b[i0]);done_tp=np.zeros(nt,np.uint8);done_sl=np.zeros(ns,np.uint8);next_h=0;jj=i0+1;end_t=t[i0]+holds[-1]
  while jj<t.size and t[jj]<=end_t:
   px=int(b[jj] if dd>0 else a[jj]);fav=(px-er)*dd;adv=-fav
   for z in range(nt):
    if done_tp[z]==0 and fav>=tp_levels[z]:tp_t[k,z]=t[jj];tp_p[k,z]=fav/1000.-.02;done_tp[z]=1
   for z in range(ns):
    if done_sl[z]==0 and adv>=sl_levels[z]:sl_t[k,z]=t[jj];sl_p[k,z]=fav/1000.-.02;done_sl[z]=1
   while next_h<nh and t[jj]>=t[i0]+holds[next_h]:
    h_t[k,next_h]=t[jj];h_p[k,next_h]=fav/1000.-.02;next_h+=1
   if next_h>=nh and done_tp.sum()==nt and done_sl.sum()==ns:break
   jj+=1
  if jj>=t.size:jj=t.size-1
  px=int(b[jj] if dd>0 else a[jj]);fav=(px-er)*dd
  while next_h<nh:
   h_t[k,next_h]=t[jj];h_p[k,next_h]=fav/1000.-.02;next_h+=1
 return tp_t,tp_p,sl_t,sl_p,h_t,h_p

def metrics(p):
 gp=float(p[p>0].sum());gl=float(p[p<=0].sum());return dict(net=float(p.sum()),trades=int(len(p)),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)),exp=float(np.mean(p)))

def evaluate(tp_t,tp_p,sl_t,sl_p,h_t,h_p):
 rows=[]
 for hi,hm in enumerate(HOLDS):
  for ti in range(-1,len(TP_LEVELS)):
   for si in range(-1,len(SL_LEVELS)):
    n=h_t.shape[0];p=np.empty(n,np.float64)
    for k in range(n):
     ht=h_t[k,hi];tt=tp_t[k,ti] if ti>=0 else np.int64(9223372036854775807);st=sl_t[k,si] if si>=0 else np.int64(9223372036854775807)
     if tt<=st and tt<=ht:p[k]=tp_p[k,ti]
     elif st<tt and st<=ht:p[k]=sl_p[k,si]
     else:p[k]=h_p[k,hi]
    m=metrics(p);m.update(tp=0 if ti<0 else int(TP_LEVELS[ti]),sl=0 if si<0 else int(SL_LEVELS[si]),hold_ms=int(hm));rows.append(m)
 rows.sort(key=lambda r:r['net'],reverse=True);return rows

def main():
 t,sa,sb,start,end=j.load_month(2,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);h4,h1,m15,m5=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)))
 idx,d,hr,sig,disp=build_events(t,mid,h4,h1,m15,m5,start,end,50)
 M=json.load(open('/mnt/data/gamma02_feb_native_markout_124.json'))['rows'];cells=[z for z in M if z['n']>=200 and z['mean300']>=1.0 and z['pf300']>=1.5];cells.sort(key=lambda z:z['net300'],reverse=True)
 out=[]
 for ci,z in enumerate(cells):
  m=(hr==z['hour'])&(sig==z['sigcode']);ii=idx[m];dd=d[m]
  H=precompute_hits(t,a,b,ii,dd,TP_LEVELS,SL_LEVELS,HOLDS);rows=evaluate(*H)
  q=[r for r in rows if r['pf']>=2.0 and r['win']>=.60];q.sort(key=lambda r:r['net'],reverse=True)
  rec=dict(cell={k:z[k] for k in ['hour','sigcode','h4','h1','m15','m5','direction','n','net300','mean300','pf300','win300']},top_net=rows[:12],top_quality=q[:12]);out.append(rec)
  json.dump({'candidate':'GAMMA02_FEB_NATIVE_LIFECYCLE_QUALITY_125','cells':out},open('/mnt/data/gamma02_feb_lifecycle_quality_125.partial.json','w'),indent=2)
 json.dump({'candidate':'GAMMA02_FEB_NATIVE_LIFECYCLE_QUALITY_125','cells':out},open('/mnt/data/gamma02_feb_lifecycle_quality_125.json','w'),indent=2)
if __name__=='__main__':main()
