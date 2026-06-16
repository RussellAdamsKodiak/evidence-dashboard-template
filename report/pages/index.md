---
title: Dashboard
---

# Dashboard

This is the sample dashboard built from `sources/sample/metrics.csv`.
Replace the CSV data (or wire up the Elasticsearch source) and reshape
these charts to match your use case.

```sql total_requests
SELECT
  SUM(requests) AS total_requests,
  SUM(errors)   AS total_errors,
  ROUND(SUM(errors)::FLOAT / SUM(requests) * 100, 2) AS error_rate_pct
FROM metrics
WHERE environment = 'prod'
```

<BigValue
  data={total_requests}
  value=total_requests
  title="Total Requests (prod)"
  fmt=num0
/>

<BigValue
  data={total_requests}
  value=total_errors
  title="Total Errors (prod)"
  fmt=num0
/>

<BigValue
  data={total_requests}
  value=error_rate_pct
  title="Error Rate"
  fmt=pct2
/>

---

```sql requests_over_time
SELECT
  date,
  service,
  SUM(requests) AS requests
FROM metrics
WHERE environment = 'prod'
GROUP BY date, service
ORDER BY date
```

<LineChart
  data={requests_over_time}
  x=date
  y=requests
  series=service
  title="Requests Over Time (prod)"
/>

---

```sql error_rate_by_service
SELECT
  service,
  SUM(requests) AS requests,
  SUM(errors)   AS errors,
  ROUND(SUM(errors)::FLOAT / SUM(requests) * 100, 2) AS error_rate_pct
FROM metrics
WHERE environment = 'prod'
GROUP BY service
ORDER BY error_rate_pct DESC
```

<DataTable data={error_rate_by_service} />

---

```sql p99_trend
SELECT
  date,
  service,
  AVG(p99_ms) AS p99_ms
FROM metrics
WHERE environment = 'prod'
GROUP BY date, service
ORDER BY date
```

<BarChart
  data={p99_trend}
  x=date
  y=p99_ms
  series=service
  title="p99 Latency (ms)"
  type=grouped
/>
