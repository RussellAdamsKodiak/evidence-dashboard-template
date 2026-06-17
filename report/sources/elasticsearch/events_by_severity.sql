SELECT *
FROM read_parquet('sources/elasticsearch/events_by_severity.parquet')
ORDER BY date
