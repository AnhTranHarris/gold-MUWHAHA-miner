import json
import gamma02_083_global_child_cap_087 as c

def main():
    D,A=c.build(); rows=[];cache={}
    for cap in range(640,705,4):
        r,B=c.one(A,cap);rows.append(r);cache[cap]=B
        print(json.dumps({k:r[k] for k in ['cap','net','trades','pf','win','expectancy','avg_hold_s','maxopen_event','all_metric_crossover']}),flush=True)
    valid=[r for r in rows if r['all_metric_crossover']]
    valid.sort(key=lambda q:q['cap'])
    exact=[]
    if valid:
        for r in valid[:3]:
            z=c.exact(D,cache[r['cap']],r);exact.append(z);print('EXACT',json.dumps({k:z[k] for k in ['cap','net','trades','pf','win','expectancy','avg_hold_s','equity_dd','equity_dd_pct_peak','minimum_total_equity','maxopen_exact','all_metric_crossover']}),flush=True)
    obj={'candidate':'GAMMA02_083_CHILD_CAP_BOUNDARY_087B','rows':rows,'minimum_all_metric_cap':valid[0] if valid else None,'exact_rows':exact}
    json.dump(obj,open('/mnt/data/gamma02_083_child_cap_boundary_087b.json','w'),indent=2)
if __name__=='__main__':main()