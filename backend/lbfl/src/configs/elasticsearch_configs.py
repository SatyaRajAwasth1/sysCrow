from elasticsearch import Elasticsearch


class ElasticConnection:
    def __init__(self, hosts, username=None, password=None, verify_certs=False):
        """
        Initializes the Elasticsearch connection.
        Args:
            hosts (list): List of Elasticsearch hosts.
            username (str): Username for authentication (if required).
            password (str): Password for authentication (if required).
            verify_certs (bool): Whether to verify SSL certificates.
        """
        self.es = Elasticsearch(
            hosts=hosts,
            http_auth=(username, password) if username and password else None,
            verify_certs=verify_certs
        )

    def get_connection(self):
        """
        Returns the Elasticsearch connection instance.
        """
        return self.es
