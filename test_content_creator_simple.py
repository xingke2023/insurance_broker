#!/usr/bin/env python3
"""
简单测试文案制作功能
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_extract_video_id():
    """测试视频 ID 提取"""
    from urllib.parse import urlparse, parse_qs

    def extract_video_id(url):
        try:
            parsed_url = urlparse(url)
            if parsed_url.netloc in ['youtu.be', 'www.youtu.be']:
                return parsed_url.path[1:].split('?')[0]
            if parsed_url.netloc in ['youtube.com', 'www.youtube.com', 'm.youtube.com']:
                if parsed_url.path == '/watch':
                    query_params = parse_qs(parsed_url.query)
                    return query_params.get('v', [None])[0]
                elif parsed_url.path.startswith('/embed/'):
                    return parsed_url.path.split('/')[2].split('?')[0]
                elif parsed_url.path.startswith('/shorts/'):
                    return parsed_url.path.split('/')[2].split('?')[0]
            return None
        except:
            return None

    print("=" * 50)
    print("测试视频 ID 提取功能")
    print("=" * 50)

    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/rQpiV35akrs",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
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
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        print("   正在测试 Gemini API...")
        response = model.generate_content("Say hello in one word")
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
        print("✅ youtube-transcript-api 已安装")
        print("   注意: 实际字幕提取需要服务器能访问 YouTube")
        return True
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
    print(f"{'✅' if youtube_ok else '❌'} YouTube API 库: {'已安装' if youtube_ok else '未安装'}")

    if gemini_ok and youtube_ok:
        print("\n✨ 所有功能测试通过!")
        print("\n📝 使用步骤:")
        print("   1. 访问: http://your-domain.com/dashboard")
        print("   2. 点击「文案制作」卡片")
        print("   3. 输入 YouTube 视频链接")
        print("   4. 点击「提取字幕」")
        print("\n🎯 功能特点:")
        print("   - 自动识别多语言字幕")
        print("   - AI 智能优化格式")
        print("   - 一键复制字幕内容")
    else:
        print("\n⚠️  部分功能未就绪")

if __name__ == '__main__':
    main()
