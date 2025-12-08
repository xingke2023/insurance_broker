"""
Alibaba CosyVoice Personal Voice Management Views
使用阿里云通义语音复刻服务创建和管理个人语音模型
"""
import os
import time
import uuid
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# 阿里云配置
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

# 个人语音数据存储路径
PERSONAL_VOICE_DATA_DIR = '/var/www/harry-insurance2/media/personal_voices'
os.makedirs(PERSONAL_VOICE_DATA_DIR, exist_ok=True)

# 目标模型 - 声音复刻时使用的模型必须与语音合成时使用的模型保持一致
TARGET_MODEL = 'cosyvoice-v3-plus'


def get_personal_voice_list_path():
    """获取个人语音列表文件路径"""
    return os.path.join(PERSONAL_VOICE_DATA_DIR, 'voices.json')


def load_personal_voice_list():
    """加载个人语音列表"""
    list_path = get_personal_voice_list_path()
    if os.path.exists(list_path):
        with open(list_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_personal_voice_list(voices):
    """保存个人语音列表"""
    list_path = get_personal_voice_list_path()
    with open(list_path, 'w', encoding='utf-8') as f:
        json.dump(voices, f, ensure_ascii=False, indent=2)


@csrf_exempt
@require_http_methods(["GET"])
def get_personal_voices(request):
    """获取用户的个人语音列表"""
    try:
        voices = load_personal_voice_list()
        return JsonResponse({
            'status': 'success',
            'voices': voices
        })
    except Exception as e:
        logger.error(f"获取个人语音列表失败: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_personal_voice(request):
    """
    创建个人语音
    请求参数:
    - voice_name: 语音名称（必填）
    - voice_talent_name: 配音员姓名 (可选)
    - company_name: 公司名称 (可选)
    - voice_sample: 语音样本音频文件（必填，推荐10-60秒）
    - audio_url: 或者直接提供公网可访问的音频URL
    """
    try:
        # 获取表单数据
        voice_name = request.POST.get('voice_name', '').strip()
        voice_talent_name = request.POST.get('voice_talent_name', '').strip() or '未命名'
        company_name = request.POST.get('company_name', '').strip() or '个人'

        if not voice_name:
            return JsonResponse({
                'status': 'error',
                'message': '语音名称不能为空'
            }, status=400)

        # 获取音频文件
        voice_sample_file = request.FILES.get('voice_sample')
        audio_url = request.POST.get('audio_url', '').strip()  # 支持直接提供URL

        if not voice_sample_file and not audio_url:
            return JsonResponse({
                'status': 'error',
                'message': '请上传语音样本音频文件或提供音频URL'
            }, status=400)

        # 验证DashScope配置
        if not DASHSCOPE_API_KEY:
            return JsonResponse({
                'status': 'error',
                'message': 'DashScope API Key配置缺失'
            }, status=500)

        # 设置API Key
        import dashscope
        dashscope.api_key = DASHSCOPE_API_KEY

        # 生成唯一ID
        personal_voice_id = f'pv-{uuid.uuid4().hex[:12]}'

        # 为音色起一个有意义的前缀 (仅允许数字和小写字母，小于十个字符)
        voice_prefix = f"cv{uuid.uuid4().hex[:6]}"

        # 创建个人语音专用目录
        voice_dir = os.path.join(PERSONAL_VOICE_DATA_DIR, personal_voice_id)
        os.makedirs(voice_dir, exist_ok=True)

        # 如果上传了文件，需要保存并提供公网访问URL
        if voice_sample_file:
            # 保存音频样本
            voice_sample_filename = f'voice_sample_{uuid.uuid4().hex[:8]}.wav'
            voice_sample_path = os.path.join(voice_dir, voice_sample_filename)

            # 保存上传的文件
            with open(voice_sample_path, 'wb') as f:
                for chunk in voice_sample_file.chunks():
                    f.write(chunk)

            # 转换音频格式为标准WAV (如果需要)
            import subprocess
            converted_sample_path = os.path.join(voice_dir, 'voice_sample.wav')

            try:
                subprocess.run([
                    'ffmpeg', '-i', voice_sample_path,
                    '-ar', '16000',  # 采样率 16kHz
                    '-ac', '1',       # 单声道
                    '-sample_fmt', 's16',  # 16-bit
                    '-y',  # 覆盖输出文件
                    converted_sample_path
                ], check=True, capture_output=True)

                # 检查音频时长
                result = subprocess.run([
                    'ffprobe', '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    converted_sample_path
                ], capture_output=True, text=True)
                sample_duration = float(result.stdout.strip())

                logger.info(f"音频样本时长: {sample_duration}秒")

                # 删除原始文件
                os.remove(voice_sample_path)

            except subprocess.CalledProcessError as e:
                logger.error(f"音频格式转换失败: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'音频格式转换失败: {e.stderr.decode() if e.stderr else str(e)}'
                }, status=500)

            # CosyVoice要求音频URL必须是公网可访问的HTTP/HTTPS URL
            # 构建可通过Web服务器访问的URL
            # 假设服务器域名配置在环境变量或使用默认值
            server_domain = os.getenv('SERVER_DOMAIN', 'https://hongkong.xingke888.com')
            relative_path = converted_sample_path.replace('/var/www/harry-insurance2', '')
            audio_url = f"{server_domain}{relative_path}"
            logger.info(f"音频URL: {audio_url}")

        # 验证URL格式
        if not audio_url.startswith('http://') and not audio_url.startswith('https://'):
            return JsonResponse({
                'status': 'error',
                'message': f'音频URL格式错误: {audio_url}。必须是http://或https://开头的公网可访问URL。'
            }, status=400)

        logger.info(f"开始创建个人语音: {voice_name}, prefix={voice_prefix}, url={audio_url}")

        # 步骤1: 创建音色 (异步任务)
        service = VoiceEnrollmentService()
        try:
            voice_id = service.create_voice(
                target_model=TARGET_MODEL,
                prefix=voice_prefix,
                url=audio_url
            )
            request_id = service.get_last_request_id()
            logger.info(f"Voice enrollment submitted successfully. Request ID: {request_id}")
            logger.info(f"Generated Voice ID: {voice_id}")
        except Exception as e:
            logger.error(f"创建音色失败: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': f'创建音色失败: {str(e)}'
            }, status=500)

        # 步骤2: 轮询查询音色状态
        logger.info("开始轮询音色状态...")
        max_attempts = 30
        poll_interval = 10  # 秒

        for attempt in range(max_attempts):
            try:
                voice_info = service.query_voice(voice_id=voice_id)
                status = voice_info.get("status")
                logger.info(f"Attempt {attempt + 1}/{max_attempts}: Voice status is '{status}'")

                if status == "OK":
                    logger.info("Voice is ready for synthesis.")
                    break
                elif status == "UNDEPLOYED" or status == "FAILED":
                    logger.error(f"Voice processing failed with status: {status}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'音色处理失败，状态: {status}。请检查音频质量或联系技术支持。'
                    }, status=500)

                # 对于 "DEPLOYING" 等中间状态，继续等待
                time.sleep(poll_interval)

            except Exception as e:
                logger.error(f"查询音色状态失败: {str(e)}")
                time.sleep(poll_interval)
        else:
            logger.error("Polling timed out. The voice is not ready after several attempts.")
            return JsonResponse({
                'status': 'error',
                'message': '音色创建超时，请稍后重试'
            }, status=500)

        # 保存个人语音信息到列表
        voices = load_personal_voice_list()
        voice_data = {
            'id': personal_voice_id,
            'name': voice_name,
            'voice_talent_name': voice_talent_name,
            'company_name': company_name,
            'voice_id': voice_id,  # CosyVoice的voice_id
            'voice_prefix': voice_prefix,
            'status': 'active',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        voices.append(voice_data)
        save_personal_voice_list(voices)

        logger.info(f"个人语音创建成功: {personal_voice_id}, voice_id={voice_id}")

        return JsonResponse({
            'status': 'success',
            'message': '个人语音创建成功',
            'voice': voice_data
        })

    except Exception as e:
        logger.error(f"创建个人语音错误: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'创建个人语音失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def synthesize_with_personal_voice(request):
    """
    使用个人语音合成
    请求参数:
    - text: 要转换的文本
    - voice_id: CosyVoice的voice_id (从创建的个人语音中获取)
    - rate: 语速 (可选)
    - pitch: 音调 (可选)
    """
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        voice_id = data.get('voice_id', '').strip()  # 使用voice_id而不是speaker_profile_id
        rate = data.get('rate', '0%')
        pitch = data.get('pitch', '0%')

        if not text or not voice_id:
            return JsonResponse({
                'status': 'error',
                'message': '文本和语音ID不能为空'
            }, status=400)

        if len(text) > 5000:
            return JsonResponse({
                'status': 'error',
                'message': '文本长度不能超过5000字符'
            }, status=400)

        # 验证DashScope配置
        if not DASHSCOPE_API_KEY:
            return JsonResponse({
                'status': 'error',
                'message': 'DashScope API Key配置缺失'
            }, status=500)

        # 设置API Key
        import dashscope
        dashscope.api_key = DASHSCOPE_API_KEY

        # 创建语音合成器
        synthesizer = SpeechSynthesizer(model=TARGET_MODEL, voice=voice_id)

        logger.info(f"使用个人语音合成: voice_id={voice_id}")

        # 调用合成接口
        audio_data = synthesizer.call(text)

        if not audio_data:
            raise Exception("语音合成返回空数据")

        # 生成唯一的文件名
        audio_filename = f"personal_tts_{uuid.uuid4()}.mp3"

        # 保存到media目录
        media_dir = '/var/www/harry-insurance2/media/tts'
        os.makedirs(media_dir, exist_ok=True)
        audio_path = os.path.join(media_dir, audio_filename)

        # 写入音频数据
        with open(audio_path, 'wb') as f:
            f.write(audio_data)

        logger.info(f"个人语音合成成功: {audio_filename}, size={len(audio_data)} bytes")

        return JsonResponse({
            'status': 'success',
            'message': '个人语音合成成功',
            'audio_url': f'/media/tts/{audio_filename}',
            'filename': audio_filename
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"个人语音合成错误: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'个人语音合成失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_personal_voice(request, voice_id):
    """删除个人语音"""
    try:
        voices = load_personal_voice_list()
        voice_to_delete = None
        remaining_voices = []

        for voice in voices:
            if voice['id'] == voice_id:
                voice_to_delete = voice
            else:
                remaining_voices.append(voice)

        if not voice_to_delete:
            return JsonResponse({
                'status': 'error',
                'message': '语音不存在'
            }, status=404)

        # 从CosyVoice删除资源
        try:
            import dashscope
            dashscope.api_key = DASHSCOPE_API_KEY

            service = VoiceEnrollmentService()
            cosy_voice_id = voice_to_delete.get('voice_id')
            if cosy_voice_id:
                service.delete_voice(voice_id=cosy_voice_id)
                logger.info(f"已从CosyVoice删除语音: {cosy_voice_id}")
        except Exception as e:
            logger.warning(f"从CosyVoice删除资源时出错: {str(e)}")

        # 删除本地文件
        voice_dir = os.path.join(PERSONAL_VOICE_DATA_DIR, voice_id)
        if os.path.exists(voice_dir):
            import shutil
            shutil.rmtree(voice_dir)

        # 更新列表
        save_personal_voice_list(remaining_voices)

        return JsonResponse({
            'status': 'success',
            'message': '个人语音已删除'
        })

    except Exception as e:
        logger.error(f"删除个人语音错误: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
