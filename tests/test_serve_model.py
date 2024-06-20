# Insert the current directory into the search path.
# This lets us import in the same context as the project root directory.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import unittest
import json

from main.ServeModel import get_prediction


def load_json_to_dict(filename: str) -> dict:
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# Load cases
case_lead_flag = load_json_to_dict("tests/case_lead_flag.json")

# Tests
class TestGetPrediction(unittest.TestCase):

    def test_get_prediction(self):
        pred = get_prediction(case_lead_flag["lead"], "v0.0")
        self.assertTrue(isinstance(pred, tuple))


if __name__ == '__main__':
    unittest.main()