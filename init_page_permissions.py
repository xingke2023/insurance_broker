#!/usr/bin/env python3
"""
初始化页面权限配置脚本
用于创建"计划书分步骤分析"页面的权限配置
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('/var/www/harry-insurance2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import Group
from api.models import PagePermission


def init_plan_analyzer_permission():
    """初始化计划书分步骤分析页面权限"""

    # 确保 plan_analyzer 用户组存在
    group, group_created = Group.objects.get_or_create(name='plan_analyzer')
    if group_created:
        print('✅ 创建用户组: plan_analyzer')
    else:
        print('ℹ️  用户组已存在: plan_analyzer')

    # 创建或更新页面权限配置
    page, created = PagePermission.objects.update_or_create(
        page_code='plan-analyzer-2',
        defaults={
            'page_name': '计划书分步骤分析',
            'route_path': '/plan-analyzer-2',
            'description': '使用AI分步骤分析保险计划书，提取受保人信息、保费信息、年度价值表等详细数据',
            'icon': 'DocumentTextIcon',
            'color': 'from-emerald-600 to-teal-600',
            'require_staff': False,
            'is_active': True,
            'sort_order': 10,
        }
    )

    if created:
        print(f'✅ 创建页面权限配置: {page.page_name}')
        # 添加 plan_analyzer 组到允许的组列表
        page.allowed_groups.add(group)
        print(f'✅ 将 plan_analyzer 组添加到允许列表')
    else:
        print(f'ℹ️  页面权限配置已存在: {page.page_name}')
        # 确保 plan_analyzer 组在允许列表中
        if group not in page.allowed_groups.all():
            page.allowed_groups.add(group)
            print(f'✅ 将 plan_analyzer 组添加到允许列表')

    print('\n📋 当前配置：')
    print(f'   页面名称：{page.page_name}')
    print(f'   页面代码：{page.page_code}')
    print(f'   路由路径：{page.route_path}')
    print(f'   是否启用：{"是" if page.is_active else "否"}')
    print(f'   需要管理员权限：{"是" if page.require_staff else "否"}')
    print(f'   允许的用户组：{", ".join([g.name for g in page.allowed_groups.all()])}')

    print('\n✅ 初始化完成！')
    print('\n💡 提示：')
    print('   1. 现在您可以在 Django Admin 后台管理页面权限')
    print('   2. 访问：http://your-domain:8007/admin/api/pagepermission/')
    print('   3. 可以添加或移除用户组、修改权限规则')
    print('   4. 用户需要重新登录才能看到权限变化')


def main():
    print('🚀 开始初始化页面权限配置...\n')
    init_plan_analyzer_permission()


if __name__ == '__main__':
    main()
