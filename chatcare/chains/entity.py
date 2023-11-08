import json
import jieba


def _init_entity():
    json_file = '/workspace/knowledge_base/qa/entity.json'
    # 1. load entity
    entity = json.load(open(json_file, 'r', encoding='utf-8'))
    entity_searcher = {}
    for item in entity:
        entity_searcher[item['name']] = item
        for synonym in item['synonym']:
            entity_searcher[synonym] = item

    # 2. gen jiea userdict
    jieba_dict_list = []
    for item in entity:
        jieba_dict_list.append(item['name'])
        jieba_dict_list.extend(item['synonym'])
    jieba_dict_list = sorted(list(set(jieba_dict_list)))
    freq = 1000
    for word in jieba_dict_list:
        jieba.add_word(word, freq)
    return entity, entity_searcher


entity, entity_searcher = _init_entity()


def query_entity(query: str) -> list:
    """
    查询 entity
    Args:
        query:
    Return:
        entities (List(Dict)): 实体列表
    """
    global entity_searcher
    seg_list = jieba.cut(query, cut_all=False)
    entities = []
    for seg in seg_list:
        entity = entity_searcher.get(seg)
        if entity is None:
            continue
        entities.append(entity)
    entities = [eval(entity) for entity in set([str(entity) for entity in entities])]
    return entities


if __name__ == '__main__':
    from pprint import pprint
    queries = [
        '手腕骨折过，做了石膏固定，怎么护理？',
        '骨折如何护理',
        '如何进行血糖监测',
    ]
    for query in queries:
        entities = query_entity(query)
        print(f'{query = }')
        pprint(entities)
        print('====='*10)
