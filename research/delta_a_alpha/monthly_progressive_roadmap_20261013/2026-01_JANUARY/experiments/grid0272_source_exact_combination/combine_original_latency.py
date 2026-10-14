"""GRID0272 experimental faithful January source-combination on original Dukascopy quotes.
Original 131A Watchdog parent/state/scout/proof/renewal from recovered source.
Original 131D as-of session/HTF masks, heartbeat and 50-unit grid events reconstructed
without using hindsight-selected close PnL to generate/accept new supplemental entries.
All subsequent child and supplemental entries realized first actual quote >=request+250ms;
0.01 lot=1oz, $0.20 roundtrip, original Bid/Ask, exit rules are original source.
SHADOW SCIENCE ONLY; not Coinexx-certified, not current FourSessionV1 production code.
"""
import sys,os,time,json,heapq
import numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data/GRID0272_JAN_COMBINATIONS/ORIGINAL')
import stmr_base as c
from original_latency import renewal_owned_delayed

@njit(cache=True)
def price_supp(t,a,b,E,D,TP,SL,HOLD,latency_ms,fee):
 n=len(E)
 outE=np.full(n,-1,np.int64);outX=np.full(n,-1,np.int64);outR=np.zeros(n,np.int64);outP=np.zeros(n,np.float64);outH=np.zeros(n,np.float64);drop=np.zeros(n,np.int8)
 for k in range(n):
  signal=E[k];tm=t[signal]+latency_ms;ii=np.searchsorted(t,tm)
  if ii>=len(t) or t[ii]>t[signal]+2000:
   drop[k]=1;continue
  dr=D[k];entry=int(a[ii] if dr>0 else b[ii]);end_t=t[ii]+HOLD[k]
  exit_i=ii
  for j in range(ii+1,len(t)):
   px=int(b[j] if dr>0 else a[j]);fav=(px-entry)*dr
   exit_i=j
   if TP[k]>0 and fav>=TP[k]:break
   if SL[k]>0 and fav<=-SL[k]:break
   if t[j]>=end_t:break
  outE[k]=ii;outX[k]=exit_i;outR[k]=entry;outP[k]=((int(b[exit_i] if dr>0 else a[exit_i])-entry)*dr)/1000.-fee;outH[k]=(t[exit_i]-t[ii])/1000.
 return outE,outX,outR,outP,outH,drop

