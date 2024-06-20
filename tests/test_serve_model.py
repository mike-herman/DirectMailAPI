# Insert the current directory into the search path.
# This lets us import in the same context as the project root directory.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import unittest
import json

from src.serve_model import get_prediction
from src.data_model import Lead, Version


def load_json_to_dict(filename: str) -> dict:
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# Load cases
case_lead_flag = load_json_to_dict("tests/case_lead_flag.json")
case_lead = Lead(**case_lead_flag["lead"])
case_version = Version("v0.0")

# Tests
class TestGetPrediction(unittest.TestCase):

    def test_get_prediction_dict_input(self):
        pred = get_prediction(case_lead_flag["lead"], "v0.0")
        self.assertTrue(isinstance(pred, tuple))
        self.assertTrue(pred[0] == 0)
        self.assertTrue(pred[1] < 0.50)
    
    def test_get_prediction_type_input(self):
        pred = get_prediction(case_lead,case_version)
        self.assertTrue(isinstance(pred,tuple))
        self.assertTrue(pred[0] == 0)
        self.assertTrue(pred[1] < 0.50)



if __name__ == '__main__':
    unittest.main()