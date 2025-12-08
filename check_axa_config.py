#!/usr/bin/env python3
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, '/var/www/harry-insurance2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import InsuranceCompany, InsuranceCompanyRequest
import json

# 查询AXA公司信息
try:
    axa = InsuranceCompany.objects.get(code='axa')
    print("=" * 60)
    print("AXA 公司信息:")
    print("=" * 60)
    print(f"名称: {axa.name}")
    print(f"Bearer Token长度: {len(axa.bearer_token) if axa.bearer_token else 0}")
    print(f"Bearer Token前50字符: {axa.bearer_token[:50] if axa.bearer_token else '(空)'}")
    print(f"Cookie长度: {len(axa.cookie) if axa.cookie else 0}")
    print()

    # 查询利益表计算的配置
    req = InsuranceCompanyRequest.objects.get(company=axa, request_name='利益表计算')
    print("=" * 60)
    print("利益表计算 请求配置:")
    print("=" * 60)
    print(f"请求URL: {req.request_url}")
    print(f"请求方法: {req.request_method}")
    print(f"Headers配置: {json.dumps(req.headers, indent=2, ensure_ascii=False)}")
    print(f"Authorization配置长度: {len(req.authorization) if req.authorization else 0}")
    print(f"可配置字段: {req.configurable_fields}")
    print(f"字段说明: {json.dumps(req.field_descriptions, indent=2, ensure_ascii=False)}")

except InsuranceCompany.DoesNotExist:
    print("AXA公司不存在，请先在Admin后台创建")
except InsuranceCompanyRequest.DoesNotExist:
    print("利益表计算请求配置不存在，请先在Admin后台创建")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
