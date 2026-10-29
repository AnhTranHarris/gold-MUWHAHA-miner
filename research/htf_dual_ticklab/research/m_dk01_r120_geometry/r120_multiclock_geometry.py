#!/usr/bin/env python3
"""R120-G native-tick, six-clock + overlapping UTC-session multi-geometry causal state.

Original FILTER08 t0 is a reference: every state at t0 uses ONLY source ticks
with timestamp strictly less than t0.  Completed candles have end<=t0;
developing candle is explicitly labeled partial. Empty interval candles are not
synthesized. Quote size is L1 quoted size only, never trade volume.

No trading performance / M-DK-01 approval is asserted by these features.
"""
import io, json, pathlib, zipfile, hashlib, gc, argparse
import numpy as np
import pandas as pd
from numba import njit

WIDTH=np.array([250,500,1000,5000,15000,30000],dtype=np.int64)
NAMES=['250ms','500ms','1s','5s','15s','30s']
# Asia 00:00-09:00, Europe 07:00-16:00, Americas 13:00-22:00 UTC proxy.
# DST and holiday calendar not provided; these are RESEARCH UTC CLOCK WINDOWS.
SESSION_START=np.array([0,7,13],dtype=np.int64)
SESSION_END=np.array([9,16,22],dtype=np.int64)
PIN={'01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
'02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
'06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
'07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'}
ORIG='/mnt/data/F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip'
ROOT=pathlib.Path('/mnt/data/R120_GRID_GEOMETRY');ROOT.mkdir(exist_ok=True)
# Block per scale = 11 floats: completed bar slopes at 4 & 8, acceleration, trend
# efficiency, side-aware support proximity, breakout direction, realized high-low,
# quoted-size imbalance, bar activity (log), freshest completed age, developing
# candle side-slope.  Additional overlap/per-session coupling features.
FEATURES=[]
for _w in NAMES:
 for _n in ('slope4','slope8','accel','efficiency','support_distance','breakout_pressure','range_raw','size_imbalance','log_quote_count','last_bar_age','partial_signed_delta'):
  FEATURES.append(f'{_w}_{_n}')
for _s in ('asia','london','newyork'):
 for _n in ('active','anchor_trend','range_position','support_distance','quote_flow','log_quote_count'):
  FEATURES.append(f'{_s}_{_n}')
FEATURES+=['allscale_mean_signed_slope4','allscale_std_signed_slope4','micro_macro_trend_conflict','scale_positive_count','wallclock_spread_raw','wallclock_quote_age_ms','utc_hour_sin','utc_hour_cos']

