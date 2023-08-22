# -*- coding: utf-8 -*-
import os

from chatcare.utils.params import Params
from chatcare.utils.logger import logger

# sys param for chat
params = Params(
    # api params
    host='0.0.0.0',
    port=8000,
    chat_mode='llms',  # `llms`：大模型 or `embedings`：向量搜索
    url_db='./db',
    concurrency=10,

    # embedings params

    # llm params
    llm_model_name="chatglm2_6b",  # `baichuan7b` or `baichuan13b` or `qwen` or `chatglm2_6b`
    llm_checkpoint_dir="/aidata/junjie/data/model/modelscope/chatglm2-6b-int4",
    device="cuda",  # `cpu` or 'cuda'

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
    params.port = os.getenv("PORT", params.port)
    params.chat_mode = os.getenv("CHAT_MODE", params.chat_mode)
    params.debug = os.getenv("DEBUG", params.debug)


update_params_from_env()

if params.debug:
    logger.info(f"Params of ChatCare: {params}")
