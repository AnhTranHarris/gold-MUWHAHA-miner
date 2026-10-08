import json,datetime,heapq,numpy as np
from pathlib import Path
import gamma02_jan_watchdog119_grid_layer_refinement_131a as wd131a
import gamma02_campaign_heartbeat_019 as hb
import gamma02_m1_density as gmd
import gamma02_funded_cap_equity_dd_028 as eq
import gamma02_ny_campaign_inventory_portfolio_001 as gp
from general_session_state_discovery_131c import build_events

BASE=Path('/mnt/data/gamma02_jan_repro')
SYN=json.load(open(BASE/'r9_synth_jan_daily_weekly.json'))
OUT=BASE/'jan_session_portfolio_131d.json'

# Conservative rescue cells: recurrent, all-positive across observed days in discovery.
# Hour is UTC. Each uses only completed HTF states + current ladder event direction.
RESCUE_RULES=[
 ((2,1,1,-1,-1,1),(12000,4000,300000),'ASIA02_CONT'),
 ((7,1,-1,-1,-1,1),(0,0,120000),'LONDON07_ROTATE_LONG'),
 ((10,1,-1,-1,-1,1),(0,0,120000),'LONDON10_ROTATE_LONG'),
 ((13,1,-1,1,-1,-1),(12000,4000,300000),'OVERLAP13_SHORT'),
 ((16,1,-1,-1,-1,1),(0,0,120000),'OVERLAP16_LONG'),
 ((21,1,-1,-1,-1,1),(12000,4000,300000),'LATE21_LONG'),
]

def st(p):
 p=np.asarray(p,float);gpv=float(p[p>0].sum());gl=float(p[p<0].sum());bal=peak=dd=0.
 for v in p: bal+=float(v); peak=max(peak,bal); dd=max(dd,peak-bal)
 return dict(net=float(p.sum()),trades=int(len(p)),gross_profit=gpv,gross_loss=gl,pf=float(gpv/-gl if gl<0 else 999.),win=float(np.mean(p>0)) if len(p) else 0.,expectancy=float(np.mean(p)) if len(p) else 0.,balance_dd=float(dd))

def periods(t,X,P):
 d={};w={}
 for i,x in enumerate(X):
  z=datetime.datetime.fromtimestamp(int(t[int(x)])/1000,datetime.timezone.utc);ds=z.strftime('%Y-%m-%d');ws=f'{z.isocalendar().year}-W{z.isocalendar().week:02d}'
  d.setdefault(ds,[]).append(i);w.setdefault(ws,[]).append(i)
 return {k:st(P[np.asarray(v)]) for k,v in sorted(d.items())},{k:st(P[np.asarray(v)]) for k,v in sorted(w.items())}

def score(t,E,X,R,D,P,H,label,meta=None):
 o=np.lexsort((np.arange(len(E)),E));E,X,R,D,P,H=[z[o] for z in (E,X,R,D,P,H)]
 ex=eq.exact_equity_sweep(t,AASK,BBID,E,X,R,D,P); d,w=periods(t,X,P);s=st(P)
 s.update(name=label,equity_dd=float(ex[4]),min_total_equity=float(100000+ex[5]),maxopen=int(ex[9]),avg_hold_s=float(np.mean(H)) if len(H) else 0.,daily=d,weekly=w)
 s['positive_days']=sum(d.get(k,{'net':0})['net']>0 for k in SYN['daily'])
 s['beat_days']=sum(d.get(k,{'net':0})['net']>=v['net'] for k,v in SYN['daily'].items())
 s['positive_weeks']=sum(w.get(k,{'net':0})['net']>0 for k in SYN['weekly'])
 s['beat_weeks']=sum(w.get(k,{'net':0})['net']>=v['net'] for k,v in SYN['weekly'].items())
 s['daily_ratios']={k:float(d.get(k,{'net':0})['net']/v['net']) for k,v in SYN['daily'].items()}
 if meta:s.update(meta)
 return s,(E,X,R,D,P,H)

def cap_arrays(E,X,R,D,P,H,cap):
 heap=[];keep=[];mo=0;sk=0
 for k in range(len(E)):
  now=int(E[k])
  while heap and heap[0][0]<=now:heapq.heappop(heap)
  if len(heap)>=cap:sk+=1;continue
  keep.append(k);heapq.heappush(heap,(int(X[k]),k));mo=max(mo,len(heap))
 kk=np.asarray(keep,np.int64);return tuple(z[kk] for z in (E,X,R,D,P,H)),mo,sk

