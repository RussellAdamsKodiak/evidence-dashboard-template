# Elasticsearch Fetch Script

Queries a date-histogram aggregation from Elasticsearch and writes
`report/sources/elasticsearch/events_by_day.parquet` for Evidence to read.

## Setup

```bash
cd fetch/elasticsearch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your cluster URL and API key
```

## Running

```bash
# From fetch/elasticsearch/ with venv active:
python fetch.py              # last 30 days (cached same-day)
python fetch.py --days 90    # last 90 days
python fetch.py --force      # bypass same-day cache

# Then rebuild the Evidence sources:
cd ../../report && npm run sources
```

## Customising the query

The fetch script aggregates by `@timestamp` (day) and `log.level` by default.
Override via `.env` (see `.env.example`) or edit `fetch.py` directly:

- `ES_INDEX` — which index pattern to query
- `ES_TIMESTAMP_FIELD` — the date field to bucket on
- `ES_LEVEL_FIELD` — the breakdown field (any keyword field works)

To change the aggregation entirely, edit `build_query()` in `fetch.py` and
update the corresponding SQL in `report/sources/elasticsearch/events_by_day.sql`
and the dashboard page at `report/pages/elasticsearch/index.md`.

## Getting an API key

In Kibana → Stack Management → API keys → Create API key.
Assign the minimum privileges needed for your index (e.g. `read` on the index pattern).
