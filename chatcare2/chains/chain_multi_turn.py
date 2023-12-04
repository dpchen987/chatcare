import time
import copy
import zhipuai

from chatcare2.embeddings.embedding_bge import bge
from chatcare2.chains.intention_classify import classify
from chatcare2.utils.chat_cache import MemCache, MemCacheList
from chatcare2.utils.logger import logger

from chatcare2.chains.entity import query_entity
from chatcare2.chains.entity import entity as all_entities
from chatcare2.chains.intention import intentions
from chatcare2.chains.kb_search_mysql import search_mysql
from chatcare2.config import params
from .async_sse import sse_async

CHAT_CACHE = MemCache()
CACHE_LIST = MemCacheList()

# company
zhipuai.api_key = '880dcc0db4f8226d9ba785c74e377441.ldIxRW21PM6xxmDg'
# zhipuai.api_key = '6574a4c99fa996c861b982bf256844c1.eDRvyeGFkczH8boH'


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
                    msg = f'disease not match treatment, {et_disease = }, {et_treatment = }'
                    logger.warn(msg)
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


def gen_prompt(query):
    prompt = f"假设你是一名资深的居家护理师，具有丰富的康养和护理知识，请结合你的专业知识用{params.gpt_tokens}个字以内回答问题：{query}"
    logger.info(prompt)
    return prompt


async def gpt_async(query):
    prompt = gen_prompt(query)
    gpt_params = dict(
        api_key=zhipuai.api_key,
        model="chatglm_turbo",
        prompt=[{"role": "user", "content": prompt}],
        top_p=0.7,
        temperature=0.9,
    )
    async for event in sse_async(**gpt_params):
        print(time.time(), event['data'])
        yield event


async def gpt_sse(query):
    prompt = gen_prompt(query)
    response = zhipuai.model_api.sse_invoke(
        model="chatglm_turbo",
        prompt=[{"role": "user", "content": prompt}],
        top_p=0.7,
        temperature=0.9,
    )
    for e in response.events():
        event = {
            'id': e.id,
            'data': e.data,
            'event': e.event,
            'comment': e.meta,
        }
        yield event


async def gpt(chat_id, query):
    prompt = gen_prompt(query)
    history = CACHE_LIST.get(chat_id)
    history.append({"role": "user", "content": prompt})
    logger.info(history)
    response = zhipuai.model_api.invoke(
        model="chatglm_turbo",
        prompt=history,
        top_p=0.7,
        temperature=0.9,
    )
    if response['code'] == 200:
        message = response['data']['choices'][0]
        content = message['content'].replace('\\n', '\n').replace('\\"', '"').strip('\\" ')
        message['content'] = content
        CACHE_LIST.save(chat_id, message)
        logger.info(response['data']['usage'])
    else:
        content = response['msg']
    return content


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
        CHAT_CACHE.remove(chat_id)
        CACHE_LIST.remove(chat_id)
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
    embedding = bge.onnx_embed([query])
    intent_id = classify(embedding)
    # clear memory, start new topic
    CHAT_CACHE.save(chat_id, 0, [])

    # return intent id & script
    print(f'xxxxxxxxx{ intent_id = }', type(intent_id))
    if intent_id == '3':
        summary = intentions[intent_id]["intent_script"]
    else:
        intent_id = '0'
        summary = 'answered by GPT'
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
