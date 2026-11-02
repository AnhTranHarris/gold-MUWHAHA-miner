"""R5 all-four label-contaminated memorization demonstration; NOT foresight.

Different from withheld July. Entire four months' hindsight labels are allowed
in this teacher fit; all precision reported solely as training resubstitution.
"""
from pathlib import Path
import json,time,numpy as np,lightgbm as lgb
from fitted_quote_excitation import ROOT,MONTHS
from four_month_competing_risks import load,features,labels
from fit_asymmetric_actions import enrich,ranking

def run():
    data=load()
    # Cross-intensity fitted January+February; July hidden until this
    # deliberate all-four strong-label overfit training.
    for m in MONTHS:
        with np.load(ROOT/f'R5_FITTED_INTENSITY_cross_{m}.npz') as z:r=z['rates']
        data[m]=enrich(data[m],r)
    x=np.vstack([features(*data[m][:3],data[m][4],'ordered') for m in MONTHS])
    y=np.hstack([labels(data[m][3]) for m in MONTHS])
    t0=time.monotonic()
    model=lgb.train({'objective':'multiclass','num_class':4,'learning_rate':.11,
         'num_leaves':63,'max_depth':-1,'min_data_in_leaf':15,'verbosity':-1,
         'num_threads':4,'seed':20261102,'deterministic':True,'force_col_wise':True},
         lgb.Dataset(x,label=y),num_boost_round=85)
    results={'provenance':'SAME 4 months used to train AND score; contaminated overfit only','fit_seconds':round(time.monotonic()-t0,2), 'rounds':85,'four_month_samples':60000,'action_rows':120000,'monthly':{}}
    for m in MONTHS:
        basic,path,mark,k,t=data[m]
        pred=model.predict(features(basic,path,mark,t,'ordered')).reshape(2,len(k),4).transpose(1,0,2)
        score=pred[:,:,3]-1.5*pred[:,:,0]-.3*pred[:,:,1]
        results['monthly'][m]=ranking(score,pred,k,m)
        print('RESUB',m,'top_1pct',results['monthly'][m][1],flush=True)
    model.save_model(str(ROOT/'R5_FOUR_MONTH_EXPLICITLY_CONTAMINATED_model.txt'))
    (ROOT/'R5_ALL4_IN_SAMPLE_HINDSIGHT_OVERFIT.json').write_text(json.dumps(results,indent=2))
    return results
if __name__=='__main__':run()
