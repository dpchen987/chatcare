import openai

openai.api_key = "EMPTY"
openai.api_base = "http://localhost:8000/v1"

model = "chatglm2-6b-int4"

completion = openai.ChatCompletion.create(
    model=model,
    messages=[{"role": "user", "content": "上海颐家是什么?", "stream": True}],
)

print(completion.choices[0].message.content)
