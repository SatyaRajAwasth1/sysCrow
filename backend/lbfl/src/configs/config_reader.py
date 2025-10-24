import yaml
from drain3.template_miner_config import TemplateMinerConfig


class ConfigReader:
    def __init__(self, config_file='D:\exp\\research\\sysCrow\\backend\\lbfl\\config.yml'):
        self.config_file = config_file
        self.configs = self.load_config()

    def load_config(self):
        """Load and parse the YAML configuration file."""
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file)
                if not config:
                    raise ValueError("Config file is empty or invalid.")
                return config
        except Exception as e:
            raise RuntimeError(f"Failed to load config file: {e}")

    def get_application_mode(self) -> str:
        """Get the application mode from the configuration file."""
        return self.configs.get('application', {}).get('mode', 'inference')

    def get_kafka_consumer_config(self):
        """Get the Kafka consumer configuration."""
        kafka_config = self.configs.get('kafka', {}).get('log-consumer', {})
        return KafkaConsumerConfig(
            training_topic=kafka_config.get('training_mode_topic', 'raw-logs'),
            inference_topic=kafka_config.get('inference_mode_topic', 'raw-logs'),
            bootstrap_servers=kafka_config.get('bootstrap_servers', 'localhost:9092'),
            auto_offset_reset=kafka_config.get('auto_offset_reset', 'earliest'),
            enable_auto_commit=kafka_config.get('enable_auto_commit', True),
            group_id=kafka_config.get('group_id', 'default-consumer-group')
        )

    def get_state_persistence_config(self):
        """Get the Kafka state persistence configuration."""
        config = self.load_config()
        state_config = config.get('kafka', {}).get('state-persistence', {})
        return state_config

    def get_mysql_configs(self):
        config = self.load_config()
        return config.get('persistence', {}).get('mysql', {})

    def get_drain3_template_miner_config(self):
        """Get the drain3 template miner configuration."""
        config = TemplateMinerConfig()
        config.load(self.configs.get('template-miner', {}).get('drain3_config_url', 'drain3.ini'))
        return config

    def get_log_config(self):
        """Get the paths for the log files and CSV file."""
        log_config = self.configs.get('log-config', {})
        return {
            'ngram_tree_path': log_config.get('ngram_tree_path', './.tmp/ngram.tree'),
            'training_log_file': log_config.get('training_log_file', './data/training_dataset.log'),
            'training_csv_file': log_config.get('training_csv_file', './.tmp/training_dataset.csv'),
            'training_segmented_sequence': log_config.get('training_segmented_sequence','./data/training_data_segments.csv')
        }

    # @Deprecated
    def get_elastic_config(self):
        """Get the Elasticsearch configuration."""
        elastic_config = self.configs.get('persistence', {}).get('elasticsearch', {})
        connection = elastic_config.get('connection', {})
        indices = elastic_config.get('indices', {})
        processed_logs = indices.get('activities', {})
        return ElasticConfig(
            hosts=connection.get('hosts', ['http://localhost:9200']),
            username=connection.get('username'),
            password=connection.get('password'),
            verify_certs=connection.get('verify_certs', False),
            indices=ElasticConfig.Indices(
                suspicious_sequence=indices.get('suspicious_sequences', 'suspicious-sequence'),
                processed_logs_indices=ElasticConfig.Indices.ProcessedLogIndices(
                    log_details=processed_logs.get('log_details', 'log-details'),
                    templates=processed_logs.get('templates', 'log-templates'),
                    properties=processed_logs.get('properties', 'log-properties')
                )
            )
        )


class KafkaConsumerConfig:
    def __init__(self, training_topic, inference_topic, bootstrap_servers, auto_offset_reset, enable_auto_commit,
                 group_id):
        self.training_topic = training_topic
        self.inference_topic = inference_topic
        self.bootstrap_servers = bootstrap_servers
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.group_id = group_id

    def to_dict(self):
        return {
            'bootstrap.servers': self.bootstrap_servers,
            'auto.offset.reset': self.auto_offset_reset,
            'enable.auto.commit': self.enable_auto_commit,
            'group.id': self.group_id,
        }


class Drain3KafkaPersistenceStateConfig:
    def __init__(self, config_reader: ConfigReader):
        state_persistence_configs = config_reader.get_state_persistence_config()
        self.configs = state_persistence_configs
        self.configs['bootstrap.servers'] = self.configs.pop('bootstrap_servers', 'localhost:9092')
        self.configs["group.id"] = "drain3-state-group"
        self.configs["auto.offset.reset"] = "earliest"

    def get_kafka_client_options(self):
        return self.configs


class ElasticConfig:
    def __init__(self, hosts, username, password, verify_certs, indices):
        self.hosts = hosts
        self.username = username
        self.password = password
        self.verify_certs = verify_certs
        self.indices = indices

    def con_dict(self):
        """Return a dictionary with connection properties."""
        return {
            'hosts': self.hosts,
            'http_auth': (self.username, self.password) if self.username and self.password else None,
            'verify_certs': self.verify_certs,
        }

    class Indices:
        def __init__(self, suspicious_sequence, processed_logs_indices):
            self.suspicious_sequence = suspicious_sequence
            self.processed_logs_indices = processed_logs_indices

        class ProcessedLogIndices:
            def __init__(self, log_details, templates, properties):
                self.log_details = log_details
                self.templates = templates
                self.properties = properties
