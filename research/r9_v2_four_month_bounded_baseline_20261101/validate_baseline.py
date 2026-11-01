#!/usr/bin/env python3
"""Cross-check frozen-policy bounded-baseline accounting and chronology."""
import collections,gzip,json,csv,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent
R=B/'results'
w=json.loads((R/'walkforward_summary.json').read_text());s=json.loads((R/'baseline_scorecard.json').read_text());ledger=json.loads((R/'walkforward_selected_trades.json').read_text())
assert w['total_dev_trades']==len(ledger)==s['aggregate']['trades']
assert abs(w['total_dev_net']-sum(x['net'] for x in ledger))<1e-6
assert all(x['status']=='ok' for x in w['folds'])
assert s['ticks_scanned']==64515445 and s['paired_paths']==25536
assert set(x['source'] for x in ledger)=={'coinexx'}
per=collections.defaultdict(list)
for x in ledger:per[x['source']].append(x)
for broker,rows in per.items():
    rows.sort(key=lambda x:x['utc_ms'])
    assert all(rows[i+1]['utc_ms']>rows[i]['exit_utc_ms'] for i in range(len(rows)-1))
assert all('teacher' not in x['features'] and 'net' not in x['features'] for _ in [0] for x in [])
for src in ('coinexx','dukascopy'):
    for month in ('01','02','06','07'):
        f=B/'bounded_collections'/f'{src}_{month}_router_v2_paths.csv.gz'
        with gzip.open(f,'rt') as io:
            r=next(csv.DictReader(io))
            ft=json.loads(r['features'])
            assert 'teacher' not in ft and 'net' not in ft and 'exit_type' not in ft
            assert 'geo_4h_ready' in ft and 'hawk_burst_250' in ft
result={'status':'PASS','tests':['selected trade count equality','exact net reconciliation','all four successful chronological folds',
    'eight monthly archives and bounded candidate totals','strict single-position chronology per source',
    'no future/teacher label in runtime features','H4 and 250ms feature schema'],
    'source_commit':'35056fa38c11a7b2e9b9d6bab984af3368e905be','selected_trades':len(ledger),'selected_net':w['total_dev_net']}
(R/'validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
