# Direct Mail Predictive Model API

This repo contais a basic API server. The main endpoint of the server is `/dm_response_predict`. It accepts a JSON payload containing all the data necessary to make the prediction. It returns a response JSON with the prediction itself.

## Use case
The predictive model here is based off of a [Kaggle competition](https://www.kaggle.com/datasets/dineshmk594/loan-campaign) for a loan campaign. In this campaign, the bank has a lits of existing customers and their attributes. It needs to know if the individual is likely to respond to a direct mail campaign (`1`) or not (`0`). Since probabilities are sometimes _more_ useful than a simple prediction, this API returns both the prediction and the probability.

This project represents an initial setup that can be iterated on with different versions of the model. To handle versioning, we require a `version` to be specified in the request. This lets the API know what version of the predictive model to use. New models could be added as new versions.

# Tooling
The following tools are used in this app:
- OpenAPI specification is used to specify the API endpoints and contract in the `api.pml` file. This file can also be used to automatically generate `pydantic` models, though it usually needs some manual tweaking.
- [fly.io](https://fly.io) is used to deploy. In practice, this could be deployed in any cloud service. But fly.io is extremely easy to set up and use.
- Docker is used to containerize the app.
- For the server, we use [FastAPI](https://fastapi.tiangolo.com/). FastAPI has some great features that include:
  - Integration with `pydantic` to validate inputs. This makes sure, for instance, if a field requires a `float` that the API won't accept the string `"one"` (but it will accept and parse a string `"1"`). It's also great for ensuring a string is one of a given input list.
  - Once you're used to the `pydantic` typing, creating endpoints is remarkably easy.
  - It automatically creates a `/docs` endpoint with nice documentation of the contents.
- The code utilizes the [pydantic](https://pydantic.dev/) framework.
- The _predictive_ model is developed in a notebook in the project. It is a fitted `sklearn` pipeline that we have fitted and pickled to a file.
- While not shown in this project, I use Postman to check both local and production APIs.

# Project Organization

Here's how the project is organized. Feel free to browse.
- `main.py` is the main server file. It pulls from files in `src` directory to run the guts of the app.
- `src` directory contains most of the API logic.
  - `serve_model.py` will "serve" the predictive model. The primary function is `get_prediction` which accepts a dictionary (or `pydantic` model) with the individual's information along with the verison of the model to run. It returns a tuple with the prediction flag and a probability.
  - `data_model.py` contains the `pydantic` models. The `Lead` model contains all the information about the individual.
- `models` directory contains the predictive model files. This includes both the pickled models themselves and the notebooks used to create models.
  - `notebooks` is a directory that contains notebooks used to create the models. In this case, there's only one.
  - `model_store` contains the pickled models. The models are named after the version strings specified in the API. So if the API request specifies model "v0.0" then it will use the model saved to the file `models/model_store/v0.0`.
- `tets` is a test directory. It includes a file with a standard JSON request.
- The rest of the files are various configs.

# The Predictive Model
This was developed off of a Kaggle data set on direct mail. It is one of a few data sets I keep around for general use. You can read more about it and see field definitions [here](https://github.com/mike-herman/credit_datasets). This is a pretty clean dataset to begin with, so cleaning and imputing missing fields wasn't necessary. In most cases though, we would expect to have incomplete information that would require imputation. That would be built into the model.

To make the scenario and analysis more realistic, I madee some assumptions about the costs and benefits. Specifically, I assumed a single direct mailer costs $1 to send and that the average present value of a loan's cashflows is $1,900. When fitting the model, I chose not to use a standard utility metric and instead to explicitly maximize the economic profit. This is done by defining a custom scoring function:
```
def direct_mail_score_func(y_true, y_proba):
    """ Expected profit from campaign.

    This uses the probability of response to calculate the mail cost and origination value.
    It return sthe expected profit from the campaign.
    """
    mail_cost = y_proba.sum() * -1
    origination_value = (y_proba * y_true).sum() * 380
    return origination_value - mail_cost

direct_mail_score = make_scorer(direct_mail_score_func,greater_is_better=True,response_method="predict_proba")
```

I used an `xgboost` classifier as a model because it tends to work pretty well out-of-the-box. For the first version, I chose not to do further feature engineering.

Despite not explicitly using `auc` as a scoring metric, the model had a fairly high AUC score of 91%. On a test set of 4,000 data points, the model would select 7.2% of individuals to target and would expect a 92.7% response rate. This would leave out 264 individuals who _would have_ responded if mailed. But lowering our targeting threshold to capture those individuals would require sending more mailers than we would recoup in expected profit.

You can read more about the model development in the `models/notebooks/model_notebook.ipynb` file.

# The Workflow

This project is meant to be a jumping off point for an ongoing model used by an organization. The workflow to further improve this application would look like this.

1. Create a new notebook to develop a new version of the model. You'll need to specify the S3 or database connection to wherever the data is. Develop the model as needed. Once you find the `best_model` and finish the final `best_model.fit()`, you can pickle that model object to models/mode_store/vX.X.
2. Add "vX.X" to the api.yml file enums and the data_model.py enums. Assuming we're not using any new data fields, no other changes to data_model.py or serve_model.py should be necessary. If we are using new data fields (e.g. new columns specified in the request API) then we'll need to edit the api.yml, the and data_model.py file accordingly.
3. Create and run unit tests in the tests directory. Make sure they all pass.
4. Start the application locally by running `fastapi dev main.py` in the terminal. This will launch the app to http://localhost:8080. Run some test queries on the local API (e.g. using Postman).
5. If deploying using fly.io, all you need to do is `fly deploy` in the terminal to deploy the new application model.
6. Run some test queries on the production server (e.g. using Postman).

## Things to add
- In this case, I have not set up a separate fly.io test server to delpoy to. Typically, this would be done before step 5 above.
- We would want to implement proper logging in this deployment. That may require setting up a log store in fly.io.
- The `apy.yml` file only documents the main endpoint, but typically all of them would be documented there.

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