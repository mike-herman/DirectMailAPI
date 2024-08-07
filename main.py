# pip install fastapi
from fastapi import FastAPI
from pydantic import BaseModel
from src.data_model import DM_Prediction_Request, DM_Prediction_Response, Prediction
from src.serve_model import get_prediction

import logfire

app = FastAPI()

logfire.configure()
logfire.instrument_fastapi(app)

@app.get("/")
def hello():
    hello_dict = {
        "endpoints": {
            "/": "This page.",
            "/healthcheck": "Returns the status of the API.",
            "/dm_response_predict": "Accepts a JSON payload and returns the prediction results.",
            "/docs" : "Provides documentation for the API.",
        }
    }
    return hello_dict

@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}

@app.post("/dm_response_predict/")
def predict_response(dm_prediction_request: DM_Prediction_Request):
    version_string = dm_prediction_request.version
    lead_instance = dm_prediction_request.lead
    predict_flag, probability = get_prediction(lead_instance, version_string)
    prediction_dict = {"version":version_string, "predict_flag":predict_flag, "probability":probability}
    prediction = Prediction(**prediction_dict)
    response = DM_Prediction_Response(**{"lead":lead_instance,"prediction":prediction})
    return response