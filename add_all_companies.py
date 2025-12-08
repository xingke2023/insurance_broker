"""
批量添加11家保险公司到数据库
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InsuranceCompany

def add_all_companies():
    """添加所有保险公司"""

    companies = [
        {
            'code': 'prudential',
            'name': '保诚',
            'name_en': 'Prudential',
            'icon': '🏛️',
            'color_gradient': 'from-red-600 to-red-700',
            'bg_color': 'bg-red-50',
            'description': '英国保诚保险有限公司',
            'sort_order': 1
        },
        {
            'code': 'manulife',
            'name': '宏利',
            'name_en': 'Manulife',
            'icon': '🌲',
            'color_gradient': 'from-green-600 to-green-700',
            'bg_color': 'bg-green-50',
            'description': '宏利人寿保险（国际）有限公司',
            'sort_order': 2
        },
        {
            'code': 'sunlife',
            'name': '永明',
            'name_en': 'Sun Life',
            'icon': '☀️',
            'color_gradient': 'from-yellow-600 to-orange-600',
            'bg_color': 'bg-yellow-50',
            'description': '永明金融（亚洲）有限公司',
            'sort_order': 3
        },
        {
            'code': 'axa',
            'name': '安盛',
            'name_en': 'AXA',
            'icon': '🏢',
            'color_gradient': 'from-blue-600 to-blue-700',
            'bg_color': 'bg-blue-50',
            'description': '安盛保险有限公司',
            'sort_order': 4
        },
        {
            'code': 'boc',
            'name': '中银',
            'name_en': 'BOC',
            'icon': '🏦',
            'color_gradient': 'from-red-700 to-red-800',
            'bg_color': 'bg-red-50',
            'description': '中银集团人寿保险有限公司',
            'sort_order': 5
        },
        {
            'code': 'chinalife',
            'name': '国寿',
            'name_en': 'China Life',
            'icon': '🐉',
            'color_gradient': 'from-red-600 to-orange-600',
            'bg_color': 'bg-red-50',
            'description': '中国人寿保险（海外）股份有限公司',
            'sort_order': 6
        },
        {
            'code': 'ctf',
            'name': '周大福',
            'name_en': 'Chow Tai Fook',
            'icon': '💎',
            'color_gradient': 'from-purple-600 to-pink-600',
            'bg_color': 'bg-purple-50',
            'description': '周大福金融集团',
            'sort_order': 7
        },
        {
            'code': 'ftlife',
            'name': '富通',
            'name_en': 'FTLife',
            'icon': '🔷',
            'color_gradient': 'from-blue-700 to-indigo-700',
            'bg_color': 'bg-blue-50',
            'description': '富通保险有限公司',
            'sort_order': 8
        },
        {
            'code': 'fwd',
            'name': '富卫',
            'name_en': 'FWD',
            'icon': '🛡️',
            'color_gradient': 'from-orange-600 to-red-600',
            'bg_color': 'bg-orange-50',
            'description': '富卫人寿保险（百慕达）有限公司',
            'sort_order': 9
        },
        {
            'code': 'transamerica',
            'name': '立桥',
            'name_en': 'Transamerica',
            'icon': '🌉',
            'color_gradient': 'from-teal-600 to-cyan-600',
            'bg_color': 'bg-teal-50',
            'description': '立桥人寿保险有限公司',
            'sort_order': 10
        },
        {
            'code': 'aia',
            'name': '友邦',
            'name_en': 'AIA',
            'icon': '🤝',
            'color_gradient': 'from-green-700 to-teal-700',
            'bg_color': 'bg-green-50',
            'description': '友邦保险（国际）有限公司',
            'sort_order': 11
        }
    ]

    created_count = 0
    updated_count = 0

    for company_data in companies:
        company, created = InsuranceCompany.objects.update_or_create(
            code=company_data['code'],
            defaults={
                'name': company_data['name'],
                'name_en': company_data['name_en'],
                'icon': company_data['icon'],
                'color_gradient': company_data['color_gradient'],
                'bg_color': company_data['bg_color'],
                'description': company_data['description'],
                'is_active': True,
                'sort_order': company_data['sort_order']
            }
        )

        if created:
            print(f"✓ 创建: {company.icon} {company.name} ({company.name_en})")
            created_count += 1
        else:
            print(f"✓ 更新: {company.icon} {company.name} ({company.name_en})")
            updated_count += 1

    print(f"\n完成！")
    print(f"新建: {created_count} 个")
    print(f"更新: {updated_count} 个")
    print(f"总计: {InsuranceCompany.objects.count()} 个保险公司")

    print("\n所有保险公司列表：")
    for company in InsuranceCompany.objects.all().order_by('sort_order'):
        requests_count = company.api_requests.count()
        print(f"{company.sort_order:2d}. {company.icon} {company.name:6s} ({company.name_en:15s}) - {requests_count} 个API配置")

if __name__ == '__main__':
    add_all_companies()
