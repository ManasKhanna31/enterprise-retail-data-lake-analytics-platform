"""Transactional PostgreSQL extraction adapter; watermarking is caller-owned."""
from sqlalchemy import create_engine, text
def extract_table(database_url: str, table: str, watermark_column: str | None = None, watermark_value=None):
    engine = create_engine(database_url, pool_pre_ping=True)
    query = text(f"SELECT * FROM {table}" + (f" WHERE {watermark_column} > :watermark" if watermark_column else ""))
    with engine.connect() as connection:
        result = connection.execute(query, {"watermark": watermark_value} if watermark_column else {})
        return [dict(row._mapping) for row in result]
