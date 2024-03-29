# -*- coding: utf-8 -*-
import os
from chatcare.utils.params import Params
from chatcare.utils.logger import logger

# sys param for chat
params = Params(
    # api params
    host='0.0.0.0',
    port=8000,
    chat_mode='kb',  # `vs`：QA向量搜索 or `llm`：大模型 or `kb`：基于知识库多模态对话
    vector_db='hnsw',  # 选择向量搜索数据库 `milvus` or `hnsw`
    concurrency=10,
    root_path='',

    # webui params
    webui_host='0.0.0.0',
    webui_port=8001,

    # embedings params
    bge_model_path='/workspace/models/bge-base-zh',

    # classification params
    embed_dim=768,
    # cf1
    num_class=26,
    classify_model_path='/workspace/models/embedding_classify.pt',
    # cf2
    num_class_intention=5,
    classify_intention_path='/workspace/models/intention_classify.pt',
    intention_inf_json = '/workspace/knowledge_base/qa/intention.json',

    # vector store: hnsw
    hnsw_kb_init_jsonl="/workspace/knowledge_base/qa/example_v1.2.2.jsonl",  # 初始化db的问答对
    hnsw_kb_index_file="/workspace/knowledge_base/db/kb_index.bin",
    hnsw_kb_text_file="/workspace/knowledge_base/db/kb_text.bin",

    # vector store: milvus
    milvus_host='127.0.0.1',
    milvus_port=19530,
    milvus_collection_name='care_qa',

    # llm params
    llm_model_name="chatglm2_6b",  # `baichuan7b` or `baichuan13b` or `qwen` or `chatglm2_6b`
    llm_checkpoint_dir="/workspace/models/chatglm2-6b-int4",
    device='cuda',  # `cpu` or 'cuda'

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
    params.chat_mode = os.getenv("CHAT_MODE", params.chat_mode)
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
