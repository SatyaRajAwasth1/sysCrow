import csv
import os
import pickle
from collections import defaultdict
from pathlib import Path
from loguru import logger

from backend.lbfl.src.configs.config_reader import ConfigReader
from backend.lbfl.src.model.voting_experts import VotingExperts
from src.persistence.log_details_repository import LogDetailsRepository
from src.persistence.unsupervised_segmented_sequence_repo import UnsupervisedSegmentedSequencesRepository
from src.persistence.models import UnsupervisedSegmentedSequence


class UnsupervisedSequenceSegmenter:
    def __init__(self, window_size=7, threshold=4):
        config_reader = ConfigReader()
        self.window = window_size
        self.threshold = threshold
        self.mode = config_reader.get_application_mode().upper()
        self.ve = VotingExperts(window_size, threshold)
        self.log_details_repo = LogDetailsRepository()
        self.segmented_sequences_repo = UnsupervisedSegmentedSequencesRepository()
        logger.info(f"UnsupervisedSequenceSegmenter initialized with window_size={self.window}, threshold={self.threshold}")


    def train_model_and_export_ngram_tree(self, training_dataset_csv, training_data_segments_path, path_to_export_ngram_tree):
        logger.info(f"Starting model training and n-gram tree export with dataset: {training_dataset_csv}")

        # Step 1: Read logs from the log file (training mode)
        #log_entries = read_logs_from_file(training_dataset_csv)
        log_entries = pd.read_csv(training_dataset_csv)
        logger.info(f"Read {len(log_entries)} log entries for model training.")

        # Step 2: Prepare event dictionary
        # event_dict = defaultdict(list)
        # for log_entry in log_entries:
        #     if log_entry['correlation_id'] and log_entry['template_id']:
        #         event_dict[log_entry['correlation_id']].append(log_entry['template_id'])
        event_dict = log_entries.groupby('correlation_id')['template_id'].apply(list).to_dict()

        # Step 3: Apply fit on VotingExperts to build n-gram tree and standardize
        self.ve.fit(event_dict)
        logger.info("VotingExperts model fitting completed.")

        # Step 4: Apply transform method for segmentation
        segmentation = self.ve.transform(event_dict, self.window, self.threshold)
        logger.info(f"Segmentation completed with {len(segmentation)} segmented sequences.")

        # Step 5: Export the segmented sequences to CSV
        export_segmentations_to_csv(log_entries, segmentation, training_data_segments_path)

        # Step 6: Export the n-gram tree to a file
        self.export_ngram_tree(path_to_export_ngram_tree)

        return segmentation


    def perform_unsupervised_sequence_segmentation(self, batch_title, ngram_tree_path):
        # Step 1: Load the pre-trained n-gram tree
        logger.info(f"Starting unsupervised sequence segmentation for batch: {batch_title}")

        if ngram_tree_path is None or not Path(ngram_tree_path).is_file():
            logger.error("ngram_tree_path is not provided or the file does not exist.")
            raise ValueError("ngram_tree_path is not provided or the file does not exist.")

        # Load the n-gram tree from the specified file
        with open(ngram_tree_path, 'rb') as file:
            self.ve.ngram_tree = pickle.load(file)

        # Step 2: Read logs from the database for segmentation
        log_entries = self.log_details_repo.get_log_entries()
        logger.info(f"Loaded {len(log_entries)} log entries from the database.")

        # Prepare the event dictionary
        event_dict = defaultdict(list)
        for log_entry in log_entries:
            if log_entry.correlation_id and log_entry.template_id:
                event_dict[log_entry.correlation_id].append(log_entry.template_id)

        # Step 3: Apply the transform method for segmentation
        segmentations = self.ve.transform(event_dict, self.window, self.threshold)
        logger.info(f"Segmentation completed with {len(segmentations)} segmented sequences.")

        # Step 4: Persist the segmented sequences to the database
        self.persist_segmentations(segmentations, batch_title)
        logger.info(f"Segmentations for batch {batch_title} have been persisted successfully.")

        return segmentations


    def export_ngram_tree(self, path_to_export_ngram_tree):
        """Export the n-gram tree to a file, creating a new file or overwriting the existing one."""
        if not path_to_export_ngram_tree:
            logger.error("Path to export n-gram tree is not provided.")
            raise ValueError("Path to export n-gram tree is not provided.")

        try:
            # Open the file in write-binary mode ('wb'). This creates a new file or overwrites if it exists.
            with open(path_to_export_ngram_tree, 'wb') as file:
                pickle.dump(self.ve.ngram_tree, file)
            logger.info(f"Successfully exported n-gram tree to {path_to_export_ngram_tree}")
        except Exception as e:
            logger.error(f"Failed to export n-gram tree: {e}")
            raise


    def persist_segmentations(self, segmentations, batch_title):
        """Persist the segmented sequences in the unsupervised_segmented_sequences table."""
        sequences_to_save = []
        for correlation_id, event_sequence in segmentations.items():
            # Create a new UnsupervisedSegmentedSequence entry
            segmented_sequence = UnsupervisedSegmentedSequence(
                correlation_id=correlation_id,
                event_sequence=str(event_sequence),  # Convert to string if needed
                line_sequence=str([]),  # Or provide appropriate data
                timestamp=None, #TODO: Store sequence init and end timestamp
                batch=batch_title
            )
            sequences_to_save.append(segmented_sequence)

        self.segmented_sequences_repo.save_sequences(sequences_to_save)
        logger.info(f"Persisted {len(sequences_to_save)} segmented sequences.")


