#!/usr/bin/env python3
"""
管理脚本：为现有用户设置初始额度为3次
使用方法：python scripts/set_user_initial_quota.py
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserQuota


def set_initial_quota_for_users():
    """为所有现有用户设置3次初始额度"""
    print("=" * 60)
    print("开始为现有用户设置初始额度（3次）...")
    print("=" * 60)

    # 获取所有用户
    all_users = User.objects.all()
    total_users = all_users.count()
    print(f"\n📊 总用户数: {total_users}")

    if total_users == 0:
        print("❌ 没有找到任何用户")
        return

    # 统计信息
    created_count = 0
    already_exists_count = 0
    updated_count = 0

    for user in all_users:
        try:
            # 检查用户是否已有 UserQuota 记录
            quota, created = UserQuota.objects.get_or_create(
                user=user,
                defaults={
                    'available_quota': 3,
                    'total_purchased': 0
                }
            )

            if created:
                created_count += 1
                print(f"✅ [{created_count}] 为用户 '{user.username}' 创建额度: 3次")
            else:
                already_exists_count += 1
                # 如果用户已有额度记录，可以选择是否更新
                # 这里我们只显示信息，不覆盖现有额度
                print(f"ℹ️  用户 '{user.username}' 已有额度记录 (当前: {quota.available_quota}次)")

        except Exception as e:
            print(f"❌ 处理用户 '{user.username}' 时出错: {str(e)}")

    # 输出总结
    print("\n" + "=" * 60)
    print("📊 执行结果统计:")
    print(f"   - 总用户数: {total_users}")
    print(f"   - 新创建额度: {created_count} 个用户")
    print(f"   - 已有额度记录: {already_exists_count} 个用户")
    print("=" * 60)
    print("✅ 初始额度设置完成！")
    print("=" * 60)


if __name__ == '__main__':
    set_initial_quota_for_users()
