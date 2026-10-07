import sys,json,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_ny16_17_18_subphase_lifecycle_001 as cur
import gamma02_london_overlap_portfolio_001 as lo
import gamma02_london_overlap_markout_stream_001 as lom
import gamma02_time_decay_conviction_001 as td
from gamma02_london_ny_hourly_conviction_002 import THR

def dedup_last(idx,*arrs):
    if len(idx)==0:return (idx,)+arrs
    keep=np.r_[idx[1:]!=idx[:-1],True]
    return (idx[keep],)+tuple(a[keep] for a in arrs)

def build_lo(t,a,b,mid,h4,h1,m15,m5):
 idx,dr,hr,disp=lom.build_events_stream(t,mid,h4,h1);parts=[]
 for hour,H4,H1,M15,M5,D,hs in lo.RULES:
  m=(hr==hour)&(h4[idx]==H4)&(h1[idx]==H1)&(m15[idx]==M15)&(m5[idx]==M5)&(dr==D)&(disp>=THR.get(hour,0))
  ii=idx[m];dd=dr[m];di=disp[m];ii,dd,di=dedup_last(ii,dd,di)
  ent=np.where(dd>0,a[ii],b[ii]).astype(np.int64);j=np.searchsorted(t,t[ii]+hs*1000,side='left');j=np.minimum(j,len(t)-1);ex=np.where(dd>0,b[j],a[j]);p=((ex-ent)*dd)/1000.-0.02
  parts.append((t[ii],t[j],p,np.full(ii.size,3,np.int8),np.full(ii.size,hour,np.int16)))
 arr=[np.concatenate([q[k] for q in parts]) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def build_ny(t,a,b,mid,h4,h1,m15,m5):
 ei,ed,eh,ess,edisp=g.build_perm_extension_events(t,mid,h4,h1,m15,m5,2,50,200);parts=[];m17=td.MAP17['lateBias'];m18=td.MAP18['lateClean']
 for hour in (16,17,18):
  p=np.nonzero((eh==hour)&(ess==4))[0];idx=ei[p];dr=ed[p];disp=edisp[p];idx,dr,disp=dedup_last(idx,dr,disp)
  keep=np.zeros(idx.size,dtype=np.bool_);allowed=cur.SIGS[hour]
  for k,i in enumerate(idx):keep[k]=(int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(dr[k])) in allowed
  idx=idx[keep];dr=dr[keep];disp=disp[keep];mins=((t[idx]//60000)%60).astype(np.int16)
  for lo0,(tp,sl,hold) in cur.CFGS[hour].items():
   m=(mins>=lo0)&(mins<lo0+10)
   if hour==16:m &= disp>=500
   elif hour==17:m &= disp>=m17[lo0]
   else:
    mn,mx=m18[lo0];m &= (disp>=mn)&(disp<mx)
   ii=idx[m];dd=dr[m];ex,pnl,rs=g.precompute_outcomes(t,a,b,ii,dd,tp,sl,hold);parts.append((t[ii],ex,pnl,rs,np.full(ii.size,hour,np.int16)))
 arr=[np.concatenate([q[k] for q in parts]) for k in range(5)];o=np.argsort(arr[0],kind='stable');return tuple(x[o] for x in arr)

def run(caps,out):
 t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();L=build_lo(t,a,b,mid,h4,h1,m15,m5);N=build_ny(t,a,b,mid,h4,h1,m15,m5);arr=[np.concatenate((L[k],N[k])) for k in range(5)];o=np.argsort(arr[0],kind='stable');arr=[x[o] for x in arr];rows=[]
 for cap in caps:
  ae,ap,asrc,ar,sk,mo=g.cap_select(*arr,cap);r=g.summarize(ae,ap,asrc,ar,sk,mo);r['cap']=cap;rows.append(r);print(json.dumps({k:r[k] for k in ['cap','net','trades','pf','exp','balance_dd','maxopen','skips','sources']}),flush=True)
 json.dump({'candidate':'GAMMA02_ONE_EVENT_PER_TICK_AUDIT_014','policy':'deepest newly crossed level only per tick per source','rows':rows},open(out,'w'),indent=2)
if __name__=='__main__':
 import argparse;ap=argparse.ArgumentParser();ap.add_argument('--caps',default='32,64,96,128,160,192,256,384,512');ap.add_argument('--out',required=True);z=ap.parse_args();run([int(x) for x in z.caps.split(',')],z.out)