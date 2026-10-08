#!/usr/bin/env python3
"""FAIL CLOSED: historical Feb1 V1 full-system label cannot be attached to a subset engine.
Audit is about source code and source lineage, not invented funding performance.
"""
from pathlib import Path
import ast,hashlib,json
ROOT=Path('/mnt/data/daa_feb1_whitepaper_integrity_027')
SRC=Path('/mnt/data/daa_january_full_execution_024/jan024_reconstructed_full_portfolio.py')
txt=SRC.read_text();mod=ast.parse(txt)
run=next(x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name=='run')
if_nodes=[x for x in ast.walk(run) if isinstance(x,ast.If)]
def refs(node,s):return any(isinstance(x,ast.Name) and x.id==s for x in ast.walk(node))
wd_streak_as_admission=any(refs(node.test,'streak') for node in if_nodes)
funded_recovery_entry=False  # no source=7 explicit funded recovery branch exists in the audited engine
source7_literal=('src=7' in txt or 'src == 7' in txt or 'src==7' in txt)
margin_implemented='margin_requirement' in txt or 'margin_used' in txt or 'free_margin' in txt
per_layer_caps=('layer_cap' in txt or 'layer_budget' in txt)
# Strict per-layer contracts: must be TRUE to assert complete executable V1 parity.
rows=[
('L0','Tick fill / first-touch / full tick floating equity',True,'Implemented for reconstructed source subset, not exact 131E order lineage'),
('L1','Complete stateful independent session grid geometries',False,'One-minute price anchor / local session cell; no complete owned V1 session lattice'),
('L2','Completed H4/H1/M15/M5, role-distinct market context',False,'Completed EMA states exist; role-specific environments/phase/location not complete'),
('L3','Entire accepted London/overlap/NY hourly harvesting portfolio',False,'Selected 131D-like cells, not full original supplement and ownership'),
('L4','Complete independent Asia geometry',False,'One Asia02 specialist, not the independent multi-state Asia geometry'),
('L5','Original funded 049/051/075/084/119/131E Watchdog parent and depth',bool(wd_streak_as_admission),'Missing 4-win authorization, exact multi-parent stream, owned unlocks and depth'),
('L6','Full native trend-within-trend state routing',False,'Four handcrafted specialist cells, not original native full router'),
('L7','Physically coded, bounded state-conditional wrong-direction recovery',bool(source7_literal or funded_recovery_entry),'Recovery described but not implemented as a funded source; no recovered trade stream'),
('L8','Single global physical equity + layer caps + broker margin/stopout',bool(margin_implemented and per_layer_caps),'Global cap+floating marks present; no margin model or per-layer budgets'),
]
cut=json.loads((ROOT/'feb1_cutover_tick_integrity.json').read_text());htf=json.loads((ROOT/'feb1_predeployment_htf_bootstrap.json').read_text())
out={'unit':'DAA_027_WHITEPAPER_COMPLETE_SYSTEM_DEPLOYMENT_GATE','deployment_policy':{'asof_start_utc':'2026-02-01T00:00:00Z','first_available_quote_utc':cut['first_feb_quote_utc'],'allowed_prestart_history':'2026-01 only','february_was_inspected_in_prior_research':True,'february_is_pristine_unseen_holdout':False,'august_sealed':True,'september_reserved':True},'source_audited':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_checks':{'four_funded_child_wins_gates_renewal':wd_streak_as_admission,'funded_recovery_entry_code':source7_literal or funded_recovery_entry,'broker_margin_governor_implemented':margin_implemented,'per_layer_budget_implemented':per_layer_caps},'layers':[{'layer':k,'mandatory_contract':description,'full_contract_met':good,'finding':finding} for k,description,good,finding in rows],'full_whitepaper_system_certified':all(good for _,_,good,_ in rows),'actual_quote_source_qa_pass':cut['pass'],'all_structural_timeframes_preseedable_from_january':htf['all_tf_initializable_on_first_feb_quote'],'live_five_minute_order_ready_certified':False,'full_portfolio_february_1_to_28_pnl_certified':False,'must_not_substitute':'131E historical normalized-spread, 132A transfer or 134K in-month discovered frontiers as a newly executed raw-quote full whitepaper result'}
(ROOT/'feb1_whitepaper_layer_gate.json').write_text(json.dumps(out,indent=2))
for x in out['layers']:print(x['layer'], 'PASS' if x['full_contract_met'] else 'FAIL',x['finding'])
print('ALL_NINE_CONTRACTS_PASS',out['full_whitepaper_system_certified']);print('QUOTE_DATA_READY',cut['pass']);print('ALL_FOUR_HTF_PRESEEDABLE',htf['all_tf_initializable_on_first_feb_quote'])