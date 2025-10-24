from confluent_kafka import Consumer

from backend.lbfl.src.configs.config_reader import ConfigReader


class KafkaConfigurationProvider:

    def __init__(self):
        self.config_reader = ConfigReader()

    def get_kafka_consumer(self):
        consumer_configs = self.config_reader.get_kafka_consumer_config()
        return Consumer(consumer_configs.to_dict())

