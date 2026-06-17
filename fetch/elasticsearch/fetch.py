#!/usr/bin/env python3
"""
Fetch event counts from Elasticsearch and write parquet for Evidence.

Outputs (in report/sources/elasticsearch/):
  events_by_severity.parquet  — date, severity, count
  events_by_truck.parquet     — date, truck_name, count

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
    import requests as http
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

# ---------------------------------------------------------------------------
# Config — edit or override via .env
# ---------------------------------------------------------------------------
ES_URL           = os.environ["ES_URL"]
ES_API_KEY       = os.getenv("ES_API_KEY")
ES_USERNAME      = os.getenv("ES_USERNAME")
ES_PASSWORD      = os.getenv("ES_PASSWORD")
INDEX            = os.getenv("ES_INDEX", "logs-*")
TIMESTAMP_FIELD  = os.getenv("ES_TIMESTAMP_FIELD", "@timestamp")
SEVERITY_FIELD   = os.getenv("ES_SEVERITY_FIELD", "severity")   # or "log.level"
ENTITY_FIELD     = os.getenv("ES_TRUCK_FIELD", "truck_name")     # any grouping keyword
TOP_N            = int(os.getenv("ES_TOP_N", "15"))
REQUEST_TIMEOUT  = int(os.getenv("ES_TIMEOUT_S", "120"))

OUT_DIR = Path(__file__).parent.parent.parent / "report" / "sources" / "elasticsearch"
# ---------------------------------------------------------------------------


def auth_header():
    if ES_API_KEY:
        return {"Authorization": f"ApiKey {ES_API_KEY}"}
    return {}


def auth_tuple():
    if ES_USERNAME and ES_PASSWORD:
        return (ES_USERNAME, ES_PASSWORD)
    return None


def build_query(days: int) -> dict:
    since = (date.today() - timedelta(days=days)).isoformat()
    return {
        "size": 0,
        "query": {"range": {TIMESTAMP_FIELD: {"gte": since}}},
        "aggs": {
            "by_day": {
                "date_histogram": {
                    "field": TIMESTAMP_FIELD,
                    "calendar_interval": "day",
                    "format": "yyyy-MM-dd",
                },
                "aggs": {
                    "by_severity": {
                        "terms": {"field": SEVERITY_FIELD, "size": 20, "missing": "UNKNOWN"}
                    },
                    "by_entity": {
                        "terms": {"field": ENTITY_FIELD, "size": TOP_N, "missing": "unknown"}
                    },
                },
            }
        },
    }


def fetch(days: int):
    url = f"{ES_URL.rstrip('/')}/{INDEX}/_search"
    resp = http.post(
        url,
        auth=auth_tuple(),
        headers={**auth_header(), "Content-Type": "application/json"},
        json=build_query(days),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    severity_rows, entity_rows = [], []
    for day_bucket in data["aggregations"]["by_day"]["buckets"]:
        day = day_bucket["key_as_string"]
        for b in day_bucket["by_severity"]["buckets"]:
            severity_rows.append({"date": day, "severity": b["key"], "count": b["doc_count"]})
        for b in day_bucket["by_entity"]["buckets"]:
            entity_rows.append({"date": day, "truck_name": b["key"], "count": b["doc_count"]})

    df_sev = pd.DataFrame(severity_rows, columns=["date", "severity", "count"])
    df_sev["date"] = pd.to_datetime(df_sev["date"]).dt.date

    df_entity = pd.DataFrame(entity_rows, columns=["date", "truck_name", "count"])
    df_entity["date"] = pd.to_datetime(df_entity["date"]).dt.date

    return df_sev, df_entity


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--force", action="store_true", help="skip same-day cache")
    args = parser.parse_args()

    sev_file = OUT_DIR / "events_by_severity.parquet"
    if not args.force and sev_file.exists():
        mtime = date.fromtimestamp(sev_file.stat().st_mtime)
        if mtime == date.today():
            print(f"Cache hit (written today). Use --force to refresh.")
            return

    print(f"Fetching last {args.days} days from {ES_URL} index={INDEX} ...")
    df_sev, df_entity = fetch(args.days)
    print(f"  {len(df_sev)} severity rows, {len(df_entity)} entity rows")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df_sev.to_parquet(sev_file, index=False)
    df_entity.to_parquet(OUT_DIR / "events_by_truck.parquet", index=False)
    print(f"  Wrote {OUT_DIR}/")


if __name__ == "__main__":
    main()
