"""V16 entry-only teacher-to-REAL transfer. Bounded original source streaming.

Run: python v16_train_and_replay.py --merged ORIGINAL_MERGED.csv.gz \
    --ticks ORIGINAL_REAL_TICKLOGGER_part01.csv.gz --max-rows 1800000
Only saves tiny frozen LightGBM models and compact metrics. No tick duplication.
The runtime router does not load any teacher labels, and the holdout replay
uses its OWN fixed preexisting R9 exits for second-entry eligibility.
"""
from __future__ import annotations
import argparse,csv,gzip,json,math,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import lightgbm as lgb
from v16_full_teacher_bridge import (
   Quote,V16CausalBridge,all_teacher_targets,clock_priors,sha256,cents,FEATURE_NAMES)
from dataclasses import dataclass
from zoneinfo import ZoneInfo


def session_floor(time_s:int,offset_minutes:int)->float:
    """Original R9 London/New York M5 ATR floor, at as-of source quote."""
    utc=datetime.fromtimestamp(time_s-offset_minutes*60,timezone.utc)
    lon=utc.astimezone(ZoneInfo('Europe/London'))
    ny=utc.astimezone(ZoneInfo('America/New_York'))
    l=8*60 <= lon.hour*60+lon.minute < 16*60+30
    n=8*60 <= ny.hour*60+ny.minute < 17*60
    return 175. if n else 200. if l else 250.


@dataclass
class OwnPosition:
    """Frozen reference exit/rearm harness. No trade-exit optimization."""
    side:int
    entry_cents:int
    entry_msc:int
    initial_stop_cents:int
    stop_cents:int

    def manage(self,q:Quote)->bool:
        if (self.side==1 and q.bid_cents<=self.stop_cents) or \
           (self.side==-1 and q.ask_cents>=self.stop_cents):
            return True
        if q.second-self.entry_msc//1000>=30:return True
        if self.side==1 and q.bid_cents-self.entry_cents>=10:
            self.stop_cents=max(self.stop_cents,q.bid_cents-3)
        elif self.side==-1 and self.entry_cents-q.ask_cents>=10:
            self.stop_cents=min(self.stop_cents,q.ask_cents+3)
        return False


