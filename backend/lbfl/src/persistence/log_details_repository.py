from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, text
from datetime import datetime, timedelta

from backend.lbfl.src.configs.config_reader import ConfigReader
from backend.lbfl.src.persistence.models import LogDetails


class LogDetailsRepository:
    def __init__(self):
        mysql_configs = ConfigReader().get_mysql_configs()

        connection_url = f"mysql+mysqlconnector://{mysql_configs['url']}"

        engine = create_engine(connection_url)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def save_log_entry(self, log_entry):
        """Persist a log entry to MySQL."""
        try:
            self.session.add(log_entry)
            self.session.commit()
            print(f"Log entry saved: {log_entry}")
        except Exception as e:
            self.session.rollback()
            print(f"Error saving log entry: {e}")
        finally:
            self.session.close()

    def get_log_entries(self, limit=100):
        """Fetch log entries from MySQL."""
        try:
            log_entries = self.session.query(LogDetails).limit(limit).all()
            return log_entries
        except Exception as e:
            print(f"Error fetching log entries: {e}")
            return []
        finally:
            self.session.close()

    def get_log_entry_by_id(self, log_id):
        """Fetch a log entry by ID from MySQL."""
        try:
            log_entry = self.session.query(LogDetails).filter(LogDetails.id == log_id).first()
            return log_entry
        except Exception as e:
            print(f"Error fetching log entry by ID: {e}")
            return None
        finally:
            self.session.close()

    def get_log_counts_for_templates(self, template_ids):
        """Get total success counts, fail counts, and total counts for specified templates."""
        try:
            # Ensure the template_ids parameter is a list and not empty
            if not template_ids:
                print("No template IDs provided.")
                return []

            # Query to filter by the provided list of template IDs and group by template_id
            result = self.session.query(
                LogDetails.template_id,
                func.sum(func.case([(LogDetails.level == 'INFO', 1)], else_=0)).label('success_count'),
                func.sum(func.case([(LogDetails.level == 'ERROR', 1)], else_=0)).label('fail_count')
            ).filter(LogDetails.template_id.in_(template_ids))  # Filter by the list of template_ids
            result = result.group_by(LogDetails.template_id).all()

            # Return results as a list of dictionaries
            log_counts = []
            for row in result:
                log_counts.append({
                    "template_id": row.template_id,
                    "success_count": row.success_count,
                    "fail_count": row.fail_count
                })

            return log_counts
        except Exception as e:
            print(f"Error fetching log counts by template: {e}")
            return []
        finally:
            self.session.close()

    def get_total_success_fail_counts(self):
        """Get total success and fail counts across all log entries."""
        try:
            # Query to count successes (INFO) and failures (ERROR) globally
            result = self.session.query(
                func.sum(func.case([(LogDetails.level == 'INFO', 1)], else_=0)).label('success_count'),
                func.sum(func.case([(LogDetails.level == 'ERROR', 1)], else_=0)).label('fail_count')
            ).first()

            # If the query returns None, handle the case
            success_count = result.success_count if result.success_count is not None else 0
            fail_count = result.fail_count if result.fail_count is not None else 0

            return {
                "success_count": success_count,
                "fail_count": fail_count
            }

        except Exception as e:
            print(f"Error fetching total success and fail counts: {e}")
            return {"success_count": 0, "fail_count": 0}
        finally:
            self.session.close()


    def get_log_counts_by_4h(self):
        """Fetch log counts for each log level for every 4-hour period."""
        try:
            sql = text("""
                SELECT 
                    DATE_FORMAT(timestamp, '%H:00') AS time,
                    SUM(CASE WHEN level = 'INFO' THEN 1 ELSE 0 END) AS INFORMATIVE,
                    SUM(CASE WHEN level = 'WARN' THEN 1 ELSE 0 END) AS WARNING,
                    SUM(CASE WHEN level = 'ERROR' THEN 1 ELSE 0 END) AS ERROR,
                    SUM(CASE WHEN level = 'CRITICAL' THEN 1 ELSE 0 END) AS CRITICAL,
                    SUM(CASE WHEN level = 'DEBUG' THEN 1 ELSE 0 END) AS DEBUG,
                    SUM(CASE WHEN level = 'UNKNOWN' THEN 1 ELSE 0 END) AS UNKNOWN
                FROM log_details
                WHERE timestamp >= '2024-05-13 00:00:00' - INTERVAL 24 HOUR
                GROUP BY time
                ORDER BY time;
            """)

            result = self.session.execute(sql).fetchall()

            return [
                {
                    "time": row[0],
                    "INFORMATIVE": row[1] or 0,
                    "WARNING": row[2] or 0,
                    "ERROR": row[3] or 0,
                    "CRITICAL": row[4] or 0,
                    "DEBUG": row[5] or 0,
                    "UNKNOWN": row[6] or 0
                }
                for row in result
            ]

        except Exception as e:
            print(f"Error fetching log counts by 4-hour intervals: {e}")
            return []

        finally:
            self.session.close()


