#!/usr/bin/env python3

from FlagEmbedding import FlagModel
from chatcare.config import params


def get_bge(msize):
    assert msize in ['large', 'base', 'small']
    model_path = params.bge_model_path
    bge = FlagModel(
        model_path,
        query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
        use_fp16=False,
    )
    return bge


'''
form this import bge
use bge.encode_queries(text) for better classification
'''
bge = get_bge('base')
