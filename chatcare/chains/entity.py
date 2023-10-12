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


def search_entity(word: str, entity_searcher: dict) -> list:
    """
    查寻

    Args:
        word:
        entity_searcher:
    Return:
        idx (int): df_entity index
    """
    entities = []
    for search_word in entity_searcher:
        if word == search_word:
            entities.append(entity_searcher[search_word])
    return entities


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
        entities.extend(search_entity(seg, entity_searcher))
    entities = [eval(entity) for entity in set([str(entity) for entity in entities])]
    return entities


if __name__ == '__main__':
    query = '骨折了怎么办？'
    entities = query_entity(query)
    print(entities)
