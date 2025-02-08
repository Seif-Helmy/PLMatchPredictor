import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score



# TODO : Optimize and Improve Model
# SCRAPER.PY AND CLEANER.PY ARE COMPLETE
def make_predictions(data, predictors):

    rf = RandomForestClassifier(n_estimators=100, random_state=42)

    training = data[data["Date"] < "2024-07-30"]
    test = data[data["Date"] > "2024-07-30"]

    rf.fit(training[predictors], training["Result"])
    prediction = rf.predict(test[predictors])

    accuracy = accuracy_score(test["Result"], prediction)

    precision = precision_score(test["Result"], prediction)

    print(precision)
    print(accuracy)



make_predictions(pd.read_csv("CleanedAllFixtures.csv", index_col=0),
                 ["Venue", "OppCode", "ClubCode", "GF_Rolling", "GA_Rolling", "Poss_Rolling", "Sh_Rolling",
                  "SoT_Rolling", "SoT%_Rolling", "G/Sh_Rolling", "G/SoT_Rolling"])


