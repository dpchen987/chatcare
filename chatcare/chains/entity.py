import json
import jieba


def _init_entity(json_file='entity.json'):
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
    with open('entity_dict.txt', 'w', encoding='utf-8') as f:
        jieba_dict_list = [word + '\n' for word in jieba_dict_list]
        f.writelines(jieba_dict_list)
    jieba.load_userdict('entity_dict.txt')

    return entity, entity_searcher


entity, entity_searcher = _init_entity()


def search_entity(word: str, entity_searcher: dict) -> dict:
    """
    查寻

    Args:
        word:
        entity_searcher:
    Return:
        entity (dict): entity or None
    """
    for search_word in entity_searcher:
        if word == search_word:
            return entity_searcher[search_word]


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
        entity = search_entity(seg, entity_searcher)
        entities.append(entity) if entity else None
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
