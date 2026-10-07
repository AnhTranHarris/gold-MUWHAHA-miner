import sys,json,numpy as np
sys.path.insert(0,'/mnt/data')
import gamma02_m1_density as gmd
import gamma02_ny_campaign_inventory_portfolio_001 as g
import gamma02_ny16_17_18_subphase_lifecycle_001 as cur

MAP17={
 'global3000':{0:3000,10:3000,20:3000,30:3000,40:3000,50:3000},
 'decayA':{0:6000,10:6000,20:4000,30:3000,40:2000,50:1000},
 'decayB':{0:8000,10:6000,20:4000,30:2000,40:1000,50:500},
 'decayC':{0:4000,10:4000,20:3000,30:2000,40:1000,50:500},
 'lateBias':{0:8000,10:8000,20:6000,30:3000,40:1000,50:0},
}
MAP18={
 'global1000':{0:(1000,10**9),10:(1000,10**9),20:(1000,10**9),30:(1000,10**9),40:(1000,10**9),50:(1000,10**9)},
 'lateClean':{0:(0,10**9),10:(0,10**9),20:(500,10**9),30:(500,10**9),40:(2000,10**9),50:(1000,6000)},
 'lateTight':{0:(0,10**9),10:(0,10**9),20:(1000,8000),30:(1000,10**9),40:(3000,8000),50:(1500,4000)},
}

def prep_variant(m17,m18,cap=128):
 t,a,b,mid,h4,h1,m15,m5,es,ee=gmd.prep();ei,ed,eh,ess,edisp=g.build_perm_extension_events(t,mid,h4,h1,m15,m5,2,50,200)
 parts=[]
 for hour in (16,17,18):
  p=np.nonzero((eh==hour)&(ess==4))[0];idx=ei[p];dr=ed[p];disp=edisp[p]
  keep=np.zeros(idx.size,dtype=np.bool_);allowed=cur.SIGS[hour]
  for k,i in enumerate(idx):keep[k]=(int(h4[i]),int(h1[i]),int(m15[i]),int(m5[i]),int(dr[k])) in allowed
  idx=idx[keep];dr=dr[keep];disp=disp[keep];mins=((t[idx]//60000)%60).astype(np.int16)
  for lo,(tp,sl,hold) in cur.CFGS[hour].items():
   m=(mins>=lo)&(mins<lo+10)
   if hour==16:m &= (disp>=500)
   elif hour==17:m &= (disp>=MAP17[m17][lo])
   else:
    mn,mx=MAP18[m18][lo];m &= (disp>=mn)&(disp<mx)
   ii=idx[m];dd=dr[m];ex,pnl,rs=g.precompute_outcomes(t,a,b,ii,dd,tp,sl,hold);times=t[ii];src=np.full(times.size,hour,dtype=np.int8)
   parts.append((times,ex,pnl,rs,src))
 arr=[np.concatenate([q[j] for q in parts]) for j in range(5)];o=np.argsort(arr[0],kind='stable');arr=[x[o] for x in arr]
 ae,ap,asrc,ar,sk,mo=g.cap_select(*arr,cap);r=g.summarize(ae,ap,asrc,ar,sk,mo);r.update(cap=cap,map17=m17,map18=m18);return r
if __name__=='__main__':
 rows=[]
 for a in MAP17:
  for b in MAP18:
   r=prep_variant(a,b,128);rows.append(r);print(json.dumps({k:r[k] for k in ['net','trades','pf','exp','balance_dd','map17','map18','sources']}),flush=True)
 rows.sort(key=lambda x:x['net'],reverse=True);json.dump(rows,open('/mnt/data/gamma02_time_decay_conviction_001.json','w'),indent=2)