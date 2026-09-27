exec(open('/mnt/data/gamma2_recovery_jan_variants.py').read().split('def main():')[0])

def met(v):
    v=np.asarray(v,float)
    gp=float(v[v>0].sum()); gl=float(v[v<0].sum())
    return {'trades':int(len(v)),'winners':int((v>0).sum()),'win':float((v>0).mean()) if len(v) else 0.0,'net':float(v.sum()),'gl':gl,'pf':(gp/-gl if gl<0 else (999.0 if gp>0 else 0.0))}

@njit
def gen_tick_ts(t,mid,sec_ids,first_ix,hb,lb,cb,m5,al,ash,cont_mode,liq_shift,ts_mode,align_mode):
 cap=180000;X=np.empty((cap,4),np.float64);n=0
 state=0;level=0.;started=0;break_t=0;reclaim_t=0;minute=-1;trades=0;cool_until=-1;j=0
 for i in range(len(t)):
  s=t[i]//1000
  while j+1<len(sec_ids) and sec_ids[j+1]<=s:j+=1
  mn=s//60
  if mn!=minute:
   minute=mn;trades=0;state=0;level=0.;started=0;break_t=0;reclaim_t=0
  if s<cool_until or trades>=5 or j<21:continue
  av=m5[j]
  if not np.isfinite(av) or av+1e-12<floor_session(s):continue
  newest=j-1+liq_shift;oldest=newest-19
  if oldest<0 or newest>=j:continue
  upper=-1e18;lower=1e18
  for q in range(oldest,newest+1):
   if hb[q]>upper:upper=hb[q]
   if lb[q]<lower:lower=lb[q]
  bid=mid[i]-H;ask=mid[i]+H;oldestv=j-5
  if oldestv<0:continue
  prev=cb[oldestv];start=prev;travel=0.
  for q in range(oldestv+1,j):v=cb[q];travel+=abs(v-prev);prev=v
  travel+=abs(bid-prev);disp=bid-start;eff=abs(disp)/(travel+1e-9)
  if state==0:
   if ask>=upper+.10:state=1;level=upper;started=s;break_t=t[i];reclaim_t=0
   elif bid<=lower-.10:state=-1;level=lower;started=s;break_t=t[i];reclaim_t=0
  if state==1:
   if ask<=level-.15:state=2;started=s;reclaim_t=t[i]
   elif s-started>=2 and ask>=level+.08 and disp>=.15 and eff>=.30:
    if cont_mode==1:state=0;level=0.;started=0
    elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool_until=s+1
    elif cont_mode==3:state=0;level=0.;started=0;trades+=1
    elif cont_mode==4:state=0;level=0.;started=0;cool_until=s+1
  elif state==-1:
   if bid>=level+.15:state=-2;started=s;reclaim_t=t[i]
   elif s-started>=2 and bid<=level-.08 and disp<=-.15 and eff>=.30:
    if cont_mode==1:state=0;level=0.;started=0
    elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool_until=s+1
    elif cont_mode==3:state=0;level=0.;started=0;trades+=1
    elif cont_mode==4:state=0;level=0.;started=0;cool_until=s+1
  elif state==2:
   if disp<=-.15 and eff>=.30:
    sig=t[i] if ts_mode==0 else (break_t if ts_mode==1 else (reclaim_t if ts_mode==2 else first_ix[j]))
    jj=j
    if align_mode==1:
     es=sig//1000;jj=np.searchsorted(sec_ids,es)
     if jj>=len(sec_ids):jj=len(sec_ids)-1
    X[n,0]=sig;X[n,1]=-1;X[n,2]=level;X[n,3]=ash[jj];n+=1;trades+=1;cool_until=s+1;state=0;level=0.;started=0
   
  elif state==-2:
   if disp>=.15 and eff>=.30:
    sig=t[i] if ts_mode==0 else (break_t if ts_mode==1 else (reclaim_t if ts_mode==2 else first_ix[j]))
    jj=j
    if align_mode==1:
     es=sig//1000;jj=np.searchsorted(sec_ids,es)
     if jj>=len(sec_ids):jj=len(sec_ids)-1
    X[n,0]=sig;X[n,1]=1;X[n,2]=level;X[n,3]=al[jj];n+=1;trades+=1;cool_until=s+1;state=0;level=0.;started=0
  if state!=0 and started>0 and s-started>20:state=0;level=0.;started=0;break_t=0;reclaim_t=0
 return X[:n]

def main2():
 d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False);a=d.ask_raw.to_numpy(np.float64)/1000.;b=d.bid_raw.to_numpy(np.float64)/1000.;mid=(a+b)*.5;mb=mid-H
 sec,first_t,o,h,l,c,first_ix,last_ix=active_seconds(t,mb); e5,r5,a5=aggregate(sec,h,l,c,300);m5=map_completed(sec,e5,a5);al=np.zeros(len(sec),np.int8);ash=np.zeros(len(sec),np.int8)
 for tf in (60,180,300,600,1200):
  e,r,a2=aggregate(sec,h,l,c,tf);rr=map_completed(sec,e,r);aa=map_completed(sec,e,a2);ok=np.isfinite(aa);al+=((rr>0)&ok).astype(np.int8);ash+=((rr<0)&ok).astype(np.int8)
 rows=[]
 for lv in (0,-1):
  for cm in (0,1,2,3,4):
   for tm in (0,1,2,3):
    for am in (0,1):
     X=gen_tick_ts(t,mid,sec,first_ix,h,l,c,m5,al,ash,cm,lv,tm,am);rows.append(evalx(f'lv{lv}_cont{cm}_ts{tm}_align{am}',X,t,mid))
 Path('/mnt/data/GAMMA2_RETRO_TS.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main2()
