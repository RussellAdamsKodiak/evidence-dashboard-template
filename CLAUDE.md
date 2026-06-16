# Evidence Dashboard — Claude Context

This repo is an [Evidence.dev](https://evidence.dev) dashboard deployed to GitHub Pages.
Claude (this file's reader) is here to help you build and extend it.

## Project layout

```
report/                       Evidence.dev project
  evidence.config.yaml        Theme, appearance, plugins
  package.json
  pages/
    index.md                  Main dashboard (edit this first)
    elasticsearch/index.md    Elasticsearch data dashboard
  sources/
    sample/
      connection.yaml         CSV source type
      metrics.csv             Replace with your own CSV data
    elasticsearch/
      connection.yaml         DuckDB source (reads parquet files)
      events_by_day.sql       SQL query over the parquet
fetch/
  elasticsearch/
    fetch.py                  Pulls from ES → writes parquet
    .env.example              Copy to .env and fill in credentials
.github/workflows/deploy.yml  GitHub Pages CI/CD
```

## Local dev workflow

```bash
cd report
npm install

# CSV source works out of the box
npm run sources    # process sources
npm run dev        # http://localhost:3000

# After running the ES fetch script:
cd ../fetch/elasticsearch
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ES_URL and ES_API_KEY
python fetch.py
cd ../../report && npm run sources && npm run dev
```

## How Evidence pages work

Each `.md` file in `pages/` is a dashboard page. SQL queries go in fenced
code blocks tagged with a variable name — Evidence runs them at build time:

````md
```sql my_query
SELECT date, service, SUM(requests) AS requests
FROM metrics
GROUP BY date, service
```

<LineChart data={my_query} x=date y=requests series=service />
````

The query name (`my_query`) becomes the variable you pass to components.
Sources are referenced by their directory name — `metrics` above comes from
`sources/sample/metrics.csv`.

## Common Evidence components

```md
<BigValue data={q} value=col title="My Metric" fmt=num0 />
<LineChart data={q} x=date y=value series=category title="Trend" />
<BarChart data={q} x=date y=value series=category type=stacked />
<DataTable data={q} />
<Dropdown name=env data={q} value=environment defaultValue="prod" />
```

Filter with a Dropdown:
```sql filtered
SELECT * FROM metrics WHERE environment = '${inputs.env}'
```

Full component reference: https://docs.evidence.dev/components/all-components/

## Connecting a new data source

**CSV**: drop a `.csv` into `sources/<name>/` and add `connection.yaml`:
```yaml
name: my_source
type: csv
```

**DuckDB / parquet**: write parquet files from a fetch script, then:
```yaml
name: my_source
type: duckdb
options:
  filename: ":memory:"
```
Add `.sql` files next to the parquet that use `read_parquet('sources/my_source/file.parquet')`.

**Postgres / other DB**: add the package to `package.json` and configure
`connection.yaml` — see Evidence docs for the connection schema.

## Extending the Elasticsearch fetch

`fetch/elasticsearch/fetch.py` runs a date-histogram aggregation bucketed
by `log.level`. To change what it fetches:

1. Edit `build_query()` in `fetch.py` to adjust the aggregation or add fields
2. Update `sources/elasticsearch/events_by_day.sql` to match the new schema
3. Update `pages/elasticsearch/index.md` with new chart components
4. Re-run `python fetch.py --force` then `npm run sources`

Use `.env` to override `ES_INDEX`, `ES_TIMESTAMP_FIELD`, and `ES_LEVEL_FIELD`
without touching the script.

## Deploying

Push to `main` — GitHub Actions builds Evidence and deploys to GitHub Pages.
Enable GitHub Pages in repo Settings → Pages → Source: GitHub Actions.

The sample dashboard (CSV data) works without running any fetch scripts,
so the first deploy is functional immediately after forking.
