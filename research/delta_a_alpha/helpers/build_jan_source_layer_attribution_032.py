"""Source-preserving original 131E component attribution after exact supplement de-dup/cap.
No new entry rules; only diagnostic family labels restored from original input parts.
"""
from pathlib import Path
import sys,json,csv,collections,datetime,numpy as np
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import stmr_base as st
st.materialize=lambda t,sa,sb:(sa.copy(),sb.copy())
import jan_profit_per_heat_highrange_131e as F
import jan_session_portfolio_131d as J
import jan_session_portfolio_lean_131d as L
T=J.DATA[0]
A,lay=F.build_raw();E,X,R,D,P,H=A
base=np.flatnonzero(lay<=35);ii=base[F.capsel(E[base],X[base],640)];WD=tuple(z[ii] for z in A)
orig=[('L4_WATCHDOG_131E',WD),('L3_HOURLY_COVERAGE',J.build_coverage()),('L3_HOURLY_COLDSTART',J.build_coldstart(50,450,64))]
orig+= [('L3_ORIGINAL_LEAN4_'+n,L.build_rule(k,l,stp,cap)) for k,l,n,stp,cap in L.LEAN]
scal={}
for name,part in orig[1:]:
 for ei in part[0]:scal.setdefault(int(ei),name)
supp,sk=J.dedup_market_tick([p for name,p in orig[1:]])
O=np.argsort(supp[0],kind='stable');supp=tuple(z[O] for z in supp)
supp,mo,sk2=J.cap_arrays(*supp,512)
by=collections.defaultdict(lambda:[0,0,0,0])
day=collections.defaultdict(lambda:[0,0,0,0]);week=collections.defaultdict(lambda:[0,0,0,0]);unique=collections.defaultdict(set)
for label,part in [('L4_WATCHDOG_131E',WD),('SUPPLEMENT',supp)]:
 for ei,xi,p in zip(part[0],part[1],part[4]):
  name=label if label!='SUPPLEMENT' else scal[int(ei)]
  dt=datetime.datetime.fromtimestamp(int(T[xi])/1000,datetime.timezone.utc)
  daykey=dt.strftime('%Y-%m-%d');weekkey=f'{dt.isocalendar().year}-W{dt.isocalendar().week:02d}'
  for key,dct in ((name,by),((daykey,name),day),((weekkey,name),week)):
   a=dct[key];a[0]+=float(p);a[1]+=1;a[2]+=max(0,float(p));a[3]+=min(0,float(p))
  unique[name].add(int(ei))
ledger={'all_month':{k:{'net':round(v[0],3),'trades':v[1],'gross_profit':round(v[2],3),'gross_loss':round(v[3],3),'unique_entry_ticks':len(unique[k])} for k,v in by.items()},'daily':{'|'.join(k):{'net':round(v[0],3),'trades':v[1],'gross_loss':round(v[3],3)} for k,v in day.items()},'weekly':{'|'.join(k):{'net':round(v[0],3),'trades':v[1],'gross_loss':round(v[3],3)} for k,v in week.items()},'supp_source_duplicate_rejections':sk,'supp_source_capacity_rejections':sk2,'sup_funded_count':len(supp[0]),'watchdog_funded_count':len(WD[0]),'labels_source':'Original preserved 131E part order; actual Bid/Ask; labels are DIAGNOSTIC not claim of complete whitepaper layer parity.'}
(ROOT/'output'/'JAN032_ORIGINAL_SOURCE_COMPONENT_ATTRIBUTION.json').write_text(json.dumps(ledger,indent=2))
with (ROOT/'output'/'JAN032_COMPONENT_DAILY.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['UTC_date','original_source_component','net_usd','trades','gross_loss_usd'])
 for (date,name),v in sorted(day.items()):w.writerow([date,name,round(v[0],3),v[1],round(v[3],3)])
month=sum(v[0] for v in by.values());tr=sum(v[1] for v in by.values());print('SOURCE_COMPONENTS',len(by),'total',round(month,3),'trades',tr,'supp_duplicate',sk,'supp_cap',sk2)
for k,v in by.items():print(k,round(v[0],2),v[1],round(v[3],2))
for d in ['2026-01-08','2026-01-30']:
 print('DATE',d,[(name,round(v[0],2),v[1]) for (date,name),v in day.items() if date==d])
assert abs(month-93425.311)<.01 and tr==47511