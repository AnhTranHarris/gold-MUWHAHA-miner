from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import time
import zipfile
import lightgbm as lgb
import numpy as np

R=Path(__file__).resolve().parent;W=R.parent
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def table(cols,rows):
    return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+
        ['| '+' | '.join(str(v) for v in row)+' |' for row in rows])
recount=json.loads((R/'results/INDEPENDENT_RECOUNT.json').read_text());assert recount['status']=='PASS'
rows=[];validation=[];totals=[];market=[];detail=[]
for view in ('full','ablation','online'):
    bad=good=additional_bad=additional_good=0; expbad=expgood=0.
    for month in ('01','02','06','07'):
        d=json.loads((R/'results'/f'score_{view}_{month}.json').read_text())
        s=next(x for x in d['counts'] if x['split'].startswith('FULL_') and x['latency']==250)
        a=np.load(R/'cache'/f'actions_{month}.npz');dec=np.load(R/'results'/f'decisions_{view}_{month}.npz')
        no=a['touch_250'][:,0]<0;y=a['truth_class']
        mb=int((no&(y!=0)).sum());mg=int((no&(y==0)).sum())
        ab=int((~no&dec['no_touch']&(y!=0)).sum());ag=int((~no&dec['no_touch']&(y==0)).sum())
        rows.append([month,view,s['incorrect_no_touch'],s['correct_no_touch'],ab,ag])
        detail.append(dict(month=month,view=view,**s,additional_bad_to_market=ab,additional_good_to_market=ag))
        bad+=s['incorrect_no_touch'];good+=s['correct_no_touch'];additional_bad+=ab;additional_good+=ag
        expbad+=d['placebo_expected']['incorrect_no_touch'];expgood+=d['placebo_expected']['correct_no_touch']
        if view=='full':market.append([month,mb,mg])
        if month=='01':
            for split in ('CAL','VAL','SHADOW'):
                q=next(x for x in d['counts'] if x['split']==split and x['latency']==250)
                validation.append([view,split,q['n'],q['incorrect_no_touch'],q['correct_no_touch']])
    totals.append([view,bad,good,additional_bad,additional_good,round(expbad,3),round(expgood,3)])
