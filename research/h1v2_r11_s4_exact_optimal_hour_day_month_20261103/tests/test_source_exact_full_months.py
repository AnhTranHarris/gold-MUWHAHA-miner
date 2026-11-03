"""R11S4 exact full-four-month forensic regression, on preserved binary input."""
import glob, hashlib, io, json, pathlib, zipfile
import numpy as np
import pandas as pd
import pytest
from hour_quota_oracle import load_month, greedy_all, greedy_day_upper, greedy_from_start, MONTHS, SOURCE_SHAS

ROOT=pathlib.Path('/mnt/data/r11_s4')
EXPECT={'01':(4012834,35652,27980,480,430,26,22),
        '02':(3076349,33640,33523,458,307,24,16),
        '06':(4173378,40296,31758,497,470,26,26),
        '07':(4038891,35813,24324,482,464,26,24)}

def reader(m):
 base=ROOT/f'month_{m}'
 j=json.load(open(base/f'R11S4_{m}_EXACT_COMPLETE_RESULT.json'))
 h=pd.read_csv(base/f'R11S4_{m}_ALL_UTC_HOURS.csv')
 d=pd.read_csv(base/f'R11S4_{m}_ALL_UTC_DAYS.csv')
 with np.load(base/f'R11S4_{m}_FULL_SELECTED_SOURCE_TRACE.npz') as zz:
  tr={k:zz[k].copy() for k in zz.files}
 return j,h,d,tr

@pytest.mark.parametrize('m',MONTHS)
def test_source_zip_and_manifest_source_exact(m):
 d=load_month(m); assert d['archive_sha']==SOURCE_SHAS[m]
 assert d['original_candidate_count']==EXPECT[m][0]
 assert np.all(np.diff(d['t'])>=0) and len(d['t'])==d['good_event_count']
 assert np.all(np.isin(d['side'],[-1,1]))
 assert d['good_event_count']>EXPECT[m][1]

@pytest.mark.parametrize('m',MONTHS)
def test_complete_future_known_trade_trace_original_membership(m):
 source=load_month(m); report,hrs,days,trace=reader(m)
 orig=source['row'];want=trace['source_candidate_row']
 i=np.searchsorted(orig,want)
 assert np.array_equal(orig[i],want)
 assert np.array_equal(trace['entry_utc_ms'],source['t'][i])
 assert np.array_equal(trace['source_tick_ordinal'],source['tick'][i])
 assert np.array_equal(trace['side'],source['side'][i])
 assert np.array_equal(trace['entry_side_margin_raw'],source['margin'][i])
 assert len(want)==EXPECT[m][1]
 assert np.all(trace['reservation_ms']==30000)
 assert np.all(trace['full15_favorable_and_full30_survival'])
 assert np.all(np.diff(trace['entry_utc_ms'])>30000)  # across all hour and UTC day boundaries

