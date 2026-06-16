SELECT *
FROM read_parquet('sources/elasticsearch/events_by_day.parquet')
ORDER BY date
