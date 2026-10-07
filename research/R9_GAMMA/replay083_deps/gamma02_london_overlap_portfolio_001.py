import sys,json,time,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_london_overlap_markout_stream_001 as lom

RULES=[
(7,1,1,-1,-1,1,1800),(8,1,1,-1,-1,1,300),(8,1,1,-1,1,1,900),
(9,1,1,-1,-1,1,1800),(9,1,1,1,-1,1,1800),
(11,1,1,-1,-1,1,1800),(11,1,1,-1,1,1,1800),(11,1,1,1,-1,1,900),
(12,1,1,-1,-1,1,1800),(12,1,1,-1,1,1,900),(12,1,1,1,-1,1,1800),
(13,1,1,-1,-1,1,1800),(13,1,1,-1,1,1,1800),(13,1,1,1,-1,1,1800),
(14,1,1,-1,-1,1,1800),(14,1,1,-1,1,1,900),
(15,1,1,-1,1,1,1800),(15,1,1,1,-1,1,1800),(15,1,1,1,1,1,1800),
]

def prepare():
 t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep(); idx,dr,hr,disp=lom.build_events_stream(t,mid,h4,h1)
 parts=[]
 for hour,H4,H1,M15,M5,D,hs in RULES:
  m=(hr==hour)&(h4[idx]==H4)&(h1[idx]==H1)&(m15[idx]==M15)&(m5[idx]==M5)&(dr==D)
  ii=idx[m];dd=dr[m];di=disp[m]
  ent=np.where(dd>0,a[ii],b[ii]).astype(np.int64)
  j=np.searchsorted(t,t[ii]+hs*1000,side='left');j=np.minimum(j,len(t)-1)
  ex=np.where(dd>0,b[j],a[j]).astype(np.int64)
  pnl=((ex-ent)*dd)/1000.-0.02
  group=np.full(ii.size,0 if hour<=9 else (1 if hour<=12 else 2),dtype=np.int8)
  src=np.full(ii.size,hour,dtype=np.int8);rs=np.full(ii.size,3,dtype=np.int8)
  parts.append((t[ii],t[j],pnl,rs,src,di,group))
 arr=[np.concatenate([q[k] for q in parts]) for k in range(7)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def one(arr,cap,thr):
 et,xt,pnl,rs,src,disp,grp=arr
 m=np.ones(et.size,dtype=bool)
 for k,v in enumerate(thr):m &= ((grp!=k)|(disp>=v))
 ae,ap,asrc,ar,sk,mo=g.cap_select(et[m],xt[m],pnl[m],rs[m],src[m],cap)
 r=g.summarize(ae,ap,asrc,ar,sk,mo);r.update(cap=cap,thr_early=thr[0],thr_mid=thr[1],thr_overlap=thr[2]);return r

def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--cap',type=int,default=64);ap.add_argument('--out',required=True);z=ap.parse_args()
 arr=prepare();vals=[0,250,500,1000,1500,2000,3000,4000,6000]
 base=one(arr,z.cap,(0,0,0)); rows=[base]
 # atomic one-dimensional screens
 for grp in range(3):
  for v in vals[1:]:
   th=[0,0,0];th[grp]=v;rows.append(one(arr,z.cap,tuple(th)))
 # combine best one-dimensional thresholds and nearby zeros
 best=[]
 for grp in range(3):
  rr=[x for x in rows if sum(int(x[k]>0) for k in ['thr_early','thr_mid','thr_overlap'])<=1]
  key=['thr_early','thr_mid','thr_overlap'][grp]
  q=[x for x in rr if (x[key]>0 or (x['thr_early']==x['thr_mid']==x['thr_overlap']==0))]
  best.append(max(q,key=lambda x:x['net'])[key])
 combos=set([tuple(best),(0,best[1],best[2]),(best[0],0,best[2]),(best[0],best[1],0)])
 for th in combos:
  if th!=(0,0,0):rows.append(one(arr,z.cap,th))
 rows.sort(key=lambda x:x['net'],reverse=True);json.dump({'candidate':'GAMMA02_LONDON_OVERLAP_PORTFOLIO_001','rows':rows},open(z.out,'w'),indent=2)
 for r in rows[:12]:print(json.dumps({k:r[k] for k in ['net','trades','pf','exp','balance_dd','cap','thr_early','thr_mid','thr_overlap','sources']}),flush=True)
if __name__=='__main__':main()