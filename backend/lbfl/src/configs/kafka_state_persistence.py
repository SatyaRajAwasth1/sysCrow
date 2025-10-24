import logging
from typing import Any, Optional
from confluent_kafka import Producer, Consumer, TopicPartition
from drain3.persistence_handler import PersistenceHandler
from loguru import logger


class ConfluentKafkaPersistence(PersistenceHandler):
    """
    A confluent kafka version of KafkaPersistence for Drain3 state persistence.
    """

    def __init__(self, topic: str, snapshot_poll_timeout_sec: int = 60, **kafka_client_options: Any) -> None:
        self.topic = topic
        kafka_client_options['auto.offset.reset'] = 'earliest'
        kafka_client_options['enable.auto.commit'] = False
        self.kafka_client_options = kafka_client_options
        self.snapshot_poll_timeout_sec = snapshot_poll_timeout_sec

        # Initialize Confluent Kafka producer
        self.producer = Producer(**self.kafka_client_options)
        logger.info(
            f"Initializing ConfluentKafkaPersistence topic {self.topic} for Drain3 state persistence with client options {self.kafka_client_options} \n")

    def save_state(self, state: bytes) -> None:
        """Saves the serialized state to Kafka."""

        def delivery_report(err, msg):
            if err is not None:
                logger.error(f"Delivery failed: {err}")
            else:
                logger.info(f"Message delivered to {msg.topic()} [Partition {msg.partition()}]")

        self.producer.produce(self.topic, value=state, callback=delivery_report)
        self.producer.flush()  # Ensure the message is sent before returning

    def load_state(self) -> Optional[bytes]:
        """Loads the latest state from Kafka."""
        # Initialize Confluent Kafka consumer
        consumer = Consumer(**self.kafka_client_options)

        # Assign the consumer to the specified topic and partition
        partition = TopicPartition(self.topic, 0)
        consumer.assign([partition])

        # Ensure assignment is updated
        consumer.poll(0)  # Fetch metadata and avoid erroneous seek

        end_offsets = consumer.get_watermark_offsets(partition)
        end_offset = end_offsets[1]  # High watermark is the latest offset

        state = None

        if end_offset > 0:
            last_offset = end_offset - 1
            # Seek to the last message
            consumer.seek(TopicPartition(self.topic, 0, last_offset))

            msg = consumer.poll(self.snapshot_poll_timeout_sec)
            if msg is None or msg.error():
                raise RuntimeError(f"Error receiving message during restore: {msg.error() if msg else 'Timeout'}")

            state = msg.value()

        consumer.close()
        return state
