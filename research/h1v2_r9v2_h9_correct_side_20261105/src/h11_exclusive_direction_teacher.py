"""H11 exclusive first-direction HINDSIGHT TEACHER. Preregistered, quote ordinal exact.
First side is a future label, NEVER a live feature or BUY/SELL causal action.
"""
from __future__ import annotations
import json,time,datetime
import numpy as np
import h9_teacher_january as H

def exclusive(first,side_stage):
    assert first.ndim==2 and first.shape[1]==2 and first.shape==side_stage.shape
    # First *favorable mid event* winner is unique (ties no first). First raw quote order is preserved.
    other=first[:,::-1]
    return side_stage & (first>=0) & ((other<0)|(first<other))

def stage_at(t,fill,ev,stop,censor,ms):
    early=ev[:,:,0];adverse=ev[:,:,1]
    first=(early>=0)&((adverse<0)|(early<adverse))&(fill[:,None]>=0)&(stop[:,None]>=0)
    first&=(t[np.maximum(early,0)]-t[np.maximum(fill[:,None],0)]<=ms)
    first&=((censor[:,None]<0)|(early<censor[:,None]))
    return first

def run():
    start=time.monotonic();t,b,a,signal,fill,ev,stop,censor,ref,q0=H.load()
    early=ev[:,:,0];info={'classification':'FULL_JAN_SOURCE_EXACT_HINDSIGHT_EXCLUSIVE_INITIAL_DIRECTION_ONLY','source_raw_sha':H.PIN,'source_H8_sha':H.sha_file(H.H8ZIP),'original_signals':len(signal),'orig_ref':int(ref.sum()),'prereg':'https://drive.google.com/file/d/1ry3ODYXD29uaP84fPFiWWtP3f03cDsuJ/view','case_metrics':[]}
    for ms in (2000,5000,15000):
        stage=stage_at(t,fill,ev,stop,censor,ms)
        ex=exclusive(early,stage)
        assert not np.any(np.all(ex,axis=1)), 'EXCLUSIVE SIDE CONTRACT FAILURE'
        assert np.all(ex<=stage)
        rejected_both=int(np.count_nonzero(np.all(stage,axis=1)))
        no_unique=int(np.count_nonzero(np.sum(ex,axis=1)==0))
        name=f'H11_DUKAS_JAN_FIRST{ms//1000:02d}S_EXCLUSIVE_DIRECTION_TP0300_EXIT_LT30'
        st=H.select_teacher(t,b,a,fill,ev,stop,ex,3,30000,q0,ref,name)
        st['initial_direction_purity']={'stage_both_sides_eligible':rejected_both,'no_qualifying_exclusive_side':no_unique,'unique_side_signal_count':int(ex.sum()),'percentage_unique_side':float(ex.sum()/len(signal)), 'stage_side_pairs':int(stage.sum()),'no_post_entry_future_online':True}
        print('H11_EXCLUSIVE_CASE',ms,json.dumps({'future_selected':st['future_selected_count'],'hour':st['hour'],'quarter':st['quarter'],'day':st['day'],'stage':st['initial_direction_purity']}),flush=True)
        info['case_metrics'].append(st)
    info['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();info['elapsed_s']=round(time.monotonic()-start,3)
    p=H.ROOT/'results'/'H11_EXCLUSIVE_FIRST_SIDE_FULL_JAN_ALL_UTC_AND_SOURCE_ORDINALS.json';p.write_text(json.dumps(info,indent=2)+'\n')
    return info

if __name__=='__main__':run()
