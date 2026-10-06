from pathlib import Path
import json,time
import numpy as np,pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
ROOT=Path('/mnt/data');RAW=ROOT/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz';BASEE=ROOT/'SA100_R10AB_REVERT900_REV30_EPISODES.csv';BASEL=ROOT/'SA100_R10AB_REVERT900_REV30_LEGS.csv';ANN=ROOT/'SA100_R10I_ANNOTATED_EPISODES.csv';OUT=ROOT/'SA100_R10AD_EARLY_CONT180_DIRECTION_SCREEN01.json';CSV=ROOT/'SA100_R10AD_EARLY_CONT180_DIRECTION_CANDIDATES01.csv'
DAY=86400000;P75=np.array([20,20,21,21],np.int64);COST=.02

def main():
 st=time.time();D=pd.read_csv(BASEE).sort_values('event_id').reset_index(drop=True);A=pd.read_csv(ANN).sort_values('event_id').reset_index(drop=True);assert np.array_equal(D.event_id.values,A.event_id.values);L=pd.read_csv(BASEL);legs={int(k):g.sort_values(['open_ms','close_ms']).copy() for k,g in L.groupby('event_id')}
 raw=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'});t=raw.timestamp_ms_utc.to_numpy(np.int64);ar=raw.ask_raw.to_numpy(np.int64);br=raw.bid_raw.to_numpy(np.int64);tod=t%DAY;il=(tod>=8*3600000)&(tod<16.5*3600000);iny=(tod>=13*3600000)&(tod<22*3600000);ss=np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8);spr=P75[ss]*10;mm=ar+br;bid=((mm-spr+10)//20)*10/1000.;ask=bid+spr/1000.
 target=(D.tag.astype(str)=='HOLD')&(D.candidate_pnl!=0)&(A.owner.astype(str)=='CONT')&(A.horizon_s==180);cps=[1,2,3,5,10,15,20];rhs=[15,30,45,60,90,120];rows=[]
 for qi in np.flatnonzero(target):
  ev=int(D.event_id.iloc[qi]);g=legs[ev];pg=g[g.leg.astype(str).str.contains('PRIMARY')];pg=(pg.iloc[0] if len(pg) else g.iloc[0]);pside=int(pg.side);os=int(pg.open_ms);oi=min(np.searchsorted(t,os,'left'),len(t)-1);pent=ask[oi] if pside==1 else bid[oi];base=float(D.candidate_pnl.iloc[qi]);disc=bool(D.discovery.iloc[qi]);fixed=dict(event_id=ev,base_pnl=base,discovery=disc,shadow_balance=float(D.shadow_balance.iloc[qi]),source_gap=float(A.source_gap.iloc[qi]),session=str(A.session.iloc[qi]),hour=int(A.hour.iloc[qi]),pre30_range=float(A.pre30_range.iloc[qi]),side=pside,date=str(A.date.iloc[qi]))
  for cp in cps:
   tm=os+cp*1000;k=min(np.searchsorted(t,tm,'right')-1,len(t)-1);ix=np.arange(oi,k+1);pal=((bid[ix]-pent) if pside==1 else (pent-ask[ix]))-COST;disp=float(pal[-1]);mfe=float(pal.max());mae=float(pal.min());rng=float(pal.max()-pal.min());travel=float(np.abs(np.diff(pal)).sum());eff=abs(disp)/(travel+1e-12);sg=np.sign(np.diff(pal));sg=sg[sg!=0];turns=int(np.sum(sg[1:]!=sg[:-1])) if len(sg)>1 else 0;tps=float(len(ix)/max(cp,1))
   close=0.
   for z in g.itertuples(index=False):
    zos=int(z.open_ms);zcs=int(z.close_ms);zsd=int(z.side)
    if zcs<=tm:close+=float(z.pnl)
    elif zos<=tm<zcs:
     zo=min(np.searchsorted(t,zos,'left'),len(t)-1);zen=ask[zo] if zsd==1 else bid[zo];close+=((bid[k]-zen) if zsd==1 else (zen-ask[k]))-COST
   r=dict(fixed,checkpoint_s=cp,pnl_cp=disp,mfe=mfe,mae=mae,path_range=rng,eff=eff,turns=turns,ticks_per_s=tps,close_pnl=close,close_delta=close-base)
   for rh in rhs:
    rk=min(np.searchsorted(t,tm+rh*1000,'right')-1,len(t)-1);rs=-pside;ren=ask[k] if rs==1 else bid[k];rp=((bid[rk]-ren) if rs==1 else (ren-ask[rk]))-COST;alt=close+rp;r[f'rev{rh}_pnl']=alt;r[f'rev{rh}_delta']=alt-base
   rows.append(r)
 C=pd.DataFrame(rows);C.to_csv(CSV,index=False);feat=['pnl_cp','mfe','mae','path_range','eff','turns','ticks_per_s','pre30_range','source_gap','shadow_balance','hour'];cand=[]
 for cp in cps:
  S=C[C.checkpoint_s==cp].copy();disc=S.discovery.to_numpy(bool);hold=~disc;X=S[feat].to_numpy(float)
  for act in ['close']+[f'rev{x}' for x in rhs]:
   alt=S[f'{act}_pnl'].to_numpy(float);base=S.base_pnl.to_numpy(float);delta=alt-base;y=((delta>0)&(alt>0)).astype(int)
   for depth in [1,2,3]:
    for leaf in [8,10,12,15,20,25,30,40,50]:
     if disc.sum()<2*leaf or y[disc].sum()<4:continue
     clf=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=leaf,random_state=0,class_weight='balanced').fit(X[disc],y[disc]);pred=clf.predict(X).astype(bool)
     if pred[disc].sum()<8 or pred[hold].sum()<25:continue
     def met(m):
      n=int(m.sum());a=alt[m];b=base[m];return dict(n=n,delta=float((a-b).sum()),win=float((a>0).mean()) if n else None,converted=int(np.sum((b<0)&(a>0))),gl_reduction=float(a[a<0].sum()-b[b<0].sum()) if n else 0.)
     md=met(pred&disc);mh=met(pred&hold);ma=met(pred)
     if md['delta']<=0 or mh['delta']<=0 or md['win']<.50 or mh['win']<.50 or md['gl_reduction']<=0 or mh['gl_reduction']<=0:continue
     rec=dict(cp=cp,action=act,depth=depth,leaf=leaf,disc=md,hold=mh,all=ma,tree=export_text(clf,feature_names=feat,decimals=3));cand.append(rec)
 cand.sort(key=lambda z:(z['all']['delta']+.35*z['all']['gl_reduction'],z['all']['converted']),reverse=True)
 out={'id':'SA100_R10AD_EARLY_CONT180_DIRECTION_SCREEN01','status':'COMPLETE_FAST_CAUSAL_DIRECTION_SCREEN','target_episodes':int(target.sum()),'target_net':float(D.loc[target,'candidate_pnl'].sum()),'target_gl':float(D.loc[target&(D.candidate_pnl<0),'candidate_pnl'].sum()),'target_win':float((D.loc[target,'candidate_pnl']>0).mean()),'soft_success_target':0.50,'qualifying_rules':len(cand),'top':cand[:40],'august_accessed':False,'elapsed_s':time.time()-st};OUT.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2)[:50000])
if __name__=='__main__':main()