# -*- coding: utf-8 -*-
import os

from chatcare.utils.params import Params
from chatcare.utils.logger import logger

# sys param for chat
params = Params(
    # api params
    host='0.0.0.0',
    port=8000,
    chat_mode='se',  # `se`：向量搜索 or `llm`：大模型 or `kb`：llm+知识库(待开发)
    url_db='./db',
    concurrency=10,

    # webui params
    webui_host='0.0.0.0',
    webui_port=8001,

    # embedings params
    bge_model_path='/workspace/models/bge-base-zh',

    # classification params
    num_class=2,
    embed_dim=768,
    classify_model_path='/workspace/models/embedding_classify.pt',

    # vector store: milvus
    milvus_host='127.0.0.1',
    milvus_port=19530,
    milvus_collection_name='care_qa',

    # llm params
    llm_model_name="chatglm2_6b",  # `baichuan7b` or `baichuan13b` or `qwen` or `chatglm2_6b`
    llm_checkpoint_dir="/workspace/models/chatglm2-6b-int4",
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
