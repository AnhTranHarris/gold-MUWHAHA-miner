#!/usr/bin/env python3
"""No-trade causal feature probe for Router v2 on raw tick sources."""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from router_v2_dataset import iter_ticks,decision_neutral_gate
from router_v2_features import RouterV2FeatureEngine,MARKET_STATES

def run(path,source,limit=500000,scan_ms=500):
    e=RouterV2FeatureEngine();last_slot=None;c=collections.Counter();sp=[];samples=[]
    for i,q in enumerate(iter_ticks(path,source)):
        if i>=limit:break
        e.add(q);c['ticks']+=1
        slot=q.utc_ms//scan_ms
        if slot==last_slot:continue
        last_slot=slot;c['scans']+=1
        f=e.snapshot(q)
        if f is None:c['not_ready']+=1;continue
        c['ready']+=1
        dom=max(MARKET_STATES,key=lambda s:f.get('state_'+s,0.))
        c['state_'+dom]+=1
        if decision_neutral_gate(f,q):
            c['candidate_points']+=1;sp.append(q.spread)
            if len(samples)<10:
                samples.append({'utc_ms':q.utc_ms,'spread':q.spread,'dominant_state':dom,
                                'buy':e.oriented(f,1),'sell':e.oriented(f,-1)})
    return {'source':source,'limit':limit,'scan_ms':scan_ms,'counts':dict(c),'gap_resets':e.gap_resets,
            'candidate_spread_mean':sum(sp)/len(sp) if sp else None,'sample_decisions':samples,
            'status':'FEATURE_PROBE_ONLY_NO_FUTURE_LABELS_NO_TRADES'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ticks',required=True);ap.add_argument('--source',required=True);ap.add_argument('--out',required=True);ap.add_argument('--limit',type=int,default=500000)
    a=ap.parse_args();r=run(a.ticks,a.source,a.limit);Path(a.out).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='sample_decisions'},indent=2))
if __name__=='__main__':main()
