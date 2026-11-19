#!/usr/bin/env python3
"""January AR1-R6: Atlas-led full-account risk observer and source-exact self-proof.

READ-ONLY historical research. R9 immutable entry/exit/book outcomes; Coinexx REAL quotes
for price-path evidence; owner-frozen S100 as a price-distance reference. NO orders,
entry filters, shadow stops, hypothetical P&L or overwritten source datasets.

R5 held-day score is the ONLY predictive claim; full-January fitted R5 scores are not
substituted for the six January warm-up days. All 27,980 historical rows remain.
"""
from __future__ import annotations
from pathlib import Path
import json, zipfile, gzip, hashlib, time
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, confusion_matrix
from ar1_january_integrated_policy import HistoricalR9BookObserver, TradeRiskObservation

ROOT=Path('/mnt/data')
R5=ROOT/'AR1_JAN_R5_MECHANISM_FIRST_20261118'
R1=ROOT/'AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip'
R2=ROOT/'AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118'
OUT=ROOT/'AR1_JAN_R6_ACCOUNT_RISK_INTEGRATED_20261118'
OUT.mkdir(parents=True,exist_ok=True)
START=time.monotonic()
STEP=((100,4),(700,5),(1100,9),(16200,11),(19900,14),(27500,15),(29300,23),(33200,24),(33300,30),(340100,74))

