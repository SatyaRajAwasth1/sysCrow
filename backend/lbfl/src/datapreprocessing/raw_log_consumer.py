import re
from drain3 import TemplateMiner
from loguru import logger

from backend.lbfl.src.configs.config_reader import ConfigReader, Drain3KafkaPersistenceStateConfig
from backend.lbfl.src.configs.kafka_configs import KafkaConfigurationProvider
from backend.lbfl.src.configs.kafka_state_persistence import ConfluentKafkaPersistence
from src.datapreprocessing.drain_client import Drain3Client
from src.persistence.models import LogDetails
from src.persistence.log_details_repository import LogDetailsRepository


class RawLogKafkaConsumer:

    def __init__(self):
        # Initialize ConfigReader
        self.config_reader = ConfigReader()

        # Get Kafka consumer configuration
        self.raw_log_consumer_config = self.config_reader.get_kafka_consumer_config()
        kafka_config_provider = KafkaConfigurationProvider()
        self.raw_log_consumer = kafka_config_provider.get_kafka_consumer()

        # Set up Drain3 with Kafka persistence
        state_config = Drain3KafkaPersistenceStateConfig(self.config_reader).get_kafka_client_options()
        persistence = ConfluentKafkaPersistence(
            topic=state_config.pop("topic"),
            **state_config
        )
        template_miner_config = self.config_reader.get_drain3_template_miner_config()
        self.template_miner = TemplateMiner(persistence, template_miner_config)
        self.drain_client = Drain3Client()

        # Repositories for log entries
        self.log_entry_repo = LogDetailsRepository()

        # Determine application mode
        self.mode = self.config_reader.get_application_mode()

        # Define log pattern regex
        self.log_pattern = re.compile(
            # r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s\[(?P<thread>[^\]]+)\]\s(?P<level>\w+)\s\[(?P<correlationId>[^\]]+)\]\s(?P<logger>[^\s]+)\s-\s(?P<message>.+)"
            r"(?P<timestamp>\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d{3})\s\[(?P<thread>[^\]]+)\]\s(?P<level>\w+)\s*(?P<logger>[^\s]+)\s-\s*(?P<message>.+)"
        )

    def consume_and_process_logs(self):
        logger.info(f"Starting consuming logs from Kafka with consumer configs: {self.raw_log_consumer_config.to_dict()} \n"
              f"and processing in {self.mode} mode...")

        self.raw_log_consumer.subscribe([self.raw_log_consumer_config.inference_topic])

        while True:
            msg = self.raw_log_consumer.poll(5.0)
            if msg:
                log_message = msg.value().decode("utf-8")
                match = self.log_pattern.match(log_message)

                if match:
                    parsed_log = match.groupdict()
                    logger.info(f"Parsed log: {parsed_log}")
                    self.process_inference_mode(parsed_log)
                else:
                    logger.error(f"Log message does not match expected pattern: {log_message}")
            else:
                logger.info("No new messages received.")


    def process_inference_mode(self, parsed_log):
        """Process log message in inference mode."""
        try:
            log_message = parsed_log["message"]
            # Use the template miner to check for log message patterns
            result = self.template_miner.match(log_message)

            # correlation_id=parsed_log["correlationId"],
            log_entry = LogDetails(
                timestamp=parsed_log["timestamp"],
                thread=parsed_log["thread"],
                level=parsed_log["level"],
                correlation_id=parsed_log["thread"],
                logger_name=parsed_log["logger"],
                template_id=0,
            )

            if result:
                template_text = result.get_template()

                logger.info(f"Matched Template: {template_text}")

                # Extract properties from the template miner's result
                properties = self.template_miner.get_parameter_list(template_text, log_message)

                log_entry.template_id = result.cluster_id
                log_entry.properties = ",".join(map(str, properties)).removesuffix(",")

            else:
                logger.info("No matching template found for the log message, adding message to drain")
                added_result = self.drain_client.add_log_msg_in_drain_template_miner(log_message)

                # The added result should have the new template_id
                log_entry.template_id = added_result.get("cluster_id", None)

            # Persist log details using the repository regardless of whether a new template was found
            self.persist_log_details(log_entry)

        except Exception as e:
            logger.error(f"Error processing log in inference mode: {e}")



    def persist_log_details(self, log_entry):
        """
        Persists log details using the repository.
        Args:
            log_entry (LogDetails): Log entry object.
        """
        try:
            # Persist the log entry using the ProcessedLogsRepository
            self.log_entry_repo.save_log_entry(log_entry)
            logger.info(f"Log details persisted: {log_entry}")
        except Exception as e:
            logger.error(f"Failed to persist log details: {e}")
