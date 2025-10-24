from fastapi import FASTAPI, WebSocket
import asyncio

app = FastAPI()

LOG_FILE_PATH = "log/hdfs_abnormal"

async def tail_log(websocket: WebSocket):
    await websocket.accept()
    with open(LOG_FILE_PATH, "r") as file:
        file.seek(0, SEEK_END) # Move to the end of the file
        while True:
            line = file.readline()
            if line:
                await websocket.send_text(line.strip())
            await asyncio.sleep(0.5)

@app.websocket("/logstream")
async def log_stream(websocket: WebSocket):
    await tail_log(websocket)
