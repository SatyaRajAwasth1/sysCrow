import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging
import asyncio

app = FastAPI()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

async def send_log(websocket: WebSocket):
    await websocket.accept()
    logger.info("websocket connection accepted")
    await websocket.send_text(line.strip())
    await asyncio.sleep(0.5)

@app.websocket("/modelstream")
async def model_stream(websocket: WebSocket):
    await send_log(websocket)
