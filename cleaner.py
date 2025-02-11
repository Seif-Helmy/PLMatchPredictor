import pandas as pd
# pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns




# The current_form_games takes the number of games that should be considered before
# the game we are trying to predict to compute the rolling averages for.
def clean_fixtures_table(csv_file, current_form_games):

    # Loading the csv file as a pandas DataFrame
    past_fixtures = pd.read_csv(csv_file, index_col=0)


    # The Club Column and Opponent Column do not match
    standardize_opponent_names(past_fixtures)


    # Turns the Date into a datetime object
    # Turns the Home and Away t a numeric value
    # Gives Each Team a respective OppCode
    # So far we're trying to predict wins and so 1 is for win.
    past_fixtures["Date"] = pd.to_datetime(past_fixtures["Date"])
    past_fixtures["Venue"] = past_fixtures["Venue"].map({"Home": 0, "Away": 1})
    past_fixtures["OppCode"] = past_fixtures["Opponent"].astype("category").cat.codes
    past_fixtures["Result"] = past_fixtures["Result"].map({"W": 1, "D": 0, "L": 0})



    # Here we add ClubCode which needs to match with OppCode for the same team
    # This is done by finding the mapping between Opponent and OppCode then reusing the mapping on th Club Column
    # This is why we had to standardise the names between the Opponent and Club Columns
    club_mapping = past_fixtures.set_index("Opponent")["OppCode"].to_dict()
    past_fixtures["ClubCode"] = past_fixtures["Club"].map(club_mapping)



    # The way the model is going to work is that we get the rolling averages of the past 10 games before each game
    # and use that to determine the output of the current game
    predictors_to_be_rolled = ["GF", "GA", "Poss", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT"]
    new_predictors_rolling = [f"{c}_Rolling" for c in predictors_to_be_rolled]



    # The following computes the rolling averages and adds them to their respective columns
    # For each Club we sort their games and the function puts them in chronological order
    # Then compute ethe mean of certain column to get the tolling averages of the past 10 games
    # The Club Column gets removed, so we need to re add it and drop the level the group by columns
    past_fixtures_with_rolling = past_fixtures.groupby("Club", group_keys=True).apply(
        lambda x: rolling_averages(x, predictors_to_be_rolled, new_predictors_rolling, current_form_games), include_groups=False)
    past_fixtures_with_rolling = past_fixtures_with_rolling.assign(Club=past_fixtures_with_rolling.index.get_level_values(0))
    past_fixtures_with_rolling = past_fixtures_with_rolling.droplevel("Club")




    # makes first column index Unique again and not grouped by teams
    # Dropping unnecessary columns from the Data
    past_fixtures_with_rolling.index = range(past_fixtures_with_rolling.shape[0])
    past_fixtures_with_rolling = past_fixtures_with_rolling.drop(
        columns=['Comp', 'xG', 'xGA', 'Poss', 'Sh', 'SoT', 'SoT%', 'G/Sh', 'G/SoT'])


    # list of final predictors
    final_predictors = ["Venue", "OppCode", "ClubCode", "GF_Rolling", "GA_Rolling", "Poss_Rolling",
                        "Sh_Rolling", "SoT_Rolling", "SoT%_Rolling", "G/Sh_Rolling", "G/SoT_Rolling"]



    # Good test with the rolling average "game" parameter size for method 1
    # the more you increase the number of games rolled, the more exponentially it removes rows
    # print(past_fixtures.shape)
    # print(past_fixtures["Club"].value_counts())
    # print()
    # print()
    # print(past_fixtures_with_rolling.shape)
    # print(past_fixtures_with_rolling["Club"].value_counts())



    past_fixtures_with_rolling.to_csv("CleanedAllFixtures.csv", index=True)
    return "CleanedAllFixtures.csv", final_predictors







# Has a dictionary with the teams that have a different name between the Opponent column and the Club Column
# Changes the names of the teams in the Opponent Column to their respective name in the Club Column
def standardize_opponent_names(df):
    opponent_to_club_map = {
        "Brighton": "Brighton and Hove Albion",
        "Manchester Utd": "Manchester United",
        "Newcastle Utd": "Newcastle United",
        "Nott'ham Forest": "Nottingham Forest",
        "Sheffield Utd": "Sheffield United",
        "Tottenham": "Tottenham Hotspur",
        "West Ham": "West Ham United",
        "Wolves": "Wolverhampton Wanderers"
    }

    df["Opponent"] = df["Opponent"].replace(opponent_to_club_map)

    return df





# ROLLING AVERAGE FUNCTION HAS A LOT OF POWER OVER THE MODEL
# THE DROP NA REMOVES ALOT OF MATCHES DEPENDING ON THE GAMES PARAMETER IN METHOD 1
# METHOD 2 IS NOT ACCURATE BUT CLOSE ENOUGH. IT GIVES THE CLOSEST VALUE T THE GAME WHERE WE CAN'T COMPUTE
# Calculates rolling averages of the statistics column into the rolling columns.
# Puts data that is already grouped by club in chronological order to compute the averages of the past 10 games
def rolling_averages(group, stats, rolling_cols, games=10):
    group = group.sort_values("Date")
    rolling_stats = group[stats].rolling(games, min_periods=1, closed="left").mean()

    # METHOD 1
    # group[rolling_cols] = rolling_stats
    # return group.dropna(subset=rolling_cols)

    # METHOD 2
    group[rolling_cols] = rolling_stats.bfill()
    return group

