import torch
import torch.nn as nn
import time
import argparse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging
import asyncio
from typing import List

# device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = FastAPI()

class WebSocketLogHandler(logging.Handler):
    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket
        self.formatter = logging.Formatter('%(message)s')

    async def emit(self, record):
        try:
            log_entry = self.formatter.format(record)
            await self.websocket.send_text(log_entry)
        except Exception:
            self.handleError(record)

async def generate(name: str, window_size: int, websocket: WebSocket) -> List[tuple]:
    hdfs = []
    try:
        with open(f'data/{name}', 'r') as f:
            for ln in f.readlines():
                # Convert string to list of integers and subtract 1 from each
                ln = [int(x) - 1 for x in ln.strip().split()]
                
                # Pad the line with -1 if length is smaller than window_size + 1
                ln.extend([-1] * (window_size + 1 - len(ln)))
                
                hdfs.append(tuple(ln))
        
        log_msg = f'Number of sessions({name}): {len(hdfs)}'
        await websocket.send_text(log_msg)
        return hdfs
    except FileNotFoundError:
        await websocket.send_text(f"Error: Could not find file data/{name}")
        return []
    except Exception as e:
        await websocket.send_text(f"Error processing file: {str(e)}")
        return []

class Model(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, num_keys: int):
        super(Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_keys)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

async def run_model(websocket: WebSocket):
    try:
        # Hyperparameters
        num_classes = 28
        input_size = 1
        model_path = 'model/Adam_batch_size=2048_epoch=300.pt'
        
        # Default arguments since we can't use argparse with FastAPI
        num_layers = 2
        hidden_size = 64
        window_size = 10
        num_candidates = 9

        # Initialize and load model
        model = Model(input_size, hidden_size, num_layers, num_classes).to(device)
        try:
            model.load_state_dict(torch.load(model_path))
            await websocket.send_text(f'Model loaded from: {model_path}')
        except Exception as e:
            await websocket.send_text(f"Error loading model: {str(e)}")
            return

        model.eval()
        
        # Generate test data
        test_abnormal_loader = await generate('abnormal_subset', window_size, websocket)
        if not test_abnormal_loader:
            return
            
        TP = 0
        FP = 0
        
        start_time = time.time()
        
        with torch.no_grad():
            await websocket.send_text("Starting evaluation for the abnormal sequence dataset")
            for j, line in enumerate(test_abnormal_loader):
                await websocket.send_text(f"Processing line number: {j}")
                
                for i in range(len(line) - window_size):
                    seq = line[i: i + window_size]
                    label = line[i + window_size]
                    
                    seq = torch.tensor(seq, dtype=torch.float).view(-1, window_size, input_size).to(device)
                    label = torch.tensor(label).view(-1).to(device)
                    
                    output = model(seq)
                    predicted = torch.argsort(output, 1)[0][-num_candidates:]
                    
                    if label not in predicted:
                        await websocket.send_text(f"Anomaly detected in sequence {j}")
                        TP += 1
                        break

        elapsed_time = time.time() - start_time
        await websocket.send_text(f'Elapsed time: {elapsed_time:.3f}s')

        # Compute metrics
        FN = len(test_abnormal_loader) - TP
        P = 100 * TP / (TP + FP) if (TP + FP) > 0 else 0
        R = 100 * TP / (TP + FN) if (TP + FN) > 0 else 0
        F1 = 2 * P * R / (P + R) if (P + R) > 0 else 0
        
        await websocket.send_text(
            f'Results:\nFP: {FP}, FN: {FN}\n'
            f'Precision: {P:.3f}%\nRecall: {R:.3f}%\nF1: {F1:.3f}%'
        )
        
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
    except Exception as e:
        await websocket.send_text(f"Error during model execution: {str(e)}")

@app.websocket("/modelstream")
async def model_stream(websocket: WebSocket):
    await websocket.accept()
    
    # Set up logging
    handler = WebSocketLogHandler(websocket)
    logger = logging.getLogger('modelstream')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    try:
        await run_model(websocket)
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        logger.removeHandler(handler)
        await websocket.close()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)