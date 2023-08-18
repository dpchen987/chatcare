import aiohttp
import asyncio
import json


async def post_completion(model: str, messages: list, temperature: float, top_p: float, max_length: int, stream: bool):
    url = 'http://192.168.10.10:8000/v1/chat/completions'
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_length": max_length,
        "stream": stream
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
            response_text = await resp.text()
            return response_text


# Example usage
async def main():
    messages = [{
        "role": "user",
        "content": "你好"
    }]
    response_text = await post_completion("string", messages, 0, 0, 0, False)
    print(response_text)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
