import openai

openai.api_key = "EMPTY"
openai.api_base = "http://localhost:8000/v1"

model = "baichuan-13b"

completion = openai.ChatCompletion.create(
    model=model,
    messages=[{"role": "user", "content": "上海颐家是什么?"}]
)

print(completion.choices[0].message.content)
