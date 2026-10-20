#!/usr/bin/env python3
"""Append-only precise feature-group attribution for FILTER08 already fitted models.
Gain is in-sample LightGBM split metric, NOT causal/out-of-sample evidence.
"""
import csv,json
from pathlib import Path
D=Path('/mnt/data/R00_054_FILTER08_FOUR_MONTH_DISCOVERY')
def fam(name):
 if name.startswith('side_orig_'):i=int(name.rsplit('_',1)[1]);return 'SIDE_RELATIVE_LONG_SHORT_RETURNS' if i<=8 else 'SIDE_RELATIVE_QUOTE_DIRECTIONAL_IMBALANCE'
 if name.startswith('orig_'):
  i=int(name[5:]);
  if i<=8:return 'MULTIHORIZON_PAST_RETURNS_1S_TO_H1'
  if i<=11:return 'DIRECTIONAL_EFFICIENCY_5_TO_30S'
  if i<=13 or i==42:return 'SOURCE_TICK_ARRIVAL_INTENSITY'
  if i==14:return 'BID_ASK_SPREAD'
  if i<=17:return 'SOURCE_TICK_SIGN_IMBALANCE'
  if i<=20:return 'QUOTE_PATH_REALIZED_VOLATILITY'
  if i<=24:return 'COMPLETED_M1_STRUCTURE_GEOMETRY'
  if i<=28:return 'COMPLETED_M5_STRUCTURE_GEOMETRY'
  if i<=32:return 'COMPLETED_M15_STRUCTURE_GEOMETRY'
  if i<=36:return 'COMPLETED_H1_STRUCTURE_GEOMETRY'
  return 'UTC_SESSION_CLOCK_CONTEXT'
 if name.startswith('matured_'):return 'MATURED_PRIOR_SIGNAL_FEEDBACK'
 if name.startswith('expert_') or name.startswith('side_expert_'):return 'INDEPENDENT_EXPERT_LIFECYCLE_STATES'
 if name.startswith('hour_') or name.startswith('dow_') or name.startswith('session_'):return 'UTC_SESSION_CLOCK_CONTEXT'
 if name=='side':return 'ORIGINAL_BUY_SELL_SIDE'
 return 'ORDERED_BID_ASK_QUOTE_RESPONSE'
rows=[]
for b in ('coinexx','dukascopy'):
 for m in ('01','02','06','07'):
  f=D/f'FEATURE_GAINS_{b}_{m}.csv'
  with f.open(newline='') as fh: data=list(csv.DictReader(fh))
  den=sum(float(v['gain']) for v in data)
  for v in data:
   rows.append({'broker':b,'month':m,'feature':v['feature'],'group':fam(v['feature']),'model_fit_gain_fraction':float(v['gain'])/den,'original_in_sample_rank':int(v['rank'])})
with (D/'FINE_GRAINED_FEATURE_FACETS_PER_MODEL.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
by={}
for r in rows:
 k=(r['broker'],r['group']);by[k]=by.get(k,0)+r['model_fit_gain_fraction']/4
sorted_groups={b:sorted([{'group':group,'average_fit_gain_share':share} for (br,group),share in by.items() if br==b],key=lambda x:-x['average_fit_gain_share']) for b in ('coinexx','dukascopy')}
(D/'FINE_GRAINED_FAMILY_GAINS_PER_BROKER.json').write_text(json.dumps({'method':'average in-sample LightGBM booster gain split across four same-month fitted overlays; descriptive only, not proof of independent forecast power','groups':sorted_groups},indent=2)+'\n')
for b in ('coinexx','dukascopy'):
 print(b,[(x['group'],round(x['average_fit_gain_share']*100,1)) for x in sorted_groups[b][:8]])
