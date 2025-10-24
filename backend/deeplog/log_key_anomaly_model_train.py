import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import TensorDataset, DataLoader
import os
import time
import torch.optim as optim
import argparse

# device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

def generate(name, window_size):
    num_sessions = 0
    inputs = []
    outputs = []

    if not os.path.exists('data/' + name):
        print("path error")
        return

    with open('./data/' + name, 'r') as f:
        for line in f.readlines():
            num_sessions += 1
            line = tuple(map(lambda n: n - 1, map(int, line.strip().split())))

            # check if the number of elements is smaller than the window_size
            if len(line) < window_size:
                print("a line was skipped for having less no of elements than the window_size")
                continue

            for i in range(len(line) - window_size):
                inputs.append(line[i:i + window_size]) # sliding window input
                outputs.append(line[i + window_size]) # the immediate log following the window
    print('Number of sessions({}): {}'.format(name, num_sessions))
    print('Number of sequences({}): {}'.format(name, len(inputs)))
    dataset = TensorDataset(torch.tensor(inputs, dtype=torch.float), torch.tensor(outputs, dtype = torch.long))
    return dataset

#print(generate('hdfs_train', 3))

class Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_keys):
        super(Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        #LSTM Layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first = True)

        #fully connected(linear) layer mapping the hidden state to the desired output size
        self.fc = nn.Linear(hidden_size, num_keys)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device) # x.size(0) : batch size
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.lstm(x, (h0, c0)) # shape of out : (batch_size, sequence_length(window_size), hidden_size)
        out = self.fc(out[:, -1, :]) #  extract the hidden state at the last time step for each sequence in the batch.

# Why Use the Last Time Step?
# The hidden state at the last time step (out[:, -1, :]) summarizes the information from the entire sequence. This is because the LSTM processes the sequence step by step, updating its hidden state at each time step. By the last time step, the hidden state has "seen" the entire sequence and encodes its overall context.

        return out

if __name__ == '__main__':

    #hyperparameters:
    num_classes = 28
    num_epochs = 100
    batch_size = 2048
    input_size = 1
    model_dir = 'model'

    log = 'Adam_batch_size={}_epoch={}'.format(str(batch_size), str(num_epochs))
    parser = argparse.ArgumentParser()
    parser.add_argument('-num_layers', default = 2, type = int)
    parser.add_argument('-hidden_size', default = 64, type = int)
    parser.add_argument('-window_size', default = 10, type = int)
    args = parser.parse_args()
    
    num_layers = args.num_layers
    hidden_size = args.hidden_size
    window_size = args.window_size

    model = Model(input_size, hidden_size, num_layers, num_classes).to(device)
    seq_dataset = generate('hdfs_train', window_size)
    dataloader = DataLoader(seq_dataset, batch_size = batch_size, shuffle = True, pin_memory = True)
    writer = SummaryWriter(log_dir = 'log/' + log)
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())

    # Train the model
    start_time = time.time()
    total_step = len(dataloader)
    print('total steps: {}'.format(total_step))
    for epoch in range(num_epochs): # Loop over the dataset multiple times
        train_loss = 0
        for step, (seq, label) in enumerate(dataloader):
            # Forward pass
            seq = seq.clone().detach().view(-1, window_size, input_size).to(device)
            output = model(seq)
            loss = criterion(output, label.to(device))

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward() # compute gradients of the loss with respect to the model parameters using backpropagation
            train_loss += loss.item() # accumulate loss for the current batch
            optimizer.step() # update model parameters using the computed gradients

            writer.add_graph(model, seq)

        print('Epoch [{}/{}], train_loss: {:.4f}'.format(epoch + 1, num_epochs, train_loss / total_step))
        writer.add_scalar('train_loss', train_loss / total_step, epoch + 1)

    elapsed_time = time.time() - start_time
    print('elapsed_time: {:.3f}s'.format(elapsed_time))

    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)

    torch.save(model.state_dict(), model_dir + '/' + log + '.pt')
    writer.close()
    print('Finished training')


