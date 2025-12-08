import os
import json
import base64
from openai import OpenAI


def extract_plan_data_from_pdf(pdf_file):
    """
    使用阿里千问视觉模型直接识别PDF文件
    支持直接上传PDF文件进行识别

    注意：阿里千问API不支持PDF格式，仅支持图片格式(image_url)
    此函数保留用于未来支持或转换为图片后使用
    """
    # 从环境变量获取API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError('DASHSCOPE_API_KEY环境变量未设置')

    # 初始化客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 读取PDF文件内容并转换为base64
    pdf_file.seek(0)
    pdf_content = pdf_file.read()
    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

    # 构建提示词
    prompt = """请分析这份保险计划书PDF文件，提取以下关键信息并以JSON格式返回：

需要提取的字段：
1. customer_name: 客户/受保人姓名
2. customer_age: 客户年龄（数字）
3. customer_gender: 性别（男/女）
4. insurance_product: 保险产品名称
5. insurance_company: 保险公司名称
6. insurance_amount: 保额/保险金额（数字，单位：元）
7. premium_amount: 年缴保费（数字，单位：元）
8. payment_years: 缴费年期（数字，如20表示20年）
9. total_premium: 总保费（数字，单位：元）
10. insurance_period: 保险期限（如：终身、至70岁、20年等）

请以JSON格式返回数据，如果某个字段无法从文档中提取，请设置为null。
请确保数字字段返回纯数字，不要包含单位或其他文字。

返回格式示例：
{
    "customer_name": "张三",
    "customer_age": 35,
    "customer_gender": "男",
    "insurance_product": "XX终身寿险",
    "insurance_company": "XX保险公司",
    "insurance_amount": 500000,
    "premium_amount": 15000,
    "payment_years": 20,
    "total_premium": 300000,
    "insurance_period": "终身"
}

请直接返回JSON，不要包含其他说明文字。"""

    try:
        # 打印发送的提示词
        print("\n" + "="*80)
        print("📤 发送到千问视觉模型的提示词:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")

        # 调用千问视觉模型API
        response = client.chat.completions.create(
            model="qwen-vl-max-latest",  # 使用千问视觉模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档分析助手，擅长从保险计划书中提取结构化数据。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file_url": {
                                "url": f"data:application/pdf;base64,{pdf_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=2000
        )

        # 获取响应内容
        content = response.choices[0].message.content.strip()

        # 打印模型返回的原始结果
        print("\n" + "="*80)
        print("📥 千问视觉模型返回的原始结果:")
        print("="*80)
        print(content)
        print("="*80 + "\n")

        # 尝试解析JSON
        # 移除可能的markdown代码块标记
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]

        content = content.strip()

        # 解析JSON
        extracted_data = json.loads(content)

        # 打印解析后的JSON数据（视觉模型）
        print("\n" + "="*80)
        print("✅ 视觉模型 - 成功解析的JSON数据:")
        print("="*80)
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")

        return {
            'success': True,
            'data': extracted_data,
            'raw_response': response.choices[0].message.content
        }

    except json.JSONDecodeError as e:
        print("\n" + "="*80)
        print("❌ 视觉模型 - JSON解析失败:")
        print("="*80)
        print(f"错误: {str(e)}")
        print("="*80 + "\n")
        return {
            'success': False,
            'error': f'JSON解析失败: {str(e)}',
            'raw_response': response.choices[0].message.content if 'response' in locals() else None
        }
    except Exception as e:
        print("\n" + "="*80)
        print("❌ 视觉模型 - API调用失败:")
        print("="*80)
        print(f"错误: {str(e)}")
        print("="*80 + "\n")
        return {
            'success': False,
            'error': f'API调用失败: {str(e)}'
        }


