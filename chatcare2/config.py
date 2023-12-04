# -*- coding: utf-8 -*-
import os
from chatcare2.utils.params import Params
from chatcare2.utils.logger import logger

# sys param for chat
params = Params(
    # api params
    host='0.0.0.0',
    port=8000,
    concurrency=10,
    root_path='',

    # webui params
    webui_host='0.0.0.0',
    webui_port=8001,

    # embedings params
    bge_model_path='/workspace/models/bge-base-zh-v1.5_onnx',

    # classification params
    embed_dim=768,
    # cf1
    num_class=26,
    classify_model_path='/workspace/models/embedding_classify.pt',
    # cf2
    num_class_intention=5,
    classify_intention_path='/workspace/models/intention_classify.pt',
    intention_inf_json = '/workspace/knowledge_base/qa/intention.json',

    # dev params
    debug=True,

    # mysql
    db_host='127.0.0.1',
    db_port='3306',
    db_name='chatcare',
    db_user='ailab',
    db_pass='TheAIdb0',

    # GPT
    gpt_tokens=50,
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
    params.port = int(os.getenv("PORT", params.port))
    params.debug = bool(os.getenv("DEBUG", params.debug))
    params.root_path = os.getenv("ROOT_PATH", params.root_path)
    params.db_host = os.getenv('DB_HOST', params.db_host)
    params.db_port = int(os.getenv('DB_PORT', params.db_port))
    params.db_name = os.getenv('DB_NAME', params.db_name)
    params.db_user = os.getenv('DB_USER', params.db_user)
    params.db_pass = os.getenv('DB_PASS', params.db_pass)
    params.gpt_tokens = int(os.getenv('GPT_TOKENS', params.gpt_tokens))


update_params_from_env()

if params.debug:
    logger.info(f"Params of ChatCare: {params}")
