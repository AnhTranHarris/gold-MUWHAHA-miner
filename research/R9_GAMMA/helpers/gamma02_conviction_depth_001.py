import sys,json,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_ny16_17_18_subphase_lifecycle_001 as cur

def prepare():
 t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep()
 ei,ed,eh,ess,edisp=g.build_perm_extension_events(t,mid,h4,h1,m15,m5,2,50,200)
 parts=[]
 for hour in (16,17,18):
  p=np.nonzero((eh==hour)&(ess==4))[0]; idx=ei[p];dr=ed[p];disp=edisp[p]
  keep=np.zeros(idx.size,dtype=np.bool_);allowed=cur.SIGS[hour]
  for k,i in enumerate(idx):
   sig=(int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(dr[k]));keep[k]=sig in allowed
  idx=idx[keep];dr=dr[keep];disp=disp[keep];mins=((t[idx]//60000)%60).astype(np.int16)
  for lo,(tp,sl,hold) in cur.CFGS[hour].items():
   m=(mins>=lo)&(mins<lo+10);ii=idx[m];dd=dr[m];di=disp[m]
   ex,pnl,rs=g.precompute_outcomes(t,a,b,ii,dd,tp,sl,hold)
   times=t[ii];src=np.full(times.size,hour,dtype=np.int8)
   parts.append((times,ex,pnl,rs,src,di))
 arr=[np.concatenate([q[j] for q in parts]) for j in range(6)]
 o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def screen(cap,out):
 arr=prepare();t,ex,pnl,rs,src,disp=arr
 th16=[0,500,1000,1500,2000,3000,4000,6000]
 th17=[0,500,1000,1500,2000,3000,4000,6000]
 th18=[0,250,500,1000,1500,2000,3000,4000]
 rows=[]
 for a in th16:
  for b in th17:
   for c in th18:
    m=((src==16)&(disp>=a))|((src==17)&(disp>=b))|((src==18)&(disp>=c))
    ae,ap,asrc,ar,sk,mo=g.cap_select(t[m],ex[m],pnl[m],rs[m],src[m],cap)
    r=g.summarize(ae,ap,asrc,ar,sk,mo);r.update(cap=cap,min16=a,min17=b,min18=c);rows.append(r)
 rows.sort(key=lambda x:x['net'],reverse=True);json.dump(rows,open(out,'w'),indent=2)
 for r in rows[:30]:print(json.dumps({k:r[k] for k in ['net','trades','pf','exp','balance_dd','min16','min17','min18','sources']}),flush=True)
if __name__=='__main__':
 import argparse;ap=argparse.ArgumentParser();ap.add_argument('--cap',type=int,default=128);ap.add_argument('--out',required=True);z=ap.parse_args();screen(z.cap,z.out)
