from chatcare.embeddings.embedding_bge import bge
import chatcare.config 
from chatcare.chains.embedding_classify import classify
from chatcare.chains.kb_search import kb_search


def chain(query):
    '''
    query -> classify -> search -> answer
    '''
    embedding = bge.encode_queries([query])
    label = classify(embedding)
    if label == 0:
        return '超出我的知识范围，请询问护理相关的问题'
    results = kb_search(embedding)
    # for i, result in enumerate(results):
    #     print("\nSearch result for {}th vector: ".format(i))
    #     for j, res in enumerate(result):
    #         print("Top {}: {}".format(j, res))
    entity = results[0][0].entity
    answer = entity.get('answer')
    return answer


if __name__ == "__main__":
    query = '肺炎的护理内容是什么'
    answer = chain(query)
    print(f'{query = }')
    print(f'{answer = }')