import pandas as pd

def ve_segmentation(df, segmentation):
    new_data = []
    seq_number = 1  # Initialize sequence number for the output

    # Group the DataFrame by 'correlation_id'
    grouped_by_correlation_id = df.groupby('correlation_id')

    for correlation_id, df_window in grouped_by_correlation_id:
        # For each 'correlation_id', retrieve the corresponding segmented sequences
        segments = segmentation.get(correlation_id, [])

        start_idx = 0  # Index to keep track of where we are in the DataFrame for each correlation_id

        for segment in segments:
            # Segment is a list of event indices from the segmented sequence
            df_window_segment = df_window.iloc[start_idx:start_idx + len(segment)]

            if len(df_window_segment) > 1:
                if len(df_window_segment) > 512:
                    start = 0
                    end = len(segment)

                    # If the window length exceeds 512, split into smaller windows
                    while (end - start) > 512:
                        df_window_inner = df_window_segment.iloc[start:start + 512]
                        new_data.append([
                            seq_number,  # sequence number
                            correlation_id,  # correlation_id
                            ','.join(df_window_inner['template_id'].astype(str)),  # event_sequence (comma-separated)
                            ','.join(df_window_inner['line_number'].astype(str)),  # line_sequence (comma-separated)
                            ','.join(df_window_inner['timestamp'].astype(str)),  # timestamp (comma-separated)
                        ])
                        seq_number += 1
                        start += 512  # Move by 512 each time

                    # Append the remaining part if any
                    if start < end:
                        df_window_segment = df_window_segment.iloc[start:end]
                        new_data.append([
                            seq_number,  # sequence number
                            correlation_id,  # correlation_id
                            ','.join(df_window_segment['template_id'].astype(str)),  # event_sequence
                            ','.join(df_window_segment['line_number'].astype(str)),  # line_sequence
                            ','.join(df_window_segment['timestamp'].astype(str)),  # timestamp
                        ])
                        seq_number += 1
                else:
                    # No need to split if the segment length is less than 512
                    new_data.append([
                        seq_number,  # sequence number
                        correlation_id,  # correlation_id
                        ','.join(df_window_segment['template_id'].astype(str)),  # event_sequence
                        ','.join(df_window_segment['line_number'].astype(str)),  # line_sequence
                        ','.join(df_window_segment['timestamp'].astype(str)),  # timestamp
                    ])
                    seq_number += 1

                start_idx += len(segment)  # Move start index for the next segment
            else:
                # If the segment length is 1 or invalid, just skip
                start_idx += 1


    # Return the DataFrame with desired columns
    return pd.DataFrame(new_data, columns=['s.n.', 'correlation_id', 'event_sequence', 'line_sequence', 'timestamp'])


def export_segmentations_to_csv(dataframe, segmentation, training_data_segments_path):
    logger.info(f"Exporting segmented sequences to CSV at {training_data_segments_path}")

    # Write the segmented sequences to a CSV file
    dataframe = ve_segmentation(dataframe, segmentation)
    dataframe.to_csv(training_data_segments_path, index=False)

    logger.info(f"Segmented sequences have been exported to {training_data_segments_path}")


def read_logs_from_file(file_path):
    """Reads logs from a CSV or similar file and formats them as a list of dictionaries."""
    if not file_path or not os.path.isfile(file_path):
        logger.error(f"Invalid log file path: {file_path}")
        raise ValueError(f"Invalid log file path: {file_path}")

    log_entries = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            log_entries.append({
                'timestamp': row['timestamp'],
                'thread': row['thread'],
                'level': row['level'],
                'correlation_id': row['correlation_id'],
                'logger_name': row['logger_name'],
                'template_id': row['template_id'],
                'properties': row['properties']  # Assuming properties column contains JSON
            })
    logger.info(f"Read {len(log_entries)} logs from file: {file_path}")

    return log_entries
