"""Map fitted strict-prior-slot excitation intensities onto 250ms candidates."""
from __future__ import annotations
import numpy as np
from fitted_slot_excitation import slot_dataset,design_matrix,predict
FITTED_INTENSITY_FEATURE_VERSION='r9_v2_fitted_slot_intensity_features_v1'
FITTED_INTENSITY_NAMES=('fit_lambda_BU','fit_lambda_BD','fit_lambda_AU','fit_lambda_AD','fit_lambda_SW','fit_lambda_SN',
 'fit_price_direction','fit_spread_narrow_balance','fit_total_intensity','fit_intensity_entropy','fit_bid_ask_direction_gap')
FITTED_INTENSITY_COUNT=len(FITTED_INTENSITY_NAMES)

def candidate_fitted_intensities(t,bid,ask,day,candidate_ts,model_npz):
 z=np.load(model_npz) if not hasattr(model_npz,'files') else model_npz
 slot,Y,S,sess=slot_dataset(t,bid,ask,day);X,_=design_matrix(S,sess,z['scales']);P=predict(X,z['coef']);cslot=(np.asarray(candidate_ts,np.int64)//250)*250;ix=np.searchsorted(slot,cslot)
 if np.any(ix>=len(slot)) or not np.array_equal(slot[ix],cslot):raise ValueError('candidate slot not found')
 q=P[ix];up=q[:,0]+q[:,2];down=q[:,1]+q[:,3];sw=q[:,4];sn=q[:,5];tot=q.sum(1);prob=q/(tot[:,None]+1e-12);ent=-np.sum(prob*np.log(prob+1e-12),axis=1)
 derived=np.column_stack(((up-down)/(up+down+1e-12),(sn-sw)/(sn+sw+1e-12),tot,ent,(q[:,0]-q[:,1])-(q[:,2]-q[:,3])));out=np.column_stack((q,derived)).astype(np.float32)
 if out.shape!=(len(candidate_ts),FITTED_INTENSITY_COUNT) or not np.isfinite(out).all():raise ValueError('fitted intensity feature contract')
 return out
