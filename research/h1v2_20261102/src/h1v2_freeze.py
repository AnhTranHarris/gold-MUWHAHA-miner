"""H1V2 immutable four-month oracle provenance and portable recovery outputs.

Does not rerun a teacher that already has matching raw-source/checkpoint hashes.
Uploads can carry compact exact selected-trade traces without 1GB full teacher
label arrays; full arrays and raw sources must still be retained separately.
"""
from __future__ import annotations
import json, zipfile, hashlib, os, pathlib, math
import numpy as np
from h1v2_teacher import MONTHS,SYNTH,read_ticks,digest

PINNED={
 '01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
 '02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
 '06':'34686ce53ba992dfb83ea35d555b6a4947a9216635853857c8bf11ce70c00ae2',
 '07':'e171e8c2fb59f3f4147a6f845eb68e664fa9c0f4815caa33acdbb42cc2f768b7'
}

def freeze(root='/mnt/data/h1v2/results',raw_root='/mnt/data'):
    root=pathlib.Path(root);raw_root=pathlib.Path(raw_root)
    reports=[];all_trades=0;all_synth=0;tot_ticks=0;tot_candidates=0
    for month in MONTHS:
        rp=root/f'h1v2_dukascopy_{month}_receipt.json'
        doc=json.loads(rp.read_text());p=root/f'h1v2_dukascopy_{month}_oracle_labels.npz'
        raw=raw_root/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
        assert doc['raw_sha256']==PINNED[month] and digest(raw)==PINNED[month]
        assert digest(p)==doc['teacher_labels_sha256']
        with np.load(p,allow_pickle=False) as z:
            entries=z['tick_index'];sel=z['selected_row'];side=z['selected_side'];which=(side==-1).astype(np.int64)
            exit_ix=z['exit_tick_index'][sel,which];net=z['net'][sel,which]
            first=z['first_event_ms'][sel,which]
            assert np.all(z['code'][sel,which]==1) and np.all(np.isfinite(net)) and np.all(net>0)
            assert np.all(first>=0) and np.all(first<=30000)
            if len(sel)>1:assert np.all(entries[sel[1:]]>exit_ix[:-1])
            assert len(sel)==doc['oracle_nonoverlapping']['trades']
            t,b,a=read_ticks(raw)
            assert np.all(z['t']==t[entries])
            v=entries[sel];assert np.all(exit_ix>v)
            out=root/f'h1v2_dukascopy_{month}_selected_exact_trace.npz'
            np.savez_compressed(out,entry_tick_ix=v,entry_utc_ms=t[v],side=side,entry_bid=b[v],entry_ask=a[v],
                        exit_tick_ix=exit_ix,exit_utc_ms=t[exit_ix],exit_bid=b[exit_ix],exit_ask=a[exit_ix],
                        first_favorable_elapsed_ms=first,net=net)
        doc['selected_trace_sha256']=digest(out)
        (root/f'h1v2_dukascopy_{month}_receipt.json').write_text(json.dumps(doc,indent=2))
        reports.append(doc);all_trades+=len(sel);all_synth+=SYNTH[month]
        tot_ticks+=doc['tick_count'];tot_candidates+=doc['unique_250ms_candidates']
    agg={'teacher':'H1V2','status':'SOURCE_EXACT_FUTURE_PRIVILEGED_HINDSIGHT_ONLY',
         'months':list(MONTHS),'raw_ticks':tot_ticks,'eligible_250ms_decisions':tot_candidates,
         'synth_trade_reference':all_synth,'monthly_80pct_floors_sum':sum(math.ceil(.80*SYNTH[x]) for x in MONTHS),
         'oracle_nonoverlapping_correct':all_trades,'oracle_count_vs_synth_ratio':all_trades/all_synth,
         'all_months_exceed_floor':all(x['oracle_count_pass_80pct'] for x in reports),
         'fees_included':'USD $0.02 research fee plus actual Dukascopy quote spread; no slippage',
         'science':'Oracle knows future quote path, cannot act prospectively. No as-of model qualifies at 80%; not a trading strategy.',
         'items':[{k:m[k] for k in ('month','tick_count','unique_250ms_candidates','at_least_one_side_strict_good',
                  'oracle_nonoverlapping','synth_reference','monthly_80pct_floor','raw_sha256','selected_trace_sha256') } for m in reports]}
    (root/'H1V2_FOUR_MONTH_SOURCE_EXACT_REPORT.json').write_text(json.dumps(agg,indent=2))
    return agg
if __name__=='__main__':print(json.dumps(freeze(),indent=2))
