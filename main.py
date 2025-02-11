from scraper import scrap_data_team_season_stats, scrap_data_team_past_fixtures
from cleaner import clean_fixtures_table





def main():
    fixtures_data, predictors = get_and_clean_club_fixtures_data()

    print(fixtures_data)





def get_and_clean_club_fixtures_data():

    # Scraping Data Past Seasons' Fixtures data and creating csv file
    csv_file_path = scrap_data_team_past_fixtures()

    # Cleaning the Data
    return clean_fixtures_table(csv_file_path, 8)







if __name__ == "__main__":
    main()
