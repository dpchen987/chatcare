#!/usr/bin/env python3

from fastembed.embedding import EmbeddingModel
from pathlib import Path
from chatcare2.config import params


def get_bge():
    model_path = Path(params.bge_model_path)
    bge_onnx = EmbeddingModel(model_path, model_name='bge')
    return bge_onnx


'''
form this import bge
use bge.onnx_embed([text]) for getting embedding
'''
bge = get_bge()
