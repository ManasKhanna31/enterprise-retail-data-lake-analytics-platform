"""PySpark Bronze -> Silver -> Gold transformation job."""

from pathlib import Path

from pyspark.sql import SparkSession, functions as F


def create_spark_session() -> SparkSession:
    """Create a local Spark session."""
    return (
        SparkSession.builder
        .appName("EnterpriseRetailDataLake")
        .master("local[2]")
        .getOrCreate()
    )


def transform(
    bronze_dir: str = "data/lake/bronze",
    silver_dir: str = "data/lake/silver_spark",
    gold_dir: str = "data/lake/gold_spark",
) -> None:
    """Read Bronze data, create Silver datasets, and build Gold fact_sales."""

    spark = create_spark_session()

    try:
        bronze = Path(bronze_dir)
        silver = Path(silver_dir)
        gold = Path(gold_dir)

        silver.mkdir(parents=True, exist_ok=True)
        gold.mkdir(parents=True, exist_ok=True)

        # -------------------------
        # 1. Read Bronze
        # -------------------------
        orders = spark.read.json(str(bronze / "orders.json"))
        order_items = spark.read.json(str(bronze / "order_items.json"))
        products = spark.read.json(str(bronze / "products.json"))

        print("=== BRONZE COUNTS ===")
        print("Orders:", orders.count())
        print("Order Items:", order_items.count())
        print("Products:", products.count())

        # -------------------------
        # 2. Silver transformations
        # -------------------------
        orders_silver = (
            orders
            .filter(F.col("order_id").isNotNull())
            .dropDuplicates(["order_id"])
        )

        order_items_silver = (
            order_items
            .filter(F.col("order_id").isNotNull())
            .filter(F.col("product_id").isNotNull())
            .filter(F.col("quantity").cast("int") > 0)
            .dropDuplicates(["order_id", "product_id"])
        )

        products_silver = (
            products
            .filter(F.col("product_id").isNotNull())
            .dropDuplicates(["product_id"])
        )

        # Save Silver
        orders_silver.write.mode("overwrite").json(
            str(silver / "orders")
        )

        order_items_silver.write.mode("overwrite").json(
            str(silver / "order_items")
        )

        products_silver.write.mode("overwrite").json(
            str(silver / "products")
        )

        print("\n=== SILVER COUNTS ===")
        print("Orders:", orders_silver.count())
        print("Order Items:", order_items_silver.count())
        print("Products:", products_silver.count())

        # -------------------------
        # 3. Gold transformation
        # -------------------------
        gold_df = (
            orders_silver
            .join(order_items_silver, "order_id")
            .join(products_silver, "product_id")
            .withColumn(
                "revenue",
                F.col("quantity") * F.col("unit_price")
                - F.coalesce(F.col("discount"), F.lit(0))
            )
            .withColumn(
                "profit",
                F.col("revenue")
                - F.col("quantity") * F.col("cost")
            )
            .select(
                "order_id",
                "order_date",
                "customer_id",
                "store_id",
                "product_id",
                "category",
                "quantity",
                "revenue",
                "profit",
            )
        )

        # -------------------------
        # 4. Write Gold
        # -------------------------
        gold_df.write.mode("overwrite").json(
            str(gold / "fact_sales")
        )

        print("\n=== GOLD ===")
        print("Rows:", gold_df.count())

        gold_df.show(truncate=False)

        print("\nSpark transformation completed successfully.")

    finally:
        spark.stop()


if __name__ == "__main__":
    transform()