import uuid
from chatcare.embeddings.embedding_bge import bge
from chatcare.chains.intention_classify import classify
from chatcare.utils.chat_cache import MemCache
from chatcare.utils.logger import logger

from chatcare.chains.entity import query_entity
from chatcare.chains.intention import intentions
from chatcare.chains.kb_search_mysql import search_mysql

CHAT_CACHE = MemCache()


def process_entity(entities, context):
    msg, hints, slots = '', [], []
    intent_entities = {}  # {intent_id: [entity,]}
    has_disease_type = False
    for et in entities:
        tmp = []
        if et['type'] == '疾病类别':
            msg = f'请问老人的{et["name"]}，具体是以下哪种？'
            hints = et['children']
            intent_entities[1] = []
            has_disease_type = True
            continue
        if et['type'] in ['疾病名称', '治疗方式']:
            intent_id = 1  # 查询疾病护理方案
        elif et['type'] == '操作名称':
            intent_id = 2
        else:
            logger.warn(f'invalid entity type: {et["type"]}')
            continue
        if et['type'] == '疾病名称':
            hints = et['children']
        tmp.append(et)
        if intent_id in intent_entities:
            intent_entities[intent_id].extend(tmp)
        else:
            intent_entities[intent_id] = tmp
    # context processing 
    if context:
        for iid, ee in intent_entities.items():
            if iid != context['intent_id']:
                continue
            types = [e['type'] for e in ee]
            for e in context['entities']:
                if e['type'] in types:
                    continue
                ee.append(e)
        
    # intents process 
    intent_id = 0
    got_entities = []
    if not intent_entities:
        logger.warn(f'no invalid entity from {entities}')
        msg = '我不是很理解您的提问，请再详细说一下您的问题'
    else:
        intents = list(intent_entities.keys())
        intents.sort()
        intent_id = intents[0]
        got_entities = intent_entities[intent_id]
        print(f'{got_entities = }')
        got_slots = [g['type'] for g in got_entities]
        slots = intentions[intent_id]['slots']
        logger.info(f'got entities: {got_entities}, slots: {slots}')
        lack = [e for e in slots if e not in got_slots]
        print(f'{lack = }')
        if not lack:
            msg = 'ok'
        else:
            if not (has_disease_type and len(got_entities) == 0):
                if lack[0] == '疾病名称':
                    msg = '请问老人患有哪种疾病？'
                else:
                    msg = f'请问老人的{lack[0]} 是怎样的？'
    return msg, hints, intent_id, got_entities 


def chain(query, chat_id):
    '''
    query -> classify -> entity recgonition -> search -> answer
    1. 实体识别
        1. 如果实体类型是'疾病类别', 则返回该类别所有的疾病名称；
        2. 如果实体是'疾病名称、治疗方式', 则看上下文还缺哪些实体
            1. 如果不缺则进行知识查询
            2. 如果缺这返回，提示要补充的实体
        3. 如果实体是'护理操作', 则查询该操作相关的知识
    2. 如果没有实体
        1. 判断意图
            1. 如果无关，则返回话术
            2. 针对该意图，让用户补充实体

    '''
    context = CHAT_CACHE.get(chat_id)
    print(f'{context = }')
    entities = query_entity(query)
    print(f'{entities = }')
    if entities:
        msg, hints, intent_id, intent_entities = process_entity(entities, context)
        if intent_entities:
            CHAT_CACHE.save(chat_id, intent_id, intent_entities)
        if msg != 'ok':
            return {
                'summary': msg,
                'intent_id': intent_id,
                'hints': hints,
                'details': []
            }
        # slots is full, to get answer
        msg, details = search_mysql(intent_id, intent_entities)
        result = {
            'summary': msg,
            'intent_id': intent_id,
            'hints': [],
            'details': details,
        }
        return result
    # no entities
    embedding = bge.encode_queries([query])
    intent_id = classify(embedding)
    if intent_id == 0:
        return {
            'summary': '超出我的知识范围，请询问居家护理相关的问题',
            'intent_id': intent_id,
            'hints': [],
            'details': [],
        }
    # ask for identity
    if intent_id == 3:
        return {
            'summary': '我是颐小爱护理AI，专注于提供专科疾病领域的家庭护理信息和支持。我可以回答关于护理、健康、康复等相关问题。有什么关于家庭护理方面的问题我可以帮助您解答吗？',
            'intent_id': intent_id,
            'hints': [],
            'details': [],
        }
    # right intent but no entities
    if intent_id == 1:
        msg = '请问老人患的是哪种病？'
    elif intent_id == 2:
        msg = '请问您要查询的护理操作的名称是什么'
    return {
        'summary': msg,
        'intent_id': intent_id,
        'hints': [],
        'details': []
    }


if __name__ == "__main__":
    from pprint import pprint
    query = '骨折如何照护'
    while 1:
        answer, chat_id = chain(query, chat_id='abc')
        print(f'{chat_id = }')
        pprint(f'{answer = }')
        query = input('>')
