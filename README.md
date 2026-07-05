# 17-0_nfl_app

NFL data scraper for a football version of [82-0](https://www.82-0.com/). Pulls team season/passing/rushing-receiving stats from [pro-football-reference.com](https://www.pro-football-reference.com/).

## Why FlareSolverr

pro-football-reference.com sits behind Cloudflare's bot-check challenge ("Just a moment..."), which blocks plain `requests` calls and even headless Playwright/Chromium (Cloudflare detects headless automation directly). [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) runs a real, challenge-solving browser session behind a small HTTP API, so the scraper just POSTs the target URL to it and gets back solved HTML.

## Running it

Everything is one command from the project root:

```
docker compose up --build
```

This starts FlareSolverr, waits for it to report healthy, then runs the scraper against it. Output CSVs land in `Scrapers/Data/` on the host (mounted from the container).

To run it in the background:

```
docker compose up -d --build
```

## Configuration

- `FLARESOLVERR_URL` — where the scraper looks for FlareSolverr's `/v1` endpoint. Defaults to `http://localhost:8191/v1` for local (non-Docker) runs; the compose file overrides this to `http://flaresolverr:8191/v1` for container-to-container networking.

## Local (non-Docker) dev

```
python -m venv .venv
.venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
docker run -d --name=flaresolverr -p 8191:8191 --restart unless-stopped ghcr.io/flaresolverr/flaresolverr:latest
python Scrapers/team_scraper.py
```
