import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os
from pathlib import Path
import time

from helpers import TEAM_IDS, YEARS

FLARESOLVERR_URL = os.environ.get("FLARESOLVERR_URL", "http://localhost:8191/v1")

# create a session for efficiency when looping
session_resp = requests.post(FLARESOLVERR_URL, json={"cmd": "sessions.create", "session": "nfl_scraper"})

def fetch_html(url):
    resp = requests.post(FLARESOLVERR_URL, json={
        "cmd": "request.get",
        "url": url,
        "session": "nfl_scraper",
        "maxTimeout": 60000,
    })
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"FlareSolverr error fetching {url}: {data.get('message')}")
    return data["solution"]["response"]

def fetch_team_info(team_id, year):
    url = f"https://www.pro-football-reference.com/teams/{team_id}/{year}.htm"
    soup = BeautifulSoup(fetch_html(url), "html.parser")

    def get_table_by_id(table_id):
        table = soup.find("table", id=table_id)
        if table is None:
            raise RuntimeError(f"Table with id '{table_id}' not found")
        df = pd.read_html(StringIO(str(table)))[0]
        # Remove repeated header rows if any
        df = df[~(df == list(df.columns)).all(axis=1)]
        df.reset_index(drop=True, inplace=True)
        return df

    games = get_table_by_id("games")
    passing = get_table_by_id("passing")
    rushing_receiving = get_table_by_id("rushing_and_receiving")

    return games, passing, rushing_receiving

if __name__ == "__main__":
    games, passing, rushing_receiving = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # safely iterate over TEAM_IDS and YEARS, catching exceptions to avoid stopping the entire process
    for team_id in TEAM_IDS:
        for year in YEARS:
            try:
                g, p, rr = fetch_team_info(team_id, year)
                # add year and team column to each data frame with year value
                g['Year'] = year
                g['Team'] = team_id
                p['Year'] = year
                p['Team'] = team_id
                rr['Year'] = year
                rr['Team'] = team_id

                games = pd.concat([games, g], ignore_index=True)
                passing = pd.concat([passing, p], ignore_index=True)
                rushing_receiving = pd.concat([rushing_receiving, rr], ignore_index=True)
            except Exception as e:
                # some teams don't have specific years, catch exception and move on
                print(f"Error fetching data for {team_id} in {year}: {e}")
            time.sleep(1)
        #print(f"Completed data scrape for team {team_id}")

    print("=== 2024 Seasons ===")
    print(games.head())

    print("\n=== 2024 Passing Stats ===")
    print(passing.head())


    print("\n=== 2024 Rushing and Receiving Stats ===")
    print(rushing_receiving.head())

    # Optional: Save to CSV
    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent
    DATA = os.path.join(root_dir, "Data")
    os.makedirs(DATA, exist_ok=True)

    games.to_csv(os.path.join(DATA, "seasons.csv"), index=False)
    passing.to_csv(os.path.join(DATA, "passing.csv"), index=False)
    rushing_receiving.to_csv(os.path.join(DATA, "rushing_receiving.csv"), index=False)

    # Clean up the session after scraping is complete
    requests.post(FLARESOLVERR_URL, json={"cmd": "sessions.destroy", "session": "nfl_scraper"})