import os
import json
import jieba
from jieba import analyse
import pandas as pd

# TODO: entity.json gen from db
df_entity = pd.read_json('entity.json')


def gen_jieba_userdict(dict_file: str):
    """
    生成 jieba userdict

    Args:
         dict_file:

    Returns:

    """
    entity_list = df_entity['name'].tolist()
    for synonym in df_entity['synonym']:
        entity_list += synonym
    for idx, item in enumerate(entity_list):
        item = item.replace('\n', '') + '\n'
        entity_list[idx] = item
    entity_list = sorted(list(set(entity_list)))
    with open(dict_file, 'w', encoding='utf-8') as f:
        f.writelines(entity_list)


def search_entity(word: str, df_entity: pd.DataFrame) -> int:
    """
    查寻

    Args:
        word:
        words_list:
    Return:
        idx (int): df_entity index
    """
    for idx, df_item in df_entity.iterrows():
        name = df_item['name']
        synonyms = df_item['synonym']
        if word in name:
            return idx
        for word_synonym in synonyms:
            if word in word_synonym:
                return idx
    return -1


def query_entity(query: str) -> list:
    """
    查询 entity
    Args:
        query:
    Return:
        entities (List(Dict)): 实体列表
    """
    if not os.path.exists('entity_dict.txt'):
        gen_jieba_userdict('entity_dict.txt')
    jieba.load_userdict('entity_dict.txt')
    tags_list = jieba.analyse.extract_tags(query, topK=5)
    entity_ids = []
    for tag in tags_list:
        search_id = search_entity(tag, df_entity)
        if search_id > -1:
            entity_ids.append(search_id)
    entities = json.dumps(df_entity.loc[entity_ids].to_dict('records'), ensure_ascii=False, indent=4)
    return entities


if __name__ == '__main__':
    query = '老年痴呆了怎么办？'
    entities = query_entity(query)
    print(entities)
