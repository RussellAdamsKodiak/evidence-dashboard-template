---
title: Elasticsearch Events
---

# Elasticsearch Events

This dashboard reads from `sources/elasticsearch/events_by_day.parquet`,
which is written by `fetch/elasticsearch/fetch.py`.

To populate it: set your credentials in `.env` (see `fetch/elasticsearch/.env.example`),
run the fetch script, then `npm run sources && npm run dev`.

```sql daily_events
SELECT *
FROM events_by_day
ORDER BY date
```

<LineChart
  data={daily_events}
  x=date
  y=count
  series=log_level
  title="Events per Day by Log Level"
/>

<DataTable data={daily_events} />
