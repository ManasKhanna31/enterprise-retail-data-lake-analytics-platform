"""CSV ingestion with Bronze snapshots."""
from pathlib import Path
import csv, json
from datetime import datetime, timezone

def ingest_files(source_dir: str, lake_dir: str) -> dict[str, list[dict]]:
    source, bronze, silver = Path(source_dir), Path(lake_dir) / "bronze", Path(lake_dir) / "silver"
    bronze.mkdir(parents=True, exist_ok=True); silver.mkdir(parents=True, exist_ok=True); result = {}
    for path in sorted(source.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as f: rows = list(csv.DictReader(f))
        enriched = [{**row, "_ingested_at": datetime.now(timezone.utc).isoformat(), "_source": path.name} for row in rows]
        result[path.stem] = enriched
        (bronze / f"{path.stem}.json").write_text(
    "\n".join(json.dumps(row) for row in enriched),
    encoding="utf-8",
)
        unique = list({tuple(sorted(row.items())): row for row in enriched}.values())
        (silver / f"{path.stem}.json").write_text(json.dumps(unique, indent=2), encoding="utf-8")
    return result
