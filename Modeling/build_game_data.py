"""Builds the compact, self-contained game data artifact the web app serves from.

Reads:  Data/reg_combined_team_player_stats.csv, Data/team_season_points.csv
        (both produced by Modeling/build_dataset.py)
Writes: Data/game_pool.json

This is the only place nflreadpy/pandas touch the game -- the FastAPI app
just loads the resulting JSON at startup, so container startup is instant
and offline.
"""
import json
import pandas as pd
import nflreadpy as nfl

combined = pd.read_csv("Data/reg_combined_team_player_stats.csv")
team_strength = pd.read_csv("Data/team_season_points.csv")
teams_meta = nfl.load_teams().to_pandas().set_index("team_abbr")

MIN_GAMES = 4  # drop tiny injury-shortened/backup samples from the draftable pool

combined["Total_Yards"] = (
    combined["passing_yards"].fillna(0)
    + combined["rushing_yards"].fillna(0)
    + combined["receiving_yards"].fillna(0)
)
combined["Total_TDs"] = (
    combined["passing_tds"].fillna(0)
    + combined["rushing_tds"].fillna(0)
    + combined["receiving_tds"].fillna(0)
)
combined["TD_INT"] = combined["passing_tds"] / combined["passing_interceptions"].replace(0, pd.NA)

players = combined[
    combined["position_group"].isin(["QB", "RB", "WR", "TE"])
    & combined["player_name"].notna()
    & (combined["games"] >= MIN_GAMES)
    & (combined["Total_Yards"] > 0)
].copy()

player_records = []
for row in players.itertuples():
    meta = teams_meta.loc[row.Team] if row.Team in teams_meta.index else None
    player_records.append({
        # position included because abbreviated player_name isn't always unique
        # within a team-season (e.g. 2000 BAL: "J.Lewis" is both Jermaine Lewis,
        # WR, and Jamal Lewis, RB)
        "id": f"{row.season}_{row.Team}_{row.player_name}_{row.position_group}",
        "name": row.player_display_name,
        "season": int(row.season),
        "team": row.Team,
        "position": row.position_group,  # QB / RB / WR / TE -- used for slot eligibility
        "games": int(row.games),
        "total_yards": round(float(row.Total_Yards), 1),
        "total_tds": round(float(row.Total_TDs), 1),
        "td_int": round(float(row.TD_INT), 2) if pd.notna(row.TD_INT) else 0.0,
        "carries": round(float(row.carries), 1) if pd.notna(row.carries) else 0.0,
        "target_share": round(float(row.target_share), 4) if pd.notna(row.target_share) else 0.0,
        # raw counts needed for the position-specific list-row stat columns
        # (CMP/INT for QB, REC for WR/TE) -- separate from the TD/INT ratio used by the model
        "completions": int(row.completions) if pd.notna(row.completions) else 0,
        "interceptions": int(row.passing_interceptions) if pd.notna(row.passing_interceptions) else 0,
        "receptions": int(row.receptions) if pd.notna(row.receptions) else 0,
        # carried on the player (not just the team record) so a drafted
        # player's card still has its team color after the round's pool is gone
        "color": meta["team_color"] if meta is not None else "#445269",
    })

actual_win_pct = combined[["season", "Team", "Win_Pct"]].drop_duplicates(["season", "Team"]).set_index(["season", "Team"])["Win_Pct"]

team_records = []
for row in team_strength.itertuples():
    meta = teams_meta.loc[row.Team] if row.Team in teams_meta.index else None
    win_pct = actual_win_pct.get((row.season, row.Team))
    team_records.append({
        "id": f"{row.season}_{row.Team}",
        "season": int(row.season),
        "team": row.Team,
        "team_name": meta["team_name"] if meta is not None else row.Team,
        "base_team_strength": round(float(row.Base_Team_Strength), 6),
        # the model's actual input feature (Pythagorean win expectation) --
        # kept separate from actual_win_pct below, which is display-only
        "actual_win_pct": round(float(win_pct), 3) if pd.notna(win_pct) else None,
        "color": meta["team_color"] if meta is not None else "#445269",
        "color2": meta["team_color2"] if meta is not None else "#b4bdcc",
    })

game_pool = {"players": player_records, "teams": team_records}

with open("Data/game_pool.json", "w") as f:
    json.dump(game_pool, f)

print(f"players: {len(player_records)}")
print(f"team-seasons: {len(team_records)}")
