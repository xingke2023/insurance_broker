#!/home/ubuntu/bin/python3
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/var/www/harry-insurance2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InsuranceCompany, InsuranceCompanyRequest
import json

# AXA API的标准Headers
AXA_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Language": "zh-Hant",
    "X-Compcode": "AXAHK",
    "X-Device-Type": "web",
    "X-Device-Version": "1.41.0.4.30",
    "Origin": "https://atk.axahk.digital",
    "Referer": "https://atk.axahk.digital/"
}

try:
    # 1. 检查并更新AXA公司信息
    axa, created = InsuranceCompany.objects.get_or_create(
        code='axa',
        defaults={
            'name': '安盛',
            'name_en': 'AXA',
            'icon': '🏢',
            'color_gradient': 'from-blue-600 to-blue-700',
            'bg_color': 'bg-blue-50',
            'description': '安盛保险公司',
            'bearer_token': '',  # 需要手动在Admin后台配置
            'cookie': '',  # 需要手动在Admin后台配置
            'is_active': True,
            'sort_order': 4
        }
    )

    if created:
        print(f"✓ 创建了AXA公司记录")
    else:
        print(f"✓ AXA公司已存在")

    print(f"  - Bearer Token长度: {len(axa.bearer_token) if axa.bearer_token else 0}")
    print(f"  - Cookie长度: {len(axa.cookie) if axa.cookie else 0}")

    # 2. 检查并更新"利益表计算"请求配置
    req, created = InsuranceCompanyRequest.objects.get_or_create(
        company=axa,
        request_name='利益表计算',
        defaults={
            'request_url': 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate',
            'request_method': 'POST',
            'headers': AXA_HEADERS,
            'authorization': '',  # 可以为空，会使用公司级别的bearer_token
            'configurable_fields': ['premium'],
            'field_descriptions': {
                'premium': {
                    'label': '每期保费',
                    'type': 'number',
                    'default': 50000,
                    'required': True
                },
                'bearer_token': {
                    'label': 'Bearer Token',
                    'type': 'string',
                    'sensitive': True,
                    'required': False
                }
            },
            'insurance_product': '盛利 II 儲蓄保險',
            'requires_bearer_token': True,
            'is_active': True,
            'sort_order': 1
        }
    )

    if created:
        print(f"✓ 创建了'利益表计算'请求配置")
    else:
        # 更新headers
        req.headers = AXA_HEADERS
        req.save()
        print(f"✓ 更新了'利益表计算'的headers配置")

    print(f"\n当前Headers配置:")
    print(json.dumps(req.headers, indent=2, ensure_ascii=False))

    # 3. 检查并更新"提取金额计算"请求配置
    req2, created2 = InsuranceCompanyRequest.objects.get_or_create(
        company=axa,
        request_name='提取金额计算',
        defaults={
            'request_url': 'https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate',
            'request_method': 'POST',
            'headers': AXA_HEADERS,
            'authorization': '',
            'configurable_fields': ['premium', 'withdrawal_amount'],
            'field_descriptions': {
                'premium': {
                    'label': '每期保费',
                    'type': 'number',
                    'default': 50000,
                    'required': True
                },
                'withdrawal_amount': {
                    'label': '提取金额',
                    'type': 'number',
                    'default': 10000,
                    'required': True
                },
                'bearer_token': {
                    'label': 'Bearer Token',
                    'type': 'string',
                    'sensitive': True,
                    'required': False
                }
            },
            'insurance_product': '盛利 II 儲蓄保險',
            'requires_bearer_token': True,
            'is_active': True,
            'sort_order': 2
        }
    )

    if created2:
        print(f"✓ 创建了'提取金额计算'请求配置")
    else:
        req2.headers = AXA_HEADERS
        req2.save()
        print(f"✓ 更新了'提取金额计算'的headers配置")

    print("\n" + "=" * 60)
    print("配置完成！")
    print("=" * 60)
    print("\n⚠️  重要提示：")
    print("1. 请登录Admin后台：http://your-domain:8007/admin/")
    print("2. 进入'保险公司'表，找到AXA")
    print("3. 配置Bearer Token和Cookie（如果需要）")
    print("4. 保存后即可在前端使用")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
