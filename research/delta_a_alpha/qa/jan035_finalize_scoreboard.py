"""Reconcile chosen Jan035 fixed original-candidate tape scenarios to R9.
Forensic causal admission interventions, not full funded parent genealogy.
"""
from pathlib import Path
import json,hashlib,datetime,csv
import numpy as np,pandas as pd
from jan035_combined_causal_admission import load,lagged,run
R=Path('/mnt/data/daa_jan_combined_035');SYN=json.load(open('/mnt/data/daa_jan_exact_032/r9_synth_jan_daily_weekly.json'))
CASES=[
 ('original_raw',9999,640,0,0,0,0,0,0),
 ('fast384',384,640,0,0,0,0,0,0),
 ('fast384_spread3',384,640,0,0,3000,0,0,0),
 ('fast256_heat500',256,640,0,0,0,0,500,0),
 ('fast192',192,640,0,0,0,0,0,0),
 ('fast256_spread2',256,640,0,0,2000,0,0,0),
 ('fast512_spread3',512,640,0,0,3000,0,0,0),
 ('broker_proxy_one_per_quote',1,640,0,0,0,0,0,0),
]

def sheet(key,t,exit_i,p):
    dt=pd.to_datetime(t[exit_i],unit='ms',utc=True)
    if key=='day': lab=dt.strftime('%Y-%m-%d')
    else:
        i=dt.isocalendar();lab=i.year.astype(str)+'-W'+i.week.astype(str).str.zfill(2)
    f=pd.DataFrame({'p':p,'group':lab})
    out=f.groupby('group')['p'].agg(net='sum',trades='size',gross_profit=lambda s:s[s>0].sum(),gross_loss=lambda s:s[s<0].sum(),wins=lambda s:(s>0).sum())
    benchmark=SYN['daily' if key=='day' else 'weekly']
    joined=[]
    for period,v in benchmark.items():
        r=out.loc[period].to_dict() if period in out.index else {'net':0.,'trades':0,'gross_profit':0.,'gross_loss':0.,'wins':0}
        rr={'period':period,**{k:(int(value) if k in ('trades','wins') else round(float(value),4)) for k,value in r.items()},'R9_synth_net':v['net'],'R9_synth_trades':v['trades'],'R9_synth_gross_loss_from_saved_daily_source':v['gross_loss'],'delta_R9_net':round(float(r['net'])-float(v['net']),4)}
        joined.append(rr)
    return joined

def main():
 t,a,b,E,X,Rp,D,S=load();l5=lagged(t,a,b,E,5000);l15=lagged(t,a,b,E,15000);l60=lagged(t,a,b,E,60000)
 scores=[]
 for j,c in enumerate(CASES):
    n,pc,wd,v5,v15,sp,tb,h,st=c
    p,s,x,e,dd,maxop,maxwd,rej,pk,tr=run(t,a,b,E,X,Rp,D,S,l5,l15,l60,pc,wd,v5,v15,sp,tb,h,st,True)
    assert int(x.max())<len(t)
    gp=float(p[p>0].sum());gl=float(p[p<0].sum());net=float(p.sum())
    daily=sheet('day',t,x,p);weekly=sheet('week',t,x,p)
    result={'name':n,'params':{'max_same_tick_Watchdog_proposals':pc,'wd_open_cap':wd,'adverse5_raw':v5,'adverse15_raw':v15,'entry_spread_ceiling_raw':sp,'trend_bias':tb,'wd_open_floating_loss_no_new_trade_threshold':h,'stress':st},'net':net,'trades':int(len(p)),'gross_profit':gp,'gross_loss':gl,'profit_factor':gp/-gl,'win_rate_pct':float(100*(p>0).mean()),'floating_equity_dd':float(dd),'max_open_total':int(maxop),'max_open_watchdog':int(maxwd),'watchdog_net':float(p[s==0].sum()),'hourly_net':float(p[s==1].sum()),'positive_days':sum(r['net']>0 for r in daily),'days_beat_synth_net':sum(r['delta_R9_net']>0 for r in daily),'positive_weeks':sum(r['net']>0 for r in weekly),'weeks_beat_synth_net':sum(r['delta_R9_net']>0 for r in weekly),'jan30_net':next(r['net'] for r in daily if r['period']=='2026-01-30'),'jan30_trades':next(r['trades'] for r in daily if r['period']=='2026-01-30')}
    if n=='original_raw':assert abs(net-93425.311)<.01 and abs(dd-56921.6)<.1
    (R/(n+'_DAILY.json')).write_text(json.dumps(daily,indent=2)+'\n');(R/(n+'_WEEKLY.json')).write_text(json.dumps(weekly,indent=2)+'\n')
    scores.append(result)
    print(n,round(net,2),len(p),round(gl,2),round(gp/-gl,2),round(dd,2),result['days_beat_synth_net'],result['weeks_beat_synth_net'],flush=True)
 pd.DataFrame(scores).to_csv(R/'JAN035_FINAL_MONTHLY_COMPARISON.csv',index=False)
 (R/'JAN035_FINAL_MONTHLY_COMPARISON.json').write_text(json.dumps({'benchmark':{'jan_2026_synth_net':41520.82,'trades':27980,'canonical_profit_factor':21.042778,'canonical_gross_loss':-2071.61},'candidate_tape_causality_limitation':'Original 131E prospective parents/children are NOT re-derived after rejected or exited originals, so selection is a sensitivity result, not whole-system V1 parity','cases':scores},indent=2)+'\n')
 with (R/'JAN035_WEEKLY_SELECTED.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['strategy','period','net','trades','gross_loss','R9_synth_net','R9_synth_trades','delta_R9_net']);w.writeheader()
  for n,*_ in CASES:
   for row in json.load(open(R/(n+'_WEEKLY.json'))):w.writerow({k:(n if k=='strategy' else row.get(k)) for k in w.fieldnames})
 with (R/'JAN035_DAILY_SELECTED.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['strategy','period','net','trades','gross_loss','R9_synth_net','R9_synth_trades','delta_R9_net']);w.writeheader()
  for n,*_ in CASES:
   for row in json.load(open(R/(n+'_DAILY.json'))):w.writerow({k:(n if k=='strategy' else row.get(k)) for k in w.fieldnames})
if __name__=='__main__':main()