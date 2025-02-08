from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import time
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)




def scrap_data_team_past_fixtures():

    # Sending request to access FBRef and retrieving HTML content
    fb_ref_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    page = requests.get(fb_ref_url)


    # Seasons that will get extracted, and final output table initialized
    years = [2024, 2023, 2022, 2021]
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
            club_page_soup = BeautifulSoup(club_page.text, features="lxml")
            # club_shooting_table_href = next(
            #     ("https://fbref.com" + club_page_hrefs["href"]
            #         for club_page_hrefs in club_page_soup.find_all("a", href=True)
            #         if "/all_comps/shooting/" in club_page_hrefs["href"]
            #      ),
            #     None
            # )

            club_page_hyperlinks = club_page_soup.find_all("a")
            shooting_table_link = "https://fbref.com"
            for link in club_page_hyperlinks:
                shooting_link = link.get("href")
                if shooting_link and "/all_comps/shooting/" in shooting_link:
                    shooting_table_link += shooting_link
                    print(shooting_table_link)
                    break


            # Getting list of fixtures with shooting stats
            # club_shooting_fixture_page = requests.get(shooting_table_link)          # Request to download HTML
            # club_shooting_fixtures = pd.read_html(StringIO(club_shooting_fixture_page.text),
            #                                       match="Shooting")[0]
            #
            # club_shooting_fixtures.columns = club_shooting_fixtures.columns.droplevel()  # Dropping the first headers
            #
            # club_fixtures = club_fixtures[["Date", "Comp", "Venue", "Result", "GF", "GA",
            #                               "Opponent", "xG", "xGA", "Poss"]]
            #
            # try:
            #     fixtures = club_fixtures.merge(club_shooting_fixtures[
            #                                        ["Date", "Sh", "SoT", "SoT%", "G/Sh", "G/SoT"]], on="Date")
            # except ValueError:
            #     continue
            #
            #
            # fixtures = fixtures[fixtures["Comp"] == "Premier League"]
            # fixtures["Season"] = season
            # fixtures["Club"] = club_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
            # all_fixtures.append(fixtures)
            # time.sleep(8)


        page = requests.get("https://fbref.com" + page_soup.select("a.prev")[0].get("href"))



    all_fixtures_df = pd.concat(all_fixtures)
    all_fixtures_df.to_csv("AllFixtures.csv")



scrap_data_team_past_fixtures()








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

    season_stats = pd.merge(current_form_table, ag_shootings_df, on="Squad")

    season_stats.to_csv("AllFixtures.csv")


