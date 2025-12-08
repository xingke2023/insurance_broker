"""
视频生成器视图
根据字幕使用DeepSeek生成场景提示词
创建视频（代理到视频生成服务）
管理视频项目（CRUD）
"""
import logging
import os
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import VideoProject

logger = logging.getLogger(__name__)

# 视频生成服务地址
VIDEO_SERVICE_URL = os.getenv('VIDEO_SERVICE_URL', 'http://localhost:8067')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_scene_prompts(request):
    """
    根据字幕使用DeepSeek生成场景图提示词

    请求参数:
    - subtitles: 字幕内容（字符串）

    返回:
    - prompts: 场景提示词列表
    """
    try:
        subtitles = request.data.get('subtitles', '')

        if not subtitles.strip():
            return Response({
                'status': 'error',
                'message': '字幕内容不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取DeepSeek API密钥
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')

        if not deepseek_api_key:
            return Response({
                'status': 'error',
                'message': '未配置DeepSeek API密钥，请联系管理员'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 构建提示词
        system_prompt = """你是一个专业的视频场景设计师。根据用户提供的字幕内容，将字幕合理分组，为每组字幕生成一个对应的场景图提示词。

要求：
1. 将字幕按照内容相关性分组，每组包含2-5句字幕
2. 为每组字幕生成一个详细的场景描述提示词，提示词要能够涵盖这组字幕的整体内容
3. 提示词要具体、生动，包含场景、氛围、色彩、构图等元素
4. 提示词要适合用于AI图像生成（如Stable Diffusion, Midjourney等）
5. 每个提示词独立一行
6. 不要添加编号或其他前缀
7. 提示词用中文表达

示例：
输入字幕：
春天到了
万物复苏
大地变绿了
花园里开满了鲜花
蜜蜂在忙碌采蜜
蝴蝶在花间飞舞

输出提示词：
春天的清晨，阳光透过薄雾洒在刚刚苏醒的大地上，嫩绿的新芽从泥土中探出头来，树木发出新枝，草地铺满绿色，暖色调，生机勃勃的氛围
五彩缤纷的花园，玫瑰、郁金香、向日葵竞相开放，蜜蜂在花丛中忙碌采蜜，蝴蝶在花间翩翩起舞，背景是湛蓝的天空和白云，近景特写，色彩饱和鲜艳"""

        user_prompt = f"请为以下字幕生成场景图提示词：\n\n{subtitles}"

        # 调用DeepSeek API
        try:
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {deepseek_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 2000
                },
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # 解析返回的提示词
            generated_text = result['choices'][0]['message']['content']

            # 按行分割，过滤空行
            prompts = [line.strip() for line in generated_text.split('\n') if line.strip()]

            logger.info(f"用户 {request.user.username} 生成了 {len(prompts)} 个场景提示词")

            return Response({
                'status': 'success',
                'prompts': prompts,
                'count': len(prompts)
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'DeepSeek API调用失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"生成场景提示词失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'生成失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_video(request):
    """
    创建视频（代理到视频生成服务）

    请求参数:
    - images: 场景图片列表
      [
        {
          "image_url": "图片URL",
          "text": "字幕文本"
        },
        ...
      ]
    - duration: 每个场景的时长（秒），默认3.0
    - voice: 语音类型，默认"zh-CN-XiaoxiaoNeural"

    返回:
    - 视频生成服务的响应
    """
    try:
        # 获取请求数据
        images = request.data.get('images', [])
        duration = request.data.get('duration', 3.0)
        voice = request.data.get('voice', 'zh-CN-XiaoxiaoNeural')

        if not images:
            return Response({
                'status': 'error',
                'message': '场景列表不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证每个场景
        for idx, image in enumerate(images):
            if not image.get('image_url'):
                return Response({
                    'status': 'error',
                    'message': f'场景 {idx + 1} 缺少图片URL'
                }, status=status.HTTP_400_BAD_REQUEST)
            if not image.get('text'):
                return Response({
                    'status': 'error',
                    'message': f'场景 {idx + 1} 缺少字幕文本'
                }, status=status.HTTP_400_BAD_REQUEST)

        # 构建代理请求
        proxy_data = {
            'images': images,
            'duration': duration,
            'voice': voice
        }

        logger.info(f"用户 {request.user.username} 创建视频，共 {len(images)} 个场景")

        # 发送请求到视频生成服务
        try:
            response = requests.post(
                f'{VIDEO_SERVICE_URL}/api/create',
                json=proxy_data,
                timeout=300  # 5分钟超时
            )

            # 返回视频服务的响应
            return Response(
                response.json(),
                status=response.status_code
            )

        except requests.exceptions.Timeout:
            logger.error("视频生成服务超时")
            return Response({
                'status': 'error',
                'message': '视频生成超时，请稍后重试'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)

        except requests.exceptions.ConnectionError:
            logger.error("无法连接到视频生成服务")
            return Response({
                'status': 'error',
                'message': '无法连接到视频生成服务'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except requests.exceptions.RequestException as e:
            logger.error(f"视频生成服务请求失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'视频生成服务请求失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"创建视频失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'创建视频失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== 视频项目管理API ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_projects(request):
    """获取用户的视频项目列表"""
    try:
        projects = VideoProject.objects.filter(user=request.user)

        projects_data = [{
            'id': p.id,
            'title': p.title,
            'status': p.status,
            'status_display': p.get_status_display(),
            'scene_count': p.scene_count,
            'taskid': p.taskid,
            'video_url': p.video_url,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat(),
        } for p in projects]

        return Response({
            'status': 'success',
            'data': projects_data
        })
    except Exception as e:
        logger.error(f"获取视频项目列表失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_project_detail(request, project_id):
    """获取视频项目详情"""
    try:
        project = get_object_or_404(VideoProject, id=project_id, user=request.user)

        data = {
            'id': project.id,
            'title': project.title,
            'subtitles': project.subtitles,
            'scene_count': project.scene_count,
            'duration': project.duration,
            'voice': project.voice,
            'scenes_data': project.scenes_data,
            'status': project.status,
            'status_display': project.get_status_display(),
            'taskid': project.taskid,
            'video_url': project.video_url,
            'error_message': project.error_message,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
        }

        return Response({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        logger.error(f"获取视频项目详情失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_video_project(request):
    """创建新的视频项目"""
    try:
        title = request.data.get('title', '未命名视频')
        subtitles = request.data.get('subtitles', '')
        scenes_data = request.data.get('scenes_data', [])
        duration = request.data.get('duration', 3.0)
        voice = request.data.get('voice', 'zh-CN-XiaoxiaoNeural')
        project_status = request.data.get('status', 'draft')
        taskid = request.data.get('taskid', None)

        project = VideoProject.objects.create(
            user=request.user,
            title=title,
            subtitles=subtitles,
            scene_count=len(scenes_data),
            duration=duration,
            voice=voice,
            scenes_data=scenes_data,
            status=project_status,
            taskid=taskid
        )

        logger.info(f"用户 {request.user.username} 创建了视频项目: {project.id}, status={project_status}, taskid={taskid}")

        return Response({
            'status': 'success',
            'data': {
                'id': project.id,
                'title': project.title,
                'status': project.status,
                'taskid': project.taskid
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"创建视频项目失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_video_project(request, project_id):
    """更新视频项目"""
    try:
        project = get_object_or_404(VideoProject, id=project_id, user=request.user)

        if 'title' in request.data:
            project.title = request.data['title']
        if 'subtitles' in request.data:
            project.subtitles = request.data['subtitles']
        if 'scenes_data' in request.data:
            project.scenes_data = request.data['scenes_data']
            project.scene_count = len(request.data['scenes_data'])
        if 'duration' in request.data:
            project.duration = request.data['duration']
        if 'voice' in request.data:
            project.voice = request.data['voice']
        if 'status' in request.data:
            project.status = request.data['status']
        if 'taskid' in request.data:
            project.taskid = request.data['taskid']
        if 'video_url' in request.data:
            project.video_url = request.data['video_url']
        if 'error_message' in request.data:
            project.error_message = request.data['error_message']

        project.save()

        logger.info(f"用户 {request.user.username} 更新了视频项目: {project.id}")

        return Response({
            'status': 'success',
            'data': {
                'id': project.id,
                'title': project.title,
                'status': project.status
            }
        })
    except Exception as e:
        logger.error(f"更新视频项目失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_video_project(request, project_id):
    """删除视频项目"""
    try:
        project = get_object_or_404(VideoProject, id=project_id, user=request.user)
        project_title = project.title
        project.delete()

        logger.info(f"用户 {request.user.username} 删除了视频项目: {project_title}")

        return Response({
            'status': 'success',
            'message': '删除成功'
        })
    except Exception as e:
        logger.error(f"删除视频项目失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def video_proxy_download(request):
    """
    视频下载反向代理接口

    将外部视频服务的下载请求代理到本地
    前端访问: /api/video/download?task_id=xxx
    实际代理到: {VIDEO_SERVICE_URL}/api/download?task_id=xxx

    参数:
    - task_id: 视频任务ID

    返回:
    - 视频文件流
    """
    try:
        task_id = request.GET.get('task_id')

        if not task_id:
            return Response({
                'status': 'error',
                'message': 'task_id参数必填'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 构建外部服务URL
        external_url = f'{VIDEO_SERVICE_URL}/api/download?task_id={task_id}'

        logger.info(f"代理视频下载请求: task_id={task_id}")

        try:
            # 使用流式请求获取视频
            response = requests.get(external_url, stream=True, timeout=60)

            if response.status_code != 200:
                logger.error(f"视频下载失败: {response.status_code}")
                return Response({
                    'status': 'error',
                    'message': '视频下载失败'
                }, status=response.status_code)

            # 创建Django HttpResponse并流式传输视频
            from django.http import StreamingHttpResponse

            django_response = StreamingHttpResponse(
                response.iter_content(chunk_size=8192),
                content_type=response.headers.get('Content-Type', 'video/mp4')
            )

            # 复制相关的响应头
            if 'Content-Disposition' in response.headers:
                django_response['Content-Disposition'] = response.headers['Content-Disposition']
            if 'Content-Length' in response.headers:
                django_response['Content-Length'] = response.headers['Content-Length']

            return django_response

        except requests.exceptions.Timeout:
            logger.error("视频下载超时")
            return Response({
                'status': 'error',
                'message': '视频下载超时'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)

        except requests.exceptions.ConnectionError:
            logger.error("无法连接到视频服务")
            return Response({
                'status': 'error',
                'message': '无法连接到视频服务'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except requests.exceptions.RequestException as e:
            logger.error(f"视频下载请求失败: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'视频下载失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"视频代理下载失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'下载失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def video_completion_callback(request):
    """
    视频生成完成回调接口

    视频制作服务器完成任务后调用此接口通知任务完成

    请求参数:
    - taskid: 任务ID（必填）
    - video_url: 生成的视频URL（可选）
    - status: 任务状态，success或failed（可选，默认success）
    - error_message: 错误信息（可选）

    返回:
    - status: success/error
    - message: 消息
    """
    try:
        taskid = request.data.get('taskid')
        video_url = request.data.get('video_url')
        callback_status = request.data.get('status', 'success')
        error_message = request.data.get('error_message')

        if not taskid:
            return Response({
                'status': 'error',
                'message': 'taskid参数必填'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 通过taskid查找项目
        try:
            project = VideoProject.objects.get(taskid=taskid)
        except VideoProject.DoesNotExist:
            logger.warning(f"未找到taskid对应的项目: {taskid}")
            return Response({
                'status': 'error',
                'message': f'未找到taskid对应的项目: {taskid}'
            }, status=status.HTTP_404_NOT_FOUND)

        # 根据回调状态更新项目
        if callback_status == 'success':
            project.status = 'completed'
            if video_url:
                # 将外部视频URL转换为代理URL
                # 外部格式: http://localhost:8067/api/download?task_id=xxx
                # 转换为: /api/video/download?task_id=xxx
                import re
                from urllib.parse import urlparse, parse_qs

                try:
                    parsed = urlparse(video_url)
                    query_params = parse_qs(parsed.query)
                    task_id = query_params.get('task_id', [taskid])[0]

                    # 使用代理URL
                    project.video_url = f'/api/video/download?task_id={task_id}'
                    logger.info(f"转换视频URL: {video_url} -> {project.video_url}")
                except Exception as e:
                    logger.warning(f"解析视频URL失败，使用原始URL: {e}")
                    project.video_url = video_url

            project.error_message = None
            logger.info(f"视频项目 {project.id} 生成成功，taskid: {taskid}")
        else:
            project.status = 'failed'
            project.error_message = error_message or '视频生成失败'
            logger.warning(f"视频项目 {project.id} 生成失败，taskid: {taskid}, error: {error_message}")

        project.save()

        return Response({
            'status': 'success',
            'message': '回调处理成功',
            'data': {
                'project_id': project.id,
                'project_status': project.status
            }
        })

    except Exception as e:
        logger.error(f"视频完成回调处理失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'回调处理失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
