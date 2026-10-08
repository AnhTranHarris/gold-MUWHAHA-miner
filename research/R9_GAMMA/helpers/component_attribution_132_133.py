import sys,json,numpy as np,importlib
modname=sys.argv[1]; out=sys.argv[2]
M=importlib.import_module(modname); J=M.J; L=M.L

def score_part(name,Q):
    s,_=J.score(M.t,*Q,name,{})
    return {k:s[k] for k in ['name','net','trades','gross_profit','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen','positive_days','beat_days','positive_weeks','beat_weeks','daily','weekly']}
parts=[]
wd=J.build_watchdog();parts.append(score_part('WATCHDOG',wd))
cov=M.build_coverage_targeted();parts.append(score_part('COVERAGE',cov))
cold=M.build_coldstart_targeted(50,450,64);parts.append(score_part('COLD64',cold))
for k,l,n,st,cap in L.LEAN:
    q=L.build_rule(k,l,st,cap);parts.append(score_part(n,q))
json.dump({'module':modname,'parts':parts},open(out,'w'),indent=2)
for s in parts:
    print({k:s[k] for k in ['name','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','positive_days','beat_days','positive_weeks','beat_weeks']})