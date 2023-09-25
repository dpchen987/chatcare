import json
import os
from chatcare.embeddings.embedding_bge import bge
from chatcare.config import params
from chatcare.chains.embedding_classify import classify
from chatcare.chains.kb_search_milvus import kb_search
from chatcare.chains.kb_search_hnsw import KnowledgeBaseService
from chatcare.utils.logger import logger

# kb方式问答知识库标签
KB_LABEL_LIST = [
    "无关",
    "股骨颈骨折的非手术治疗",
    "股骨颈骨折的内固定术式",
    "股骨颈骨折后髋关节置换",
    "腰椎间盘突出非手术治疗",
    "腰椎间盘突出微创手术治疗",
    "腰椎间盘突出开放性手术治疗",
    "桡骨远端骨折非手术治疗",
    "桡骨远端骨折手术治疗",
    "肱骨近端骨折非手术治疗",
    "肱骨近端骨折切开复位钢板内固定",
    "肱骨近端骨折髓内钉固定",
    "人工肩关节置换",
    "认知障碍症",
    "帕金森",
    "脑卒中",
    "支架介入",
    "冠脉搭桥",
    "清洁类护理",
    "皮肤护理",
    "饮食用药护理",
    "排泄护理",
    "移动",
    "热敷",
    "冷敷",
    "老年人基础照护"
]


def _init_kbs_hnsw():
    """init kbs_hnsw obj"""
    kbs_hnsw = KnowledgeBaseService(
        kb_index_file=params.hnsw_kb_index_file,
        kb_text_file=params.hnsw_kb_text_file,
        dim=params.embed_dim,
    )
    if (not (os.path.exists(params.hnsw_kb_index_file) and os.path.exists(
            params.hnsw_kb_text_file))) and os.path.exists(params.hnsw_kb_init_jsonl):
        data_init = [json.loads(line) for line in open(params.hnsw_kb_init_jsonl)]
        data_init_question = [item['question'] for item in data_init]
        embedding_init = bge.encode_queries(data_init_question)
        kbs_hnsw.insert_kb(embedding_init, data_init)
        logger.info(f"Init hnsw successfully! || Init kb data: {params.hnsw_kb_init_jsonl}")

    return kbs_hnsw


if params.vector_db == "hnsw":
    kbs_hnsw = _init_kbs_hnsw()


def search_kbs_hnsw_from_label(label, kbs_hnsw: KnowledgeBaseService):
    """基于question名称直接搜问题"""
    kb_text = kbs_hnsw.kb_text
    for item_idx in kb_text:
        if label == kb_text[item_idx]['question']:
            return kb_text[item_idx]['answer']
    return "知识库中未找到该问题！"


def chain(query):
    '''
    query -> classify -> search -> answer
    '''
    global kbs_hnsw
    embedding = bge.encode_queries([query])
    label = classify(embedding)
    logger.info(f'{query = }, label = {KB_LABEL_LIST[label]}')
    if label == 0:
        return '超出我的知识范围，请询问护理相关的问题'

    # kb_text search
    if params.chat_mode == "kb":
        return search_kbs_hnsw_from_label(KB_LABEL_LIST[label], kbs_hnsw)

    # embedding search
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
        result = kbs_hnsw.query_kb(embedding, k=1)
        answer = result["text"][0][0]["answer"]
        logger.info(f"QA with hnsw successfully!")
    return answer


if __name__ == "__main__":
    query = '老年痴呆/阿尔茨海默的老人怎么照护？'
    answer = chain(query)
    print(f'{query = }')
    print(f'{answer = }')
