import importlib.util,json
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('v','/mnt/data/BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
# nearby January-qualified adaptive cost/opportunity variants
configs=[('ADAPT_090_070',.90,.70,.18),('ADAPT_100_065',1.00,.65,.18),('ADAPT_110_065',1.10,.65,.18),('ADAPT_120_060',1.20,.60,.18)]
agg={n:{'trades':0,'wins':0,'net':0.,'gp':0.,'gl':0.,'equity':0.,'peak':0.,'maxdd':0.} for n,_,_,_ in configs}
base={'trades':0,'wins':0,'net':0.,'gp':0.,'gl':0.,'equity':0.,'peak':0.,'maxdd':0.};tail=None;months=[]
for month,fn,expect in v.FILES:
 p=Path('/mnt/data')/fn;t,a,b,sha,problems=v.load_month(p);assert sha==expect and not problems
 if tail is not None:
  tw,aw,bw=tail;tall=np.concatenate([tw,t]);aall=np.concatenate([aw,a]);ball=np.concatenate([bw,b]);start_i=len(tw)
 else:tall,aall,ball=t,a,b;start_i=0
 prep=v.prep(tall,aall,ball)
 R=v.sim(tall,aall,ball,start_i,*prep,0,0.,0.,0.,base['equity'],base['peak'],base['maxdd']);tr,wi,wr,net,gp,gl,eq,peak,dd=R;base.update({'equity':float(eq),'peak':float(peak),'maxdd':float(dd)});base['trades']+=int(tr);base['wins']+=int(wi);base['net']+=float(net);base['gp']+=float(gp);base['gl']+=float(gl)
 mm={'month':month,'base':{'trades':int(tr),'wins':int(wi),'win_rate':float(wr),'net_usd':float(net)},'candidates':{}}
 for name,cap,ratio,d5 in configs:
  T=agg[name];R=v.sim(tall,aall,ball,start_i,*prep,1,cap,ratio,d5,T['equity'],T['peak'],T['maxdd']);tr,wi,wr,net,gp,gl,eq,peak,dd=R;T.update({'equity':float(eq),'peak':float(peak),'maxdd':float(dd)});T['trades']+=int(tr);T['wins']+=int(wi);T['net']+=float(net);T['gp']+=float(gp);T['gl']+=float(gl);mm['candidates'][name]={'trades':int(tr),'wins':int(wi),'win_rate':float(wr),'net_usd':float(net),'gross_loss_usd':float(gl),'cumulative_dd_usd':float(dd)}
 months.append(mm);cut=t[-1]-2*3600*1000;j=np.searchsorted(t,cut,side='left');tail=(t[j:].copy(),a[j:].copy(),b[j:].copy());print(month,{n:(mm['candidates'][n]['wins'],round(mm['candidates'][n]['net_usd'],1)) for n,_,_,_ in configs},flush=True)
basewr=base['wins']/base['trades']
for n,T in agg.items():
 T['win_rate']=T['wins']/T['trades'];T['wins_change_pct']=100*(T['wins']/base['wins']-1);T['win_rate_change_pct']=100*(T['win_rate']/basewr-1);T['net_improve_pct_abs_base']=100*(T['net']-base['net'])/abs(base['net']);T['net_improvement_usd']=T['net']-base['net'];T['dd_change_pct']=100*(T['maxdd']/base['maxdd']-1);T['gross_loss_change_pct']=100*(abs(T['gl'])/abs(base['gl'])-1);T['passes_entry_10pct_gate']=T['wins_change_pct']>10 and T['win_rate_change_pct']>10 and T['net_improve_pct_abs_base']>10 and T['maxdd']<base['maxdd']
 T['fee_030_net']=T['net']-.10*T['trades'];T['fee_040_net']=T['net']-.20*T['trades'];T['fee_030_improve_pct']=100*(T['fee_030_net']-(base['net']-.10*base['trades']))/abs(base['net']-.10*base['trades']);T['fee_040_improve_pct']=100*(T['fee_040_net']-(base['net']-.20*base['trades']))/abs(base['net']-.20*base['trades'])
out={'unit_id':'BETA_010_JAN_JUL_ADAPTIVE_ENTRY_FAMILY__001','base':base,'candidate_definitions':{n:{'spread_abs_cap':cap,'spread_to_recent_range_cap':ratio,'d5_ignition_min':d5} for n,cap,ratio,d5 in configs},'monthly':months,'aggregate':agg,'method':'Same fixed R9 hold/exit; early momentum specialist; actual Dukascopy Bid/Ask fills; $0.20 roundtrip fee baseline; source SHA/CRC verified each month by shared loader; 2h previous-month warmup; January discovery then Jan-Jul analysis.','august_read':False}
Path('/mnt/data/BETA_010_JAN_JUL_ADAPTIVE_ENTRY_FAMILY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'base':base,'aggregate':agg},indent=2))