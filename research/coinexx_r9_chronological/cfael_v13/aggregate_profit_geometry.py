"""Source-exact causal feature cohorts, no model-training access to future bars."""
import pandas as pd,numpy as np,json
from pathlib import Path
import os
P=Path(os.environ.get('CFAEL_V13_OUTPUT','/mnt/data/cfael_v13'))
df=pd.concat([pd.read_csv(P/f'{m:02d}_causal_entry_features.csv.gz') for m in range(1,10)],ignore_index=True)
df=df[df.original_net.notna()].copy()
df['month_i']=df.month.astype(int)
def summary(x):
 return {'trades':len(x),'winners':int((x.original_net>0).sum()),'win_pct':round(100*(x.original_net>0).mean(),2) if len(x) else None,
         'net':round(float(x.original_net.sum()),2),'net_per_trade':round(float(x.original_net.mean()),4) if len(x) else None}
winning=int((df.original_net>0).sum())
categories={
 'micro_twap_location':pd.cut(df.micro_twap_dev_c,[-1e8,-150,-75,-30,0,30,75,150,1e8],include_lowest=True),
 'session_anchor_location':pd.cut(df.session_twap_dev_c,[-1e8,-500,-200,-75,0,75,200,500,1e8],include_lowest=True),
 'fib_m1_nearest':pd.cut(df.fib_m1_dist_50_c,[-1e8,-150,-50,-25,0,25,50,150,1e8],include_lowest=True),
 'fib_m5_nearest':pd.cut(df.fib_m5_dist_50_c,[-1e8,-250,-100,-50,0,50,100,250,1e8],include_lowest=True),
 'ema20_sma20_divergence':pd.cut(df.ema20_sma20_spread_c,[-1e8,-300,-100,-25,0,25,100,300,1e8],include_lowest=True),
 'micro_range':pd.cut(df.micro_range_c,[-1,50,100,200,400,800,1600,1e8]),
 'micro_position_frac':pd.cut(df.micro_position_frac,[-1,.2,.4,.6,.8,1.,2.],include_lowest=True),
 'session_hour_utc':df.hour_utc,
 'pivot_direction_M1':df.fib_m1_direction,
 'pivot_direction_M5':df.fib_m5_direction,
 'ema_slope':pd.cut(df.ema20_slope_c,[-1e8,-50,-10,0,10,50,1e8]),
 'sma_slope':pd.cut(df.m5_sma20_slope_c,[-1e8,-100,-25,0,25,100,1e8]),
}
report={'source':'Nine original pinned Coinexx months + original V12 entry/exit snapshots', 'entries':338065,'completed':len(df),
 'winning_entries':winning,'baseline':summary(df),'definitions':'All groups use as-of-entry causal features, outcomes are original V9 simulated cash with cost. No group is an executable altered strategy.',
 'by_feature':{}}
for name,key in categories.items():
 groups=[]
 for value,group in df.groupby(key,dropna=False,observed=True):
  g=summary(group)
  g.update(group=str(value),share_of_profitable_V9_trades_pct=round(g['winners']/winning*100,2),
    jan_apr_net_per_trade=round(float(group[group.month_i<=4].original_net.mean()),5) if len(group[group.month_i<=4]) else None,
    jul_sep_net_per_trade=round(float(group[group.month_i>=7].original_net.mean()),5) if len(group[group.month_i>=7]) else None)
  groups.append(g)
 report['by_feature'][name]=groups
(P/'V13_NINE_MONTH_PROFITABLE_TRADE_GEOMETRY.json').write_text(json.dumps(report,indent=2))
for name in ('micro_twap_location','fib_m1_nearest','ema20_sma20_divergence','micro_position_frac'):
 print(name,[(x['group'],x['trades'],x['winners'],x['share_of_profitable_V9_trades_pct'],x['net_per_trade']) for x in report['by_feature'][name]])
