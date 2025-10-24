from collections import Counter

import numpy as np
import pandas as pd
from loguru import logger

from src.persistence.models import SuspiciousLogSequence
from src.persistence.suspicious_logs_repository import SuspiciousLogSequencesRepository
from src.persistence.unsupervised_segmented_sequence_repo import UnsupervisedSegmentedSequencesRepository


class ContextBasedFaultLocalizer:
    def __init__(self, training_seq_segmented_data_path):
        self.train_file_path = training_seq_segmented_data_path  # Path to the file exported after unsupervised sequence segmentation on training data
        self.unsupervised_sequences_repo = UnsupervisedSegmentedSequencesRepository()
        self.suspicious_sequences_repo = SuspiciousLogSequencesRepository()

    def localize_fault_for_batch(self, batch_title):
        # Step 1: Read training data from the file
        train = pd.read_csv(self.train_file_path, index_col=0)
        train["event_sequence"] = train["event_sequence"].apply(lambda x: eval(x))  # Convert string to list

        # Step 2: Build vocabulary and calculate suspiciousness score from the training data
        bigdoc = []
        for idx, row in train.iterrows():
            bigdoc.extend(list(set(row["event_sequence"])))
        vocab = set(bigdoc)
        cnt = Counter(bigdoc)

        # Step 3: Fetch unsupervised segmented sequences from the database (inference data)
        inference_sequences = self.unsupervised_sequences_repo.get_sequences_by_batch(batch_title, limit=10000)

        # Step 4: Build vocabulary for inference data and calculate suspiciousness scores
        fail_bigdoc = []
        for seq in inference_sequences:
            event_sequence = eval(seq.event_sequence)  # Convert string to list
            fail_bigdoc.extend(list(set(event_sequence)))
        fail_vocab = set(fail_bigdoc)
        fail_cnt = Counter(fail_bigdoc)

        suspicious_score = {}
        for word in fail_vocab:
            suspicious_score[word] = fail_cnt[word] / (fail_cnt[word] + cnt[word])

        # Step 5: Process each sequence from the inference data and compute the confidence (suspiciousness)
        sbfl_anomalies_segments = []
        sbfl_anomalies_lines = []
        sbfl_anomalous_timestamp = []
        sbfl_anomalous_confidence = []
        confidences = []

        for seq in inference_sequences:
            event_sequence = eval(seq.event_sequence)
            scores = []
            one_word_not_in_vocab = False
            for idx, word in enumerate(event_sequence):
                if word not in vocab:
                    one_word_not_in_vocab = True
                    sbfl_anomalies_lines.append(seq.line_sequence[idx])  # Store the anomalous line number
                if word in suspicious_score:
                    scores.append(suspicious_score[word])
                else:
                    scores.append(0)

            # Calculate confidence based on suspicious score
            confidences.append(np.mean(scores))

            if one_word_not_in_vocab:
                conf_sc = np.mean(scores)
                sbfl_anomalous_confidence.append(1 - conf_sc)
                sbfl_anomalies_segments.append(seq)

                sbfl_anomalous_timestamp.append(np.int64(seq.timestamp[0]))

        # Step 6: Prepare the final suspicious sequences for persistence
        sbfl_anomalies = []
        for idx in sbfl_anomalies_segments:
            suspicious_log_sequence = SuspiciousLogSequence(
                line_sequence=idx.line_sequence,
                event_sequence=idx.event_sequence,
                correlation_id=idx.correlation_id,
                timestamp=sbfl_anomalous_timestamp[sbfl_anomalies_segments.index(idx)],
                confidence=sbfl_anomalous_confidence[sbfl_anomalies_segments.index(idx)]
            )
            sbfl_anomalies.append(suspicious_log_sequence)

        # Step 7: Save the suspicious log sequences to the database
        self.suspicious_sequences_repo.save_sequences(sbfl_anomalies)
        logger.info(f"Persisted {len(sbfl_anomalies)} suspicious log sequences to the database.")