def row_stream(ticks:Path,max_rows:int):
    with gzip.open(ticks,'rt',encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f)
        need={'run_label','time_msc','bid','ask','atr'}
        if not need.issubset(r.fieldnames or []):raise ValueError('Wrong original REAL source schema')
        prev=-1
        for i,row in enumerate(r):
            if i>=max_rows:break
            if row['run_label']!='REAL':raise ValueError('SYNTH data is forbidden in REAL replay')
            ms=int(row['time_msc'])
            if ms<prev:raise ValueError('REAL TickLogger time out of order')
            prev=ms
            yield i,Quote(ms,cents(row['bid']),cents(row['ask']),float(row['atr'])*100.,
                          session_floor(ms//1000,0))


def ready(q,engine):
    return (q.spread<=25 and q.spread>=0 and
            q.completed_m5_atr_cents is not None and
            q.completed_m5_atr_cents>=q.session_m5_atr_floor_cents and
            len(engine.closed_seconds)>=10)


def build_examples(ticks,targets,priors,train_end:int,valid_end:int,test_end:int):
    engine=V16CausalBridge(priors,threshold=2.)
    engine.feature_only=True
    data={p:{leg:[[],[]] for leg in (1,2)} for p in ('train','valid')}
    seen={p:Counter() for p in ('train','valid','test')}
    first_test_ms=last_test_ms=None
    for i,q in row_stream(ticks,test_end):
        stage='train' if i<train_end else 'valid' if i<valid_end else 'test'
        first=engine.last_sec!=q.second
        engine.observe(q)
        if not first or not ready(q,engine):continue
        seen[stage]['eligible_seconds']+=1
        if stage=='test':
            first_test_ms=q.time_msc if first_test_ms is None else first_test_ms
            last_test_ms=q.time_msc
            continue
        teacher1=targets.get((q.minute,1))
        teacher2=targets.get((q.minute,2))
        if teacher1 is None or q.second<=teacher1['teacher_second']:
            for side in (-1,1):
                label=int(teacher1 is not None and teacher1['teacher_second']==q.second
                          and teacher1['side']==side)
                data[stage][1][0].append(engine.features(q,1,side))
                data[stage][1][1].append(label)
                seen[stage]['positive_first']+=label
        if teacher1 is not None and q.second>teacher1['teacher_second']:
            for side in (-1,1):
                label=int(teacher2 is not None and teacher2['teacher_second']==q.second
                          and teacher2['side']==side)
                data[stage][2][0].append(engine.features(q,2,side))
                data[stage][2][1].append(label)
                seen[stage]['positive_second']+=label
    return data,seen,(first_test_ms,last_test_ms)


def fit(data,out:Path):
    models={};metrics={}
    for leg in (1,2):
        X=np.asarray(data['train'][leg][0],dtype=np.float32)
        y=np.asarray(data['train'][leg][1],dtype=np.int8)
        Xv=np.asarray(data['valid'][leg][0],dtype=np.float32)
        yv=np.asarray(data['valid'][leg][1],dtype=np.int8)
        if not (len(y)>1000 and y.sum()>=10 and yv.sum()>=5):
            raise RuntimeError(f'Insufficient real source aligned {leg} labels: train {y.sum()}; valid {yv.sum()}')
        # False positive penalty and source event class balance are explicit;
        # all negative samples are from observed eligible quote seconds.
        train=lgb.Dataset(X,label=y,feature_name=list(FEATURE_NAMES))
        valid=lgb.Dataset(Xv,label=yv,reference=train)
        model=lgb.train({'objective':'binary','metric':'binary_logloss',
          'num_leaves':15,'max_depth':5,'learning_rate':0.035,
          'min_data_in_leaf':100,'feature_fraction':0.9,'verbosity':-1,
          'num_threads':2,'seed':16,'scale_pos_weight':min(100.,float((len(y)-int(y.sum()))/int(y.sum())))},
          train,num_boost_round=160,valid_sets=[valid],
          callbacks=[lgb.early_stopping(15,verbose=False)])
        model.save_model(str(out/f'v16_teacher_leg{leg}.txt'))
        probs=model.predict(Xv,num_threads=2)
        # Entry sensitivity is calibrated ONLY on an earlier validation
        # window. As rare-event model outputs are not necessarily calibrated
        # to a universal 0.50 threshold, choose from fixed score quantiles.
        from sklearn.metrics import average_precision_score
        ap=float(average_precision_score(yv,probs))
        quantiles=(0.75,0.85,0.90,0.94,0.97,0.985,0.995)
        cutoffs=sorted(set(float(np.quantile(probs,q)) for q in quantiles))
        stats={}
        for t in cutoffs:
            fired=probs>=t
            tp=int((fired & (yv==1)).sum());fp=int((fired & (yv==0)).sum())
            recall=tp/max(1,int(yv.sum()))
            precision=tp/max(1,int(fired.sum()))
            f2=5*precision*recall/max(1e-9,4*precision+recall)
            stats[str(round(t,6))]={'recall':round(recall,5),
                'precision':round(precision,5),'fired':int(fired.sum()),'f2':round(f2,5)}
        threshold=max(cutoffs,key=lambda t:stats[str(round(t,6))]['f2'])
        models[leg]=model
        metrics[f'leg{leg}']={'samples_train':int(len(y)),'positives_train':int(int(y.sum())),
            'samples_valid':int(len(yv)),'positives_valid':int(int(yv.sum())),
            'valid_average_precision':round(ap,6),'threshold':threshold,
            'threshold_grid_validation_only':stats,
            'top_features':sorted(zip(FEATURE_NAMES,model.feature_importance(importance_type='gain').tolist()),
                                  key=lambda x:-x[1])[:12]}
    return models,metrics


def candidate_receipt(e,targets):
    t=targets.get((e.minute,e.leg))
    same=bool(t is not None and t['side']==e.side)
    return {'minute':e.minute,'leg':e.leg,'side':e.side,
        'time_msc':e.time_msc,'decision_msc':e.origin_time_msc,
        'price_cents':e.price_cents,'score':e.score,
        'same_minute_leg':t is not None,'same_side':same,
        'same_second':same and e.origin_time_msc//1000==t['teacher_second'],
        'near_mapped_2s_5c':same and abs(e.time_msc-t['mapped_ms'])<=2000 and
                            abs(e.price_cents-t['price_cents'])<=5,
        'exact_mapped_quote':same and e.time_msc==t['mapped_ms'] and e.price_cents==t['price_cents']}


def replay(ticks,targets,priors,models,start:int,end:int,thresholds:dict):
    # Run distinct independent first/second trained models but one shared
    # market clock, same preexisting own-stop inventory and opposite rearm.
    engine=V16CausalBridge(priors,models[1],models[2],threshold=thresholds[1])
    pos=None;cnt=Counter();first_ms=last_ms=None;seen=set();examples=[]
    for i,q in row_stream(ticks,end):
        if i<start:
            # Warm up history on prior original source quotes, without trading.
            # Call base state update with no fitted model to avoid leaked prior
            # trades affecting measured holdout inventory.
            engine.models={1:None,2:None}
            engine.feature_only=True
            engine.observe(q)
            continue
        if first_ms is None:
            first_ms=q.time_msc
            engine.pending=None;engine.first_done=False;engine.second_done=False
            engine.own_position_side=None;engine.rearm_side=None
            engine.current_minute=None  # force new independent testing cycle
            engine.models=models
            engine.feature_only=False
        last_ms=q.time_msc
        if engine.first_done and engine.rearm_side is not None:
            engine.score_threshold=thresholds[2]
        else:engine.score_threshold=thresholds[1]
        intents=engine.observe(q)
        for e in intents:
            seen.add((e.minute,e.leg))
            z=candidate_receipt(e,targets)
            cnt['entries']+=1;cnt['leg'+str(e.leg)]+=1
            for k in ('same_minute_leg','same_side','same_second','near_mapped_2s_5c','exact_mapped_quote'):
                if z[k]:cnt[k]+=1
            if len(examples)<25:examples.append(z)
            if pos is not None:raise AssertionError('Replaying overlapping independent positions')
            stop=q.bid_cents-30 if e.side==1 else q.ask_cents+30
            pos=OwnPosition(e.side,e.price_cents,e.time_msc,stop,stop)
        if not intents and pos is not None and pos.manage(q):
            engine.notify_closed(q.time_msc,pos.side)
            pos=None
    if first_ms is None:raise ValueError('empty holdout')
    ref={key:t for key,t in targets.items() if first_ms//1000<=t['teacher_second']<=last_ms//1000}
    cnt['reference_all']=len(ref)
    cnt['reference_first']=sum(t['leg']==1 for t in ref.values())
    cnt['reference_second']=sum(t['leg']==2 for t in ref.values())
    cnt['matched_opportunity_keys']=len(seen & ref.keys())
    return {'source_quote_interval_msc':[first_ms,last_ms],
       'counts':dict(cnt),'examples':examples,
       'mapped_2s_5c_recall_all_references':cnt['near_mapped_2s_5c']/max(1,len(ref)),
       'mapped_2s_5c_precision_all_candidates':cnt['near_mapped_2s_5c']/max(1,cnt['entries'])}


def run(args):
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    targets=all_teacher_targets(args.merged)
    prior=clock_priors(targets,train_months=('2026-02','2026-03','2026-04'))
    # Clock prior is trained on NON-January source teacher months to keep
    # validation/test January reference event seconds out of the prior.
    start=time.monotonic()
    data,counts,times=build_examples(args.ticks,targets,prior,args.train_end,args.valid_end,args.max_rows)
    models,fitstat=fit(data,out)
    del data
    stats=replay(args.ticks,targets,prior,models,args.valid_end,args.max_rows,
                 {leg:fitstat[f'leg{leg}']['threshold'] for leg in (1,2)})
    report={'engine':'V16 causal full-R9 entry bridge',
        'merged_sha':sha256(args.merged),'real_tick_part':args.ticks.name,
        'real_tick_part_sha256':sha256(args.ticks),
        'full_teacher_target_legs':len(targets),'full_teacher_first':192487,'full_teacher_second':79865,
        'clock_priors_off_source_months':['2026-02','2026-03','2026-04'],
        'source_rows_train_valid_test':[args.train_end,args.valid_end-args.train_end,args.max_rows-args.valid_end],
        'source_quote_stage_eligibility':{x:dict(v) for x,v in counts.items()},
        'fitted_heads':fitstat,'independent_holdout':stats,
        'elapsed_seconds':round(time.monotonic()-start,2),
        'teacher_events_in_training_labels_only':True,
        'runtime_teacher_events_or_profitable_family_features':False,
        'original_r9_and_mt5_eas_unchanged':True,'native_mql5_or_broker_fills_tested':False}
    (out/'v16_full_entry_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'v16_priors_febapr.json').write_text(json.dumps(prior,indent=2)+'\n')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--merged',type=Path,required=True)
    ap.add_argument('--ticks',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--train-end',type=int,default=500000)
    ap.add_argument('--valid-end',type=int,default=750000)
    ap.add_argument('--max-rows',type=int,default=1200000)
    opts=ap.parse_args()
    if not (0<opts.train_end<opts.valid_end<opts.max_rows<=1800000):
        ap.error('Require 0<train-end<valid-end<max-rows<=1800000 on original part01')
    r=run(opts)
    print(json.dumps({'fit':r['fitted_heads'],'holdout':r['independent_holdout']['counts'],
                      'recall':r['independent_holdout']['mapped_2s_5c_recall_all_references'],
                      'elapsed_seconds':r['elapsed_seconds']},indent=2))
