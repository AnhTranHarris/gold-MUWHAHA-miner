"""Causal feature stratification for prospective V15 entry groups.
Do not select on realized future trade labels at decision time. Reports ALL
trades per predefined group, winners and full costs to avoid survivor bias.
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np
BASE=Path('/mnt/data/v15_profitfirst')
FAMILIES=('C_fib382_costcovered','R2_two_sided_stop_run_reclaim','S_verified_breakout_cascade')
MONTHS=('01','05','09')
rows=[]
for family in FAMILIES:
    for month in MONTHS:
        p=BASE/f'V15_{month}_{family}_all_events.csv.gz'
        if not p.exists():continue
        d=pd.read_csv(p)
        x=d['modeled_net_cash'];sign=d['side']
        # Predeclared as-of-entry geometry / execution proxy slices;
        # deliberately not a large Cartesian hyperparameter grid.
        masks={
         'ALL':np.ones(len(d),dtype=bool),
         'M15_TREND_ALIGNED':d['m15_ema20_slope_align']==True,
         'M15_COUNTER_DIRECTION':d['m15_ema20_slope_align']==False,
         'M15_ALIGNED_SPREAD_LE20':(d['m15_ema20_slope_align']==True)&(d['entry_spread_c']<=20),
         'M15_COUNTER_TWAP_DISCOUNT':(d['m15_ema20_slope_align']==False)&(d['session_twap_premium_c']<=0),
         'M15_ALIGNED_STRONG_RECLAIM_BAR':(d['m15_ema20_slope_align']==True)&(d['completed_5s_range_c']>=100),
         'LOCAL_TWAP_DISCOUNT_QUOTE_QUALITY':(d['session_twap_premium_c']<=0)&(d['entry_spread_c']<=20),
        }
        for name,mask in masks.items():
            subset=d[mask]
            if len(subset)==0:continue
            y=subset.modeled_net_cash
            rows.append(dict(family=family,month=month,group=name,
                n=len(y),positive_trades=int((y>0).sum()),win_pct=round(100*(y>0).mean(),2),
                mean_cash=round(y.mean(),4),net_cash=round(y.sum(),2),
                mean_winner_cash=round(y[y>0].mean(),4) if any(y>0) else None,
                mean_loser_cash=round(y[y<=0].mean(),4) if any(y<=0) else None))
output=BASE/'V15_POSITIVE_OPPORTUNITY_STRATA.csv'
pd.DataFrame(rows).to_csv(output,index=False)
for fam in FAMILIES:
    print('\n',fam)
    vals=pd.DataFrame(rows);sel=vals[(vals.family==fam)&(vals.n>=60)]
    if len(sel):print(sel.pivot_table(index='group',columns='month',values='mean_cash').round(3).to_string())
