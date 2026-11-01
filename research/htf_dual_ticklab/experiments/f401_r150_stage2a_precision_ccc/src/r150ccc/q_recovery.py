"""Research-only frozen R150Q mask recovery; never substitutes Q2, R150W, or R148B.

Requires original eight F395 per-event arrays, a separately authenticated frozen
R150Q 1% eight-cell archive, independent source-emitter/root proof and true
T1/T2 first-native-quote time/intent witnesses. This module checks consistency;
it cannot grant authenticity to its own claimed proof objects.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from contextlib import ExitStack
import hashlib, io, json, zipfile
import numpy as np

CELLS=tuple(f'{b}_{m}' for b in ('coinexx','dukascopy') for m in ('01','02','06','07'))
EXPECTED_COUNTS={'events':2574251,'correct':1208071,'opposite':1064545,
                 'neutral':301635,'q_bad':234507,'q_correct_lost':9639}
Q_COLUMNS=('ordinal','t0_ms','side','q_t1_veto','q_t2_veto','has_native_t1',
           't1_ms','q_t1_decision_ms','has_native_t2','t2_ms',
           'pending_t1','pending_t2')

@dataclass(frozen=True)
class RecoveryResult:
    status:str
    cells:dict
    totals:dict
    blocker:str|None


def digest(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4<<20),b''):h.update(b)
    return h.hexdigest()


def _read_npz(zip_obj:zipfile.ZipFile,name:str):
    with np.load(io.BytesIO(zip_obj.read(name)),allow_pickle=False) as f:
        return {k:f[k].copy() for k in f.files}



def _validate_clock_arrays(k:str,a:dict,o:dict)->dict:
    """Pure check of ONE source-exact original Q clock vector. Testable without Q archive."""
    if not set(Q_COLUMNS).issubset(a):raise ValueError('Q original clock columns missing '+k)
    if not(np.array_equal(a['ordinal'],o['original_index']) and np.array_equal(a['t0_ms'],o['t'])
           and np.array_equal(a['side'],o['side'])):
        raise ValueError('Q mask original t/side/ordinal join mismatch '+k)
    n=len(o['t']);t0=o['t'];t1=a['t1_ms'];t2=a['t2_ms'];q1=a['q_t1_veto'];q2=a['q_t2_veto']
    if any(len(a[col])!=n for col in Q_COLUMNS):raise ValueError('Q original length mismatch '+k)
    if any(a[col].dtype!=np.bool_ for col in ('q_t1_veto','q_t2_veto','has_native_t1','has_native_t2','pending_t1','pending_t2')):
        raise ValueError('nonbinary Q eligibility '+k)
    if np.any(q1&q2):raise ValueError('one intent vetoed at T1 and T2 '+k)
    if np.any(q1&(~a['has_native_t1']|~a['pending_t1'])):raise ValueError('Q T1 no actual pending source quote '+k)
    if np.any(q2&(~a['has_native_t1']|~a['has_native_t2']|~a['pending_t2'])):
        raise ValueError('Q T2 no genuine still-pending source quote '+k)
    if np.any(q1&((t1<t0+15000)|(t1>=t0+16000)|(a['q_t1_decision_ms']!=t1))):
        raise ValueError('T1 is not first genuine [t0+15,16) Q decision '+k)
    if np.any(q2&((t2<=t1)|(t2>t1+1000))):
        raise ValueError('T2 is not after T1 in bounded decision period '+k)
    bad=o['truth']!=0;good=~bad
    return {'events':n,'q_t1_bad':int(np.sum(q1&bad)),'q_t1_correct':int(np.sum(q1&good)),
           'q_t2_bad':int(np.sum(q2&bad)),'q_t2_correct':int(np.sum(q2&good)),
           'q1_mask_sha256':hashlib.sha256(np.packbits(q1).tobytes()).hexdigest(),
           'q2_mask_sha256':hashlib.sha256(np.packbits(q2).tobytes()).hexdigest()}

def validate_original_and_q(*,f395_zip:Path,q_zip:Path|None,
                            independent_root_receipt:Path|None,
                            expected_original_sha256:str|None=None,
                            expected_q_sha256:str|None=None)->RecoveryResult:
    """A hard **integrity** barrier, NOT self-certifying provenance.

    Missing Q data returns BLOCKED rather than generating a pseudo-mask.
    An independent root/clock attestation must be obtained from external
    original source replay; a JSON statement alone is not accepted as proof.
    """
    f395_zip=Path(f395_zip)
    if not f395_zip.is_file():raise FileNotFoundError('original F395 unavailable')
    h_f395=digest(f395_zip)
    if expected_original_sha256 is not None and h_f395!=expected_original_sha256:
        raise ValueError('immutable F395 archive hash mismatch')
    with zipfile.ZipFile(f395_zip) as z:
        if z.testzip() is not None:raise ValueError('F395 CRC error')
        originals={}
        totals={'events':0,'correct':0,'opposite':0,'neutral':0,
                'q_bad':0,'q_correct_lost':0,'q_t1_bad':0,'q_t1_correct':0,
                'q_t2_bad':0,'q_t2_correct':0}
        for k in CELLS:
            o=_read_npz(z,f'F395_S14_{k}_FROZEN_ORIGINAL_EVENT_MASK.npz')
            assert all(t in o for t in ('t','side','original_index','truth'))
            n=len(o['t']); assert len(o['truth'])==len(o['side'])==len(o['original_index'])==n
            if not np.array_equal(o['original_index'],np.arange(n,dtype=np.int32)):
                raise ValueError('frozen ordinal mismatch '+k)
            if not np.all(np.diff(o['t'])>0) or not np.isin(o['side'],(-1,1)).all():
                raise ValueError('invalid original event clock/side '+k)
            if not np.isin(o['truth'],(0,1,2)).all():raise ValueError('original class corrupt '+k)
            originals[k]=o
            for name,value in (('events',n),('correct',np.sum(o['truth']==0)),
                               ('opposite',np.sum(o['truth']==1)),('neutral',np.sum(o['truth']==2))):
                totals[name]+=int(value)
        if any(totals[k]!=EXPECTED_COUNTS[k] for k in ('events','correct','opposite','neutral')):
            raise ValueError('not original 2,574,251 event universe')
    if q_zip is None or not Path(q_zip).is_file():
        return RecoveryResult('TRAINING_BLOCKED_NO_ORIGINAL_R150Q',{},totals,'missing frozen Q event-level masks')
    if not expected_q_sha256 or len(expected_q_sha256)!=64:
        return RecoveryResult('TRAINING_BLOCKED_NO_AUTHENTIC_Q_DIGEST',{},totals,'independent original R150Q archive hash required')
    if digest(q_zip)!=expected_q_sha256:
        raise ValueError('R150Q archive digest mismatch: not original approved dependency')
    if independent_root_receipt is None or not Path(independent_root_receipt).is_file():
        return RecoveryResult('TRAINING_BLOCKED_SOURCE_ROOT_UNCERTIFIED',{},totals,
                              'no independent original event-selector/root producer deletion evidence')
    root=json.loads(Path(independent_root_receipt).read_text())
    # A passed, independently REPLAYED source-root certificate is required.
    # This boolean alone does not prove the statement; manual attestation and
    # underlying original root replay must also be reviewed outside this module.
    if root.get('status')!='SOURCE_ROOT_INDEPENDENT_REPLAY_PASSED' or not root.get('original_producer_delete_replay_paths'):
        return RecoveryResult('TRAINING_BLOCKED_SOURCE_ROOT_UNCERTIFIED',{},totals,
                              'root source-replay attestation lacks independently inspected evidence paths')
    cell_details={}
    with zipfile.ZipFile(q_zip) as z:
        if z.testzip() is not None:raise ValueError('R150Q CRC error')
        # Fixed source-exact member naming prevents silently reading W/P2/Q2.
        expected=set(f'R150Q_1PCT_{k}_ORIGINAL_EVENT_CLOCK_MASK.npz' for k in CELLS)
        if set(z.namelist())!=expected:raise ValueError('Q archive missing/extra source-clock members')
        for k in CELLS:
            a=_read_npz(z,f'R150Q_1PCT_{k}_ORIGINAL_EVENT_CLOCK_MASK.npz');o=originals[k]
            c=_validate_clock_arrays(k,a,o)
            for kk in ('q_t1_bad','q_t1_correct','q_t2_bad','q_t2_correct'):totals[kk]+=c[kk]
            cell_details[k]=c
        totals['q_bad']=totals['q_t1_bad']+totals['q_t2_bad']
        totals['q_correct_lost']=totals['q_t1_correct']+totals['q_t2_correct']
        if totals['q_bad']!=234507 or totals['q_correct_lost']!=9639:
            raise ValueError('NOT original R150Q 1% 234507 BAD/9639 CORRECT policy')
    return RecoveryResult('STRUCTURE_AND_COUNTS_MATCH_ROOT_EXTERNAL_REVIEW_REQUIRED',cell_details,totals,
                          'manual independent root/source/as-of and original Q archive provenance audit required')