@njit(cache=True)
def build_states(t,bid,ask,av,bv,ev,side):
    n=len(ev); m=len(WIDTH)
    X=np.zeros((n,m*11+3*6+8),dtype=np.float32)
    # per-scale developing bar
    current_id=np.full(m,-1,dtype=np.int64)
    op=np.zeros(m);hi=np.zeros(m);lo=np.zeros(m);cl=np.zeros(m)
    ncur=np.zeros(m,dtype=np.int64)
    qa=np.zeros(m);qb=np.zeros(m);s_cur=np.zeros(m)
    # ring of completed bars -- 24 prior *published* events
    buf_end=np.zeros((m,24),dtype=np.int64);buf_close=np.zeros((m,24))
    buf_high=np.zeros((m,24));buf_low=np.zeros((m,24))
    buf_qa=np.zeros((m,24));buf_qb=np.zeros((m,24));buf_n=np.zeros((m,24),dtype=np.int64)
    count=np.zeros(m,dtype=np.int64)
    # overlapping session anchors
    day_key=np.full(3,-1,dtype=np.int64)
    sess_open=np.zeros(3);sess_hi=np.zeros(3);sess_lo=np.zeros(3)
    sess_tick_n=np.zeros(3,dtype=np.int64);sess_up=np.zeros(3);sess_dn=np.zeros(3)
    prev_mid=0.;prev_tick_time=-1;prev_spread=0.;k=0
    for j in range(n):
        T=ev[j]
        # Ingest strictly earlier source quotes; same-millisecond ticks are excluded.
        while k<len(t) and t[k]<T:
            ts=t[k]; mid=.5*(float(bid[k])+float(ask[k])); sp=ask[k]-bid[k]
            for w in range(m):
                bno=ts//WIDTH[w]
                if current_id[w]!=bno:
                    if current_id[w]>=0:
                        p=count[w]%24
                        buf_end[w,p]=(current_id[w]+1)*WIDTH[w]
                        buf_close[w,p]=cl[w];buf_high[w,p]=hi[w];buf_low[w,p]=lo[w]
                        buf_qa[w,p]=qa[w];buf_qb[w,p]=qb[w];buf_n[w,p]=ncur[w]
                        count[w]+=1
                    current_id[w]=bno;op[w]=mid;hi[w]=mid;lo[w]=mid;cl[w]=mid
                    ncur[w]=1;qa[w]=av[k];qb[w]=bv[k];s_cur[w]=sp
                else:
                    if mid>hi[w]:hi[w]=mid
                    if mid<lo[w]:lo[w]=mid
                    cl[w]=mid;ncur[w]+=1;qa[w]+=av[k];qb[w]+=bv[k];s_cur[w]=sp
            hh=(ts%86400000)//3600000;day=ts//86400000
            for z in range(3):
                if hh>=SESSION_START[z] and hh<SESSION_END[z]:
                    if day_key[z]!=day:
                        day_key[z]=day;sess_open[z]=mid;sess_hi[z]=mid;sess_lo[z]=mid
                        sess_tick_n[z]=0;sess_up[z]=0;sess_dn[z]=0
                    if mid>sess_hi[z]:sess_hi[z]=mid
                    if mid<sess_lo[z]:sess_lo[z]=mid
                    if prev_tick_time>=0 and prev_tick_time//86400000==day:
                        dp=mid-prev_mid
                        if dp>0:sess_up[z]+=dp
                        else:sess_dn[z]-=dp
                    sess_tick_n[z]+=1
            prev_mid=mid;prev_tick_time=ts;prev_spread=sp;k+=1
        slopes=np.zeros(m)
        for w in range(m):
            # Publish any completed candle even if no new source tick after close.
            if current_id[w]>=0 and (current_id[w]+1)*WIDTH[w]<=T:
                p=count[w]%24
                buf_end[w,p]=(current_id[w]+1)*WIDTH[w]
                buf_close[w,p]=cl[w];buf_high[w,p]=hi[w];buf_low[w,p]=lo[w]
                buf_qa[w,p]=qa[w];buf_qb[w,p]=qb[w];buf_n[w,p]=ncur[w]
                count[w]+=1;current_id[w]=-1
            K=min(count[w],24);out=w*11
            if K>0:
                p=(count[w]-1)%24;c0=buf_close[w,p]
                maxh=-1e20;minl=1e20;sumv=0.;path=0.;nta=0.;ntb=0.;nquotes=0
                prevc=c0
                for lag in range(min(K,16)):
                    q=(count[w]-1-lag)%24
                    if buf_high[w,q]>maxh:maxh=buf_high[w,q]
                    if buf_low[w,q]<minl:minl=buf_low[w,q]
                    nta+=buf_qa[w,q];ntb+=buf_qb[w,q];nquotes+=buf_n[w,q]
                    if lag>0:path+=abs(prevc-buf_close[w,q])
                    prevc=buf_close[w,q]
                rng=max(maxh-minl,1.0)
                q4=(count[w]-1-min(K-1,4))%24
                q8=(count[w]-1-min(K-1,8))%24
                c4=buf_close[w,q4];c8=buf_close[w,q8]
                s=side[j]
                X[j,out+0]=s*(c0-c4)/rng
                X[j,out+1]=s*(c0-c8)/rng
                X[j,out+2]=s*(c0-2*c4+c8)/rng
                X[j,out+3]=abs(c0-c8)/(path+1.0)
                X[j,out+4]=(c0-minl)/rng if s>0 else (maxh-c0)/rng
                X[j,out+5]=s*(c0-(maxh+minl)*.5)/rng
                X[j,out+6]=np.log1p(rng)
                X[j,out+7]=(ntb-nta)/(nta+ntb+1e-8)
                X[j,out+8]=np.log1p(nquotes)
                X[j,out+9]=min((T-buf_end[w,p])/WIDTH[w],1e6)
                slopes[w]=X[j,out+0]
            if current_id[w]>=0:
                # developing candle: only previous ticks strictly before original t0
                X[j,out+10]=side[j]*(cl[w]-op[w])/(max(hi[w]-lo[w],1.0))
        hh=(T%86400000)//3600000;day=T//86400000
        for z in range(3):
            u=m*11+z*6
            active=hh>=SESSION_START[z] and hh<SESSION_END[z] and day_key[z]==day
            if active and prev_tick_time>=0:
                r=max(sess_hi[z]-sess_lo[z],1.)
                X[j,u]=1.
                X[j,u+1]=side[j]*(prev_mid-sess_open[z])/r
                X[j,u+2]=(prev_mid-sess_lo[z])/r
                X[j,u+3]=(prev_mid-sess_lo[z])/r if side[j]>0 else (sess_hi[z]-prev_mid)/r
                X[j,u+4]=(sess_up[z]-sess_dn[z])/(sess_up[z]+sess_dn[z]+1.)
                X[j,u+5]=np.log1p(sess_tick_n[z])
        off=m*11+18
        mean=0.
        for w in range(m):mean+=slopes[w]
        mean/=m;X[j,off]=mean
        var=0.;pos=0
        for w in range(m):
            var+=(slopes[w]-mean)**2
            if slopes[w]>0:pos+=1
        X[j,off+1]=np.sqrt(var/m)
        X[j,off+2]=slopes[0]-slopes[5]
        X[j,off+3]=pos
        X[j,off+4]=prev_spread
        X[j,off+5]=T-prev_tick_time if prev_tick_time>=0 else 1e9
        phase=2*np.pi*((T%86400000)/86400000.0)
        X[j,off+6]=np.sin(phase);X[j,off+7]=np.cos(phase)
    return X

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while True:
   c=f.read(1<<22)
   if not c:break
   h.update(c)
 return h.hexdigest()

