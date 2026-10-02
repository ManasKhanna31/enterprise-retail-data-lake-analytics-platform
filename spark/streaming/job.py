"""Spark Structured Streaming entry point for retail.orders."""
from pyspark.sql import SparkSession, functions as F, types as T
EVENT_SCHEMA = T.StructType([T.StructField("order_id", T.IntegerType()), T.StructField("product_id", T.IntegerType()), T.StructField("store_id", T.IntegerType()), T.StructField("quantity", T.IntegerType()), T.StructField("amount", T.DoubleType()), T.StructField("timestamp", T.TimestampType())])
def run(bootstrap_servers: str, topic: str, checkpoint: str, output: str):
    spark = SparkSession.builder.appName("retail-orders-stream").getOrCreate()
    events = spark.readStream.format("kafka").option("kafka.bootstrap.servers", bootstrap_servers).option("subscribe", topic).load()
    parsed = events.select(F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("event")).select("event.*").filter((F.col("quantity") > 0) & F.col("order_id").isNotNull())
    query = parsed.writeStream.format("parquet").option("path", output).option("checkpointLocation", checkpoint).outputMode("append").start()
    query.awaitTermination()
