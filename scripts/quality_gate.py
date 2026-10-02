"""Run data quality checks as a pipeline gate."""

from ingestion.files.reader import ingest_files
from quality.checks import quality_report


def main():
    records = ingest_files("data/sample_clean", "data/lake")
    report = quality_report(records)

    print(report)

    if not report["overall"]:
        raise RuntimeError("Data quality checks failed. Pipeline stopped.")

    print("Data quality checks passed.")


if __name__ == "__main__":
    main()