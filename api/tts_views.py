"""
Azure Text-to-Speech Views with Word/Character Boundaries
使用Azure认知服务提供语音合成功能，支持字符级别字幕
"""
import os
import uuid
import json
import logging
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Azure配置
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')

# 语音选项配置
VOICE_OPTIONS = {
    # 中文语音
    'zh-CN-XiaoxiaoNeural': {'name': '晓晓 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-YunxiNeural': {'name': '云希 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-YunjianNeural': {'name': '云健 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-XiaoyiNeural': {'name': '晓伊 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-YunyangNeural': {'name': '云扬 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-XiaochenNeural': {'name': '晓辰 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaohanNeural': {'name': '晓涵 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaomengNeural': {'name': '晓梦 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaomoNeural': {'name': '晓墨 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaoqiuNeural': {'name': '晓秋 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaoruiNeural': {'name': '晓睿 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaoshuangNeural': {'name': '晓双 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaoxuanNeural': {'name': '晓萱 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaoyanNeural': {'name': '晓颜 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaoyouNeural': {'name': '晓悠 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-XiaozhenNeural': {'name': '晓甄 (女声)', 'language': 'zh-CN', 'gender': 'Female'},
    'zh-CN-YunfengNeural': {'name': '云枫 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-YunhaoNeural': {'name': '云皓 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-YunxiaNeural': {'name': '云夏 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-YunyeNeural': {'name': '云野 (男声)', 'language': 'zh-CN', 'gender': 'Male'},
    'zh-CN-YunzeNeural': {'name': '云泽 (男声)', 'language': 'zh-CN', 'gender': 'Male'},

    # 粤语
    'zh-HK-HiuGaaiNeural': {'name': '曉佳 (粤语女声)', 'language': 'zh-HK', 'gender': 'Female'},
    'zh-HK-HiuMaanNeural': {'name': '曉曼 (粤语女声)', 'language': 'zh-HK', 'gender': 'Female'},
    'zh-HK-WanLungNeural': {'name': '雲龍 (粤语男声)', 'language': 'zh-HK', 'gender': 'Male'},

    # 台湾话
    'zh-TW-HsiaoChenNeural': {'name': '曉臻 (台湾女声)', 'language': 'zh-TW', 'gender': 'Female'},
    'zh-TW-HsiaoYuNeural': {'name': '曉雨 (台湾女声)', 'language': 'zh-TW', 'gender': 'Female'},
    'zh-TW-YunJheNeural': {'name': '雲哲 (台湾男声)', 'language': 'zh-TW', 'gender': 'Male'},

    # 英语
    'en-US-JennyNeural': {'name': 'Jenny (美式女声)', 'language': 'en-US', 'gender': 'Female'},
    'en-US-GuyNeural': {'name': 'Guy (美式男声)', 'language': 'en-US', 'gender': 'Male'},
    'en-US-AriaNeural': {'name': 'Aria (美式女声)', 'language': 'en-US', 'gender': 'Female'},
    'en-GB-SoniaNeural': {'name': 'Sonia (英式女声)', 'language': 'en-GB', 'gender': 'Female'},
    'en-GB-RyanNeural': {'name': 'Ryan (英式男声)', 'language': 'en-GB', 'gender': 'Male'},
}


@csrf_exempt
@require_http_methods(["GET"])
def get_voices(request):
    """获取可用的语音列表"""
    try:
        voices = []
        for voice_id, info in VOICE_OPTIONS.items():
            voices.append({
                'id': voice_id,
                'name': info['name'],
                'language': info['language'],
                'gender': info['gender']
            })

        return JsonResponse({
            'status': 'success',
            'voices': voices
        })
    except Exception as e:
        logger.error(f"获取语音列表失败: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def synthesize_speech(request):
    """
    合成语音并生成字符级别字幕
    请求参数:
    - text: 要转换的文本
    - voice: 语音ID (可选，默认为zh-CN-XiaoxiaoNeural)
    - rate: 语速 (-50% 到 +50%, 可选，默认为0%)
    - pitch: 音调 (-50% 到 +50%, 可选，默认为0%)
    """
    try:
        import json
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        voice_id = data.get('voice', 'zh-CN-XiaoxiaoNeural')
        rate = data.get('rate', '0%')
        pitch = data.get('pitch', '0%')

        if not text:
            return JsonResponse({
                'status': 'error',
                'message': '文本不能为空'
            }, status=400)

        if voice_id not in VOICE_OPTIONS:
            return JsonResponse({
                'status': 'error',
                'message': f'不支持的语音: {voice_id}'
            }, status=400)

        # 验证Azure配置
        if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
            return JsonResponse({
                'status': 'error',
                'message': 'Azure Speech配置缺失'
            }, status=500)

        # 配置Azure Speech
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )

        # 设置语音
        speech_config.speech_synthesis_voice_name = voice_id

        # 生成唯一的文件名
        audio_filename = f"tts_{uuid.uuid4()}.mp3"
        audio_path = os.path.join('/tmp', audio_filename)

        # 配置音频输出
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)

        # 创建合成器
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        # 用于收集字幕数据
        subtitle_data = []

        # 注册事件处理器以获取字符边界信息
        def word_boundary_cb(evt):
            """处理词边界事件，获取每个字符/词的时间信息"""
            subtitle_data.append({
                'text': evt.text,
                'audio_offset': evt.audio_offset / 10000,  # 转换为毫秒
                'duration': evt.duration.total_seconds() * 1000 if evt.duration else 0,
                'word_length': evt.word_length,
                'text_offset': evt.text_offset,
                'boundary_type': evt.boundary_type.name
            })

        # 连接词边界事件
        synthesizer.synthesis_word_boundary.connect(word_boundary_cb)

        # 构建SSML (Speech Synthesis Markup Language)
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
            <voice name='{voice_id}'>
                <prosody rate='{rate}' pitch='{pitch}'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        # 合成语音
        result = synthesizer.speak_ssml_async(ssml).get()

        # 检查结果
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"语音合成成功: {audio_filename}, 字幕条目数: {len(subtitle_data)}")

            # 保存到media目录
            media_dir = '/var/www/harry-insurance2/media/tts'
            os.makedirs(media_dir, exist_ok=True)
            final_audio_path = os.path.join(media_dir, audio_filename)

            # 移动文件
            import shutil
            shutil.move(audio_path, final_audio_path)

            # 生成字幕文件（JSON格式）
            subtitle_filename = f"tts_{uuid.uuid4().hex[:8]}.json"
            subtitle_path = os.path.join(media_dir, subtitle_filename)

            with open(subtitle_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'text': text,
                    'voice': voice_id,
                    'rate': rate,
                    'pitch': pitch,
                    'subtitles': subtitle_data
                }, f, ensure_ascii=False, indent=2)

            # 生成SRT格式字幕（可选）
            srt_filename = f"tts_{uuid.uuid4().hex[:8]}.srt"
            srt_path = os.path.join(media_dir, srt_filename)
            generate_srt(subtitle_data, srt_path)

            # 生成WebVTT格式字幕（可选）
            vtt_filename = f"tts_{uuid.uuid4().hex[:8]}.vtt"
            vtt_path = os.path.join(media_dir, vtt_filename)
            generate_webvtt(subtitle_data, vtt_path)

            return JsonResponse({
                'status': 'success',
                'message': '语音合成成功',
                'audio_url': f'/media/tts/{audio_filename}',
                'subtitle_url': f'/media/tts/{subtitle_filename}',
                'srt_url': f'/media/tts/{srt_filename}',
                'vtt_url': f'/media/tts/{vtt_filename}',
                'filename': audio_filename,
                'subtitle_count': len(subtitle_data),
                'subtitles': subtitle_data  # 直接返回字幕数据
            })
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            error_msg = f"语音合成失败: {cancellation.reason}"
            if cancellation.reason == speechsdk.CancellationReason.Error:
                error_msg += f" - {cancellation.error_details}"
            logger.error(error_msg)
            return JsonResponse({
                'status': 'error',
                'message': error_msg
            }, status=500)
        else:
            return JsonResponse({
                'status': 'error',
                'message': '语音合成失败'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"语音合成错误: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def generate_srt(subtitle_data, output_path):
    """生成SRT格式字幕文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for idx, item in enumerate(subtitle_data, 1):
                start_time = item['audio_offset']
                end_time = start_time + item.get('duration', 0)

                # 转换为SRT时间格式: HH:MM:SS,mmm
                start_srt = format_srt_time(start_time)
                end_srt = format_srt_time(end_time)

                f.write(f"{idx}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                f.write(f"{item['text']}\n")
                f.write("\n")
    except Exception as e:
        logger.error(f"生成SRT字幕失败: {str(e)}")


def generate_webvtt(subtitle_data, output_path):
    """生成WebVTT格式字幕文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")

            for idx, item in enumerate(subtitle_data, 1):
                start_time = item['audio_offset']
                end_time = start_time + item.get('duration', 0)

                # 转换为WebVTT时间格式: HH:MM:SS.mmm
                start_vtt = format_webvtt_time(start_time)
                end_vtt = format_webvtt_time(end_time)

                f.write(f"{idx}\n")
                f.write(f"{start_vtt} --> {end_vtt}\n")
                f.write(f"{item['text']}\n")
                f.write("\n")
    except Exception as e:
        logger.error(f"生成WebVTT字幕失败: {str(e)}")


def format_srt_time(milliseconds):
    """格式化时间为SRT格式: HH:MM:SS,mmm"""
    hours = int(milliseconds // 3600000)
    minutes = int((milliseconds % 3600000) // 60000)
    seconds = int((milliseconds % 60000) // 1000)
    millis = int(milliseconds % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def format_webvtt_time(milliseconds):
    """格式化时间为WebVTT格式: HH:MM:SS.mmm"""
    hours = int(milliseconds // 3600000)
    minutes = int((milliseconds % 3600000) // 60000)
    seconds = int((milliseconds % 60000) // 1000)
    millis = int(milliseconds % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


@csrf_exempt
@require_http_methods(["GET"])
def download_audio(request, filename):
    """下载音频文件"""
    try:
        file_path = os.path.join('/var/www/harry-insurance2/media/tts', filename)

        if not os.path.exists(file_path):
            return JsonResponse({
                'status': 'error',
                'message': '文件不存在'
            }, status=404)

        response = FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"下载音频失败: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
