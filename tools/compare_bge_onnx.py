#!/usr/bin/env python3

from fastembed.embedding import EmbeddingModel
from pathlib import Path
from FlagEmbedding import FlagModel
import time
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

device = 'cpu'

# model_path = '/aidata/weiliang/huggingface/bge-large-zh'
model_path = '/aidata/huggingface/bge-base-zh'
# model_path = '/aidata/weiliang/huggingface/bge-small-zh'
b = time.time()
model_bge = FlagModel(
    model_path,
    query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
    use_fp16=False
)
model_bge.device = torch.device('cpu')
model_bge.model.to(model_bge.device)
e = time.time()
print('bge model loading time:', e - b)

b = time.time()
model_path = Path('/aidata/weiliang/projects/chatcare/train/bge-base-zh-v1.5_onnx')
model_path = Path('/aidata/weiliang/projects/chatcare/train/bge-small-zh-v1.5_onnx_O4')
model_path = Path('/aidata/weiliang/projects/chatcare/train/bge-small-zh-v1.5_onnx')
model_onnx = EmbeddingModel(model_path, model_name='bge')
print('onnx model loading time:', time.time() - b)

sentences = [
    '那是個快樂的人',
    '那是个快乐的人',
    '那是条快乐的狗',
    '他是个幸福的人',
    '今天天气不错啊',
    '今天天气不错',
    '长护险',
    '长期护理保险',
]
p = '为这个句子生成表示以用于检索相关文章：'
sentences = [p+s for s in sentences]

sentences_warmup = [
    '世界上的那是個快樂的人',
    '世界上的那是个快乐的人',
    '世界上的那是条快乐的狗',
    '世界上的他是个幸福的人',
    '世界上的今天天气不错啊',
    '世界上的今天天气不错',
    '世界上的长护险',
    '世界上的长期护理保险',
]

for i in range(5):
    embeddings_bge = model_bge.encode_queries(sentences_warmup)
    embeddings_onnx = model_onnx.onnx_embed(sentences_warmup)
    print(f'warm up {i}')


times_bge = []
times_onnx = []
for i in range(10):
    b = time.time()
    embeddings_bge = model_bge.encode_queries(sentences)
    e = time.time()
    print('bge batch encoding time:', e - b, embeddings_bge.shape)
    times_bge.append(e-b)
    # sentences_onnx = sentences
    b = time.time()
    embeddings_onnx = model_onnx.onnx_embed(sentences)
    e = time.time()
    print('onnx batch encoding time:', e - b, embeddings_onnx.shape)
    times_onnx.append(e-b)
    print('=='*10)
avg_bge = sum(times_bge) / len(times_bge)
avg_onnx = sum(times_onnx) / len(times_onnx)
print(f'{avg_bge = }, {avg_onnx = }, speed up: {avg_bge / avg_onnx}')
#
for i in range(len(sentences)):
    sim_bge = embeddings_bge[i] @ embeddings_bge[0].T
    sim_onnx = embeddings_onnx[i] @ embeddings_onnx[0].T
    print(f'{sentences[i]} vs {sentences[0]}, {sim_bge = }, {sim_onnx = }')

print('\n\n')