def load_source(m):
 fn=pathlib.Path(f'/mnt/data/XAUUSD_DUKAS_2026_{m}_ticks.csv.gz')
 assert sha256(fn)==PIN[m],f'RAW SHA MISMATCH {m}'
 with zipfile.ZipFile(ORIG) as z:
  q=np.load(io.BytesIO(z.read(f'F395_S14_dukascopy_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz')))
  original={k:q[k] for k in q.files}
  assert z.testzip() is None
 df=pd.read_csv(fn,compression='gzip',dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32','ask_volume':'float32','bid_volume':'float32'})
 arr=[df[k].to_numpy(copy=True) for k in ('timestamp_ms_utc','bid_raw','ask_raw','ask_volume','bid_volume')]
 del df;gc.collect()
 return arr,original

def main():
 pa=argparse.ArgumentParser();pa.add_argument('--months',nargs='+',default=['01']);pa.add_argument('--dry',action='store_true');args=pa.parse_args()
 for mo in args.months:
  data,orig=load_source(mo)
  ev=orig['t'];side=orig['side'];truth=orig['truth']
  assert np.all(np.diff(ev)>=0) and np.isin(side,[-1,1]).all()
  print('SOURCE',mo,len(data[0]),len(ev),flush=True)
  if args.dry:continue
  X=build_states(*data,ev,side)
  assert X.shape==(len(ev),len(FEATURES)) and np.all(np.isfinite(X))
  np.save(ROOT/f'R120_{mo}_MULTICLOCK_GEOMETRY.npy',X)
  result={'month':mo,'n_events':len(ev),'n_ticks':len(data[0]),'raw_sha256':PIN[mo],
    'features':FEATURES,'shape':X.shape,'finite':True,
    'active_session_counts':{s:int(X[:,66+ix*6].sum()) for ix,s in enumerate(['asia','london','newyork'])},
    'coverage':{'bars_250ms_valid':int((X[:,9]<1e5).sum()),'bars_30sec_valid':int((X[:,55+9]<1e5).sum())},
    'class_counts':{str(v):int((truth==v).sum()) for v in [0,1,2]},
    'feature_matrix_sha256':sha256(ROOT/f'R120_{mo}_MULTICLOCK_GEOMETRY.npy')}
  (ROOT/f'R120_{mo}_GEOMETRY_RECEIPT.json').write_text(json.dumps(result,indent=2))
  print('FEATURES',mo,X.shape,'sha',result['feature_matrix_sha256'],flush=True)
  del X,data;gc.collect()
if __name__=='__main__':main()