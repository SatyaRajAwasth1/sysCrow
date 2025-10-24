from confluent_kafka import Consumer, KafkaError
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import sys
import logging
from os.path import dirname

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

persistence_type = "FILE"

app = FastAPI()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

if persistence_type == "FILE":
    from drain3.file_persistence import FilePersistence

    persistence = FilePersistence("drain3_state.bin")
else:
    persistence = None

config = TemplateMinerConfig()
config.load(f"{dirname(__file__)}/drain3.ini")
config.profiling_enabled = False

template_miner = TemplateMiner(persistence, config)
print(f"Drain3 started with '{persistence_type}' persistence")
print(f"{len(config.masking_instructions)} masking instructions are in use")
print(f"Starting training mode. Reading from kafka-topic ('q' to finish)")


# Kafka consumer configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9091',  # Adjust as per your broker
    'group.id': 'log-consumer-group',
    'auto.offset.reset': 'earliest'  # Start from the earliest message
}

consumer = Consumer(consumer_config)

def process_log(log_line):
    # Apply Drain3 log parsing
    result = template_miner.add_log_message(log_line)
    if result["change_type"] != "none":
        result_json = json.dumps(result)
        logger.info(f"Input : {log_line}")
        logger.info(f"Result: {result_json}")
    return result

websocket_connected = False
current_websocket = None

# Kafka consumer callback
async def consume_logs():
    consumer.subscribe(['logs_topic'])  # Adjust topic name as per your Kafka setup
    try:
        while True:
            if current_websocket == None:
                await log_stream()
            msg = consumer.poll(0.3)  # Poll for new messages every 1 second
            if msg   is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
            else:
                log_line = msg.value().decode('utf-8')
                parsed_log = process_log(log_line)
                print(f"Processed log: {json.dumps(parsed_log)}")
                store_in_db(parsed_log)  # Send processed log to the database

                if websocket_connected:
                    await current_websocket.send_text(log_line.strip())                
    except WebSocketDisconnect:
        logger.info("Websocket connection closed")
        websocket_connected = False
        current_websocket = None
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        websocket_connected = False
        current_websocket = None
        logger.info("WebSocket connection has been closed.")

# Function to store extracted log data in MySQL (or any other database)
def store_in_db(parsed_log):
    import mysql.connector
    
    # Connect to the MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Your database username
        password='root',  # Your database password
        database='sysCrow'
    )
    cursor = connection.cursor()

    # Example of inserting parsed log data into the database
    query = "INSERT INTO logs_table (log_data) VALUES (%s)"
    cursor.execute(query, (json.dumps(parsed_log),))
    connection.commit()

    cursor.close()
    connection.close()

@app.websocket("/logstream")
async def log_stream(websocket: WebSocket):
    global websocket_connected
    global current_websocket

    await websocket.accept()
    logger.info("Websocket connection accepted")

    websocket_connected = True
    current_websocket = websocket


if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    consume_logs()
    sorted_clusters = sorted(template_miner.drain.clusters, key=lambda it: it.size, reverse=True)
    for cluster in sorted_clusters:
        logger.info(cluster)
    print("Prefix Tree:")
    template_miner.drain.print_tree()