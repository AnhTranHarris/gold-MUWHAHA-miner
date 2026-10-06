from pathlib import Path
import json,time
import numpy as np,pandas as pd
from numba import njit
ROOT=Path('/mnt/data');RAW=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz';BASEE=ROOT/'SA100_R10AB_REVERT900_REV30_EPISODES.csv';BASEL=ROOT/'SA100_R10AB_REVERT900_REV30_LEGS.csv';ANN=ROOT/'SA100_R10I_ANNOTATED_EPISODES.csv';OUT=ROOT/'SA100_R10AF_REVERT900_EARLY_DIRECTION_EXACT_COMPARE01.json';COST=.02;DAY=86400000;P75=np.array([20,20,21,21],np.int64)
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
 st=time.time();D=pd.read_csv(BASEE).sort_values('event_id').reset_index(drop=True);A=pd.read_csv(ANN).sort_values('event_id').reset_index(drop=True);assert np.array_equal(D.event_id.values,A.event_id.values);L0=pd.read_csv(BASEL);legs={int(k):g.sort_values(['open_ms','close_ms']).copy() for k,g in L0.groupby('event_id')}
 raw=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'});t=raw.timestamp_ms_utc.to_numpy(np.int64);ar=raw.ask_raw.to_numpy(np.int64);br=raw.bid_raw.to_numpy(np.int64);tod=t%DAY;il=(tod>=8*3600000)&(tod<16.5*3600000);iny=(tod>=13*3600000)&(tod<22*3600000);ss=np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8);spr=P75[ss]*10;mm=ar+br;bid=((mm-spr+10)//20)*10/1000.;ask=bid+spr/1000.
 target=(D.tag.astype(str)=='HOLD')&(D.candidate_pnl!=0)&(A.owner.astype(str)=='REVERT')&(A.horizon_s==900)
 variants=[('V15_R45',15,45),('V30_R60',30,60),('V30_R90',30,90)];outs=[]
 for name,cp,rh in variants:
  sel={}
  for qi in np.flatnonzero(target):
   ev=int(D.event_id.iloc[qi]);g=legs[ev];pg=g[g.leg.astype(str).str.contains('PRIMARY')];pg=(pg.iloc[0] if len(pg) else g.iloc[0]);pside=int(pg.side);os=int(pg.open_ms);oi=min(np.searchsorted(t,os,'left'),len(t)-1);tm=os+cp*1000;k=min(np.searchsorted(t,tm,'right')-1,len(t)-1);pent=ask[oi] if pside==1 else bid[oi];ix=np.arange(oi,k+1);pal=((bid[ix]-pent) if pside==1 else (pent-ask[ix]))-COST;pnow=float(pal[-1]);mfe=float(pal.max());mae=float(pal.min());rng=float(pal.max()-pal.min());travel=float(np.abs(np.diff(pal)).sum());eff=abs(pnow)/(travel+1e-12);sg=np.sign(np.diff(pal));sg=sg[sg!=0];turns=int(np.sum(sg[1:]!=sg[:-1])) if len(sg)>1 else 0;tps=float(len(ix)/cp);pre=float(A.pre30_range.iloc[qi]);sb=float(D.shadow_balance.iloc[qi])
   yes=False
   if name=='V15_R45':
    yes=((pnow<=-.445 and sb>229.165 and pre>2.914) or (pnow>-.445 and (mae<=-.865 or (mae>-.865 and turns<=41))))
   elif name=='V30_R60':
    yes=((pnow<=-.300 and mae>-1.820 and pre>1.705) or (pnow>-.300 and (mae<=-.535 or pre<=2.457)))
   else:
    yes=((pnow<=-.515 and mae>-1.820 and rng>1.835) or (pnow>-.515 and (eff>.030 or (eff<=.030 and tps>7.067))))
   if yes:sel[ev]=(tm,k,pside)
  clegs=[];new=D.candidate_pnl.to_numpy(float).copy();base=D.candidate_pnl.to_numpy(float);disc=D.discovery.to_numpy(bool)
  for qi,r in D.iterrows():
   ev=int(r.event_id)
   if float(r.candidate_pnl)==0:continue
   g=legs[ev]
   if ev not in sel:
    for z in g.itertuples(index=False):clegs.append((ev,str(z.leg),int(z.open_ms),int(z.close_ms),int(z.side),float(z.pnl)))
   else:
    tm,k,pside=sel[ev];tot=0.
    for z in g.itertuples(index=False):
     os=int(z.open_ms);cs=int(z.close_ms);sd=int(z.side);lg=str(z.leg)
     if cs<=tm:clegs.append((ev,lg,os,cs,sd,float(z.pnl)));tot+=float(z.pnl)
     elif os<=tm<cs:
      oi=min(np.searchsorted(t,os,'left'),len(t)-1);en=ask[oi] if sd==1 else bid[oi];p=((bid[k]-en) if sd==1 else (en-ask[k]))-COST;clegs.append((ev,name+'_CLOSE_'+lg,os,tm,sd,float(p)));tot+=float(p)
    rs=-pside;rt=tm+rh*1000;rk=min(np.searchsorted(t,rt,'right')-1,len(t)-1);ren=ask[k] if rs==1 else bid[k];rp=((bid[rk]-ren) if rs==1 else (ren-ask[rk]))-COST;clegs.append((ev,name+'_REV',tm,int(t[rk]),rs,float(rp)));tot+=float(rp);new[qi]=tot
  L=pd.DataFrame(clegs,columns=['event_id','leg','open_ms','close_ms','side','pnl']).sort_values(['close_ms','open_ms']).reset_index(drop=True);sm=np.array([int(e) in sel for e in D.event_id]);changed=new[sm]
  b=100.;pk=100.;dd=0.;mn=100.
  for z in L.itertuples(index=False):b+=z.pnl;pk=max(pk,b);dd=max(dd,pk-b);mn=min(mn,b)
  oi=np.minimum(np.searchsorted(t,L.open_ms.to_numpy(np.int64),'left'),len(t)-1);ci=np.minimum(np.searchsorted(t,L.close_ms.to_numpy(np.int64),'left'),len(t)-1);sd=L.side.to_numpy(np.int8);ent=np.where(sd==1,ask[oi],bid[oi]);fb,meq,edd,mf,ml,mp=eqscan(t,bid,ask,oi.astype(np.int64),ci.astype(np.int64),sd,ent,L.pnl.to_numpy(float))
  def blk(m):return dict(n=int(m.sum()),win=float((new[m]>0).mean()) if m.sum() else None,delta=float((new[m]-base[m]).sum()),converted=int(np.sum((base[m]<0)&(new[m]>0))))
  out=dict(name=name,cp=cp,rh=rh,selected=int(sm.sum()),specialist_win=float((changed>0).mean()) if sm.sum() else None,converted=int(np.sum((base[sm]<0)&(new[sm]>0))),disc=blk(sm&disc),hold=blk(sm&(~disc)),physical=econ(L.pnl),episodes=econ(new),delta_net=float(new.sum()-base.sum()),physical_gl_improvement=float(econ(L.pnl)['gl']-econ(L0.pnl)['gl']),episode_gl_improvement=float(econ(new)['gl']-econ(base)['gl']),balance_dd=dd,min_balance=mn,tick_min_equity=meq,tick_dd=edd,min_free_margin=mf,min_margin_level=ml,max_positions=int(mp));outs.append(out)
 out={'id':'SA100_R10AF_REVERT900_EARLY_DIRECTION_EXACT_COMPARE01','status':'COMPLETE_EXACT_COMPARE','base_physical':econ(L0.pnl),'base_episodes':econ(D.candidate_pnl),'variants':outs,'august_accessed':False,'elapsed_s':time.time()-st};OUT.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()