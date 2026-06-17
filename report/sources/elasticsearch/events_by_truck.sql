SELECT *
FROM read_parquet('sources/elasticsearch/events_by_truck.parquet')
ORDER BY date
