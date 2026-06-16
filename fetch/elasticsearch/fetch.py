#!/usr/bin/env python3
"""
Fetch event counts from Elasticsearch and write parquet for Evidence.

Output: ../../report/sources/elasticsearch/events_by_day.parquet
Schema: date (date), log_level (str), count (int)

Usage:
    python fetch.py              # last 30 days
    python fetch.py --days 90    # last 90 days
    python fetch.py --force      # skip same-day cache check
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    import pandas as pd
    from dotenv import load_dotenv
    from elasticsearch import Elasticsearch
except ImportError:
    print("Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

# ---------------------------------------------------------------------------
# Config — edit these for your index and field names
# ---------------------------------------------------------------------------
ES_URL       = os.environ["ES_URL"]          # https://your-cluster.es.io:9200
ES_API_KEY   = os.environ["ES_API_KEY"]      # base64 API key from Kibana
INDEX        = os.getenv("ES_INDEX", "logs-*")
TIMESTAMP_FIELD = os.getenv("ES_TIMESTAMP_FIELD", "@timestamp")
LEVEL_FIELD     = os.getenv("ES_LEVEL_FIELD", "log.level")

OUT_DIR = Path(__file__).parent.parent.parent / "report" / "sources" / "elasticsearch"
OUT_FILE = OUT_DIR / "events_by_day.parquet"
# ---------------------------------------------------------------------------


def build_query(days: int) -> dict:
    since = (date.today() - timedelta(days=days)).isoformat()
    return {
        "size": 0,
        "query": {
            "range": {TIMESTAMP_FIELD: {"gte": since}}
        },
        "aggs": {
            "by_day": {
                "date_histogram": {
                    "field": TIMESTAMP_FIELD,
                    "calendar_interval": "day",
                    "format": "yyyy-MM-dd",
                },
                "aggs": {
                    "by_level": {
                        "terms": {
                            "field": LEVEL_FIELD,
                            "size": 20,
                            "missing": "unknown",
                        }
                    }
                },
            }
        },
    }


def fetch(days: int) -> pd.DataFrame:
    es = Elasticsearch(ES_URL, api_key=ES_API_KEY)
    resp = es.search(index=INDEX, body=build_query(days))

    rows = []
    for day_bucket in resp["aggregations"]["by_day"]["buckets"]:
        day = day_bucket["key_as_string"]
        for level_bucket in day_bucket["by_level"]["buckets"]:
            rows.append({
                "date": day,
                "log_level": level_bucket["key"],
                "count": level_bucket["doc_count"],
            })

    df = pd.DataFrame(rows, columns=["date", "log_level", "count"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--force", action="store_true", help="skip same-day cache")
    args = parser.parse_args()

    if not args.force and OUT_FILE.exists():
        mtime = date.fromtimestamp(OUT_FILE.stat().st_mtime)
        if mtime == date.today():
            print(f"Cache hit ({OUT_FILE.name} written today). Use --force to refresh.")
            return

    print(f"Fetching last {args.days} days from {ES_URL} index={INDEX} ...")
    df = fetch(args.days)
    print(f"  {len(df)} rows")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_FILE, index=False)
    print(f"  Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
