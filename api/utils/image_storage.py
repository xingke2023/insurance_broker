"""
图像存储工具模块
处理从Gemini下载图像并保存到本地服务器
"""
import os
import requests
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.conf import settings


def download_and_save_image(image_url, media_type, user_id):
    """
    从URL下载图像并保存到本地

    Args:
        image_url: Gemini生成的图像URL
        media_type: 媒体类型 ('ip_image' 或 'content_image')
        user_id: 用户ID

    Returns:
        dict: {
            'success': bool,
            'local_path': str,  # 相对路径
            'width': int,
            'height': int,
            'file_size': int,
            'error': str  # 如果失败
        }
    """
    try:
        # 1. 下载图像
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # 2. 获取图像数据
        image_data = response.content
        file_size = len(image_data)

        # 3. 使用PIL获取图像尺寸
        image = Image.open(BytesIO(image_data))
        width, height = image.size

        # 4. 生成文件名和路径
        # 格式: user_{user_id}_{uuid}_{timestamp}.png
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"user_{user_id}_{unique_id}_{timestamp}.png"

        # 确定子目录
        subdir = 'ip_images' if media_type == 'ip_image' else 'content_images'

        # 相对路径 (用于数据库)
        relative_path = os.path.join('generated_images', subdir, filename)

        # 绝对路径 (用于文件系统)
        media_root = os.path.join(settings.BASE_DIR, 'media')
        absolute_path = os.path.join(media_root, 'generated_images', subdir, filename)

        # 5. 确保目录存在
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        # 6. 保存文件
        with open(absolute_path, 'wb') as f:
            f.write(image_data)

        return {
            'success': True,
            'local_path': relative_path,
            'width': width,
            'height': height,
            'file_size': file_size
        }

    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'下载图像失败: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'保存图像失败: {str(e)}'
        }


def save_to_media_library(user, media_type, original_url, prompt='', related_ip_image_id=None):
    """
    下载图像并保存到素材库

    Args:
        user: User对象
        media_type: 'ip_image' 或 'content_image'
        original_url: Gemini生成的图像URL
        prompt: 提示语或文案
        related_ip_image_id: 关联的IP形象ID (仅对content_image有效)

    Returns:
        MediaLibrary对象或None
    """
    from api.models import MediaLibrary

    # 下载并保存图像
    result = download_and_save_image(original_url, media_type, user.id)

    if not result['success']:
        print(f"❌ 下载图像失败: {result.get('error')}")
        return None

    # 创建素材库记录
    try:
        media = MediaLibrary.objects.create(
            user=user,
            media_type=media_type,
            original_url=original_url,
            local_path=result['local_path'],
            prompt=prompt,
            width=result.get('width'),
            height=result.get('height'),
            file_size=result.get('file_size'),
            related_ip_image_id=related_ip_image_id
        )
        print(f"✅ 图像已保存到素材库: {media.id}")
        return media

    except Exception as e:
        print(f"❌ 创建素材库记录失败: {str(e)}")
        # 如果数据库保存失败，删除已下载的文件
        try:
            absolute_path = os.path.join(settings.BASE_DIR, 'media', result['local_path'])
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
        except:
            pass
        return None


def delete_media_file(local_path):
    """
    删除本地媒体文件

    Args:
        local_path: 相对路径

    Returns:
        bool: 是否成功删除
    """
    try:
        absolute_path = os.path.join(settings.BASE_DIR, 'media', local_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            return True
        return False
    except Exception as e:
        print(f"❌ 删除文件失败: {str(e)}")
        return False
