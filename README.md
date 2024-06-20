---
title: Direct Mail API
author: Michael Herman
date: 2024-06-20
---
# Direct Mail Predictive Model API

This repo contais a basic API server. The main endpoint of the server is `/dm_response_predict`. It accepts a JSON payload containing all the data necessary to make the prediction. It returns a response JSON with the prediction itself.

## Use case
The predictive model here is based off of a [Kaggle competition](https://www.kaggle.com/datasets/dineshmk594/loan-campaign) for a loan campaign. In this campaign, the bank has a lits of existing customers and their attributes. It needs to know if the individual is likely to respond to a direct mail campaign (`1`) or not (`0`). Since probabilities are sometimes _more_ useful than a simple prediction, this API returns both the prediction and the probability.

This project represents an initial setup that can be iterated on with different versions of the model. To handle versioning, we require a `version` to be specified in the request. This lets the API know what version of the predictive model to use. New models could be added as new versions.

# Tooling
The following tools are used in this app:
- OpenAPI specification is used to specify the API endpoints and contract in the `api.pml` file. This file can also be used to automatically generate `pydantic` models, though it usually needs some manual tweaking.
- [fly.io](https://fly.io) is used to deploy. In practice, this could be deployed in any cloud service. But fly.io is extremely easy to set up and use.
- Docker is uesd to containerize the app.
- For the server, we use [FastAPI](https://fastapi.tiangolo.com/). FastAPI has some great features that include:
  - Integration with `pydantic` to validate inputs. This makes sure, for instance, you if a field requires a `float` that the API won't accept the string `"one"`. It's also great for ensuring a string is one of a given input list.
  - Once you're used to the `pydantic` typing, creting endpoints is remarkably easy.
  - It automatically creates a `/docs` endpoint with nice documentation of the contents.
- The code utilizes the [pydantic](https://pydantic.dev/) framework.
- The model itself is developed in the project and consists of a pickled `sklearn` model.
- While not shown in this project, I use Postman to check both local and production APIs.

# Project Organization

Here's how the project is organized. Feel free to browse.
- `main.py` is the main server file. It pulls from files in `src` directory to run the guts of the app.
- `src` directory contains the guts of the app.
  - `serve_model.py` will "serve" the predictive model. The primary function is `get_prediction` which accepts a dictionary (or `pydantic` model) with the individual's information along with the verison of the model to run. It returns a tuple with the prediction flag and a probability.
  - `data_model.py` contains the `pydantic` models. The `Lead` model contains all the information about the individual.
- `models` directory contains the predictive model files. This includes both the pickled models themselves and the notebooks used to create models.
  - `notebooks` is a directory that contains notebooks used to create the models. In this case, there's only one.
  - `model_store` contains the pickled models. The models are named after the version strings specified in the API. So if the API request specifies model "v0.0" then it will use the model saved to the file `models/model_store/v0.0`.
- `tets` is a test directory. It includes a file with a standard JSON request.
- The rest of the files are various configs.

# Where to find this model

This model is live!

You can see the API documentation at [https://directmailapi.fly.dev/docs](https://directmailapi.fly.dev/docs).

Or you can query the API itself in the terminal using the code below.

```
curl --location 'https://directmailapi.fly.dev/dm_response_predict/' \
--header 'Content-Type: application/json' \
--data '{
    "lead": {
        "BALANCE": 3383.75,
        "OCCUPATION": "SELF-EMP",
        "SCR": 776,
        "HOLDING_PERIOD": 30,
        "ACC_TYPE": "SA",
        "LEN_OF_RLTN_IN_MNTH": 146,
        "NO_OF_L_CR_TXNS": 7,
        "NO_OF_L_DR_TXNS": 3,
        "NO_OF_BR_CSH_WDL_DR_TXNS": 0,
        "NO_OF_ATM_DR_TXNS": 1,
        "NO_OF_NET_DR_TXNS": 2,
        "NO_OF_MOB_DR_TXNS": 0,
        "NO_OF_CHQ_DR_TXNS": 0,
        "FLG_HAS_CC": 0,
        "AMT_ATM_DR": 13100,
        "AMT_BR_CSH_WDL_DR": 0,
        "AMT_CHQ_DR": 0,
        "AMT_NET_DR": 973557.0,
        "AMT_MOB_DR": 0,
        "AMT_L_DR": 986657.0,
        "FLG_HAS_ANY_CHGS": 0,
        "AMT_OTH_BK_ATM_USG_CHGS": 0,
        "AMT_MIN_BAL_NMC_CHGS": 0,
        "NO_OF_IW_CHQ_BNC_TXNS": 0,
        "NO_OF_OW_CHQ_BNC_TXNS": 0,
        "AVG_AMT_PER_ATM_TXN": 13100.0,
        "AVG_AMT_PER_CSH_WDL_TXN": 0.0,
        "AVG_AMT_PER_CHQ_TXN": 0.0,
        "AVG_AMT_PER_NET_TXN": 486778.5,
        "AVG_AMT_PER_MOB_TXN": 0.0,
        "FLG_HAS_NOMINEE": 1,
        "FLG_HAS_OLD_LOAN": 1
    },
    "version": "v0.0"
}'
```