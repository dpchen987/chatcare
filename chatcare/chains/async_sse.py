#!/usr/bin/env python3
# coding:utf-8

import asyncio
import aiohttp

from zhipuai.utils import jwt_token


URL = 'https://open.bigmodel.cn/api/paas/v3/model-api/chatglm_turbo/sse-invoke'
_FIELD_SEPARATOR = ":"
_BUF = b""


async def connect(token, **kwargs):
    headers = {"Authorization": token}
    data = b''
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, headers=headers, json=kwargs) as resp:
            if resp.status != 200:
                raise Exception('zhipu 请求异常')
            async for line in resp.content:
                data += line
                if data.endswith((b'\r\r', b'\n\n', b'\r\n\r\n')):
                    yield data
                    data = b""
            if data:
                yield data


async def sse_async(**kwargs):
    if 'api_key' not in kwargs:
        raise ValueError('api_key not provided')
    api_key = kwargs.pop('api_key')
    token = jwt_token.generate_token(api_key)
    stream = connect(token, **kwargs)
    async for chunk in stream:
        event = {'id': 0, 'event': '', 'data': '', 'retry': 0, 'meta': ''}
        for line in chunk.splitlines():
            line = line.decode('utf8')
            if not line.strip() or line.startswith(_FIELD_SEPARATOR):
                continue
            data = line.split(_FIELD_SEPARATOR, 1)
            field = data[0]
            if field not in event:
                continue
            if len(data) > 1:
                if data[1].startswith(" "):
                    value = data[1][1:]
                else:
                    value = data[1]
            else:
                value = ""
            if field == 'data':
                event['data'] += value + '\n'
            else:
                if field == 'meta':
                    field = 'comment'
                event[field] = value
        if not event['data']:
            continue
        event.pop('meta')
        if event['data'].endswith('\n'):
            event['data'] = event['data'][0:-1]
        if not event['event']:
            event['event'] = 'message'
        yield event
        asyncio.sleep(0.01)


async def main():
    api_key = '6574a4c99fa996c861b982bf256844c1.eDRvyeGFkczH8boH'
    prompt = f"请用50个字回答问题：食物选择"
    args = dict( 
        model="chatglm_turbo",
        prompt=[{"role": "user", "content": prompt}],
        top_p=0.7,
        temperature=0.9,
    )
    gen = sse_async(api_key=api_key, **args)
    async for e in gen:
        print(e)


if __name__ == '__main__':
    asyncio.run(main())
