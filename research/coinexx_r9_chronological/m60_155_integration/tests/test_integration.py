"""Small synthetic integration unit tests; no 72M-quote data reconstruction."""
import csv
import io
import json
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone

import numpy as np

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import score_snapshot as s
import frozen_snapshot as f


def sample(model_id="final_is"):
    year,month=(2026,11) if model_id=="final_is" else (2026,int(model_id[-2:]))
    ms=int(datetime(year,month,2,tzinfo=timezone.utc).timestamp()*1000)
    return dict(
        schema_id=s.SCHEMA,market_source="Coinexx",
        feature_origin="FROZEN_EXACT_ASOF",
        time_msc=ms,feature_end_time_msc=ms,source_ordinal=123,
        account_login=123456,magic=5559,symbol="XAUUSD",
        bid_cents=400000,ask_cents=400020,side=1,
        features=[0.0]*155,
    )


class DummyModel:
    def predict_proba(self, x):
        assert x.shape==(1,155)
        return np.asarray([[0.875,0.125]],dtype=np.float64)


class ModelBridgeTests(unittest.TestCase):
    def test_correct_155_and_fold_month(self):
        x=s.validate_snapshot(sample(), "final_is")
        self.assertEqual(x.shape,(1,155))
        self.assertEqual(s.validate_snapshot(sample("fold05"),"fold05").shape,(1,155))

    def test_prevent_in_sample_period_mislabelled_out_of_sample(self):
        with self.assertRaises(ValueError):
            s.validate_snapshot(sample("fold05"),"final_is")
        with self.assertRaises(ValueError):
            s.validate_snapshot(sample("fold05"),"fold06")

    def test_partial_and_future_vectors_fail_closed(self):
        for key,val in (("features",[0.0]*154),
                        ("feature_end_time_msc",sample()["time_msc"]+1),
                        ("bid_cents",400030),
                        ("market_source","Dukascopy"),
                        ("feature_origin","FABRICATED")):
            obj=sample()
            obj[key]=val
            with self.assertRaises(ValueError,msg=key):
                s.validate_snapshot(obj,"final_is")

    def test_zero_finite_missing_values_valid(self):
        obj=sample()
        obj["features"][12]=None
        arr=s.validate_snapshot(obj,"final_is")
        self.assertTrue(np.isnan(arr[0,12]))

    def test_model_output_packet_and_atomic_file(self):
        obj=sample()
        digest=s.EXPECTED["final_is"][1]
        score,packet=s.predict_one(DummyModel(),digest,"final_is",obj)
        self.assertAlmostEqual(score,.125)
        self.assertEqual(len(packet),16)
        self.assertEqual(packet[0],"R9M60_155_V1")
        self.assertEqual(packet[9],digest)
        self.assertEqual(packet[13],"0.125")
        with tempfile.TemporaryDirectory() as td:
            path=pathlib.Path(td)
            file=s.packet_filename(obj)
            s.write_packet_atomic(path,file,packet)
            with (path/file).open(newline="",encoding="ascii") as fh:
                data=list(csv.reader(fh))
            self.assertEqual(data,[packet])
            self.assertEqual(len(list(path.iterdir())),1)

    def test_exact_schema_feature_position(self):
        old=np.arange(145,dtype=np.float32)
        ev=np.arange(77,dtype=np.float32)*0.1
        pr=np.arange(23,dtype=np.float32)
        fn=lambda events,spread,stop,target,side: np.full((1,11),9.0,dtype=np.float32)
        x=f.assemble_feature_vector(old,ev,pr,1,20,40,80,fn)
        self.assertEqual(len(x),155)
        self.assertEqual(float(x[0]),0.0)
        self.assertEqual(float(x[14]),14.0)
        self.assertEqual(float(x[14+len(f.OLD_HFT_IDX)]),0.0)
        self.assertEqual(float(x[-5]),1.0)
        self.assertEqual(float(x[-4]),1.0)
        self.assertEqual(float(x[-1]),20.0)
        self.assertTrue(np.all(x[139:150]==9.0))

    def test_invalid_geometry_rejected(self):
        fn=lambda *a:np.ones((1,11),np.float32)
        with self.assertRaises(ValueError):
            f.assemble_feature_vector(np.zeros(145),np.zeros(77),
                                      np.zeros(23),1,20,0,50,fn)


if __name__=="__main__":
    unittest.main()
