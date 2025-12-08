#!/usr/bin/env python3
"""
素材库功能测试脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import MediaLibrary
from api.utils.image_storage import save_to_media_library, delete_media_file


def test_media_library():
    """测试素材库功能"""
    print("=" * 60)
    print("素材库功能测试")
    print("=" * 60)

    # 1. 检查数据库表
    print("\n1. 检查数据库表...")
    try:
        count = MediaLibrary.objects.count()
        print(f"   ✅ MediaLibrary表存在，当前记录数: {count}")
    except Exception as e:
        print(f"   ❌ 数据库表检查失败: {str(e)}")
        return

    # 2. 检查本地存储目录
    print("\n2. 检查本地存储目录...")
    media_root = os.path.join(os.path.dirname(__file__), 'media')
    ip_images_dir = os.path.join(media_root, 'generated_images', 'ip_images')
    content_images_dir = os.path.join(media_root, 'generated_images', 'content_images')

    if os.path.exists(ip_images_dir):
        print(f"   ✅ IP形象目录存在: {ip_images_dir}")
    else:
        print(f"   ❌ IP形象目录不存在: {ip_images_dir}")

    if os.path.exists(content_images_dir):
        print(f"   ✅ 文案配图目录存在: {content_images_dir}")
    else:
        print(f"   ❌ 文案配图目录不存在: {content_images_dir}")

    # 3. 检查用户
    print("\n3. 检查测试用户...")
    users = User.objects.all()[:3]
    if users:
        print(f"   ✅ 找到 {len(users)} 个用户可用于测试")
        for user in users:
            media_count = MediaLibrary.objects.filter(user=user).count()
            print(f"      - {user.username}: {media_count} 个素材")
    else:
        print("   ⚠️  没有找到用户")

    # 4. 统计信息
    print("\n4. 素材库统计...")
    total = MediaLibrary.objects.count()
    ip_count = MediaLibrary.objects.filter(media_type='ip_image').count()
    content_count = MediaLibrary.objects.filter(media_type='content_image').count()
    favorite_count = MediaLibrary.objects.filter(is_favorite=True).count()

    print(f"   总素材数: {total}")
    print(f"   IP形象: {ip_count}")
    print(f"   文案配图: {content_count}")
    print(f"   收藏数: {favorite_count}")

    # 5. 最近的素材
    print("\n5. 最近的素材（前5条）...")
    recent_media = MediaLibrary.objects.all()[:5]
    if recent_media:
        for media in recent_media:
            print(f"   ID:{media.id} | {media.get_media_type_display()} | {media.user.username} | {media.created_at}")
            print(f"      提示词: {media.prompt[:50]}...")
            if media.local_path:
                print(f"      本地路径: {media.local_path}")
            else:
                print(f"      原始URL: {media.original_url[:60]}...")
            print()
    else:
        print("   暂无素材")

    # 6. 检查文件存在性
    print("\n6. 检查本地文件存在性...")
    media_with_local = MediaLibrary.objects.exclude(local_path='')[:10]
    checked = 0
    exists = 0
    for media in media_with_local:
        checked += 1
        file_path = os.path.join(media_root, media.local_path)
        if os.path.exists(file_path):
            exists += 1
            file_size = os.path.getsize(file_path)
            print(f"   ✅ {media.local_path} ({file_size} bytes)")
        else:
            print(f"   ❌ {media.local_path} (不存在)")

    if checked > 0:
        print(f"\n   检查了 {checked} 个文件，{exists} 个存在")

    # 7. 显示API端点
    print("\n7. 可用的API端点:")
    print("   GET    /api/media-library/                     - 获取素材库列表")
    print("   GET    /api/media-library/stats/               - 获取统计信息")
    print("   GET    /api/media-library/{id}/                - 获取素材详情")
    print("   POST   /api/media-library/{id}/favorite/       - 切换收藏状态")
    print("   DELETE /api/media-library/{id}/delete/         - 删除素材")
    print("   POST   /api/media-library/batch-delete/        - 批量删除")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_media_library()
