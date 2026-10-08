import json,numpy as np
import jan_session_portfolio_131d as J
import gamma02_ny_campaign_inventory_portfolio_001 as gp
from general_session_state_discovery_131c import build_events

OUT='/mnt/data/gamma02_jan_repro/jan_session_portfolio_lean_131d.json'
# per-session causal geometry selected from local plateaus, no calendar labels
LEAN=[
 ((2,1,1,-1,-1,1),(12000,4000,300000),'ASIA02_CONT',50,64),
 ((10,1,-1,-1,-1,1),(0,0,120000),'LONDON10_ROTATE_LONG',50,16),
 ((13,1,-1,1,-1,-1),(12000,4000,300000),'OVERLAP13_SHORT',50,16),
 ((21,1,-1,-1,-1,1),(0,0,120000),'LATE21_LONG',50,32),
]

def build_rule(key,life,step,cap):
 t,a,b,mid,h4,h1,m15,m5=J.DATA[:8];es,ee=J.DATA[-2:];ii,d=build_events(t,mid,step);m=(t[ii]>=es)&(t[ii]<ee);ii=ii[m];d=d[m];hour=((t[ii]//3600000)%24).astype(np.int8)
 hh,H4,H1,M15,M5,dr=key;mm=(hour==hh)&(h4[ii]==H4)&(h1[ii]==H1)&(m15[ii]==M15)&(m5[ii]==M5)&(d==dr);ev=ii[mm];dirs=d[mm];tp,sl,hold=life;xt,p,rs=gp.precompute_outcomes(t,a,b,ev,dirs,tp,sl,hold);X=np.searchsorted(t,xt);R=np.where(dirs>0,a[ev],b[ev]).astype(np.int64);H=(t[X]-t[ev])/1000.;return J.cap_arrays(ev.astype(np.int64),X.astype(np.int64),R,dirs.astype(np.int8),p.astype(float),H.astype(float),cap)[0]

def main():
 wd=J.build_watchdog();cov=J.build_coverage();rules=[build_rule(k,l,st,cap) for k,l,n,st,cap in LEAN];rows=[]
 for coldcap in [0,64,96,128,160,192,256]:
  parts=[cov]
  if coldcap:parts.append(J.build_coldstart(50,450,coldcap))
  parts+=rules
  Q,meta=J.merge_preserve_watchdog(wd,parts,512);meta.update(cold_cap=coldcap,rescue_profile='LEAN4')
  s,_=J.score(J.DATA[0],*Q,f'WD119_COVERAGE_LEAN4_COLD{coldcap}',meta);rows.append(s)
 rows.sort(key=lambda r:(r['positive_days'],r['beat_weeks'],r['beat_days'],r['pf'],r['net']),reverse=True)
 json.dump({'candidate':'GAMMA_02_JAN_SESSION_PORTFOLIO_LEAN_131D','lean_rules':[{'cell':list(k),'life':list(l),'name':n,'step':st,'cap':cap} for k,l,n,st,cap in LEAN],'rows':rows},open(OUT,'w'),indent=2)
 for r in rows:print({k:r[k] for k in ['name','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks','cold_cap']},'weeks',{k:round(v['net'],2) for k,v in r['weekly'].items()},'weak',{k:round(r['daily'][k]['net'],2) for k in ['2026-01-07','2026-01-08','2026-01-15','2026-01-16']})
if __name__=='__main__':main()