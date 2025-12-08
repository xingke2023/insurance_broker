"""
素材库管理视图
提供用户素材库的查询、删除、上传等功能
"""
import logging
import os
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import MediaLibrary
from .utils.image_storage import delete_media_file

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_media_library(request):
    """
    获取用户的素材库列表

    查询参数:
    - media_type: 筛选素材类型 ('ip_image' 或 'content_image')
    - is_favorite: 筛选收藏状态 (true/false)
    - page: 页码（默认1）
    - page_size: 每页数量（默认20）
    """
    try:
        # 获取查询参数
        media_type = request.GET.get('media_type', '')
        is_favorite = request.GET.get('is_favorite', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        # 构建查询
        queryset = MediaLibrary.objects.filter(user=request.user)

        # 按类型筛选
        if media_type in ['ip_image', 'content_image']:
            queryset = queryset.filter(media_type=media_type)

        # 按收藏状态筛选
        if is_favorite.lower() == 'true':
            queryset = queryset.filter(is_favorite=True)

        # 获取总数
        total_count = queryset.count()

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        media_list = queryset[start:end]

        # 序列化数据
        data = []
        for media in media_list:
            # 构建访问URL
            if media.local_path:
                media_url = f"https://{request.get_host()}/media/{media.local_path}"
            else:
                media_url = media.original_url

            data.append({
                'id': media.id,
                'media_type': media.media_type,
                'media_type_display': media.get_media_type_display(),
                'url': media_url,
                'original_url': media.original_url,
                'prompt': media.prompt,
                'width': media.width,
                'height': media.height,
                'file_size': media.file_size,
                'is_favorite': media.is_favorite,
                'related_ip_image_id': media.related_ip_image_id,
                'created_at': media.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return Response({
            'status': 'success',
            'data': {
                'items': data,
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })

    except Exception as e:
        logger.error(f"获取素材库失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'获取素材库失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_media_detail(request, media_id):
    """
    获取单个素材的详细信息
    """
    try:
        media = MediaLibrary.objects.get(id=media_id, user=request.user)

        # 构建访问URL
        if media.local_path:
            media_url = f"https://{request.get_host()}/media/{media.local_path}"
        else:
            media_url = media.original_url

        return Response({
            'status': 'success',
            'data': {
                'id': media.id,
                'media_type': media.media_type,
                'media_type_display': media.get_media_type_display(),
                'url': media_url,
                'original_url': media.original_url,
                'prompt': media.prompt,
                'width': media.width,
                'height': media.height,
                'file_size': media.file_size,
                'is_favorite': media.is_favorite,
                'related_ip_image_id': media.related_ip_image_id,
                'created_at': media.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': media.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        })

    except MediaLibrary.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '素材不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"获取素材详情失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'获取素材详情失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, media_id):
    """
    切换素材的收藏状态
    """
    try:
        media = MediaLibrary.objects.get(id=media_id, user=request.user)
        media.is_favorite = not media.is_favorite
        media.save()

        return Response({
            'status': 'success',
            'message': '收藏状态已更新',
            'is_favorite': media.is_favorite
        })

    except MediaLibrary.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '素材不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"切换收藏状态失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'操作失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_media(request, media_id):
    """
    删除单个素材
    """
    try:
        media = MediaLibrary.objects.get(id=media_id, user=request.user)

        # 删除本地文件
        if media.local_path:
            delete_media_file(media.local_path)

        # 删除数据库记录
        media.delete()

        return Response({
            'status': 'success',
            'message': '素材已删除'
        })

    except MediaLibrary.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '素材不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"删除素材失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_delete_media(request):
    """
    批量删除素材

    请求体:
    {
        "media_ids": [1, 2, 3, ...]
    }
    """
    try:
        media_ids = request.data.get('media_ids', [])

        if not media_ids or not isinstance(media_ids, list):
            return Response({
                'status': 'error',
                'message': '请提供有效的素材ID列表'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 查询要删除的素材
        media_list = MediaLibrary.objects.filter(
            id__in=media_ids,
            user=request.user
        )

        deleted_count = 0
        for media in media_list:
            # 删除本地文件
            if media.local_path:
                delete_media_file(media.local_path)
            deleted_count += 1

        # 批量删除数据库记录
        media_list.delete()

        return Response({
            'status': 'success',
            'message': f'成功删除 {deleted_count} 个素材'
        })

    except Exception as e:
        logger.error(f"批量删除素材失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_media_stats(request):
    """
    获取用户素材库统计信息
    """
    try:
        # 总数统计
        total_count = MediaLibrary.objects.filter(user=request.user).count()

        # 按类型统计
        ip_image_count = MediaLibrary.objects.filter(
            user=request.user,
            media_type='ip_image'
        ).count()

        content_image_count = MediaLibrary.objects.filter(
            user=request.user,
            media_type='content_image'
        ).count()

        # 收藏数量
        favorite_count = MediaLibrary.objects.filter(
            user=request.user,
            is_favorite=True
        ).count()

        # 总存储大小
        from django.db.models import Sum
        total_size = MediaLibrary.objects.filter(
            user=request.user
        ).aggregate(Sum('file_size'))['file_size__sum'] or 0

        return Response({
            'status': 'success',
            'data': {
                'total_count': total_count,
                'ip_image_count': ip_image_count,
                'content_image_count': content_image_count,
                'favorite_count': favorite_count,
                'total_size': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        })

    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'获取统计信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_media(request):
    """
    上传图片到素材库

    请求参数:
    - image: 图片文件 (必需)
    - media_type: 素材类型 (可选，默认 'content_image')
    - prompt: 描述/标题 (可选)
    """
    try:
        # 获取上传的图片
        uploaded_image = request.FILES.get('image')
        if not uploaded_image:
            return Response({
                'status': 'error',
                'message': '请上传图片文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
        if uploaded_image.content_type not in allowed_types:
            return Response({
                'status': 'error',
                'message': '只支持 JPG, PNG, WEBP, GIF 格式的图片'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小 (限制10MB)
        if uploaded_image.size > 10 * 1024 * 1024:
            return Response({
                'status': 'error',
                'message': '图片大小不能超过10MB'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取其他参数
        media_type = request.data.get('media_type', 'content_image')
        prompt = request.data.get('prompt', '')

        # 验证媒体类型
        if media_type not in ['ip_image', 'content_image']:
            media_type = 'content_image'

        # 读取图片数据
        image_data = uploaded_image.read()

        # 使用PIL获取图像尺寸
        image = Image.open(BytesIO(image_data))
        width, height = image.size

        # 生成文件名和路径
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_ext = uploaded_image.name.split('.')[-1].lower()
        filename = f"user_{request.user.id}_{unique_id}_{timestamp}.{file_ext}"

        # 确定子目录
        subdir = 'ip_images' if media_type == 'ip_image' else 'content_images'

        # 相对路径 (用于数据库)
        relative_path = os.path.join('generated_images', subdir, filename)

        # 绝对路径 (用于文件系统)
        media_root = os.path.join(settings.BASE_DIR, 'media')
        absolute_path = os.path.join(media_root, 'generated_images', subdir, filename)

        # 确保目录存在
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        # 保存文件
        with open(absolute_path, 'wb') as f:
            f.write(image_data)

        # 创建素材库记录
        media = MediaLibrary.objects.create(
            user=request.user,
            media_type=media_type,
            original_url='',  # 用户上传的图片没有原始URL
            local_path=relative_path,
            prompt=prompt,
            width=width,
            height=height,
            file_size=uploaded_image.size
        )

        # 生成访问URL
        media_url = f"https://{request.get_host()}/media/{relative_path}"

        logger.info(f"用户 {request.user.username} 上传素材成功: {filename}")

        return Response({
            'status': 'success',
            'message': '上传成功',
            'data': {
                'id': media.id,
                'url': media_url,
                'media_type': media.media_type,
                'media_type_display': media.get_media_type_display(),
                'width': width,
                'height': height,
                'file_size': uploaded_image.size,
                'created_at': media.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        logger.error(f"上传素材失败: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'上传失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
