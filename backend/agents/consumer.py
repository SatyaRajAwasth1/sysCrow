from confluent_kafka import Producer, Consumer, KafkaError
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import sys
import logging
import asyncio
import aiomysql
from os.path import dirname
from typing import Set, Dict
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from contextlib import asynccontextmanager

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

# producer config
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'parsed-log-producer'
}

producer = Producer(producer_config)

# callback function for the produce() method
def deliver_log(err, msg):
    if err:
        print(f"Error while publishing parsed log: {err}")
    else:
        print(f"Log message delivered to {msg.topic()} [{msg.partition}]")

class LogStreamingService:
    def __init__(self):
        self.app = FastAPI()
        self.active_connections: Set[WebSocket] = set()
        self.db_pool = None
        self.template_miner = self._setup_template_miner()
        self.consumer = self._setup_kafka_consumer()
        self.setup_routes()
        
    def _setup_template_miner(self) -> TemplateMiner:
        persistence_type = "FILE"
        if persistence_type == "FILE":
            from drain3.file_persistence import FilePersistence
            persistence = FilePersistence("drain3_state.bin")
        else:
            persistence = None
            
        config = TemplateMinerConfig()
        config.load(f"{dirname(__file__)}/drain3.ini")
        config.profiling_enabled = True
        return TemplateMiner(persistence, config)

    def _setup_kafka_consumer(self) -> Consumer:
        consumer_config = {
            'bootstrap.servers': 'localhost:9091',
            'group.id': 'log-consumer-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 5000,  # Commit every 5 seconds
            'max.poll.interval.ms': 300000,   # 5 minutes
            'session.timeout.ms': 30000       # 30 seconds
        }
        consumer = Consumer(consumer_config)
        consumer.subscribe(['logs_topic'])
        return consumer

    def setup_routes(self):
        @self.app.websocket("/logstream")
        async def log_stream(websocket: WebSocket):
            await self.handle_websocket_connection(websocket)

    async def init_db(self):
        """Initialize database connection pool"""
        if not self.db_pool:
            self.db_pool = await aiomysql.create_pool(
                host='localhost',
                user='root',
                password='root',
                db='sysCrow',
                autocommit=True,
                maxsize=20,  # Increased pool size
                minsize=5    # Minimum connections
            )

    async def store_in_db(self, parsed_log: Dict):
        """Store parsed log in database with connection pooling"""
        if not self.db_pool:
            await self.init_db()
            
        async with self.db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = "INSERT INTO logs_table (log_data) VALUES (%s)"
                await cursor.execute(query, (json.dumps(parsed_log),))

    def process_log(self, log_line: str) -> Dict:
        """Process log line using Drain3"""
        result = self.template_miner.add_log_message(log_line)

        # publish the parsed logs to kafka topic for consumption by model
        producer.produce("parsed_logs_topic", json.dumps(result), callback=deliver_log)
        producer.poll(0)

        if result["change_type"] != "none":
            result_json = json.dumps(result)
            logger.info(f"Input : {log_line}")
            logger.info(f"Result: {result_json}")
        return result

    async def handle_websocket_connection(self, websocket: WebSocket):
        """Handle individual WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        try:
            while True:
                # Keep connection alive and handle any incoming messages
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.active_connections.remove(websocket)

    async def broadcast_log(self, log_line: str):
        """Broadcast log to all connected WebSocket clients"""
        disconnected = set()
        for websocket in self.active_connections:
            try:
                await websocket.send_text(log_line.strip())
            except Exception:
                disconnected.add(websocket)
        
        # Clean up disconnected clients
        self.active_connections -= disconnected

    async def consume_logs(self):
        """Consume logs from Kafka with batching"""
        batch_size = 100
        batch_timeout = 1.0  # seconds
        
        while True:
            try:
                messages = []
                start_time = asyncio.get_event_loop().time()
                
                # Collect messages until batch size or timeout
                while len(messages) < batch_size and \
                      (asyncio.get_event_loop().time() - start_time) < batch_timeout:
                    
                    msg = self.consumer.poll(0.1)
                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            continue
                        logger.error(f"Kafka error: {msg.error()}")
                        continue
                        
                    messages.append(msg.value().decode('utf-8'))

                # Process batch
                if messages:
                    # Create tasks for processing and broadcasting
                    processing_tasks = []
                    for log_line in messages:
                        # Process log
                        parsed_log = self.process_log(log_line)
                        
                        # Create tasks for DB storage and WebSocket broadcast
                        processing_tasks.extend([
                            self.store_in_db(parsed_log),
                            self.broadcast_log(log_line)
                        ])
                    
                    # Wait for all processing tasks to complete
                    if processing_tasks:
                        await asyncio.gather(*processing_tasks)
                        
            except Exception as e:
                logger.error(f"Error in consume_logs: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on error

    async def startup(self):
        """Startup tasks"""
        await self.init_db()
        asyncio.create_task(self.consume_logs())

    def run(self):
        """Run the service"""
        import uvicorn
        
        @asynccontextmanager
        async def lifespan(app):
            await self.startup()
            yield
            # Cleanup
            if self.db_pool:
                self.db_pool.close()
                await self.db_pool.wait_closed()
            self.consumer.close()
            producer.flush()
        
        self.app.router.lifespan_context = lifespan
        uvicorn.run(self.app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    service = LogStreamingService()
    service.run()