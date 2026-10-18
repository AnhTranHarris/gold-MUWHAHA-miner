"""Non-fitting read-only label feasibility audit on original R00-063 +30s event arrays.
No new market data, no backtest or outcome relabeling. Neutrals/missing remain wrong.
"""
import csv, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np

SOURCE = Path('/mnt/data/R00_063_COMPLETE_NATIVE_QUOTE_RESEARCH_20261018.zip')
PIN = 'c36bd88c018c8fa10f47b9f344a8e551abf7059961436b4b71051b61c436c880'
OUT = Path('/mnt/data/R00_066_EVENT_LABEL_CEILING_AUDIT_20261018.csv')

def main():
    actual=hashlib.file_digest(SOURCE.open('rb'),'sha256').hexdigest()
    if actual!=PIN:
        raise ValueError(f'Source ZIP digest mismatch: {actual}')
    rows=[]
    with zipfile.ZipFile(SOURCE) as z:
        for broker in ('coinexx','dukascopy'):
            for month in ('06','07'):
                member=f'R00_063_NATIVE_RESEARCH_20261018/native_{broker}_{month}.npz'
                with np.load(io.BytesIO(z.read(member)),allow_pickle=False) as obj:
                    y=obj['y']; known=obj['known_future']; n=len(y)
                    up=int((y==1).sum()); down=int((y==-1).sum())
                    neutral=int(((y==0)&known).sum()); missing=int((~known).sum())
                    assert up+down+neutral+missing==n
                    rows.append({'broker':broker,'month_2026':month,'events':n,'up':up,'down':down,
                                 'neutral_known':neutral,'missing_future':missing,
                                 'maximum_accuracy_at_100pct_emission':(up+down)/n,
                                 'conditional_direction_accuracy_needed_for_80pct_overall':.8/((up+down)/n)})
    with OUT.open('w',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    event_count=sum(r['events'] for r in rows); directional=sum(r['up']+r['down'] for r in rows)
    print(json.dumps({'source_sha256':PIN,'events':event_count,'directional':directional,
          'non_directional':event_count-directional,
          'maximum_accuracy_at_100pct_emission':directional/event_count,
          'conditional_direction_accuracy_needed_for_80pct_overall':.8/(directional/event_count),
          'note':'Exposed June-July diagnostic population; strict initial native R00-063 clock and +30s target; not a blind test.'},indent=2))
if __name__=='__main__': main()
