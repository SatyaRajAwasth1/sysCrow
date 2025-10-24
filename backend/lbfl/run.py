import time
from threading import Thread
from loguru import logger

from backend.lbfl.src.configs.config_reader import ConfigReader
from src.datapreprocessing.raw_log_consumer import RawLogKafkaConsumer
from src.enums.application_mode import ApplicationMode
from backend.lbfl.src.model.models_aggregator import ModelAggregator


class ContinuousLogProcessor:
    def __init__(self, config_reader: ConfigReader, kafka_consumer: RawLogKafkaConsumer,
                 model_provider: ModelAggregator):
        self.config_reader = config_reader
        self.kafka_consumer = kafka_consumer
        self.model_provider = model_provider
        self.first_run_done = False

    def consume_logs(self):
        """Consume logs asynchronously from Kafka."""
        while True:
            # Continuously consume logs from Kafka (asynchronously)
            self.kafka_consumer.consume_and_process_logs()
            # time.sleep(1)

    def start_batch_processing(self):
        """Start batch processing immediately after startup, then on hourly basis."""
        logger.info("Starting initial batch processing immediately after startup...")

        # Perform initial batch processing (within 2 seconds after startup)
        self.model_provider.perform_seq_segmentation_n_fault_localization()

        # Keep performing batch processing every hour
        while True:
            logger.info("New Batch process running . . .")
            if not self.first_run_done:
                time.sleep(600)  # Ensures the first processing happens 2 Seconds after startup
                self.first_run_done = True

            self.model_provider.perform_seq_segmentation_n_fault_localization()
            # Perform batch processing every hour
            logger.info("Current batch processing completed, sleeping to next hour...")
            time.sleep(3600)  # Sleep for 1 hour before running the model again

    def start(self):
        """Start Kafka consumer and batch processing threads."""
        # Start the Kafka consumer thread
        consumer_thread = Thread(target=self.consume_logs)
        consumer_thread.daemon = True
        consumer_thread.start()

        # Start the batch processing thread
        batch_processing_thread = Thread(target=self.start_batch_processing)
        batch_processing_thread.daemon = True
        batch_processing_thread.start()

        # Keep the main thread running indefinitely
        while True:
            time.sleep(1)


if __name__ == '__main__':
    logger.info("Ka Ka Ka Cra Cra c Cro Cs Corwww ... sysCrow started!")

    config_reader = ConfigReader()
    mode = config_reader.get_application_mode()
    model_operation_provider = ModelAggregator()

    if mode.upper() == ApplicationMode.TRAINING.name:
        logger.info("Application running in TRAINING mode, no logs will be consumed, Started training model...")
        model_operation_provider.train_model()
    else:
        logger.info("Application running in INFERENCE mode ...")
        kafka_raw_log_consumer = RawLogKafkaConsumer()
        continuous_log_processor = ContinuousLogProcessor(config_reader, kafka_raw_log_consumer, model_operation_provider)
        continuous_log_processor.start()

# from confluent_kafka import Consumer
#
# consumer = Consumer({
#     'bootstrap.servers': '127.0.0.1:9091,127.0.0.1:9092,127.0.0.1:9093',
#     'group.id': 'test-consumer-group',
#     'auto.offset.reset': 'earliest'
# })
#
# consumer.subscribe(['raw-logs'])
#
# print("Starting consumer...")
# while True:
#     msg = consumer.poll(5.0)
#     if msg is None:
#         print("No message received")
#         continue
#     if msg.error():
#         print(f"Consumer error: {msg.error()}")
#         continue
#
#     print(f"Received message: {msg.value().decode('utf-8')}")
