#!/usr/bin/env python3
"""测试Azure连续语音识别"""
import os
import sys
import time
import threading
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

def recognize_audio_continuous(audio_file_path):
    """使用连续识别模式识别音频文件内容"""
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

    all_results = []
    done = threading.Event()

    def recognized_cb(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f'识别到: {evt.result.text}')
            all_results.append(evt.result.text)

    def canceled_cb(evt):
        print(f'取消: {evt}')
        done.set()

    def stopped_cb(evt):
        print('停止识别')
        done.set()

    # 连接回调
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_stopped.connect(stopped_cb)
    speech_recognizer.canceled.connect(canceled_cb)

    # 开始连续识别
    print("开始连续识别...")
    speech_recognizer.start_continuous_recognition()

    # 等待完成
    done.wait()

    # 停止识别
    speech_recognizer.stop_continuous_recognition()

    return ' '.join(all_results)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_continuous_recognition.py <音频文件路径>")
        sys.exit(1)

    audio_file = sys.argv[1]
    if not os.path.exists(audio_file):
        print(f"文件不存在: {audio_file}")
        sys.exit(1)

    recognized_text = recognize_audio_continuous(audio_file)

    print(f"\n完整识别结果: {recognized_text}")
