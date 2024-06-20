import os
import pickle
import pandas as pd

MODEL_STORE_DIR = "models/model_store"

def get_prediction(request_dict : dict, version_str : str) -> dict:
    model_path = os.path.join(MODEL_STORE_DIR,version_str)
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    instance_df = pd.DataFrame(request_dict["lead"],index=[0])
    prediction = model.predict(instance_df).item()
    out_dict = dict()
    out_dict["lead"] = request_dict["lead"]
    out_dict["will_respond"] = prediction
    return out_dict
    

