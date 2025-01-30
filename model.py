import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)




def cleanup_data(csv_file):
    past_fixtures = pd.read_csv("AllFixtures.csv", index_col=0)
    # print(past_fixtures.dtypes)

    # print(past_fixtures["Opponent"].value_counts())

    past_fixtures["Date"] = pd.to_datetime(past_fixtures["Date"])               # Turns the Date into a Daytime object
    past_fixtures["Venue"] = past_fixtures["Venue"].map({"Home": 0, "Away": 1})               # 0 = Home, 1 = Away
    past_fixtures["OppCode"] = past_fixtures["Opponent"].astype("category").cat.codes
    past_fixtures["Result"] = past_fixtures["Result"].map({"W": 1, "D": 0, "L": -1})      # 1 = Win, 0 = Draw, -1 = Loss


    rf = RandomForestClassifier(n_estimators=50, min_samples_split=10, random_state=1)

    training = past_fixtures[past_fixtures["Date"] < "2024-07-30"]
    print(training)
    test = past_fixtures[past_fixtures["Date"] > "2024-07-30"]
    print(test)

    predictors = ["Venue", "Result", "GF", "GA", "OppCode", "Poss", "Sh", "SoT", "SoT%",  "G/Sh", "G/SoT"]
    rf.fit(training[predictors], training["Result"])

    pred = rf.predict(test[predictors])

    print(accuracy_score(test["Result"], pred))
    print()
    print()
    print()
    print(past_fixtures.head())




cleanup_data(None)
