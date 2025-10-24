from confluent_kafka import Consumer, KafkaError
import json
import logging
import torch
import torch.nn as nn
import time
import argparse
import sys

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

consumer_config = {
    'bootstrap.servers' : 'localhost:9092',
    'group.id': 'log-consumer-group',
    'auto.offset.reset': 'earliest'  # Start from the earliest message
}

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

consumer = Consumer(consumer_config)

def consume_logs():
    consumer.subscribe(['parsed_logs_topic'])
    try: 
        while True:
            msg = consumer.poll(10)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
            else:
                parsed_log = msg.value().decode('utf-8')
                print("log read from the kafka topic:", parsed_log)
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_logs()
                