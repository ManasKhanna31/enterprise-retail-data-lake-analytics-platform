import json
from kafka import KafkaProducer
def create_producer(bootstrap_servers: str):
    return KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda v: json.dumps(v).encode())
