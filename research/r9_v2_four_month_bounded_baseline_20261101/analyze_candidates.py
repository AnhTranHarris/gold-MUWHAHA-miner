#!/usr/bin/env python3
"""Produce descriptive only, not-executable counterfactual diagnostics from frozen labels."""
import csv,gzip,json,collections,glob,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
out=[]
for p in sorted((ROOT/'bounded_collections').glob('*_router_v2_paths.csv.gz')):
    name=p.name.split('_');source,month=name[0],name[1]
    stats=collections.defaultdict(lambda:{'n':0,'win':0,'net':0.,'spread':0.,'teacher':0,'exit':collections.Counter(),'favorable':0,'adverse':0})
    with gzip.open(p,'rt') as f:
        for row in csv.DictReader(f):
            s=stats[row['role']];net=float(row['net'])
            s['n']+=1;s['win']+=(net>0);s['net']+=net;s['spread']+=float(row['spread']);s['teacher']+=int(row['teacher']);s['exit'][row['exit_type']]+=1
            s['favorable']+=(row['class']=='FAVORABLE');s['adverse']+=(row['class']=='ADVERSE')
    for k,v in stats.items():
        n=v['n']
        out.append({'source':source,'month':month,'role':k,'hypothetical_paths':n,'win_fraction':v['win']/n if n else None,
                    'average_net':v['net']/n if n else None,'mean_spread':v['spread']/n if n else None,
                    'teacher_fraction':v['teacher']/n if n else None,'favorable_class_fraction':v['favorable']/n if n else None,
                    'adverse_class_fraction':v['adverse']/n if n else None,'exit_types':dict(v['exit'])})
(ROOT/'results'/'candidate_diagnostics.json').write_text(json.dumps(out,indent=2))
for s in out:
    if s['role']=='development_check':print(s)
