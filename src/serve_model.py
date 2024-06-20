import os
import pickle
import pandas as pd
from src.data_model import Lead, Version


MODEL_STORE_DIR = "models/model_store"
    

def get_prediction(lead_instance : dict | Lead, version_string : str | Version) -> tuple:
    lead_dict = lead_instance.model_dump() if isinstance(lead_instance, Lead) else lead_instance
    v_string = version_string.value if isinstance(version_string, Version) else version_string

    # Load the correct model version.
    with open(os.path.join(MODEL_STORE_DIR,v_string), 'rb') as f:
        model = pickle.load(f)
    # Convert lead instance to dataframe.
    lead_df = pd.DataFrame(lead_dict, index=[0])
    # Run predictions
    predict_flag = model.predict(lead_df).item()
    probability = model.predict_proba(lead_df).item(1)
    return (predict_flag, probability)


