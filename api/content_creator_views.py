import os
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from google import genai
from google.genai import types
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# 配置 Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# 创建 Gemini 客户端
def get_gemini_client():
    if not GEMINI_API_KEY:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


def extract_video_id(url):
    """
    从 YouTube URL 中提取视频 ID
    支持多种格式:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    """
    try:
        parsed_url = urlparse(url)

        # 处理 youtu.be 短链接
        if parsed_url.netloc in ['youtu.be', 'www.youtu.be']:
            return parsed_url.path[1:].split('?')[0]

        # 处理标准 YouTube URL
        if parsed_url.netloc in ['youtube.com', 'www.youtube.com', 'm.youtube.com']:
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                return query_params.get('v', [None])[0]
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2].split('?')[0]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2].split('?')[0]
            elif parsed_url.path.startswith('/shorts/'):
                return parsed_url.path.split('/')[2].split('?')[0]

        return None
    except Exception as e:
        logger.error(f"提取视频ID失败: {str(e)}")
        return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_subtitle(request):
    """
    使用 Gemini API 直接从 YouTube 视频中提取字幕内容
    """
    try:
        video_url = request.data.get('video_url', '')

        if not video_url:
            return Response({
                'code': 400,
                'message': '请提供视频链接'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 提取视频 ID (用于返回)
        video_id = extract_video_id(video_url)
        if not video_id:
            return Response({
                'code': 400,
                'message': '无效的 YouTube 视频链接'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"开始使用 Gemini 提取视频字幕: video_id={video_id}, url={video_url}")

        # 获取 Gemini 客户端
        client = get_gemini_client()
        if not client:
            return Response({
                'code': 500,
                'message': 'Gemini API 未配置,请设置 GEMINI_API_KEY 环境变量'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            model = "gemini-2.0-flash-exp"

            # 构建提示词 - 让 Gemini 直接访问视频并提取字幕
            prompt_text = f"""请分析这个 YouTube 视频并提取完整的字幕内容。

视频链接: {video_url}

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

            # 配置工具 - 启用 URL 上下文以访问 YouTube 视频
            tools = [
                types.Tool(url_context=types.UrlContext()),
            ]

            # 生成内容配置
            generate_content_config = types.GenerateContentConfig(
                temperature=0.7,  # 降低温度以获得更准确的提取
                tools=tools,
            )

            # 收集流式响应
            subtitle_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    subtitle_text += chunk.text

            if not subtitle_text or len(subtitle_text) < 10:
                logger.error(f"Gemini 返回的字幕内容为空或过短: {subtitle_text}")
                return Response({
                    'code': 404,
                    'message': '无法提取视频字幕,该视频可能没有字幕或无法访问'
                }, status=status.HTTP_404_NOT_FOUND)

            logger.info(f"成功使用 Gemini 提取字幕，长度: {len(subtitle_text)}")

            return Response({
                'code': 200,
                'message': '字幕提取成功',
                'data': {
                    'subtitle': subtitle_text.strip(),
                    'video_id': video_id,
                    'method': 'gemini_url_context'
                }
            })

        except Exception as e:
            logger.error(f"Gemini 提取字幕失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'无法提取视频字幕: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"提取字幕错误: {str(e)}")
        return Response({
            'code': 500,
            'message': f'提取字幕失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_content_with_context(request):
    """
    使用 Gemini API 生成内容，支持 URL 上下文和 Google 搜索
    """
    try:
        video_url = request.data.get('video_url', '')
        user_prompt = request.data.get('prompt', '')
        use_url_context = request.data.get('use_url_context', True)
        use_google_search = request.data.get('use_google_search', False)

        if not video_url and not user_prompt:
            return Response({
                'code': 400,
                'message': '请提供视频链接或提示内容'
            }, status=status.HTTP_400_BAD_REQUEST)

        client = get_gemini_client()
        if not client:
            return Response({
                'code': 500,
                'message': 'Gemini API 未配置'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"开始生成内容: video_url={video_url}, use_url_context={use_url_context}, use_google_search={use_google_search}")

        # 构建提示内容
        if video_url and not user_prompt:
            prompt_text = f"请分析这个 YouTube 视频并提供详细的摘要: {video_url}"
        elif video_url and user_prompt:
            prompt_text = f"{user_prompt}\n\n视频链接: {video_url}"
        else:
            prompt_text = user_prompt

        model = "gemini-2.0-flash-exp"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt_text),
                ],
            ),
        ]

        # 配置工具
        tools = []
        if use_url_context:
            tools.append(types.Tool(url_context=types.UrlContext()))
        if use_google_search:
            tools.append(types.Tool(google_search=types.GoogleSearch()))

        # 生成内容配置
        generate_content_config = types.GenerateContentConfig(
            temperature=1.0,
            tools=tools if tools else None,
        )

        # 收集流式响应
        result_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                result_text += chunk.text

        logger.info(f"成功生成内容，长度: {len(result_text)}")

        return Response({
            'code': 200,
            'message': '内容生成成功',
            'data': {
                'content': result_text,
            }
        })

    except Exception as e:
        logger.error(f"生成内容错误: {str(e)}")
        return Response({
            'code': 500,
            'message': f'生成内容失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
