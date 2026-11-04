"""Independent selected-winner and full-calendar read-only C8 verifier.
Replay every NEW offline selected winner on source quote ordinals in pure Python.
This is not validation of causal side selection nor original R9 stop/exit.
"""
from __future__ import annotations
import sys,csv,json,argparse
from pathlib import Path
import numpy as np
R=Path('/mnt/data/h1v2_r20_last46');sys.path.insert(0,str(R/'src'))
import r20_residual_quote_hazard as base

def rows(path):
 with open(path,newline='') as f:return list(csv.DictReader(f))

def one(src,mon):
 t,b,a,_,_,_,pr=base.get_frozen(src,mon);refs=base.r18.refs_for_month(mon,Path('/mnt/data'))
 qref=refs['qref'];href=refs['href'];qkeys=refs['qkeys'];oldf,olde,baseq,miss=base.get_old(src,mon,t,refs)
 stem=f'R20C8_{src}_{mon}';sc=rows(R/'results'/f'{stem}_ALL_SCENARIOS.csv');q=rows(R/'results'/f'{stem}_ALL_UTC_QUARTERS.csv');h=rows(R/'results'/f'{stem}_ALL_UTC_HOURS.csv')
 assert len(sc)==5 and len(q)==5*len(qref) and len(h)==5*len(href)
 path=R/'results'/f'{stem}_ALL_TRIAL_SOURCE_ORDINALS_AND_TWO_SIDES.npz';verified=0
 with np.load(path,allow_pickle=False) as z:
  for case in sc:
   name=case['mechanism'];qr=[x for x in q if x['mechanism']==name];hr=[x for x in h if x['mechanism']==name];assert len(qr)==len(qref) and len(hr)==len(href)
   bq=np.array([int(x['base_R19_S3_future_winners']) for x in qr]);nq=np.array([int(x['R20_future_total']) for x in qr]);dq=nq-bq
   assert np.array_equal(bq,baseq) and np.all(dq>=0)
   assert np.array_equal(np.array([int(x['R9_SYNTH_source_ref']) for x in qr]),qref)
   assert np.array_equal(np.array([int(x['future_total_hour']) for x in hr]),nq.reshape(-1,4).sum(axis=1))
   assert int(case['new_active_quarter_quota_met'])==int(np.sum((qref>0)&(nq>=qref)))
   assert int(case['new_active_hour_quota_met'])==int(np.sum((href>0)&(nq.reshape(-1,4).sum(axis=1)>=href)))
   orig=z[name+'__filled_quote_ordinal'];codes=z[name+'__both_buy_sell_independent_codes'];ex=z[name+'__both_side_exit_quote_ordinals'];nets=z[name+'__both_side_realized_quoted_price_net_raw'];stop=z[name+'__stop_raw'];assert len(orig)==len(codes)==len(stop)==len(ex)==len(nets)
   assert int(case['independent_dual_side_completed_good'])==int((codes==1).sum())
   assert int(case['independent_dual_side_completed_stop'])==int((codes==0).sum())
   assert int(case['independent_dual_side_completed_timeout'])==int((codes==2).sum())
   assert int(case['independent_dual_side_right_censored'])==int((codes==-3).sum())
   complete=(codes==0)|(codes==1)|(codes==2)
   assert int(case['independent_dual_side_COMPLETED_quote_net_sum_counterfactual_RAW'])==int(nets[complete].astype(np.int64).sum())
   addf=z[name+'__new_fill_quote_ordinal'];adde=z[name+'__new_first_target_exit_quote_ordinal'];addside=z[name+'__new_future_side'];addnet=z[name+'__new_net_quote_raw']
   assert len(addf)==len(adde)==len(addside)==len(addnet)==dq.sum()
   if len(addf)>1:assert np.all(t[addf[1:]]>t[adde[:-1]])
   assert np.array_equal(np.bincount(t[addf]//900000-qkeys[0],minlength=len(qref)),dq)
   oldnewst=np.r_[t[oldf],t[addf]];oldnewen=np.r_[t[olde],t[adde]];j=np.argsort(oldnewst,kind='stable');assert np.all(oldnewst[j][1:]>oldnewen[j][:-1])
   for f,j,side,net in zip(addf,adde,addside,addnet):
    i=int(np.searchsorted(orig,f));assert i<len(orig) and int(orig[i])==int(f)
    sd=0 if side==1 else 1;bar=int(stop[i]);opening=int(b[f] if side==1 else a[f]);entry=int(a[f] if side==1 else b[f])
    assert bar>=100 and bar<=1000 and int(ex[i,sd])==int(j) and int(codes[i,sd])==1
    prev=int(t[f]);first=-1;check=0
    for k in range(int(f)+1,int(j)+1):
     if t[k]==t[f]:continue
     assert t[k]-prev<=15000;prev=int(t[k]);liq=int(b[k] if side==1 else a[k])
     assert ((liq>opening-bar) if side==1 else (liq<opening+bar))
     v=liq-entry-20 if side==1 else entry-liq-20
     if v>=100:first=k;check=v;break
    assert first==j and int(net)==check
    verified+=1
 obj={'source':src,'month':mon,'raw_source_sha256':base.r18.PINS[src][mon],
  'five_contracts_complete_quarters':len(q),'five_contracts_complete_hours':len(h),
  'all_new_future_selected_actual_quote_first_touch_independently_verified':verified,
  'original_R19_S3_count_no_regression':True,'C8_stop_is_new_contract_not_original_S1':True,
  'full_equity_profit_and_real_broker_fill_UNVERIFIED':True}
 path=R/'results'/f'{stem}_INDEPENDENT_VERIFICATION.json';path.write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj),flush=True)
 return obj
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True)
 x=p.parse_args();one(x.source,x.month)
