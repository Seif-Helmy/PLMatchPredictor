from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score




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



