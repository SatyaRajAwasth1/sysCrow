import torch
import torch.nn as nn
import time
import argparse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging
import asyncio

# device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

app = FastAPI()

#Create an async log handler to send logs through the websocket
class WebSocketLogHandler(logging.Handler):
    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket

    async def emit(self, record):
        log_entry = self.format(record)
        await self.websocket.send_text(log_entry)

def generate(name, window_size, websocket):
    hdfs = []
    with open('data/' + name, 'r') as f:
        for ln in f.readlines():
            ln = list( map( lambda n: n - 1, map( int, ln.strip().split())))

            # pad the line with -1 if length of line is smaller than window_size
            ln = ln + [-1] * ( window_size + 1 - len(ln))

            hdfs.append(tuple(ln))
    log_msg = f'Number of sessions({name}): {len(hdfs)}'
    print(log_msg)
    websocket.send_text(log_msg)
    return hdfs

#generate('hdfs_train', 3)

class Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_keys):
        super(Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first = True)
        self.fc = nn.Linear(hidden_size, num_keys)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :]) # shape of out : (batch_size, sequence_length(window_size), hidden_size)
        return out
    
@app.websocket("/modelstream")
async def model_stream(websocket: WebSocket):
    await websocket.accept()

    websocket_handler = WebSocketLogHandler(websocket)
    logging.basicConfig(level=logging.INFO, handlers=[websocket_handler])

    logging.info("WebSocket connection established")

    await run_model(websocket)
    
    await websocket.close()



    
async def run_model(websocket: WebSocket):

    # hyperparameters
    num_classes = 28
    input_size = 1
    model_path = 'model/Adam_batch_size=2048_epoch=300.pt'

    # parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-num_layers', default=2, type=int)
    parser.add_argument('-hidden_size', default=64, type=int)
    parser.add_argument('-window_size', default=10, type=int)
    parser.add_argument('-num_candidates', default=9, type=int)
    args = parser.parse_args()

    num_layers = args.num_layers
    hidden_size = args.hidden_size
    window_size = args.window_size
    num_candidates = args.num_candidates

    model = Model(input_size, hidden_size, num_layers, num_classes).to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    logging.info(f'Model loaded from: {model_path}')
    
    # test_normal_loader = generate('hdfs_test_normal', window_size)
    test_abnormal_loader = generate('abnormal_subset', window_size, websocket)
    TP = 0
    FP = 0

    # test the model
    start_time = time.time()

    # with torch.no_grad():
    #     for line in test_normal_loader:
    #         print("starting evaluation for the normal sequence dataset: \n")
    #         for i in range(len(line) - window_size):
    #             seq = line[i: i + window_size]
    #             label = line[i + window_size]
    #             seq = torch.tensor(seq, dtype=torch.float).view(-1, window_size, input_size).to(device)
    #             label = torch.tensor(label).view(-1).to(device)
    #             output = model(seq) # shape of out : (batch_size, sequence_length(window_size), hidden_size)
    #             print('model evalled: {} \n'.format(seq, label))
    #             predicted = torch.argsort(output, 1)[0][-num_candidates:]
    #             if label not in predicted:
    #                 FP += 1
    #                 break

    with torch.no_grad():
        print("starting evaluation for the abnormal sequence dataset: \n")
        # print("number of sessions:{}".format(len(test_abnormal_loader)))
        j = 0
        for line in test_abnormal_loader:
            print("line number:{}".format(j))
            j = j + 1
            for i in range(len(line) - window_size):
                seq = line[i : i + window_size]
                label = line[i + window_size]
                seq = torch.tensor(seq, dtype=torch.float).view(-1, window_size, input_size).to(device)
                label = torch.tensor(label).view(-1).to(device)
                output = model(seq)
                #print('model evalled: {} \n'.format(seq, label))
                predicted = torch.argsort(output, 1)[0][-num_candidates:]
                if label not in predicted:
                    logging.info(f"Anomaly detected: {seq}, {label}")
                    TP += 1
                    break
    
    elapsed_time = time.time() - start_time
    logging.info(f'Elapsed time: {elapsed_time:.3f}s')

    # compute precision, recall and F1-measure
    FN = len(test_abnormal_loader) - TP
    P = 100 * TP / (TP + FP)
    R = 100 * TP / (TP + FN)
    F1 = 2 * P * R / (P + R)
    logging.info(f'FP: {FP}, FN: {FN}, Precision: {P:.3f}%, Recall: {R:.3f}%, F1: {F1:.3f}%')
    logging.info('Finished Predicting')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)