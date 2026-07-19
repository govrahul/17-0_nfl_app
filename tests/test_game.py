import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Server import game


def test_roll_team_excludes_teams_without_players(monkeypatch):
    team_with_players = {"id": "team-1", "season": 2020, "team": "A"}
    team_without_players = {"id": "team-2", "season": 2020, "team": "B"}

    monkeypatch.setattr(game, "TEAMS", [team_with_players, team_without_players])
    monkeypatch.setattr(
        game,
        "_players_by_team_season",
        {(2020, "A"): [{"id": "player-1"}]},
    )
    monkeypatch.setattr(game.random, "choice", lambda seq: seq[-1])

    result = game.roll_team(set())

    assert result["team"]["id"] == "team-1"
    assert result["players"] == [{"id": "player-1"}]
