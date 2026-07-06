# arketingm Geopolitical Globe

3D interactive globe with live stock prices, geopolitical risk pins, and macro event markers.

## Setup

1. Copy `.env.example` to `.env` and add your Alpha Vantage API key
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python app.py`

## Deploy to Railway

1. Push to GitHub
2. New Project → Deploy from GitHub repo
3. Set environment variable: `ALPHA_VANTAGE_KEY=your_key`
4. Railway auto-detects Procfile and deploys

## Environment Variables

| Variable | Description |
|---|---|
| `ALPHA_VANTAGE_KEY` | Alpha Vantage API key (free at alphavantage.co) |
| `PORT` | Auto-set by Railway |

## API Endpoints

- `GET /` — Globe app
- `GET /api/prices` — All ticker prices (15min cache)
- `GET /api/price/:ticker` — Single ticker
- `GET /api/health` — Health check
