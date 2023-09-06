# coding=utf-8
import gradio as gr

from chatcare.api.chat_llm import load_llm_model, chat_llm, chat_llm_stream
from chatcare.api.chat_search_engine import chat_search_engine, chat_search_engine_stream
from chatcare.config import params
from chatcare.utils import __version__


async def chat_se_generator(query: str, chat_history: list, stream: bool = True):
    """
    与 search engine 对话
    """
    if stream:
        content = ""
        async for chunk in chat_search_engine_stream(query, None):
            content += chunk
            yield "", chat_history + [(query, content)]
        chat_history.append((query, content))

    else:
        content = await chat_search_engine(query, None)
        chat_history.append((query, content))
        yield "", chat_history


async def chat_llm_generator(query: str, chat_history: list, stream: bool = True):
    """
    与 llm 对话
    """
    global model, tokenizer, infer, infer_stream
    if "infer" not in globals():
        model, tokenizer, infer, infer_stream = load_llm_model(params)
    if stream:
        content = ""
        async for chunk in chat_llm_stream(query, None):
            content += chunk
            yield "", chat_history + [(query, content)]
        chat_history.append((query, content))

    else:
        response = await chat_llm(query, None)
        chat_history.append((query, response))
        yield "", chat_history


async def chat(query: str, chat_history: list, mode: int, stream: bool = True):
    if mode == 0:
        async for chunk in chat_se_generator(query, chat_history, stream):
            yield chunk
    else:
        async for chunk in chat_llm_generator(query, chat_history, stream):
            yield chunk


def main():
    theme = gr.themes.Default(
        primary_hue="orange",
        secondary_hue="blue",
        neutral_hue="emerald"
    ).set(slider_color="#06b4bd")
    with gr.Blocks(theme=theme) as app:
        with gr.Row():
            with gr.Column():
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
                # TODO
                btn_export = gr.Button(value="📃导出记录")
            with gr.Column(scale=15):
                chatbot = gr.Chatbot(label="ChatCare")
                tb_input = gr.Textbox(
                    label="请输入内容：", value="上海颐家简介",
                    placeholder="输入问题后，回车开始生成！"
                )
                tb_input.submit(chat, [tb_input, chatbot, dd_mode], [tb_input, chatbot])
                btn_clear.click(lambda x, y: ("", None), [tb_input, chatbot], [tb_input, chatbot])

    app.queue(concurrency_count=16).launch(
        # auth=("yixiaoai", "AI**yshy"),
        server_name=params.webui_host,
        server_port=params.webui_port,
        share=True)


if __name__ == '__main__':
    main()
