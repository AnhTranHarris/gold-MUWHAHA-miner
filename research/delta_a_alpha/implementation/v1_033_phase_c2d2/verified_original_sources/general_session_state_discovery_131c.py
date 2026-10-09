import json,datetime,time,numpy as np
from numba import njit
import gamma02_m1_density as gmd

@njit(cache=True)
def build_events(t,mid,step_raw=250):
 cap=2000000;idx=np.empty(cap,np.int64);dr=np.empty(cap,np.int8);n=0
 cur=np.int64(-1);anchor=0;up=0;dn=0
 for i in range(t.size):
  minute=(t[i]//60000)*60000;m=int(mid[i])
  if minute!=cur:
   cur=minute;anchor=m;up=0;dn=0;continue
  du=m-anchor;dd=anchor-m
  # one event max per direction per market tick; jump resets to current attained ladder rung
  if du>=up+step_raw:
   up=(du//step_raw)*step_raw
   if n<cap:idx[n]=i;dr[n]=1;n+=1
  if dd>=dn+step_raw:
   dn=(dd//step_raw)*step_raw
   if n<cap:idx[n]=i;dr[n]=-1;n+=1
 return idx[:n],dr[:n]

def pnl_horizon(t,a,b,idx,d,hsec):
 x=np.searchsorted(t,t[idx]+int(hsec*1000),side='left');x=np.minimum(x,len(t)-1);e=np.where(d>0,a[idx],b[idx]).astype(np.int64);z=np.where(d>0,b[x],a[x]).astype(np.int64);p=((z-e)*d)/1000.-.02;return x,p

def st(p):
 p=np.asarray(p,float);g=float(p[p>0].sum());l=float(p[p<0].sum());return {'net':float(p.sum()),'n':int(len(p)),'pf':float(g/-l if l<0 else 999.),'win':float(np.mean(p>0)),'exp':float(np.mean(p)),'gl':l}

def main():
 D=gmd.prep();t,a,b,mid,h4,h1,m15,m5=D[:8];es,ee=D[-2:]
 ii,d=build_events(t,mid,250);m=(t[ii]>=es)&(t[ii]<ee);ii=ii[m];d=d[m];print('events',len(ii),flush=True)
 hour=((t[ii]//3600000)%24).astype(np.int8);sig=np.stack((hour,h4[ii],h1[ii],m15[ii],m5[ii],d),axis=1)
 # calendar tags at entry
 day=(t[ii]//86400000).astype(np.int64)
 dts=[datetime.datetime.fromtimestamp(int(x)/1000,datetime.timezone.utc) for x in t[ii]]
 week=np.asarray([z.isocalendar().week for z in dts],np.int16)
 rows=[];frontiers={}
 for hsec in [5,10,20,30,60,120]:
  x,p=pnl_horizon(t,a,b,ii,d,hsec);keys=np.unique(sig,axis=0);rr=[]
  for k in keys:
   mm=np.all(sig==k,axis=1);n=int(mm.sum())
   if n<12:continue
   q=p[mm];days=np.unique(day[mm]);weeks=np.unique(week[mm]);dn=[]
   for z in days:dn.append(float(q[day[mm]==z].sum()))
   wn=[]
   for z in weeks:wn.append(float(q[week[mm]==z].sum()))
   s=st(q);s.update(hour=int(k[0]),h4=int(k[1]),h1=int(k[2]),m15=int(k[3]),m5=int(k[4]),direction=int(k[5]),horizon_s=hsec,days=int(len(days)),weeks=int(len(weeks)),positive_day_frac=float(np.mean(np.asarray(dn)>0)),median_day_net=float(np.median(dn)),min_day_net=float(np.min(dn)),positive_week_frac=float(np.mean(np.asarray(wn)>0)),median_week_net=float(np.median(wn)));rr.append(s)
  # robust selected: enough recurrence, meaningful edge; allow 2-day cells only if both positive & strong
  sel=[]
  for r in rr:
   recurrent=(r['days']>=3 and r['positive_day_frac']>=0.67 and r['weeks']>=2 and r['positive_week_frac']>=0.5) or (r['days']==2 and r['positive_day_frac']==1 and r['weeks']>=2)
   if recurrent and r['pf']>=1.5 and r['exp']>=0.40 and r['net']>0 and r['median_day_net']>0:sel.append(r)
  # apply selected keys to event stream; each cell uses this horizon, keep once
  keyset={(r['hour'],r['h4'],r['h1'],r['m15'],r['m5'],r['direction']) for r in sel}
  mask=np.asarray([tuple(map(int,z)) in keyset for z in sig],bool);q=p[mask];xx=x[mask]
  summary=st(q) if len(q) else {'net':0,'n':0,'pf':0,'win':0,'exp':0,'gl':0}
  # daily/weekly realized by entry date for diagnostics
  dd={};ww={}
  for j in np.flatnonzero(mask):
   z=dts[j];ds=z.strftime('%Y-%m-%d');ws=f'{z.isocalendar().year}-W{z.isocalendar().week:02d}';dd.setdefault(ds,[]).append(float(p[j]));ww.setdefault(ws,[]).append(float(p[j]))
  summary.update(cells=len(sel),daily={k:st(v) for k,v in sorted(dd.items())},weekly={k:st(v) for k,v in sorted(ww.items())});frontiers[str(hsec)]=summary;rows.extend(rr)
  print('H',hsec,'cells',len(sel),summary,flush=True)
 json.dump({'candidate':'GENERAL_SESSION_STATE_DISCOVERY_131C','event_step_raw':250,'frontiers':frontiers,'cell_rows':rows},open('/mnt/data/gamma02_jan_repro/general_session_state_discovery_131c.json','w'),indent=2)
if __name__=='__main__':main()