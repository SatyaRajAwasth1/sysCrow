# elastic_operations.py
from backend.lbfl.src.configs.config_reader import ConfigReader
from backend.lbfl.src.configs.elasticsearch_configs import ElasticConnection


class ElasticsearchRepository:
    def __init__(self):
        """
        Initializes repository with connection to an ElasticSearch instance
        """
        elastic_configs = ConfigReader().get_elastic_config()
        connection = ElasticConnection(elastic_configs.hosts, elastic_configs.username, elastic_configs.password)
        self.es = connection.get_connection()

    def save_entry(self, index_name, document):
        """
        Inserts a log document into Elasticsearch.
        Args:
            index_name (str): Name of the Elasticsearch index.
            log (dict): Log data to insert.
        Returns:
            dict: Response from Elasticsearch.
        """
        response = self.es.index(index=index_name, document=document)
        return response

    def query_index(self, index_name, query, size=100):
        """
        Fetches logs from Elasticsearch based on a query.
        Args:
            index_name (str): Name of the Elasticsearch index.
            query (dict): Elasticsearch query DSL.
            size (int): Number of logs to fetch.
        Returns:
            list: List of matching log documents.
        """
        response = self.es.search(index=index_name, query=query, size=size)
        return [hit["_source"] for hit in response["hits"]["hits"]]
