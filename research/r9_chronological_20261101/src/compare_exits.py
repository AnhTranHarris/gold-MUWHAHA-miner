#!/usr/bin/env python3
"""Match trade lifecycles anchored on exact-time+side+price entries."""
import csv,collections,datetime as dt,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def tm(s):return int(dt.datetime.strptime(s,'%Y.%m.%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp())
ref=[];prev=None
with open(ROOT/'results/coinexx_reference/january_deals.csv') as f:
 for r in csv.DictReader(f):
  if r['E']=='in':prev=r
  elif r['E']=='out' and prev:
   p=prev;prev=None
   ref.append({'s':tm(p['A']),'side':1 if p['D']=='buy' else -1,'price':float(p['G']),
     'exit_s':tm(r['A']),'exit_price':float(r['G']),'exit_type':'stop' if r['M'].startswith('sl ') else 'timeout',
     'net':float(r['K'])+float(r['I'])+float(p['I'])})
sim=[]
with open(ROOT/'results/coinexx_january/trades.csv') as f:
 for r in csv.DictReader(f):
  sim.append({'s':int(r['entry_time_ms'])//1000,'side':int(r['side']),'price':float(r['entry_price']),
    'exit_s':int(r['exit_time_ms'])//1000,'exit_price':float(r['exit_price']),'exit_type':r['reason'],'net':float(r['net'])})
# match exact second and side and entry price to unique same-key multiset, greedily order.
bykey=collections.defaultdict(list)
for i,r in enumerate(sim):bykey[(r['s'],r['side'],round(r['price'],2))].append(i)
match=[]
for j,r in enumerate(ref):
 k=(r['s'],r['side'],round(r['price'],2))
 if bykey[k]:match.append((j,bykey[k].pop(0)))
absdiff=[abs(ref[j]['exit_price']-sim[k]['exit_price']) for j,k in match]
status=collections.Counter((ref[j]['exit_type'],sim[k]['exit_type']) for j,k in match)
netref=sum(r['net'] for r in ref);netsim=sum(r['net'] for r in sim)
value={'reference_trades':len(ref),'replay_trades':len(sim),'exact_entry_time_side_price_matched':len(match),
       'exact_entry_match_ref_recall':len(match)/len(ref),'exit_exact_second_matched':sum(ref[j]['exit_s']==sim[k]['exit_s'] for j,k in match),
       'exit_exact_price_matched':sum(abs(ref[j]['exit_price']-sim[k]['exit_price'])<1e-6 for j,k in match),
       'exit_median_abs_price_difference':statistics.median(absdiff),
       'exit_mean_abs_price_difference':statistics.fmean(absdiff),
       'exit_type_agreement':sum(ref[j]['exit_type']==sim[k]['exit_type'] for j,k in match)/len(match),
       'exit_type_confusion':{str(k):v for k,v in status.items()},
       'reference_jan_net':round(netref,2),'sim_jan_net':round(netsim,2),
       'net_difference_sim_minus_ref':round(netsim-netref,2),
       'first_matched_exit_divergences':[{'ref':ref[j],'replay':sim[k]} for j,k in match if ref[j]['exit_s']!=sim[k]['exit_s']][:20]}
(ROOT/'results/coinexx_exit_parity.json').write_text(json.dumps(value,indent=2))
print(json.dumps({k:v for k,v in value.items() if not k.startswith('first_')},indent=2))
