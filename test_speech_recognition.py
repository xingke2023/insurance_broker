#!/usr/bin/env python3
"""测试Azure语音识别，验证录音内容"""
import os
import sys
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

def recognize_audio(audio_file_path):
    """识别音频文件内容"""
    print(f"正在识别音频文件: {audio_file_path}")

    # 创建语音配置
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )
    speech_config.speech_recognition_language = "zh-CN"

    # 使用音频文件作为输入
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

    # 创建识别器
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    print("开始识别...")
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"\n识别成功！")
        print(f"识别文本: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print(f"\n无法识别语音")
        print(f"详情: {result.no_match_details}")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"\n识别被取消: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"错误详情: {cancellation_details.error_details}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_speech_recognition.py <音频文件路径>")
        sys.exit(1)

    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"文件不存在: {audio_file}")
        sys.exit(1)

    recognized_text = recognize_audio(audio_file)

    # 与预期文本比较
    if recognized_text:
        # 假设配音员姓名和公司名称
        expected_texts = [
            "我 张三 知道我的录音将被 寰宇數據 用于创建和使用我的语音合成版本",
            "我张三知道我的录音将被寰宇數據用于创建和使用我的语音合成版本",
            "我张三知道我的录音将被寰宇数据用于创建和使用我的语音合成版本",
        ]

        print(f"\n比较结果:")
        for expected in expected_texts:
            if recognized_text.strip().replace(" ", "") == expected.replace(" ", ""):
                print(f"✅ 匹配! 识别文本与预期文本一致")
                break
        else:
            print(f"❌ 不匹配")
            print(f"预期(示例): {expected_texts[0]}")
            print(f"实际识别: {recognized_text}")
