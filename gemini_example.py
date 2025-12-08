#!/usr/bin/env python3
"""
Gemini API 示例调用代码
使用新的 google-genai SDK

使用方法:
1. 设置环境变量: export GEMINI_API_KEY="your_api_key"
2. 运行脚本: python3 gemini_example.py
"""

import os
from google import genai
from google.genai import types


def generate():
    """使用 Gemini API 生成内容的示例"""

    # 创建客户端
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # 选择模型
    model = "gemini-2.0-flash-exp"

    # 构建内容
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""请简要介绍一下人工智能的发展历程"""),
            ],
        ),
    ]

    # 配置工具 (可选)
    # 启用 URL 上下文和 Google 搜索
    tools = [
        types.Tool(url_context=types.UrlContext()),
        types.Tool(google_search=types.GoogleSearch()),
    ]

    # 生成内容配置
    generate_content_config = types.GenerateContentConfig(
        temperature=1.0,
        tools=tools,  # 如果不需要工具，可以设置为 None
    )

    print("正在调用 Gemini API...")
    print("-" * 50)

    # 使用流式生成
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text:
            print(chunk.text, end="")

    print("\n" + "-" * 50)


def generate_with_youtube_url():
    """使用 YouTube URL 提取字幕的示例"""

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-exp"

    # 提供 YouTube 视频链接
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    # 构建提示词 - 让 Gemini 直接访问视频并提取字幕
    prompt_text = f"""请分析这个 YouTube 视频并提取完整的字幕内容。

视频链接: {youtube_url}

要求:
1. 提取视频的完整字幕或语音内容
2. 优先使用中文字幕,如果没有中文字幕则使用英文或其他语言
3. 删除重复的内容
4. 合理分段,提高可读性
5. 修正明显的错误
6. 保持原意不变
7. 不要添加任何额外的解释或说明,只输出字幕文本

请直接输出字幕内容:"""

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]

    # 启用 URL 上下文以访问视频内容
    tools = [
        types.Tool(url_context=types.UrlContext()),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.7,  # 降低温度以获得更准确的提取
        tools=tools,
    )

    print("正在使用 Gemini 提取 YouTube 视频字幕...")
    print("-" * 50)

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.text:
            print(chunk.text, end="")

    print("\n" + "-" * 50)


if __name__ == "__main__":
    # 检查 API Key
    if not os.environ.get("GEMINI_API_KEY"):
        print("错误: 请设置 GEMINI_API_KEY 环境变量")
        print("示例: export GEMINI_API_KEY='your_api_key_here'")
        exit(1)

    print("=== 示例 1: 基本文本生成 ===")
    generate()

    print("\n\n=== 示例 2: 提取 YouTube 视频字幕 ===")
    print("提示: 取消注释以下行来测试 YouTube 视频字幕提取")
    # generate_with_youtube_url()
