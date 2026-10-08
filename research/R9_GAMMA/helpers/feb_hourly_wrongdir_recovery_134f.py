import sys,json,datetime
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
BASE=Path('/mnt/data/gamma02_jan_repro');D0=V.load_month();t,a,b,mid,h4,h1,m15,m5=D0[:8]
z=np.load(BASE/'feb_hourly_heartbeat_stream_134b.npz');E,X,R,D,P,H=[z[k] for k in ['E','X','R','D','P','H']];z.close();ei=E.astype(np.int64);ent=np.where(D>0,a[ei],b[ei]).astype(np.int64)
DELAYS=[2,5,10,15,30,60];THR=[-.1,-.25,-.5,-1,-2,-4];HOLDS=[5,10,15,30,60,120,300]
def met(p):
 p=np.asarray(p,float);gp=float(p[p>0].sum());gl=float(p[p<=0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gross_profit=gp,gross_loss=gl,pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)) if len(p) else 0,exp=float(np.mean(p)) if len(p) else 0)
def main():
 rows=[]; candidates_by_combo={}
 for delay in DELAYS:
  ri=np.searchsorted(t,t[ei]+delay*1000,side='left');ri=np.minimum(ri,len(t)-1);alive=ri<X;markpx=np.where(D>0,b[ri],a[ri]).astype(np.int64);mark=((markpx-ent)*D)/1000.-.02
  print('delay',delay,'alive',int(alive.sum()),'neg',int((alive&(mark<0)).sum()),flush=True)
  for thr in THR:
   m0=alive&(mark<=thr)
   if m0.sum()<30:continue
   jj=ri[m0];rd=(-D[m0]).astype(np.int8);orig=D[m0];hour=((t[jj]//3600000)%24).astype(np.int8);b10=((t[jj]//600000)%6).astype(np.int8)
   j60=np.searchsorted(t,t[jj]-60000,side='left');ticks60=jj-j60+1;act=np.select([ticks60<=200,ticks60<=500],[0,1],default=2).astype(np.int8)
   sig=np.stack((hour,b10,h4[jj],h1[jj],m15[jj],m5[jj],orig,act),axis=1)
   dts=[datetime.datetime.fromtimestamp(int(x)/1000,datetime.timezone.utc) for x in t[jj]];day=np.array([x.strftime('%Y-%m-%d') for x in dts]);week=np.array([f'{x.isocalendar().year}-W{x.isocalendar().week:02d}' for x in dts])
   rent=np.where(rd>0,a[jj],b[jj]).astype(np.int64)
   for hold in HOLDS:
    rx=np.searchsorted(t,t[jj]+hold*1000,side='left');rx=np.minimum(rx,len(t)-1);rex=np.where(rd>0,b[rx],a[rx]).astype(np.int64);rp=((rex-rent)*rd)/1000.-.02
    for key in np.unique(sig,axis=0):
     m=np.all(sig==key,axis=1);n=int(m.sum())
     if n<25:continue
     p=rp[m];ds=day[m];ws=week[m];dn=[float(p[ds==z].sum()) for z in np.unique(ds)];wn=[float(p[ws==z].sum()) for z in np.unique(ws)];r=met(p)
     r.update(delay=delay,trigger=thr,hold=hold,hour=int(key[0]),b10=int(key[1]),h4=int(key[2]),h1=int(key[3]),m15=int(key[4]),m5=int(key[5]),orig_direction=int(key[6]),activity=int(key[7]),days=len(dn),weeks=len(wn),positive_day_frac=float(np.mean(np.array(dn)>0)),positive_week_frac=float(np.mean(np.array(wn)>0)),median_day=float(np.median(dn)),min_day=float(np.min(dn)))
     rows.append(r)
 # robust exact-state selections
 by={}
 for r in rows:
  if r['days']<3 or r['weeks']<2 or r['positive_day_frac']<.67 or r['positive_week_frac']<.5 or r['pf']<2.0 or r['exp']<.25 or r['net']<=0 or r['median_day']<=0:continue
  key=(r['hour'],r['b10'],r['h4'],r['h1'],r['m15'],r['m5'],r['orig_direction'],r['activity'])
  score=r['net']*min(r['pf'],10)/10*(.5+r['positive_day_frac']/2)
  if key not in by or score>by[key][0]:by[key]=(score,r)
 sel=[v[1] for v in by.values()]
 (BASE/'feb_hourly_wrongdir_recovery_134f.json').write_text(json.dumps({'selected':sel,'top_rows':sorted(rows,key=lambda x:x['net'],reverse=True)[:1000]},indent=2))
 print('SELECTED',len(sel),'potential net sum',sum(x['net'] for x in sel),flush=True)
 for r in sorted(sel,key=lambda x:x['net'],reverse=True)[:50]:print(json.dumps(r),flush=True)
if __name__=='__main__':main()