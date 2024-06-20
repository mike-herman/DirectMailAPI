# pip install fastapi
from fastapi import FastAPI
from pydantic import BaseModel
from src.data_model import DM_Prediction_Request, DM_Prediction_Response, Prediction
from src.serve_model import get_prediction

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

@app.get("/healthcheck")
def read_root():
    return {"status": "ok"}


@app.post("/item/")
def create_item(item: Item):
    return item

@app.post("/dm_response_predict/")
def predict_response(dm_prediction_request: DM_Prediction_Request):
    version_string = dm_prediction_request.version
    lead_instance = dm_prediction_request.lead
    predict_flag, probability = get_prediction(lead_instance, version_string)
    prediction_dict = {"version":version_string, "predict_flag":predict_flag, "probability":probability}
    prediction = Prediction(**prediction_dict)
    response = DM_Prediction_Response(**{"lead":lead_instance,"prediction":prediction})
    return response