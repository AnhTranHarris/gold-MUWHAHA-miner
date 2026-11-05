"""H9-0002 finite prereg directional horizon variants using original H8+source.
No research winners used as features. Historical, future-selected oracle only.
"""
from __future__ import annotations
import datetime, json, time
import numpy as np
import h9_teacher_january as H

def run():
    t,b,a,signal,fill,ev,stop,censor,ref,q0=H.load()
    early=ev[:,:,0];ad=ev[:,:,1]
    stage=(early>=0)&((ad<0)|(early<ad))&(fill[:,None]>=0)&(stop[:,None]>=0)
    stage &= (censor[:,None]<0)|(early<censor[:,None])
    secs=(t[np.maximum(early,0)]-t[np.maximum(fill[:,None],0)])
    outputs=[]
    for k in (2000,5000,10000,15000):
        allowed=stage & (secs<=k)
        for raw,col in [('TP0300',3),('TP0500',4)]:
            name=f'H9_JAN_FAVORABLE_WITHIN_{k}MS_{raw}_EXIT_LT30'
            out=H.select_teacher(t,b,a,fill,ev,stop,allowed,col,30000,q0,ref,name)
            out['favorable_deadline_ms']=k
            outputs.append(out)
            print(name,out['future_selected_count'],out['hour']['positive_active_ratio'],out['quarter']['positive_active_ratio'],flush=True)
    outp=H.ROOT/'results'/'H9_JAN_0002_EIGHT_DIRECTIONAL_HORIZON_ABLATIONS.json'
    outp.write_text(json.dumps({'status':'HINDSIGHT_ONLY_ONE_MONTH_NOT_CAUSAL','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':outputs},indent=2)+'\n')
    print('DONE',outp)
if __name__=='__main__':run()
