#!/usr/bin/env python3
"""
用户权限管理脚本
用于管理用户对"计划书分步骤分析"功能的访问权限
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/var/www/harry-insurance2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User, Group


def create_plan_analyzer_group():
    """创建plan_analyzer用户组"""
    group, created = Group.objects.get_or_create(name='plan_analyzer')
    if created:
        print('✅ 成功创建用户组: plan_analyzer')
    else:
        print('ℹ️  用户组已存在: plan_analyzer')
    return group


def add_user_to_group(username):
    """将用户添加到plan_analyzer组"""
    try:
        user = User.objects.get(username=username)
        group = Group.objects.get(name='plan_analyzer')
        user.groups.add(group)
        print(f'✅ 用户 {username} 已添加到 plan_analyzer 组')
        print(f'   该用户现在可以访问"计划书分步骤分析"功能')
    except User.DoesNotExist:
        print(f'❌ 用户 {username} 不存在')
    except Group.DoesNotExist:
        print(f'❌ 用户组 plan_analyzer 不存在，请先运行 create 命令')


def remove_user_from_group(username):
    """从plan_analyzer组移除用户"""
    try:
        user = User.objects.get(username=username)
        group = Group.objects.get(name='plan_analyzer')
        user.groups.remove(group)
        print(f'✅ 用户 {username} 已从 plan_analyzer 组移除')
        print(f'   该用户现在无法访问"计划书分步骤分析"功能')
    except User.DoesNotExist:
        print(f'❌ 用户 {username} 不存在')
    except Group.DoesNotExist:
        print(f'❌ 用户组 plan_analyzer 不存在')


def list_group_members():
    """列出plan_analyzer组的所有成员"""
    try:
        group = Group.objects.get(name='plan_analyzer')
        users = group.user_set.all()
        if users:
            print(f'\n📋 plan_analyzer 组成员列表（共{users.count()}人）：')
            for user in users:
                print(f'   - {user.username} ({user.email})')
        else:
            print('ℹ️  plan_analyzer 组目前没有成员')
    except Group.DoesNotExist:
        print(f'❌ 用户组 plan_analyzer 不存在，请先运行 create 命令')


def list_all_users():
    """列出所有用户及其权限状态"""
    users = User.objects.all().order_by('username')
    print(f'\n👥 系统所有用户（共{users.count()}人）：')
    print(f'{"用户名":<20} {"邮箱":<30} {"管理员":<10} {"可访问分析"}')
    print('-' * 70)

    group = None
    try:
        group = Group.objects.get(name='plan_analyzer')
    except Group.DoesNotExist:
        pass

    for user in users:
        is_admin = '是' if user.is_staff else '否'
        has_access = '是' if (user.is_staff or (group and group in user.groups.all())) else '否'
        print(f'{user.username:<20} {user.email:<30} {is_admin:<10} {has_access}')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='管理用户对"计划书分步骤分析"功能的访问权限',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例：
  # 创建用户组
  python3 manage_user_permissions.py create

  # 授予用户权限
  python3 manage_user_permissions.py add username

  # 撤销用户权限
  python3 manage_user_permissions.py remove username

  # 查看有权限的用户列表
  python3 manage_user_permissions.py list

  # 查看所有用户及权限状态
  python3 manage_user_permissions.py list-all
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='操作命令')

    # create命令
    subparsers.add_parser('create', help='创建plan_analyzer用户组')

    # add命令
    add_parser = subparsers.add_parser('add', help='授予用户访问权限')
    add_parser.add_argument('username', help='用户名')

    # remove命令
    remove_parser = subparsers.add_parser('remove', help='撤销用户访问权限')
    remove_parser.add_argument('username', help='用户名')

    # list命令
    subparsers.add_parser('list', help='列出有权限的用户')

    # list-all命令
    subparsers.add_parser('list-all', help='列出所有用户及权限状态')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'create':
        create_plan_analyzer_group()
    elif args.command == 'add':
        add_user_to_group(args.username)
    elif args.command == 'remove':
        remove_user_from_group(args.username)
    elif args.command == 'list':
        list_group_members()
    elif args.command == 'list-all':
        list_all_users()


if __name__ == '__main__':
    main()
