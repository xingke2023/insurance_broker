import sys
import os
import django

sys.path.insert(0, '/var/www/harry-insurance2')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

# 找到正确的Python解释器路径
import subprocess
result = subprocess.run(['which', 'python3'], capture_output=True, text=True)
python_path = result.stdout.strip()
print(f"使用Python路径: {python_path}")

# 尝试导入Django
try:
    import django
    django.setup()
    from api.models import InsuranceCompany, InsuranceCompanyRequest
    import json
    
    # 查询AXA的利益表计算配置
    company = InsuranceCompany.objects.get(code='axa')
    req = InsuranceCompanyRequest.objects.get(company=company, request_name='利益表计算')
    
    print("\n" + "="*60)
    print("AXA 利益表计算 - 字段描述配置:")
    print("="*60)
    print(json.dumps(req.field_descriptions, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("可配置字段列表:")
    print("="*60)
    print(req.configurable_fields)
    
    print("\n" + "="*60)
    print("Headers配置:")
    print("="*60)
    print(f"类型: {type(req.headers)}")
    if isinstance(req.headers, str):
        print(f"字符串长度: {len(req.headers)}")
        print(f"内容预览: {req.headers[:200]}")
        try:
            parsed = json.loads(req.headers)
            print(f"\n解析后的Headers:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print("无法解析为JSON")
    else:
        print(json.dumps(req.headers, indent=2, ensure_ascii=False))
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
