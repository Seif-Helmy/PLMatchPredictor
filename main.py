from scraper import scrap_data_team_season_stats, scrap_data_team_past_fixtures





def main():
    get_and_format_club_fixtures_data()





def get_and_format_club_fixtures_data():

    # Scraping Data Past Seasons' Fixtures data and creating csv file
    csv_file_path = scrap_data_team_past_fixtures()

    # Formatting the Data


if __name__ == "__main__":
    main()
