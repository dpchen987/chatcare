import time
import requests
from zhipuai.utils.sse_client import SSEClient

base_url = "http://127.0.0.1:8800"


def chat_sse(query):
    data = {
        "messages": [
            {
                "role": "user",
                "content": f"{query}"
            }
        ],
        'chat_id': 'afefff'
    }
    print('start post', time.time())
    stream = requests.post(f"{base_url}/v1/chat/multi_turn", stream=True, json=data)
    print(stream.headers)
    print('post  done', time.time())
    if stream.status_code == 200:
        # 处理流式响应
        sse = SSEClient(stream)
        print('sse client start', time.time())
        for event in sse.events():
            print(f'{event.event = }')
            print(f'{event.id = }')
            print(f'{event.data = }')
            print(time.time(), event.data)
            # print(event.data, end='', flush=True)
        print('\n')
        print('sse client done', time.time())
    else:
        print("Error:", stream.status_code)
        return None


if __name__ == "__main__":
    queries = [
        '腰椎间盘突出症如何护理',
        '食物选择',
        # '心脏病人如何护理？'
    ]
    for q in queries:
        chat_sse(q)
        print('==='*20)
