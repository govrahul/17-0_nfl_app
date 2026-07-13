from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import game

app = FastAPI(title="17-0")

PLAYERS_BY_ID = {p["id"]: p for p in game.PLAYERS}
TEAMS_BY_ID = {t["id"]: t for t in game.TEAMS}

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/api/roll")
def roll(exclude: str = "", team: str | None = None, season: int | None = None):
    exclude_ids = set(filter(None, exclude.split(",")))
    try:
        return game.roll_team(exclude_ids, pin_team=team, pin_season=season)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class DraftPicks(BaseModel):
    base_team_id: str
    qb_id: str
    rb_id: str
    wr1_id: str
    wr2_id: str
    flex_id: str


@app.post("/api/predict")
def predict(picks: DraftPicks):
    base_team = TEAMS_BY_ID.get(picks.base_team_id)
    if base_team is None:
        raise HTTPException(status_code=400, detail=f"Unknown base team: {picks.base_team_id}")

    try:
        qb = PLAYERS_BY_ID[picks.qb_id]
        rb = PLAYERS_BY_ID[picks.rb_id]
        wr1 = PLAYERS_BY_ID[picks.wr1_id]
        wr2 = PLAYERS_BY_ID[picks.wr2_id]
        flex = PLAYERS_BY_ID[picks.flex_id]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown player id: {e.args[0]}")

    return game.predict_record(base_team["base_team_strength"], qb, rb, wr1, wr2, flex)


# Serve the built React app (production build produced in the Docker image)
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
