#!/usr/bin/env python
"""
测试阿里千问API配置是否正确
"""
import os
import sys
from pathlib import Path

# 添加项目路径
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def test_qwen_text_api():
    """测试千问文本模型"""
    print("=" * 50)
    print("测试千问文本模型...")
    print("=" * 50)

    try:
        from api.qwen_service import extract_plan_data_from_text

        # 测试文本
        test_text = """
        保险计划书

        投保人信息：
        姓名：张三
        年龄：35岁
        性别：男

        保险产品信息：
        保险公司：中国平安人寿保险股份有限公司
        产品名称：平安福终身寿险
        保险金额：500,000元
        年缴保费：15,000元
        缴费年期：20年
        保险期间：终身
        总保费：300,000元
        """

        result = extract_plan_data_from_text(test_text)

        if result['success']:
            print("✓ API调用成功！")
            print("\n提取的数据：")
            import json
            print(json.dumps(result['data'], indent=2, ensure_ascii=False))
        else:
            print("✗ API调用失败")
            print(f"错误信息：{result['error']}")
            if 'raw_response' in result and result['raw_response']:
                print(f"\n原始响应：{result['raw_response']}")

        return result['success']

    except Exception as e:
        print(f"✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_qwen_vision_api():
    """测试千问视觉模型（需要实际PDF文件）"""
    print("\n" + "=" * 50)
    print("测试千问视觉模型...")
    print("=" * 50)

    # 检查是否有测试PDF文件
    test_pdf_path = project_dir / "test_insurance_plan.pdf"

    if not test_pdf_path.exists():
        print("跳过视觉模型测试（未找到测试PDF文件）")
        print(f"如需测试，请将PDF文件放置在：{test_pdf_path}")
        return None

    try:
        from api.qwen_service import extract_plan_data_from_pdf

        with open(test_pdf_path, 'rb') as f:
            result = extract_plan_data_from_pdf(f)

        if result['success']:
            print("✓ API调用成功！")
            print("\n提取的数据：")
            import json
            print(json.dumps(result['data'], indent=2, ensure_ascii=False))
        else:
            print("✗ API调用失败")
            print(f"错误信息：{result['error']}")
            if 'raw_response' in result and result['raw_response']:
                print(f"\n原始响应：{result['raw_response']}")

        return result['success']

    except Exception as e:
        print(f"✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


def check_environment():
    """检查环境配置"""
    print("=" * 50)
    print("检查环境配置...")
    print("=" * 50)

    api_key = os.getenv('DASHSCOPE_API_KEY')

    if not api_key:
        print("✗ 未找到 DASHSCOPE_API_KEY 环境变量")
        print("\n请在 .env 文件中设置：")
        print("DASHSCOPE_API_KEY=sk-your-api-key-here")
        return False

    if api_key.startswith('sk-'):
        print("✓ 找到 DASHSCOPE_API_KEY")
        print(f"  密钥前缀：{api_key[:10]}...")
    else:
        print("⚠ DASHSCOPE_API_KEY 格式可能不正确")
        print(f"  当前值：{api_key[:20]}...")

    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("阿里千问API配置测试")
    print("=" * 50 + "\n")

    # 检查环境
    if not check_environment():
        print("\n✗ 环境配置检查失败，请先配置 DASHSCOPE_API_KEY")
        return 1

    # 测试文本模型
    text_result = test_qwen_text_api()

    # 测试视觉模型（可选）
    vision_result = test_qwen_vision_api()

    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)

    if text_result:
        print("✓ 文本模型测试通过")
    else:
        print("✗ 文本模型测试失败")

    if vision_result is None:
        print("⊘ 视觉模型测试已跳过")
    elif vision_result:
        print("✓ 视觉模型测试通过")
    else:
        print("✗ 视觉模型测试失败")

    if text_result:
        print("\n✓ 基础功能正常，可以开始使用！")
        return 0
    else:
        print("\n✗ 配置存在问题，请检查API密钥和网络连接")
        return 1


if __name__ == '__main__':
    exit(main())
