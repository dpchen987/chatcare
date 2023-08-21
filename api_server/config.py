# -*- coding: utf-8 -*-
import os

from utils.params import Params
from utils.logger import logger

# sys param for chat
params = Params(
    # api params
    host='0.0.0.0',
    port=8000,
    chat_mode='llm',  # `llm`：大模型 or `embedings`：向量搜索
    url_db='./db',
    concurrency=10,

    # embedings params

    # llm params
    llm_model_name="baichuan13b",  # `baichuan7b` or `baichuan13b` or `qwen` or `tinystory`
    llm_checkpoint_dir="/aidata/junjie/data/model/llms/baichuan13b/baichuan-13b-chat-int4.flm",
    device="cpu",  # `cpu` or 'cuda'

    # dev params
    debug=True,

)


def update_params_from_env():
    """
    read configs in sys env used for docker
    Args:
        ...
    Return:
         ...
    """
    global params
    params.host = os.getenv('HOST', params.host)


update_params_from_env()
logger.info(f"{params=}")
