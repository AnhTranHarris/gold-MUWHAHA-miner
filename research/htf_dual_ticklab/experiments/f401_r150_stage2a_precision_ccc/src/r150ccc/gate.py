"""Exact R150Q Stage2A population completeness gate; missing cannot be waived."""
from __future__ import annotations
from pathlib import Path
import hashlib,json

CELLS=tuple(f'{b}_{m}' for b in ('coinexx','dukascopy') for m in ('01','02','06','07'))

def external_evidence_gate(index_file:Path):
    """Rejects Q mask substitutes, absent source/root producer, or missing cells.

    Merely passing this file-structure gate is NOT an attestation of upstream
    source-root independence: an independent root audit is still mandatory.
    """
    index_file=Path(index_file)
    raw=json.loads(index_file.read_text());cells=raw.get('cells',{})
    if set(cells)!=set(CELLS):raise ValueError('all eight ORIGINAL Q veto populations required')
    if raw.get('independent_original_emitter_root_producer_deletion') is not True:
        raise ValueError('full R150H ORIGINAL event-emitter root gate NOT CERTIFIED')
    if raw.get('q_policy')!='R150Q_1PCT_9639_LOSS_FROZEN':
        raise ValueError('unverified/approximate historical R150Q policy')
    if raw.get('forbidden_inference_sources_removed') is not True:
        raise ValueError('transitive original class/teacher/r24/r148b lineage unproven')
    for cell,item in cells.items():
        if any(not isinstance(item.get(k),str) or len(item[k])!=64 for k in
            ('event_identity_sha256','original_q_mask_sha256','market_feature_sha256')):
            raise ValueError('source pins missing '+cell)
        if not item.get('real_t1_t2_action_clock_proved'):
            raise ValueError('independent action-time intent proof missing '+cell)
    return raw
