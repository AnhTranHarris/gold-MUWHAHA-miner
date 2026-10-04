from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd
D=86400000; T=10; SCALE=1000; SA=1767225600000; SE=1768737600000; W=7
USDST=1772953200000; UKDST=1774746000000; P75=np.array([20,20,21,21],np.int64)
MAXSP=250; STOP=300; ACT=100; DIST=30; HOLD=30
SHA={'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','03':'814ba35e72f219a58badd806ed5c0f30ef0fb4ffe56a48205d873706513bd177','04':'30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f','05':'3a50e0f1eba3076154238290ec02842cf3744ab192e5c9a2acc1cc07367c6a0d','06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2','07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}
CFG=('C01_DIRECTIONAL_RECLAIM','C02_REVERSAL_HALF_CLOSE','C03_ENGULFING_RECOVERY','C04_DIRECTIONAL_RANGE_EXPANSION')
def sh(p):
 h=hashlib.sha256(); f=open(p,'rb')
 for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 f.close(); return h.hexdigest()
def aw(p,o):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); n=None
 try:
  with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',prefix='.'+p.name+'.',suffix='.tmp',dir=p.parent,delete=False) as f:
   n=f.name; json.dump(o,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
  os.replace(n,p); n=None
 finally:
  if n:
   try: os.unlink(n)
   except FileNotFoundError: pass
def p75(t,a,b):
 tod=t%D; ls=np.where(t>=UKDST,7,8)*3600000; le=ls+30600000; ns=np.where(t>=USDST,12,13)*3600000; ne=ns+32400000
 s=np.where((tod>=ls)&(tod<le)&(tod>=ns)&(tod<ne),2,np.where((tod>=ls)&(tod<le),1,np.where((tod>=ns)&(tod<ne),3,0))).astype(np.int8)
 sp=P75[s]*T; m=a.astype(np.int64)+b.astype(np.int64); bid=((m-sp+T)//(2*T))*T; return bid+sp,bid
def bars(t,b):
 q=t//5000; st=np.r_[0,np.flatnonzero(q[1:]!=q[:-1])+1]; en=np.r_[st[1:],len(t)]
 return {'e':((q[st]+1)*5000).astype(np.int64),'o':b[st],'c':b[en-1],'h':np.maximum.reduceat(b,st),'l':np.minimum.reduceat(b,st)}
def levels(t,b):
 d=t//D; st=np.r_[0,np.flatnonzero(d[1:]!=d[:-1])+1]; en=np.r_[st[1:],len(t)]; z={}; ph=pl=None
 for s,e in zip(st,en):
  x=int(d[s]);
  if ph is not None:z[x]=(ph,pl)
  ph=int(np.max(b[s:e])); pl=int(np.min(b[s:e]))
 return z
def ok(cfg,k,B,j):
 o,c,h,l=map(lambda x:int(B[x][j]),('o','c','h','l')); dr=c<o if k=='PDH' else c>o
 if cfg=='C01_DIRECTIONAL_RECLAIM': return dr
 if cfg=='C02_REVERSAL_HALF_CLOSE': return c<=(h+l)/2 if k=='PDH' else c>=(h+l)/2
 if j<1:return False
 po,pc,ph,pl=map(lambda x:int(B[x][j-1]),('o','c','h','l'))
 if cfg=='C03_ENGULFING_RECOVERY': return dr and max(o,c)>=max(po,pc) and min(o,c)<=min(po,pc)
 return dr and h-l>ph-pl
def props(t,a,b,start,end,cfg=None):
 L=levels(t,b); B=bars(t,b); d=t//D; st=np.r_[0,np.flatnonzero(d[1:]!=d[:-1])+1]; en=np.r_[st[1:],len(t)]; out=[]
 for s,e in zip(st,en):
  day=int(d[s]); ds=day*D
  if ds<start or ds>=end or day not in L:continue
  for k,x,side in [('PDH',L[day][0],-1),('PDL',L[day][1],1)]:
   q=np.flatnonzero(b[s:e]>x) if k=='PDH' else np.flatnonzero(b[s:e]<x)
   if not q.size:continue
   tm=int(t[s+int(q[0])]); j=int(np.searchsorted(B['e'],tm,side='right')); r=-1
   while j<len(B['e']) and int(B['e'][j])<=(day+1)*D:
    c=int(B['c'][j])
    if (k=='PDH' and c<x) or (k=='PDL' and c>x):r=j;break
    j+=1
   if r<0:continue
   ii=int(np.searchsorted(t,int(B['e'][r]),side='left')); reason='ELIGIBLE'
   if ii>=len(t) or int(t[ii])>=(day+1)*D or int(t[ii])>=end:reason='NO_TICK'
   elif not ((int(b[ii])<x) if k=='PDH' else (int(b[ii])>x)):reason='RELOST'
   elif int(a[ii]-b[ii])>MAXSP:reason='SPREAD'
   elif cfg and not ok(cfg,k,B,r):reason='QUALITY'
   out.append((min(ii,len(t)-1),side,k,ds,reason))
 return sorted(out)
def sim(P,t,a,b,start,end):
 E={}
 for x in P:
  if x[4]=='ELIGIBLE' and start<=int(t[x[0]])<end:E.setdefault(x[0],[]).append(x)
 pos=entry=stop=es=0; tr=win=acc=blk=lo=sho=0; gp=gl=net=0.; i0=int(np.searchsorted(t,start)); i1=int(np.searchsorted(t,end))
 def close(raw):
  nonlocal tr,win,gp,gl,net
  deal=raw-.01; win+=deal>1e-12; gp+=deal if raw>0 else 0; gl+=deal if raw<=0 else 0; net+=deal; tr+=1
 for i in range(i0,min(i1,len(t))):
  tm=int(t[i]); aa=int(a[i]); bb=int(b[i]); sec=tm//1000; occ=pos!=0
  if pos==1 and bb<=stop:close((bb-entry)/SCALE);pos=entry=stop=es=0
  elif pos==-1 and aa>=stop:close((entry-aa)/SCALE);pos=entry=stop=es=0
  if pos:
   if sec-es>=HOLD:close(((bb-entry) if pos==1 else (entry-aa))/SCALE);pos=entry=stop=es=0
   else:
    fav=(bb-entry) if pos==1 else (entry-aa)
    if fav>=ACT:
     ns=((bb-DIST if pos==1 else aa+DIST)+T//2)//T*T
     if (pos==1 and ns>stop) or (pos==-1 and ns<stop):stop=ns
  for x in E.get(i,[]):
   if occ or pos:blk+=1;continue
   pos=x[1];entry=aa if pos==1 else bb;es=sec;stop=((bb-STOP if pos==1 else aa+STOP)+T//2)//T*T;net-=.01;gl-=.01;acc+=1;lo+=pos==1;sho+=pos==-1
 if pos and i1>i0:
  i=min(i1,len(t))-1;close(((int(b[i])-entry) if pos==1 else (entry-int(a[i])))/SCALE)
 return {'accepted_entries':acc,'blocked_position':blk,'trades':tr,'official_wins':int(win),'gross_profit':round(gp,2),'gross_loss':round(gl,2),'direct_net_usd':round(net,2),'long_entries':int(lo),'short_entries':int(sho)}
def load(P,m):
 if m=='01A':
  if sh(P['01'])!=SHA['01']:raise SystemExit('jan sha')
  z=pd.read_csv(P['01'],compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64);return z[(z.timestamp_ms_utc>=SA)&(z.timestamp_ms_utc<SE)].reset_index(drop=True),SA,SE
 mm=int(m); start=int(datetime(2026,mm,1,tzinfo=timezone.utc).timestamp()*1000); end=int(datetime(2026,mm+1,1,tzinfo=timezone.utc).timestamp()*1000); pm=f'{mm-1:02d}'
 if sh(P[pm])!=SHA[pm] or sh(P[m])!=SHA[m]:raise SystemExit('sha '+m)
 cols=['timestamp_ms_utc','ask_raw','bid_raw']; x=pd.read_csv(P[pm],compression='gzip',usecols=cols,dtype=np.int64);x=x[(x.timestamp_ms_utc>=start-W*D)&(x.timestamp_ms_utc<start)];y=pd.read_csv(P[m],compression='gzip',usecols=cols,dtype=np.int64);y=y[(y.timestamp_ms_utc>=start)&(y.timestamp_ms_utc<end)];return pd.concat([x,y],ignore_index=True),start,end
def main():
 ap=argparse.ArgumentParser();[ap.add_argument('--m'+m,type=Path,required=True) for m in SHA];ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();P={m:getattr(a,'m'+m) for m in SHA};M=['01A','02','03','04','05','06','07'];R={}
 for m in M:
  df,s,e=load(P,m);t=df.timestamp_ms_utc.to_numpy(np.int64);aa,bb=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));bp=props(t,aa,bb,s,e);R[m]={'baseline':sim(bp,t,aa,bb,s,e),'configs':{c:sim(props(t,aa,bb,s,e,c),t,aa,bb,s,e) for c in CFG}}
 bt=sum(R[m]['baseline']['trades'] for m in M);bn=round(sum(R[m]['baseline']['direct_net_usd'] for m in M),2);S={}
 for c in CFG:
  tr=sum(R[m]['configs'][c]['trades'] for m in M);net=round(sum(R[m]['configs'][c]['direct_net_usd'] for m in M),2);mw=sum(R[m]['configs'][c]['trades']>0 for m in M);nn=sum(R[m]['configs'][c]['direct_net_usd']>=0 for m in M);rt=tr/bt if bt else 0;g={'retention_0_5':rt>=.5,'months_with_trades_5':mw>=5,'nonnegative_months_4':nn>=4,'aggregate_net_nonnegative':net>=0,'improves_baseline':net>bn};g['pass']=all(g.values());S[c]={'trades':tr,'retention':round(rt,6),'months_with_trades':mw,'nonnegative_months':nn,'net':net,'baseline_net':bn,'improvement':round(net-bn,2),'gate':g}
 rank=sorted(CFG,key=lambda c:(S[c]['gate']['pass'],S[c]['nonnegative_months'],S[c]['net'],S[c]['retention']),reverse=True);lead=rank[0];passed=any(S[c]['gate']['pass'] for c in CFG);o={'schema':'delta-r037-plsr-reclaim-quality-cross-month-17x-v1','status':'COMPLETE_CROSS_MONTH_SCREEN','unit':'R037_PLSR_RECLAIM_QUALITY_CROSS_MONTH_CHECKPOINT_17X','family':'R037-PLSR-RQ-v1','surface':'DUKAS_COINEXX_LIKE_P75','months':M,'numeric_retuning':False,'post_result_retuning':False,'august_accessed':False,'baseline':{'trades':bt,'net':bn},'monthly':R,'summary':S,'ranking':rank,'finding':{'leading_config':lead,'any_gate_pass':passed,'decision':'ADVANCE_LEADER_FULL_SURROGATE_PARENT_CROSS_MONTH_VALIDATION' if passed else 'RETIRE_RECLAIM_QUALITY_REFINEMENT_NO_RETUNE','next':'R037_PLSR_RQ_LEADER_FULL_SURROGATE_PARENT_CROSS_MONTH_VALIDATION' if passed else 'R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST'},'mql5_authorized':False};aw(a.output,o);print(json.dumps({'baseline':o['baseline'],'summary':S,'finding':o['finding']},separators=(',',':')))
if __name__=='__main__':main()
