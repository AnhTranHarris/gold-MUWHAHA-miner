from pathlib import Path
import json,time
import numpy as np,pandas as pd
from numba import njit
ROOT=Path('/mnt/data')
RAW=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
BASEE=ROOT/'SA100_R10Y_CONT180_FAILURE_STATE_EPISODES_RERUN01.csv'
BASEL=ROOT/'SA100_R10Y_CONT180_FAILURE_STATE_LEGS_RERUN01.csv'
ORIG=ROOT/'delta_a_research10/SA100_R10_JAN_CANDIDATE01_LEGS.csv'
ANN=ROOT/'SA100_R10I_ANNOTATED_EPISODES.csv'
OUT=ROOT/'SA100_R10Z30_CONT180_SECOND_STAGE_FAILURE_SPECIALIST01.json'
DETAIL=ROOT/'SA100_R10Z30_CONT180_SECOND_STAGE_EPISODES.csv'
LEGSOUT=ROOT/'SA100_R10Z30_CONT180_SECOND_STAGE_LEGS.csv'
DAY=86400000;P75=np.array([20,20,21,21],np.int64);COST=.02

def econ(x):
 x=np.asarray(x,float);gp=float(x[x>0].sum());gl=float(x[x<0].sum());return dict(n=int(len(x)),net=float(x.sum()),gp=gp,gl=gl,pf=float(gp/-gl) if gl<0 else None,win=float((x>0).mean()) if len(x) else None)
@njit(cache=False)
def eqscan(t,bid,ask,oi,ci,sd,ent,pnl):
 m=len(oi);O=np.argsort(oi);C=np.argsort(ci);op=cl=0;nl=ns=0;sel=ses=0.;bal=peak=100.;mineq=1e99;dd=0.;mf=1e99;ml=1e99;mp=0
 for k in range(len(t)):
  while cl<m and ci[C[cl]]<=k:
   j=C[cl];bal+=pnl[j]
   if sd[j]==1:nl-=1;sel-=ent[j]
   else:ns-=1;ses-=ent[j]
   cl+=1
  while op<m and oi[O[op]]<=k:
   j=O[op]
   if ci[j]<=k:op+=1;continue
   if sd[j]==1:nl+=1;sel+=ent[j]
   else:ns+=1;ses+=ent[j]
   op+=1
  eq=bal+(nl*bid[k]-sel+ses-ns*ask[k])-COST*(nl+ns)
  if eq<mineq:mineq=eq
  if eq>peak:peak=eq
  if peak-eq>dd:dd=peak-eq
  pos=nl+ns
  if pos>mp:mp=pos
  if pos:
   mar=pos*((bid[k]+ask[k])/2.)/500.;fr=eq-mar;lv=eq/mar*100.
   if fr<mf:mf=fr
   if lv<ml:ml=lv
 return bal,mineq,dd,mf,ml,mp

