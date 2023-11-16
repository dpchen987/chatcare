import uuid
import copy
from chatcare.embeddings.embedding_bge import bge
from chatcare.chains.intention_classify import classify
from chatcare.utils.chat_cache import MemCache
from chatcare.utils.logger import logger

from chatcare.chains.entity import query_entity
from chatcare.chains.entity import entity as all_entities
from chatcare.chains.intention import intentions
from chatcare.chains.kb_search_mysql import search_mysql
from chatcare.config import params

CHAT_CACHE = MemCache()


def process_entity(entities, context):
    msg, hints, slots = '', [], []
    et_disease_type = None
    et_disease = None
    et_treatment = None
    intent_id = '1'
    for et in entities:
        if et['type'] == '疾病类别':
            et_disease_type = copy.deepcopy(et)
            continue
        if et['type'] == '疾病名称':
            et_disease = copy.deepcopy(et)
            continue
        if et['type'] == '治疗方式':
            et_treatment = copy.deepcopy(et)
            continue
    # context processing 
    if et_disease:
        et_disease_type = None
    if et_disease_type and not et_disease:
        et = et_disease_type
        children = '，'.join(et['children'])
        msg = f"老年人的常见的{et['name']}有{children}等，颐小爱目前可以为您提供以上病种的护理信息支持，请问老人是哪种{et['name']}？"
        hints = []
        for c in et['children']:
            for z in all_entities:
                if z['name'] == c:
                    synonym = ','.join(z['synonym'][:1])
                    x = f'{c}（{synonym}）'
                    hints.append(x)
        return msg, hints, intent_id, [et] 
    if context:
        for e in context['entities']:
            if e['type'] == '疾病类别' and not et_disease_type:
                et_disease_type = copy.deepcopy(e)
                continue
            if e['type'] == '疾病名称' and not et_disease:
                et_disease = copy.deepcopy(e)
                continue
            if e['type'] == '治疗方式' and not et_treatment:
                et_treatment = copy.deepcopy(e)
                continue
    logger.info(f'{context = }, {et_disease = }, {et_treatment = }')
    if not et_disease_type and not et_disease and not et_treatment:
        intent_id = '0'
        msg = '我不是很理解您的提问，请再详细说一下您的问题'
        return msg, hints, intent_id, [] 
    if et_disease:
        got = []
        got.append(et_disease)
        if not et_disease['children']:
            msg = 'ok'
        else:
            if not et_treatment:
                msg = '请问老人采用哪种形式的治疗？'
            else:
                disease_name = et_disease['name']
                if disease_name not in et_treatment['relation']:
                    logger.warn(f'disease not match treatment, {et_disease = }, {et_treatment = }')
                    msg = '请问老人采用哪种形式的治疗？'
                    hints = et_disease['children']
                    return msg, hints, intent_id, [et_disease]
                et_treatment['name'] = et_treatment['relation'][disease_name]
                msg = 'ok'
                got.append(et_treatment)
        hints = et_disease['children']
        return msg, hints, intent_id, got
    else:
        got = []
        if et_treatment:
            got.append(et_treatment)
        msg = '请问老人患有哪种疾病？'
        return msg, hints, intent_id, got
    # somethins else
    logger.info('something else')
    return msg, hints, intent_id, []


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
    if query == '新话题':
        CHAT_CACHE.save(chat_id, 0, [])
        return {
            'summary': '好的，我们开始新话题吧',
            'intent_id': 0,
            'hints': [],
            'details': []
        }
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
    # clear memory, start new topic
    CHAT_CACHE.save(chat_id, 0, [])

    # return intent id & script
    if intent_id in intentions:
        summary = intentions[intent_id]["intent_script"]
    else:
        summary = intentions['0']['intent_script']
    return {
        'summary': summary,
        'intent_id': intent_id,
        'hints': [],
        'details': [],
    }


if __name__ == "__main__":
    from pprint import pprint
    query = '骨折如何照护'
    while 1:
        answer, chat_id = chain(query, chat_id='abc')
        print(f'{chat_id = }')
        pprint(f'{answer = }')
        query = input('>')
