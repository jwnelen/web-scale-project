import json
import logging

from kafka import KafkaConsumer, KafkaProducer

logging.basicConfig(level=logging.INFO)


class KafkaConnector:

    def __init__(self, bootstrap_servers, group_id, topic):
        super().__init__()
        self.type = "Kafka REST Connector"

        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                      api_version=(0, 10, 2))

        self.consumer = KafkaConsumer(topic,
                                      group_id=group_id,
                                      bootstrap_servers=bootstrap_servers,
                                      api_version=(0, 10, 2),
                                      request_timeout_ms=600000,
                                      connections_max_idle_ms=1200000)

    def deliver_response(self, topic, payload):
        self.producer.send(topic, json.dumps(payload).encode('utf-8'))
        self.producer.flush()
