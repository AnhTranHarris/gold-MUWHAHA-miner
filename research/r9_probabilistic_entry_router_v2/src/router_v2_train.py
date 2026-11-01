#!/usr/bin/env python3
"""Strict chronological walk-forward trainer for R9 Probabilistic Entry Router v2.

No pooled future-month fitting. For each development-check day, the model is fitted
only on decisions whose outcomes fully resolved before that month's NP calibration
window. The current calibration day sets the NP governor; the subsequent dev day is
then replayed without refit. SYNTH teacher contributes at most +10% weight to already
FAVORABLE real outcomes and is never a runtime feature.
"""
from __future__ import annotations
import argparse,collections,datetime as dt,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from router_v2_dataset import DAYS,ROLES,read_paths
from router_v2_model import BayesianCompetingRiskModel


def day_ms(s:str)->int:
    return int(dt.datetime.strptime(s,'%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp()*1000)


def load_all(paths):
    rows=[]
    for p in paths:rows.extend(read_paths(str(p)))
    rows.sort(key=lambda r:(r['utc_ms'],r['source'],r['side']))
    return rows


def training_example(r):
    return {'features':r['features'],'class':r['class'],'net':r['net'],'teacher':r['teacher'],
            'entry_ms':r['utc_ms'],'target_010_ms':r.get('target_010_ms'),'target_030_ms':r.get('target_030_ms'),
            'target_050_ms':r.get('target_050_ms'),'adverse_stop_ms':r.get('adverse_stop_ms')}


def replay_dev(model,rows,dev_date,min_utility=0.0):
    grouped=collections.defaultdict(dict)
    for r in rows:
        if r['date']==dev_date and r['role']=='development_check':grouped[(r['source'],r['utc_ms'])][r['side']]=r
    results=[];last_exit=collections.defaultdict(lambda:-1);counts=collections.Counter()
    for (source,when),sides in sorted(grouped.items(),key=lambda x:(x[0][1],x[0][0])):
        if when<=last_exit[source]:continue
        if 1 not in sides or -1 not in sides:continue
        action,detail=model.route(sides[1]['features'],sides[-1]['features'],min_utility=min_utility)
        counts[action]+=1
        if action=='WAIT':continue
        side=1 if action=='BUY' else -1;r=sides[side]
        last_exit[source]=int(r['exit_utc_ms'])
        results.append({**r,'action':action,'model_detail':detail})
    out={'date':dev_date,'trades':len(results),'net':round(sum(r['net'] for r in results),5),'counts':dict(counts),'by_source':{}}
    for s in ('coinexx','dukascopy'):
        a=[r for r in results if r['source']==s]
        out['by_source'][s]={'n':len(a),'net':round(sum(r['net'] for r in a),5),
                             'mean':round(sum(r['net'] for r in a)/len(a),6) if a else 0.,
                             'win':round(sum(r['net']>0 for r in a)/len(a),5) if a else 0.}
    return out,results


def walkforward(rows,out_dir,teacher_weight=.10,np_alpha=.10,min_utility=0.0):
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True);folds=[];all_selected=[]
    for month in ('01','02','06','07'):
        cal_date=DAYS[month][2];dev_date=DAYS[month][3];cal_start=day_ms(cal_date);dev_start=day_ms(dev_date)
        train=[training_example(r) for r in rows if r['exit_utc_ms'] and int(r['exit_utc_ms'])<cal_start]
        cal_rows=[r for r in rows if r['date']==cal_date and r['role']=='np_calibration' and int(r['exit_utc_ms'])<dev_start]
        # Purge calibration labels whose forward outcome would overlap the development window.
        cal=[training_example(r) for r in cal_rows]
        if not train or not cal:
            folds.append({'month':month,'status':'insufficient_data','train':len(train),'cal':len(cal)});continue
        model=BayesianCompetingRiskModel(np_alpha=np_alpha)
        try:model.fit(train,teacher_weight=teacher_weight)
        except ValueError as e:
            folds.append({'month':month,'status':'fit_failed','error':str(e),'train':len(train),'cal':len(cal)});continue
        ok=model.calibrate_np(cal)
        if not ok:
            folds.append({'month':month,'status':'np_failed','train':len(train),'cal':len(cal),'model':model.export()});continue
        metrics,selected=replay_dev(model,rows,dev_date,min_utility)
        policy_file=out/f'fold_{month}_research_policy.json'
        policy_file.write_text(json.dumps({**model.export(),'status':'RESEARCH_ONLY_NOT_APPROVED','fold_month':month,
                                           'fit_cutoff_utc_ms':cal_start,'calibration_date':cal_date,'development_date':dev_date},indent=2))
        folds.append({'month':month,'status':'ok','train':len(train),'cal':len(cal),'development':metrics,'policy':policy_file.name})
        all_selected.extend(selected)
    summary={'status':'RESEARCH_ONLY_NO_MT5_COMPILE','teacher_weight':teacher_weight,'np_alpha':np_alpha,'min_utility':min_utility,
             'walkforward_rule':'fit only resolved outcomes before current calibration day; calibrate current day; replay later dev day without refit',
             'folds':folds,'total_dev_trades':sum(f.get('development',{}).get('trades',0) for f in folds),
             'total_dev_net':round(sum(f.get('development',{}).get('net',0) for f in folds),5),
             'no_unselected_months_touched':True,'runtime_teacher_feature':False}
    (out/'walkforward_summary.json').write_text(json.dumps(summary,indent=2))
    # compact selected ledger, details omitted to avoid model object serialization.
    ledger=[]
    for r in all_selected:
        ledger.append({k:r[k] for k in ('source','month','date','utc_ms','side','spread','entry','exit_utc_ms','exit_type','net','class','teacher','action')})
    (out/'walkforward_selected_trades.json').write_text(json.dumps(ledger,indent=2))
    return summary


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',required=True);ap.add_argument('--out',required=True);ap.add_argument('--teacher-weight',type=float,default=.10)
    ap.add_argument('--np-alpha',type=float,default=.10);ap.add_argument('--min-utility',type=float,default=0.)
    a=ap.parse_args();paths=sorted(Path(a.data_dir).glob('*_router_v2_paths.csv.gz'))
    rows=load_all(paths);print(json.dumps(walkforward(rows,a.out,a.teacher_weight,a.np_alpha,a.min_utility),indent=2))
if __name__=='__main__':main()
