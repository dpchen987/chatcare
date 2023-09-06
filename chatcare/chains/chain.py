import json
import os

from chatcare.embeddings.embedding_bge import bge
from chatcare.config import params
from chatcare.chains.embedding_classify import classify
from chatcare.chains.kb_search_milvus import kb_search
from chatcare.chains.kb_search_hnsw import KnowledgeBaseService
from chatcare.utils.logger import logger

# init kbs_hnsw obj
if params.vector_db == "hnsw":
    kbs_hnsw = KnowledgeBaseService(
        kb_index_file=params.hnsw_kb_index_file,
        kb_text_file=params.hnsw_kb_text_file,
        dim=params.embed_dim,
    )


def chain(query):
    '''
    query -> classify -> search -> answer
    '''
    global kbs_hnsw
    embedding = bge.encode_queries([query])
    label = classify(embedding)
    if label == 0:
        return '超出我的知识范围，请询问护理相关的问题'

    # QA with milvus
    if params.vector_db == "milvus":
        results = kb_search(embedding)
        # for i, result in enumerate(results):
        #     print("\nSearch result for {}th vector: ".format(i))
        #     for j, res in enumerate(result):
        #         print("Top {}: {}".format(j, res))
        entity = results[0][0].entity
        answer = entity.get('answer')
        logger.info(f"QA with milvus successfully!")

    # QA with hnsw
    else:
        # 初始化插入向量
        if (not (os.path.exists(params.hnsw_kb_index_file) and os.path.exists(
                params.hnsw_kb_text_file))) and os.path.exists(params.hnsw_kb_init_jsonl):
            logger.info(f"Init hnsw successfully! || Init kb data: {params.hnsw_kb_init_jsonl}")
            data_init = [json.loads(line) for line in open(params.hnsw_kb_init_jsonl)]
            data_init_question = [item['question'] for item in data_init]
            embedding_init = bge.encode_queries(data_init_question)
            kbs_hnsw.insert_kb(embedding_init, data_init)
        result = kbs_hnsw.query_kb(embedding, k=1)
        answer = result["text"][0][0]["answer"]
        logger.info(f"QA with hnsw successfully!")
    return answer


if __name__ == "__main__":
    query = '肺炎的护理内容是什么'
    answer = chain(query)
    print(f'{query = }')
    print(f'{answer = }')
