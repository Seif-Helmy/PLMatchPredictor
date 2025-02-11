from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import time









# If there's issue with requesting the page, run this to know how long to wait before retrying
def check_page_request(page):

    if page.status_code == 200:
        print("Page request is working!")

    else:
        print(f"Error: {page.status_code}")

        if page.status_code == 429:
            retry_after = page.headers.get("Retry-After")
            wait_time = int(retry_after)
            print(f"Rate limit hit. Retrying after {wait_time} seconds...")










# Scraps all fixture of the previous $ seasons of the PL with statistics with each feature
def scrap_data_team_past_fixtures():

    # Sending request to access FBRef and retrieving HTML content
    fb_ref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    page = requests.get(fb_ref_url)


    # Seasons that will get extracted, and final output table initialized
    years = [2024.2025, 2023.2024, 2022.2023, 2021.2022]
    all_fixtures = []



    for season in years:

        # Using Beautiful Soup to find all the hyperlinks for each club in the respective season
        # Tables on the website are of the class "table.stats_table" and we want the first one
        page_soup = BeautifulSoup(page.text, features="lxml")
        prem_table = page_soup.select("table.stats_table")[0]



        # From the first table (standings table) we need to get all the hyperlinks for each Club
        # We do this by getting all the anchor tags with hyperlinks and filtering them.
        list_of_team_links = [
            "https://fbref.com" + team["href"]
                for team in prem_table.find_all("a", href=True)
                    if "/squads/" in team["href"]
        ]



        # For each club we want to extract certain stats from their home page
        for club_url in list_of_team_links:


            # Getting first "Scores & Fixtures" table
            # Use Pandas here directly as we want to extract tables only and not HTML element like before
            club_page = requests.get(club_url)
            club_fixtures = pd.read_html(StringIO(club_page.text), match="Scores & Fixtures")[0]



            # On each club home page there's a hyperlink to their shooting stats per fixture
            # We want to access some shooting statistics for our predictions
            # For each anchor tag with a href value check if it is for the shooting table
            club_page_soup = BeautifulSoup(club_page.text, features="lxml")
            club_shooting_table_href = next(
                ("https://fbref.com" + club_page_hrefs["href"]
                    for club_page_hrefs in club_page_soup.find_all("a", href=True)
                    if "/all_comps/shooting/" in club_page_hrefs["href"]
                 ),
                None
            )



            # Accessing the Shootings Stats per fixture table of each team and getting certain statistics
            # The Shooting Stats per Fixture table is the first table on this page
            club_shooting_fixture_page = requests.get(club_shooting_table_href)
            print(club_url)
            club_shooting_fixtures = pd.read_html(StringIO(club_shooting_fixture_page.text), match="Shooting")[0]
            club_shooting_fixtures.columns = club_shooting_fixtures.columns.droplevel()



            # Keep these selected columns from the Fixture table of the club
            club_fixtures = club_fixtures[["Date", "Comp", "Venue", "Result", "GF", "GA",
                                          "Opponent", "xG", "xGA", "Poss"]]

            # Keep these selected columns from the Shootings Stats per Fixture table of the club
            club_shooting_fixtures = club_shooting_fixtures[["Date", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT"]]

            # Merging both Tables to get the full Fixture table of Each Club
            try:
                fixtures = club_fixtures.merge(club_shooting_fixtures, on="Date")
            except ValueError:
                continue



            # Final formatting of the Data
            # Removing all fixtures that are not in the Premier League
            # Adding a Column to indicate the Season, and a column to Indicate the club
            fixtures = fixtures[fixtures["Comp"] == "Premier League"]
            fixtures["Season"] = season
            fixtures["Club"] = club_url.split("/")[-1].replace("-Stats", "").replace("-", " ")


            # Appending to data frame to the all fixtures list and waiting to not get blocked from website
            all_fixtures.append(fixtures)
            time.sleep(10)



        # Changing the page to the Premier League Standings page of the previous season.
        page = requests.get("https://fbref.com" + page_soup.select("a.prev")[0].get("href"))



    # Appending all the Dataframes in the list to each other to make on Data frame
    # THen outputting the DataFrame as a csv
    all_fixtures_df = pd.concat(all_fixtures)
    all_fixtures_df.to_csv("AllFixtures.csv")

    return "AllFixtures.csv"









# Fetches this season's team statistics for each team
# TODO : Figure out how to incorporate this
# TODO : Properly comment this function
def scrap_data_team_season_stats():
    fb_ref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    page = requests.get(fb_ref_url)
    standard_stats_df = pd.read_html(StringIO(page.text))[2]
    standard_stats_df.columns = standard_stats_df.columns.droplevel()


    standard_stats_df = standard_stats_df[["Squad", "Poss", "Gls", "G+A", "PrgP", "Gls"]]
    standard_stats_df.columns.values[3] = "Gls/90"
    standard_stats_df.columns.values[5] = "Drop"
    standard_stats_df.columns.values[7] = "Drop"
    standard_stats_df.columns.values[8] = "Drop"
    standard_stats_df = standard_stats_df.drop(columns=standard_stats_df.columns[[5]])


    standings_df = pd.read_html(StringIO(page.text))[1]
    standings_df.columns = standings_df.columns.droplevel()
    standings_df = standings_df[["Rk", "Squad"]]

    current_form_table = pd.merge(standard_stats_df, standings_df, on="Squad")


    shootings_df = pd.read_html(StringIO(page.text))[8]
    shootings_df.columns = shootings_df.columns.droplevel()
    shootings_df = shootings_df[["Squad", "SoT", "SoT/90", "G/SoT"]]

    current_form_table = pd.merge(current_form_table, shootings_df, on="Squad")


    ag_shootings_df = pd.read_html(StringIO(page.text))[9]
    ag_shootings_df.columns = ag_shootings_df.columns.droplevel()
    ag_shootings_df = ag_shootings_df[["Squad", "Gls", "SoT", "G/SoT"]]
    ag_shootings_df.columns.values[1] = "Vs-Gls"
    ag_shootings_df.columns.values[2] = "Vs-SoT"
    ag_shootings_df.columns.values[3] = "Vs-G/SoT"
    ag_shootings_df["Squad"] = ag_shootings_df["Squad"].str.replace("vs ", "")

    season_stats = pd.merge(current_form_table, ag_shootings_df, on="Squad")

    season_stats.to_csv("ClubSeasonStats.csv")


