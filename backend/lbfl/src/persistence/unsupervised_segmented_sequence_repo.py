from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.lbfl.src.configs.config_reader import ConfigReader
from src.persistence.models import UnsupervisedSegmentedSequence

class UnsupervisedSegmentedSequencesRepository:
    def __init__(self):
        mysql_configs = ConfigReader().get_mysql_configs()

        connection_url = f"mysql+mysqlconnector://{mysql_configs['url']}"

        engine = create_engine(connection_url)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def save_sequences(self, sequences):
        """Persist a list of unsupervised segmented sequences to MySQL."""
        try:
            for sequence in sequences:
                self.session.add(sequence)
            self.session.commit()
            print(f"{len(sequences)} sequences saved.")
        except Exception as e:
            self.session.rollback()
            print(f"Error saving sequences: {e}")
        finally:
            self.session.close()

    def get_sequences_by_batch(self, batch, limit=100, offset=0):
        """Fetch unsupervised segmented sequences by batch."""
        try:
            sequences = (self.session.query(UnsupervisedSegmentedSequence)
                         .filter(UnsupervisedSegmentedSequence.batch == batch).limit(limit).offset(offset).all())
            return sequences
        except Exception as e:
            print(f"Error fetching sequences: {e}")
            return []
        finally:
            self.session.close()

    def get_sequence_by_id(self, sequence_id):
        """Fetch a specific unsupervised segmented sequence by ID."""
        try:
            sequence = (self.session.query(UnsupervisedSegmentedSequence)
                        .filter(UnsupervisedSegmentedSequence.id == sequence_id).first())
            return sequence
        except Exception as e:
            print(f"Error fetching sequence by ID: {e}")
            return None
        finally:
            self.session.close()