with (R/'results/SCORECARD.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(detail[0]));w.writeheader();w.writerows(detail)

# Local throughput is just model inference, not feature extraction or MT5.
x=np.load(R/'cache/x_01.npy',mmap_mode='r')[:25000]
models=[lgb.Booster(model_file=str(R/'models'/f'full_{a}.txt')) for a in range(1,5)]
started=time.perf_counter()
for m in models:m.predict(x,num_threads=4)
elapsed=time.perf_counter()-started
bench=dict(events=25000,model_heads=4,threads=4,seconds=elapsed,events_per_second=25000/elapsed,
    feature_cost_included=False,mt5_parity=False)
(R/'results/THROUGHPUT.json').write_text(json.dumps(bench,indent=2)+'\n')

report='''# F401-R116-ACTION — completed source-native action geometry and matured-response study

2026-10-28 America/Chicago. **UNAPPROVED. No M-DK-01 replacement achieved.**

Two distinct information treatments were implemented and evaluated: ordered bid/ask path plus completed structure selecting action geometry, then a matured action-response correction after the static selector's capacity collapse. A separate feature ablation measures the new coordinates' contribution. All eight trained models completed 96 rounds, using every eligible January FIT row. All 1,266,934 original Dukascopy Jan/Feb/Jun/Jul event rows and 32,290,648 original quotes were processed; no sample extrapolation. Nine causal/sequence tests and the independent saved-event recount pass.

## Decision, actual advance, and limits

The constrained selector does not deliver the requested high capacity. At the predeclared 1% January CAL correct-opportunity loss limit, the first feasible multiplier was 8 and almost every event selected MARKET. The online action-response mechanism adds some declined opportunities in exposed months, but does not beat the matching randomized action control there. The new ordered/role features do not establish a useful gain over their ablation. These specific configurations are parked; do not run a nearby threshold, leaf, horizon or half-life sweep.

The completed output is a reusable, source-causal multiaction prototype and exact evidence, **not a breakthrough claim**. Original M-DK-01 January comparator remains 94,603 incorrect veto /7 correct losses; four monthly fitted teachers 448,187/41. The new measurements are hypothetical quote non-touches for proposed never-submitted intents, not identical original t0 signal vetoes. The >400,000 goal is unmet by the learned protected policies. G06 is a collection-level gate, not this component's acceptance criterion.

## Mechanism and scientific distinction

Each decision observes only quotes strictly before original t0. The original native feature producer and R110-DIST completed 3/5/9-bar structure function are reused. There are 319 total coordinates: native returns/quote cadence, side interactions, completed M1/M5/M15/H1 geometry, 48 support/resistance role changes, and 104 degree-two ordered bid/ask/time/one-sided-update path coordinates across 8/16/32/64 increments. Same endpoint displacement with reversed bid/ask update order produces different features, verified by test. No real executed volume, L2 depth, economic-calendar feed, or external quote tape exists in this experiment.

Actions are MARKET, directional CONTINUE at .15/.35 dollars, a three-phase breakout-retreat-reclaim RETEST, and a completed M1/M5 support/resistance-derived stop distance clipped .10–.70. Four separate 3-class models estimate touch, missed-correct, and missed-incorrect action outcomes. Parameters: 96 rounds, 127 leaves, minimum96 rows/leaf, learning rate .06, L2=5, deterministic seeds; 16-round saved checkpoints. New-feature ablation has four independently fitted models. This changes action-specific targets and ordered information, and does not re-run R112–R115's post-intent correct guardian.

The second mechanism corrects each action's predicted response with earlier observed-versus-expected class mass in side × six-hour session × completed M1/M15 alignment states. Updates occur strictly after +33.001s, with 30-minute decay and prior32. January FIT outcomes are excluded from updates; subsequent months reset state. No trees were refitted for this arm. Its future-label mutation and maturity-boundary tests pass. This rule is distinct from global correctness calibration but does not supply an external information source.

## Frozen evaluation and all outcomes

January first60% FIT, 60–80% CAL, 80–90% VAL, 90–100% shadow; 40-second label embargo before each next interval. January FIT has 206,414 rows (confirm exact model receipts if a source changes). Each arm selects one of 21 predeclared constraint multipliers, maximizing incorrect non-touches subject to <=1% correct missed in CAL and <=2% in side/session cells with >=100 correct. These are researcher-selected calibration constraints, not newly invented owner acceptance laws or guaranteed future limits. No post-VAL tuning. The multiplier is 8 in every arm. At multiplier4, static CAL missed887 correct while avoiding3,107 incorrect, so it violates the specified cap; multiplier8 yields8/2. No claim that the coarse multiplier set is the mathematical optimum among all possible policies.

Full-month counts include January FIT/CAL. February/June/July and all current-run validation are historically exposed, not prospective. Original correctness labels and teacher masks are preserved unchanged. Source-month/side/session summaries, every CAL multiplier and 0/250/1000ms mechanical sensitivity are saved.

### Four-month totals at 250ms

'''+table(['arm','incorrect no-touch','correct no-touch','additional bad vs MARKET','additional good missed vs MARKET','random expected bad','random expected good'],totals)+'''

MARKET itself can miss a quote before the16s expiry. Those misses are not algorithmic filter skill; additional columns isolate new non-touches beyond that control. Matched random expectation preserves selected action counts within each original UTC-hour/side cell. It randomizes action assignments, not outcome labels, and is not the missing F234 cascade comparison. Apparent pooled advantage is dominated by the fitted January region.

### Full original monthly populations

'''+table(['month','arm','incorrect no-touch','correct no-touch','additional bad vs MARKET','additional good missed vs MARKET'],rows)+'''

### January current-run intervals, outside FIT

'''+table(['arm','split','n','incorrect no-touch','correct no-touch'],validation)+'''

The static and adaptive arms each avoid zero incorrect on VAL while missing one correct; the ablation avoids zero and misses zero. Low correct loss alone is not success when wrong-signal capacity disappears.

## New correlation audit

The new atlas covers all152 newly added ordered/role coordinates against the original teacher mask, original wrong class, and .35 action non-touch. Eight-bin edges use only first60% January feature values; association is evaluated on Jan last40 and the three exposed months. Highest minimum cross-month original-wrong mutual information is about0.000227 bits for the last64 joint-update share; the same coordinate has at least0.002174 bits association with action non-touch. Individual associations are descriptive; the nonlinear action model and ablation are the conditional usefulness test. This extends the old197-feature atlas with new coordinates without rerunning that completed audit. No family gain percentage is relabelled as an independent veto count.

## Quote-side economics and chronology

Main latency250ms; fixed0/1000ms sensitivity. Zero latency starts strictly after t0, and all actions expire at+16s. BUY entries use ask, SELL entries bid; exit at the first quote in [+32,+34)s uses the opposite executable side. RETEST requires favorable excursion, retreat, then reclaim in that order. Source quote touches are bounds, not server-confirmed fills. Missing exits remain explicitly unknown, not assigned zero profit. Only no-entry intents have no trading exposure in these hypothetical arms. All available aggregate gross quote-side sums are negative; commissions, financing, queue, margin and shared capital are not simulated. No whole-EA profitability or12-scenario test is claimed.

January/February first source events have no strictly prior quote. They are retained with unsupported zero features and forced MARKET outcomes for every action. All other source event identities remain exact. A reporting-key-only rename occurred after January cache creation; original receipt retained, no feature/action calculation changed. Nine unit tests address future/equal-time quote changes, completed bars, path ordering, entry latency, retest sequence, embargo and maturity. Independent recount validates each saved policy and original event identity for every monthly row and all3 mechanical latencies. Model inference throughput is in results/THROUGHPUT.json; it excludes feature computation and is not a measured MT5 tick-handler budget.

## Preservation and research hierarchy

Source SHA pins and documentary retrieval revisions are recorded. Eleven reused core engine blobs match their recorded Git identities; no engine repair or rebuild. Git source parent c941d7b5f0369079c1226fd642bc34cc1b22380b is an explicit merge preserving sibling R110-DIST and R112–R115 histories. This resolves the stale R93/R94/R112 cursor without erasing research. Full code, models, event masks, probabilities, actions and results are packaged; feature caches are reproducible from existing authorized sources and are omitted to avoid redundant storage.

The complete current document texts were retrieved; operative governor, original forensic definitions/checklist and current receipts were inspected. This run does not certify a word-for-word reading of every older appended historical paragraph; see BOOTSTRAP_RECEIPT.md. No checklist or /02 promotion occurs. 21/39 historical owner approvals and G01–G09 open remain unchanged. Exact FILTER05, F234 composition masks, original R9 intent join and complete historical F400 ZIP remain unresolved; a bounded two-account FILTER05 search found references, not its original publisher. This is four-DK exploration, not eight-cell validation.

## Next cursor: R117, not executed

Do not count another no-touch capacity surrogate as an M-DK-01 replacement. Before another expensive fit, recover the exact accepted parent masks and strongest prior positive specialist source, then target **unique wrong errors still passed by that parent** with an episode-level conditional specialist. Train against the accepted specialist's failure/rescue residual and retain class/side/session overlap. This is a different training population and contribution target; it must not be implemented as another globalY scalar or another delayed guardian. The missing original FILTER05 publisher remains a bounded information-recovery task, not permission to fabricate its15 columns or rebuild the engine.

Three next alternatives: (1) source-authenticated cooperative residual/rescue specialist with action-independent original t0 masks; (2) action-conditioned causal online state based on genuine intent/fill lifecycle rather than hypothetical source touch, once that evidence exists; (3) a calibrated marked temporal event model trained on future quote-sequence likelihood with cross-horizon transfer, distinct from the tested degree-two summary and from prior coarse renewal codebooks, only if it demonstrates new conditional information before full fitting. R116 provides implementation/control assets for these; no further numerical edge is asserted.

Method references: https://github.com/bottler/iisignature ; https://www.pywhy.org/EconML/_autosummary/econml.policy.DRPolicyForest.html ; https://www.mql5.com/en/docs/standardlibrary/tradeclasses/ctrade/ctradebuystop . Ideas only; no third-party strategy code/data imported. Follow the refreshed actual newest branch/ledger before R117 to avoid concurrent-study duplication.
'''
fit_rows=json.loads((R/'models/full_1.json').read_text())['fit_rows']
report=report.replace('206,414 rows',f'{fit_rows:,} rows')
(R/'SCIENTIFIC_REPORT.md').write_text(report)
(R/'README.md').write_text('''# Reproduce R116-ACTION (unapproved)

Extract all delivery ZIPs into the same directory, retaining the research_r116/ prefix. Place existing approved original FILTER08 ZIP at sources/filter08_recovered.zip and four approved original DK CSV.GZ files under sources/. Preserve the unchanged engine modules under repo/research/htf_dual_ticklab/. Source pins are in SOURCE_CONTRACT.json; do not fetch substitute data. Python3.12, NumPy, pandas, Numba and LightGBM are required. No imported third-party strategy.

Run tests: `python -m unittest discover -s research_r116 -p 'test_*.py' -v`.
Feature caches are deliberately omitted; use a fresh reproduction directory with empty cache/results/models. Prepare each month: `python research_r116/run.py prepare --month 01` (then02,06,07). The saved models are authoritative; copying them into models/ permits frozen prediction without fitting. Use `fit --view full` or `fit --view ablation` only for a deliberately requested fresh reproduction in an empty model directory, not a new scientific result.

For each static view: predict01, calibrate once, score01; then predict and score02/06/07. Call syntax: `python research_r116/run.py predict --view full --month 01`; replace stage by calibrate (omitmonth) or score. Online: `python research_r116/online.py --month 01`, then02/06/07. Saved results must not be overwritten. Full package already includes all scores and decisions, so `python research_r116/verify_saved.py` can independently recount them without regeneration once original FILTER08 is supplied.

Models checkpoint every16rounds. Never mix code/plan hashes with a different run; no auto-refit on interrupted session. Main experiment is hypothetical never-submitted source-quote action exploration, not a live EA or originalR9 order replay. No deployment or owner signoff follows.
''')
contract=json.loads((W/'research_r110/SOURCE_CONTRACT.json').read_text())
contract.update(experiment='F401-R116-ACTION',state='UNAPPROVED_PARKED',scientific_parent='ab9758b2ffa1754fd463b91e30afab9844543497',
 publication_parent='c941d7b5f0369079c1226fd642bc34cc1b22380b',preserved_next_cursor='R117_UNRUN',
 tested_run_sha256=sha(R/'run.py'),plan_sha256=sha(R/'PLAN.md'),online_sha256=sha(R/'online.py'),
 python=sys.version,platform=platform.platform())
(R/'SOURCE_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n')

# Preserve outputs, not reproducible feature caches or raw source duplicates.
files=[]
for p in R.rglob('*'):
    if not p.is_file() or any(v.startswith('.') for v in p.relative_to(R).parts) or '__pycache__' in p.parts or p.suffix in ('.tmp','.pyc','.nbi','.nbc'):continue
    if p.parent.name=='cache' and p.suffix=='.npy':continue
    if p.name in ('ARCHIVE_MANIFEST.json','DELIVERY_RECEIPT.json','DELIVERY.md','PACKAGE.log'):continue
    files.append(p)
manifest={str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)}
(R/'ARCHIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(R/'ARCHIVE_MANIFEST.json')
# Bound every part below the connector limit using uncompressed member sizes.
groups={};part=[];size=0
for p in sorted(files):
    if size+p.stat().st_size>44_000_000 and part:
        groups[f'PART{len(groups)+1:02d}']=part;part=[];size=0
    part.append(p);size+=p.stat().st_size
if part:groups[f'PART{len(groups)+1:02d}']=part
receipts=[]
for label,members in groups.items():
    out=W/f'F401_R116_ACTION_{label}_20261028.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in members:z.write(p,'research_r116/'+str(p.relative_to(R)))
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for n in z.namelist():
            key=n.removeprefix('research_r116/')
            if key in manifest:assert hashlib.sha256(z.read(n)).hexdigest()==manifest[key]['sha256']
    receipts.append(dict(file=out.name,bytes=out.stat().st_size,sha256=sha(out),members=len(members),crc='PASS',member_sha='PASS'))
    print(receipts[-1],flush=True)
(R/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipts,indent=2)+'\n')