def extract_plan_data_from_text(text_content, company_code='other'):
    """
    使用阿里千问模型从文本中提取结构化数据

    Args:
        text_content: PDF提取的文本内容
        company_code: 保险公司代码（aia, prudential, manulife等）
    """
    # 从环境变量获取API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        raise ValueError('DASHSCOPE_API_KEY环境变量未设置')

    # 初始化客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 使用保险公司配置生成定制化提示词
    from .insurance_company_configs import generate_prompt_for_company
    prompt = generate_prompt_for_company(company_code, text_content)

    # 如果使用默认提示词（兼容旧代码）
    if False:  # 保留原有逻辑作为参考
        prompt = f"""请仔细分析以下保险计划书内容，提取所有关键信息并以JSON格式返回。

【基本信息字段】：
1. customer_name: 客户/受保人姓名
2. customer_age: 客户年龄（数字）
3. customer_gender: 性别（男/女）
4. insurance_product: 保险产品名称
5. insurance_company: 保险公司名称
6. insurance_amount: 保额/保险金额（数字，单位：元）
7. premium_amount: 年缴保费（数字，单位：元）
8. payment_years: 缴费年期（数字，如20表示20年）
9. total_premium: 总保费（数字，单位：元）
10. insurance_period: 保险期限（如：终身、至70岁、20年等）

【年度价值表】（重要！）：
11. annual_values: 保单年度价值表数组，包含每个保单年度的退保价值
   格式：[
     {{
       "policy_year": 1,  // 保单年度终结（第几年）
       "guaranteed_value": 1000,  // 保证现金价值/保证金额
       "non_guaranteed_value": 500,  // 非保证现金价值/非保证金额/红利
       "total_value": 1500  // 总现金价值/退保价值总额
     }},
     ...
   ]

**重要提取规则**：
1. 必须提取完整的年度价值表，从第1年到最后一年
2. 不同保险公司的表格列名可能不同，请识别以下可能的列名：
   - 保单年度/年度终结/保单年份/年份/Year
   - 保证现金价值/保证金额/保证价值/Guaranteed Cash Value
   - 非保证现金价值/非保证金额/红利/Bonus/Non-Guaranteed Value
   - 总现金价值/退保价值/总额/Total Cash Value/Surrender Value
3. 数字字段必须返回纯数字（不含逗号、货币符号、单位）
4. 如果某个字段无法提取，设置为null
5. 年度价值表如果找不到，annual_values设置为空数组[]

**计划书内容**：
{text_content[:15000]}

请直接返回JSON格式，不要包含任何解释文字。"""

    try:
        # 打印发送的提示词
        print("\n" + "="*80)
        print("📤 发送到千问文本模型的提示词:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")

        # 调用千问API
        response = client.chat.completions.create(
            model="qwen-plus-latest",  # 使用千问Plus模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档分析助手，擅长从保险计划书中提取结构化数据。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=2000
        )

        # 获取响应内容
        content = response.choices[0].message.content.strip()

        # 打印模型返回的原始结果
        print("\n" + "="*80)
        print("📥 千问文本模型返回的原始结果:")
        print("="*80)
        print(content)
        print("="*80 + "\n")

        # 尝试解析JSON
        # 移除可能的markdown代码块标记
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]

        content = content.strip()

        # 解析JSON
        extracted_data = json.loads(content)

        # 打印解析后的JSON数据（文本模型）
        print("\n" + "="*80)
        print("✅ 文本模型 - 成功解析的JSON数据:")
        print("="*80)
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")

        return {
            'success': True,
            'data': extracted_data,
            'raw_response': response.choices[0].message.content
        }

    except json.JSONDecodeError as e:
        print("\n" + "="*80)
        print("❌ 文本模型 - JSON解析失败:")
        print("="*80)
        print(f"错误: {str(e)}")
        print("="*80 + "\n")
        return {
            'success': False,
            'error': f'JSON解析失败: {str(e)}',
            'raw_response': response.choices[0].message.content if 'response' in locals() else None
        }
    except Exception as e:
        print("\n" + "="*80)
        print("❌ 文本模型 - API调用失败:")
        print("="*80)
        print(f"错误: {str(e)}")
        print("="*80 + "\n")
        return {
            'success': False,
            'error': f'API调用失败: {str(e)}'
        }
