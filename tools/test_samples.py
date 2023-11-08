import requests
import json

# Define the URL and endpoint
url = 'http://192.168.10.10:8800/v1/chat/multi_turn'
qu_li = [['腰椎间盘突出症手术治疗后的护理方式有哪些'], ['腰椎间盘突出手术治疗后要怎么护理'], ['认知障碍症如何护理'], ['老年痴呆怎么照顾'],
         ['腰椎间盘突出症的护理方式有哪些', '手术治疗'], ['患者有腰椎间盘突出症要怎么护理', '手术治疗'], ['患者桡骨远端骨折怎么护理', '我们不想手术'],
         ['患者有肱骨骨折如何护理', '近端骨折', '手术治疗'], ['患者有肱骨骨折如何护理', '手术治疗', '远端骨折'],
         ['患者桡骨远端骨折怎么护理', '我们希望能保守治疗'], ['患者骨折了怎么护理', '股骨颈骨折', '手术'], ['患者腰有问题该怎么护理', '保守治疗', '腰椎间盘突出症']
         ]

# Define the headers for the request
headers = {
    'Content-Type': 'application/json',
}

# Define the data to be sent in the request
data = {
    "messages": [
    ],
}

def result(data):
    # Send a POST request to the server
    response = requests.post(url, headers=headers, json=data)

    # Check for a valid response
    if response.status_code == 200:
        # Parse the JSON response
        response_data = response.json()
        return json.dumps(response_data['summary'], indent=4, ensure_ascii=False)
    else:
        print(f'Failed to retrieve data: {response.status_code}')
        return response.text

# data['messages']+=[{'role': 'user', 'content': '患者腰有问题该怎么护理'}, {'role': 'assistant', 'content': '"请问老人患有哪种疾病？"'}, {'role': 'user', 'content': '腰椎间盘突出'}, {'role': 'assistant', 'content': '"请问老人采用哪种形式的治疗？"'},{'role': 'user', 'content': '保守治疗'}]
# # print(data)
# print(result(data))

li = []
for i in qu_li:
    for j in i:
        data['messages'].append({"role": "user", "content": j})
        data['messages'].append({"role": "assistant", "content": result(data)})
    li.append(data['messages'])
    # print(data['messages'])
    data['messages'] = []

import pandas as pd
df = pd.DataFrame()
df['对话'] = li
df.to_excel('对话模板.xlsx', index=False)


