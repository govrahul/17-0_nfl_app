# 17-0

A playable draft game: build a team from real historical NFL players and team-seasons, then get a projected record from a trained model. A football-themed take on [82-0](https://www.82-0.com/).

## Playing the game

Everything is one command from the project root:

```
docker compose up --build
```

Then open **http://localhost:8000**. Draft a base team plus QB / RB / WR / WR / FLEX across 6 rounds; once all 6 slots are filled you'll get a projected win-loss record.

The `game` service is fully self-contained — the player pool, team stats, and trained model are all baked into `Data/game_pool.json` and `Modeling/random_forest_model.pkl`, both committed to the repo, so there's no live scraping or network access needed to play.

## Refreshing the underlying data

The scraper/data-prep pipeline (FlareSolverr + `nflreadpy`) is only needed if you want to pull new seasons or recompute stats — it's gated behind a Compose profile so it doesn't run by default:

```
docker compose --profile scrape up scraper
```

A [Compose profile](https://docs.docker.com/compose/how-tos/profiles/) is a label on a service that keeps it from starting with a plain `docker compose up`. Services with no profile (like `game`) always start; services tagged with a profile (like `flaresolverr` and `scraper`, both tagged `scrape` here) only start if that profile is explicitly activated with `--profile <name>`. That's how playing the game never spins up the scraping stack, and vice versa.

pro-football-reference.com sits behind Cloudflare's bot-check challenge ("Just a moment..."), which blocks plain `requests` calls and even headless Playwright/Chromium. [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) runs a real, challenge-solving browser session behind a small HTTP API for that older scraper path; the current data pipeline instead uses `nflreadpy` (see `Scrapers/nfl_scraper.py`), which isn't blocked.

After refreshing, regenerate the game data and rebuild:

```
python Modeling/build_dataset.py
python Modeling/build_game_data.py
docker compose up --build game
```

## Local (non-Docker) dev

Backend:
```
python -m venv .venv
.venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
uvicorn Server.main:app --port 8000
```

Frontend (separate terminal, hot-reloading dev server on :5173, proxies `/api` to :8000):
```
cd frontend
npm install
npm run dev
```
