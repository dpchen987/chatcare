#!/usr/bin/env python3

import sys
sys.path.insert(0, '..')
import time
import os
import torch.onnx
import onnx
import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
# PyTorch TensorBoard support
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
import onnxruntime as rt
from chatcare.utils.classification_model import EmbeddingClassification
import numpy as np
torch.manual_seed(1258)
msize = 'base'
zzz = {
    'small': 512,
    'base': 768,
    'large': 1024
}
embed_dim = zzz[msize]
num_class = 5


class EmbeddingDataset(Dataset):
    def __init__(self, embeds, labels):
        self.embeds = torch.tensor(embeds)
        self.labels = torch.tensor(labels, dtype=torch.int64)
        self.len = len(labels)

    def __len__(self):
        return self.len

    def __getitem__(self, idx):
        embed = self.embeds[idx]
        label = self.labels[idx]
        return embed, label


def load_embedding(train_data_path):
    import os
    import pickle
    embed_path = train_data_path + '.pkl'
    # if os.path.exists(embed_path):
    if os.path.exists(embed_path):
        os.remove(embed_path)
        # with open(embed_path, 'rb') as f:
        #     dd = pickle.load(f)
        # return dd['embeds'], dd['labels']
    labels = []
    texts = []
    with open(train_data_path, 'r') as f:
        for l in f:
            zz = l.strip().split(' ', 1)
            print(zz)
            assert len(zz) == 2
            labels.append(int(zz[0]))
            texts.append(zz[1])
    from chatcare2.embeddings.embedding_bge import bge
    embeds = bge.onnx_embed(texts)
    with open(embed_path, 'wb') as f:
        pickle.dump({'embeds': embeds, 'labels': labels}, f)
    return embeds, labels


def train(train_data_path, test_data_path):
    embeds, labels = load_embedding(train_data_path)
    print(labels)
    print(f'======= {embeds.shape = }, {len(labels) = }')
    vembeds, vlabels = load_embedding(test_data_path)
    print(f'------- {vembeds.shape = }, {len(vlabels) = }')
    train_data = EmbeddingDataset(embeds, labels)
    trainloader = DataLoader(train_data, batch_size=8, shuffle=True)
    val_data = EmbeddingDataset(vembeds, vlabels)
    validationloader = DataLoader(val_data, batch_size=2, shuffle=False)

    assert embed_dim == embeds.shape[-1]
    print("len(set(labels)", len(set(labels)))
    assert num_class == len(set(labels))
    print(f'-- {embed_dim = }, {num_class = } ===================')
    assert num_class == 5
    lr = 0.0001
    momentum = 0.9
    model = EmbeddingClassification(embed_dim, num_class)
    loss_fn = torch.nn.CrossEntropyLoss()
    # optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)


    def train_one_epoch(epoch_index, tb_writer):
        running_loss = 0
        last_loss = 0
        steps = 2

        for i, data in enumerate(trainloader):
            # print('============= one i:', i, data)
            inputs, labels = data
            # print(f'\t{inputs.shape = }, {labels.shape = }')
            # print(f'\t{inputs = }, {labels = }')
            inputs = inputs.to(torch.float32)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            if i % steps == steps - 1:
                last_loss = running_loss / steps
                # print(f' batch {i+1} loss: {last_loss}')
                tb_x = epoch_index * len(trainloader) + i + 1
                tb_writer.add_scalar('Loss/train', last_loss, tb_x)
                running_loss = 0
        return last_loss
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    writer = SummaryWriter(f'runs/trainer_{timestamp}')
    epochs = 200
    best_vloss = 10000
    for epoch_number in range(epochs):
        print(f'Epoch {epoch_number + 1}')
        model.train(True)
        avg_loss = train_one_epoch(epoch_number, writer)
        running_vloss = 0.0
        model.eval()
        with torch.no_grad():
            for i, vdata in enumerate(validationloader):
                vinputs, vlabels = vdata
                vinputs = vinputs.to(torch.float32)
                voutputs = model(vinputs)
                vloss = loss_fn(voutputs, vlabels)
                running_vloss += vloss
        avg_vloss = running_vloss / (i + 1)
        print(f'LOSS train {avg_loss} valid {avg_vloss}')
        writer.add_scalars('Training vs. Validation Loss',
                           {'Training': avg_loss, 'Validation': avg_vloss},
                           epoch_number + 1)
        writer.flush()
        if avg_vloss < best_vloss:
            best_vloss = avg_vloss
        if epoch_number % 180 == 0:
            model_path = f'model_{timestamp}_{epoch_number}'
            torch.save(model.state_dict(), model_path)