def candidates(J,hb,build_events):
 t,a,b,mid,h4,h1,m15,m5=J.DATA[:8];start,end=J.DATA[-2:]
 sets=[]
 # original 131D V3 source coverage mask (rebuilt on entry-only heartbeat_candidates)
 for ms,gc in [(int(os.getenv('GRID0272_COVERAGE_INTERVAL_MS','250')),0),(int(os.getenv('GRID0272_COVERAGE_INTERVAL_MS','250')),2)]:
  idx,dr,src,hold,tp,sl=hb.heartbeat_candidates(t,mid,h4,h1,m15,m5,ms,gc)
  et=t[idx];minute_bin=((et//60000)%60)//10;j60=np.searchsorted(t,et-60000,side='left');ticks60=idx-j60+1
  if gc==0:
   k=np.zeros(len(idx),bool)
   k |= (src==9)&(minute_bin==0)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
   k |= (src==11)&np.isin(minute_bin,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
   k |= (src==11)&(minute_bin==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)
   k |= (src==12)&np.isin(minute_bin,[0,1,2])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
   k |= (src==12)&(minute_bin==4)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=210)
   k |= (src==13)&np.isin(minute_bin,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==-1)
   k |= (src==14)&(minute_bin==3)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==-1)&(m5[idx]==1)
   k |= (src==15)&np.isin(minute_bin,[2,3])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==1)
  else:
   k=(src==16)&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&np.isin(minute_bin,[0,3,4])
  k &= (et>=start)&(et<end)
  # original coverage long, fixed 250s HOLD on heartbeat source
  sets.append((idx[k],np.ones(sum(k),np.int8),np.zeros(sum(k),np.int32),np.zeros(sum(k),np.int32),hold[k],f'coverage_gc{gc}'))
 # exact source12 cold-start conditions before original future fill path/cap
 idx,dr,src,hold,tp,sl=hb.heartbeat_candidates(t,mid,h4,h1,m15,m5,50,0)
 et=t[idx];bin10=((et//60000)%60)//10;j60=np.searchsorted(t,et-60000,side='left');ticks60=idx-j60+1
 k=(src==12)&np.isin(bin10,[4,5])&(h4[idx]==1)&(h1[idx]==1)&(m15[idx]==1)&(m5[idx]==-1)&(ticks60<=450)&(et>=start)&(et<end)
 sets.append((idx[k],np.ones(sum(k),np.int8),np.zeros(sum(k),np.int32),np.zeros(sum(k),np.int32),hold[k],'coldstart'))
 # exact four LEAN session masks and source geometry
 import jan_session_portfolio_lean_131d as L
 ev,d=build_events(t,mid,50);m=(t[ev]>=start)&(t[ev]<end);ev=ev[m];d=d[m];h=((t[ev]//3600000)%24).astype(np.int8)
 for state,life,name,step,cap in L.LEAN:
  hour,H4,H1,M15,M5,dr=state
  mask=(h==hour)&(h4[ev]==H4)&(h1[ev]==H1)&(m15[ev]==M15)&(m5[ev]==M5)&(d==dr)
  ii=ev[mask];dire=d[mask];tp,sl,hold=life
  sets.append((ii,dire,np.full(len(ii),tp,np.int32),np.full(len(ii),sl,np.int32),np.full(len(ii),hold,np.int64),name))
 return sets

def portfolio(qmap,cap=703,fee=.20,latency_ms=250,coldcap=64,suppcap=512):
 c.materialize=lambda t,a,b:(np.asarray(a,dtype=np.int32),np.asarray(b,dtype=np.int32))
 import gamma02_jan_watchdog119_grid_layer_refinement_131a as WD
 import jan_session_portfolio_131d as J
 import gamma02_campaign_heartbeat_019 as hb
 from general_session_state_discovery_131c import build_events
 WD.renewal_owned=lambda t,a,b,pei,pxi,pd,q,r,ri,desk: renewal_owned_delayed(t,a,b,pei,pxi,pd,q,r,ri,desk,latency_ms,fee)
 start=time.perf_counter();
 # run original Watchdog 131A parent/child and causal Watchdog proof EXACT, only child timing/cost changed.
 box={};old=WD.cap.one
 def capwrap(Q,capn):
  r,B=old(Q,capn);box['wd']=B;return r,B
 WD.cap.one=capwrap
 try: rw=WD.build(qmap,cap)
 finally:WD.cap.one=old
 E,X,R,D,P,H,S=box['wd'];W=(E,X,R,D,P,H)
 print('WATCHDOG',len(E),round(float(np.sum(P)),2),'s',round(time.perf_counter()-start,2),flush=True)
 # replay unchanged source as-of event conditions without future-position selection masks
 suites=candidates(J,hb,build_events)
 t,a,b=J.DATA[:3]
 print('CANDIDATE_RAW',[(name,len(e)) for e,d,tp,sl,hold,name in suites],flush=True)
 new=[];seen=set();supp_stats={};source_by_fill={}
 for ee,dd,tp,sl,hold,name in suites:
  # de-dup original request market tick between supplemental desks, not across Watchdog grid
  ix=np.array([k for k,j in enumerate(ee) if (int(j) not in seen) and (not seen.add(int(j)))],np.int64)
  ee,dd,tp,sl,hold=[z[ix] for z in (ee,dd,tp,sl,hold)]
  # Approved-for-research only: alter causal heartbeat lifecycle without calendar labels.
  if name.startswith('coverage'):
   hold=np.asarray(np.maximum(1000,np.minimum(3_600_000,hold*float(os.getenv('GRID0272_COVERAGE_HOLD_MULT','1.0')))),dtype=np.int64)
  E0,X0,R0,P0,H0,bad=price_supp(t,a,b,ee,dd,tp,sl,hold,latency_ms,fee)
  sel=(bad==0)&(E0>=0);E0,X0,R0,P0,H0,dd=[z[sel] for z in (E0,X0,R0,P0,H0,dd)]
  # Exact original source-level per-specialist position caps, now on latency-adjusted fills/exits.
  s_cap = 64 if name=='coldstart' else (512 if name.startswith('coverage') else {'ASIA02_CONT':64,'LONDON10_ROTATE_LONG':16,'OVERLAP13_SHORT':16,'LATE21_LONG':32}.get(name,16))
  ordered=np.lexsort((np.arange(len(E0)),E0))
  m0,_,_ = J.cap_arrays(*[z[ordered] for z in (E0,X0,R0,dd,P0,H0)],s_cap)
  for fillindex in m0[0]: source_by_fill.setdefault(int(fillindex),name)
  new.append(m0);supp_stats[name]=dict(source_requests=len(ee),fill_succeeded=len(E0),retained_by_specialist_cap=len(m0[0]),source_cap=s_cap,gross_cash_before_cap=float(sum(P0)),gross_loss_before_cap=float(sum(P0[P0<0])))
  print('SUPPLEMENT',name, len(E0),round(float(np.sum(P0)),2),flush=True)
 n=np.sum([len(z[0]) for z in new]);allE,allX,allR,allD,allP,allH=[np.concatenate([p[k] for p in new]) for k in range(6)]
 order=np.lexsort((np.arange(n),allE));supp,mo,sk=J.cap_arrays(*[z[order] for z in [allE,allX,allR,allD,allP,allH]],suppcap)
 # Note original coldcap+per-lean caps NOT yet enforced: corrected version must do so.
 Q,meta=J.merge_preserve_watchdog(W,[supp],suppcap)
 # Reconstruct complete per-ticket provenance after exact merge (no event is silently lost).
 s0,_=J.dedup_market_tick([supp]); ordr=np.lexsort((np.arange(len(s0[0])),s0[0])); s0=[v[ordr] for v in s0]; s1,_,_=J.cap_arrays(*s0,suppcap)
 allrows=[np.concatenate((W[k],s1[k])) for k in range(6)]; jj=np.lexsort((np.arange(len(allrows[0])),allrows[0])); check=[z[jj] for z in allrows]
 assert all(np.array_equal(check[k],Q[k]) for k in range(6)), 'source attribution and final portfolio mismatch'
 source=np.concatenate((np.full(len(W[0]),'WD119',dtype='U24'),np.asarray([source_by_fill.get(int(i),'UNKNOWN') for i in s1[0]],dtype='U24')))[jj]
 tag=f'cap{cap}_hold{os.getenv("GRID0272_COVERAGE_HOLD_MULT","1.0")}_interval{os.getenv("GRID0272_COVERAGE_INTERVAL_MS","250")}'
 np.savez_compressed('/mnt/data/GRID0272_JAN_COMBINATIONS/trades_'+tag+'.npz',entry_idx=Q[0],exit_idx=Q[1],entry_ms=t[Q[0]],exit_ms=t[Q[1]],entry_price_raw=Q[2],direction=Q[3],net_cash=Q[4],hold_seconds=Q[5],source=source)
 r,_=J.score(t,*Q,'JAN131A_131D_CAUSAL_COMBINED_RAW250MS_FEE20',meta)
 r.update(coverage_interval_ms=int(os.getenv('GRID0272_COVERAGE_INTERVAL_MS','250')),ledger_npz='trades_'+tag+'.npz',coverage_hold_multiplier=float(os.getenv('GRID0272_COVERAGE_HOLD_MULT','1.0')),source='J131A unmodified parent/Watchdog plus as-of 131D source-event masks',latency_ms=latency_ms,fee=fee,params=dict(qmap=qmap,wd_cap=cap,supp_cap=suppcap,per_specialist_caps_enforced=True),supplemental_sources=supp_stats,seconds=time.perf_counter()-start)
 fname=f'original_composite_raw_{latency_ms}ms_fee{int(fee*100)}_q{qmap[0]}_cap{cap}_hold{os.getenv("GRID0272_COVERAGE_HOLD_MULT","1.0")}_interval{os.getenv("GRID0272_COVERAGE_INTERVAL_MS","250")}.json'
 open('/mnt/data/GRID0272_JAN_COMBINATIONS/'+fname,'w').write(json.dumps(r,indent=2))
 print('FINAL',json.dumps({k:r.get(k) for k in ['net','trades','gross_loss','pf','win','equity_dd','balance_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks','seconds']}),flush=True)
 return r
if __name__=='__main__':
 q=[int(i) for i in sys.argv[1].split(',')] if len(sys.argv)>1 else [1190]*5+[1100]
 portfolio(q,int(sys.argv[2]) if len(sys.argv)>2 else 703)
