import sys, numpy as np, pandas as pd, calendar, time, json
from pathlib import Path
from numba import njit
sys.path.insert(0,'/mnt/data')
import stmr_base as c

TP=np.array([4000,4000,4000,3000,4000,3000,4000,2500,4000,4000,4000,2500],np.int32)
SL=np.array([1000,1500,750,750,1500,750,1500,1500,1500,1500,1500,1250],np.int32)
GAPS=c.GAPS
DAY=c.DAY_MS
NAMES=['ASIA_LOWER_TAKEOVER','ASIA_M15_DIVERGE_M5_RECLAIM','LONDON_M5_TAKEOVER','LONDON_M5_RECLAIM','OVERLAP_LOWER_TAKEOVER','OVERLAP_ALIGNED_COUNTERCROSS','NY_LOWER_TRANSFER','NY_LOWER_COUNTERCROSS','LATE_ALIGNED_MOMENTUM','LATE_MACRO_SPLIT_TRANSFER','LATE_M5_REJECTION','LATE_LOWER_TAKEOVER']
FILES={1:'/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',2:'/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv(3).gz',3:'/mnt/data/XAUUSD_DUKAS_2026_03_ticks.csv(3).gz',4:'/mnt/data/XAUUSD_DUKAS_2026_04_ticks.csv(3).gz',5:'/mnt/data/XAUUSD_DUKAS_2026_05_ticks.csv(3).gz',6:'/mnt/data/XAUUSD_DUKAS_2026_06_ticks.csv(3).gz',7:'/mnt/data/XAUUSD_DUKAS_2026_07_ticks.csv(2).gz'}

