# coding=utf-8
import asyncio
import gradio as gr

from chatcare.api.chat_llm import chat_llm, load_llm_model
from chatcare.api.chat_search_engine import chat_search_engine
from chatcare.config import params
from chatcare.utils import __version__


async def chat_gr_llm(query: str, chat_history: list):
    """
    导入chat-func
    """
    global model, tokenizer, infer
    if "infer" not in globals():
        model, tokenizer, infer = load_llm_model(params)
    response = await chat_llm(query, None)
    chat_history.append((query, response))
    return "", chat_history


async def chat_gr_se(query: str, chat_history: list):
    """
    导入chat-func
    """
    response = await chat_search_engine(query, None)
    chat_history.append((query, response))
    return "", chat_history


def chat(query: str, chat_history: list, mode):
    if mode == 0:
        return asyncio.run(chat_gr_se(query, chat_history))
    else:
        return asyncio.run(chat_gr_llm(query, chat_history))


async def chat_stream(query, chat_history):
    """流式回答"""
    raise NotImplementedError


def main():
    with gr.Blocks() as app:
        with gr.Row():
            with gr.Column(elem_id="column1"):
                gr.Markdown(
                    '<div align="center"><img src="https://www.day-care.cn/wp-content/themes/yijia/assets/images/LOGO-min.png" alt="logo"></div>\n\n'
                    '# <center> ChatCare \n'
                    f'<center> version: {__version__}'
                )
                dd_mode = gr.Dropdown(
                    label="选择对话模式：",
                    choices=["向量搜索模式(se)", "大模型模式(llm)", "知识库模式(kb)"],
                    type="index",
                    value="向量搜索模式(se)"
                )
                btn_clear = gr.Button(value="🗑️清空对话")
                #TODO
                btn_export = gr.Button(value="📃导出记录")
            with gr.Column(scale=15, elem_id="column2"):
                chatbot = gr.Chatbot(label="ChatCare")
                tb_input = gr.Textbox(
                    label="请输入内容：", value="上海颐家是什么?",
                    placeholder="输入问题后，回车开始生成！"
                )
                tb_input.submit(chat, [tb_input, chatbot, dd_mode], [tb_input, chatbot])
                btn_clear.click(lambda x, y: ("", None), [tb_input, chatbot], [tb_input, chatbot])

    app.launch(server_name=params.webui_host, server_port=params.webui_port, share=True)


if __name__ == '__main__':
    main()
