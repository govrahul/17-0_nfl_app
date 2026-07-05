import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os

def fetch_team_info(team_id, year):
    url = f"https://www.pro-football-reference.com/teams/{team_id}/{year}.htm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

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
    games, passing, rushing_receiving = fetch_team_info("det", 2024)

    print("=== 2024 Seasons ===")
    print(games.head())

    print("\n=== 2024 Passing Stats ===")
    print(passing.head())


    print("\n=== 2024 Rushing and Receiving Stats ===")
    print(rushing_receiving.head())

    # Optional: Save to CSV
    # set data folder path
    DATA = os.path.join(os.path.dirname(__file__), "Data")

    games.to_csv(os.path.join(DATA, "lions_2024_season.csv"), index=False)
    passing.to_csv(os.path.join(DATA, "lions_2024_passing.csv"), index=False)
    rushing_receiving.to_csv(os.path.join(DATA, "lions_2024_rushing_receiving.csv"), index=False)