# Evidence Dashboard Template

A ready-to-fork [Evidence.dev](https://evidence.dev) dashboard that deploys to GitHub Pages.

**Fork this repo → push to `main` → dashboard is live.** No servers, no credentials required for the sample data.

## What's included

| | |
|---|---|
| **Sample dashboard** | Works immediately — CSV data, no setup needed |
| **Elasticsearch fetch** | Python script → parquet → Evidence chart |
| **GitHub Pages CI/CD** | Pushes to `main` auto-deploy via GitHub Actions |
| **Claude context** | `CLAUDE.md` explains the project to Claude Code so you can build with AI |

## Quick start

```bash
# 1. Fork or clone
git clone https://github.com/<your-org>/evidence-dashboard-template
cd evidence-dashboard-template/report

# 2. Install and run
npm install
npm run sources
npm run dev        # http://localhost:3000
```

## Enable GitHub Pages

1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**
3. Push to `main` — the workflow deploys automatically

## Add Elasticsearch data

```bash
cd fetch/elasticsearch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # fill in ES_URL and ES_API_KEY
python fetch.py
cd ../../report && npm run sources && npm run dev
```

See `fetch/elasticsearch/README.md` for full details.

## Project structure

```
report/           Evidence.dev project (pages + sources)
fetch/            Data fetch scripts (one per source)
  elasticsearch/  Elasticsearch → parquet
.github/          GitHub Actions deploy workflow
CLAUDE.md         AI assistant context for building the dashboard
```

## Developing with Claude

Open this repo in [Claude Code](https://claude.ai/code). The `CLAUDE.md`
gives Claude full context on how Evidence works so it can write queries,
add charts, wire up new data sources, and extend the fetch scripts.

Example prompts to get started:
- "Add a page showing the top 10 services by error rate"
- "Add a date range filter to the main dashboard"
- "Write a fetch script for our Postgres metrics table and add a chart"
- "Change the Elasticsearch aggregation to break down by `service.name` instead of log level"

## Tech stack

- [Evidence.dev](https://evidence.dev) v40 — SQL + markdown → static dashboards
- [DuckDB](https://duckdb.org) — in-process SQL over parquet files
- GitHub Actions + GitHub Pages — zero-infrastructure deploy
- Python + `elasticsearch` client — Elasticsearch data fetching
