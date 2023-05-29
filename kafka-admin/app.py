import logging
import os
from time import sleep

from kafka import KafkaAdminClient
from kafka.admin import NewPartitions


def main():
    logging.basicConfig(level=logging.INFO)
    print("test")
    bootstrap_servers = ""

    if 'BOOTSTRAP_SERVERS' in os.environ:
        bootstrap_servers = os.environ['BOOTSTRAP_SERVERS']

    topic = 'stock-worker'
    admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers, api_version=(0, 10, 2))
    topic_partitions = {topic: NewPartitions(total_count=3)}
    admin_client.create_partitions(topic_partitions)

    print(admin_client.list_topics())
    print(admin_client.describe_cluster())

    while True:
        sleep(60)
        print("Keep alive")


if __name__ == "__main__":
    main()
