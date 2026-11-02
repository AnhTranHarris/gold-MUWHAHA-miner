#!/usr/bin/env python3
"""Exact original on-policy unfiltered 60s entry study vs owner acceptance.
Training outputs are OFF-POLICY and must NOT masquerade as executed entries.
"""
from pathlib import Path
import json,math,hashlib
from teacher_60s import hash_file
ROOT=Path('/mnt/data/v2_new_research/sixty')
SYNTH={'01':27980,'02':33523,'06':31801,'07':24382}

def validate(source,month):
 r=json.loads((ROOT/'results'/f'{source}_{month}_full'/'run.json').read_text())
 t=json.loads((ROOT/'teacher'/f'{source}_{month}'/'receipt.json').read_text())
 f=json.loads((ROOT/'models_reachable_3s'/f'{source}_{month}'/'FOLD_RECEIPT.json').read_text())
 aux=json.loads((ROOT/'models_60s_aux'/f'{source}_{month}'/'FOLD_60S_AUX.json').read_text())
 chk=json.loads((ROOT/'models_reachable_3s'/f'{source}_{month}'/'FROZEN_Q85_HELDOUT_DIAGNOSTIC.json').read_text())
 assert r['month']['closed']==t['trades'] and t['net_mismatch']==t['class_mismatch']==0
 trades=r['month']['closed'];floor=math.ceil(.85*SYNTH[month]);m=r['month'];day=r['byday'];weeks=r['byweek']
 def metrics(x):
  n=x['closed'];return {'trades':n,'rate15':x.get('CORRECT15',0)/n if n else None,
           'rate30':x.get('CORRECT30',0)/n if n else None,
           'net':x.get('net_microdollar',0)/1e6,
           'passes_both80':bool(n and x.get('CORRECT15',0)/n>=.80 and x.get('CORRECT30',0)/n>=.80)}
 dy={k:metrics(v) for k,v in day.items()};wk={k:metrics(v) for k,v in weeks.items()}
 cal=[{'id':x['id'],'valid':x['valid'],'best_calibration_precision':max((p['precision'] for p in x['sweep'] if p['selected']),default=None)} for x in f['trials']]
 return {'source':source,'month':month,'raw_source_sha256':t['source_sha256'],
 'complete_trades':trades,'R9_SYNTH_reference':SYNTH[month], 'minimum_trades':floor,'volume_pass_unfiltered':trades>=floor,
 'unfiltered_month':metrics(m), 'unfiltered_days':dy,'unfiltered_weeks':wk,
 'days_pass_80':sum(x['passes_both80'] for x in dy.values()),'days_total':len(dy),
 'weeks_pass_80':sum(x['passes_both80'] for x in wk.values()),'weeks_total':len(wk),
 'teacher_60s_RECONCILIATION':{'class_mismatch':t['class_mismatch'],'net_mismatch':t['net_mismatch'],
 '60s_late_wait_rescue':t['wait_rescue']},
 'walkforward_calibration':cal,'research_policy_approved':False,
 'three_class_check_auc_correct':f['heldout']['auc_correct'],
 'check_auc_reachable_WAIT':f['heldout']['auc_wait_rescue'],
 'q85_calibrated_off_policy':chk,
 'auxiliary_60s_valid_calibration':aux['selected_earlier_calibration'] is not None,
 'models_on_policy_promoted':False,
 'scientific_status':'UNFILTERED_VOLUME_PASS; SURVIVAL_AND_NET_FAIL; ALL_STUDENTS_REJECTED'}

if __name__=='__main__':
 all=[]
 for s in ('coinexx','dukascopy'):
  for m in ('01','02','06','07'):all.append(validate(s,m))
 out=ROOT/'results'/'FULL_EIGHT_TRAINING_ACCEPTANCE.json'
 out.write_text(json.dumps({'source_months':all,'all_complete_real_ticks':True,'all_class_and_net_reconciled':True,
  'trade_volume_pass_count':sum(z['volume_pass_unfiltered'] for z in all),
  'trade_survival_pass_count':sum(z['unfiltered_month']['passes_both80'] for z in all),
  'approved_students':0,'on_policy_trained_policy_evaluation':'NONE_CALIBRATED_FAIL_CLOSED'},indent=2))
 for z in all:
  print(z['source'],z['month'],'trades',z['complete_trades'],'floor',z['minimum_trades'],
    '15/30',round(z['unfiltered_month']['rate15']*100,2),round(z['unfiltered_month']['rate30']*100,2),
    'net',round(z['unfiltered_month']['net'],2),'days80',z['days_pass_80'],'/',z['days_total'])
 print('ALL_COMPLETE',len(all))
