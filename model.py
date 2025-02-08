import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score


class MissingDict(dict):
    __missing__ = lambda self, key: key



map_values = {"Brighton and Hove Albion": "Brighton",
              "Manchester United": "Manchester Utd",
              "Newcastle United": "Newcastle Utd",
              "Tottenham Hotspur": "Tottenham",
              "West Ham United": "West Ham",
              "Wolverhampton Wanderers": "Wolves"}

mapping = MissingDict(**map_values)


def cleanup_data(csv_file):
    past_fixtures = pd.read_csv("AllFixtures.csv", index_col=0)

    past_fixtures["Date"] = pd.to_datetime(past_fixtures["Date"])                               # Turns the Date into a Daytime object
    past_fixtures["Venue"] = past_fixtures["Venue"].map({"Home": 0, "Away": 1})                 # 0 = Home, 1 = Away
    past_fixtures["OppCode"] = past_fixtures["Opponent"].astype("category").cat.codes
    past_fixtures["Result"] = past_fixtures["Result"].map({"W": 1, "D": -1, "L": -1})            # 1 = Win, 0 = Draw, -1 = Loss


    predictors = ["Venue", "OppCode"]

    predictors_rolling = ["GF", "GA", "Poss", "Sh", "SoT", "SoT%",  "G/Sh", "G/SoT"]
    new_predictors_rolling = [f"{c}_Rolling" for c in predictors_rolling]

    past_fixtures_rolling = past_fixtures.groupby("Club", group_keys=True).apply(lambda x:
                              rolling_averages(x, predictors_rolling, new_predictors_rolling), include_groups=False)

    past_fixtures_rolling = past_fixtures_rolling.assign(Club=past_fixtures_rolling.index.get_level_values(0))

    past_fixtures_rolling = past_fixtures_rolling.droplevel("Club")
    past_fixtures_rolling.index = range(past_fixtures_rolling.shape[0])


    make_predictions(past_fixtures_rolling, predictors + new_predictors_rolling)


def rolling_averages(group, cols, new_cols):

    group = group.sort_values("Date")
    rolling_stats = group[cols].rolling(5, closed="left").mean()

    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group
    pass


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



cleanup_data(None)