def gap_for(book_cents:int)->int:
    balance_tier=max(100,100*(int(book_cents)//10000))
    g=4
    for threshold,gap in STEP:
        if balance_tier>=threshold:g=gap
    return 100*g

def safe_metrics(y,p):
    if not len(y):return {'n':0}
    result={'n':len(y),'R9_negative':int(y.sum()),'baseline_R9_negative_rate':float(y.mean()),'AP':float(average_precision_score(y,p)),'Brier':float(brier_score_loss(y,p))}
    if 0<y.sum()<len(y):result['ROC_AUC']=float(roc_auc_score(y,p))
    return result

def rec(x):return x.item() if isinstance(x,np.generic) else x

with zipfile.ZipFile(R1) as z:
    with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as fh:
        d=pd.read_csv(fh)
    manifest=json.load(z.open('JAN_RESEARCH_AUDIT_RECEIPT.json'))
r5 = pd.read_csv(R5/'JAN_ALL_27980_SOURCE_EXACT_RISK_OBSERVER_REAL_TICK_PYTHON_SELFPROOF.csv.gz')
model = pd.read_csv(R5/'JAN_STRICT_PREENTRY_27980_POLICY_SCORES.csv.gz')
feat = pd.read_csv(R5/'JAN_STRICT_PREENTRY_MODEL_FEATURES.csv.gz', usecols=[
 'gross_1m_to_book','gross_5m_to_book','gross_60m_to_book','gross_240m_to_book','gross_1440m_to_book',
 'R9_asof_HWM_drawdown_pct','previous_3_realized_loss_count','previous_5_realized_loss_count',
 'book_tie_ambiguity','mean_spread60_USD','quotes10','quotes60','quote_staleness_ms',
 'micro5s_ha_body_atr_side','micro15s_ha_body_atr_side','micro1s_fib_retrace',
 'secondleg_HA5_HA15_Fib1_protection','firstleg_fib1_depth_HA15_flip'])
assert len(d)==len(r5)==len(model)==len(feat)==27980
assert d.source_row.equals(r5.source_row) and d.source_row.equals(model.source_row)
assert d.source_row.is_unique and (d.net_cents==r5.original_R9_net_cents).all()
assert d.net_cents.sum()==4152082 and d.book_before_cents.iloc[0]==10000 and d.book_after_cents.iloc[-1]==4162082
assert (10000+np.r_[0,np.cumsum(d.net_cents.to_numpy(np.int64)[:-1])]==d.book_before_cents.to_numpy(np.int64)).all()
assert (d.book_before_cents+d.net_cents==d.book_after_cents).all()
assert all(gap_for(int(b))==int(g) for b,g in zip(d.book_before_cents,d.frozen_s100_gap_cents))
assert (d.frozen_s100_gap_cents==r5.original_s100_gap_cents).all()
assert d.leg.isin([1,2]).all()
assert ((d.net_cents>0).sum(),(d.net_cents<0).sum(),(d.net_cents==0).sum()) == (24368,3606,6)

# Absolute R9 booked account state comes from the full unmodified chronological ledger.
book_before=d.book_before_cents.to_numpy(np.int64);book_after=d.book_after_cents.to_numpy(np.int64)
previous_HWM=np.maximum.accumulate(np.r_[10000,book_after[:-1]])
original_exit_sec=(pd.to_datetime(d.exit_time_broker,utc=True).astype('int64')//1_000_000_000).to_numpy(np.int64)
original_entry_ms=(pd.to_datetime(d.entry_time_broker,utc=True).astype('int64')//1_000_000).to_numpy(np.int64)
assert np.array_equal(original_entry_ms, r5.original_fixed_entry_ms.to_numpy(np.int64)-1000)
# These are account research statistics, not simulated Coinexx broker equity.
book_dd_cents=np.maximum(0,previous_HWM-book_before)
book_dd_ratio=book_dd_cents/np.maximum(1,previous_HWM)
loss=np.maximum(0,-d.net_cents.to_numpy(np.int64))
# Closed trade intensity strictly from previously closed R9 trade outcomes.
prior_loss_run=np.zeros(len(d),dtype=np.int16)
for i in range(1,len(d)):
    # When prior exit shares the next entry second, causality is ambiguous: do not use it as known.
    if original_exit_sec[i-1]>=original_entry_ms[i]//1000:
        prior_loss_run[i]=0
    else:
        j=i-1; count=0
        while j>=0 and original_exit_sec[j]<original_entry_ms[i]//1000 and d.net_cents.iloc[j]<0:
            count+=1;j-=1
        prior_loss_run[i]=count

p=model.clean_asof_HA_Fib_mechanism_interactions_oof.to_numpy(float)
held=np.isfinite(p)
assert held.sum()==21069 and int((d.net_cents.to_numpy()[held]<0).sum())==2637
is_loss=d.net_cents.to_numpy()<0
book_signal=(book_dd_cents>0)
cluster_signal=(prior_loss_run>=2)
# The release is a telemetry vector. p>=.5 below is a diagnostic review cutoff only;
# it is NEVER used for a trading decision or to update original booked balance.
loss_score_flag=held & (p>=0.5)
observed_dd=r5.real_Coinexx_peak_to_trough_DD_cents.to_numpy(float)
winquote=r5.real_Coinexx_inside_window_quote_count.to_numpy(int)
strict=(r5.quote_quality_strict.to_numpy(bool))
known=winquote>0
assert (known==(np.isfinite(observed_dd))).all()
assert (~known).sum()==33
u25=r5.Coinexx_u25_first_observed_quote_ms.to_numpy(np.int64)
u50=r5.Coinexx_u50_first_observed_quote_ms.to_numpy(np.int64)
u75=r5.Coinexx_u75_first_observed_quote_ms.to_numpy(np.int64)
u90=r5.Coinexx_u90_first_observed_quote_ms.to_numpy(np.int64)
assert np.all((u50<0)|(u25>=0)) and np.all((u75<0)|(u50>=0))

# Complete observational January risk-vector schema. Nothing in this table changes the R9 source fields.
ledger=pd.DataFrame({
 'source_row':d.source_row.to_numpy(),
 'cycle_id':d.cycle_id.to_numpy(),
 'original_R9_entry_time':d.entry_time_broker.to_numpy(),
 'original_R9_exit_time':d.exit_time_broker.to_numpy(),
 'original_R9_immutable_entry_ms':original_entry_ms,
 'original_R9_net_cents':d.net_cents.to_numpy(np.int64),
 'original_R9_book_before_cents':book_before,
 'original_R9_book_after_cents':book_after,
 'R9_book_prior_HWM_cents':previous_HWM,
 'R9_book_preentry_drawdown_cents':book_dd_cents,
 'R9_book_preentry_drawdown_pct':book_dd_ratio*100,
 'R9_prior_consecutive_booked_losses':prior_loss_run,
 'R9_preentry_gross_negative_1m_to_book':feat.gross_1m_to_book.to_numpy(float),
 'R9_preentry_gross_negative_5m_to_book':feat.gross_5m_to_book.to_numpy(float),
 'R9_preentry_gross_negative_60m_to_book':feat.gross_60m_to_book.to_numpy(float),
 'R9_preentry_gross_negative_240m_to_book':feat.gross_240m_to_book.to_numpy(float),
 'R9_preentry_gross_negative_1440m_to_book':feat.gross_1440m_to_book.to_numpy(float),
 'S100_gap_cents_FROZEN':d.frozen_s100_gap_cents.to_numpy(np.int64),
 'R9_leg_known_at_entry':d.leg.to_numpy(np.int8),
 'R9_side_known_at_entry':d.side.to_numpy(),
 'atlas_atomic_family_RETROSPECTIVE_ONLY':d.atomic.to_numpy(),
 'atlas_parent_family_RETROSPECTIVE_ONLY':d.family.to_numpy(),
 'R9_profitable_leg_RETROSPECTIVE_ONLY':(d.net_cents.to_numpy()>0),
 'R9_positive_complete_cycle_leg_RETROSPECTIVE_ONLY':d.protected_R9_positive_cycle.to_numpy(bool),
 'AR1_R5_loss_probability_held_day_chronological':p,
 'AR1_R5_training_status':np.where(held,'EARLIER_JAN_DAYS_TRAINED','JAN_WARMUP_NO_CAUSAL_JAN_TRAINING'),
 'AR1_R5_loss_review_p_ge_0_5_OBSERVATION_ONLY':loss_score_flag,
 'AR1_booked_prior_under_HWM':book_signal,
 'AR1_prior_closed_loss_cluster_ge_2_OBSERVATION_ONLY':cluster_signal,
 'AR1_micro_preentry_mean_spread60_USD':feat.mean_spread60_USD.to_numpy(float),
 'AR1_micro_preentry_quotes10':feat.quotes10.to_numpy(float),
 'AR1_micro_preentry_quotes60':feat.quotes60.to_numpy(float),
 'AR1_micro_preentry_quote_age_ms':feat.quote_staleness_ms.to_numpy(float),
 'AR1_micro_preentry_HA5_strength':feat.micro5s_ha_body_atr_side.to_numpy(float),
 'AR1_micro_preentry_HA15_strength':feat.micro15s_ha_body_atr_side.to_numpy(float),
 'AR1_micro_preentry_Fib1_retrace':feat.micro1s_fib_retrace.to_numpy(float),
 'AR1_HA_Fib_secondleg_protection_interaction':feat.secondleg_HA5_HA15_Fib1_protection.to_numpy(float),
 'AR1_HA_Fib_firstleg_retrace_flip_interaction':feat.firstleg_fib1_depth_HA15_flip.to_numpy(float),
 'AR1_Coinexx_inside_window_quotes':winquote,
 'AR1_Coinexx_anchor_both_strict':strict,
 'AR1_Coinexx_exact_path_status':np.where(~known,'NO_OBSERVED_INSIDE_QUOTE',np.where(strict,'OBSERVED_STRICT','OBSERVED_TIMING_EXCEPTION')),
 'AR1_Coinexx_quote_MFE_cents':r5.real_Coinexx_MFE_cents.to_numpy(float),
 'AR1_Coinexx_quote_MAE_cents':r5.real_Coinexx_MAE_cents.to_numpy(float),
 'AR1_Coinexx_quote_peakDD_cents':observed_dd,
 'AR1_Coinexx_DD_over_original_book_pct':observed_dd/np.maximum(1,book_before)*100,
 'AR1_Coinexx_observed_S100_utilization':observed_dd/np.maximum(1,d.frozen_s100_gap_cents.to_numpy()),
 'AR1_Coinexx_first_u25_msc':u25,
 'AR1_Coinexx_first_u50_msc':u50,
 'AR1_Coinexx_first_u75_msc':u75,
 'AR1_Coinexx_first_u90_msc':u90,
 'AR1_R9_account_tie_time_ambiguous':feat.book_tie_ambiguity.to_numpy(float)>0,
 'AR1_trade_action':np.full(len(d),'NONE_OBSERVATIONAL_ONLY'),
})
# Full R9 historical booked chronology and protected cycles unaltered.
assert (ledger.original_R9_net_cents.to_numpy()==d.net_cents.to_numpy()).all()
assert np.all(ledger.AR1_trade_action=='NONE_OBSERVATIONAL_ONLY')
assert ledger.AR1_Coinexx_exact_path_status.eq('NO_OBSERVED_INSIDE_QUOTE').sum()==33
ledger.to_csv(OUT/'JAN_R6_ALL_27980_INTEGRATED_ACCOUNT_RISK_OBSERVER.csv.gz',compression='gzip',index=False)

# Fresh full raw Coinexx Python stress replay: every January original tick, quote-side
# liquidation path and all S100 event transition stamps (not a simulated stop).
pinned=manifest['pinned_original_Coinexx_tick_archives_sha256']
replayed=[];days=[];integrated_states=[]
runtime_book=HistoricalR9BookObserver()
for day, idxs in d.groupby(d.entry_time_broker.str[:10],sort=True):
    src=ROOT/f'R9_REAL_{day}_ticks.csv.gz'
    sha=hashlib.sha256(src.read_bytes()).hexdigest()
    assert sha==pinned[src.name],f'Original source hash mismatch {src}'
    ticks=pd.read_csv(src,compression='gzip',usecols=['run_label','time_msc','bid','ask'])
    assert ticks.run_label.eq('REAL').all()
    msc=ticks.time_msc.to_numpy(np.int64)
    bid=np.rint(ticks.bid.to_numpy(float)*100).astype(np.int64)
    ask=np.rint(ticks.ask.to_numpy(float)*100).astype(np.int64)
    assert (np.diff(msc)>=0).all() and (ask>=bid).all()
    held_quotes=0;previous_original_close=-1
    for i,tr in idxs.iterrows():
        entry=int(tr.open_ms);end=int(tr.close_ms)
        left=int(np.searchsorted(msc,max(entry,previous_original_close),side='right' if entry<=previous_original_close else 'left'))
        right=int(np.searchsorted(msc,end,side='right'))
        tm=msc[left:right]
        q=(bid[left:right] if tr.side=='buy' else -ask[left:right])
        # Actual read-only account state machine, fed all original entries/exits in order.
        pre_book_dd=runtime_book.start(tr.book_before_cents,tr.frozen_s100_gap_cents)
        assert pre_book_dd==book_dd_cents[i]
        pos=TradeRiskObservation(
            source_row=int(tr.source_row),side=str(tr.side),
            true_entry_second_ms=int(original_entry_ms[i]),
            observed_quote_window_entry_ms=int(tr.open_ms),
            observed_quote_window_exit_ms=int(tr.close_ms),
            gap_cents=int(tr.frozen_s100_gap_cents),
            booked_hwm_drawdown_cents=pre_book_dd,
            previous_closed_loss_run=int(prior_loss_run[i]),
            prior_60m_gross_loss_to_book=float(feat.gross_60m_to_book.iloc[i]),
            strictly_prior_entry_loss_probability=(float(p[i]) if held[i] else None))
        pos.observe_exact_window_quote_sequence(tm,bid[left:right],ask[left:right])
        n=len(q);held_quotes+=n
        if n:
            dd=np.maximum.accumulate(q)-q
            if tr.side=='buy':marks=bid[left:right]-ask[left]
            else:marks=bid[left]-ask[left:right]
            mf=int(max(0,marks.max()));ma=int(max(0,-marks.min()));pk=int(dd.max())
            assert n==tr.quote_count and mf==tr.observed_MFE_cents and ma==tr.observed_MAE_cents and pk==tr.observed_peakDD_cents
            crossing={}
            for label,frac in [('u25',.25),('u50',.50),('u75',.75),('u90',.90),('full',1.)]:
                match=np.flatnonzero(dd>=tr.frozen_s100_gap_cents*frac)
                crossing[label]=int(tm[match[0]]) if len(match) else -1
        else:
            assert tr.quote_count==0
            crossing={s:-1 for s in ['u25','u50','u75','u90','full']}
            mf=ma=pk=None
        assert crossing['u25']==u25[i] and crossing['u50']==u50[i] and crossing['u75']==u75[i] and crossing['u90']==u90[i]
        assert crossing['full']<0
        assert (pos.quote_count,pos.observed_mfe_cents,pos.observed_mae_cents,pos.observed_peak_dd_cents)==(n,mf,ma,pk)
        assert (pos.first_u25_ms,pos.first_u50_ms,pos.first_u75_ms,pos.first_u90_ms,pos.first_full_touch_ms)==(crossing['u25'],crossing['u50'],crossing['u75'],crossing['u90'],crossing['full'])
        integrated_states.append(pos.state_at_end(strict_anchor=bool(tr.strict),ambiguous_prior_exit=bool(feat.book_tie_ambiguity.iloc[i])))
        replayed.append({'source_row':int(tr.source_row),'time_first_observed_u25_ms':crossing['u25'],
                         'time_first_observed_u50_ms':crossing['u50'],'time_first_observed_u75_ms':crossing['u75'],
                         'time_first_observed_u90_ms':crossing['u90'], 'time_first_full_S100_ms':crossing['full'],
                         'quote_count':n,'mae_cents':ma,'mfe_cents':mf,'DD_cents':pk,
                         'first_u25_seconds_before_source_fixed_exit':round((int(tr.close_ms)-crossing['u25'])/1000,3) if crossing['u25']>=0 else None,
                         'first_u50_seconds_before_source_fixed_exit':round((int(tr.close_ms)-crossing['u50'])/1000,3) if crossing['u50']>=0 else None})
        runtime_book.record_original_fixed_exit(tr.net_cents,tr.book_after_cents)
        pos.original_exit_processed=True
        previous_original_close=end
    days.append({'day':day,'source_sha256':sha,'all_real_tick_quotes':len(msc),'R9_trades':len(idxs),'quotes_in_original_R9_windows':held_quotes})
    print('JAN_R6_PY_SOURCE_DAY',day,'ticks',len(msc),'original_trades',len(idxs),flush=True)
    del ticks,msc,bid,ask
RP=pd.DataFrame(replayed)
assert len(RP)==27980 and RP.source_row.equals(d.source_row)
assert runtime_book.completed==27980 and runtime_book.book_cents==4162082 and runtime_book.sum_net_cents==4152082
states=pd.DataFrame(integrated_states)
assert len(states)==27980 and states.source_row.equals(d.source_row)
assert states.trade_action.eq('NONE_OBSERVATIONAL_ONLY').all()
assert states.observed_S100_u25.sum()==930 and states.observed_S100_u50.sum()==110
states.to_csv(OUT/'JAN_R6_POLICY_RUNTIME_STATE_MACHINE_REPLAY.csv.gz',compression='gzip',index=False)
assert sum(x['all_real_tick_quotes'] for x in days)==7699274
assert sum(x['quotes_in_original_R9_windows'] for x in days)==2272602
assert (RP.time_first_full_S100_ms<0).all()
RP.to_csv(OUT/'JAN_R6_ALL_27980_REAL_TICK_EVENT_TIMES.csv.gz',compression='gzip',index=False)

# Full-cycle protection: count complete successful cycles, not just individual positive legs.
cy=d.groupby('cycle_id',sort=False).agg(net_cents=('net_cents','sum'),legs=('source_row','count'))
assert len(cy)==19775
protected_cycles=cy.net_cents>0
pos_in_cycle=d.cycle_id.map(protected_cycles).to_numpy(bool)
assert pos_in_cycle.sum()==int(d.protected_R9_positive_cycle.sum())==26148
negative_in_positive=int(((d.net_cents<0)&pos_in_cycle).sum())

# Account-risk diagnosis at January key Atlas source-row targets and market stress periods.
w=pd.read_csv(R2/'JAN_ATLAS_WITNESS_MATCHED_CONTROL_MAP.csv')
assert len(w)==240 and set(w.target_row).issubset(set(d.source_row))
K=ledger.set_index('source_row',drop=False)
K['R6_loss_prob_review_ge05']=K.AR1_R5_loss_review_p_ge_0_5_OBSERVATION_ONLY
K['R6_Coinexx_observed_u25']=K.AR1_Coinexx_first_u25_msc.ge(0)
K['R6_Coinexx_observed_u50']=K.AR1_Coinexx_first_u50_msc.ge(0)
K['R6_R9_historical_win']=K.R9_profitable_leg_RETROSPECTIVE_ONLY
for col in ['AR1_R5_loss_probability_held_day_chronological','R6_loss_prob_review_ge05','R6_Coinexx_observed_u25','R6_Coinexx_observed_u50','R9_book_preentry_drawdown_cents','AR1_prior_closed_loss_cluster_ge_2_OBSERVATION_ONLY','AR1_Coinexx_exact_path_status','R6_R9_historical_win']:
    w['target_'+col]=w.target_row.map(K[col])
    w['matched_control_'+col]=w.control_row.map(K[col])
w.to_csv(OUT/'JAN_R6_ATLAS_240_WITNESS_INTEGRATED_POLICY_STRESS.csv',index=False)

# Exhaustive 27 parent/atomic family × 10 ladder levels; parent rows overlap atomic rows.
fm=[]
for fam in list(sorted(d.atomic.unique()))+['PARENT_A','PARENT_B','PARENT_C','PARENT_D']:
    select=(d.family==fam[-1]) if fam.startswith('PARENT_') else (d.atomic==fam)
    for step,gap in STEP:
        idx=np.where(select & (d.frozen_s100_gap_cents.to_numpy()==gap*100))[0]
        seen=idx[held[idx]];alert=seen[p[seen]>=0.5]
        fm.append({'family_line':fam,'overlapping_parent':fam.startswith('PARENT_'),'frozen_s100_gap_usd':gap,
                   'all_original_R9_trades':len(idx),'original_R9_profitable_legs':int((d.net_cents.iloc[idx]>0).sum()),
                   'original_R9_losing_legs':int((d.net_cents.iloc[idx]<0).sum()),
                   'original_R9_booked_gross_negative_usd':round(float(loss[idx].sum())/100,2),
                   'max_original_book_HWM_drawdown_usd':float(book_dd_cents[idx].max()/100) if len(idx) else None,
                   'max_observed_Coinexx_MAE_usd':float(np.nanmax(r5.real_Coinexx_MAE_cents.iloc[idx])/100) if len(idx) and np.isfinite(r5.real_Coinexx_MAE_cents.iloc[idx]).any() else None,
                   'max_observed_Coinexx_MFE_usd':float(np.nanmax(r5.real_Coinexx_MFE_cents.iloc[idx])/100) if len(idx) and np.isfinite(r5.real_Coinexx_MFE_cents.iloc[idx]).any() else None,
                   'max_observed_Coinexx_DD_usd':float(np.nanmax(observed_dd[idx])/100) if len(idx) and np.isfinite(observed_dd[idx]).any() else None,
                   'no_quote_count':int((winquote[idx]==0).sum()),
                   'chronological_scored_earlier_day_count':len(seen),'p_ge05_diagnostic_alerts':len(alert),
                   'p_ge05_alerted_R9_losers':int(is_loss[alert].sum()),
                   'p_ge05_alerted_profitable_R9_legs':int((d.net_cents.iloc[alert]>0).sum()),
                   'observed_Coinexx_25pct_S100_count':int((u25[idx]>=0).sum()),
                   'observed_Coinexx_50pct_S100_count':int((u50[idx]>=0).sum())})
family_tier=pd.DataFrame(fm)
assert len(family_tier)==270
assert int(family_tier.loc[~family_tier.overlapping_parent,'all_original_R9_trades'].sum())==27980
family_tier.to_csv(OUT/'JAN_R6_27_FAMILIES_X_10_FROZEN_S100_POLICY_STRESS.csv',index=False)

# No look-ahead control: only chronologically earlier-day-fitted R5 scores are evaluated.
scored_idx=np.where(held)[0]
LOSS=p[held]>=.5
C=pd.DataFrame({'source_row':d.source_row.iloc[scored_idx], 'actual_losing_R9':is_loss[held],
                'p':p[held],'review_p05':LOSS,'original_net_cents':d.net_cents.iloc[scored_idx],
                'book_under_prior_hwm':book_signal[held],'prior_book_loss_cluster_ge2':cluster_signal[held],
                'u25_observed':u25[held]>=0,'u50_observed':u50[held]>=0,
                'family':d.atomic.iloc[scored_idx], 'leg':d.leg.iloc[scored_idx],
                'gap':d.frozen_s100_gap_cents.iloc[scored_idx]/100,
                'day':d.entry_time_broker.iloc[scored_idx].str[:10]})
conditions={
 'all_chronologically_scored_trades':np.ones(len(C),dtype=bool),
 'first_leg':C.leg.eq(1).to_numpy(),
 'second_leg':C.leg.eq(2).to_numpy(),
 'preentry_R9_book_underwater':C.book_under_prior_hwm.to_numpy(),
 'preentry_R9_consecutive_loss_cluster_ge2':C.prior_book_loss_cluster_ge2.to_numpy(),
 'Coinexx_observed_quarter_S100_pressure':C.u25_observed.to_numpy(),
 'Coinexx_observed_half_S100_pressure':C.u50_observed.to_numpy(),
 'Jan29_30_actual_shock_days':C.day.isin(['2026-01-29','2026-01-30']).to_numpy(),
 'original_protected_R9_net_positive_cycle':pos_in_cycle[held],
}
strata=[]
for name,mask in conditions.items():
    Z=C.iloc[np.flatnonzero(mask)]
    yy=Z.actual_losing_R9.to_numpy(bool)
    hi=Z.review_p05.to_numpy(bool)
    strata.append({'stress_stratum':name,'n':len(Z),'losses':int(yy.sum()),'profitable_legs':int((Z.original_net_cents>0).sum()),
       'observational_high_loss_alerts':int(hi.sum()),'high_alert_R9_losses':int((hi&yy).sum()),
       'high_alert_original_winners_collision':int((hi&(Z.original_net_cents>0)).sum()),
       'loss_recall_within_stratum':float((hi&yy).sum()/yy.sum()) if yy.sum() else None,
       'diagnostic_probability_AP':float(average_precision_score(yy,Z.p)) if yy.any() else None,
       'source_original_positive_book_net_usd':round(float(Z.original_net_cents[Z.original_net_cents>0].sum())/100,2)})
stress=pd.DataFrame(strata);stress.to_csv(OUT/'JAN_R6_INTEGRATED_ACCOUNT_POLICY_STRESS_STRATA.csv',index=False)

# Chronology condition labels, not a proof of risk reduction through a trade-altering intervention.
heldtrue=is_loss[held];held_p=p[held];train=~held
p05=held_p>=.5
positive_collision=(held & (p>=.5)&(d.net_cents.to_numpy()>0))
positive_collided_net=float(d.net_cents.to_numpy()[positive_collision].sum())/100
# Sensitive high-variance evidence strata; report separately, no balancing artificially.
regimes={}
for gap in [4,5,9,11,14,15,23,24,30,74]:
 mask=(d.frozen_s100_gap_cents.to_numpy()==gap*100)
 valid=mask&held
 regimes[str(gap)]={'all_original_R9_trades':int(mask.sum()),'chronological_scored_count':int(valid.sum()),
                    'historical_positive':int(((d.net_cents>0)&mask).sum()),
                    'historical_losing':int(((d.net_cents<0)&mask).sum()),
                    'predictive_precision_if_scored':float(((p>=.5)&is_loss&valid).sum()/max(1,((p>=.5)&valid).sum())) if valid.any() else None,
                    'no_inside_window_quotes':int(((winquote==0)&mask).sum()),
                    'u50_observed':int(((u50>=0)&mask).sum())}

# Stress diagnostics about missingness and time, not fabricated quote paths.
entry_gap=(r5.original_fixed_entry_ms.to_numpy(np.int64)-original_entry_ms)
assert (entry_gap==1000).all()
# No last recorded quote can be after original fixed exit in actual fixed-window observer.
for label,arr in [('u25',u25),('u50',u50),('u75',u75),('u90',u90)]:
    assert np.all((arr<0)|((arr>=r5.original_fixed_entry_ms.to_numpy(np.int64))&(arr<=r5.original_fixed_exit_ms.to_numpy(np.int64))))

# Reproducibility source custody, robust output receipts.
files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.glob('*') if f.is_file() and f.suffix in ('.csv','.gz')}
result={
 'status':'INTEGRATED_JAN_R6_OBSERVATIONAL_ACCOUNT_RISK_FULL_SOURCE_STRESS_PASSED; TRADE_ALTERING_CAPITAL_PROTECTION_NOT_CERTIFIED',
 'source_contract':'R9 SYNTH original booked accounting/fixed trades + Coinexx REAL TickLogger quote paths; original S100 frozen',
 'original_trades':len(d),'original_R9_total_net_USD':float(net:=d.net_cents.sum()/100),'original_R9_book_start_USD':100.0,'original_R9_book_end_USD':41620.82,
 'original_R9_profitable_legs':int((d.net_cents>0).sum()),'original_R9_losing_legs':int((d.net_cents<0).sum()),
 'original_R9_positive_complete_cycles':int(protected_cycles.sum()),'legs_in_original_positive_cycles':int(pos_in_cycle.sum()),
 'negative_legs_inside_original_positive_cycles':negative_in_positive,
 'source_exact_original_Coinexx_REAL_quotes_read':int(sum(x['all_real_tick_quotes'] for x in days)),
 'source_exact_actual_quotes_inside_R9_fixed_windows':int(sum(x['quotes_in_original_R9_windows'] for x in days)),
 'count_MFE_MAE_DD_mismatches_vs_preserved_R1_R5':0,
 'integrated_running_book_statemachine_reconciled':True,
 'integrated_quote_pressure_state_machine_reconciled':True,
 'original_no_inside_quote_windows':int((winquote==0).sum()), 'original_window_quote_timing_exceptions':int((known&~strict).sum()),
 'S100_reference_ladder_all_27980_reconciles':True,
 'observed_u25_trades':int((u25>=0).sum()),'observed_u50_trades':int((u50>=0).sum()),'observed_u75_trades':int((u75>=0).sum()),
 'observed_u90_trades':int((u90>=0).sum()),'observed_full_S100_touches':0,
 'R5_model_strict_entry_held_day_scored_trades':int(held.sum()),'R5_model_earliest_days_untrained_trades':int(train.sum()),
 'R5_held_day_earlier_train_loss_AP':safe_metrics(heldtrue,held_p),
 'R5_p05_diagnostic_alert_count':int(p05.sum()),
 'R5_p05_original_R9_losing_alerts':int((p05&heldtrue).sum()),
 'R5_p05_original_R9_profitable_collisions':int(positive_collision.sum()),
 'R5_p05_original_profitable_booked_net_USD_in_alerted_legs_DESCRIPTIVE_NOT_COUNTERFACTUAL':round(positive_collided_net,2),
 'R5_p05_alerts_that_are_profitable_complete_cycle_legs':int(((held&(p>=.5))&pos_in_cycle).sum()),
 'original_book_hwm_underwater_at_entry_count':int(book_signal.sum()),
 'original_prior_consecutive_R9_loss_run_ge2_count':int(cluster_signal.sum()),
 'original_same_second_prior_exit_next_entry_ambiguous_count':int((feat.book_tie_ambiguity>0).sum()),
 'atlas_240_witness_rows_checked':int(len(w)),'atlas_27_families_by_10_S100_levels':int(len(family_tier)),
 'all_original_trades_unchanged':True,'all_original_exit_times_unchanged':True,'all_original_booked_results_unchanged':True,
 'no_R9_positive_trade_filtered':True,'no_trade_action_in_integrated_policy':True,
 'jan_early_S100_gap_4_5_no_prior_trained_predictor':True,
 'no_broker_equity_or_counterfactual_execution_claim':True,
 'source_days':days,'regimes_by_S100_gap':regimes,'small_derived_output_sha256':files,
 'runtime_sec':round(time.monotonic()-START,2)
}
(OUT/'JAN_R6_INTEGRATED_STRESS_TEST_RECEIPT.json').write_text(json.dumps(result,indent=2))
print('JAN_R6_FULL_INTEGRATED_SELF_PROOF',json.dumps({k:v for k,v in result.items() if k not in ('source_days','regimes_by_S100_gap','small_derived_output_sha256')},indent=2),flush=True)
