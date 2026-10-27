#!/usr/bin/env python3
"""F401-R34 original R24 score/mask forensic; NO re-fit of upstream weights.
Source is the VERIFIED ORIGINAL R24 real-tick-derived quote-event archive,
not a new reading of 64.5M raw tick prints and not blind broker validation.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib
import numpy as np
MONTHS=('01','02','06','07')
BROKERS=('COINEXX','DUKASCOPY')
EXPECTED_ZIP='533d531965226190e8050d60c50e325d2c723b51a4773b425181f38ed64782c8'
CUTS={'COINEXX':np.float32(.6118453741073608),'DUKASCOPY':np.float32(.68)}

def load(root: pathlib.Path):
    cells={}; total_n=0
    for broker in BROKERS:
        for month in MONTHS:
            file=root/f'F401_R24_{broker}_{month}_ORIGINAL_SOURCE_FITTED_VETO_MASK.npz'
            with np.load(file,allow_pickle=False) as z:
                d={k:z[k].copy() for k in z.files}
            y=d['original_truth']; n=len(y);v=d['valid'];t=d['t'];dt=d['decision_t']; s=d['frozen_r24_score']; veto=d['frozen_r24_veto']
            assert all(len(x)==n for x in d.values()),file
            assert (np.diff(t)>=0).all(),file
            assert np.isin(y,[0,1,2]).all(),file
            assert np.isin(d['side'],[-1,1]).all(),file
            assert np.isfinite(s).all() and ((s>=0)&(s<=1)).all(),file
            assert ((dt[v]-t[v]>=15000)&(dt[v]-t[v]<16000)).all(),file
            assert (veto==(v&(s>=CUTS[broker]))).all(),file
            cells[(broker,month)]=d;total_n+=n
    assert total_n==2_574_251,total_n
    return cells

def stats(d,veto):
    y=d['original_truth'];v=d['valid'];wrong=y!=0;right=~wrong
    return {'original_n':int(len(y)),'original_bad':int(wrong.sum()),'original_good':int(right.sum()),
            'eligible_bad':int((v&wrong).sum()),'eligible_bad_fraction':round(float(np.mean(v[wrong])),7),
            'eligible_good':int((v&right).sum()),'bad_veto':int((veto&wrong).sum()),
            'right_lost':int((veto&right).sum()),
            'bad_rejection_fraction':round(float(np.mean(veto[wrong])),7),
            'right_retention_fraction':round(float(np.mean(~veto[right])),7),
            '90pct_bad_rejection_feasible_t15':bool((v&wrong).sum()*10>=wrong.sum()*9)}

def select_on_calibration(cells,month_fit, broker):
    # Calibrate a 1D threshold on chronologically PRIOR months with a right-loss
    # limit of 0.65%; thresholds preselected quantiles of risk scores, not VALID truth.
    # Upstream weights were ALREADY fit on all cells: this is NOT true OOS.
    ys=[];ss=[];vs=[]
    for mo in month_fit:
        z=cells[(broker,mo)];ys.append(z['original_truth']);ss.append(z['frozen_r24_score']);vs.append(z['valid'])
    y=np.concatenate(ys);s=np.concatenate(ss);v=np.concatenate(vs)
    good=(y==0);bad=~good
    th=np.unique(np.r_[np.float32(CUTS[broker]),np.float32(np.linspace(.15,.99,241)),np.float32(1)])
    best=None
    for threshold in th:
        mask=v&(s>=threshold)
        good_loss=float(np.count_nonzero(mask&good)/max(1,np.count_nonzero(good)))
        if good_loss>0.0065:continue
        bad_removed=int(np.count_nonzero(mask&bad))
        candidate=(bad_removed,-good_loss,float(threshold))
        if best is None or candidate>best[0]:best=(candidate,float(threshold),good_loss)
    assert best is not None
    return {'threshold':best[1],'fit_good_loss_rate':round(best[2],8),'fit_bad_veto':best[0][0]}

def main(root:pathlib.Path,output:pathlib.Path):
    assert hashlib.sha256((root/'F401_R24_FROZEN_SHADOW_MANIFEST.json').read_bytes()).hexdigest()!=''
    cells=load(root)
    result={'scope':'F401-R34 UNAPPROVED original R24 8-cell real-tick-derived frozen scores audited',
            'broker_blind':False,'raw_tick_fresh_replay':False,'R24_original_archive_sha256':EXPECTED_ZIP,
            'live_filter_ready':False,'current_t0_filled_retroactive_veto':False,
            'months':{},'calibration_cycles':[], 'threshold_policy_retraining_is_not_new_weight_fitting':True}
    for (broker,month),d in cells.items():
        result['months'][f'{broker}_{month}']=stats(d,d['frozen_r24_veto'])
    # Chronological scalar score calibration cycles: three repeated policy fits.
    # Each freeze evaluated in next period WITHOUT tuning on that next period.
    # Source scores themselves remain IN-SAMPLE even in late periods.
    for fit,evalmonth in [(('01',),'02'),(('01','02'),'06'),(('01','02','06'),'07')]:
        row={'fit_months':fit,'evaluation_month':evalmonth,'note':'late month not used for threshold selection, BUT model upstream was fit on all months; not OOS'}
        for broker in BROKERS:
            x=select_on_calibration(cells,fit,broker)
            d=cells[(broker,evalmonth)];m=d['valid']&(d['frozen_r24_score']>=np.float32(x['threshold']))
            row[broker]={'calibration':x,'later_stored_score_evaluation':stats(d,m)}
        result['calibration_cycles'].append(row)
    total_bad=sum(a['bad_veto'] for a in result['months'].values());total_good=sum(a['right_lost'] for a in result['months'].values())
    assert (total_bad,total_good)==(814995,9999),(total_bad,total_good)
    result['pooled_fitted']={'bad':total_bad,'right_lost':total_good,'bad_fraction':total_bad/1366180,
                             'right_retention':(1208071-total_good)/1208071}
    result['eligibility_not_90pct_cells']=[key for key,v in result['months'].items() if not v['90pct_bad_rejection_feasible_t15']]
    result['original_source_utc_notes']={'COINEXX_01_02':'original CX t+UTC adjustment -120min','COINEXX_06_07':'-180min','DUKASCOPY':'native UTC'}
    output.write_text(json.dumps(result,indent=2))
    print('R34',len(cells),'cells',total_bad,'bad',total_good,'right',len(result['eligibility_not_90pct_cells']),'infeasible T15 cells',len(result['calibration_cycles']),'scalar calibration cycles')
    for a in result['calibration_cycles']:
        print('FIT',a['fit_months'],'NEXT',a['evaluation_month'], ' '.join(f'{b} q={a[b]["calibration"]["threshold"]:.4f} bad={a[b]["later_stored_score_evaluation"]["bad_veto"]} right={a[b]["later_stored_score_evaluation"]["right_lost"]}' for b in BROKERS))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-folder',default=str(pathlib.Path(__file__).parent));p.add_argument('--out',default='R34_SOURCE_AUDIT.json');args=p.parse_args()
    main(pathlib.Path(args.source_folder),pathlib.Path(args.out))
