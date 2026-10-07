import json, numpy as np
import sys
sys.path.insert(0,'/mnt/data')
import stmr_janjul as j, stmr_base as c
from gamma02_feb_native_markout_124 import build_events
from gamma02_feb_lifecycle_quality_125 import precompute_hits,TP_LEVELS,SL_LEVELS,HOLDS
from gamma02_feb_lifecycle_portfolio_125 import choose_outcomes,cap_select,summarize
THR=np.array([0,250,500,750,1000,1500,2000,3000,4000,5000,6000,8000,10000,12000],np.int32)
def met(p):
 gp=float(p[p>0].sum());gl=float(p[p<=0].sum());return dict(net=float(p.sum()),trades=int(len(p)),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0) if len(p) else 0),exp=float(np.mean(p) if len(p) else 0))
def prep_cells():
 t,sa,sb,start,end=j.load_month(2,10);a,b=c.materialize(t,sa,sb);mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32);h4,h1,m15,m5=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)))
 idx,d,hr,sig,disp=build_events(t,mid,h4,h1,m15,m5,start,end,50);L=json.load(open('/mnt/data/gamma02_feb_lifecycle_quality_125.json'))['cells'];out=[]
 for ci,z in enumerate(L,1):
  cell=z['cell']
  if z['top_quality']:cfg=z['top_quality'][0]
  elif z['top_net'][0]['pf']>=2.0:cfg=z['top_net'][0]
  else:continue
  m=(hr==cell['hour'])&(sig==cell['sigcode']);ii=idx[m];dd=d[m];dv=disp[m];b10=((t[ii]//600000)%6).astype(np.int8)
  H=precompute_hits(t,a,b,ii,dd,TP_LEVELS,SL_LEVELS,HOLDS);xt,pnl,reason=choose_outcomes(*H,int(cfg['tp']),int(cfg['sl']),int(cfg['hold_ms']))
  out.append(dict(id=ci,cell=cell,cfg=cfg,ei=ii,et=t[ii],xt=xt,pnl=pnl,reason=reason,disp=dv,b10=b10))
 return t,out
def screen_cell(z):
 rows=[]
 for th in THR:
  m=z['disp']>=th
  if m.sum()>=40:
   r=met(z['pnl'][m]);r.update(thr_raw=int(th),b10_mask=63);rows.append(r)
 masks=[]
 for mask in range(1,64):
  bits=[i for i in range(6) if (mask>>i)&1];contiguous=(max(bits)-min(bits)+1==len(bits))
  if contiguous or mask in (0b000111,0b111000,0b001111,0b111100):masks.append(mask)
 for mask in masks:
  bm=np.zeros(len(z['b10']),dtype=bool)
  for q in range(6):
   if (mask>>q)&1:bm|=(z['b10']==q)
  for th in THR:
   m=bm&(z['disp']>=th)
   if m.sum()<40:continue
   r=met(z['pnl'][m]);r.update(thr_raw=int(th),b10_mask=int(mask));rows.append(r)
 rows.sort(key=lambda r:r['net'],reverse=True);return rows
def pick(rows,mode):
 if mode=='maxnet':return rows[0]
 if mode=='pf5':q=[r for r in rows if r['pf']>=5 and r['win']>=.70 and r['trades']>=60]
 elif mode=='pf10':q=[r for r in rows if r['pf']>=10 and r['win']>=.80 and r['trades']>=40]
 elif mode=='win80':q=[r for r in rows if r['win']>=.80 and r['pf']>=3 and r['trades']>=50]
 else:q=[]
 return max(q,key=lambda r:r['net']) if q else None
def build_portfolio(cells,screens,mode):
 Es=[];Xs=[];Ps=[];Rs=[];Ss=[];chosen=[]
 for z,rows in zip(cells,screens):
  q=pick(rows,mode)
  if q is None:continue
  bm=np.zeros(len(z['b10']),dtype=bool)
  for b in range(6):
   if (q['b10_mask']>>b)&1:bm|=(z['b10']==b)
  m=bm&(z['disp']>=q['thr_raw'])
  Es.append(z['et'][m]);Xs.append(z['xt'][m]);Ps.append(z['pnl'][m]);Rs.append(z['reason'][m]);Ss.append(np.full(int(m.sum()),z['id'],np.int16));chosen.append(dict(cell_id=z['id'],cell=z['cell'],lifecycle=z['cfg'],gate=q))
 if not Es:return None,chosen
 E=np.concatenate(Es);X=np.concatenate(Xs);P=np.concatenate(Ps);R=np.concatenate(Rs);S=np.concatenate(Ss);o=np.argsort(E,kind='stable');return (E[o],X[o],P[o],R[o],S[o]),chosen
def main():
 t,cells=prep_cells();screens=[];out={'candidate':'GAMMA02_FEB_NATIVE_CONVICTION_ROUTING_126','cells':[],'modes':{}}
 for z in cells:
  rows=screen_cell(z);screens.append(rows);rec=dict(cell_id=z['id'],cell=z['cell'],lifecycle=z['cfg'],top_net=rows[:10])
  for mode in ('pf5','pf10','win80'):rec[mode]=pick(rows,mode)
  out['cells'].append(rec);json.dump(out,open('/mnt/data/gamma02_feb_conviction_routing_126.partial.json','w'),indent=2)
 for mode in ('maxnet','pf5','pf10','win80'):
  A,chosen=build_portfolio(cells,screens,mode)
  if A is None:continue
  rows=[]
  for cap in (32,64,96,128,160,192,256,320,384,512):
   B=cap_select(*A,cap);rows.append(summarize(*B[:5],cap,B[5],B[6]))
  out['modes'][mode]={'candidate_events':len(A[0]),'chosen':chosen,'rows':rows};json.dump(out,open('/mnt/data/gamma02_feb_conviction_routing_126.partial.json','w'),indent=2)
 json.dump(out,open('/mnt/data/gamma02_feb_conviction_routing_126.json','w'),indent=2)
if __name__=='__main__':main()
