exec(open('/mnt/data/gamma2_recovery_timestamp_alignment.py').read().split('def main4():')[0])

def metric(v):
 gp=float(v[v>0].sum());gl=float(v[v<0].sum());return {'trades':len(v),'winners':int((v>0).sum()),'win':float((v>0).mean()),'net':float(v.sum()),'gp':gp,'gl':gl,'pf':gp/-gl if gl<0 else 999.}

def main5():
 d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False);a=d.ask_raw.to_numpy(np.float64)/1000.;b=d.bid_raw.to_numpy(np.float64)/1000.;mid=(a+b)*.5;mb=mid-H
 sec,first_t,o,h,l,c,first_ix,last_ix=active_seconds(t,mb);e5,r5,a5=aggregate(sec,h,l,c,300);m5=map_completed(sec,e5,a5);al=np.zeros(len(sec),np.int8);ash=np.zeros(len(sec),np.int8)
 for tf in (60,180,300,600,1200):
  e,r,a2=aggregate(sec,h,l,c,tf);rr=map_completed(sec,e,r);aa=map_completed(sec,e,a2);ok=np.isfinite(aa);al+=((rr>0)&ok).astype(np.int8);ash+=((rr<0)&ok).astype(np.int8)
 rows=[]
 specs=[]
 # causal confirmation and retro ceil-break on quota-only cont3, lv0; also cont2
 for cm in (2,3):
  for rm,lag,name in [(0,0,'confirm') ,(2,0,'ceilbreak'),(0,750,'break750')]:
   # confirm needs special: generator with round0 lag0 is raw break, not confirm, so use gen_tick_bars for causal
   if name=='confirm':
    base=gen_tick_bars(t,mid,sec,first_ix,h,l,c,m5,al,ash,cm,0)
    # no confirm extras; mappings from signal sec
    sigsec=(base[:,0]//1000).astype(np.int64); jj=np.searchsorted(sec,sigsec); jj=np.minimum(jj,len(sec)-1); sides=base[:,1].astype(int)
   else:
    base=gen(t,mid,sec,h,l,c,m5,al,ash,cm,0,lag,rm,0)
    sigsec=(base[:,0]//1000).astype(np.int64); jj=np.searchsorted(sec,sigsec);jj=np.minimum(jj,len(sec)-1);sides=base[:,1].astype(int)
   maps={}
   maps['side']=np.where(sides>0,al[jj],ash[jj])
   maps['opposite']=np.where(sides>0,ash[jj],al[jj])
   maps['max']=np.maximum(al[jj],ash[jj]);maps['min']=np.minimum(al[jj],ash[jj])
   maps['long_only']=al[jj];maps['short_only']=ash[jj]
   maps['all_weak']=np.zeros(len(jj));maps['all_aligned']=np.full(len(jj),5)
   maps['sumclip']=np.minimum(5,al[jj]+ash[jj]);maps['diffabs']=np.abs(al[jj]-ash[jj])
   for mn,av in maps.items():
    X=base[:,:4].copy();X[:,3]=av
    O=replay(t,mid,X);ix=nonoverlap(X,O);q=O[ix];m=metric(q[:,0]);m.update(label=f'c{cm}_{name}_{mn}',raw=len(X),trade_delta=m['trades']-TARGET[0],winner_delta=m['winners']-TARGET[1],win_delta=m['win']-TARGET[2],net_delta=m['net']-TARGET[3],gl_delta=m['gl']-TARGET[4]);rows.append(m)
 def dist(r):return abs(r['trades']-TARGET[0])/TARGET[0]+abs(r['winners']-TARGET[1])/TARGET[1]+abs(r['net']-TARGET[3])/10000+abs(r['gl']-TARGET[4])/10000
 out={'best':sorted(rows,key=dist)[:40],'rows':rows};Path('/mnt/data/GAMMA2_ALIGNMENT_MAPPING_FORENSIC.json').write_text(json.dumps(out,indent=2))
 for r in out['best'][:30]:print(json.dumps(r))
if __name__=='__main__':main5()
