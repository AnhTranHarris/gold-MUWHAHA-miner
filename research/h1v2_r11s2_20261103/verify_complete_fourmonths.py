"""Source-exact no-summary, all nine policies x four months S2 replay audit."""
from __future__ import annotations
import pathlib,hashlib,json,math
import numpy as np
import pandas as pd
R=pathlib.Path('/mnt/data/h1v2_r11_s2_full_month')
L=pathlib.Path('/mnt/data/h1v2_r11_lab/survival/full_population')
ORIGINAL_SOURCE_SHA={'01':'eba04f81252000349ff999f7452584bdbfc1ff43d1eda678a7f64b10bbcbcb1a','02':'43ca82b635e1f0cfe58253eaab8f5f02dbe2301469835964e8a2a8459924393c','06':'62fa8124fc1611a404f91d44bac65f2b0acd237eada7b8bb32add0607a3493bf','07':'abbf9c302e686fa2aca856412e5f5831104dd51decc5fcefa0c4cc548cbef949'}
SOURCE_FILE={'01':'source_history/R11S2_JAN_FIT_V01_EXACT_SOURCE.py','02':'source_history/R11S2_FEB_FIT_AND_REPLAY_EVAL_V02.py','06':'source_history/R11S2_JUNE_FIT_AND_EVAL_V03.py','07':'src/train_entry_survival.py'}
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report={'name':'R11S2_FOUR_MONTH_INDEPENDENT_FULL_SCORING_TRAINING_REPLAY_AUDIT','status':'SOURCE_RECHECKED_FOUR_MONTHS_WITHIN_MONTH_FIT_AND_FULL_SOURCE_SCORING_NOT_OOS','source_months':{},'all_four_scored_complete':False,'all_nine_policies_per_month_verified':False,'scored_only_not_profit_or_exit':True,'source_files_version_pinned':SOURCE_FILE}
for m in ('01','02','06','07'):
 fp=R/SOURCE_FILE[m]
 if sha(fp)!=ORIGINAL_SOURCE_SHA[m]:raise ValueError('fit source hash drift '+m)
 zfile=L/f'month_{m}'/f'R11S_{m}_ALL_V5_CANDIDATE_H15_H30_EXACT_SURVIVAL_LABELS.npz'
 mrec=json.loads((L/f'month_{m}'/f'R11S_{m}_FULL_SOURCE_LABEL_MANIFEST.json').read_text())
 if sha(zfile)!=mrec['full_population_sha256']:raise ValueError('label source SHA drift '+m)
 with np.load(zfile,allow_pickle=False) as z:
  ix=z['source_tick_ordinal'].copy();t=z['entry_utc_ms'].copy();cov=z['h15_coverage']&z['h30_coverage'];
  buy=np.where(z['h30_BUY_survives_no_adverse'],np.where(z['h15_BUY_survives_and_favorable'],2,1),0).astype(np.uint8)
  sell=np.where(z['h30_SELL_survives_no_adverse'],np.where(z['h15_SELL_survives_and_favorable'],2,1),0).astype(np.uint8)
 p_buy=R/'models'/f'R11S2_{m}_BUY_COMPLETE_FIT_RECEIPT.json';p_sell=R/'models'/f'R11S2_{m}_SELL_COMPLETE_FIT_RECEIPT.json'
 modelrecs={side:json.loads((R/'models'/f'R11S2_{m}_{side}_COMPLETE_FIT_RECEIPT.json').read_text()) for side in ('BUY','SELL')}
 scores={}
 for side,rec in modelrecs.items():
  if rec['code_file_sha256']!=ORIGINAL_SOURCE_SHA[m]:raise ValueError('source pin wrong '+m+side)
  if rec['eligible_rows']!=len(ix) or rec['all_source_month_rows_scored']!=len(ix) or rec['train_rows_actual']!=400000:raise ValueError('train/score population mismatch')
  if rec['exact_full_label_sha256']!=mrec['full_population_sha256']:raise ValueError('train label drift')
  if sha(R/'models'/rec['model_file'])!=rec['model_sha256']:raise ValueError('model SHA drift')
  if sha(R/'models'/rec['full_month_pgood_file'])!=rec['full_month_pgood_sha256']:raise ValueError('score SHA drift')
  scores[side]=np.load(R/'models'/rec['full_month_pgood_file'],mmap_mode='r')
 z=json.loads((R/'replay'/f'R11S2_{m}_FULLSOURCE_IN_SAMPLE_15S30S_RANKING_RECEIPT.json').read_text())
 if z['full_250ms_source_rows']!=len(ix) or len(z['policies'])!=9:raise ValueError('missing results')
 allpol=[]
 for key,v in z['policies'].items():
  f=R/'replay'/v['trace_file'];
  if sha(f)!=v['trace_sha256']:raise ValueError('trace SHA drift')
  with np.load(f,allow_pickle=False) as tr:
   tidx=tr['entry_tick_ordinal'];tt=tr['entry_utc_ms'];ss=tr['BUY_side'];c=tr['hindsight_class'];ce=tr['source_censor'];sc=tr['training_only_candidate_score']
   if not len(tidx)==v['selected_nonoverlap_30s']:raise ValueError('trade count mismatch')
   if len(tt)>1 and not np.all(np.diff(tt)>30000):raise ValueError('trade overlap')
   loc=np.searchsorted(ix,tidx)
   if len(loc) and ((loc>=len(ix)).any() or not np.array_equal(ix[loc],tidx) or not np.array_equal(t[loc],tt)):raise ValueError('original ordinal mismatch')
   if not np.array_equal(c,np.where(ss,buy[loc],sell[loc])):raise ValueError('class join error')
   if not np.array_equal(ce,~cov[loc]):raise ValueError('censor join error')
   if not np.allclose(sc,np.maximum(scores['BUY'][loc],scores['SELL'][loc]),rtol=0,atol=1e-7):raise ValueError('score join error')
   good=int(((c==2)&~ce).sum());neu=int(((c==1)&~ce).sum());bad=int(((c==0)&~ce).sum());censored=int(ce.sum())
   if (good,neu,bad,censored)!=(v['survive30_and_favorable15'],v['survive30_without_favorable15'],v['adverse30'],v['censored_unscored']):raise ValueError('evaluation result misaggregation '+m+key)
  if len(v['per_active_day_all'])==0 or len(v['per_iso_week_all'])==0:raise ValueError('missing full calendars')
  if sum(x['entries'] for x in v['per_active_day_all'])!=len(tidx) or sum(x['entries'] for x in v['per_iso_week_all'])!=len(tidx):raise ValueError('calendar count drift')
  allpol.append({k:v[k] for k in ('fraction','candidate_signals','selected_nonoverlap_30s','survive30_and_favorable15','survive30_without_favorable15','adverse30','censored_unscored','strict_goal_rate_on_completed','synth_85pct_floor','synth_85pct_volume_pass','zero_active_source_days','zero_active_source_iso_weeks','active_days_below_80pct_goal','active_weeks_below_80pct_goal','trace_sha256')})
 selected=next((v for v in allpol if v['synth_85pct_volume_pass']),None)
 report['source_months'][m]={'raw_source_sha256':mrec['source_raw_sha256'],'full_entry_candidate_rows':len(ix),
  'source_model_training_script':str(fp.relative_to(R)),'source_model_training_script_sha256':sha(fp),
  'full_source_15_30_label_sha256':mrec['full_population_sha256'],
  'fit_receipts':modelrecs,'all_9_policy_receipts_source_exact':allpol,
  'first_month_volume_qualified_policy':selected,
  'entire_source_month_evaluated':True,'each_per_day_and_iso_week_calendar_reconciled':True,
  'source_bound_30sec_ordinal_trades_verified':True}
 print('VERIFIED',m,'training 400000 per side / scoring',len(ix),'policies',len(allpol),'first monthly quota', selected['fraction'],selected['selected_nonoverlap_30s'],'strict',selected['strict_goal_rate_on_completed'],flush=True)
report['all_four_scored_complete']=len(report['source_months'])==4
report['all_nine_policies_per_month_verified']=all(len(v['all_9_policy_receipts_source_exact'])==9 for v in report['source_months'].values())
report['source_sha256']=sha(__file__)
p=R/'R11S2_FOUR_MONTH_FULL_SOURCE_RANKING_VERIFICATION_20261103.json';p.write_text(json.dumps(report,indent=2))
print('COMPLETE',p,len(report['source_months']),'model_count',8,'replayed_policies',36,flush=True)
