from chatcare.embeddings.embedding_bge import bge
from chatcare.chains.embedding_classify import classify
from chatcare.utils.chat_cache import MemCache

from .intention import intentions

CHAT_CACHE = MemCache()


def chain(query, chat_id):
    '''
    query -> classify -> entity recgonition -> search -> answer
    '''
    context = CHAT_CACHE.get(chat_id)

    embedding = bge.encode_queries([query])
    label = classify(embedding)
    if label == 0:
        return '超出我的知识范围，请询问护理相关的问题'

    return 'TODO'


if __name__ == "__main__":
    query = '老年痴呆/阿尔茨海默的老人怎么照护？'
    answer = chain(query)
    print(f'{query = }')
    print(f'{answer = }')
