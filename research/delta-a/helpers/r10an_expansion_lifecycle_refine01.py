import pandas as pd, numpy as np, json, time
from numba import njit
from pathlib import Path
st=time.time(); raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'; ev='/mnt/data/SA100_R10AM_P4P6_HARVEST_EVENTS01.csv'
E=pd.read_csv(ev); C=E[E.owner=='CONT'].copy().sort_values('time_ms').reset_index(drop=True)
mask=(C.range30>18.9)|((C.range30<=18.9)&(C.eff15<=0.32)&(C.tick15>9.83)&(C.disp120>0.56)); C=C[mask].copy().sort_values('time_ms').reset_index(drop=True)
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=D.timestamp_ms_utc.to_numpy(np.int64);mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.;evms=C.time_ms.to_numpy(np.int64);side=C.cross_dir.to_numpy(np.int8);eix=np.searchsorted(t,evms);eix=np.minimum(eix,len(t)-1)
@njit
def sim(t,mid,evms,side,eix,stop,act,trail,maxhold):
 out=np.empty(len(evms),np.float64); hold=np.empty(len(evms),np.float64)
 for q in range(len(evms)):
  i=eix[q];sd=side[q];entry=mid[i]+.10*sd; sl=entry-stop*sd; end=evms[q]+maxhold*1000;k=i;armed=False;done=False;ex=entry
  while k<len(t) and t[k]<=end:
   px=mid[k]-.10 if sd>0 else mid[k]+.10;pnl=(px-entry)*sd
   if pnl<=-stop: ex=entry-stop*sd;done=True;break
   if pnl>=act:
    armed=True;cand=px-trail*sd
    if (sd>0 and cand>sl) or (sd<0 and cand<sl):sl=cand
   if armed and ((sd>0 and px<=sl) or (sd<0 and px>=sl)):ex=px;done=True;break
   k+=1
  if not done:
   k=np.searchsorted(t,end,side='right')-1
   if k<i:k=i
   ex=mid[k]-.10 if sd>0 else mid[k]+.10
  out[q]=(ex-entry)*sd;hold[q]=(t[k]-evms[q])/1000.
 return out,hold
cut=int(len(C)*.6);rows=[]
for stop in [.5,.75,1.,1.5,2.,3.,5.]:
 for act,trail in [(.05,.02),(.10,.03),(.20,.05),(.30,.08),(.50,.10)]:
  for mh in [30,60,120]:
   p,h=sim(t,mid,evms,side,eix,stop,act,trail,mh);r={'stop':stop,'act':act,'trail':trail,'maxhold':mh}
   for lab,s in [('disc',slice(0,cut)),('hold',slice(cut,None)),('all',slice(None))]:
    x=p[s];gp=x[x>0].sum();gl=x[x<0].sum();r.update({f'{lab}_net':float(x.sum()),f'{lab}_win':float((x>0).mean()),f'{lab}_gl':float(gl),f'{lab}_pf':float(gp/(-gl)) if gl<0 else None})
   if r['disc_net']>0 and r['hold_net']>0 and r['disc_win']>.5 and r['hold_win']>.5:rows.append(r)
res=pd.DataFrame(rows)
if len(res):res=res.sort_values(['all_gl','all_net'],ascending=[False,False])
res.to_csv('/mnt/data/SA100_R10AN_EXPANSION_LIFECYCLE_CANDIDATES01.csv',index=False)
out={'status':'COMPLETE_EXACT_RAW_TICK','selected_events':len(C),'candidates':len(res),'top_loss_efficiency':res.head(20).to_dict('records') if len(res) else [],'top_net':res.sort_values('all_net',ascending=False).head(10).to_dict('records') if len(res) else [],'elapsed_s':time.time()-st};Path('/mnt/data/SA100_R10AN_EXPANSION_LIFECYCLE_CANDIDATES01.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))