def main():
 st=time.time();D=pd.read_csv(BASEE).sort_values('event_id').reset_index(drop=True);A=pd.read_csv(ANN).sort_values('event_id').reset_index(drop=True);assert np.array_equal(D.event_id.values,A.event_id.values)
 L0=pd.read_csv(BASEL);O0=pd.read_csv(ORIG);orig={int(k):g.sort_values(['open_ms','close_ms']).copy() for k,g in O0.groupby('event_id')};baselegs={int(k):g.sort_values(['open_ms','close_ms']).copy() for k,g in L0.groupby('event_id')}
 raw=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'});t=raw.timestamp_ms_utc.to_numpy(np.int64);ar=raw.ask_raw.to_numpy(np.int64);br=raw.bid_raw.to_numpy(np.int64);tod=t%DAY;il=(tod>=8*3600000)&(tod<16.5*3600000);iny=(tod>=13*3600000)&(tod<22*3600000);ss=np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8);spr=P75[ss]*10;mm=ar+br;bid=((mm-spr+10)//20)*10/1000.;ask=bid+spr/1000.
 target=(D.tag.astype(str)=='HOLD')&(D.candidate_pnl!=0)&(A.owner.astype(str)=='CONT')&(A.horizon_s==180);selinfo={};stats=[]
 for qi in np.flatnonzero(target):
  ev=int(D.event_id.iloc[qi]);pg=orig[ev][orig[ev].leg.astype(str)=='PRIMARY'].iloc[0];side=int(pg.side);os=int(pg.open_ms);tm=os+3000;oi=min(np.searchsorted(t,os,'left'),len(t)-1);k=min(np.searchsorted(t,tm,'right')-1,len(t)-1);en=ask[oi] if side==1 else bid[oi];ix=np.arange(oi,k+1);aligned=(bid[ix]-en) if side==1 else (en-ask[ix]);pp=aligned-COST;mfe=float(pp.max());mae=float(pp.min());fire=(mfe>0.30) and (mfe<=3.50) and (mae<=-1.70);stats.append((ev,fire,mfe,mae));
  if fire:selinfo[ev]=(tm,k,side)
 clegs=[];new=D.candidate_pnl.to_numpy(float).copy();tags=D.tag.astype(str).to_numpy(object)
 for qi,r in D.iterrows():
  ev=int(r.event_id);tag=str(r.tag)
  if float(r.candidate_pnl)==0:continue
  if ev not in selinfo:
   g=baselegs.get(ev)
   if g is None:continue
   for z in g.itertuples(index=False):clegs.append((ev,str(z.leg),int(z.open_ms),int(z.close_ms),int(z.side),float(z.pnl)))
  else:
   tm,k,pside=selinfo[ev];g=baselegs[ev];tot=0.
   for z in g.itertuples(index=False):
    os=int(z.open_ms);cs=int(z.close_ms);sd=int(z.side);lg=str(z.leg)
    if cs<=tm:clegs.append((ev,lg,os,cs,sd,float(z.pnl)));tot+=float(z.pnl)
    elif os<=tm<cs:
     oix=min(np.searchsorted(t,os,'left'),len(t)-1);en=ask[oix] if sd==1 else bid[oix];p=((bid[k]-en) if sd==1 else (en-ask[k]))-COST;clegs.append((ev,'R10Z_CLOSE3_'+lg,os,tm,sd,float(p)));tot+=float(p)
   rs=-pside;rtm=tm+30000;rk=min(np.searchsorted(t,rtm,'right')-1,len(t)-1);ren=ask[k] if rs==1 else bid[k];rp=((bid[rk]-ren) if rs==1 else (ren-ask[rk]))-COST;clegs.append((ev,'R10Z_REV30',tm,int(t[rk]),rs,float(rp)));tot+=float(rp);new[qi]=tot;tags[qi]='R10Z_REV30'
 L=pd.DataFrame(clegs,columns=['event_id','leg','open_ms','close_ms','side','pnl']).sort_values(['close_ms','open_ms']).reset_index(drop=True);disc=D.discovery.to_numpy(bool);base=D.candidate_pnl.to_numpy(float);selected=set(k for k in selinfo);sm=np.array([int(e) in selected for e in D.event_id]);changed=new[sm]
 b=100.;pk=100.;dd=0.;mn=100.
 for z in L.itertuples(index=False):b+=z.pnl;pk=max(pk,b);dd=max(dd,pk-b);mn=min(mn,b)
 oi=np.minimum(np.searchsorted(t,L.open_ms.to_numpy(np.int64),'left'),len(t)-1);ci=np.minimum(np.searchsorted(t,L.close_ms.to_numpy(np.int64),'left'),len(t)-1);sd=L.side.to_numpy(np.int8);ent=np.where(sd==1,ask[oi],bid[oi]);fb,meq,edd,mf,ml,mp=eqscan(t,bid,ask,oi.astype(np.int64),ci.astype(np.int64),sd,ent,L.pnl.to_numpy(float))
 dates=pd.to_datetime(A.event_time_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%d').to_numpy()
 def ds(day):
  m=(dates==day)&sm;return dict(n=int(m.sum()),changed_win=float((new[m]>0).mean()) if m.sum() else None,delta_usd=float((new[m]-base[m]).sum()),converted_losses=int(np.sum((base[m]<0)&(new[m]>0))))
 detail=D.copy();detail['candidate_pnl']=new;detail['tag']=tags;detail.to_csv(DETAIL,index=False);L.to_csv(LEGSOUT,index=False)
 out={'id':'SA100_R10Z30_CONT180_SECOND_STAGE_FAILURE_SPECIALIST01','status':'COMPLETE_EXACT_TICK_SECOND_STAGE_CONVERSION','rule':'after R10Y abstains, residual HOLD/CONT/180s at +3s: if MFE>$0.30 and <=$3.50 and MAE<=-$1.70, close current basket/cancel future legs and reverse one 0.01 for 30s','target_episodes':int(target.sum()),'selected_episodes':int(sm.sum()),'specialist_changed_win':float((changed>0).mean()),'converted_losses':int(np.sum((base[sm]<0)&(new[sm]>0))),'jan29':ds('2026-01-29'),'jan30':ds('2026-01-30'),'physical_legs':econ(L.pnl),'episodes':econ(new),'discovery':econ(new[disc]),'holdout':econ(new[~disc]),'delta_net_usd':float(new.sum()-base.sum()),'episode_gl_reduction_usd':float(new[new<0].sum()-base[base<0].sum())*-1.,'realized_balance_dd_usd':dd,'realized_min_balance_usd':mn,'tick_min_equity_usd':meq,'tick_max_equity_dd_usd':edd,'min_free_margin_usd':mf,'min_margin_level_pct':ml,'max_positions':int(mp),'executed_episode_win':float((new[new!=0]>0).mean()),'disc_exec_win':float((new[disc&(new!=0)]>0).mean()),'hold_exec_win':float((new[(~disc)&(new!=0)]>0).mean()),'august_accessed':False,'elapsed_s':time.time()-st};OUT.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()