def infer(model_path):
    tests = []
    with open('./z-test.txt') as f:
        for l in f:
            zz = l.strip().split(' ', 1)
            assert len(zz) == 2
            tests.append((int(zz[0]), zz[1]))

    def infer_fn(text):
        embed = bge.onnx_embed([text])
        embed = torch.tensor(embed)
        embed = embed.to(torch.float32)
        # print(embed)
        with torch.no_grad():
            ilabel = model(embed)
        return ilabel

    model = EmbeddingClassification(embed_dim, num_class)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    from chatcare2.embeddings.embedding_bge import bge
    good = 0
    for t in tests:
        label = t[0]
        text = t[1]
        ilabel = infer_fn(text)
        # print(ilabel)
        ilabel = int(ilabel.argmax(dim=1)[0])
        if label != ilabel:
            print(f'{label = } != {ilabel = }', text)
        else:
            good += 1
    accuracy = round(good / len(tests), 2)
    print('Accuracy:', accuracy)
    while True:
        text = input('>')
        ilabel = infer_fn(text)
        print(ilabel)

def infer_onnx(model_path):
    tests = []
    model = rt.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    with open('./z-test.txt') as f:
        for l in f:
            zz = l.strip().split(' ', 1)
            assert len(zz) == 2
            tests.append((int(zz[0]), zz[1]))

    def infer_fn(text):
        embed = bge.onnx_embed([text])
        # print(type(embed))
        # embed = torch.tensor(embed)
        # embed = embed.to(torch.float32)
        # print(embed)
        ilabel = classify(embed)
        return ilabel

    def classify(embed):
        '''
        attention: input is embedding of text
        '''
        array = embed
        input_name = model.get_inputs()[0].name
        ilabel = model.run(None, {input_name: array})[0]
        # print(type(ilabel), ilabel)
        ilabel = int(np.argmax(ilabel, axis=1)[0])
        return str(ilabel)
    from chatcare2.embeddings.embedding_bge import bge
    good = 0
    for t in tests:
        label = t[0]
        text = t[1]
        ilabel = infer_fn(text)
        # print(f"{ilabel=}")
        ilabel = int(ilabel)
        if label != ilabel:
            print(f'{label = } != {ilabel = }', text)
        else:
            good += 1
    accuracy = round(good / len(tests), 2)
    print('Accuracy:', accuracy)
    while True:
        text = input('>')
        ilabel = infer_fn(text)
        print(ilabel)

def convert(model_name):
    model = EmbeddingClassification(embed_dim, num_class)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    dummy_input = torch.randn(1, embed_dim, requires_grad=True)
    onnx_name = f'{model_name}.onnx'

    # Export the model
    torch.onnx.export(
        model,  # model being run
        dummy_input,  # model input (or a tuple for multiple inputs)
        onnx_name,  # where to save the model
        export_params=True,  # store the trained parameter weights inside the model file
        opset_version=11,  # the ONNX version to export the model to
        do_constant_folding=True,  # whether to execute constant folding for optimization
        input_names = ['modelInput'],  # the model's input names
        output_names = ['label'], # the model's output names
        dynamic_axes={
            'modelInput' : {0: 'batch_size'},    # variable length axes
            # 'tag': {0: 'batch_size'},
            # 'time': {0: 'batch_size', 1: 'times'},
        },
    )
    print(" ")
    print('Model has been converted to ONNX')
    onnxmodel = onnx.load(onnx_name)
    onnx.checker.check_model(onnxmodel)
    # print(onnx.helper.printable_graph(onnxmodel.graph))
    print('check_model done')



if __name__ == "__main__":
    from sys import argv
    opt = argv[1]
    if opt == 'train':
        train_data_path = argv[2]
        test_data_path = argv[3]
        train(train_data_path, test_data_path)
    elif opt == 'infer':
        model_path = argv[2]
        infer(model_path)
    elif opt == 'onnx':
        model_path = argv[2]
        convert(model_path)
    elif opt == 'infer_onnx':
        model_path = argv[2]
        infer_onnx(model_path)
    else:
        print('invalid opt:', opt)
