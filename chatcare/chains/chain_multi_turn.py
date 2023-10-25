import uuid
from chatcare.embeddings.embedding_bge import bge
from chatcare.chains.intention_classify import classify
from chatcare.utils.chat_cache import MemCache
from chatcare.utils.logger import logger

from chatcare.chains.entity import query_entity
from chatcare.chains.entity import entity as all_entities
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
            context = None
            children = '，'.join(et['children'])
            msg = f"老年人的常见的{et['name']}有{children}等，颐小爱目前可以为您提供以上病种的护理信息支持，请问老人是哪种{et['name']}？"
            hints = []
            for c in et['children']:
                for z in all_entities:
                    if z['name'] == c:
                        synonym = ','.join(z['synonym'][:1])
                        x = f'{c}（{synonym}）'
                        hints.append(x)
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
            no_treatment = False
            for e in ee:
                if not e['children'] and e['type'] == '疾病名称':
                    no_treatment = True
            for e in context['entities']:
                if e['type'] in types:
                    continue
                if no_treatment and e['type'] == '治疗方式':
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
        logger.info(f'{got_entities = }')
        got_slots = {g['type']: g for g in got_entities}
        slots = intentions[intent_id]['slots']
        logger.info(f'got entities: {got_entities}, slots: {slots}')
        lack = []
        no_treatment = False
        for e in slots:
            if e in got_slots:
                if e == '疾病名称' and not got_slots[e]['children']:
                    no_treatment = True
                continue
            if e == '治疗方式' and no_treatment:
                continue
            lack.append(e)
        logger.info(f'{lack = }')
        if not lack:
            msg = 'ok'
        else:
            if not (has_disease_type and len(got_entities) == 0):
                if lack[0] == '疾病名称':
                    msg = '请问老人患有哪种疾病？'
                else:
                    msg = '请问老人采用哪种形式的治疗？'
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
    logger.info(f'{context = }')
    entities = query_entity(query)
    logger.info(f'recgonition: {entities = }')
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
            'summary': '对不起，你的问题超出我的知识范围了，我可以回答关于专病种护理、健康、康复等相关问题。如果您有与专科疾病护理相关的问题或需要特定建议，随时向我提问。',
            'intent_id': intent_id,
            'hints': [],
            'details': [],
        }
    # ask for identity
    if intent_id == 3:
        return {
            'summary': '我是颐家的护理AI助手，专注于提供专科疾病领域的家庭护理信息和支持。我可以回答关于专病种护理、健康、康复等相关问题。如果您有与专科疾病护理相关的问题或需要特定建议，随时向我提问。',
            'intent_id': intent_id,
            'hints': [],
            'details': [],
        }
    # ask for basecare
    if intent_id == 4:
        return {
            'summary': '我目前专注于提供专科疾病领域的家庭护理知识，你可以尝试问我疾病护理相关的问题，如，老人骨折了如何照护？',
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
