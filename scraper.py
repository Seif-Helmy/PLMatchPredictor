from bs4 import BeautifulSoup
import requests


def scrap_data():
    url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    website = requests.get(url)

    if website.status_code == 200:
        print("good")
    else:
        print("mot")








