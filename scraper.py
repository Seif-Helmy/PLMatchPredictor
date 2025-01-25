from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import time
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)


def scrap_data_team_past_fixtures():

    # Sending request to access FBRef
    fb_ref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    # ================== 1 ================== #
    # Extracting all the past fixtures from last three seasons (2024/2025, 2023/2024, 2022/2023)
    # with key statistics from each match
    years = [2024, 2023, 2022, 2021]
    all_fixtures = []

    for season in years:
        page = requests.get(fb_ref_url)                                             # Request to download HTML of page
        page_soup = BeautifulSoup(page.text, features="lxml")                       # Soup page
        prem_table = page_soup.select("table.stats_table")[0]                       # Access prem table


        links = prem_table.find_all("a")                                           # Get all Anchor tags from table
        # === Getting all club URLS === #
        list_of_team_links = []
        for team in links:                                                          # for each anchor tag
            link = team.get("href")                                                 # Getting href attribute from a-tag
            if "/squads/" in link:                                                  # if it is a squads href
                list_of_team_links.append("https://fbref.com" + link)               # Add to the list of squad pages

        fb_ref_url = "https://fbref.com" + page_soup.select("a.prev")[0].get("href")

        for club_url in list_of_team_links:

            club_name = club_url.split("/")[-1].replace("-Stats", "").replace("-", " ")

            # Past fixtures
            club_page = requests.get(club_url)                                      # Request HTML of club page
            club_fixtures = pd.read_html(StringIO(club_page.text),
                                         match="Scores & Fixtures")[0]              # Get fixture table of club

            # Getting Additional shooting stats of past fixtures to assess form
            club_page_soup = BeautifulSoup(club_page.text, features="lxml")         # Making Soup of the club page
            club_page_links = club_page_soup.find_all("a")                          # Get all anchor tags on club page

            # Getting the href of the shooting table
            shooting_table_link = "https://fbref.com"
            for link in club_page_links:                                            # for all anchor tags
                shooting_link = link.get("href")                                    # get the href of all a-tags
                if shooting_link and "/all_comps/shooting/" in shooting_link:       # if a-tag is shooting
                    shooting_table_link += shooting_link                            # Get club shooting page link
                    break

            # Getting list of fixtures with shooting stats
            club_shooting_fixture_page = requests.get(shooting_table_link)          # Request to download HTML
            club_shooting_fixtures = pd.read_html(StringIO(club_shooting_fixture_page.text),
                                                  match="Shooting")[0]

            club_shooting_fixtures.columns = club_shooting_fixtures.columns.droplevel()  # Dropping the first headers

            club_fixtures = club_fixtures[["Date", "Comp", "Venue", "Result", "GF", "GA",
                                          "Opponent", "xG", "xGA", "Poss"]]

            try:
                fixtures = club_fixtures.merge(club_shooting_fixtures[
                                                   ["Date", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT"]], on="Date")
            except ValueError:
                continue


            fixtures = fixtures[fixtures["Comp"] == "Premier League"]
            fixtures["Season"] = season
            fixtures["Club"] = club_name
            all_fixtures.append(fixtures)
            time.sleep(8)

    all_fixtures_df = pd.concat(all_fixtures)
    all_fixtures_df.to_csv("AllFixtures.csv")




def scrap_data_team_season_stats():
    fb_ref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

    page = requests.get(fb_ref_url)                                             # Request and download HTML of page
    standard_stats_df = pd.read_html(StringIO(page.text))[2]                    # Parse for third table on the page
    standard_stats_df.columns = standard_stats_df.columns.droplevel()           # drop first header column


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

    return pd.merge(current_form_table, ag_shootings_df, on="Squad")



scrap_data_team_past_fixtures()