# import numpy as np
# from sqlalchemy.orm import sessionmaker
# from src.persistence.log_details_repository import LogDetailsRepository
# from src.persistence.unsupervised_segmented_sequence_repo import UnsupervisedSegmentedSequencesRepository
# from src.persistence.suspicious_logs_repository import SuspiciousLogSequencesRepository
# from src.persistence.models import SuspiciousLogSequence
# from loguru import logger
#
# class ContextBasedFaultLocalizer:
#     def __init__(self, db_session, train_file_path):
#         self.db_session = db_session  # Database session passed in for DB operations
#         self.train_file_path = train_file_path  # Path to the training file
#         self.log_details_repo = LogDetailsRepository(session=self.db_session)
#         self.unsupervised_sequences_repo = UnsupervisedSegmentedSequencesRepository(session=self.db_session)
#         self.suspicious_sequences_repo = SuspiciousLogSequencesRepository(session=self.db_session)
#
#     def localize_fault(self, test_batch_name):
#         # Step 1: Fetch unsupervised segmented sequences from the database
#         inference_sequences = self.unsupervised_sequences_repo.get_sequences_by_batch(batch=test_batch_name, limit=10000)
#
#         # Step 2: Get the list of templates in the inference sequences
#         template_ids = set()
#         for seq in inference_sequences:
#             event_sequence = eval(seq.event_sequence)  # Convert string back to list
#             for event in event_sequence:
#                 template_ids.add(event['template_id'])  # Assuming each event has 'template_id'
#
#         # Step 3: Fetch success and fail counts for these templates from the DB
#         log_counts = self.log_details_repo.get_log_counts_for_templates(template_ids)
#
#         success_count = {log['template_id']: log['success_count'] for log in log_counts}
#         fail_count = {log['template_id']: log['fail_count'] for log in log_counts}
#
#         # Fetch total fail and pass counts
#         total_fail_count, total_pass_count = self.log_details_repo.get_total_success_fail_counts().values()
#
#         # Step 4: Calculate suspiciousness score for each event in the sequences
#         suspicious_score = {}
#         for template_id in template_ids:
#             fail = fail_count.get(template_id, 0)
#             success = success_count.get(template_id, 0)
#
#             # Susceptibility score based on the formula
#             if (fail + success) > 0:
#                 sus_score = (fail / total_fail_count) / ((fail / total_fail_count) + (success / total_pass_count))
#             else:
#                 sus_score = 0
#             suspicious_score[template_id] = sus_score
#
#         # Step 5: Load training data to calculate suspiciousness score based on context
#         self.calculate_training_scores()
#
#         # Step 6: Apply context-based ranking
#         context_based_rankings = []
#         for seq in inference_sequences:
#             event_sequence = eval(seq.event_sequence)
#             segment_sus_scores = []
#
#             # Get suspiciousness scores for each event in the sequence
#             for event in event_sequence:
#                 template_id = event['template_id']
#                 sus_score = suspicious_score.get(template_id, 0)
#                 segment_sus_scores.append(sus_score)
#
#             # Calculate the mean suspiciousness score for this segment
#             mean_sus_score = np.mean(segment_sus_scores)
#
#             # Calculate context-based ranking for the segment
#             context_rank = 1 - mean_sus_score
#             context_based_rankings.append((seq.line_sequence, context_rank, seq.event_sequence, seq.correlation_id, seq.timestamp))
#
#         # Step 7: Sort sequences by context-based ranking (from most suspicious to least suspicious)
#         sorted_by_context = sorted(context_based_rankings, key=lambda x: x[1], reverse=True)
#
#         self.persist_suspicious_logs(sorted_by_context)
#
#     def calculate_training_scores(self):
#         # Read the training data from the file
#         with open(self.train_file_path, 'r') as file:
#             train_data = file.readlines()
#
#         # Process training data to calculate suspiciousness scores
#         bigdoc = []
#         class_cnt = 0
#         for line in train_data:
#             # Assuming each line contains a JSON or a log entry in a specific format
#             event_sequence = eval(line.strip())  # Parse each line into a list of events
#             for event in event_sequence:
#                 bigdoc.extend(list(set(event)))  # Collect events across training logs
#             class_cnt += 1
#
#         vocab = set(bigdoc)
#         cnt = Counter(bigdoc)
#
#         suspicious_score = {}
#         for word in vocab:
#             # Assuming this step calculates a log sequence suspiciousness score
#             suspicious_score[word] = cnt[word] / (cnt[word] + len(bigdoc))
#
#         # Add logic for calculating training-based suspiciousness score as needed
#         logger.info(f"Training suspiciousness scores calculated.")
#
#     def persist_suspicious_logs(self, log_sequences):
#         # Prepare suspicious logs for database persistence
#         sequences_to_save = []
#         for seq in log_sequences:
#             suspicious_log_sequence = SuspiciousLogSequence(
#                 line_sequence=seq[0],  # Assuming line_sequence is available
#                 event_sequence=seq[2],  # Event sequence as it is
#                 correlation_id=seq[3],  # Assuming correlation_id is available
#                 timestamp=seq[4],  # Timestamp as it is
#                 confidence=seq[1]  # Context-based ranking as confidence
#             )
#             sequences_to_save.append(suspicious_log_sequence)
#
#         # Persist the suspicious logs using the repository
#         self.suspicious_sequences_repo.save_sequences(sequences_to_save)
#         logger.info("Suspicious logs saved to the database.")
#
# # Usage
# # context_based_localizer = ContextBasedFaultLocalizer(db_session=db_session, train_file_path='path_to_training_file.txt')
# # context_based_localizer.localize_fault(test_batch_name="your_batch_name_here")
