---
title: Vehicle Debug Logs
---

# Vehicle Debug Logs

Aggregated from `debug_log_index-*` — 30-day rolling window, bucketed by day.
Data fetched by `fetch/elasticsearch/fetch.py`.

```sql totals
SELECT
  severity,
  SUM(count) AS total_events
FROM events_by_severity
GROUP BY severity
ORDER BY total_events DESC
```

<BigValue data={totals.filter(d => d.severity === 'WARNING')} value=total_events title="Warnings (30d)" fmt=num0 />
<BigValue data={totals.filter(d => d.severity === 'ERROR')} value=total_events title="Errors (30d)" fmt=num0 />
<BigValue data={totals.filter(d => d.severity === 'INFO')} value=total_events title="Info (30d)" fmt=num0 />

---

```sql severity_trend
SELECT date, severity, count
FROM events_by_severity
ORDER BY date
```

<LineChart
  data={severity_trend}
  x=date
  y=count
  series=severity
  title="Events per Day by Severity"
/>

---

```sql error_rate
SELECT
  date,
  SUM(CASE WHEN severity = 'ERROR' THEN count ELSE 0 END) AS errors,
  SUM(count) AS total,
  ROUND(SUM(CASE WHEN severity = 'ERROR' THEN count ELSE 0 END)::FLOAT / SUM(count) * 100, 4) AS error_pct
FROM events_by_severity
GROUP BY date
ORDER BY date
```

<AreaChart
  data={error_rate}
  x=date
  y=error_pct
  title="Daily Error Rate (%)"
/>

---

```sql top_trucks
SELECT
  truck_name,
  SUM(count) AS total_events
FROM events_by_truck
GROUP BY truck_name
ORDER BY total_events DESC
LIMIT 15
```

<BarChart
  data={top_trucks}
  x=truck_name
  y=total_events
  title="Total Events by Truck (30d)"
  swapXY=true
/>

---

```sql truck_trend
SELECT date, truck_name, count
FROM events_by_truck
ORDER BY date
```

<LineChart
  data={truck_trend}
  x=date
  y=count
  series=truck_name
  title="Events per Day by Truck"
/>
