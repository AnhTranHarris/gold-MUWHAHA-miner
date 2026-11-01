#!/usr/bin/env python3
"""Bounded real-tick end-to-end smoke test for Router v2.

This is a BUILD VALIDATION only: small January prefixes, no SYNTH teacher, no tuning,
no performance claims. It proves real ticks -> causal features -> future-path labels ->
Bayesian fit -> NP calibration -> BUY/SELL/WAIT routing executes without leakage.
"""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from router_v2_dataset import iter_ticks,decision_neutral_gate
from router_v2_features import RouterV2FeatureEngine
from router_v2_labels import ActivePath,outcome_class
from router_v2_model import BayesianCompetingRiskModel


def collect(path,source,limit=25000,scan_ms=2000):
    e=RouterV2FeatureEngine();active=[];records=[];slot=None;c=collections.Counter()
    for i,q in enumerate(iter_ticks(path,source)):
        if i>=limit:break
        c['ticks']+=1
        if active:
            rem=[]
            for p in active:
                o=p['path'].update(q)
                if o is None:rem.append(p);continue
                records.append({'source':source,'utc_ms':o.entry_ms,'exit_utc_ms':o.exit_ms,'side':o.side,
                                'features':p['features'],'class':outcome_class(o),'net':o.net,'teacher':0})
                c['labeled']+=1
            active=rem
        e.add(q)
        s=q.utc_ms//scan_ms
        if s==slot:continue
        slot=s;c['scans']+=1
        f=e.snapshot(q)
        if f is None or not decision_neutral_gate(f,q):continue
        c['decision_points']+=1
        for side in (1,-1):active.append({'features':e.oriented(f,side),'path':ActivePath(q,side,0)});c['actions']+=1
    c['censored']=len(active)
    return records,dict(c)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--coinexx',required=True);ap.add_argument('--dukascopy',required=True);ap.add_argument('--out',required=True);ap.add_argument('--limit',type=int,default=25000)
    a=ap.parse_args();allr=[];counts={}
    for source,path in [('coinexx',a.coinexx),('dukascopy',a.dukascopy)]:
        r,c=collect(path,source,a.limit);allr.extend(r);counts[source]=c
    allr.sort(key=lambda x:(x['utc_ms'],x['source'],x['side']))
    n=len(allr);i1=int(.60*n);i2=int(.80*n);fit=allr[:i1];cal=allr[i1:i2];dev=allr[i2:]
    status='OK';err=None;summary={}
    try:
        m=BayesianCompetingRiskModel(min_context=20).fit(fit,teacher_weight=0.0)
        ok=m.calibrate_np(cal)
        if not ok:raise RuntimeError('NP calibration failed')
        groups=collections.defaultdict(dict)
        for r in dev:groups[(r['source'],r['utc_ms'])][r['side']]=r
        last=collections.defaultdict(lambda:-1);selected=[];decisions=collections.Counter()
        for (source,when),sides in sorted(groups.items(),key=lambda z:(z[0][1],z[0][0])):
            if when<=last[source] or 1 not in sides or -1 not in sides:continue
            action,detail=m.route(sides[1]['features'],sides[-1]['features'],min_utility=0.0);decisions[action]+=1
            if action=='WAIT':continue
            side=1 if action=='BUY' else -1;r=sides[side];last[source]=r['exit_utc_ms'];selected.append(r)
        summary={'fit':len(fit),'cal':len(cal),'dev':len(dev),'decisions':dict(decisions),'selected':len(selected),
                 'selected_net':round(sum(r['net'] for r in selected),5),'by_source':{},'model':m.export()}
        for s in ('coinexx','dukascopy'):
            rr=[r for r in selected if r['source']==s];summary['by_source'][s]={'n':len(rr),'net':round(sum(x['net'] for x in rr),5)}
    except Exception as e:
        status='FAILED';err=repr(e)
    out={'status':status,'error':err,'scope':'BUILD_SMOKE_ONLY_NO_TEACHER_NO_TUNING_NO_PERFORMANCE_CLAIM','counts':counts,'records':n,'summary':summary}
    Path(a.out).write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='summary'},indent=2));print(json.dumps(summary,indent=2)[:5000])
if __name__=='__main__':main()
