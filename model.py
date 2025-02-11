import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score




# MODEL NOT PERFORMING WELL
# NEED TO INTEGRATE TEH SECOND TABLE SCRAPPED FROM SCRAPPER.PY
def make_predictions(data, predictors):
    pl_data = pd.read_csv(data, index_col=0)


    # Since the model takes data from the past to predict the future,
    # we must divide the train/test split by chronological order
    pl_data = pl_data.sort_values("Date")


    # Here we use an 90%/10% train/test split
    splitting_index = int(len(pl_data) * 0.9)
    training_data = pl_data.iloc[:splitting_index]
    test_data = pl_data[splitting_index:]


    # Define the predictors X and the target variables Y
    x_train, y_train = training_data[predictors], training_data["Result"]
    x_test, y_test = test_data[predictors], test_data["Result"]


    # Initialise the RandForrest model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(x_train, y_train)


    # Test the model
    predictions = rf_model.predict(x_test)


    # Evaluate model
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)


    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")





make_predictions("CleanedAllFixtures.csv",
                 ["Venue", "OppCode", "ClubCode", "GF_Rolling", "GA_Rolling", "Poss_Rolling", "Sh_Rolling",
                  "SoT_Rolling", "SoT%_Rolling", "G/Sh_Rolling", "G/SoT_Rolling"])