def dedup_market_tick(parts):
 # one new physical ticket per market tick globally across supplemental desks; priority = earlier part.
 seen=set();outs=[[] for _ in range(6)];sk=0
 for part in parts:
  E,X,R,D,P,H=part
  for k in range(len(E)):
   key=int(E[k])
   if key in seen:sk+=1;continue
   seen.add(key)
   for j,z in enumerate((E,X,R,D,P,H)):outs[j].append(z[k])
 return tuple(np.asarray(x,dtype=[np.int64,np.int64,np.int64,np.int8,float,float][j]) for j,x in enumerate(outs)),sk

def build_watchdog():
 holder={};orig=wd131a.cap.one
 def wrap(Q,capn):
  r,B=orig(Q,capn);holder['B']=B;return r,B
 wd131a.cap.one=wrap
 try: wd131a.build([1190,1190,1190,1190,1190,1100],703)
 finally: wd131a.cap.one=orig
 E,X,R,D,P,H,S=holder['B'];return E,X,R,D,P,H

def build_coverage():
 D0=DATA;t,a,b,mid,h4,h1,m15,m5=D0[:8];gmd.prep=lambda:D0
 E=hb.heartbeat_events(D0[:8],250,0);et,xt,pnl,reason,src=E;idx=np.searchsorted(t,et);b10=((et//60000)%60)//10;j60=np.searchsorted(t,et-60000,side='left');ticks60=idx-j60+1
 k=np.zeros(len(et),bool)
 k |= (src==9)&(b10==0)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
 k |= (src==11)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
 k |= (src==11)&(b10==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
 k |= (src==12)&np.isin(b10,[0,1,2])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
 k |= (src==12)&(b10==4)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=210)
 k |= (src==13)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
 k |= (src==14)&(b10==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==1)
 k |= (src==15)&np.isin(b10,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==1)
 parts=[tuple(z[k] for z in E)]
 E16=hb.heartbeat_events(D0[:8],250,2);e,x,p,r,s=E16;i=np.searchsorted(t,e);b16=((e//60000)%60)//10;k16=(s==16)&(h4[i]==1)&(h1[i]==1)&(m15[i]==1)&(m5[i]==-1)&np.isin(b16,[0,3,4]);parts.append(tuple(z[k16] for z in E16))
 arr=[np.concatenate([q[j] for q in parts]) for j in range(5)];o=np.argsort(arr[0],kind='stable');et,xt,pnl,reason,src=[z[o] for z in arr]
 # cap512 exact previous coverage behavior
 heap=[];keep=[]
 for n in range(len(et)):
  now=int(et[n]);
  while heap and heap[0][0]<=now:heapq.heappop(heap)
  if len(heap)>=512:continue
  keep.append(n);heapq.heappush(heap,(int(xt[n]),n))
 kk=np.asarray(keep,np.int64);et,xt,pnl=[z[kk] for z in (et,xt,pnl)]
 Ei=np.searchsorted(t,et).astype(np.int64);Xi=np.searchsorted(t,xt).astype(np.int64);Di=np.ones(len(Ei),np.int8);Ri=a[Ei].astype(np.int64);Hi=(xt-et)/1000.
 return Ei,Xi,Ri,Di,pnl.astype(float),Hi.astype(float)

def build_coldstart(ms=50,thr=450,cap=128):
 D0=DATA;t,a,b,mid,h4,h1,m15,m5=D0[:8];gmd.prep=lambda:D0
 E=hb.heartbeat_events(D0[:8],ms,0);et,xt,pnl,reason,src=E;idx=np.searchsorted(t,et);b10=((et//60000)%60)//10;j60=np.searchsorted(t,et-60000,side='left');ticks60=idx-j60+1
 k=(src==12)&np.isin(b10,[4,5])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=thr)
 et,xt,pnl=[z[k] for z in (et,xt,pnl)];o=np.argsort(et,kind='stable');et,xt,pnl=[z[o] for z in (et,xt,pnl)]
 Ei=np.searchsorted(t,et).astype(np.int64);Xi=np.searchsorted(t,xt).astype(np.int64);Di=np.ones(len(Ei),np.int8);Ri=a[Ei].astype(np.int64);Hi=(xt-et)/1000.
 return cap_arrays(Ei,Xi,Ri,Di,pnl.astype(float),Hi.astype(float),cap)[0]

def build_rescue(step=75,cap=64):
 D0=DATA;t,a,b,mid,h4,h1,m15,m5=D0[:8];es,ee=D0[-2:];ii,d=build_events(t,mid,step);m=(t[ii]>=es)&(t[ii]<ee);ii=ii[m];d=d[m];hour=((t[ii]//3600000)%24).astype(np.int8);parts=[]
 for key,(tp,sl,hold),name in RESCUE_RULES:
  hh,H4,H1,M15,M5,dr=key;mm=(hour==hh)&(h4[ii]==H4)&(h1[ii]==H1)&(m15[ii]==M15)&(m5[ii]==M5)&(d==dr);ev=ii[mm];dirs=d[mm];xt,p,rs=gp.precompute_outcomes(t,a,b,ev,dirs,tp,sl,hold)
  E=ev.astype(np.int64);X=np.searchsorted(t,xt).astype(np.int64);R=np.where(dirs>0,a[E],b[E]).astype(np.int64);D=dirs.astype(np.int8);H=(t[X]-t[E])/1000.;parts.append((E,X,R,D,p.astype(float),H.astype(float)))
 E,X,R,D,P,H=[np.concatenate([q[j] for q in parts]) for j in range(6)];o=np.argsort(E,kind='stable');return cap_arrays(E[o],X[o],R[o],D[o],P[o],H[o],cap)[0]

def merge_preserve_watchdog(wd,supp_parts,supp_cap=512):
 # Preserve Watchdog's explicit same-tick scaling exactly. De-duplicate only supplemental desks.
 supp,dup=dedup_market_tick(supp_parts)
 E,X,R,D,P,H=supp;o=np.argsort(E,kind='stable');supp=tuple(z[o] for z in supp)
 supp,mo,sk=cap_arrays(*supp,supp_cap)
 E=np.concatenate([wd[0],supp[0]]);X=np.concatenate([wd[1],supp[1]]);R=np.concatenate([wd[2],supp[2]]);D=np.concatenate([wd[3],supp[3]]);P=np.concatenate([wd[4],supp[4]]);H=np.concatenate([wd[5],supp[5]])
 o=np.lexsort((np.arange(len(E)),E));Q=tuple(z[o] for z in (E,X,R,D,P,H))
 return Q,dict(supp_cap=supp_cap,supp_dedup_skips=dup,supp_cap_skips=sk,supp_maxopen=mo)

DATA=wd131a.wd.prep_month(1);AASK=DATA[1];BBID=DATA[2];gmd.prep=lambda:DATA

def main():
 wd=build_watchdog(); cov=build_coverage();
 rows=[]
 baseQ,meta=merge_preserve_watchdog(wd,[cov],512); rows.append(score(DATA[0],*baseQ,'WD119_PLUS_COVERAGE',meta)[0])
 for coldcap in [64,128,256]:
  cold=build_coldstart(50,450,coldcap)
  Q,meta=merge_preserve_watchdog(wd,[cov,cold],512);meta.update(cold_cap=coldcap,rescue_cap=0);rows.append(score(DATA[0],*Q,f'PLUS_COLDSTART_C{coldcap}',meta)[0])
 for rcap in [32,64,128]:
  rescue=build_rescue(75,rcap)
  Q,meta=merge_preserve_watchdog(wd,[cov,rescue],512);meta.update(cold_cap=0,rescue_cap=rcap);rows.append(score(DATA[0],*Q,f'PLUS_RESCUE_C{rcap}',meta)[0])
 for coldcap in [64,128]:
  cold=build_coldstart(50,450,coldcap)
  for rcap in [32,64]:
   rescue=build_rescue(75,rcap)
   Q,meta=merge_preserve_watchdog(wd,[cov,cold,rescue],512);meta.update(cold_cap=coldcap,rescue_cap=rcap);rows.append(score(DATA[0],*Q,f'FIRM_SESSION_COLD{coldcap}_RESCUE{rcap}',meta)[0])
 rows.sort(key=lambda r:(r['positive_days'],r['beat_weeks'],r['beat_days'],r['net'],-r['equity_dd']),reverse=True)
 json.dump({'candidate':'GAMMA_02_JAN_SESSION_PORTFOLIO_131D','rules':{'month_day_week_feature':False,'watchdog':'frozen 131A working base','coverage':'recovered causal coverage V3','coldstart':'source12 bins 4/5 + completed HTF + causal quote-density gate','rescue':'recurrent all-positive session/HTF cells only','global_new_ticket_rule':'one supplemental new physical ticket per market tick; global cap703'},'rows':rows},open(OUT,'w'),indent=2)
 for r in rows:
  print({k:r[k] for k in ['name','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks','cold_cap','rescue_cap'] if k in r},'weeks',{k:round(v['net'],2) for k,v in r['weekly'].items()},flush=True)
if __name__=='__main__': main()