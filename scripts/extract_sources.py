"""Extract source files into the Bronze layer."""

from ingestion.files.reader import ingest_files


def main():
    result = ingest_files("data/sample_clean", "data/lake")

    for dataset, rows in result.items():
        print(f"{dataset}: {len(rows)} records ingested")

    print("Source extraction completed successfully.")


if __name__ == "__main__":
    main()