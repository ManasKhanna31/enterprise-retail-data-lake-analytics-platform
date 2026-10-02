
"""Spark Structured Streaming entry point for retail.orders."""

from pyspark.sql import SparkSession, functions as F, types as T


EVENT_SCHEMA = T.StructType(
    [
        T.StructField("order_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("store_id", T.StringType(), True),
        T.StructField("product_id", T.StringType(), True),
        T.StructField("quantity", T.IntegerType(), True),
        T.StructField("unit_price", T.DoubleType(), True),
    ]
)


def run(
    bootstrap_servers: str,
    topic: str,
    checkpoint: str,
    output: str,
) -> None:
    spark = (
        SparkSession.builder
        .appName("retail-orders-stream")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4",
        )
        .getOrCreate()
    )

    events = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", topic)
        .option("startingOffsets", "earliest")
        .load()
    )

    parsed = (
        events
        .select(
            F.from_json(
                F.col("value").cast("string"),
                EVENT_SCHEMA,
            ).alias("event")
        )
        .select("event.*")
        .filter(
            (F.col("order_id").isNotNull())
            & (F.col("quantity") > 0)
            & (F.col("unit_price") >= 0)
        )
        .withColumn(
            "amount",
            F.col("quantity") * F.col("unit_price"),
        )
        .withColumn(
            "timestamp",
            F.current_timestamp(),
        )
    )

    query = (
    parsed.writeStream
    .format("parquet")
    .option("path", output)
    .option("checkpointLocation", checkpoint)
    .outputMode("append")
    .trigger(once=True)
    .start()
)

    query.awaitTermination()


if __name__ == "__main__":
    run(
        bootstrap_servers="localhost:9092",
        topic="retail.orders",
        checkpoint="data/checkpoints/retail_orders",
        output="data/lake/streaming/orders",
    )
