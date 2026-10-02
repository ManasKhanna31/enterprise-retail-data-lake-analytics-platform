"""Load curated retail data into the PostgreSQL warehouse."""

from pathlib import Path
import csv
import os
from datetime import date

import psycopg2


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "sample"
DDL_FILE = BASE_DIR / "sql" / "ddl" / "warehouse.sql"


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "retail"),
        user=os.getenv("POSTGRES_USER", "retail"),
        password=os.getenv("POSTGRES_PASSWORD", "retail_local_only"),
    )


def read_csv(filename):
    with (DATA_DIR / filename).open(
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def execute_ddl(connection):
    ddl = DDL_FILE.read_text(encoding="utf-8")

    with connection.cursor() as cursor:
        cursor.execute(ddl)

    connection.commit()


def load_dimensions(connection):
    customers = read_csv("customers.csv")
    products = read_csv("products.csv")
    stores = read_csv("stores.csv")
    suppliers = read_csv("suppliers.csv")

    with connection.cursor() as cursor:

        for row in customers:
            cursor.execute(
                """
                INSERT INTO dim_customer
                    (customer_id, name, state)
                VALUES (%s, %s, %s)
                ON CONFLICT (customer_id) DO NOTHING
                """,
                (
                    int(row["customer_id"]),
                    row["name"],
                    row["state"],
                ),
            )

        for row in suppliers:
            cursor.execute(
                """
                INSERT INTO dim_supplier
                    (supplier_id, supplier_name)
                VALUES (%s, %s)
                ON CONFLICT (supplier_id) DO NOTHING
                """,
                (
                    int(row["supplier_id"]),
                    row["supplier_name"],
                ),
            )

        for row in products:
            cursor.execute(
                """
                INSERT INTO dim_product
                    (product_id, product_name, category, supplier_id, cost)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING
                """,
                (
                    int(row["product_id"]),
                    row["product_name"],
                    row["category"],
                    int(row["supplier_id"]),
                    float(row["cost"]),
                ),
            )

        for row in stores:
            cursor.execute(
                """
                INSERT INTO dim_store
                    (store_id, store_name, state, region)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (store_id) DO NOTHING
                """,
                (
                    int(row["store_id"]),
                    row["store_name"],
                    row["state"],
                    row["region"],
                ),
            )

        dates = {
            row["order_date"]
            for row in read_csv("orders.csv")
        }

        for value in dates:
            parsed = date.fromisoformat(value)

            cursor.execute(
                """
                INSERT INTO dim_date
                    (date_key, full_date, year, month)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date_key) DO NOTHING
                """,
                (
                    int(parsed.strftime("%Y%m%d")),
                    parsed,
                    parsed.year,
                    parsed.month,
                ),
            )

    connection.commit()


def load_fact_sales(connection):
    orders = {
        row["order_id"]: row
        for row in read_csv("orders.csv")
    }

    products = {
        row["product_id"]: row
        for row in read_csv("products.csv")
    }

    customers = {
        row["customer_id"]: row
        for row in read_csv("customers.csv")
    }

    stores = {
        row["store_id"]: row
        for row in read_csv("stores.csv")
    }

    order_items = read_csv("order_items.csv")

    with connection.cursor() as cursor:

        for item in order_items:
            order = orders.get(item["order_id"])
            product = products.get(item["product_id"])

            if not order or not product:
                continue

            customer = customers.get(order["customer_id"])
            store = stores.get(order["store_id"])

            if not customer or not store:
                continue

            quantity = int(item["quantity"])
            unit_price = float(item["unit_price"])
            discount = float(item.get("discount") or 0)

            revenue = quantity * unit_price - discount
            profit = revenue - (
                quantity * float(product["cost"])
            )

            order_date = date.fromisoformat(
                order["order_date"]
            )

            date_key = int(
                order_date.strftime("%Y%m%d")
            )

            cursor.execute(
                """
                INSERT INTO fact_sales
                    (
                        date_key,
                        customer_key,
                        product_key,
                        store_key,
                        quantity,
                        revenue,
                        discount,
                        profit
                    )
                SELECT
                    %s,
                    c.customer_key,
                    p.product_key,
                    s.store_key,
                    %s,
                    %s,
                    %s,
                    %s
                FROM dim_customer c
                JOIN dim_product p
                    ON p.product_id = %s
                JOIN dim_store s
                    ON s.store_id = %s
                WHERE c.customer_id = %s
                """,
                (
                    date_key,
                    quantity,
                    round(revenue, 2),
                    round(discount, 2),
                    round(profit, 2),
                    int(item["product_id"]),
                    int(order["store_id"]),
                    int(order["customer_id"]),
                ),
            )

    connection.commit()


def main():
    connection = get_connection()

    try:
        print("Creating warehouse tables...")
        execute_ddl(connection)

        print("Loading dimension tables...")
        load_dimensions(connection)

        print("Loading fact_sales...")
        load_fact_sales(connection)

        print("Warehouse loading completed successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()