#!/usr/bin/env python3
"""R9 v1 BNP-Hawkes four-development-month real-tick trainer.

Research only. Reuses pinned chronological tick inputs and v1 causal feature model.
Forward labels simulate original R9 entry/SL/trail/30s timeout using *future ticks
only after the decision*; no future information enters candidate features.
Teacher: profitable SYNTH R9 trade in same native-minute/side is an offline,
weak auxiliary weight, never a live input/real profitability label.
All four months are development data; other months remain untouched.
"""
from __future__ import annotations
import argparse,collections,csv,datetime as dt,gzip,hashlib,json,math,sys,random,time
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator
sys.path.insert(0,str(Path(__file__).resolve().parent))
from entry_model import Quote,CausalEntryFeatures,BNPModel,FEATURES,VERSION

DAYS={
 '01': ('2026-01-06','2026-01-12','2026-01-20','2026-01-27'),
 '02': ('2026-02-03','2026-02-10','2026-02-19','2026-02-26'),
 '06': ('2026-06-02','2026-06-09','2026-06-18','2026-06-25'),
 '07': ('2026-07-02','2026-07-09','2026-07-16','2026-07-28'),
}
ROLES=('fit','fit','np_calibration','development_check')
COMPLETE_HOLD_MS=30_000
SOURCE_MAX_SPREAD=1.50  # candidate-generation ceiling, NOT selected execution threshold
SCAN_MS=10_000
ENTRY_FEE=0.02  # modeled round-trip 0.01-lot commissions; sensitivity required

@dataclass
class Hypo:
    quote:Quote
    side:int
    data:dict
    sl:float
    entry_px:float
    entry_ms:int
    entry_seq:int
    spread:float
    teacher:int
    date:str
    max_favourable:float=0.0
    max_adverse:float=0.0

    def update(self,q:Quote):
        # Process the first strictly LATER event, even when timestamp_ms matches.
        px=q.bid if self.side>0 else q.ask
        excursion=(px-self.entry_px)*self.side
        self.max_favourable=max(self.max_favourable,excursion)
        self.max_adverse=min(self.max_adverse,excursion)
        if (self.side>0 and q.bid<=self.sl) or (self.side<0 and q.ask>=self.sl):
            return self.result(q.time_ms,excursion,'SL')
        if q.time_ms-self.entry_ms>=COMPLETE_HOLD_MS:
            return self.result(q.time_ms,excursion,'TIMEOUT')
        # R9 management: activate on executable side, tighten stop monotonically.
        if excursion >= 0.10-1e-10:
            newstop=round(math.floor((px-self.side*0.03)/0.01+0.5)*0.01,2)
            if self.side>0:self.sl=max(self.sl,newstop)
            else:self.sl=min(self.sl,newstop)
        return None

    def result(self,exit_ms: int,excursion:float,reason:str):
        d=self.data
        return {'source':d['source'],'month':d['month'],'date':self.date,'role':d['role'],
                'utc_ms':self.quote.time_ms,'native_ms':self.quote.native_ms,
                'side':self.side,'spread':round(self.spread,5),
                'entry':round(self.entry_px,5),'exit_utc_ms':exit_ms,
                'hold_ms':exit_ms-self.entry_ms,'exit_type':reason,'net':round(excursion-ENTRY_FEE,5),
                'mfe':round(self.max_favourable,5),'mae':round(self.max_adverse,5),
                'survived':int(excursion-ENTRY_FEE>0.10),'win':int(excursion-ENTRY_FEE>0),
                'teacher':self.teacher,'bins':list(d['bins']),
                'features':[round(float(x),6) for x in d['features'].values()]}

def read_teacher(path:str):
    d={}
    with open(path,newline='') as f:
        for r in csv.DictReader(f):d[(r['native_minute'],int(r['side']))]=int(r['positive'])
    return d

def source_file(data_root,source,month):
    if source=='coinexx':return Path(data_root)/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
    return Path(data_root)/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'

