"""DELTA R037 DH05 boundary/probe parity diagnostic — Checkpoint 09C.

Purpose: reproduce the preserved Checkpoint-03 early funnel using frozen DH05 vectors
without economic optimization. Tests symmetric confirmed M5 swing widths 1/2/3 and a
causal repeated pre-failure boundary-attempt counter. August is never loaded.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

DAY_MS=86_400_000; TICK_RAW=10; STAGE_A_END_MS=1_768_737_600_000
US_DST_START_2026_MS=1_772_953_200_000; UK_DST_START_2026_MS=1_774_746_000_000
P75_POINTS=np.asarray([20,20,21,21],dtype=np.int64)
CANONICAL_JAN_SHA256="d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5"
VECTORS=(
('A03',.3,15,40,20,.15,.08,.12,.5,5),
('S05',.374062,15,9.099416,6.468982,.244588,.093793,.217011,.062661,5),
('S06',.217738,5,59.699117,23.47226,.029179,.145085,.041213,.673017,1),
('S09',.329294,15,41.910749,10.844137,.335024,.12735,.272984,.126644,1),
('S10',.26416,5,20.537168,19.210606,.108825,.077129,.088265,.644213,5),
('S16',.18608,5,31.219954,3.711492,.279091,.121753,.206212,.746067,5))
TARGET={
'A03':[6731,1009,207,797,432,266,187,187],
'S05':[7875,318,28,290,51,15,9,9],
'S06':[3470,1606,245,1358,1211,683,617,617],
'S09':[7748,208,40,168,61,40,9,9],
'S10':[6496,1316,202,1106,623,294,206,206],
'S16':[7870,135,43,92,37,18,8,8]}
STAGES=['probe','qualified','accepted','failure','reentry','reclaim','reversal','signal']

def sha256_file(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''): h.update(block)
 return h.hexdigest()

def session_code(t):
 tod=t%DAY_MS; ls=np.where(t>=UK_DST_START_2026_MS,7,8)*3_600_000; le=ls+8*3_600_000+30*60_000
 ns=np.where(t>=US_DST_START_2026_MS,12,13)*3_600_000; ne=ns+9*3_600_000
 il=(tod>=ls)&(tod<le); iny=(tod>=ns)&(tod<ne)
 return np.where(il&iny,2,np.where(il,1,np.where(iny,3,0))).astype(np.int8)

def p75(t,a,b):
 s=session_code(t); sp=P75_POINTS[s]*TICK_RAW; mid2=a.astype(np.int64)+b.astype(np.int64)
 bid=((mid2-sp+TICK_RAW)//(2*TICK_RAW))*TICK_RAW
 return (bid+sp).astype(np.int64),bid.astype(np.int64)

def bars(t,mid2,tf):
 bucket=t//tf; st=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]; en=np.r_[st[1:],len(t)]
 return {'end_ms':((bucket[st]+1)*tf).astype(np.int64),'open':mid2[st].astype(np.int64),'close':mid2[en-1].astype(np.int64),
         'high':np.maximum.reduceat(mid2,st).astype(np.int64),'low':np.minimum.reduceat(mid2,st).astype(np.int64)}

def atr14(b):
 h,l,c=b['high'],b['low'],b['close']; tr=(h-l).copy()
 if len(tr)>1: tr[1:]=np.maximum(tr[1:],np.maximum(np.abs(h[1:]-c[:-1]),np.abs(l[1:]-c[:-1])))
 cs=np.r_[0,np.cumsum(tr,dtype=np.int64)]; out=np.zeros(len(tr),dtype=np.float64)
 for i in range(13,len(tr)): out[i]=(cs[i+1]-cs[i-13])/14.0
 return out

def symmetric_swings(b,w):
 hi,lo,end=b['high'],b['low'],b['end_ms']; rev=[];side=[];lev=[]
 for k in range(w,len(hi)-w):
  h=hi[k];l=lo[k]
  ish=all(h>hi[k-j] and h>hi[k+j] for j in range(1,w+1))
  isl=all(l<lo[k-j] and l<lo[k+j] for j in range(1,w+1))
  reveal=int(end[k+w])
  if ish: rev.append(reveal);side.append(1);lev.append(int(h))
  if isl: rev.append(reveal);side.append(-1);lev.append(int(l))
 arr=np.asarray(rev,np.int64); order=np.argsort(arr,kind='stable')
 return arr[order],np.asarray(side,np.int8)[order],np.asarray(lev,np.int64)[order]

@njit(cache=True)
def bidx(end,tm): return np.searchsorted(end,tm,side='right')-1

@njit(cache=True)
def detect_attempt(t,mid2,st,ss,sl,m5e,m5a,s1e,s1o,s1c,s5e,s5o,s5c,s15e,s15o,s15c,
                   accdisp,acctf,maxfail,maxprobe,probeexc,reclaim,revdisp,effmin,revtf):
 stage=0;os=0;L=0;evatr=0.;pstart=0;fstart=0;reent=False;latest_hi=0;latest_lo=0;si=0;hiel=True;loel=True;lastacc=-1;lastrev=-1
 attempt_open=False;attempt_qualified=False;cnt=np.zeros(8,np.int64)
 for i in range(t.size):
  tm=int(t[i]);px=int(mid2[i])
  while si<st.size and st[si]<=tm:
   if ss[si]>0: latest_hi=int(sl[si])
   else: latest_lo=int(sl[si])
   si+=1
  jm=bidx(m5e,tm)
  if jm<13: continue
  ae=float(m5a[jm])
  if ae<=0: continue
  if stage==0:
   if latest_hi and px<latest_hi: hiel=True
   if latest_lo and px>latest_lo: loel=True
   if latest_hi and hiel and px>=latest_hi:
    stage=1;os=1;L=latest_hi;evatr=ae;pstart=tm;hiel=False;cnt[0]+=1;attempt_open=True;attempt_qualified=False
   elif latest_lo and loel and px<=latest_lo:
    stage=1;os=-1;L=latest_lo;evatr=ae;pstart=tm;loel=False;cnt[0]+=1;attempt_open=True;attempt_qualified=False
  if stage==0: continue
  if stage<=2:
   inside=os*(px-L)<0
   if inside:
    attempt_open=False;attempt_qualified=False
   elif not attempt_open:
    attempt_open=True;attempt_qualified=False;cnt[0]+=1
   if attempt_open and (not attempt_qualified) and os*(px-L)>=probeexc*evatr:
    attempt_qualified=True;cnt[1]+=1
  j1=bidx(s1e,tm);j5=bidx(s5e,tm);j15=bidx(s15e,tm);jacc=j5 if acctf==5 else j15
  ac=s5c[j5] if acctf==5 and j5>=0 else (s15c[j15] if j15>=0 else 0)
  if stage==1:
   if os*(px-L)>=probeexc*evatr: stage=2
   elif tm-pstart>maxprobe: stage=0;os=0;attempt_open=False;continue
  if stage<2: continue
  if jacc>=0 and jacc!=lastacc:
   lastacc=jacc
   if os*(ac-L)>=accdisp*evatr: cnt[2]+=1;stage=0;os=0;attempt_open=False;continue
  recross=os*(px-L)<0
  if stage==2:
   if tm-pstart>=maxprobe: stage=3;cnt[3]+=1;fstart=tm;attempt_open=False
   elif recross: stage=3;cnt[3]+=1;fstart=tm;attempt_open=False
  if stage==3:
   if recross and not reent: reent=True;cnt[4]+=1;stage=4
   elif fstart and tm-fstart>maxfail: stage=0;os=0;reent=False;continue
  elif stage>=4 and fstart and tm-fstart>maxfail: stage=0;os=0;reent=False;continue
  if stage<4: continue
  jrev=j1 if revtf==1 else j5;rc=s1c[j1] if revtf==1 and j1>=0 else (s5c[j5] if j5>=0 else 0)
  if stage==4 and jrev>=0 and jrev!=lastrev:
   if (-os)*(rc-L)>=reclaim*evatr: cnt[5]+=1;stage=5
  if stage<5 or jrev<0 or jrev==lastrev: continue
  ro=s1o[j1] if revtf==1 else s5o[j5]; disp=(-os)*(rc-ro); eff=1.0 if abs(rc-ro)>0 else 0.0
  if disp>=revdisp*evatr and eff>=effmin: cnt[6]+=1;cnt[7]+=1;stage=0;os=0;reent=False
  lastrev=jrev
 return cnt

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 source_sha=sha256_file(args.source)
 if source_sha!=CANONICAL_JAN_SHA256: raise SystemExit(f'canonical January SHA mismatch: {source_sha}')
 df=pd.read_csv(args.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
 df=df[df.timestamp_ms_utc<STAGE_A_END_MS];t=df.timestamp_ms_utc.to_numpy(np.int64);a,b=p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64));mid=a+b
 bs={s:bars(t,mid,s*1000) for s in (1,5,15,300)};ats={s:atr14(bs[s]) for s in (1,5,300)}
 results={}
 for w in (1,2,3):
  st,ss,sl=symmetric_swings(bs[300],w);vectors={};stage_abs=np.zeros(8,np.int64)
  for v in VECTORS:
   n,ad,at,mf,mp,pe,rb,rd,em,rt=v
   c=detect_attempt(t,mid,st,ss,sl,bs[300]['end_ms'],ats[300],bs[1]['end_ms'],bs[1]['open'],bs[1]['close'],bs[5]['end_ms'],bs[5]['open'],bs[5]['close'],bs[15]['end_ms'],bs[15]['open'],bs[15]['close'],ad,at,int(mf*1000),int(mp*1000),pe,rb,rd,em,rt)
   trg=np.asarray(TARGET[n],np.int64);err=np.abs(c-trg);stage_abs+=err
   vectors[n]={'target':dict(zip(STAGES,map(int,trg))),'actual':dict(zip(STAGES,map(int,c))),'abs_error':dict(zip(STAGES,map(int,err)))}
  results[f'symmetric_width_{w}']={'vectors':vectors,'stage_abs_error':dict(zip(STAGES,map(int,stage_abs))),'total_abs_error':int(stage_abs.sum())}
 target_probe=sum(TARGET[n][0] for n,*_ in VECTORS);target_qual=sum(TARGET[n][1] for n,*_ in VECTORS)
 best=results['symmetric_width_2']
 out={'schema':'delta-r037-dh05-boundary-probe-parity-09c-v1','status':'BOUNDED_QA_COMPLETE_MATERIAL_PARITY_CLUE',
      'source_sha256':source_sha,'stage_a_ticks':int(len(t)),'surface':'DUKAS_COINEXX_LIKE_P75','august_accessed':False,
      'numeric_vector_retune':False,'checkpoint03_target':TARGET,'results':results,
      'finding':{'candidate_boundary':'symmetric two-bar confirmed M5 swing','probe_counter':'repeated causal same-boundary attempts before failure',
                 'probe_abs_error':best['stage_abs_error']['probe'],'probe_target_total':int(target_probe),
                 'probe_abs_error_pct':100.0*best['stage_abs_error']['probe']/target_probe,
                 'qualified_abs_error':best['stage_abs_error']['qualified'],'qualified_target_total':int(target_qual),
                 'qualified_abs_error_pct':100.0*best['stage_abs_error']['qualified']/target_qual,
                 'parity_complete':False,
                 'next':'acceptance/failure/reentry semantics; do not alter frozen numeric vectors'} }
 args.output.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out['finding'],indent=2))
if __name__=='__main__': main()
