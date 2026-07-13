"""Reproduces the data-prep steps from eda.ipynb as a script, so the
model-training CSVs can be regenerated without manually running the notebook.

Reads:  Data/schedules.csv, Data/reg_player_stats.csv (from Scrapers/nfl_scraper.py)
Writes: Data/reg_combined_team_player_stats.csv, Data/team_season_points.csv
"""
import pandas as pd
import numpy as np

schedules = pd.read_csv("Data/schedules.csv")
player_stats = pd.read_csv("Data/reg_player_stats.csv")

schedules_reg = schedules[schedules["game_type"] == "REG"].copy()

# --- regular season team records (Win_Pct) ---
schedules_reg["Home_Win"] = np.where(schedules_reg["home_score"] > schedules_reg["away_score"], 1, 0)
schedules_reg["Home_Loss"] = np.where(schedules_reg["home_score"] < schedules_reg["away_score"], 1, 0)
schedules_reg["Away_Win"] = schedules_reg["Home_Loss"]
schedules_reg["Away_Loss"] = schedules_reg["Home_Win"]
schedules_reg["Tie"] = np.where(schedules_reg["home_score"] == schedules_reg["away_score"], 1, 0)

home_rec = (
    schedules_reg.groupby(["season", "home_team"])[["Home_Win", "Home_Loss", "Tie"]]
    .sum()
    .reset_index()
    .rename(columns={"home_team": "Team", "Home_Win": "Wins", "Home_Loss": "Losses", "Tie": "Ties"})
)
away_rec = (
    schedules_reg.groupby(["season", "away_team"])[["Away_Win", "Away_Loss", "Tie"]]
    .sum()
    .reset_index()
    .rename(columns={"away_team": "Team", "Away_Win": "Wins", "Away_Loss": "Losses", "Tie": "Ties"})
)

season_records_reg = (
    pd.concat([home_rec, away_rec])
    .groupby(["season", "Team"])[["Wins", "Losses", "Ties"]]
    .sum()
    .reset_index()
)
total_games = season_records_reg["Wins"] + season_records_reg["Losses"] + season_records_reg["Ties"]
season_records_reg["Win_Pct"] = (
    (season_records_reg["Wins"] + 0.5 * season_records_reg["Ties"]) / total_games
).round(3)

# --- combined team + player stats ---
master_stats = player_stats[player_stats["position"].isin(["QB", "RB", "WR", "TE", "FB"])]

combined_data = pd.merge(
    season_records_reg, master_stats, how="left",
    left_on=["season", "Team"], right_on=["season", "recent_team"],
)

drop_cols = [
    "recent_team", "player_id", "headshot_url", "season_type",
    "sacks_suffered", "sack_yards_lost", "sack_fumbles", "sack_fumbles_lost",
    "passing_air_yards", "passing_yards_after_catch", "passing_first_downs",
    "passing_cpoe", "passing_2pt_conversions", "pacr",
    "rushing_first_downs", "rushing_2pt_conversions",
    "receiving_first_downs", "receiving_2pt_conversions", "racr", "air_yards_share",
]
combined_data.drop(columns=[c for c in drop_cols if c in combined_data.columns], inplace=True)
combined_data.drop(
    columns=[
        c for c in combined_data.columns
        if c.startswith(("def_", "punt_", "fg_", "kickoff_", "pat_", "gwfg_", "fantasy_", "fumble_"))
    ],
    inplace=True,
)

combined_data.to_csv("Data/reg_combined_team_player_stats.csv", index=False)

# --- team season points -> Base_Team_Strength (Pythagorean win expectation) ---
home_stats = (
    schedules_reg.groupby(["season", "home_team"])[["home_score", "away_score"]]
    .sum()
    .reset_index()
    .rename(columns={"home_team": "team", "home_score": "PF", "away_score": "PA"})
)
away_stats = (
    schedules_reg.groupby(["season", "away_team"])[["away_score", "home_score"]]
    .sum()
    .reset_index()
    .rename(columns={"away_team": "team", "away_score": "PF", "home_score": "PA"})
)
team_season_points = (
    pd.concat([home_stats, away_stats])
    .groupby(["season", "team"])[["PF", "PA"]]
    .sum()
    .reset_index()
)
exponent = 2.37
team_season_points["Base_Team_Strength"] = (
    team_season_points["PF"] ** exponent
) / (team_season_points["PF"] ** exponent + team_season_points["PA"] ** exponent)
team_season_points.rename(columns={"team": "Team"}, inplace=True)

team_season_points.to_csv("Data/team_season_points.csv", index=False)

print(f"reg_combined_team_player_stats.csv: {len(combined_data)} rows")
print(f"team_season_points.csv: {len(team_season_points)} rows")
