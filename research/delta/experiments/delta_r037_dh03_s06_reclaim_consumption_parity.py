"""DELTA R037 DH03-S06 reclaim-level consumption / pivot-reuse parity — 13G.

Bounded clean-room semantic matrix. No numeric threshold retune.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import delta_r037_dh02_s08_cleanroom_parity as base
import delta_r037_dh03_s06_structure as structure
import delta_r037_dh03_s06_attempt_admission_parity as admission13d
import delta_r037_dh03_s06_reclaim_consumption_engine as engine

FP='a3a086b7344c'
TARGET={'trades':1563,'raw_positive_wins':690,'gross_profit':151.82,'gross_loss':-490.75,'net_profit':-338.93,'max_balance_drawdown':339.25}
PROFILES=(
 'STRICT_CLOSE_BEYOND_CONTROL',
 'INHERITED_FIRST_CLOSE_BEYOND_CONTROL',
 'STRICT_TRUE_EDGE_CROSS',
 'INHERITED_FIRST_TRUE_EDGE_CROSS',
 'STRICT_CONSUME_USED_PIVOT',
 'INHERITED_FIRST_CONSUME_USED_PIVOT',
 'INHERITED_FIRST_EDGE_CROSS_CONSUME',
)

def score(a):
    er={k:abs(a[k]-TARGET[k]) for k in TARGET}
    sc=100*er['trades']+25*er['raw_positive_wins']+er['gross_profit']+er['gross_loss']+er['net_profit']+er['max_balance_drawdown']
    return er,float(sc)

def pack(x,signals,sigsha):
    a={'generator_signals':int(signals),'signal_sha256':sigsha,'trades':int(x[0]),'raw_positive_wins':int(x[1]),'official_wins':int(x[2]),'gross_profit':float(x[3]),'gross_loss':float(x[4]),'net_profit':float(x[5]),'max_balance_drawdown':float(x[6]),'immediate_admissions':int(x[7]),'rejected_while_occupied':int(x[8])}
    er,sc=score(a); return {'actual':a,'abs_error':er,'parity_score':sc}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--evidence',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    ev=json.loads(a.evidence.read_text(encoding='utf-8'))
    if ev.get('schema')!='delta-r037-dh03-s06-reclaim-level-consumption-pivot-reuse-evidence-13g-v1': raise SystemExit('13G evidence schema mismatch')
    sh=base.sha256_file(a.source)
    if sh!=base.CANONICAL_JAN_SHA256: raise SystemExit('canonical January SHA mismatch')
    df=pd.read_csv(a.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64); df=df[df.timestamp_ms_utc<base.STAGE_A_END_MS]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if len(t)!=4_205_709: raise SystemExit(f'Stage-A tick mismatch: {len(t)}')
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64)); mid=ask+bid
    b5=base.bars(t,mid,5_000); b15=base.bars(t,mid,15_000); b30=base.bars(t,mid,30_000); m5=base.bars(t,mid,300_000); m15=base.bars(t,mid,900_000); m30=base.bars(t,mid,1_800_000)
    e5=base.signed_eff(b5,4); e15=base.signed_eff(b15,4); e30=base.signed_eff(b30,4); a5=base.atr14(m5)
    pe,ps,pdir,li,si=structure.parent_series(m15,m30); phi,plo,pht,plt=structure.latest_fast_pivots(b15)
    profiles={}
    for mode,name in enumerate(PROFILES):
        st,ss,se,c=engine.detect(t,mid,b5['end_ms'],b5['close'],e5,b15['end_ms'],b15['high'],b15['low'],b15['close'],e15,b30['end_ms'],e30,m5['end_ms'],a5,pe,ps,li,si,phi,plo,pht,plt,mode)
        sigsha=base.signal_sha(st,ss,se); x=admission13d.admit_attempt_policy(t,ask,bid,st,ss,se,0)
        profiles[name]={'signal_count':int(st.size),'signal_sha256':sigsha,'funnel':{'pullbacks':int(c[0]),'exhaustion':int(c[1]),'reclaim':int(c[2]),'signals':int(c[3]),'rearms':int(c[7]),'inherited_reclaims':int(c[8]),'edge_reclaims':int(c[9]),'consume_blocks':int(c[10]),'pivot_identity_changes_after_consume':int(c[11])},'drop_occupied':pack(x,st.size,sigsha)}
    s=profiles['STRICT_CLOSE_BEYOND_CONTROL']; sa=s['drop_occupied']['actual']
    if not (s['signal_count']==1586 and s['signal_sha256']=='261b6ad5a1cab4dd4378ec40af7fdde4e5178e82694089b3bf2a28bc6bebfdea' and sa['trades']==1513 and sa['raw_positive_wins']==674 and abs(sa['net_profit']+339.14)<1e-8): raise SystemExit('13F strict control drift')
    h=profiles['INHERITED_FIRST_CLOSE_BEYOND_CONTROL']; ha=h['drop_occupied']['actual']
    if not (h['signal_count']==1683 and h['signal_sha256']=='44e53fa1b4a1b186f8522910cc07edd7526ea0f54acac2e80bd3e141146a03f2' and ha['trades']==1610 and ha['raw_positive_wins']==716 and abs(ha['net_profit']+362.29)<1e-8): raise SystemExit('13F inherited control drift')
    candidates=PROFILES[2:]; order=sorted(candidates,key=lambda n:profiles[n]['drop_occupied']['parity_score']); lead=order[0]; q=profiles[lead]['drop_occupied']['actual']
    exact=q['trades']==TARGET['trades'] and q['raw_positive_wins']==TARGET['raw_positive_wins'] and all(abs(q[k]-TARGET[k])<0.011 for k in ('gross_profit','gross_loss','net_profit','max_balance_drawdown'))
    best_parent=min(s['drop_occupied']['parity_score'],h['drop_occupied']['parity_score'])
    material=(profiles[lead]['drop_occupied']['parity_score']<best_parent and abs(q['trades']-TARGET['trades'])<min(abs(sa['trades']-TARGET['trades']),abs(ha['trades']-TARGET['trades'])))
    out={'schema':'delta-r037-dh03-s06-reclaim-level-consumption-pivot-reuse-parity-13g-v1','status':'COMPLETE_EXACT_PARITY' if exact else ('COMPLETE_MATERIAL_RECLAIM_STATE_BREAKTHROUGH_FULL_PARITY_NOT_YET' if material else 'COMPLETE_RECLAIM_STATE_QA_NO_MATERIAL_PARITY_GAIN'),'unit':'R037_DH03_S06_RECLAIM_LEVEL_CONSUMPTION_AND_PIVOT_REUSE_PARITY_RECONSTRUCTION','source_sha256':sh,'stage_a_ticks':int(len(t)),'surface':'DUKAS_COINEXX_LIKE_P75','vector_fingerprint':FP,'numeric_vector_retune':False,'profiles':profiles,'source_candidate_ranking':order,'finding':{'leading_source_candidate':lead,'leading_trade_gap':int(q['trades']-TARGET['trades']),'leading_raw_win_gap':int(q['raw_positive_wins']-TARGET['raw_positive_wins']),'exact_historical_parity':exact,'material_nonexact':material,'target':TARGET,'next':ev['next_if_exact'] if exact else (ev['next_if_material_nonexact'] if material else ev['next_if_negative'])},'august_2026':'SEALED','mql5_authorized':False,'integrated_r037_replay_started':False}
    base.atomic_write_json(a.output,out); print(json.dumps(out['finding'],separators=(',',':')))
if __name__=='__main__': main()
