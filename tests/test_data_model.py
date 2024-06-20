# Insert the current directory into the search path.
# This lets us import in the same context as the project root directory.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import unittest
import json

from src.data_model import DM_Prediction_Request, DM_Prediction_Response

with open("tests/case_lead_flag.json", "r") as f:
    case_lead_flag_raw = f.read().replace("\n","").replace(" ","")

case_lead_flag = json.loads(case_lead_flag_raw)

class TestValidateRequest(unittest.TestCase):

    def test_validate_json_string(self):
        req = DM_Prediction_Request.model_validate_json(case_lead_flag_raw)
        self.assertTrue(isinstance(req, DM_Prediction_Request))
        self.assertTrue(req.version == "v0.0")
    
class TestValidateResponse(unittest.TestCase):
    response_dict = {
        "lead":case_lead_flag["lead"],
        "prediction":{
            "predict_flag":0,
            "probability":0.08,
            "version":"v0.0"
        }
    }
    def test_validate_response_dict(self):
        resp = DM_Prediction_Response.model_validate(self.response_dict)
        self.assertTrue(isinstance(resp, DM_Prediction_Response))
        self.assertTrue(resp.prediction.version == "v0.0")