"""PostgreSQL-backed Retail Analytics API with Redis caching."""

import os
from datetime import datetime
from typing import Any

import psycopg2
import redis
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(
    title="Retail Analytics API",
    version="1.0.0",
)

API_KEY = os.getenv("API_KEY", "local-demo-key")

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "retail"),
    "user": os.getenv("POSTGRES_USER", "retail"),
    "password": os.getenv("POSTGRES_PASSWORD", "retail_local_only"),
}

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)


def auth(x_api_key: str | None):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="invalid API key",
        )


def get_db_connection():
    return psycopg2.connect(**POSTGRES_CONFIG)


def get_redis_client():
    return redis.from_url(REDIS_URL)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sales")
def sales(
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    s.store_id,
                    SUM(f.revenue) AS revenue,
                    SUM(f.profit) AS profit
                FROM fact_sales f
                JOIN dim_store s
                    ON s.store_key = f.store_key
                GROUP BY s.store_id
                ORDER BY s.store_id
                """
            )

            rows = cursor.fetchall()

        return [
            {
                "store_id": row[0],
                "revenue": float(row[1]),
                "profit": float(row[2]),
            }
            for row in rows
        ]

    finally:
        connection.close()


@app.get("/sales/{store_id}")
def store_sales(
    store_id: int,
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)

    cache_key = f"retail:sales:store:{store_id}"
    redis_client = get_redis_client()

    cached = redis_client.get(cache_key)

    if cached:
        return {
            "source": "redis_cache",
            "data": __import__("json").loads(cached),
        }

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    s.store_id,
                    SUM(f.revenue) AS revenue,
                    SUM(f.profit) AS profit
                FROM fact_sales f
                JOIN dim_store s
                    ON s.store_key = f.store_key
                WHERE s.store_id = %s
                GROUP BY s.store_id
                """,
                (store_id,),
            )

            row = cursor.fetchone()

        if row is None:
            data = []
        else:
            data = [
                {
                    "store_id": row[0],
                    "revenue": float(row[1]),
                    "profit": float(row[2]),
                }
            ]

        redis_client.setex(
            cache_key,
            300,
            __import__("json").dumps(data),
        )

        return {
            "source": "postgresql",
            "data": data,
        }

    finally:
        connection.close()


@app.get("/inventory")
def inventory(
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)

    # Inventory is currently available in the source files,
    # but there is no inventory fact table in the warehouse DDL yet.
    return {
        "status": "not_implemented",
        "message": "Inventory warehouse table is not implemented yet.",
    }


@app.get("/pipeline/status")
def pipeline_status(
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)

    gold_file = os.path.join(
        "data",
        "lake",
        "gold",
        "fact_sales.json",
    )

    return {
        "status": "completed"
        if os.path.exists(gold_file)
        else "not_run",
        "checked_at": datetime.now().isoformat(),
    }


@app.get("/data-quality")
def data_quality(
    x_api_key: str | None = Header(default=None),
):
    auth(x_api_key)

    return {
        "status": "available",
        "message": "Run the data-quality pipeline to generate the latest report.",
    }