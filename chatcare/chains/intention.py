import json
from chatcare.utils.logger import logger
from chatcare.config import params

# key: label of classification
# value: intention meta
# intentions = {
#     0: {
#         'intent': '无关',
#         'slots': [],
#         'intent_script': "对不起，你的问题超出我的知识范围了，我可以回答关于专病种护理、健康、康复等相关问题。如果您有与专科疾病护理相关的问题或需要特定建议，随时向我提问。"
#     },
#     1: {
#         'intent': '查询疾病护理方案',
#         'slots': ['疾病名称', '治疗方式'],
#         'intent_script': "请问老人患的是哪种病？"
#     },
#     2: {
#         'intent': '查询护理操作',
#         'slots': ['操作名称'],
#         'intent_script': "请问您要查询的护理操作的名称是什么？"
#     },
#     3: {
#         'intent': '自我介绍',
#         'slots': [],
#         'intent_script': "我是颐家的护理AI助手，专注于提供专科疾病领域的家庭护理信息和支持。我可以回答关于专病种护理、健康、康复等相关问题。如果您有与专科疾病护理相关的问题或需要特定建议，随时向我提问。"
#     },
#     4: {
#         'intent': '基础照护类问题',
#         'slots': [],
#         'intent_script': "我目前专注于提供专科疾病领域的家庭护理知识，你可以尝试问我疾病护理相关的问题，如，老人骨折了如何照护？"
#     }
# }

# read intentions info
intentions = {}
with open(params.intention_inf_json) as fin:
    intentions = json.load(fin)
    logger.info('~~ load intentions dict successful ~~')


for k, v in intentions.items():
    v['slots'].sort


# with open('./intention.json', 'w') as fin:
#     json.dump(intentions, fin, ensure_ascii=False)