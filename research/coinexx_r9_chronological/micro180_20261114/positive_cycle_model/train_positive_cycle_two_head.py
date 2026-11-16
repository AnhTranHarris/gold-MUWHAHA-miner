"""Two independent positive-only trade-pattern entry heads, original quote feed.
Discovery labels: original R9 net>0 AND Coinexx mapped quote net>0, both quoted
marks eligible; never pass labels/times to online entry decision. First stage
samples both sides once each observed second; second head learns from source-only as-of quote features at each second.
Actual reentry exposure is enforced later by Micro180's own first-exit state.
"""
from __future__ import annotations
import csv,gzip,math,json,collections,datetime,hashlib,sys,time,os
import numpy as np
from lightgbm import LGBMClassifier

SOURCE=os.environ.get('SOURCE','/mnt/data/GoldMuwahaha_R9_TickLog_REAL_TESTER_20260101_000000_part01_of_10.csv.gz')
MERGED=os.environ.get('MERGED','/mnt/data/r9_synthetic_teacher_to_original_REAL_TickLogger_9m_trade_marks.csv.gz.csv')
MAX=int(os.environ.get('MAX_QUOTES','1800000'))
OUT=os.environ.get('OUT','/mnt/data/micro180_positive_entry_rebuild/positive_cycle_model')
os.makedirs(OUT,exist_ok=True)
FEATURES=['sec_of_minute','spread_u','atr_u','side_barrier_u','mid_change_since_minute','signed_s1_disp','s1_eff','s1_range','s1_turns','signed_ret1','signed_ret3','signed_ret5','signed_ret10','signed_ret15','signed_ret30','signed_ret60','signed_ret180','signed_ret300','signed_acc3','signed_basket5','signed_basket15','prior10_eff','prior30_eff','momentum_phase','hour']
SECOND_FEATURES=FEATURES+['prior_reversal_3s_u','prior_reversal_5s_u','prior_reversal_15s_u','signed_minute_high_gap_u','signed_minute_low_gap_u','signed_prior30s_bias_u','signed_prior60s_bias_u','signed_cross_basket_5_15_u','spread_delta_prev_second_u','near_minute_end_indicator']
start=time.time(); grouped=collections.defaultdict(dict); counts=collections.Counter()
with gzip.open(MERGED,'rt') as f:
 for r in csv.DictReader(f):
  d=datetime.datetime.strptime(r['entry_time_broker'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
  minute=int(d.timestamp())//60; leg=int(r['leg']); side=1 if r['side']=='buy' else -1
  net=float(r['net_usd']); q=float(r['quote_net']) if r['quote_net'].strip() else float('nan')
  valid=(0<=int(r['elag_ms'])<=2000 and 0<=int(r['xlag_ms'])<=2000 and math.isfinite(q))
  grouped[minute][leg]=(int(d.timestamp()),side,int(r['q_entry_u']),int(r['equote_ms']),False,net,q,valid)
  counts['original_teacher_rows']+=1
refs1={}; refs2={}; family1={}; family2={}
for minute, legs in grouped.items():
 first=legs.get(1);second=legs.get(2)
 if first is None: continue
 if second is None:fam='A'
 elif first[5]>0 and second[5]>0:fam='B'
 elif first[5]<=0 and second[5]>0:fam='C'
 else: continue
 all_legs=list(legs.values())
 # A POSITIVE COMPLETE CYCLE may start with an adverse first leg (family C).
 # The outcome-only class is used for TRAINING TARGET CONSTRUCTION, never
 # supplied as a feature or at a candidate execution decision.
 if not all(x[7] for x in all_legs):continue
 net=sum(x[5] for x in all_legs)
 quote=sum(x[6] for x in all_legs)
 if net<=0 or quote<=0: continue
 refs1[minute]=first;family1[minute]=fam
 if second is not None:refs2[minute]=second;family2[minute]=fam
 counts[f'positive_cycles_{fam}']+=1
 counts[f'positive_first_{fam}']+=1
 if second is not None:counts[f'positive_second_{fam}']+=1
 counts['reference_original_positive_cycle_net_usd']+=net
 counts['reference_mapped_positive_cycle_quote_net_usd']+=quote
counts['positive_first_targets']=len(refs1)
counts['positive_second_targets']=len(refs2)
counts['positive_reference_target_legs']=len(refs1)+len(refs2)
print('REFERENCE_POSITIVE_CYCLES',dict(counts),flush=True)
grouped.clear()

hist={};hist_q=collections.deque();cb=collections.deque(maxlen=305)
cur_hi=cur_lo=cur_close=None;last_sec=None;last_mid=None
minute_key=None;minute_first=None;b5=None;b15=None;mid5=None;mid15=None
raw=[];labs=[];steps=[];context2=[]; contexts_ms=[]; first_times=[];first_buy=[];first_sell=[]
rearm=None;prev_entry=None;last_position=None;last_first_mfe=0;last_first_mae=0;last_spread=None;minute_hi=minute_lo=None;previous_spread=0
source_start=source_end=None; n=0; count_events=collections.Counter();

def past(sec,age):
 for delay in (0,1,2):
  v=hist.get(sec-age-delay)
  if v is not None:return v
 return None

def eff(sec,span):
 v=[hist[sec-j] for j in range(span,0,-1) if sec-j in hist]
 if len(v)<max(3,span//2):return 0.
 return abs(v[-1]-v[0])/(sum(abs(b-a) for a,b in zip(v,v[1:]))+1e-6)

with gzip.open(SOURCE,'rt',newline='') as f:
 reader=csv.reader(f);head=next(reader); idx={v:k for k,v in enumerate(head)}
 for r in reader:
  n+=1
  if MAX and n>MAX: n=MAX; break
  ms=int(r[idx['time_msc']]); sec=ms//1000;minute=sec//60
  if source_start is None:source_start=ms
  source_end=ms
  bid=int(round(float(r[idx['bid']])*100));ask=int(round(float(r[idx['ask']])*100));mid=(bid+ask)/2;spread=ask-bid
  ev=r[idx['event']];count_events[ev]+=1
  if minute!=minute_key:
   minute_key=minute;minute_first=mid;minute_hi=minute_lo=mid;rearm=None;prev_entry=None;last_position=None;last_first_mfe=0;last_first_mae=0
  # Observe true R9 REAL logger first position state ONLY from past/current event.
  # Position close is registered when the feed reports REARM; no future teacher state.
  if ev in ('ENTRY_BUY','ENTRY_SELL') and int(r[idx['rearm_number']])==0:
   prev_entry=(ms,1 if ev=='ENTRY_BUY' else -1,ask if ev=='ENTRY_BUY' else bid,spread)
   rearm=None;last_position=prev_entry
  if prev_entry is not None and int(r[idx['position_open']])==1 and int(r[idx['rearm_number']])==0:
   last_first_mfe=max(last_first_mfe,int(round(float(r[idx['mfe']])*100)))
   last_first_mae=max(last_first_mae,int(round(float(r[idx['mae']])*100)))
  if ev=='REARM' and int(r[idx['rearm_number']])==1 and prev_entry is not None:
   oldtime,oldside,oldpx,oldspread=prev_entry
   exitprice=bid if oldside>0 else ask
   realized=oldside*(exitprice-oldpx)
   rearm=(ms,-oldside,realized,last_first_mfe,last_first_mae,ms-oldtime,oldtime,mid,sec%60,oldspread)
  if ev in ('ENTRY_BUY','ENTRY_SELL') and int(r[idx['rearm_number']])>=1:
   rearm=None
  minute_hi=max(minute_hi,mid);minute_lo=min(minute_lo,mid)
  if b5!=sec//5:b5=sec//5;mid5=mid
  if b15!=sec//15:b15=sec//15;mid15=mid
  if last_sec==sec:
   last_mid=mid;cur_hi=max(cur_hi,bid);cur_lo=min(cur_lo,bid);cur_close=bid
   continue
  if last_sec is not None:
   cb.append((last_sec,cur_close,cur_hi,cur_lo))
   hist[last_sec]=last_mid;hist_q.append(last_sec)
   while hist_q and hist_q[0]<sec-305:del hist[hist_q.popleft()]
  last_sec=sec;last_mid=mid;cur_hi=cur_lo=cur_close=bid
  first_times.append(ms);first_buy.append(ask);first_sell.append(bid)
  previous_spread=spread
  atr=float(r[idx['atr']])*100
  disp=ef=rng=turns=0.
  if len(cb)>=11:
   v=list(cb)[-10:]; cl=[a[1] for a in v];diff=[b-a for a,b in zip(cl,cl[1:])];disp=cl[-1]-cl[0]
   ef=abs(disp)/(sum(abs(x) for x in diff)+1e-9)
   rng=max(a[2] for a in v)-min(a[3] for a in v)
   signs=[1 if d>0 else -1 for d in diff if d];turns=sum(a!=b for a,b in zip(signs,signs[1:]))
  changes=[mid-p if p is not None else 0 for p in [past(sec,h) for h in (1,3,5,10,15,30,60,180,300)]]
  p6=past(sec,6);acc=2*changes[1]-(mid-(p6 if p6 is not None else mid))
  e10=eff(sec,10);e30=eff(sec,30)
  for side in (1,-1):
   price=ask if side>0 else bid
   barrier=side*(price-(minute_first+side*15))
   vec=[sec%60,spread,atr,barrier,side*(mid-minute_first),side*disp,ef,rng,turns]
   vec.extend(side*x for x in changes)
   vec.extend([side*acc,side*(mid-mid5),side*(mid-mid15),e10,e30,side*changes[3]/max(10,math.sqrt(max(1,atr))),(sec//3600)%24])
   r1=refs1.get(minute)
   label1=int(r1 is not None and r1[0]==sec and r1[1]==side)
   raw.append((minute,ms,side,price,vec));labs.append(label1)
   # SECOND-HEAD: online, same-quote causal reversal features for ALL possible
   # quote-seconds. Never require REAL_LOGGER REARM: synthetic positive second
   # references mostly precede/avoid those separate R9 real-quote state changes.
   # Micro180 execution later gates the hazard by its OWN observed first close.
   if sec%60 >= 1:
    p3=past(sec,3);p5=past(sec,5);p15=past(sec,15)
    p30=past(sec,30);p60=past(sec,60)
    rev3=side*(mid-(p3 if p3 is not None else mid))
    rev5=side*(mid-(p5 if p5 is not None else mid))
    rev15=side*(mid-(p15 if p15 is not None else mid))
    ctx=[rev3,rev5,rev15,side*(mid-minute_hi),side*(mid-minute_lo),
         side*(mid-(p30 if p30 is not None else mid)),
         side*(mid-(p60 if p60 is not None else mid)),
         side*(mid5-mid15),spread-previous_spread,float(sec%60>=45)]
    ref=refs2.get(minute)
    label2=int(ref is not None and ref[0]==sec and ref[1]==side)
    context2.append((minute,ms,side,price,vec+ctx))
    contexts_ms.append(label2)
 if n%700000==0:print('PROGRESS',n,len(raw),len(context2),round(time.time()-start,2),flush=True)
print('COLLECTED',{'source_quotes':n,'first_seconds_side_rows':len(raw),'second_eligible_side_rows':len(context2),'first_positive_events':sum(labs),'second_positive_events':sum(contexts_ms),'elapsed':round(time.time()-start,2)},flush=True)

X=np.array([x[4] for x in raw],dtype=np.float32);y=np.asarray(labs,dtype=np.uint8)
mi=np.array([x[0] for x in raw],dtype=np.int64);ts=np.array([x[1] for x in raw],dtype=np.int64);sides=np.array([x[2] for x in raw],dtype=np.int8);pr=np.array([x[3] for x in raw],dtype=np.int32)
Xs=np.asarray([x[4] for x in context2],dtype=np.float32).reshape((-1,len(SECOND_FEATURES)));ys=np.asarray(contexts_ms,dtype=np.uint8)
mi2=np.asarray([x[0] for x in context2],dtype=np.int64); ts2=np.asarray([x[1] for x in context2],dtype=np.int64);si2=np.asarray([x[2] for x in context2],dtype=np.int8);pr2=np.asarray([x[3] for x in context2],dtype=np.int32)
msfirst=np.asarray(first_times,dtype=np.int64);bf=np.asarray(first_buy,dtype=np.int32);sf=np.asarray(first_sell,dtype=np.int32)
minutes=np.unique(mi); train_end=minutes[int(len(minutes)*.58)-1];valid_end=minutes[int(len(minutes)*.78)-1]
train=mi<=train_end;valid=(mi>train_end)&(mi<=valid_end);test=mi>valid_end
train2=mi2<=train_end;valid2=(mi2>train_end)&(mi2<=valid_end);test2=mi2>valid_end
print('SPLITS',{'minutes':len(minutes),'first_positive_train_valid_test':[int(y[z].sum()) for z in (train,valid,test)],'second_positive_train_valid_test':[int(ys[z].sum()) for z in (train2,valid2,test2)],'second_causal_candidate_counts':[int(z.sum()) for z in (train2,valid2,test2)]},flush=True)

def fit(X,y,mask,names,tag):
 count=int(y[mask].sum());total=int(mask.sum())
 if count<20:return None
 model=LGBMClassifier(n_estimators=185,learning_rate=.04,num_leaves=13,min_child_samples=110,reg_lambda=12.,colsample_bytree=.84,verbosity=-1,n_jobs=2,
                      scale_pos_weight=min(50,max(1.,float((total-count)/count)/5)))
 model.fit(X[mask],y[mask],feature_name=names)
 model.booster_.save_model(OUT+'/micro180_positive_'+tag+'_hazard_model.txt')
 return model

first_model=fit(X,y,train,FEATURES,'first')
second_model=fit(Xs,ys,train2,SECOND_FEATURES,'second')

# Evaluate from predicted score on each elapsed second without target events.
# Then commit to first actual quote NEXT second. Exactly one first and at most
# one second per minute; no hindsight maximum or future teacher events.

def predict_online(model,X,mask,mi,ts,side,price,threshold,prob=None):
 if model is None:return {}
 ids=np.flatnonzero(mask)
 if prob is None:prob=model.predict_proba(X[mask])[:,1]
 result={}
 for k,v in zip(ids,prob):
  m=int(mi[k]);
  if m not in result and v>=threshold:
   result[m]=(int(ts[k]),int(side[k]),int(price[k]))
 return result

def schedule(decisions):
 result={};rejected=0
 for m,(t,side,_) in decisions.items():
  seek=(t//1000+1)*1000
  j=int(np.searchsorted(msfirst,seek,'left'))
  if j>=len(msfirst) or msfirst[j]>seek+2000 or msfirst[j]//60000!=m:
   rejected+=1;continue
  result[m]=(int(msfirst[j]),side,int(bf[j] if side==1 else sf[j]))
 return result,rejected

def score(pred,refs,valid_minutes):
 subset={m:r for m,r in refs.items() if m in valid_minutes}; matched=correct=close=near=exact=0;times=[];pxs=[]
 for minute,ref in subset.items():
  q=pred.get(minute)
  if q is None:continue
  matched+=1
  t,s,p=q
  if s!=ref[1]:continue
  correct+=1;dt=t-ref[3];dp=p-ref[2]
  times.append(abs(dt));pxs.append(abs(dp))
  close+=abs(dt)<=2000 and abs(dp)<=5
  near+=abs(dp)<=5
  exact+=dt==0 and dp==0
 return {'target_positive':len(subset),'candidate':len(pred),'matched_minute':matched,'correct_side':correct,'exact_mapped':exact,'within_mapped_2s_5c':close,'price_within_5c':near,
         'extra_candidate_minutes':sum(m not in subset for m in pred),'recall_correct_side':round(correct/max(1,len(subset)),4),'precision_positive_side':round(correct/max(1,len(pred)),4),
         'median_abs_mapped_ms':float(np.median(times)) if times else None,'median_abs_price_cents':float(np.median(pxs)) if pxs else None}

def best_threshold(model,X,mask,mi,ts,si,pr,refs):
 prob=model.predict_proba(X[mask])[:,1]
 allowed=set(int(m) for m in np.unique(mi[mask]));out=[]
 for threshold in (.015,.025,.04,.06,.08,.10,.13,.16,.20,.25,.30,.4,.5,.6,.7):
  decisions=predict_online(model,X,mask,mi,ts,si,pr,threshold,prob=prob)
  sched,skip=schedule(decisions)
  metrics=score(sched,refs,allowed)
  # Positive-only targets mean unmatched opportunities may be unlabelled
  # (not proven negative); penalize extra entries to avoid saturation.
  util=5*metrics['exact_mapped']+2.5*metrics['within_mapped_2s_5c']+0.4*metrics['correct_side']-0.45*metrics['extra_candidate_minutes']
  out.append((float(threshold),float(util),metrics,skip))
 return max(out,key=lambda x:x[1]),[{'threshold':a,'utility':round(b,3),'metrics':m} for a,b,m,_ in out]

r={'source':os.path.basename(SOURCE),'max_quotes':MAX,'actual_quotes':n,'source_msec_start_end':[source_start,source_end],
   'positive_target_definition':'A/B/C original complete cycle net>0 AND mapped quote cycle net>0, all entry/exit lags<=2s; C first loss kept as positive precursor',
   'original_trade_accounting_unchanged':True,'future_family_class_in_strategy_features':False,'positive_cycle_family_diagnostic_only':True,
   'first_model_is_independent_multihorizon_quote_hazard':True,
   'second_shadow_condition_source':'independent as-of quote reversal features; executable second head must subsequently be gated by micro180 own earlier closed first leg (not R9 REAL logger rearm)',
   'onpolicy_micro180_2nd_exposure_proven':False,'second_head_training_is_unconditional_positive_target_with_separate_causal_rearm_execution_gate':True,
   'counts':dict(counts),'source_events':dict(count_events),'positive_cycle_target_counts':dict(counts),'samples':{'first_rows':len(raw),'second_candidate_rows':len(context2),
        'first_positive_labels':int(y.sum()),'second_positive_labels':int(ys.sum())},
   'split_minute_keys':[int(train_end),int(valid_end)]}
for kind,model,arr,valid_mask,test_mask,m,t,s,p,refs in (
 ('first',first_model,X,valid,test,mi,ts,sides,pr,refs1),
 ('second',second_model,Xs,valid2,test2,mi2,ts2,si2,pr2,refs2)):
 if model is None:
  r[kind]={'status':'insufficient causal positive labels to fit'};continue
 selected,curve=best_threshold(model,arr,valid_mask,m,t,s,p,refs)
 chosen=selected[0];dec=predict_online(model,arr,test_mask,m,t,s,p,chosen);scheduled,skip=schedule(dec)
 valid_minutes=set(int(x) for x in np.unique(m[valid_mask]));test_minutes=set(int(x) for x in np.unique(m[test_mask]))
 r[kind]={'validation_selected_threshold':chosen,'validation_curve':curve,'validation':selected[2],
          'heldout_immediate':score(dec,refs,test_minutes),
          'heldout_next_second':score(scheduled,refs,test_minutes),
          'heldout_refs_observable_for_hazard':sum(x in test_minutes for x in refs),
          'positive_cycle_targets_family_counts':dict(collections.Counter((family1 if kind=='first' else family2).values())), 'model_sha256':hashlib.sha256(open(OUT+'/micro180_positive_'+kind+'_hazard_model.txt','rb').read()).hexdigest(),
          'top_features':sorted(zip((FEATURES if kind=='first' else SECOND_FEATURES),model.feature_importances_.tolist()),key=lambda x:-x[1])[:12]}
print('RESULT',json.dumps({k:r[k] for k in ('samples','first','second')},indent=2),flush=True)
with open(OUT+'/micro180_positive_two_head_experiment_results.json','w') as f:json.dump(r,f,indent=2)
print('SECONDS',round(time.time()-start,3),flush=True)
