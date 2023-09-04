# coding=utf-8
# 基于fastllm 框架实现推理
from fastllm_pytools import llm


def load_model(checkpoint_path, device="cuda"):
    model = llm.model(checkpoint_path)
    return model


def infer(model, query: str, history: list = None):
    if history:
        raise NotImplementedError
    response = model.response(query, max_length=4096)
    return response


def infer_stream():
    raise NotImplementedError


if __name__ == '__main__':
    checkpoint_path = "/aidata/junjie/data/model/llms/baichuan13b/baichuan-13b-chat-int4.flm"
    model = load_model(checkpoint_path)
    response = infer(model, "你好")
    print('-' * 88)
    print(response)
