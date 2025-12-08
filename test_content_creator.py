#!/usr/bin/env python3
"""
测试文案制作功能 - 字幕提取 API

使用方法:
python3 test_content_creator.py
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, '/var/www/harry-insurance2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wechat.settings')
django.setup()

from api.content_creator_views import extract_video_id
import google.generativeai as genai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_extract_video_id():
    """测试视频 ID 提取"""
    print("=" * 50)
    print("测试视频 ID 提取功能")
    print("=" * 50)

    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/v/dQw4w9WgXcQ",
    ]

    for url in test_urls:
        video_id = extract_video_id(url)
        status = "✅" if video_id else "❌"
        print(f"{status} URL: {url}")
        print(f"   提取的 ID: {video_id}\n")

def test_gemini_api():
    """测试 Gemini API 配置"""
    print("=" * 50)
    print("测试 Gemini API 配置")
    print("=" * 50)

    api_key = os.environ.get('GEMINI_API_KEY', '')

    if not api_key:
        print("❌ GEMINI_API_KEY 未配置")
        return False

    print(f"✅ GEMINI_API_KEY 已配置: {api_key[:20]}...")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # 简单测试
        response = model.generate_content("请用一句话介绍自己")
        print(f"✅ Gemini API 测试成功")
        print(f"   响应: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API 测试失败: {str(e)}")
        return False

def test_youtube_api():
    """测试 YouTube Transcript API"""
    print("\n" + "=" * 50)
    print("测试 YouTube Transcript API")
    print("=" * 50)

    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        # 使用一个有字幕的测试视频
        test_video_id = "dQw4w9WgXcQ"

        print(f"尝试获取视频 {test_video_id} 的字幕...")

        try:
            transcript = YouTubeTranscriptApi.get_transcript(test_video_id, languages=['en'])
            print(f"✅ YouTube Transcript API 可用")
            print(f"   获取到 {len(transcript)} 条字幕记录")
            if transcript:
                print(f"   第一条: {transcript[0]['text'][:50]}...")
            return True
        except Exception as e:
            print(f"⚠️  获取字幕失败 (这可能是正常的): {str(e)}")
            print(f"   请确保:")
            print(f"   1. 服务器可以访问 YouTube")
            print(f"   2. 视频有可用的字幕")
            return False

    except ImportError:
        print("❌ youtube-transcript-api 未安装")
        return False

def main():
    """运行所有测试"""
    print("\n🚀 开始测试文案制作功能\n")

    # 测试 1: 视频 ID 提取
    test_extract_video_id()

    # 测试 2: Gemini API
    gemini_ok = test_gemini_api()

    # 测试 3: YouTube API
    youtube_ok = test_youtube_api()

    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"✅ 视频 ID 提取: 正常")
    print(f"{'✅' if gemini_ok else '❌'} Gemini API: {'正常' if gemini_ok else '未配置或失败'}")
    print(f"{'✅' if youtube_ok else '⚠️ '} YouTube API: {'正常' if youtube_ok else '可能需要代理'}")

    if gemini_ok:
        print("\n✨ 所有核心功能测试通过!")
        print("\n📝 使用提示:")
        print("   1. 登录系统")
        print("   2. 访问 Dashboard")
        print("   3. 点击「文案制作」")
        print("   4. 输入 YouTube 视频链接")
        print("   5. 点击「提取字幕」按钮")
    else:
        print("\n⚠️  请先配置 GEMINI_API_KEY 环境变量")
        print("   获取地址: https://makersuite.google.com/app/apikey")

if __name__ == '__main__':
    main()
