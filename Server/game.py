"""Draft-pool rolling and win/loss prediction, backed by Data/game_pool.json
and Modeling/random_forest_model.pkl. This module is the only place the
model runs.
"""
import json
import pickle
import random
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "Data"
MODEL_PATH = Path(__file__).resolve().parent.parent / "Modeling"

SLOT_ELIGIBILITY = {
    "QB": {"QB"},
    "RB": {"RB"},
    "WR1": {"WR"},
    "WR2": {"WR"},
    "FLEX": {"RB", "WR", "TE"},
}

with open(DATA_DIR / "game_pool.json") as f:
    _pool = json.load(f)

PLAYERS = _pool["players"]
TEAMS = _pool["teams"]

_players_by_team_season = {}
for p in PLAYERS:
    _players_by_team_season.setdefault((p["season"], p["team"]), []).append(p)

with open(MODEL_PATH / "random_forest_model.pkl", "rb") as f:
    RF_MODEL = pickle.load(f)

with open(MODEL_PATH / "linear_model.pkl", "rb") as f:
    LINEAR_MODEL = pickle.load(f)

def eligible_slots(position: str) -> list[str]:
    return [slot for slot, allowed in SLOT_ELIGIBILITY.items() if position in allowed]


def roll_team(exclude_ids: set[str], pin_team: str | None = None, pin_season: int | None = None) -> dict:
    """Pick a random team-season not already drafted, with its full skill-position roster.

    pin_team: keep the franchise fixed, reroll only the season ("Reroll Decade").
    pin_season: keep the season fixed, reroll only the franchise ("Reroll Team").
    """
    candidates = [
        t
        for t in TEAMS
        if t["id"] not in exclude_ids and _players_by_team_season.get((t["season"], t["team"]), [])
    ]
    if pin_team is not None:
        candidates = [t for t in candidates if t["team"] == pin_team]
    if pin_season is not None:
        candidates = [t for t in candidates if t["season"] == pin_season]
    if not candidates:
        raise ValueError("No more team-seasons available")
    team = random.choice(candidates)
    roster = _players_by_team_season.get((team["season"], team["team"]), [])
    return {"team": team, "players": roster}


def _flex_volume(player: dict) -> float:
    return player["carries"] if player["position"] == "RB" else player["target_share"]


def predict_record(base_team_strength: float, qb: dict, rb: dict, wr_a: dict, wr_b: dict, flex: dict) -> dict:
    """Builds the 17-feature vector in the exact column order the RF model
    was trained on (see Modeling/tree_model.py) and predicts Win_Pct.
    """
    wr1, wr2 = sorted([wr_a, wr_b], key=lambda p: p["total_yards"], reverse=True)

    features = np.array([[
        base_team_strength,
        qb["total_yards"], qb["total_tds"], qb["td_int"],
        rb["total_yards"], rb["total_tds"], rb["carries"],
        wr1["total_yards"], wr1["total_tds"], wr1["target_share"],
        wr2["total_yards"], wr2["total_tds"], wr2["target_share"],
        flex["total_yards"], flex["total_tds"], _flex_volume(flex),
        1.0 if flex["position"] == "RB" else 0.0,
    ]])

    win_pct = float(RF_MODEL.predict(features)[0])
    win_pct = np.clip(win_pct, 0.0, 1.0)

    linear_win_pct = float(LINEAR_MODEL.predict(features[:, :-1])[0])
    linear_win_pct = np.clip(linear_win_pct, 0.0, 1.0)

    # blended average with more extreme linear model and more conservative tree model
    #final_win_pct = (0.6 * win_pct) + (0.4 * linear_win_pct)
    #final_win_pct = np.clip(final_win_pct, 0.0, 1.0)

    # pick more extreme prediction
    if abs(win_pct - 0.5) > abs(linear_win_pct - 0.5):
        final_win_pct = win_pct
    else:
        final_win_pct = linear_win_pct

    games = 17
    wins = round(final_win_pct * games)
    losses = games - wins
    return {"win_pct": round(final_win_pct, 4), "wins": wins, "losses": losses, "record": f"{wins}-{losses}"}
