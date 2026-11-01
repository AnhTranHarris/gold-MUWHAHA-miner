#!/usr/bin/env python3
"""Hard volume acceptance contract: per-source, per-month nonoverlapping trades.

R9 SYNTH reference is immutable, offline-only, and never consulted by entries.
No scaling sampled days or converting candidates to trades is permitted.
"""
from __future__ import annotations
import argparse,collections,csv,json,math
from pathlib import Path
MONTHS=('01','02','06','07')

def teacher_counts(teacher_path):
    c=collections.Counter()
    with open(teacher_path,newline='') as f:
        for r in csv.DictReader(f):
            m=r['native_minute'][5:7]
            if m in MONTHS:c[m]+=int(r['positive'])+int(r['nonpositive'])
    return dict(c)

def volume_contract(directory,teacher_path):
    counts=teacher_counts(teacher_path);out={};pass_all=True
    for source in ('coinexx','dukascopy'):
        for month in MONTHS:
            path=Path(directory)/f'{source}_{month}_full'/'result.json'
            threshold=math.ceil(0.85*counts.get(month,0))
            if not path.exists():
                out[f'{source}_{month}']={'status':'INCOMPLETE','reference_trades':counts.get(month,0),
                                          'minimum_required':threshold,'actual_trades':None}
                pass_all=False;continue
            r=json.loads(path.read_text());n=int(r['trades'])
            eligible=bool(r.get('nonoverlapping') and r['ticks']>0 and r['source']==source)
            passed=eligible and n>=threshold
            out[f'{source}_{month}']={
                'status':'VOLUME_PASS' if passed else 'VOLUME_FAIL',
                'reference_trades':counts.get(month,0), 'minimum_required':threshold,
                'actual_trades':n, 'ratio':round(n/counts.get(month,0),6) if counts.get(month,0)>0 else None,
                'net':r['net'],'profit_factor':r['profit_factor'],
                'research_approval':'NOT_APPROVED' if r['net']<=0 else 'REQUIRES_INDEPENDENT_OOS'
            }
            pass_all &=passed
    return {'monthly_trade_floor_fraction':0.85,'all_sources_months_pass_volume':pass_all,
            'independent_profitability_required':True,'entries_never_read_teacher':True,'months':out}

def main():
    p=argparse.ArgumentParser();p.add_argument('--results',required=True);p.add_argument('--teacher',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();result=volume_contract(a.results,a.teacher);Path(a.out).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
