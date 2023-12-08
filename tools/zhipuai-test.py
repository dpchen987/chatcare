import time
import zhipuai
zhipuai.api_key = '880dcc0db4f8226d9ba785c74e377441.ldIxRW21PM6xxmDg'


def gpt(query):
    response = zhipuai.model_api.invoke(
        model="chatglm_turbo",
        prompt=[
            {"role": "user", "content": f"假设你是一名资深的居家护理师，具有丰富的医疗、康复和护理知识，请用约25字回答：{query}"},
            # {"role": "user", "content": f"{query}"},
        ],
        top_p=0.7,
        temperature=0.9,
    )
    # print(response)
    total_tokens = 0
    if response['success']:
        content = response['data']['choices'][0]['content'].replace('\\n\\n', '\n').strip('" ')
        total_tokens = response['data']['usage']['total_tokens']
        print(response['data']['usage'])
    else:
        print(response['msg'])
        content = ''
    # print(content)
    return content, total_tokens


querys = [
    #'你是谁',
    #'食物选择',
    '怎么照顾',
    #'假如你是一名骨科专家，请给一名腰椎间盘突出症患者写一份手术后出院健康指导',
]

for q in querys:
    print(f'query: {q}')
    b = time.time()
    content, total = gpt(q)
    e = time.time()
    time_cost = round(e - b, 2)
    speed = int(total / time_cost)
    print(f'{speed = }, {time_cost = }, {len(content) = }, {content = }')
    print('=='*20)

