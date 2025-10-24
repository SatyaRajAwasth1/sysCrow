from confluent_kafka import Producer
import time

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': 'localhost:9091',  # Adjust as per your broker
    'client.id': 'log-producer'
}

producer = Producer(producer_config)

# callback function for the produce() method
def deliver_log(err, msg):
    if err:
        print(f"Error while publishing message: {err}")
    else:
        print(f"Log message delivered to {msg.topic()} [{msg.partition}]")

# Read log file and send to Kafka
def read_and_publish_logs(file_path, topic):
    with open(file_path, 'r') as log_file:
        for line in log_file:
            print(f"Sending log: {line.strip()}")
            producer.produce(topic, line.strip(), callback=deliver_log)
            producer.poll(0)
            time.sleep(0.1)  # Adding a small delay to simulate log streaming
        producer.flush()

if __name__ == "__main__":
    # Define the log file and Kafka topic
    log_file_path = 'C:/Users/prsyd/Downloads/HDFS_v1/HDFS.log'
    kafka_topic = 'logs_topic'
    
    read_and_publish_logs(log_file_path, kafka_topic)
