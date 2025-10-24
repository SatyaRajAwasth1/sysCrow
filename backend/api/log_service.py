from backend.lbfl.src.persistence.log_details_repository import LogDetailsRepository


class LogService:
    def __init__(self):
        self.log_details_repo = LogDetailsRepository()

    def get_log_counts_for_each_4h(self):
        """Fetch log counts by category for the last 24 hours."""
        return self.log_details_repo.get_log_counts_by_4h()


