from backend.lbfl.src.configs.config_reader import ConfigReader, Drain3KafkaPersistenceStateConfig
from backend.lbfl.src.configs.kafka_state_persistence import ConfluentKafkaPersistence
from src.persistence.log_templates_repository import LogTemplateRepository

from drain3 import TemplateMiner
from loguru import logger


class Drain3Client:
    """
    Drain3 client class to interact with Drain3 API.
    """
    def __init__(self):
        self.config_reader = ConfigReader()
        self.log_template_repo = LogTemplateRepository()

        # Set up Drain3 with Kafka persistence
        state_config = Drain3KafkaPersistenceStateConfig(self.config_reader).get_kafka_client_options()
        persistence = ConfluentKafkaPersistence(
            topic=state_config.pop("topic"),
            **state_config
        )
        template_miner_config = self.config_reader.get_drain3_template_miner_config()
        self.template_miner = TemplateMiner(persistence, template_miner_config)


    def add_log_msg_in_drain_template_miner(self, log_message):
        try:
            result = self.template_miner.add_log_message(log_message)
            if result["change_type"] is not None:
                logger.info(f"New template identified: {result['template_mined']}")

                template_id = result["cluster_id"]
                template_text = result["template_mined"]
                # Store the new template using the repository
                self.persist_template(template_id, template_text)
            logger.info(f"Parsed Log Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error processing log: {e}")


    def persist_template(self, template_id, template_text):
        """
        Stores a template using the repository if it doesn't already exist.
        Args:
            template_id (str): Unique ID of the template.
            template_text (str): Text of the log template (masked message).
        """
        try:
            # Check if the template already exists
            existing_template = self.log_template_repo.get_log_template_by_id(template_id)

            if not existing_template:
                # Template doesn't exist, insert it
                self.log_template_repo.save_log_template(template_id, template_text)
                logger.info(f"Template stored: {template_text}")
            else:
                logger.info(f"Template with ID {template_id} already exists.")
        except Exception as e:
            logger.error(f"Failed to store template: {e}")