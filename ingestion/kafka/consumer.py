import json
from kafka import KafkaConsumer
def consume(bootstrap_servers: str, topic: str, group_id: str = "retail-curation"):
    return KafkaConsumer(topic, bootstrap_servers=bootstrap_servers, group_id=group_id, value_deserializer=lambda v: json.loads(v))
