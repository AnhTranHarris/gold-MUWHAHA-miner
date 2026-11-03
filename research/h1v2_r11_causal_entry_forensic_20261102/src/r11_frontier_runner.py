"""R11 full source-exact OFFLINE frontier runner. Requires original raw ticks/NPZ.

DO NOT run without first restoring original immutable four-month artifacts.
Nothing is written inside original H1V2 result folders. No claim of executed
full-month research until the command finishes and the output hash is verified.
"""
import argparse,hashlib,json,pathlib
import numpy as np
from r11_entry_admission import H1V2_ORIGINAL,V5_SHADOW,candidate_mask
from r11_future_frontier import optimize,FrontierConfig

MONTHS=("01","02","06","07")
def sha(p):
    with open(p,"rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()

def run(month,raw_root,labels_root,out_root,contract,objective,first_max,extra_cost,occupancy_penalty):
    if month not in MONTHS:raise ValueError("unsupported month")
    from h1v2_teacher import read_ticks,candidate_250ms,schedule_oracle
    raw=pathlib.Path(raw_root)/f"XAUUSD_DUKAS_2026_{month}_ticks.csv.gz"
    labels=pathlib.Path(labels_root)/f"h1v2_dukascopy_{month}_oracle_labels.npz"
    receipt=json.loads((labels.parent/f"h1v2_dukascopy_{month}_receipt.json").read_text())
    if sha(raw)!=receipt["raw_sha256"] or sha(labels)!=receipt["teacher_labels_sha256"]:
        raise ValueError("ORIGINAL raw/teacher hash mismatch; abort")
    t,b,a=read_ticks(raw)
    with np.load(labels,allow_pickle=False) as z:
        ix=z["tick_index"].copy()
        code=z["code"].copy();net=z["net"].copy()
        end=z["exit_tick_index"].copy();first=z["first_event_ms"].copy()
        lifetime=z["exit_ms"].copy();original_row=z["selected_row"].copy()
        original_side=z["selected_side"].copy()
        if not np.array_equal(t[ix],z["t"]):
            raise ValueError("original candidate timestamp mismatch")
    from_original=candidate_250ms(t,b,a)
    if not np.array_equal(from_original,ix):
        raise ValueError("pinned original H1V2 candidate-ordinal drift")
    own=candidate_mask(t,b,a,H1V2_ORIGINAL)
    if not np.array_equal(np.flatnonzero(own),ix):
        raise ValueError("R11 H1V2 parity failed")
    v5=candidate_mask(t,b,a,V5_SHADOW)
    allowed=np.ones(len(ix),bool) if contract=="original" else v5[ix]
    # Baseline original oracle reproduction must succeed BEFORE modified scheduling.
    baseline,bs,_=schedule_oracle(ix,code,net,end)
    if not(np.array_equal(baseline,original_row) and np.array_equal(bs,original_side)):
        raise ValueError("original oracle baseline reconstruction mismatch")
    if contract=="original" and objective=="count" and first_max==30000 and extra_cost==0.0 and occupancy_penalty==0.0:
        assert len(baseline)==receipt["oracle_nonoverlapping"]["trades"]
    cfg=FrontierConfig(objective=objective,max_first_hit_ms=first_max,incremental_cost=extra_cost,occupation_penalty_per_ms=occupancy_penalty)
    rows,sides,metrics=optimize(ix,code,net,end,first,lifetime,eligible=allowed,config=cfg)
    k=(sides==-1).astype(np.int64)
    out=pathlib.Path(out_root);out.mkdir(parents=True,exist_ok=True)
    stem=f"R11_{month}_{contract}_{objective}_fast{first_max}_cost{extra_cost:.4f}_occ{occupancy_penalty:.8f}"
    trace=out/f"{stem}.npz"
    np.savez_compressed(trace,entry_tick_index=ix[rows],entry_timestamp_ms=t[ix[rows]],side=sides,
        exit_tick_index=end[rows,k],exit_timestamp_ms=t[end[rows,k]],first_favorable_ms=first[rows,k],
        original_net=net[rows,k],repriced_net=net[rows,k]-extra_cost)
    report=dict(month=month,contract=contract,scope="OFFLINE FUTURE-PRIVILEGED COUNTERFACTUAL ONLY",
        raw_sha256=receipt["raw_sha256"],teacher_sha256=receipt["teacher_labels_sha256"],
        original_oracle_count=len(original_row),original_candidate_count=len(ix),
        v5_shadow_eligible=int(v5[ix].sum()),v5_shadow_removed=int((~v5[ix]).sum()),
        exact_original_admission_parity=True,original_teacher_oracle_reconstructed=True,
        trace_sha256=sha(trace),trace_file=trace.name,
        config=cfg.__dict__,metrics=metrics,
        boundaries="v5_shadow only models known gap+warmup+spread; all strict first-hit classes from original fee .02, extra cost only post-hoc net sensitivity; zero live evidence")
    dest=out/f"{stem}.json";dest.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2),flush=True)
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--month",required=True,choices=MONTHS)
    ap.add_argument("--raw-root",required=True);ap.add_argument("--labels-root",required=True)
    ap.add_argument("--out-root",required=True)
    ap.add_argument("--contract",choices=("original","v5_shadow"),default="v5_shadow")
    ap.add_argument("--objective",choices=("count","net","occupancy"),default="count")
    ap.add_argument("--first-max-ms",type=int,default=30000)
    ap.add_argument("--extra-cost",type=float,default=0.)
    ap.add_argument("--occupation-penalty-per-ms",type=float,default=0.)
    args=ap.parse_args()
    run(args.month,args.raw_root,args.labels_root,args.out_root,args.contract,args.objective,
        args.first_max_ms,args.extra_cost,args.occupation_penalty_per_ms)
