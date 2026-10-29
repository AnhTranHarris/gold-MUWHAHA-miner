#!/usr/bin/env python3
"""F401-R133: F392 high-volume hunter + F394 delayed-path asymmetric budget router.
UNAPPROVED / PRIVILEGED HISTORICAL STRUCTURAL BENCHMARK.
CORRECT is protected by a hard false-veto budget; wrong+neutral are rejection classes.
"""
from __future__ import annotations
import io,json,math,zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip'
OUT=ROOT/'R133_ASYMMETRIC_BUDGET_ROUTER_RESULTS.json'
BROKERS=('coinexx','dukascopy');MONTHS=('01','02','06','07');EARLY={'01','02'};LATER={'06','07'}
CAP=.008278;THRESHOLDS=(.90,.91,.92,.93,.94,.95,.96,.97,1.10)

def session4h(t):
    return ((((t//1000)%86400)//3600)//4).astype(np.int8)

def load():
    data={}
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        for br in BROKERS:
            for m in MONTHS:
                d=np.load(io.BytesIO(z.read(f'F395_S14_{br}_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz')))
                s=np.load(io.BytesIO(z.read(f'F394_S13_OOF_PATH_HAZARD_{br}_{m}.npy')))
                assert len(s)==len(d['truth'])
                assert np.array_equal(d['original_index'],np.arange(len(s),dtype=np.int32))
                data[(br,m)]={k:d[k].copy() for k in ('t','side','truth','predecessor_f392_veto')}
                data[(br,m)]['score']=s.astype(np.float32,copy=True)
    return data

def base_counts(data,months):
    bad=good=opp=neu=ct=0
    for (_,m),a in data.items():
        if m not in months:continue
        y=a['truth'];v=a['predecessor_f392_veto']
        bad+=int(np.sum(v&(y!=0)));good+=int(np.sum(v&(y==0)))
        opp+=int(np.sum(v&(y==1)));neu+=int(np.sum(v&(y==2)));ct+=int(np.sum(y==0))
    return dict(bad=bad,good=good,opposite=opp,neutral=neu,correct_total=ct)

def options(data):
    groups=[(br,side,sess) for br in BROKERS for side in (-1,1) for sess in range(6)]; out={}
    for g in groups:
        br,side,sess=g; yy=[];ss=[]
        for (b,m),a in data.items():
            if b!=br or m not in EARLY:continue
            q=session4h(a['t']);ix=(a['side']==side)&(q==sess)&(~a['predecessor_f392_veto'])
            yy.append(a['truth'][ix]);ss.append(a['score'][ix])
        y=np.concatenate(yy);score=np.concatenate(ss)
        out[g]=[dict(threshold=float(th),add_bad=int(np.sum((score>=th)&(y!=0))),add_good=int(np.sum((score>=th)&(y==0)))) for th in THRESHOLDS]
    return groups,out

def optimize(data):
    base=base_counts(data,EARLY);allowed=int(math.floor(CAP*base['correct_total']));supp=max(0,allowed-base['good'])
    groups,opts=options(data);dp={0:(0,[])}
    for g in groups:
        nd={}
        for cost,(value,choices) in dp.items():
            for o in opts[g]:
                nc=cost+o['add_good']
                if nc>supp:continue
                nv=value+o['add_bad']
                if nc not in nd or nv>nd[nc][0]:nd[nc]=(nv,choices+[(g,o)])
        dp=nd
    cost,(value,choices)=max(dp.items(),key=lambda kv:kv[1][0])
    th={f'{br}|{side}|{sess}':o['threshold'] for (br,side,sess),o in choices}
    return dict(early_correct_budget=allowed,base_early_correct_loss=base['good'],supplement_correct_budget=supp,selected_supplement_good=cost,selected_supplement_bad=value,thresholds=th)

def evaluate(data,thresholds,months):
    cells=[];keys=('opposite_veto','neutral_veto','correct_lost','opposite_total','neutral_total','correct_total','base_bad','base_good');tot={k:0 for k in keys}
    for (br,m),a in data.items():
        if m not in months:continue
        y=a['truth'];q=session4h(a['t']);v=a['predecessor_f392_veto'].copy()
        for side in (-1,1):
            for sess in range(6):
                th=thresholds[f'{br}|{side}|{sess}'];ix=(a['side']==side)&(q==sess)&(~a['predecessor_f392_veto']);v[ix]=a['score'][ix]>=th
        rec=dict(broker=br,month=m,n=int(len(y)),opposite_veto=int(np.sum(v&(y==1))),neutral_veto=int(np.sum(v&(y==2))),correct_lost=int(np.sum(v&(y==0))),opposite_total=int(np.sum(y==1)),neutral_total=int(np.sum(y==2)),correct_total=int(np.sum(y==0)),base_bad=int(np.sum(a['predecessor_f392_veto']&(y!=0))),base_good=int(np.sum(a['predecessor_f392_veto']&(y==0))))
        rec['bad_veto']=rec['opposite_veto']+rec['neutral_veto'];rec['incremental_bad']=rec['bad_veto']-rec['base_bad'];rec['incremental_good']=rec['correct_lost']-rec['base_good'];rec['incremental_bad_good_ratio']=rec['incremental_bad']/max(1,rec['incremental_good']);cells.append(rec)
        for k in keys:tot[k]+=rec[k]
    tot['bad_veto']=tot['opposite_veto']+tot['neutral_veto'];tot['bad_recall']=tot['bad_veto']/max(1,tot['opposite_total']+tot['neutral_total']);tot['correct_loss_rate']=tot['correct_lost']/max(1,tot['correct_total']);tot['incremental_bad']=tot['bad_veto']-tot['base_bad'];tot['incremental_good']=tot['correct_lost']-tot['base_good'];tot['incremental_bad_good_ratio']=tot['incremental_bad']/max(1,tot['incremental_good'])
    return dict(total=tot,cells=cells)

def main():
    data=load();opt=optimize(data);early=evaluate(data,opt['thresholds'],EARLY);later=evaluate(data,opt['thresholds'],LATER);allx=evaluate(data,opt['thresholds'],set(MONTHS))
    assert base_counts(data,set(MONTHS))['bad']==399049 and base_counts(data,set(MONTHS))['good']==9404
    assert (allx['total']['bad_veto'],allx['total']['correct_lost'])==(406447,9931)
    assert (later['total']['bad_veto'],later['total']['correct_lost'])==(211966,4468)
    result={'research_id':'F401-R133','status':'UNAPPROVED_PRIVILEGED_HISTORICAL_STRUCTURAL_BENCHMARK','objective':'incorrect+neutral targeted; CORRECT hard-protected','critical_privilege_warning':'F392 publisher provenance absent; archived F394 LOMO may train on calendar-future months; not prospective live evidence','correct_loss_rate_cap':CAP,'optimizer':opt,'early_jan_feb':early,'later_jun_jul_frozen_router':later,'pooled_historical_all_four_months':allx}
    OUT.write_text(json.dumps(result,indent=2));print(json.dumps(result['pooled_historical_all_four_months']['total'],indent=2))
if __name__=='__main__':main()
