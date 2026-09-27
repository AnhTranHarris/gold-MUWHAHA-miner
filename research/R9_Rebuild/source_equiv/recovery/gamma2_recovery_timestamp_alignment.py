exec(open('/mnt/data/gamma2_recovery_jan_variants.py').read().split('def main():')[0])

def met2(v):
 v=np.asarray(v,float);gp=float(v[v>0].sum());gl=float(v[v<0].sum());return {'trades':int(len(v)),'winners':int((v>0).sum()),'win':float((v>0).mean()) if len(v) else 0.,'net':float(v.sum()),'gp':gp,'gl':gl,'pf':gp/-gl if gl<0 else 999.}

@njit
def gen(t,mid,sec_ids,hb,lb,cb,m5,al,ash,cont_mode,liq_shift,lag_ms,round_mode,align_mode):
 cap=180000;X=np.empty((cap,6),np.float64);n=0
 state=0;level=0.;started=0;break_t=0;minute=-1;trades=0;cool=-1;j=0
 for i in range(len(t)):
  s=t[i]//1000
  while j+1<len(sec_ids) and sec_ids[j+1]<=s:j+=1
  mn=s//60
  if mn!=minute:minute=mn;trades=0;state=0;level=0.;started=0;break_t=0
  if s<cool or trades>=5 or j<21:continue
  if not np.isfinite(m5[j]) or m5[j]+1e-12<floor_session(s):continue
  newest=j-1+liq_shift;oldest=newest-19
  if oldest<0 or newest>=j:continue
  upper=-1e18;lower=1e18
  for q in range(oldest,newest+1):
   if hb[q]>upper:upper=hb[q]
   if lb[q]<lower:lower=lb[q]
  bid=mid[i]-H;ask=mid[i]+H
  start=cb[j-5];prev=start;travel=0.
  for q in range(j-4,j):v=cb[q];travel+=abs(v-prev);prev=v
  travel+=abs(bid-prev);disp=bid-start;eff=abs(disp)/(travel+1e-9)
  if state==0:
   if ask>=upper+.10:state=1;level=upper;started=s;break_t=t[i]
   elif bid<=lower-.10:state=-1;level=lower;started=s;break_t=t[i]
  if state==1:
   if ask<=level-.15:state=2;started=s
   elif s-started>=2 and ask>=level+.08 and disp>=.15 and eff>=.30:
    if cont_mode==1:state=0;level=0.;started=0
    elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool=s+1
    elif cont_mode==3:state=0;level=0.;started=0;trades+=1
    elif cont_mode==4:state=0;level=0.;started=0;cool=s+1
  elif state==-1:
   if bid>=level+.15:state=-2;started=s
   elif s-started>=2 and bid<=level-.08 and disp<=-.15 and eff>=.30:
    if cont_mode==1:state=0;level=0.;started=0
    elif cont_mode==2:state=0;level=0.;started=0;trades+=1;cool=s+1
    elif cont_mode==3:state=0;level=0.;started=0;trades+=1
    elif cont_mode==4:state=0;level=0.;started=0;cool=s+1
  elif state==2:
   if disp<=-.15 and eff>=.30:
    sig=break_t+lag_ms
    if round_mode==1:sig=(sig//1000)*1000
    elif round_mode==2:sig=((sig+999)//1000)*1000
    if sig>t[i]:sig=t[i]
    if align_mode==0: jj=np.searchsorted(sec_ids,sig//1000)
    elif align_mode==1: jj=j
    else: jj=np.searchsorted(sec_ids,break_t//1000)
    if jj>=len(sec_ids):jj=len(sec_ids)-1
    X[n,0]=sig;X[n,1]=-1;X[n,2]=level;X[n,3]=ash[jj];X[n,4]=break_t;X[n,5]=t[i];n+=1;trades+=1;cool=s+1;state=0;level=0.;started=0
  elif state==-2:
   if disp>=.15 and eff>=.30:
    sig=break_t+lag_ms
    if round_mode==1:sig=(sig//1000)*1000
    elif round_mode==2:sig=((sig+999)//1000)*1000
    if sig>t[i]:sig=t[i]
    if align_mode==0: jj=np.searchsorted(sec_ids,sig//1000)
    elif align_mode==1: jj=j
    else: jj=np.searchsorted(sec_ids,break_t//1000)
    if jj>=len(sec_ids):jj=len(sec_ids)-1
    X[n,0]=sig;X[n,1]=1;X[n,2]=level;X[n,3]=al[jj];X[n,4]=break_t;X[n,5]=t[i];n+=1;trades+=1;cool=s+1;state=0;level=0.;started=0
  if state!=0 and started>0 and s-started>20:state=0;level=0.;started=0;break_t=0
 return X[:n]

def main4():
 d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False);a=d.ask_raw.to_numpy(np.float64)/1000.;b=d.bid_raw.to_numpy(np.float64)/1000.;mid=(a+b)*.5;mb=mid-H
 sec,first_t,o,h,l,c,first_ix,last_ix=active_seconds(t,mb);e5,r5,a5=aggregate(sec,h,l,c,300);m5=map_completed(sec,e5,a5);al=np.zeros(len(sec),np.int8);ash=np.zeros(len(sec),np.int8)
 for tf in (60,180,300,600,1200):
  e,r,a2=aggregate(sec,h,l,c,tf);rr=map_completed(sec,e,r);aa=map_completed(sec,e,a2);ok=np.isfinite(aa);al+=((rr>0)&ok).astype(np.int8);ash+=((rr<0)&ok).astype(np.int8)
 rows=[]
 for lv in (0,-1):
  for cm in (2,3):
   for rm in (1,2):
    for lag in (0,250,500,750,1000,1250):
     for am in (0,1,2):
      X=gen(t,mid,sec,h,l,c,m5,al,ash,cm,lv,lag,rm,am);O=replay(t,mid,X[:,:4]);ix=nonoverlap(X[:,:4],O);q=O[ix];m=met2(q[:,0]);m.update(label=f'lv{lv}_c{cm}_r{rm}_lag{lag}_align{am}',raw=len(X),trade_delta=m['trades']-TARGET[0],winner_delta=m['winners']-TARGET[1],win_delta=m['win']-TARGET[2],net_delta=m['net']-TARGET[3],gl_delta=m['gl']-TARGET[4],retro_share=float(np.mean(X[ix,0]<X[ix,5])) if len(ix) else 0.);rows.append(m)
 def dist(r):return abs(r['trades']-TARGET[0])/TARGET[0]+abs(r['winners']-TARGET[1])/TARGET[1]+abs(r['net']-TARGET[3])/10000+abs(r['gl']-TARGET[4])/10000
 out={'target':TARGET,'best':sorted(rows,key=dist)[:40],'rows':rows};Path('/mnt/data/GAMMA2_TIMESTAMP_ALIGNMENT_FORENSIC.json').write_text(json.dumps(out,indent=2))
 for r in out['best'][:30]:print(json.dumps(r))
if __name__=='__main__':main4()