def stream_month(path,source,month,teacher,out_root,paired=False):
    # Four deterministic nonadjacent source-native days per month; 2 fit, 1 cal, 1 dev-check.
    day_windows={}
    for i,s in enumerate(DAYS[month]):
        start=int(dt.datetime.strptime(s,'%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp()*1000)
        day_windows[int(start//86_400_000)]=(s,ROLES[i])
    counters=collections.Counter();eng=None;last_slot=None;active=[];day=None;seq=0
    records=[];out=Path(out_root);out.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,'rt',newline='') as f:
        for r in csv.DictReader(f):
            counters['rows_scanned']+=1
            native=int(r['time_msc']) if source=='coinexx' else int(r['timestamp_ms_utc'])
            ordinal=native//86_400_000
            data=day_windows.get(ordinal)
            if data is None:continue
            if data != day:
                # Day boundary is reset; previous outcomes without next tick are censored.
                counters['censored']+=len(active);active=[];eng=CausalEntryFeatures();last_slot=None;day=data
            if source=='coinexx':
                utc=native-(120 if month in ('01','02') else 180)*60000
                bid=float(r['bid']);ask=float(r['ask'])
            else:
                utc=native;bid=int(r['bid_raw'])/1000;ask=int(r['ask_raw'])/1000
            if not (0<bid<=ask):counters['bad_quote']+=1;continue
            q=Quote(utc,bid,ask,native)
            counters['selected_ticks']+=1;seq+=1
            # Exits can happen only after decision: process existing hypos FIRST.
            if active:
                remaining=[]
                for a in active:
                    rec=a.update(q)
                    if rec is None:remaining.append(a)
                    else:records.append(rec);counters['labeled']+=1
                active=remaining
            eng.add(q)
            slot=q.time_ms//SCAN_MS
            if slot==last_slot:continue
            last_slot=slot;counters['scans']+=1
            cand=eng.candidate(q,max_spread=SOURCE_MAX_SPREAD)
            if cand is None:continue
            counters['candidates']+=1
            sp=q.ask-q.bid
            # Teacher is an offline label, never a feature at inference time.
            teacher_ms=native if source=='coinexx' else utc+(120 if month in ('01','02') else 180)*60_000
            naive_time=dt.datetime.fromtimestamp(teacher_ms/1000,dt.timezone.utc).strftime('%Y.%m.%d %H:%M')
            for side in ((cand['side'],-cand['side']) if paired else (cand['side'],)):
                if side==cand['side']:
                    oriented=cand
                else:
                    # Candidate features are signed relative to side, except invariant
                    # efficiency, burst, ATR acceleration and spread features.
                    values=list(cand['features'].values())
                    for j in (0,2,5,6,7,8,9):values[j]=-values[j]
                    signed=dict(zip(cand['features'],values))
                    from entry_model import bins5
                    oriented={**cand,'side':side,'features':signed,'bins':bins5(values)}
                tmark=int(teacher.get((naive_time,side),0)>0)
                counters['teacher_matches']+=tmark
                price=ask if side>0 else bid
                sl=round(math.floor((bid-0.30 if side>0 else ask+0.30)/.01+.5)*.01,2)
                d={'source':source,'month':month,'role':data[1],**oriented}
                active.append(Hypo(q,side,d,sl,price,q.time_ms,seq,sp,tmark,data[0]))
    counters['censored']+=len(active)
    outpath=out/f'{source}_{month}_candidate_outcomes.csv.gz'
    columns=['source','month','date','role','utc_ms','native_ms','side','spread','entry','exit_utc_ms','hold_ms','exit_type','net','mfe','mae','survived','win','teacher','bins','features']
    with gzip.open(outpath,'wt',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=columns);wr.writeheader()
        for rec in records:
            row={**rec,'bins':json.dumps(rec['bins'],separators=(',',':')),'features':json.dumps(rec['features'],separators=(',',':'))}
            wr.writerow(row)
    return {'file':outpath.name,'data_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'source':source,'month':month,'days':DAYS[month],'rows':dict(counters),'records':len(records)}

def read_outcomes(path):
    with gzip.open(path,'rt',newline='') as f:
        for r in csv.DictReader(f):
            r['bins']=tuple(json.loads(r['bins']))
            for k in ('spread','net','entry','mfe','mae'):r[k]=float(r[k])
            for k in ('utc_ms','exit_utc_ms','hold_ms','side','survived','win','teacher'):r[k]=int(r[k])
            yield r

def fit_variant(records,teacher_weight,train_sources=('coinexx','dukascopy')):
    # Teacher can only upweight already profitable REAL outcomes, and only 0..20%.
    train=[];teacher_boost=0
    for r in records:
        if r['role']!='fit' or r['source'] not in train_sources:continue
        y=r['survived'];train.append((r['bins'],y))
        if teacher_weight and y==1 and r['teacher']:
            # Deterministic 1 / 5 fractional observation, no random hash seeds.
            if int(r['utc_ms']//SCAN_MS)%5<teacher_weight:
                train.append((r['bins'],y));teacher_boost+=1
    model=BNPModel(alpha=.15,delta=.05,min_neg=200)
    model.fit(train)
    return model,{'train':len(train),'teacher_boost':teacher_boost,'positives':model.count[1],'negatives':model.count[0]}

def evaluate_policy(records,model,spread_limit,alpha,blocked=False):
    byday=collections.defaultdict(list)
    for r in records:
        if r['role']=='development_check' and r['spread']<=spread_limit+1e-9:
            byday[(r['source'],r['date'])].append(r)
    all_trades=[];counts=collections.Counter()
    for (source,date),rows in sorted(byday.items()):
        # Chronological account policy: NEVER overlap simulated positions.
        rows.sort(key=lambda r:r['utc_ms']);last_exit=-1
        for r in rows:
            if r['utc_ms']<=last_exit:continue
            score=model.score(r['bins'])
            if score<=model.threshold:continue
            last_exit=r['exit_utc_ms']
            all_trades.append(r);counts[f'{source}_trades']+=1
    result={'trades':len(all_trades),'net':round(sum(x['net'] for x in all_trades),2),
            'win_rate':round(sum(x['win'] for x in all_trades)/max(1,len(all_trades)),5),
            'survival_rate':round(sum(x['survived'] for x in all_trades)/max(1,len(all_trades)),5),
            'by_source':{},'by_month':{},'counts':dict(counts)}
    for field in ['source','month']:
        for key in sorted({x[field] for x in all_trades}):
            selected=[x for x in all_trades if x[field]==key]
            result['by_'+field][key]={'trades':len(selected),'net':round(sum(x['net'] for x in selected),2),
              'win_rate':round(sum(x['win'] for x in selected)/len(selected),4)}
    return result

def tune(paths,out,alpha_grid=(.05,.10,.15,.20,.30),spread_grid=(.25,.40,.60,.80,1.00,1.25,1.50)):
    out=Path(out);records=[]
    for file in paths: records.extend(read_outcomes(file))
    base_stats={'examples':len(records),'by_role':dict(collections.Counter(r['role'] for r in records)),
                'by_source':dict(collections.Counter(r['source'] for r in records)),
                'by_month':dict(collections.Counter(r['month'] for r in records)),
                'positive_label_rate':sum(r['survived'] for r in records)/max(1,len(records)),
                'teacher_marker_rate':sum(r['teacher'] for r in records)/max(1,len(records))}
    trials=[]
    # Calibration scores are independent blocked date windows; never evaluate them as OOS.
    for weight in (0,1):
      model,fitmeta=fit_variant(records,weight)
      for alpha in alpha_grid:
        for sp in spread_grid:
            cal=[model.score(r['bins']) for r in records if r['role']=='np_calibration' and r['survived']==0 and r['spread']<=sp]
            model.alpha=alpha;model.ready=False;model.threshold=None
            if not model.calibrate(cal):
                trials.append({'teacher_weight':weight,'alpha':alpha,'spread':sp,'feasible':False,'cal_negative':len(cal)});continue
            metrics=evaluate_policy(records,model,sp,alpha)
            trials.append({'teacher_weight':weight,'alpha':alpha,'spread':sp,'feasible':True,
                           'cal_negative':len(cal),'threshold':model.threshold,**metrics})
    # Diagnostic ranking: require at least 20 per broker and a positive net per broker,
    # and prefer max minimum-source mean trade payoff; if no acceptable policy, mark none.
    passing=[]
    for t in trials:
      if not t.get('feasible'):continue
      both=t['by_source']
      if all(both.get(s,{}).get('trades',0)>=20 and both[s]['net']>0 for s in ('coinexx','dukascopy')):
        floor=min(both[s]['net']/both[s]['trades'] for s in ('coinexx','dukascopy'))
        passing.append((floor,t))
    passing.sort(key=lambda x:x[0],reverse=True)
    chosen=passing[0][1] if passing else None
    # Save all development trials including negative outcomes; no silent promotion.
    (out/'development_trials.json').write_text(json.dumps(trials,indent=2))
    summary={'status':'DEVELOPMENT_ONLY_NEVER_LIVE','base':base_stats,
         'fit':'teacher-weak-only-on-positive-real-outcomes, 20%-max deterministic oversampling',
         'n_trials':len(trials),'n_valid':sum(x.get('feasible',False) for x in trials),
         'n_passing':len(passing),'chosen':chosen,
         'NO_UNTOUCHED_MONTHS_EVALUATED':True,
         'label':'future path R9 SL/trailing/30-second real-tick price result; fees $0.02 RT; no slippage/margin or broker stop constraint',
         'note':'NP sample-level alpha is NOT live false-positive guarantee on dependent timeseries.'}
    (out/'development_summary.json').write_text(json.dumps(summary,indent=2))
    # Never export promoted policy. A development policy is a research checkpoint only.
    if chosen:
        model,fitmeta=fit_variant(records,chosen['teacher_weight']);model.alpha=chosen['alpha']
        cal=[model.score(r['bins']) for r in records if r['role']=='np_calibration' and r['survived']==0 and r['spread']<=chosen['spread']]
        model.calibrate(cal)
        (out/'development_policy_not_approved.json').write_text(json.dumps({**model.export(),'spread_cap':chosen['spread'],'training_meta':fitmeta,'status':'UNAPPROVED_RESEARCH_ONLY'},indent=2))
    return summary

def cli():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-root',default='/mnt/data');ap.add_argument('--teacher',required=True);ap.add_argument('--results',required=True)
    ap.add_argument('--source',choices=('coinexx','dukascopy','both'),default='both')
    ap.add_argument('--month',choices=tuple(DAYS)+('all',),default='all')
    ap.add_argument('--tune-only',action='store_true')
    ap.add_argument('--paired',action='store_true',help='Research both BUY/SELL causal actions at each candidate tick')
    args=ap.parse_args();out=Path(args.results);out.mkdir(parents=True,exist_ok=True)
    if not args.tune_only:
        teacher=read_teacher(args.teacher)
        for month in (list(DAYS) if args.month=='all' else [args.month]):
            for source in (('coinexx','dukascopy') if args.source=='both' else (args.source,)):
                path=source_file(args.data_root,source,month)
                t0=time.monotonic();report=stream_month(path,source,month,teacher,out,paired=args.paired)
                report['seconds_elapsed']=round(time.monotonic()-t0,2)
                (out/f'{source}_{month}_collection.json').write_text(json.dumps(report,indent=2))
                print(json.dumps(report),flush=True)
    if args.tune_only:
        paths=sorted(out.glob('*_candidate_outcomes.csv.gz'))
        if len(paths)<2:raise RuntimeError('insufficient source files for tuning')
        print(json.dumps(tune(paths,out),indent=2),flush=True)
if __name__=='__main__':cli()
