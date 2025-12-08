import os
import logging
import base64
import mimetypes
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pathlib import Path
import uuid
from google import genai
from google.genai import types
from .models import IPImage, GeminiUsage, UserQuota
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

# 图片存储路径
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
IP_IMAGE_DIR = os.path.join(MEDIA_ROOT, 'ip_images')

# 确保目录存在
os.makedirs(IP_IMAGE_DIR, exist_ok=True)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ip_image(request):
    """
    使用AI生成个人IP形象图片

    请求参数:
    - image: 用户上传的照片文件
    - prompt: 创意提示语

    返回:
    - status: success/error
    - image_url: 生成的图片URL
    - message: 提示信息
    """
    try:
        # 检查用户额度
        quota, created = UserQuota.objects.get_or_create(user=request.user)
        if not quota.has_quota():
            return Response({
                'status': 'error',
                'message': '您的可用次数不足，请购买次数后再试',
                'available_quota': quota.available_quota
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取请求参数
        uploaded_image = request.FILES.get('image')
        prompt = request.data.get('prompt', '')

        if not uploaded_image:
            return Response({
                'status': 'error',
                'message': '请上传照片'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not prompt.strip():
            return Response({
                'status': 'error',
                'message': '请输入提示语'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if uploaded_image.content_type not in allowed_types:
            return Response({
                'status': 'error',
                'message': '只支持 JPG, PNG, WEBP 格式的图片'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小 (限制10MB)
        if uploaded_image.size > 10 * 1024 * 1024:
            return Response({
                'status': 'error',
                'message': '图片大小不能超过10MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"收到IP形象生成请求: user={request.user.username}, prompt={prompt}")

        # 读取上传的图片数据
        image_data = uploaded_image.read()

        # 获取图片的 MIME 类型
        mime_type = uploaded_image.content_type

        # 使用 Gemini API 生成图片
        gemini_api_key = os.getenv('GEMINI_API_KEY')

        if not gemini_api_key:
            return Response({
                'status': 'error',
                'message': '暂未配置AI图像生成服务，请联系管理员配置 GEMINI_API_KEY 环境变量'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            generated_image_path = generate_with_gemini(image_data, mime_type, prompt, gemini_api_key, request.user.username)

            if generated_image_path:
                # 生成访问URL - 强制使用 https
                image_url = f"https://{request.get_host()}/media/ip_images/{os.path.basename(generated_image_path)}"

                # 扣减用户额度
                quota.consume_quota()
                logger.info(f"用户 {request.user.username} 消耗1次额度，剩余: {quota.available_quota}次")

                # 记录成功的调用统计
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='ip_image',
                    prompt=prompt,
                    success=True
                )

                logger.info(f"成功使用 Gemini 生成IP形象: {image_url}")
                return Response({
                    'status': 'success',
                    'image_url': image_url,
                    'message': 'IP形象生成成功',
                    'method': 'gemini',
                    'remaining_quota': quota.available_quota
                })
            else:
                # 记录失败的调用统计
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='ip_image',
                    prompt=prompt,
                    success=False,
                    error_message='未返回图片数据'
                )
                return Response({
                    'status': 'error',
                    'message': '生成失败，未返回图片数据'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # 记录失败的调用统计
            GeminiUsage.objects.create(
                user=request.user,
                generation_type='ip_image',
                prompt=prompt,
                success=False,
                error_message=str(e)
            )
            logger.error(f"Gemini 生成失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"生成IP形象错误: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'生成失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_with_gemini(image_data, mime_type, prompt, api_key, username):
    """
    使用 Gemini API 生成IP形象图片

    参数:
    - image_data: 用户上传的图片二进制数据
    - mime_type: 图片的MIME类型 (如 image/jpeg)
    - prompt: 用户的创意提示语
    - api_key: Gemini API密钥
    - username: 用户名（用于生成唯一文件名）

    返回:
    - 生成的图片文件路径
    """
    try:
        # 创建 Gemini 客户端
        client = genai.Client(api_key=api_key)

        # 使用图像生成模型
        model = "gemini-3-pro-image-preview"

        # 保存临时图片文件供 PIL 读取
        temp_image_path = os.path.join(IP_IMAGE_DIR, f"temp_{uuid.uuid4()}.jpg")
        with open(temp_image_path, 'wb') as f:
            f.write(image_data)

        # 使用 PIL 加载图片
        from PIL import Image as PILImage
        user_image = PILImage.open(temp_image_path)

        # 构建提示词 - 要求基于用户照片生成个性化IP形象
        full_prompt = f"""Based on this photo, create a personalized IP character image.

User's style requirement: {prompt}

Requirements:
1. Maintain the main features of the person in the photo (facial contours, hairstyle, temperament)
2. Create artistic interpretation according to the specified style
3. Generate high-quality, creative IP character image
4. Suitable for personal branding
5. Professional and aesthetically pleasing

Please generate an IP character image that meets these requirements."""

        logger.info(f"开始使用 Gemini 生成IP形象，提示语: {prompt}")

        # 简洁的多模态请求 - 直接传递图片对象和文本（按官方示例）
        response = client.models.generate_content(
            model=model,
            contents=[user_image, full_prompt],
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image'],
                temperature=1.0,
            )
        )

        # 处理响应
        generated_image_data = None
        generated_mime_type = None
        text_response = ""

        for part in response.parts:
            # 收集文本响应
            if part.text is not None:
                text_response += part.text
                logger.info(f"Gemini 文本响应: {part.text}")

            # 处理图片数据
            elif part.inline_data is not None:
                generated_image_data = part.inline_data.data
                generated_mime_type = part.inline_data.mime_type
                logger.info(f"收到生成的图片数据，MIME类型: {generated_mime_type}")

        # 清理临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        # 保存生成的图片
        if generated_image_data:
            # 根据 MIME 类型确定文件扩展名
            file_extension = mimetypes.guess_extension(generated_mime_type) or '.png'

            # 生成唯一文件名
            filename = f"ip_{username}_{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(IP_IMAGE_DIR, filename)

            # 保存图片文件
            with open(file_path, 'wb') as f:
                f.write(generated_image_data)

            logger.info(f"IP形象图片已保存: {file_path}")
            return file_path
        else:
            logger.error("Gemini 未返回图片数据")
            return None

    except Exception as e:
        logger.error(f"Gemini 生成IP形象失败: {str(e)}", exc_info=True)
        # 确保清理临时文件
        if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        raise


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_ip_image(request):
    """
    获取用户保存的个人IP形象
    """
    try:
        # 查询用户保存的IP形象
        try:
            ip_image = IPImage.objects.get(user=request.user)
            return Response({
                'status': 'success',
                'has_saved': True,
                'data': {
                    'generated_image_url': ip_image.generated_image_url,
                    'prompt': ip_image.prompt,
                    'created_at': ip_image.created_at.isoformat(),
                    'updated_at': ip_image.updated_at.isoformat(),
                }
            })
        except IPImage.DoesNotExist:
            return Response({
                'status': 'success',
                'has_saved': False,
                'message': '暂无保存的IP形象'
            })
    except Exception as e:
        logger.error(f"获取保存的IP形象错误: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'获取失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_ip_image(request):
    """
    保存用户的个人IP形象到数据库

    请求参数:
    - generated_image_url: 生成的IP形象URL
    - prompt: 使用的提示语
    - original_image_url: 原始照片URL（可选）
    """
    try:
        generated_image_url = request.data.get('generated_image_url', '')
        prompt = request.data.get('prompt', '')
        original_image_url = request.data.get('original_image_url', '')

        if not generated_image_url:
            return Response({
                'status': 'error',
                'message': '请提供生成的图片URL'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 使用 update_or_create 来创建或更新记录
        ip_image, created = IPImage.objects.update_or_create(
            user=request.user,
            defaults={
                'generated_image_url': generated_image_url,
                'prompt': prompt,
                'original_image_url': original_image_url,
            }
        )

        action = '保存' if created else '更新'
        logger.info(f"用户 {request.user.username} {action}了IP形象")

        return Response({
            'status': 'success',
            'message': f'IP形象{action}成功',
            'data': {
                'generated_image_url': ip_image.generated_image_url,
                'prompt': ip_image.prompt,
                'created_at': ip_image.created_at.isoformat(),
                'updated_at': ip_image.updated_at.isoformat(),
            }
        })
    except Exception as e:
        logger.error(f"保存IP形象错误: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'保存失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_content_image(request):
    """
    根据文案内容生成配图

    请求参数:
    - content: 文案内容
    - image_index: 图片索引（用于生成不同风格）

    返回:
    - status: success/error
    - image_url: 生成的图片URL
    - prompt: 使用的提示语
    - message: 提示信息
    """
    try:
        # 检查用户额度
        quota, created = UserQuota.objects.get_or_create(user=request.user)
        if not quota.has_quota():
            return Response({
                'status': 'error',
                'message': '您的可用次数不足，请购买次数后再试',
                'available_quota': quota.available_quota
            }, status=status.HTTP_403_FORBIDDEN)

        # 获取请求参数
        content = request.data.get('content', '')
        image_index = int(request.data.get('image_index', 1))  # 转换为整数
        include_ip_image = request.data.get('include_ip_image', 'false').lower() == 'true'
        ip_image_url = request.data.get('ip_image_url', '')

        if not content.strip():
            return Response({
                'status': 'error',
                'message': '请输入文案内容'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文案长度
        if len(content) > 1000:
            return Response({
                'status': 'error',
                'message': '文案内容不能超过1000字符'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"收到文案配图生成请求: user={request.user.username}, index={image_index}")

        # 使用 Gemini API 生成图片 - 使用与IP形象生成相同的API Key
        gemini_api_key = os.getenv('IP_IMAGE_API_KEY')

        if not gemini_api_key:
            return Response({
                'status': 'error',
                'message': '暂未配置AI图像生成服务，请联系管理员配置 IP_IMAGE_API_KEY 环境变量'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            generated_image_path, used_prompt = generate_content_image_with_gemini(
                content,
                image_index,
                gemini_api_key,
                request.user.username,
                include_ip_image,
                ip_image_url
            )

            if generated_image_path:
                # 生成访问URL - 强制使用 https
                image_url = f"https://{request.get_host()}/media/ip_images/{os.path.basename(generated_image_path)}"

                # 扣减用户额度
                quota.consume_quota()
                logger.info(f"用户 {request.user.username} 消耗1次额度，剩余: {quota.available_quota}次")

                # 记录成功的调用统计
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='content_image',
                    prompt=content[:500],  # 只存储前500个字符
                    success=True
                )

                logger.info(f"成功使用 Gemini 生成文案配图: {image_url}")
                return Response({
                    'status': 'success',
                    'image_url': image_url,
                    'prompt': used_prompt,
                    'message': '配图生成成功',
                    'method': 'gemini',
                    'remaining_quota': quota.available_quota
                })
            else:
                # 记录失败的调用统计
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='content_image',
                    prompt=content[:500],
                    success=False,
                    error_message='未返回图片数据'
                )
                return Response({
                    'status': 'error',
                    'message': '生成失败，未返回图片数据'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # 记录失败的调用统计
            GeminiUsage.objects.create(
                user=request.user,
                generation_type='content_image',
                prompt=content[:500],
                success=False,
                error_message=str(e)
            )
            logger.error(f"Gemini 生成失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"生成文案配图错误: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'生成失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_content_image_with_gemini(content, image_index, api_key, username, include_ip_image=False, ip_image_url=''):
    """
    使用 Gemini API 根据文案生成配图

    参数:
    - content: 文案内容
    - image_index: 图片索引（用于生成不同风格的配图）
    - api_key: Gemini API密钥
    - username: 用户名（用于生成唯一文件名）
    - include_ip_image: 是否包含IP形象
    - ip_image_url: IP形象图片URL

    返回:
    - (生成的图片文件路径, 使用的提示语)
    """
    try:
        # 创建 Gemini 客户端
        client = genai.Client(api_key=api_key)

        # 使用图像生成模型
        model = "gemini-3-pro-image-preview"

        # 处理IP形象图片（如果需要包含）
        ip_image = None
        temp_ip_image_path = None
        if include_ip_image and ip_image_url:
            try:
                logger.info(f"下载用户IP形象: {ip_image_url}")

                # 下载IP形象图片
                response = requests.get(ip_image_url, timeout=10)
                response.raise_for_status()

                # 保存临时文件
                temp_ip_image_path = os.path.join(IP_IMAGE_DIR, f"temp_ip_{uuid.uuid4()}.jpg")
                with open(temp_ip_image_path, 'wb') as f:
                    f.write(response.content)

                # 使用 PIL 加载图片
                from PIL import Image as PILImage
                ip_image = PILImage.open(temp_ip_image_path)
                logger.info("成功加载用户IP形象")
            except Exception as e:
                logger.warning(f"加载IP形象失败，将继续生成不包含IP形象的配图: {str(e)}")
                # 如果加载失败，继续生成不包含IP形象的图片
                ip_image = None
                if temp_ip_image_path and os.path.exists(temp_ip_image_path):
                    os.remove(temp_ip_image_path)
                    temp_ip_image_path = None

        # 定义不同风格的提示语模板
        style_variations = [
            "Create a professional, high-quality image that perfectly illustrates this content. Use a clean, modern style with vibrant colors.",
            "Generate a creative and artistic image for this content. Use an abstract, expressive style with bold colors and dynamic composition.",
            "Create a minimalist, elegant image for this content. Use simple shapes, soft colors, and plenty of white space.",
            "Generate a photorealistic image that brings this content to life. Use natural lighting and realistic details.",
            "Create a colorful, playful illustration for this content. Use a cartoon or animated style with bright, cheerful colors."
        ]

        # 根据索引选择风格（循环使用）
        style_prompt = style_variations[(image_index - 1) % len(style_variations)]

        # 构建完整提示词
        if ip_image:
            # 如果包含IP形象，修改提示词以融入IP角色
            full_prompt = f"""{style_prompt}

IMPORTANT: The first image provided is the user's personal IP character. Please incorporate this character naturally into the generated image, but as a supporting element, NOT the main focus.

Content to visualize: {content}

Requirements:
1. The PRIMARY FOCUS should be on visualizing the content theme and message
2. Include the IP character from the reference image as a natural participant or observer in the scene
3. The character should be present but blend harmoniously with the overall composition - like a protagonist in a story, not the story itself
4. The scene, atmosphere, and content message should be the main narrative, with the character experiencing or interacting with it
5. Maintain the character's distinctive features while keeping them proportionate to the scene
6. High resolution and professional quality
7. Visually appealing and suitable for social media or marketing materials
8. No text or watermarks in the image
9. The viewer should first notice the content theme, then recognize the character as part of the scene

Generate an image where the content message is the hero, and the IP character is the protagonist experiencing it."""
        else:
            # 不包含IP形象的标准提示词
            full_prompt = f"""{style_prompt}

Content to visualize: {content}

Requirements:
1. The image should clearly represent the main theme of the content
2. High resolution and professional quality
3. Visually appealing and suitable for social media or marketing materials
4. No text or watermarks in the image
5. Focus on visual storytelling

Generate an image that perfectly captures the essence of this content."""

        logger.info(f"开始使用 Gemini 生成文案配图，索引: {image_index}, 包含IP形象: {ip_image is not None}")

        # 构建请求内容
        if ip_image:
            # 多模态请求：包含IP形象和文本提示
            contents = [ip_image, full_prompt]
        else:
            # 仅文本请求
            contents = [full_prompt]

        # 图像生成请求
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image'],
                temperature=1.0,
            )
        )

        # 处理响应
        generated_image_data = None
        generated_mime_type = None
        text_response = ""

        for part in response.parts:
            # 收集文本响应
            if part.text is not None:
                text_response += part.text
                logger.info(f"Gemini 文本响应: {part.text}")

            # 处理图片数据
            elif part.inline_data is not None:
                generated_image_data = part.inline_data.data
                generated_mime_type = part.inline_data.mime_type
                logger.info(f"收到生成的图片数据，MIME类型: {generated_mime_type}")

        # 清理临时IP形象文件
        if temp_ip_image_path and os.path.exists(temp_ip_image_path):
            os.remove(temp_ip_image_path)

        # 保存生成的图片
        if generated_image_data:
            # 根据 MIME 类型确定文件扩展名
            file_extension = mimetypes.guess_extension(generated_mime_type) or '.png'

            # 生成唯一文件名
            filename = f"content_{username}_{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(IP_IMAGE_DIR, filename)

            # 保存图片文件
            with open(file_path, 'wb') as f:
                f.write(generated_image_data)

            logger.info(f"文案配图已保存: {file_path}")
            return file_path, style_prompt
        else:
            logger.error("Gemini 未返回图片数据")
            return None, None

    except Exception as e:
        logger.error(f"Gemini 生成文案配图失败: {str(e)}", exc_info=True)
        # 确保清理临时IP形象文件
        if 'temp_ip_image_path' in locals() and temp_ip_image_path and os.path.exists(temp_ip_image_path):
            os.remove(temp_ip_image_path)
        raise


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_gemini_usage_stats(request):
    """
    获取用户的 Gemini API 调用统计

    查询参数:
    - period: 统计周期 (today, week, month, all) 默认: all
    - type: 生成类型 (ip_image, content_image, all) 默认: all

    返回:
    - total_count: 总调用次数
    - success_count: 成功次数
    - failed_count: 失败次数
    - ip_image_count: IP形象生成次数
    - content_image_count: 文案配图生成次数
    - recent_usage: 最近的调用记录
    """
    try:
        period = request.query_params.get('period', 'all')
        generation_type = request.query_params.get('type', 'all')

        # 基础查询：当前用户的所有记录
        queryset = GeminiUsage.objects.filter(user=request.user)

        # 根据时间周期过滤
        if period == 'today':
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(created_at__gte=start_date)
        elif period == 'week':
            start_date = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=start_date)
        elif period == 'month':
            start_date = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=start_date)

        # 根据生成类型过滤
        if generation_type != 'all':
            queryset = queryset.filter(generation_type=generation_type)

        # 统计数据
        total_count = queryset.count()
        success_count = queryset.filter(success=True).count()
        failed_count = queryset.filter(success=False).count()

        # 按类型统计
        ip_image_count = queryset.filter(generation_type='ip_image').count()
        content_image_count = queryset.filter(generation_type='content_image').count()

        # 获取最近的调用记录（最多10条）
        recent_usage = queryset.order_by('-created_at')[:10].values(
            'id',
            'generation_type',
            'prompt',
            'success',
            'error_message',
            'created_at'
        )

        # 获取用户可用次数
        quota, created = UserQuota.objects.get_or_create(user=request.user)

        return Response({
            'status': 'success',
            'data': {
                'period': period,
                'total_count': total_count,
                'success_count': success_count,
                'failed_count': failed_count,
                'success_rate': round(success_count / total_count * 100, 2) if total_count > 0 else 0,
                'by_type': {
                    'ip_image_count': ip_image_count,
                    'content_image_count': content_image_count,
                },
                'quota': {
                    'available': quota.available_quota,
                    'total_purchased': quota.total_purchased,
                },
                'recent_usage': list(recent_usage)
            }
        })
    except Exception as e:
        logger.error(f"获取Gemini使用统计错误: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'获取统计数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 支持的纵横比
SUPPORTED_ASPECT_RATIOS = [
    "21:9", "16:9", "4:3", "3:2", "1:1",
    "9:16", "3:4", "2:3", "5:4", "4:5"
]


def _handle_content_image_generation(request, quota):
    """
    处理文案配图生成请求的辅助函数
    """
    try:
        # 获取请求参数
        content = request.data.get('content', '')
        image_index = int(request.data.get('image_index', 1))
        include_ip_image = request.data.get('include_ip_image', 'false').lower() == 'true'
        ip_image_url = request.data.get('ip_image_url', '')
        aspect_ratio = request.data.get('aspect_ratio', '9:16')

        if not content.strip():
            return Response({
                'status': 'error',
                'message': '请输入文案内容'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文案长度
        if len(content) > 1000:
            return Response({
                'status': 'error',
                'message': '文案内容不能超过1000字符'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"收到文案配图生成请求(V2): user={request.user.username}, index={image_index}, include_ip={include_ip_image}")

        # 使用 Gemini REST API 生成图片
        gemini_api_key = os.getenv('IP_IMAGE_API_KEY')
        gemini_api_url = os.getenv('GEMINI_API_URL', 'https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent')

        if not gemini_api_key:
            return Response({
                'status': 'error',
                'message': '暂未配置图片生成服务，请联系管理员'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # 调用新的 REST API 生成函数
            generated_image_path, used_prompt = generate_content_image_with_rest_api(
                content,
                image_index,
                gemini_api_key,
                gemini_api_url,
                request.user.username,
                include_ip_image,
                ip_image_url,
                aspect_ratio
            )

            if generated_image_path:
                # 生成访问URL - 强制使用 https
                image_url = f"https://{request.get_host()}/media/ip_images/{os.path.basename(generated_image_path)}"

                # 扣减用户额度
                quota.consume_quota()
                logger.info(f"用户 {request.user.username} 消耗1次额度，剩余: {quota.available_quota}次")

                # 记录使用情况
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='content_image',
                    prompt=used_prompt[:500],
                    success=True
                )

                # 获取关联的IP形象ID（如果有）
                related_ip_image_id = None
                if include_ip_image:
                    try:
                        from api.models import IPImage
                        ip_image = IPImage.objects.filter(user=request.user).first()
                        if ip_image:
                            related_ip_image_id = ip_image.id
                    except:
                        pass

                # 保存到素材库
                from api.utils.image_storage import save_to_media_library
                save_to_media_library(
                    user=request.user,
                    media_type='content_image',
                    original_url=image_url,
                    prompt=content[:500],
                    related_ip_image_id=related_ip_image_id
                )

                return Response({
                    'status': 'success',
                    'image_url': image_url,
                    'prompt': used_prompt,
                    'message': '配图生成成功'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': '生成失败，请重试'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"文案配图生成错误: {str(e)}")
            # 记录失败情况
            GeminiUsage.objects.create(
                user=request.user,
                generation_type='content_image',
                prompt=content[:500],
                success=False,
                error_message=str(e)[:500]
            )
            return Response({
                'status': 'error',
                'message': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"处理文案配图请求错误: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'请求处理失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ip_image_v2(request):
    """
    使用 Gemini REST API 生成图片（新版本）

    支持两种模式:
    1. IP形象生成: 上传照片 + 提示语
    2. 文案配图生成: 文案内容

    IP形象请求参数:
    - image: 用户上传的照片文件
    - prompt: 创意提示语
    - aspect_ratio: 纵横比（可选，默认1:1）

    文案配图请求参数:
    - content: 文案内容
    - image_index: 图片索引（用于生成不同风格）
    - include_ip_image: 是否包含IP形象（可选）
    - ip_image_url: IP形象URL（可选）

    返回:
    - status: success/error
    - image_url: 生成的图片URL
    - message: 提示信息
    """
    try:
        # 检查用户额度
        quota, created = UserQuota.objects.get_or_create(user=request.user)
        if not quota.has_quota():
            return Response({
                'status': 'error',
                'message': '您的可用次数不足，请购买次数后再试',
                'available_quota': quota.available_quota
            }, status=status.HTTP_403_FORBIDDEN)

        # 判断是IP形象生成还是文案配图生成
        uploaded_image = request.FILES.get('image')
        content = request.data.get('content', '')

        # 如果有 content 参数，则是文案配图生成
        if content:
            return _handle_content_image_generation(request, quota)

        # 否则是 IP 形象生成
        prompt = request.data.get('prompt', '')
        aspect_ratio = request.data.get('aspect_ratio', '1:1')

        if not uploaded_image:
            return Response({
                'status': 'error',
                'message': '请上传照片'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not prompt.strip():
            return Response({
                'status': 'error',
                'message': '请输入提示语'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证纵横比
        if aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
            return Response({
                'status': 'error',
                'message': f'不支持的纵横比 {aspect_ratio}。支持: {", ".join(SUPPORTED_ASPECT_RATIOS)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if uploaded_image.content_type not in allowed_types:
            return Response({
                'status': 'error',
                'message': '只支持 JPG, PNG, WEBP 格式的图片'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小 (限制10MB)
        if uploaded_image.size > 10 * 1024 * 1024:
            return Response({
                'status': 'error',
                'message': '图片大小不能超过10MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"收到IP形象生成请求(V2): user={request.user.username}, prompt={prompt}, aspect_ratio={aspect_ratio}")

        # 读取上传的图片数据
        image_data = uploaded_image.read()
        mime_type = uploaded_image.content_type

        # 获取API配置 - V2接口使用专用的IP_IMAGE_API_KEY
        gemini_api_key = os.getenv('IP_IMAGE_API_KEY')
        gemini_api_url = os.getenv('GEMINI_API_URL', 'https://api.apiyi.com/v1beta/models/gemini-3-pro-image-preview:generateContent')

        if not gemini_api_key:
            return Response({
                'status': 'error',
                'message': '暂未配置IP形象生成服务，请联系管理员配置 IP_IMAGE_API_KEY 环境变量'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            generated_image_path = generate_with_gemini_rest_api(
                image_data,
                mime_type,
                prompt,
                aspect_ratio,
                gemini_api_key,
                gemini_api_url,
                request.user.username
            )

            if generated_image_path:
                # 生成访问URL - 强制使用 https
                image_url = f"https://{request.get_host()}/media/ip_images/{os.path.basename(generated_image_path)}"

                # 扣减用户额度
                quota.consume_quota()
                logger.info(f"用户 {request.user.username} 消耗1次额度，剩余: {quota.available_quota}次")

                # 记录成功的调用统计
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='ip_image',
                    prompt=f"{prompt} (纵横比: {aspect_ratio})",
                    success=True
                )

                # 保存到素材库
                from api.utils.image_storage import save_to_media_library
                save_to_media_library(
                    user=request.user,
                    media_type='ip_image',
                    original_url=image_url,
                    prompt=f"{prompt} (纵横比: {aspect_ratio})"
                )

                logger.info(f"成功使用 Gemini REST API 生成IP形象: {image_url}")
                return Response({
                    'status': 'success',
                    'image_url': image_url,
                    'message': 'IP形象生成成功',
                    'method': 'gemini_rest_api_v2',
                    'aspect_ratio': aspect_ratio,
                    'remaining_quota': quota.available_quota
                })
            else:
                # 记录失败的调用统计
                GeminiUsage.objects.create(
                    user=request.user,
                    generation_type='ip_image',
                    prompt=prompt,
                    success=False,
                    error_message='未返回图片数据'
                )
                return Response({
                    'status': 'error',
                    'message': '生成失败，未返回图片数据'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # 记录失败的调用统计
            GeminiUsage.objects.create(
                user=request.user,
                generation_type='ip_image',
                prompt=prompt,
                success=False,
                error_message=str(e)
            )
            logger.error(f"Gemini REST API 生成失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'生成失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"生成IP形象错误(V2): {str(e)}")
        return Response({
            'status': 'error',
            'message': f'生成失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_with_gemini_rest_api(image_data, mime_type, prompt, aspect_ratio, api_key, api_url, username):
    """
    使用 Gemini REST API 生成IP形象图片

    参数:
    - image_data: 用户上传的图片二进制数据
    - mime_type: 图片的MIME类型 (如 image/jpeg)
    - prompt: 用户的创意提示语
    - aspect_ratio: 纵横比（如 "1:1", "16:9" 等）
    - api_key: Gemini API密钥
    - api_url: Gemini API地址
    - username: 用户名（用于生成唯一文件名）

    返回:
    - 生成的图片文件路径
    """
    try:
        # 将图片编码为 base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 构建请求数据（Google 原生格式）
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64
                        }
                    }
                ]
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio
                }
            }
        }

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        logger.info(f"开始使用 Gemini REST API 生成IP形象，提示语: {prompt}, 纵横比: {aspect_ratio}")

        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            error_msg = f"API 请求失败，状态码: {response.status_code}, 响应: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        # 解析响应
        result = response.json()

        # 提取图片数据
        if "candidates" not in result or len(result["candidates"]) == 0:
            raise Exception("未找到图片数据")

        candidate = result["candidates"][0]
        if "content" not in candidate or "parts" not in candidate["content"]:
            raise Exception("响应格式错误")

        parts = candidate["content"]["parts"]
        output_image_data = None

        for part in parts:
            if "inlineData" in part and "data" in part["inlineData"]:
                output_image_data = part["inlineData"]["data"]
                break

        if not output_image_data:
            raise Exception("未找到图片数据")

        # 解码图片数据
        decoded_data = base64.b64decode(output_image_data)

        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ip_{username}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(IP_IMAGE_DIR, filename)

        # 保存图片
        with open(output_path, 'wb') as f:
            f.write(decoded_data)

        file_size = len(decoded_data) / 1024  # KB
        logger.info(f"图片已保存: {output_path}, 大小: {file_size:.2f} KB")

        return output_path

    except requests.exceptions.Timeout:
        logger.error("请求超时（120秒）")
        raise Exception("请求超时，请稍后重试")
    except requests.exceptions.ConnectionError:
        logger.error("网络连接错误")
        raise Exception("网络连接错误，请检查网络")
    except Exception as e:
        logger.error(f"Gemini REST API 调用错误: {str(e)}")
        raise


def generate_content_image_with_rest_api(content, image_index, api_key, api_url, username, include_ip_image=False, ip_image_url='', aspect_ratio='9:16'):
    """
    使用 Gemini REST API 根据文案生成配图

    参数:
    - content: 文案内容
    - image_index: 图片索引（用于生成不同风格的配图）
    - api_key: Gemini API密钥
    - api_url: Gemini API地址
    - username: 用户名（用于生成唯一文件名）
    - include_ip_image: 是否包含IP形象
    - ip_image_url: IP形象图片URL
    - aspect_ratio: 纵横比（默认9:16）

    返回:
    - (生成的图片文件路径, 使用的提示语)
    """
    try:
        # 定义不同风格的提示语模板
        style_templates = [
            "现代简约风格",
            "温馨自然风格",
            "专业商务风格",
            "活泼可爱风格",
            "典雅艺术风格"
        ]

        style = style_templates[(image_index - 1) % len(style_templates)]

        # 构建基础提示语
        base_prompt = f"""请根据以下文案内容生成一张配图，风格：{style}

文案内容：{content}

要求：
1. 图片要体现文案的核心主题和情感
2. 画面简洁明了，重点突出
3. 色彩搭配协调，符合{style}的特点
4. 适合作为社交媒体配图使用"""

        # 处理IP形象图片（如果需要包含）
        parts = [{"text": base_prompt}]

        if include_ip_image and ip_image_url:
            try:
                logger.info(f"下载用户IP形象用于文案配图: {ip_image_url}")

                # 下载IP形象图片
                response = requests.get(ip_image_url, timeout=10)
                response.raise_for_status()

                # 将IP形象编码为 base64
                ip_image_base64 = base64.b64encode(response.content).decode('utf-8')

                # 添加IP形象到请求中
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": ip_image_base64
                    }
                })

                # 更新提示语，要求包含IP形象
                parts[0]["text"] = base_prompt + "\n\n5. 请将提供的人物形象自然地融入到画面中"

                logger.info("成功加载用户IP形象到文案配图请求中")
            except Exception as e:
                logger.warning(f"加载IP形象失败，将生成不包含IP形象的配图: {str(e)}")
                # 如果加载失败，继续生成不包含IP形象的图片

        # 构建请求数据
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio  # 使用前端传递的纵横比
                }
            }
        }

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        logger.info(f"开始使用 Gemini REST API 生成文案配图，索引: {image_index}, 风格: {style}")

        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            error_msg = f"API 请求失败，状态码: {response.status_code}, 响应: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        # 解析响应
        result = response.json()

        # 提取图片数据
        if "candidates" not in result or len(result["candidates"]) == 0:
            raise Exception("未找到图片数据")

        candidate = result["candidates"][0]
        if "content" not in candidate or "parts" not in candidate["content"]:
            raise Exception("响应格式错误")

        parts = candidate["content"]["parts"]
        output_image_data = None

        for part in parts:
            if "inlineData" in part and "data" in part["inlineData"]:
                output_image_data = part["inlineData"]["data"]
                break

        if not output_image_data:
            raise Exception("未找到图片数据")

        # 解码图片数据
        decoded_data = base64.b64decode(output_image_data)

        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"content_{username}_{timestamp}_{image_index}_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(IP_IMAGE_DIR, filename)

        # 保存图片
        with open(output_path, 'wb') as f:
            f.write(decoded_data)

        file_size = len(decoded_data) / 1024  # KB
        logger.info(f"文案配图已保存: {output_path}, 大小: {file_size:.2f} KB")

        return output_path, base_prompt

    except requests.exceptions.Timeout:
        logger.error("请求超时（120秒）")
        raise Exception("请求超时，请稍后重试")
    except requests.exceptions.ConnectionError:
        logger.error("网络连接错误")
        raise Exception("网络连接错误，请检查网络")
    except Exception as e:
        logger.error(f"文案配图生成错误: {str(e)}")
        raise