def ts(y,m,d=1):return np.int64(pd.Timestamp(y,m,d,tz='UTC').value//1_000_000)

def load_month(m, warm_days=10):
    cur=pd.read_csv(FILES[m],compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
    start=ts(2026,m,1); end=ts(2026,m+1,1) if m<12 else ts(2027,1,1)
    if m>1 and warm_days:
      prev=pd.read_csv(FILES[m-1],compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
      prev=prev[prev.timestamp_ms_utc>=start-warm_days*DAY]
      df=pd.concat([prev,cur],ignore_index=True)
    else:df=cur
    t=df.timestamp_ms_utc.to_numpy(np.int64);sa=df.ask_raw.to_numpy(np.int32);sb=df.bid_raw.to_numpy(np.int32)
    return t,sa,sb,start,end

def bar_states_span(t,px,tf_ms,fast,slow):
    buck=t//tf_ms;starts=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1];ends=np.r_[starts[1:]-1,len(t)-1];bars=buck[starts];cl=px[ends].astype(np.float64)
    e1=np.empty(len(cl));e2=np.empty(len(cl));e1[0]=cl[0];e2[0]=cl[0];a1=2/(fast+1);a2=2/(slow+1)
    for i in range(1,len(cl)):e1[i]=a1*cl[i]+(1-a1)*e1[i-1];e2[i]=a2*cl[i]+(1-a2)*e2[i-1]
    st=np.zeros(len(cl),np.int8);st[e1>e2]=1;st[e1<e2]=-1
    bi=np.searchsorted(bars,t//tf_ms,side='left')-1;out=np.zeros(len(t),np.int8);ok=bi>=0;out[ok]=st[bi[ok]]
    return out

@njit(cache=True)
def sleeve_state(s,h4,h1,m15,m5):
    macro=h4!=0 and h4==h1
    if s==0:
      if macro and m15==m5 and m15==-h1:return 0,m5
      if macro and m15==-h1 and m5==h1:return 1,m5
    elif s==2:
      if macro and m15==h1 and m5==-h1:return 2,m5
      if macro and m15==-h1 and m5==h1:return 3,m5
    elif s==3:
      if macro and m15==m5 and m15==-h1:return 4,m5
      if macro and m15==m5 and m15==h1:return 5,-m5
    elif s==4:
      if h4!=0 and h1!=0 and h4!=h1:
       if m15!=0 and m5==-m15:return 6,m5
       if m15==m5 and m15!=0:return 7,-m5
    elif s==5:
      if h4==h1 and h1==m15 and m15==m5 and h4!=0:return 8,m5
      if h4!=0 and h1!=0 and h4!=h1 and m15!=0 and m5==-m15:return 9,m5
      if macro and m15==h1 and m5==-h1:return 10,-m5
      if macro and m15==m5 and m15==-h1:return 11,m5
    return -1,0

@njit(cache=True)
def sess(t,mode):
    if mode==0:return c.sess_fixed(t)
    tod=t%DAY;ls=7*3600000 if t>=c.UK_DST_START_2026_MS else 8*3600000;ns=12*3600000 if t>=c.US_DST_START_2026_MS else 13*3600000
    if tod>=23*3600000 or tod<ls:return 0
    if tod<ls+2*3600000:return 1
    ov=ns+30*60000
    if tod<ov:return 2
    if tod<ov+150*60000:return 3
    nyend=20*3600000 if ns==13*3600000 else 19*3600000
    if tod<nyend:return 4
    if tod<nyend+2*3600000:return 5
    return 6

@njit(cache=True)
def phase(sl,t,gate_mask,session_mode):
    # bit0 Asia gate enabled; bit1 London-takeover gate enabled. 3 = accepted January gates, 0 = neither.
    minute=(t%DAY)//60000
    if sl==0 and (gate_mask&1): return minute>=1380
    if sl==2 and (gate_mask&2): return 660<=minute<720
    return True

@njit(cache=True)
def sim(t,a,b,mid,h4,h1,m15,m5,entry_start,entry_end,session_mode,gate_mask,genealogy_mode=0,maxpos=3):
    # genealogy 0 sleeve-local, 1 physical session-shared. Single landing-cell event per ordered tick.
    seen=np.zeros((12,32768),np.uint8);shared=np.zeros(32768,np.uint8);off=16384
    act=np.zeros(8,np.uint8);dr=np.zeros(8,np.int8);ent=np.zeros(8,np.int32);et=np.zeros(8,np.int64);stp=np.zeros(8,np.int32);tgt=np.zeros(8,np.int32);sv=np.zeros(8,np.int8)
    # result net,gp,gl,tr,wins,entries,skip,tp,sl,age,maxopen,bdd,edd,mineq,forced
    R=np.zeros(15,np.float64); S=np.zeros((12,6),np.float64)
    bal=0.;peak=0.;open_n=0;s0=-1;anchor=0;prev=0
    for i in range(t.size):
      ti=t[i];ask=int(a[i]);bid=int(b[i]);floating=0.
      # manage exits only for positions opened in window
      for j in range(8):
       if not act[j]:continue
       d=int(dr[j]);e=int(ent[j]);reason=0;ex=0
       if d>0:
        if bid>=tgt[j]:reason=1;ex=bid
        elif bid<=stp[j]:reason=2;ex=bid
        elif ti-et[j]>=300000:reason=3;ex=bid
        else:floating+=(bid-e)/1000.-.01
       else:
        if ask<=tgt[j]:reason=1;ex=ask
        elif ask>=stp[j]:reason=2;ex=ask
        elif ti-et[j]>=300000:reason=3;ex=ask
        else:floating+=(e-ask)/1000.-.01
       if reason:
        pnl=((ex-e) if d>0 else (e-ex))/1000.-.02;bal+=pnl;R[0]+=pnl;R[3]+=1;slv=int(sv[j]);S[slv,0]+=pnl;S[slv,1]+=1
        if pnl>0:R[1]+=pnl;R[4]+=1;S[slv,3]+=pnl;S[slv,5]+=1
        else:R[2]+=pnl;S[slv,4]+=pnl
        R[6+reason]+=1;act[j]=0;open_n-=1
      if bal>peak:peak=bal
      dd=peak-bal
      if dd>R[11]:R[11]=dd
      eq=bal+floating;edd=peak-eq
      if edd>R[12]:R[12]=edd
      if eq<R[13]:R[13]=eq
      s=sess(ti,session_mode)
      if s!=s0:
       s0=s;anchor=int(mid[i]);prev=0;seen[:]=0;shared[:]=0;continue
      g=int(GAPS[s])
      if g<=0:continue
      cell=(int(mid[i])-anchor)//g
      if cell==prev:continue
      d=1 if cell>prev else -1;slv,expected=sleeve_state(s,h4[i],h1[i],m15[i],m5[i]);key=(cell if d>0 else prev)+off
      # Always advance genealogy during warmup; only trade inside requested interval.
      if slv>=0 and 0<=key<32768:
       was=shared[key]!=0 if genealogy_mode==1 else seen[slv,key]!=0
       ok=(not was) and d==expected and phase(slv,ti,gate_mask,session_mode)
       if ok and ti>=entry_start and ti<entry_end:
        R[5]+=1;S[slv,2]+=1
        if open_n>=maxpos:R[6]+=1
        else:
         jj=-1
         for q in range(8):
          if not act[q]:jj=q;break
         if jj>=0:
          act[jj]=1;dr[jj]=d;ent[jj]=ask if d>0 else bid;et[jj]=ti;sv[jj]=slv;open_n+=1
          stp[jj]=ent[jj]-SL[slv] if d>0 else ent[jj]+SL[slv];tgt[jj]=ent[jj]+TP[slv] if d>0 else ent[jj]-TP[slv]
          if open_n>R[10]:R[10]=open_n
       if genealogy_mode==1:shared[key]=1
       else:seen[slv,key]=1
      prev=cell
      if ti>=entry_end and open_n==0: # after window and flat, can stop early
       # Can't return here because first tick after end could be before final month; safe once after end.
       pass
    # forced last tick
    if len(t):
     ask=int(a[-1]);bid=int(b[-1])
     for j in range(8):
      if act[j]:
       d=int(dr[j]);e=int(ent[j]);ex=bid if d>0 else ask;pnl=((ex-e) if d>0 else (e-ex))/1000.-.02;bal+=pnl;R[0]+=pnl;R[3]+=1;slv=int(sv[j]);S[slv,0]+=pnl;S[slv,1]+=1
       if pnl>0:R[1]+=pnl;R[4]+=1;S[slv,3]+=pnl;S[slv,5]+=1
       else:R[2]+=pnl;S[slv,4]+=pnl
       R[14]+=1
    return R,S

def make_states(t,b,tfconf):
    # tfconf tuple spans H4,H1,M15,M5 as (fast,slow)
    return tuple(bar_states_span(t,b,ms,*sp) for ms,sp in zip([4*3600000,3600000,15*60000,5*60000],tfconf))

def metric(R):
 return dict(net=R[0],gp=R[1],gl=R[2],trades=int(R[3]),wins=int(R[4]),entries=int(R[5]),skips=int(R[6]),tp=int(R[7]),sl=int(R[8]),age=int(R[9]),maxopen=int(R[10]),bdd=R[11],edd=R[12],mineq=R[13],forced=int(R[14]),pf=(R[1]/-R[2] if R[2]<0 else 999),exp=(R[0]/R[3] if R[3] else 0),win=(R[4]/R[3] if R[3] else 0))

if __name__=='__main__':
 variants=[
  ('BASE_FIXED_GATES',0,3,((8,21),(8,21),(8,21),(8,21))),
  ('FIXED_NO_ASIA_GATE',0,2,((8,21),(8,21),(8,21),(8,21))),
  ('FIXED_NO_LONDON_GATE',0,1,((8,21),(8,21),(8,21),(8,21))),
  ('FIXED_NO_GATES',0,0,((8,21),(8,21),(8,21),(8,21))),
  ('DST_GATES',1,3,((8,21),(8,21),(8,21),(8,21))),
  ('DST_NO_ASIA_GATE',1,2,((8,21),(8,21),(8,21),(8,21))),
  ('DST_NO_LONDON_GATE',1,1,((8,21),(8,21),(8,21),(8,21))),
  ('DST_NO_GATES',1,0,((8,21),(8,21),(8,21),(8,21))),
 ]
 allres={k:{} for k,*_ in variants}
 for m in range(1,8):
  st=time.time();t,sa,sb,start,end=load_month(m,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);states=make_states(t,b,variants[0][3]);print('month',m,'ticks',len(t),'prep',time.time()-st,flush=True)
  for name,sm,gm,tf in variants:
   R,S=sim(t,a,b,mid,*states,max(start,c.ENTRY_START),end,sm,gm,0,3);allres[name][m]=metric(R);print(name,m,allres[name][m],flush=True)
 with open('/mnt/data/stmr_session_phase1.json','w') as f:json.dump(allres,f,indent=2)
 print('AGG')
 for name in allres:
  r=allres[name];print(name,'net',sum(x['net'] for x in r.values()),'gp',sum(x['gp'] for x in r.values()),'gl',sum(x['gl'] for x in r.values()),'tr',sum(x['trades'] for x in r.values()),'monthly',[round(r[m]['net'],2) for m in range(1,8)])