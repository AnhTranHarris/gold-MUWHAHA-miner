"""R20 read-only original-gzip SHA, full eight source-month calendar and selected ordinal verifier.
No future quote forecast validation: this is strict archival/instrumentation proof only.
"""
from pathlib import Path
import sys,csv,json,hashlib
import numpy as np
ROOT=Path('/mnt/data');LAB=ROOT/'h1v2_r20_last46'
sys.path.insert(0,str(LAB/'src'))
import r20_residual_quote_hazard as r
NQUARTERS={'01':2976,'02':2688,'06':2880,'07':2976}

def read(path):
 with open(path,newline='') as f:return list(csv.DictReader(f))

def prove_one(source,mon):
 t,b,a,_,_,_,pr=r.get_frozen(source,mon)
 rr=r.r18.refs_for_month(mon,ROOT);qrefs=rr['qref'];href=rr['href'];keys=rr['qkeys']
 o,e,base,missing=r.get_old(source,mon,t,rr)
 stem=f'R20_{source}_{mon}';dir=LAB/'results'
 rp=dir/f'{stem}_ALL_SOURCE_SCENARIOS.csv'; qp=dir/f'{stem}_ALL_UTC_15MIN_SCENARIOS.csv';hp=dir/f'{stem}_ALL_UTC_HOURS_SCENARIOS.csv';npzp=dir/f'{stem}_ALL_SOURCE_CANDIDATE_DUAL_ACTION_AND_ADDED_WINNER_ORDINALS.npz'
 src=read(rp);qs=read(qp);hs=read(hp)
 assert len(src)==len(r.SCENARIOS)==6
 assert len(qs)==6*NQUARTERS[mon] and len(hs)==6*(NQUARTERS[mon]//4)
 if int(href.sum())!=int(qrefs.sum()):raise AssertionError('ORIGINAL_REFERENCE_DRIFT')
 with np.load(npzp,allow_pickle=False) as z:
  for arow in src:
   name=arow['scenario'];qrows=[d for d in qs if d['scenario']==name];hrows=[d for d in hs if d['scenario']==name]
   assert len(qrows)==len(qrefs) and len(hrows)==len(href)
   orig_q=np.array([int(x['R19S3_existing_future_winners']) for x in qrows]);new_q=np.array([int(x['R20_added_future_winners']) for x in qrows]);total=np.array([int(x['R20_total_future_winners']) for x in qrows])
   assert np.array_equal(orig_q,base) and np.array_equal(total,orig_q+new_q)
   assert np.array_equal(np.array([int(x['R9_SYNTH_ref']) for x in qrows]),qrefs)
   assert int(arow['additional_packed_future_winning_positions'])==int(new_q.sum())
   assert int(arow['new_R20_15m_met'])==int(np.count_nonzero((qrefs>0)&(total>=qrefs)))
   assert int(arow['new_R20_hours_met'])==int(np.count_nonzero((href>0)&(total.reshape(-1,4).sum(axis=1)>=href)))
   assert np.array_equal(np.array([int(x['R20_total_future_winners']) for x in hrows]),total.reshape(-1,4).sum(axis=1))
   assert np.array_equal(np.array([int(x['R9_SYNTH_hour_ref']) for x in hrows]),href)
   fill=z[name+'__added_fill_quote_ordinal'];exitord=z[name+'__added_firstTP_exit_quote_ordinal'];sig=z[name+'__added_source_signal_ordinal'];side=z[name+'__added_future_selected_side']; net=z[name+'__added_nominal_net_raw'];
   assert len(fill)==len(exitord)==len(sig)==len(side)==len(net)==new_q.sum()
   assert np.array_equal(np.bincount(t[fill]//900000-keys[0],minlength=len(qrefs)),new_q)
   assert np.all(t[exitord]>t[fill]) and np.all(t[fill]>=t[sig]+int(arow['lag_ms']))
   assert np.all(t[fill]-(t[sig]+int(arow['lag_ms']))<=1000)
   assert np.all((a[sig]-b[sig])<=int(arow['source_cap_raw_0p001']))
   assert np.all((a[fill]-b[fill])<=int(arow['fill_cap_raw_0p001']))
   assert np.all((t[exitord]-t[fill])<=int(arow['first_touch_horizon_ms']))
   assert np.all(net>=100)
   if len(fill)>1:assert np.all(t[fill[1:]]>t[exitord[:-1]])
   if len(fill):
    allstart=np.r_[t[o],t[fill]];allend=np.r_[t[e],t[exitord]];idx=np.argsort(allstart,kind='stable')
    assert np.all(allstart[idx][1:]>allend[idx][:-1])
   for s0,f0,j0,sd,pnl in zip(sig,fill,exitord,side,net):
    # Independently observe all raw integer bid/ask revisions from fill to exit.
    assert int(j0)>int(f0)
    opening=int(b[f0] if sd==1 else a[f0]);entry=int(a[f0] if sd==1 else b[f0]);slip=int(arow['extra_slip_per_leg_raw_0p001']);entry+=(slip if sd==1 else -slip)
    prev=int(t[f0]);first=-1
    for j in range(int(f0)+1,int(j0)+1):
     if t[j]==t[f0]:continue
     if t[j]-prev>15000:raise AssertionError('ADDED_WIN_GAP_BEFORE_EXIT')
     prev=int(t[j]);liq=int(b[j] if sd==1 else a[j]);v=(liq-entry-20-slip) if sd==1 else (entry-liq-20-slip)
     if (sd==1 and liq<=opening-100) or (sd==-1 and liq>=opening+100):raise AssertionError('ADVERSE_BEFORE_TP')
     if v>=100:first=j;break
    assert first==j0 and int(pnl)==v
  data={'source':source,'month':mon,'raw_sha':r.r18.PINS[source][mon],
   'source_original_quote_records':len(t),'quarter_rows':len(qs),'hour_rows':len(hs),'scenarios':len(src),
   'source_contract_reconciled':True,'selected_new_winner_quotes_independently_first_passage_verified':int(sum(int(x['additional_packed_future_winning_positions']) for x in src)),
   'original_R19S3_baseline_quotas_unchanged':True,'no_source_future_asof_validation':True}
  return data

def run():
 allrows=[];checks=[]
 for src in ('DUKASCOPY_RAW','MT5_BROKER_EXPORT'):
  for mon in ('01','02','06','07'):
   d=prove_one(src,mon);allrows.append(d);checks.append(d['source_contract_reconciled']);print(json.dumps(d),flush=True)
 proof={'research':'R20 FULL CALENDAR STRICT EVIDENCE INDEPENDENT REPLAY','all_eight_sources_pass':all(checks),
  'sources':allrows,'total_calendar_quarter_rows':sum(x['quarter_rows'] for x in allrows),
  'total_calendar_hour_rows':sum(x['hour_rows'] for x in allrows),
  'new_selected_verifications':sum(x['selected_new_winner_quotes_independently_first_passage_verified'] for x in allrows),
  'no_actual_broker_cash_or_COINEXX_LIVE_VERIFICATION':True}
 p=LAB/'R20_FULL_EIGHT_SOURCE_INDEPENDENT_REPLAY_RECEIPT.json';p.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(proof,indent=2),flush=True)
 return proof
if __name__=='__main__':run()
