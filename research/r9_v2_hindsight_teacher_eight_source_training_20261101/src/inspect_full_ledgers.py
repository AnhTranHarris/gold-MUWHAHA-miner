#!/usr/bin/env python3
"""Read COMPLETE source trade ledgers, report counts and strict 30-second outcome classes."""
import zipfile,gzip,csv,json,collections,math,datetime as dt,hashlib
from pathlib import Path
BASE=Path('/mnt/data')
REF={'01':27980,'02':33523,'06':31801,'07':24382}
MONTHS=('01','02','06','07')
def sourcefile(source,month):return BASE/f'R9_V2_FULLMONTH_{source.upper()}_2026_{month}_EXACT.zip'
def rows(source,month):
    with zipfile.ZipFile(sourcefile(source,month)) as z:
        with gzip.open(z.open('full_run/trades.csv.gz'),'rt') as g:
            yield from csv.DictReader(g)
def run():
 out={}
 for source in ('coinexx','dukascopy'):
  for month in MONTHS:
   k=f'{source}_{month}'; total=0; positive=0; positive10=0; neutral=0; adverse=0; late=0; maxms=0; total_net=0.;bysession=collections.Counter(); byday=collections.defaultdict(lambda:[0,0,0.])
   for r in rows(source,month):
    total+=1;net=float(r['net']);dur=int(r['exit_ms'])-int(r['entry_ms']);maxms=max(maxms,dur); late+=dur>30000
    win=net>0;neutral_condition=abs(net)<=.02+1e-10
    positive+=win;positive10+=net>=.10;neutral+=neutral_condition;adverse+=net<0 and not neutral_condition;total_net+=net
    d=dt.datetime.fromtimestamp(int(r['entry_ms'])/1000,dt.timezone.utc).strftime('%Y-%m-%d');val=byday[d];val[0]+=1;val[1]+=win;val[2]+=net
   target=math.ceil(.85*REF[month]); out[k]={'trades':total,'net':round(total_net,2),'win_count':positive,'win_rate':positive/total,'target_10c_count':positive10,'neutral_count':neutral,'adverse_count':adverse,'max_duration_ms':maxms,'over30s':late,'volume_floor':target,'positive_oracle_surplus':positive-target,'calendar_days':len(byday),'daily':dict(byday)}
   print(k, 'total',total,'winners',positive,'win%',round(100*positive/total,2),'volume floor',target,'max dur',maxms,flush=True)
 (BASE/'r9_v2_eight_source_training_20261101/results/full_ledger_truth.json').write_text(json.dumps(out,indent=2))
 return out
if __name__=='__main__':run()
