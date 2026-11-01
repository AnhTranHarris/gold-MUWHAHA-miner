#!/usr/bin/env python3
"""Independent streamed validation; no profit or trade-volume interpolation."""
from __future__ import annotations
import argparse,csv,gzip,json,math
from pathlib import Path

def validate(csv_gz,summary,fee=.02):
    s=json.loads(Path(summary).read_text())
    n=0;net=0.;wins=0;loss=0.;gain=0.;last_exit=None;bad=[]
    with gzip.open(csv_gz,'rt',newline='') as f:
        for r in csv.DictReader(f):
            n+=1;start=int(r['entry_ms']);end=int(r['exit_ms']);side=int(r['side'])
            x=float(r['entry_price']);y=float(r['exit_price']);v=float(r['net'])
            if last_exit is not None and start<last_exit:bad.append(f'overlap at {n}')
            last_exit=end
            if start>end:bad.append(f'negative lifecycle at {n}')
            if side not in (-1,1):bad.append(f'bad side at {n}')
            if abs((y-x)*side-fee-v)>.000011:bad.append(f'net mismatch at {n}')
            net+=v;wins+=v>0;gain+=max(0.,v);loss+=-min(0.,v)
    if n != s['trades']:bad.append(f"trade count differs: {n} vs {s['trades']}")
    if abs(net-s['net'])>.02:bad.append(f"net differs {net} vs {s['net']}")
    return {'source':s['source'],'input':s['input'],'trades_verified':n,'net_verified':round(net,2),
            'positive_fraction':round(wins/n,6) if n else 0.0,
            'profit_factor':round(gain/loss,4) if loss else None,
            'integrity_errors':bad[:25], 'integrity_error_count':len(bad),
            'integrity_pass':not bad,'profitability_pass':net>0}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--trades',required=True);a.add_argument('--summary',required=True);a.add_argument('--out',required=True)
    p=a.parse_args();v=validate(p.trades,p.summary);Path(p.out).write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
