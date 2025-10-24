from confluent_kafka import Producer
import re
import time

# Kafka Configuration
KAFKA_BROKERS = "localhost:9091,localhost:9092,localhost:9093"
KAFKA_TOPIC = "raw_logs"
LOG_FILE_PATH = "/data/training_dataset.log"

# Kafka Producer Configuration
producer_config = {
    "bootstrap.servers": KAFKA_BROKERS,
    "client.id": "log-producer"
}

# Initialize Kafka Producer
producer = Producer(producer_config)

def delivery_report(err, msg):
    """ Callback for message delivery success/failure. """
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_logs():
    """ Read log file, process multi-line log entries, and publish to Kafka """
    print("🚀 Starting Kafka log producer...")

    # Regex to detect the start of a new log entry (timestamp pattern)
    timestamp_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.\d{3}")

    log_entry = []  # To store multi-line log entries

    with open(LOG_FILE_PATH, "r", encoding="utf-8") as log_file:
        for line in log_file:
            if timestamp_pattern.match(line):  # New log entry starts
                if log_entry:  # Process previous log entry
                    send_to_kafka("".join(log_entry))
                log_entry = [line]  # Start a new log entry
            else:
                log_entry.append(line)  # Append to the current log entry

        # Send the last log entry if any
        if log_entry:
            send_to_kafka("".join(log_entry))

    print("✅ Finished publishing log entries.")

def send_to_kafka(log_entry):
    """ Send log entry to Kafka """
    log_entry = log_entry.strip()
    if log_entry:
        producer.produce(KAFKA_TOPIC, key=None, value=log_entry, callback=delivery_report)
        producer.flush()  # Ensure message is sent
        time.sleep(0.1)  # Simulate real-time streaming

if __name__ == "__main__":
    produce_logs()
