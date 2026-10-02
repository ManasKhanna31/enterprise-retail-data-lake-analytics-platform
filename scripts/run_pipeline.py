"""Run the local-mode ingestion and curation pipeline."""
from ingestion.files.reader import ingest_files
from quality.checks import quality_report
from spark.transformations.local import build_gold

def main():
    records = ingest_files("data/sample", "data/lake")
    report = quality_report(records)
    build_gold(records, "data/lake/gold")
    print(report)

if __name__ == "__main__": main()
