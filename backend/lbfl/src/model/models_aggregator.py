from backend.lbfl.src.configs.config_reader import ConfigReader
from src.datapreprocessing.drain_client import Drain3Client
from backend.lbfl.src.model.context_based_fault_localization import ContextBasedFaultLocalizer
from backend.lbfl.src.model.sequence_segmentation import UnsupervisedSequenceSegmenter

import re
import pandas as pd
from datetime import datetime
from loguru import logger
import os


class ModelAggregator:

    def __init__(self):
        config_reader = ConfigReader()
        log_config = config_reader.get_log_config()

        # Use paths from the config file
        self.training_dataset_dot_log_source = log_config['training_log_file']
        self.csv_extracted_from_logs_path = log_config['training_csv_file']
        self.path_to_ngram_tree = log_config['ngram_tree_path']
        self.training_data_segments = log_config['training_segmented_sequence']

        self.drain_client = Drain3Client()
        self.sequence_segmentor = UnsupervisedSequenceSegmenter()
        self.fault_localizer = ContextBasedFaultLocalizer(self.training_data_segments)
        # Regular expression pattern to match log format
        self.log_pattern = re.compile(
            r"(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s\[(?P<thread>[^\]]+)\]\s(?P<level>\w+)\s\[(?P<correlationId>[^\]]+)\]\s(?P<logger>[^\s]+)\s-\s(?P<message>.+)"
            # r"(?P<timestamp>\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d{3})\s\[(?P<thread>[^\]]+)\]\s(?P<level>\w+)\s*(?P<logger>[^\s]+)\s-\s*(?P<message>.+)" #
        )

        # Check if the CSV file exists, if not create it
        self._ensure_csv_file_exists()


    def perform_seq_segmentation_n_fault_localization(self):
        """
        Performs sequence segmentation and fault localization using a pre-trained model
        """
        current_batch = get_current_batch()
        logger.info(f"Performing sequence segmentation and fault localization for batch: {current_batch}")
        self.sequence_segmentor.perform_unsupervised_sequence_segmentation(current_batch, self.path_to_ngram_tree)
        self.fault_localizer.localize_fault_for_batch(current_batch)


    def train_model(self):
        """
        Train the model by reading log file, processing messages with Drain3Client,
        and appending results to a CSV file.
        """
        logger.info("Starting model training...")

        log_entry = []  # To store multi-line log entries
        timestamp_pattern = re.compile(
            r"^\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d{3}")  # Pattern to detect new log entry

        with open(self.training_dataset_dot_log_source, 'r') as log_file:
            for line in log_file:
                if timestamp_pattern.match(line):  # New log entry starts
                    if log_entry:  # Process the previous log entry
                        self.process_log_entry("".join(log_entry))
                    log_entry = [line]  # Start a new log entry
                else:
                    log_entry.append(line)  # Continue appending lines to the current log entry

            # Process the last log entry in the file
            if log_entry:
                self.process_log_entry("".join(log_entry))

        self.sequence_segmentor.train_model_and_export_ngram_tree(
            self.csv_extracted_from_logs_path, self.training_data_segments, self.path_to_ngram_tree
        )
        logger.info("Model training completed.")

    def process_log_entry(self, log_entry):
        """ Process a single log entry """
        match = self.log_pattern.match(log_entry.strip())
        if match:
            log_data = match.groupdict()
            message = log_data["message"]

            # Process with Drain3Client
            result = self.drain_client.add_log_msg_in_drain_template_miner(message)

            # If a new template was identified, append to CSV
            if result and result.get("change_type") is not None:
                logger.info(f"New template identified: {result.get('template_mined')}")
                self.append_to_csv(log_data, result)
        else:
            logger.error(f"Log entry did not match log pattern:\n{log_entry}")


    def append_to_csv(self, log_data, result):
        """
        Appends the result of the log processing to a CSV file using Pandas.
        """
        timestamp = log_data.get("timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        thread = log_data.get("thread", "Unknown")
        level = log_data.get("level", "Unknown")
        correlation_id = log_data.get("correlationId", log_data.get("thread", "Unknown"))
        logger_name = log_data.get("logger", "Unknown")
        template_id = result.get("cluster_id", "Unknown")
        properties = result.get("template_mined", "")

        # Load existing CSV data into a DataFrame to get the last row index
        try:
            df = pd.read_csv(self.csv_extracted_from_logs_path)
            line_number = len(df) + 1  # Next line number is the length of the DataFrame + 1
        except FileNotFoundError:
            # If file does not exist, start from line 1
            line_number = 1
            df = pd.DataFrame(
                columns=['line_number', 'timestamp', 'thread', 'level', 'correlation_id', 'logger_name', 'template_id',
                         'properties'])

        # Prepare the new data as a DataFrame row
        new_row = pd.DataFrame([{
            'line_number': line_number,
            'timestamp': timestamp,
            'thread': thread,
            'level': level,
            'correlation_id': correlation_id,
            'logger_name': logger_name,
            'template_id': template_id,
            'properties': properties
        }])

        # Append the new row to the DataFrame
        df = pd.concat([df, new_row], ignore_index=True)

        # Write the updated DataFrame back to the CSV
        df.to_csv(self.csv_extracted_from_logs_path, index=False)
        logger.info("Appended data to CSV successfully.")


    def _ensure_csv_file_exists(self):
        """
        Checks if the CSV file exists. If not, it creates the file and writes the header.
        """
        if not os.path.isfile(self.csv_extracted_from_logs_path):
            # Create and write the header if the file does not exist
            df = pd.DataFrame(
                columns=['line_number', 'timestamp', 'thread', 'level', 'correlation_id', 'logger_name', 'template_id',
                         'properties'])
            df.to_csv(self.csv_extracted_from_logs_path, index=False)
            logger.info(f"Created new CSV file and added header: {self.csv_extracted_from_logs_path}")


def get_current_batch():
    return "sample-batch"
