from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.lbfl.src.configs.config_reader import ConfigReader
from backend.lbfl.src.persistence.models import SuspiciousLogSequence


class SuspiciousLogSequencesRepository:
    def __init__(self):
        mysql_configs = ConfigReader().get_mysql_configs()

        connection_url = f"mysql+mysqlconnector://{mysql_configs['url']}"

        engine = create_engine(connection_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def save_logs(self, logs):
        """Persist a list of suspicious logs to MySQL."""
        try:
            for log in logs:
                self.session.add(log)
            self.session.commit()
            print(f"{len(logs)} logs saved.")
        except Exception as e:
            self.session.rollback()
            print(f"Error saving logs: {e}")
        finally:
            self.session.close()

    def get_logs(self, limit=100):
        """Fetch suspicious logs from MySQL."""
        try:
            logs = self.session.query(SuspiciousLogSequence).limit(limit).all()
            return logs
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
        finally:
            self.session.close()

    def get_log_by_id(self, log_id):
        """Fetch a suspicious log by ID."""
        try:
            log = self.session.query(SuspiciousLogSequence).filter(SuspiciousLogSequence.id == log_id).first()
            return log
        except Exception as e:
            print(f"Error fetching log by ID: {e}")
            return None
        finally:
            self.session.close()

    def save_sequences(self, sequences:list[SuspiciousLogSequence]):
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
            sequences = (self.session.query(SuspiciousLogSequence)
                         .filter(SuspiciousLogSequence.batch == batch).limit(limit).offset(offset).all())
            return sequences
        except Exception as e:
            print(f"Error fetching sequences: {e}")
            return []
        finally:
            self.session.close()
