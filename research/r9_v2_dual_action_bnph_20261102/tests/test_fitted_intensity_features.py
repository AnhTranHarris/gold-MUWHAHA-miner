import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from fitted_intensity_features import candidate_fitted_intensities,FITTED_INTENSITY_COUNT

def test_candidate_mapping_is_slot_exact_and_finite(tmp_path):
 coef=np.zeros((37,6));coef[-7:]=.1;scales=np.ones(30);p=tmp_path/'m.npz';np.savez(p,coef=coef,scales=scales,session_means=np.ones((7,6))*.1)
 base=1767657600000;offs=np.array([0,100,260,300,500,600,760,800,1000,1100,1260,1500],np.int64);t=base+offs;b=100.+np.arange(len(t))*.01;a=b+.2;candidates=np.array([base,base+260,base+760,base+1260],np.int64)
 z=candidate_fitted_intensities(t,b,a,'2026-01-06',candidates,p);assert z.shape==(4,FITTED_INTENSITY_COUNT) and np.isfinite(z).all();np.testing.assert_allclose(z[:,:6],.1)
