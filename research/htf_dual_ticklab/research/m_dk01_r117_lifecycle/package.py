from pathlib import Path
import json,hashlib,zipfile,csv,platform
R=Path(__file__).resolve().parent;W=R.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[];raw=[];spl=[];totbad=totgood=rawbad=rawgood=0
for m in ('01','02','06','07'):
 d=json.loads((R/'results'/f'score_{m}.json').read_text());k=next(k for k in d['counts'] if k.startswith('FULL'));a=d['counts'][k];b=d['raw_union'][k]
 rows.append([m,a['n'],a['incorrect_veto'],a['correct_lost'],a['teacher_wrong_overlap'],a['wrong_not_vetoed_by_teacher']])
 raw.append([m,b['incorrect_veto'],b['correct_lost']]);totbad+=a['incorrect_veto'];totgood+=a['correct_lost'];rawbad+=b['incorrect_veto'];rawgood+=b['correct_lost']
 if m=='01':spl=[[n,s['n'],s['incorrect_veto'],s['correct_lost']] for n,s in d['counts'].items() if not n.startswith('FULL')]
def table(cols,rows):return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
report=f'''# F401-R117 — direct original-signal lifecycle specialists

2026-10-28. UNAPPROVED / exact configuration parked. No replacement or >400k selective result achieved.

The user correctly identified a scope error: hypothetical order non-touches had displaced the original incorrect-signal filter objective. R117 implements actual causal t0 veto masks on unchanged original signals. It translates disclosed practitioner mechanisms into ordered multiscale auction states, then uses hindsight-selected error phenotypes to train conditional foresight specialists. It processes all1,266,934 original DK events and32,290,648 original quotes. Three models complete128 rounds each. Four causal tests and an independent complete saved-event recount pass.

The protected portfolio vetoes **{totbad:,} incorrect / {totgood:,} correct** across all four months. Its nontraining January VAL interval is21/16; February+June+July total1,044/505. January FIT supplies7,384 incorrect removals, so the pooled total must not be presented as forward capacity. Raw mechanism eligibility covers **{rawbad:,} incorrect / {rawgood:,} correct**. This exceeds the requested wrong-event scale only by also discarding most correct events. It is not success. The original fitted teachers remain448,187 incorrect veto /41 correct lost; January's original teacher94,603/7. No successful conversion is claimed.

## What was actually converted

At each completed M1/M5/M15/H1/H8 boundary, publish the last contiguous bar's high, low, body, range and quote count. Track each high/low through ordered crossing, return, recrossing, penetration, dwell and activity until its next publication. Crossing requires both quote sides past the level; rejection requires spread-scaled hysteresis. Every original signal reads strictly prior quotes, before any equal-time quote. A new bucket without a previously consumed quote abstains instead of retaining a stale level. Missing first-source history is retained as zero-state input, not dropped.

The140 new coordinates join167 existing causal native/completed-structure features. Three experts cover rejected own-direction auctions, accepted opposite-direction breakouts, and accepted own-direction expansion after an already directional bar. A context can apply to many original signals; no per-bar trade-count limit. This is distinct from R116 static role geometry/degree-two signatures and from prior nearest-episode memory. The full practitioner systems, proprietary patterns and ADX algorithms were not copied. No claim of exact champion-strategy replication.

Each expert trains on every eligible January FIT event using three classes: original correct; original wrong retained by teacher; original wrong rejected by teacher. Its runtime score is predicted teacher-selected wrong probability divided by predicted original-correct probability plus1e-6. The teacher mask is never a runtime feature. Portfolio score is the maximum eligible expert score. Models use127 leaves, min64 rows/leaf,128 rounds, learning rate.06, L2=5, deterministic seeds and16-round checkpoints. No ensemble ablation was fitted after the negative result; causal-state contribution is therefore not established independently of the combined portfolio.

## Asymmetric objective and frozen selection

Select the lowest score cut satisfying <=1% correct loss in January CAL and <=2% in each side/six-hour cell with >=100 correct. The primary objective is increasing original wrong vetoes within this constraint, not balanced accuracy or equal weighting. This is a declared research operating point, not an invented owner approval criterion. Strictly greater than the cut rejects; ties remain. The exact cut is2.828857898712158. A cell constraint binds before the aggregate1% allowance, so CAL has165 wrong/120 correct. No subsequent threshold grid or validation tuning.

January FIT first60%, CAL60–80%, VAL80–90%, shadow90–100%, with40-second label separation. **Additional teacher limitation:** the original teacher was fitted on the full month. Even restricting its use to FIT target rows carries full-month fitted information into those targets. Consequently January VAL is a separate current-run interval, not a clean unseen-teacher validation. All months were already used in historical research. None is claimed prospective or untouched. A future validation claim needs a teacher fitted within its allowed training information or independent outcome-only targets.

## Exact four-month counts

'''+table(['month','original events','incorrect veto','correct lost','teacher-wrong overlap','wrong not vetoed by teacher'],rows)+'''

Every event identity, side, archived original truth and teacher decision is retained. Wrong means opposite or neutral under the original30-second label contract. Saved score JSON includes both subclasses and each side/session. Wrong-not-vetoed-by-teacher is not unique marginal contribution against the missing F234 parent.

'''+table(['January interval','events','incorrect veto','correct lost'],spl)+'''

## Raw eligibility before learned protection

'''+table(['month','incorrect covered','correct covered'],raw)+'''

Coverage is a capacity diagnostic, not a deployed recommendation. Unique30-second side/time buckets are included in score JSON to expose clustering; these are fixed clock buckets, not independent market episodes. No effective-sample-size claim is made.

## Audit coverage and remaining source limits

| Requested axis | Implemented evidence / limit |
| --- | --- |
| Hindsight mechanism audit | Original93-feature/8-teacher contract and existing teacher family audit reused; new152-feature ordered/role association atlas completed in R116. R117 uses teacher-selected error targets and ordered lifecycle states. |
| Multi-horizon | Prior-return horizons in reused native features; original30-second target. New jointly learned2/8/30-second forecast is proposed, not run. |
| Multi-timeframe and trend | M1/M5/M15/H1/H8 publication; completed3/5/9-bar geometry retained for M1/M5/M15/H1. |
| State, regime, pattern | Crossing/rejected/reclaimed state, prior directional/compressed bar, expansion, quote activity; no independently validated exhaustive regime taxonomy. |
| Session | Original UTC six-hour side/session constraint and reporting; no imported economic calendar. |
| Event and high frequency | Every original t0 event on source quotes; full ordered quote updates, not bar-only decisions. |
| Volume | Source quote cadence only. Actual traded volume, aggressor trades and L2 depth absent. |
| Geometry, grids, support/resistance | Published extrema and prior multibar geometry; no new fixed-price grid model or actual queue-volume inference. |
| Ultra-high capacity | Raw states exceed400k wrong coverage, but selective frozen output is8,656/726. Goal unmet. |

The two existing broker engines remain pinned and unchanged. This experiment evaluates four Dukascopy cells only, not all eight broker/month cells. Exact FILTER05 ordered15 publisher, F234 accepted composition masks and genuine R9 pre-OrderSend IDs remain unresolved. G01–G09 and all owner signoffs unchanged; no /02 promotion, no4,178-quota or12 shared-capital scenario result. This original-signal classifier has no simulated fill/PnL claim.

## Practitioner and GitHub sources actually used

Unger Academy discloses a Gold example using completed480-minute extrema with a body/range compression condition: https://ungeracademy.com/blog/trading-systems-tips-how-to-identify-the-best-timeframe-and-get-new-ideas-for-your-strategies . Andrea Unger describes higher-timeframe indicator filters for already accelerated breakouts: https://ungeracademy.com/blog/how-to-use-trading-indicators . These inspired context and lifecycle construction; championship standing is not used as evidence that these adaptations work.

Kevin Davey publishes trend/countertrend breakout rules and a delayed-confirmation analysis: https://kjtradingsystems.com/Act/davey0310.pdf . We used the idea of interpreting confirmation history; his full crude-oil strategy, session parameters and ADX implementation were not reproduced. These sources describe trading mechanisms, not evidence of tick-speed HFT.

R116 independently implemented ordered integral coordinates inspired by https://github.com/bottler/iisignature and tested action-specific utility ideas informed by EconML policy learning; it did not implement doubly robust policy estimation. R117 adds independently written streaming states. No public trading code or external market tape was imported. EasyTPP, torchcde and hftbacktest were reviewed for the next mechanism designs, explicitly not executed here; see NEXT_RESEARCH.md.

## Failure-driven next mechanism

The next recommended bounded study is a persistent, marked quote-sequence forecaster trained on dense next-event and multi-horizon path supervision, with the original signal-veto readout. This changes representation and training information rather than retuning the current snapshot classifiers. A second path uses a causal continuous-time latent state and FIT-only future-path distillation. A third recovers the exact missing publisher and accepted-parent masks for source-faithful residual cooperation. NEXT_RESEARCH.md specifies inputs, targets, maturity, evaluation and reuse boundaries. No model training or performance is claimed for R118.

## Preservation and reproduction

Predeclaration commit f169180a2598d7dd7405838c07fb47a51f6b3e7b was published before feature execution/model fit. It descends from c941d7b5f0369079c1226fd642bc34cc1b22380b, preserving sibling R110-DIST and R112–R115. R116's completed failed static/ablation/online study is preserved separately, with9 Drive archives authenticated byte-for-byte after upload. No old research is erased.

One initial January event NPZ was truncated before any model fitted. It was rebuilt from byte-pinned original labels and SHA-verified unchanged feature state; all original fields across four months passed identity checks. PERSISTENCE_RECOVERY.md records this operational repair. Feature/model scientific settings were unchanged.

Extract R116 and R117 archives into the same workspace. Existing original source tapes/archive and reused pinned engine remain at their recorded paths. Source hashes and governance retrieval receipts are in R116. R117 preparation can regenerate the omitted state caches; R116 can regenerate omitted native caches. For a new deliberate reproduction use empty cache/results/models, run test discovery, prepare each month, fit, predict01, calibrate once, score01, then predict/score02/06/07. Saved models/probabilities/masks already permit verify_saved.py without rerunning science. Large reproducible feature caches and duplicate raw tapes are deliberately omitted.
'''
(R/'SCIENTIFIC_REPORT.md').write_text(report)
with (R/'results/SCORECARD.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['month','events','incorrect_veto','correct_lost','teacher_wrong_overlap','wrong_not_vetoed_by_teacher']);w.writerows(rows)
(R/'SOURCE_CONTRACT.json').write_text(json.dumps(dict(experiment='F401-R117-LIFECYCLE',state='UNAPPROVED_PARKED',predeclare_commit='f169180a2598d7dd7405838c07fb47a51f6b3e7b',plan_sha256=sha(R/'PLAN.md'),run_sha256=sha(R/'run.py'),reuse='research_r116/SOURCE_CONTRACT.json',runtime=platform.python_version(),next='R118_UNEXECUTED'),indent=2)+'\n')
assert json.loads((R/'results/INDEPENDENT_RECOUNT.json').read_text())['status']=='PASS'
files=[p for p in R.rglob('*') if p.is_file() and not any(v.startswith('.') or v=='__pycache__' for v in p.relative_to(R).parts) and p.suffix not in ('.tmp','.pyc','.nbc','.nbi') and not(p.parent.name=='cache' and p.suffix=='.npy') and p.name not in ('MANIFEST.json','PACKAGE.log','DELIVERY_RECEIPT.json','REMOTE_VERIFIED.json','DELIVERY.md')]
manifest={str(p.relative_to(R)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)}
(R/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(R/'MANIFEST.json')
parts=[];cur=[];size=0
for p in sorted(files):
 if size+p.stat().st_size>44_000_000 and cur:parts.append(cur);cur=[];size=0
 cur.append(p);size+=p.stat().st_size
if cur:parts.append(cur)
out=[]
for i,ps in enumerate(parts,1):
 p=W/f'F401_R117_LIFECYCLE_PART{i:02d}_20261028.zip'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for v in ps:z.write(v,'research_r117/'+str(v.relative_to(R)))
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  for n in z.namelist():
   k=n.removeprefix('research_r117/')
   if k in manifest:assert hashlib.sha256(z.read(n)).hexdigest()==manifest[k]['sha256']
 out.append(dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p),crc='PASS',member_sha='PASS',members=len(ps)))
 print(out[-1],flush=True)
(R/'DELIVERY_RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n')
