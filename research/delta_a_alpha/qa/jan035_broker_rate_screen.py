"""Rate/concurrency sensitivity for the archival fixed candidate stream. Not broker certification."""
import json,time,numpy as np,pandas as pd
from pathlib import Path
from jan035_combined_causal_admission import run,load,lagged
P=Path('/mnt/data/daa_jan_combined_035')
def main():
 t,a,b,E,X,R,D,S=load(); l5=lagged(t,a,b,E,5000);l15=lagged(t,a,b,E,15000);l60=lagged(t,a,b,E,60000)
 cfg=[('base',9999,640,0,0),('cap384',384,640,0,0)]
 for cap in [1,2,4,8,16,32,48,64]:
  for spread in [0,2000,3000]:cfg.append((f'rate{cap}_spr{spread}',cap,640,spread,0))
 for pos in [64,128,192,256]:
  for cap in [16,64,192]:cfg.append((f'rate{cap}_inventory{pos}',cap,pos,0,0))
 out=[]
 for i,(name,cap,wd,sp,_) in enumerate(cfg):
  p,s,x,e,dd,m,wm,rej,_,_=run(t,a,b,E,X,R,D,S,l5,l15,l60,cap,wd,0,0,sp,0,0,0,True)
  gp=float(p[p>0].sum());gl=float(p[p<0].sum())
  z={'scenario':name,'same_quote_max':cap,'total_watchdog_open_max':wd,'spread_ceiling_raw':sp,'net':round(float(p.sum()),3),'trades':len(p),'gross_loss':round(gl,3),'pf':round(gp/-gl,4),'dd':round(float(dd),2),'max_open':int(m),'wd_net':round(float(p[s==0].sum()),3),'hourly_net':round(float(p[s==1].sum()),3)}
  out.append(z)
  (P/('rate_'+name+'.json')).write_text(json.dumps(z,indent=2)+'\n')
  if i%5==0:print('SAVED',i+1,'/',len(cfg),z,flush=True)
 (P/'BROKER_RATE_SCREEN_ALL.json').write_text(json.dumps(out,indent=2)+'\n');pd.DataFrame(out).to_csv(P/'BROKER_RATE_SCREEN_ALL.csv',index=False)
if __name__=='__main__':main()