@pytest.mark.parametrize('m',MONTHS)
def test_clock_aligned_hour_complete_day_complete_quota_and_optimality(m):
 report,hrs,days,tr=reader(m)
 c,p,q,nhr,hpass,nd,dp=EXPECT[m]
 assert report['R9_SYNTH_clock_corrected_month_total']==q
 assert report['new_hour_target_beam_positions']==p
 assert report['hourly_quota_passed']==hpass
 assert report['daily_volume_quota_passed']==dp
 assert report['hourly_quota_optimistic_upper_possible']==hpass
 assert report['daily_quota_optimistic_upper_possible']==dp
 assert report['monthly_full_R9_SYNTH_quota_met']
 assert int(hrs.R9_SYNTH_UTC.sum())==q
 assert int(hrs.R11S4_HOUR_QUOTA_BEAM_ENTRIES.sum())==p
 assert int(days.R9_SYNTH_UTC.sum())==q
 assert int(days.R11S4_HINDSIGHT_ENTRIES.sum())==p
 assert int((hrs.R9_SYNTH_UTC>0).sum())==nhr
 assert int((days.R9_SYNTH_UTC>0).sum())==nd
 assert len(hrs) in (744,672,720) and len(days) in (31,28,30)
 assert int(hrs.hour_mathematically_impossible.sum())==nhr-hpass
 assert np.all(hrs.R11S4_HOUR_QUOTA_BEAM_ENTRIES<=hrs.R11S3_INDEPENDENT_HOUR_CROSSING_UPPER)
 assert np.all(days.R11S4_HINDSIGHT_ENTRIES<=days.R11S4_INDEPENDENT_DAY_OPTIMISTIC_UPPER)
 assert int((days.R11S4_DAY_PROVEN_IMPOSSIBLE==1).sum())==nd-dp
 assert int(hrs.R11S4_HINDSIGHT_ENTRY_GOOD15_SURVIVE30.sum())==p
 assert report['runtime_prediction_accuracy_claim'] is False
 assert report['economic_profit_not_objective'] is True
 assert report['holding_exit_mechanisms_unchanged'] is True
 # Count every actual UTC day and hour, including inactive R9 timestamps.
 perday=hrs.groupby('utc_day',sort=True)[['R9_SYNTH_UTC','R11S4_HOUR_QUOTA_BEAM_ENTRIES']].sum()
 assert np.array_equal(perday.R9_SYNTH_UTC.to_numpy(),days.R9_SYNTH_UTC.to_numpy())
 assert np.array_equal(perday.R11S4_HOUR_QUOTA_BEAM_ENTRIES.to_numpy(),days.R11S4_HINDSIGHT_ENTRIES.to_numpy())

@pytest.mark.parametrize('m',MONTHS)
def test_independent_month_hour_day_upper_bound_recalculated(m):
 src=load_month(m);t=src['t'];nxt=np.searchsorted(t,t+30000,side='right')
 report,hours,days,trace=reader(m)
 original_max=len(greedy_all(t,nxt))
 assert original_max==report['original_maxcount_hindsight_positions']==report['new_hour_target_beam_positions']
 start=pd.to_datetime(hours.utc_hour,utc=True).astype('int64').to_numpy()//10**6
 lo=np.searchsorted(t,start);hi=np.searchsorted(t,start+3600000)
 hourind=np.array([len(greedy_from_start(t,nxt,int(a),int(b))) if a<b else 0 for a,b in zip(lo,hi)])
 assert np.array_equal(hourind,hours.R11S3_INDEPENDENT_HOUR_CROSSING_UPPER.to_numpy())
 dayupper=np.array([len(greedy_day_upper(t,nxt,int(lo[i]),int(hi[i+23]))) for i in range(0,len(lo),24)])
 assert np.array_equal(dayupper,days.R11S4_INDEPENDENT_DAY_OPTIMISTIC_UPPER.to_numpy())
 assert sum((hours.R9_SYNTH_UTC>0)&(hourind>=hours.R9_SYNTH_UTC))==report['hourly_quota_passed']
 assert sum((days.R9_SYNTH_UTC>0)&(dayupper>=days.R9_SYNTH_UTC))==report['daily_volume_quota_passed']

@pytest.mark.parametrize('m',MONTHS)
def test_csv_trace_matches_exact_nonoverlap_npz(m):
 report,hours,days,tr=reader(m)
 csvt=pd.read_csv(ROOT/f'month_{m}'/f'R11S4_{m}_FULL_SELECTED_SOURCE_TRACE.csv')
 assert len(csvt)==len(tr['entry_utc_ms'])
 assert np.array_equal(csvt.source_candidate_row.to_numpy(),tr['source_candidate_row'])
 assert np.array_equal(csvt.source_tick_ordinal.to_numpy(),tr['source_tick_ordinal'])
 assert np.array_equal(csvt.entry_utc_ms.to_numpy(),tr['entry_utc_ms'])
 assert np.array_equal(csvt.side.to_numpy(),tr['side'])
 assert np.array_equal(csvt.safety_margin_raw.to_numpy(),tr['entry_side_margin_raw'])
 assert (csvt.strict15fav30surv==1).all()
 assert int(csvt.entry_UTC_hour.nunique())>200
