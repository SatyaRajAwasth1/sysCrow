# class LogEntry:
#     def __init__(self, timestamp, thread, level, correlation_id, logger_name, template_id, properties=None):
#         """
#         Represents a single log entry.
#         Args:
#             timestamp (str): Timestamp of the log.
#             thread (str): Thread name.
#             level (str): Log level (e.g., INFO, ERROR).
#             correlation_id (str): Request identifier or correlation ID.
#             logger_name (str): Name of the logger.
#             template_id (str): Template ID. extracted after processed by Drain3
#             properties (list): Properties that are masked by Drain3; extracted from the log.
#         """
#         self.timestamp = timestamp
#         self.thread = thread
#         self.level = level
#         self.correlation_id = correlation_id
#         self.logger_name = logger_name
#         self.template_id = template_id
#         self.properties = properties or []
#
#     def __str__(self):
#         return f"[{self.timestamp}] [{self.thread}] {self.level} [{self.correlation_id}] {self.logger_name} - {self.template_id} - {self.properties}"
#
#     def to_dict(self):
#         """Convert LogEntry to a dictionary for Elasticsearch indexing."""
#         return {
#             "timestamp": self.timestamp,
#             "thread": self.thread,
#             "level": self.level,
#             "correlation_id": self.correlation_id,
#             "logger_name": self.logger_name,
#             "template_id": self.template_id,
#             "properties": self.properties,
#         }

from sqlalchemy import Column, String, Integer, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LogDetails(Base):
    __tablename__ = 'log_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(255), nullable=False)
    thread = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False)
    correlation_id = Column(String(255), nullable=False)
    logger_name = Column(String(255), nullable=False)
    template_id = Column(String(255), nullable=False)
    properties = Column(String(255), nullable=True)

    def __init__(self, timestamp, thread, level, correlation_id, logger_name, template_id, properties=None):
        """
        Represents a single log entry.
        Args:
            timestamp (str): Timestamp of the log.
            thread (str): Thread name.
            level (str): Log level (e.g., INFO, ERROR).
            correlation_id (str): Request identifier or correlation ID.
            logger_name (str): Name of the logger.
            template_id (int): Template ID. extracted after processed by Drain3.
            properties (list(str)): Properties that are masked by Drain3; extracted from the log.
        """
        self.timestamp = timestamp
        self.thread = thread
        self.level = level
        self.correlation_id = correlation_id
        self.logger_name = logger_name
        self.template_id = template_id
        self.properties = properties

    def __str__(self):
        return f"[{self.timestamp}] [{self.thread}] {self.level} [{self.correlation_id}] {self.logger_name} - {self.template_id} - {self.properties}"

    def to_dict(self):
        """Convert LogEntry to a dictionary for MySQL persistence."""
        return {
            "timestamp": self.timestamp,
            "thread": self.thread,
            "level": self.level,
            "correlation_id": self.correlation_id,
            "logger_name": self.logger_name,
            "template_id": self.template_id,
            "properties": self.properties,
        }


class LogTemplate(Base):
    __tablename__ = 'log_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String(255), unique=True, nullable=False)
    template_text = Column(Text, nullable=False)

    def __repr__(self):
        return f"<LogTemplate(template_id={self.template_id}, template_text={self.template_text})>"

    def to_dict(self):
        """Convert LogTemplate to a dictionary."""
        return {
            "template_id": self.template_id,
            "template_text": self.template_text,
        }


class UnsupervisedSegmentedSequence(Base):
    __tablename__ = 'unsupervised_segmented_sequences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_sequence = Column(String(1000), nullable=True)
    event_sequence = Column(String(1000), nullable=True)
    correlation_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=True)  # This should use SQLAlchemy's DateTime
    batch = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<UnsupervisedSegmentedSequences(id={self.id}, correlation_id={self.correlation_id})>"


class SuspiciousLogSequence(Base):
    __tablename__ = 'suspicious_log_sequences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_sequence = Column(String(1000), nullable=True)
    event_sequence = Column(String(1000), nullable=True)
    correlation_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, nullable=True)
    confidence = Column(Float, nullable=True)
    batch = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<LogSequence(id={self.id}, correlation_id={self.correlation_id}, confidence={self.confidence}, batch={self.batch})>"
