"""H11-MT5 preregistered full original Coinexx-linked January historical quote source transfer.
Original R26 UTC and H8 labels frozen. Nondeployable hindsight only, not dealer fill.
"""
import json,datetime,time
import h9_teacher_jan_dual_feed as H
from h11_exclusive_direction_teacher import stage_at,exclusive
import numpy as np

def run():
 assert H.SOURCE=='MT5_BROKER_EXPORT', 'call with MT5_BROKER_EXPORT argument'
 s=time.monotonic();t,b,a,signal,fill,ev,stop,censor,ref,q0=H.load()
 out={'classification':'H11_FULL_JAN_COINEXX_LINKED_MT5_ORIGINAL_QUOTE_EXCLUSIVE_FIRST_SIDE_FUTURE_TEACHER_NOT_LIVE_CASH', 'source_sha256':H.PIN,'H8_source_archive_sha':H.sha_file(H.H8ZIP),'n_asof_candidates':len(signal),'n_source_events':len(t),'r9_original_synth_ref':int(ref.sum()),'UTC_offset_correction_hours':2,'source':'MT5_BROKER_EXPORT','month':'01','cases':[],'prereg':'https://drive.google.com/file/d/1-vxk3mJlnTnikqEwqZwz3p5PlmiByVC1/view'}
 for ms in (2000,5000,15000):
  stage=stage_at(t,fill,ev,stop,censor,ms)
  exc=exclusive(ev[:,:,0],stage)
  assert not np.any(exc.sum(1)>1)
  name=f'H11_MT5_BROKER_JAN_FIRST{ms//1000:02d}S_EXCLUSIVE_DIRECTION_TP0300_EXIT_LT30'
  report=H.select_teacher(t,b,a,fill,ev,stop,exc,3,30000,q0,ref,name)
  # Inherited generic source helper ALREADY uses a broker-specific SOURCE suffix.
  # H11-MT5-F01 corrected only this new wrapper's redundant rename assumption.
  suffix=H.ROOT/'results'/(name+'_MT5_BROKER_EXPORT_01_ORIGINAL_SOURCE_QUOTE_ORDINALS.npz')
  assert suffix.exists(), 'MISSING ORIGINAL MT5 QUOTE-ORDINAL SOURCE RECEIPT'
  report['original_full_source_population']={'both_independent_stage_sides_true':int(np.count_nonzero(stage.all(1))),'exclusive_side_signal_candidates':int(exc.sum()),'nonexclusive_side_rejections':int(len(signal)-np.count_nonzero(exc.any(1)))}
  out['cases'].append(report)
  print('MT5_H11_EXCLUSIVE_CASE',ms,report['future_selected_count'],report['day']['positive_active_periods'],report['hour']['positive_active_periods'],report['quarter']['positive_active_periods'],report['hour']['volume_quota_active_periods'],flush=True)
 out['elapsed_seconds']=round(time.monotonic()-s,2);out['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 p=H.ROOT/'results'/'H11_MT5_BROKER_FULL_JAN_ALL_UTC_EXCLUSIVE_FIRST_DIRECTION_SOURCE_REPORT.json';p.write_text(json.dumps(out,indent=2)+'\n')
 print('MT5_H11_COMPLETE',str(p),json.dumps({'source':out['source'],'n_original_source_events':out['n_source_events'],'case_counts':[x['future_selected_count'] for x in out['cases']]}),flush=True)
if __name__=='__main__':run()
