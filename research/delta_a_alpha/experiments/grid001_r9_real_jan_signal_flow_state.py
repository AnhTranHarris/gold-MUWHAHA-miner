from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np, pandas as pd

CAN_GP=3785.28; CAN_GL=-10436.90; CAN_NET=-6651.62

def run(rows: Path, ticks_path: Path):
 df=pd.read_csv(rows).sort_values('entry_utc_ms').reset_index(drop=True)
 ticks=pd.read_csv(ticks_path,compression='gzip',usecols=['timestamp_ms_utc'],dtype={'timestamp_ms_utc':'i8'}).timestamp_ms_utc.to_numpy()
 split=int(ticks[2*len(ticks)//3]); df['segment']=np.where(df.entry_utc_ms<split,'discovery','validation')

 t=df.entry_utc_ms.to_numpy(np.int64); side=df.side.to_numpy(np.int8); n=len(df)
 dt=np.full(n,np.nan); dt[1:]=(t[1:]-t[:-1])/1000.0
 runlen=np.ones(n,np.int32)
 for i in range(1,n): runlen[i]=runlen[i-1]+1 if side[i]==side[i-1] else 1

 p2=np.zeros(n,float); p10=np.zeros(n,float)
 s2=0.0; s10=0.0
 for i in range(n):
  if i>0:
   delta=(t[i]-t[i-1])/1000.0
   s2*=math.exp(-delta/2.0); s10*=math.exp(-delta/10.0)
  p2[i]=s2; p10[i]=s10
  s2+=side[i]; s10+=side[i]
 a2=side*p2; a10=side*p10

 def pstate(a):
  out=np.empty(len(a),object)
  out[a<=-2]='OPPOSED_STRONG'
  out[(a>-2)&(a<-.5)]='OPPOSED'
  out[(a>=-.5)&(a<=.5)]='NEUTRAL'
  out[(a>.5)&(a<2)]='SUPPORT'
  out[a>=2]='SUPPORT_STRONG'
  return out
 ps2=pstate(a2); ps10=pstate(a10)

 def nested(f,s):
  out=[]
  for x,y in zip(f,s):
   xf=x.startswith('SUPPORT'); xo=x.startswith('OPPOSED')
   yf=y.startswith('SUPPORT'); yo=y.startswith('OPPOSED')
   if xf and yf: z='BOTH_SUPPORT'
   elif xo and yo: z='BOTH_OPPOSE'
   elif xf and yo: z='FAST_SUPPORT_SLOW_OPPOSE'
   elif xo and yf: z='FAST_OPPOSE_SLOW_SUPPORT'
   elif xf and y=='NEUTRAL': z='FAST_ONLY_SUPPORT'
   elif xo and y=='NEUTRAL': z='FAST_ONLY_OPPOSE'
   elif yf and x=='NEUTRAL': z='SLOW_ONLY_SUPPORT'
   elif yo and x=='NEUTRAL': z='SLOW_ONLY_OPPOSE'
   else: z='NEUTRAL_MIXED'
   out.append(z)
  return np.array(out,object)
 flow=nested(ps2,ps10)

 def dtbin(x):
  if np.isnan(x): return 'FIRST'
  if x<1:return '<1s'
  if x<3:return '1-3s'
  if x<10:return '3-10s'
  if x<30:return '10-30s'
  return '>=30s'
 df['dt_bin']=[dtbin(x) for x in dt]

 def runbin(i):
  if i==0 or side[i]!=side[i-1]: return 'NEW_FLIP'
  r=runlen[i]
  if r==2:return 'RUN_2'
  if r<=4:return 'RUN_3_4'
  if r<=8:return 'RUN_5_8'
  return 'RUN_9_PLUS'
 df['run_bin']=[runbin(i) for i in range(n)]
 df['flow_state']=flow; df['fast_state']=ps2; df['slow_state']=ps10
 rel_map={-1:'OPPOSED',0:'NEUTRAL',1:'ALIGNED',2:'CONFLICT'}
 phase_map={0:'NONE',1:'EARLY',2:'MATURE',3:'EXTENDED'}
 df['owner_rel_name']=df.owner_relation.map(rel_map)
 df['phase_name']=df.owner_phase.map(phase_map)

 def econ(mask):
  x=df.loc[mask]
  deals=np.concatenate([x.entry_deal_cashflow.to_numpy(float),x.exit_deal_cashflow.to_numpy(float)]) if len(x) else np.array([],float)
  gp=float(deals[deals>0].sum()) if len(deals) else 0.0
  gl=float(deals[deals<0].sum()) if len(deals) else 0.0
  net=float(x.net_cashflow.sum())
  return {'trades':int(len(x)),'trade_share_pct':100*len(x)/n,'net':net,'gross_profit':gp,'gross_loss':gl,
          'pf':gp/abs(gl) if gl<0 else None,'gross_loss_share_pct':100*abs(gl)/abs(CAN_GL),
          'gross_profit_share_pct':100*gp/CAN_GP,'hypothetical_veto_net_improvement':-net}

 def add(out,family,key,mask):
  mask=np.asarray(mask,bool)
  out.append({'family':family,'key':key,'full':econ(mask),
              'discovery':econ(mask&(df.segment=='discovery')),
              'validation':econ(mask&(df.segment=='validation'))})

 out=[]
 for x in ['<1s','1-3s','3-10s','10-30s','>=30s']: add(out,'S1_DT',x,df.dt_bin==x)
 for x in ['NEW_FLIP','RUN_2','RUN_3_4','RUN_5_8','RUN_9_PLUS']: add(out,'S2_RUN',x,df.run_bin==x)
 for x in ['OPPOSED_STRONG','OPPOSED','NEUTRAL','SUPPORT','SUPPORT_STRONG']:
  add(out,'S3_FAST_PRESSURE',x,df.fast_state==x)
  add(out,'S3_SLOW_PRESSURE',x,df.slow_state==x)

 flow_states=['BOTH_SUPPORT','BOTH_OPPOSE','FAST_SUPPORT_SLOW_OPPOSE','FAST_OPPOSE_SLOW_SUPPORT',
              'FAST_ONLY_SUPPORT','FAST_ONLY_OPPOSE','SLOW_ONLY_SUPPORT','SLOW_ONLY_OPPOSE','NEUTRAL_MIXED']
 for x in flow_states: add(out,'S4_FLOW_STATE',x,df.flow_state==x)
 for x in flow_states:
  for rel in ['ALIGNED','OPPOSED','NEUTRAL','CONFLICT']:
   add(out,'S4xMARKET_REL',f'{x}__{rel}',(df.flow_state==x)&(df.owner_rel_name==rel))
  for ph in ['EARLY','MATURE','EXTENDED','NONE']:
   add(out,'S4xPHASE',f'{x}__{ph}',(df.flow_state==x)&(df.phase_name==ph))

 cands=[]
 for g in out:
  f,d,v=g['full'],g['discovery'],g['validation']
  scale=f['gross_loss_share_pct']>=20 or f['hypothetical_veto_net_improvement']>=.2*abs(CAN_NET)
  stable=d['net']<0 and v['net']<0
  efficient=f['gross_loss_share_pct']>f['gross_profit_share_pct']
  if scale and stable and efficient:
   z=dict(g); z['loss_minus_profit_share_pct']=f['gross_loss_share_pct']-f['gross_profit_share_pct']; cands.append(z)
 cands.sort(key=lambda g:(g['loss_minus_profit_share_pct'],g['full']['hypothetical_veto_net_improvement']),reverse=True)

 selective=[]
 for g in out:
  f,d,v=g['full'],g['discovery'],g['validation']
  if f['trades']>=300 and d['net']<0 and v['net']<0:
   z=dict(g); z['loss_minus_profit_share_pct']=f['gross_loss_share_pct']-f['gross_profit_share_pct']; selective.append(z)
 selective.sort(key=lambda g:(g['loss_minus_profit_share_pct'],g['full']['hypothetical_veto_net_improvement']),reverse=True)

 return {'schema':'delta-a-alpha-r9-real-jan-signal-flow-state-v1',
         'unit':'DAA_GRID_001_R9_REAL_JAN_SIGNAL_FLOW_STATE_001','status':'COMPLETE',
         'canonical':{'net':CAN_NET,'gross_profit':CAN_GP,'gross_loss':CAN_GL},
         'candidate_gate_count':len(cands),'candidates':cands[:20],
         'top_selective_stable':selective[:30],'all_groups':out}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('context_rows',type=Path)
 ap.add_argument('ticks',type=Path)
 ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args()
 res=run(args.context_rows,args.ticks)
 args.output.write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'candidate_gate_count':res['candidate_gate_count'],
                   'candidates':res['candidates'][:12],
                   'top_selective_stable':res['top_selective_stable'][:15]},indent=2))

if __name__=='__main__':
 main()
