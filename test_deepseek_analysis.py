#!/usr/bin/env python3
"""
测试 DeepSeek 年度价值表分析功能
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, '/var/www/harry-insurance')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import PlanDocument
from api.deepseek_service import analyze_insurance_table
import time

# 测试用的OCR内容（包含年度价值表信息）
test_ocr_content = """
保险计划书

受保人信息：
姓名：张三
年龄：35岁
性别：男

保险产品：终身寿险
保险公司：XX人寿保险有限公司

年度价值表：

保單年度終結    退保價值
                保證現金價值(A)    終期紅利(B)    总额(A)+(B)
1              5,000              1,000          6,000
2              10,500             2,200          12,700
3              16,200             3,500          19,700
5              28,500             6,000          34,500
10             62,000             13,000         75,000
15             105,000            22,000         127,000
20             156,000            33,000         189,000

注：以上数值仅供参考，实际价值以保单为准。
"""

def test_deepseek_analysis():
    """测试 DeepSeek 分析功能"""
    print("=" * 60)
    print("测试 DeepSeek 年度价值表分析功能")
    print("=" * 60)

    # 检查 API 密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        print(f"✓ API密钥已配置: {api_key[:20]}...")
    else:
        print("✗ API密钥未配置，将使用模拟数据")

    print("\n1. 创建测试文档...")
    doc = PlanDocument.objects.create(
        file_name='test_deepseek.pdf',
        file_size=len(test_ocr_content),
        content=test_ocr_content,
        status='completed'
    )
    print(f"✓ 文档已创建，ID: {doc.id}")

    print("\n2. 调用 DeepSeek 分析服务...")
    start_time = time.time()

    table_data = analyze_insurance_table(test_ocr_content)

    end_time = time.time()
    elapsed = end_time - start_time

    if table_data:
        print(f"✓ 分析成功！耗时: {elapsed:.2f}秒")
        print(f"✓ 提取到 {len(table_data.get('years', []))} 条年度数据")

        print("\n3. 年度价值表数据：")
        print("-" * 60)
        print(f"{'年度':<8} {'保證現金價值(A)':<15} {'終期紅利(B)':<15} {'总额':<15}")
        print("-" * 60)

        for year in table_data.get('years', []):
            policy_year = year.get('policy_year', 'N/A')
            guaranteed = year.get('guaranteed_cash_value', 0)
            bonus = year.get('terminal_bonus', 0)
            total = year.get('total', 0)

            print(f"{policy_year:<8} {guaranteed:<15,.2f} {bonus:<15,.2f} {total:<15,.2f}")

        print("-" * 60)

        print("\n4. 更新数据库...")
        doc.table = table_data
        doc.save()
        print(f"✓ 数据已保存到文档 {doc.id} 的 table 字段")

        print("\n5. 验证数据...")
        doc_check = PlanDocument.objects.get(id=doc.id)
        if doc_check.table:
            print(f"✓ 验证成功！table 字段已更新")
            print(f"  - 包含 {len(doc_check.table.get('years', []))} 条年度数据")
        else:
            print("✗ 验证失败！table 字段为空")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print(f"\n可以通过以下方式查看结果：")
        print(f"1. 访问 http://localhost:8011")
        print(f"2. 进入 '计划书管理'")
        print(f"3. 查看文档 ID: {doc.id}")
        print(f"4. 查看 '年度价值表' 部分")

        return True
    else:
        print("✗ 分析失败！")
        print("\n请检查：")
        print("1. DEEPSEEK_API_KEY 环境变量是否正确")
        print("2. 网络连接是否正常")
        print("3. API 配额是否充足")
        print("4. 查看日志了解详细错误信息")

        return False

if __name__ == '__main__':
    try:
        success = test_deepseek_analysis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
