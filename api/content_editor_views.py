"""
内容编辑器相关视图
专门处理文档内容编辑器的功能
"""
import os
import json
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from .models import PlanDocument

logger = logging.getLogger(__name__)


@api_view(['POST'])
def process_user_request(request, document_id):
    """
    处理用户在内容编辑器中的请求
    调用DeepSeek API根据文档内容和用户要求生成结果

    请求体:
    {
        "user_input": "用户输入的要求或问题"
    }

    返回:
    {
        "status": "success",
        "result": "DeepSeek返回的结果"
    }
    """
    try:
        # 获取文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'文档 {document_id} 不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 获取用户输入
        user_input = request.data.get('user_input', '').strip()

        if not user_input:
            return Response({
                'status': 'error',
                'message': '请输入您的要求'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info("="*80)
        logger.info(f"📝 处理内容编辑器请求")
        logger.info(f"   文档ID: {document_id}")
        logger.info(f"   文档名称: {doc.file_name}")
        logger.info(f"   用户输入: {user_input[:100]}...")

        # 检查文档内容
        if not doc.content:
            return Response({
                'status': 'error',
                'message': '文档内容为空，无法处理'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            logger.error('❌ DEEPSEEK_API_KEY环境变量未设置')
            return Response({
                'status': 'error',
                'message': 'API密钥未配置，请联系管理员'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 构建系统提示词
        system_prompt = f"""你是一个专业的保险计划书分析助手。你正在帮助用户处理以下保险计划书的内容。

计划书基本信息：
- 文件名：{doc.file_name}
- 受保人：{doc.insured_name or '未提取'}
- 年龄：{doc.insured_age or '未提取'}
- 性别：{doc.insured_gender or '未提取'}
- 保险公司：{doc.insurance_company or '未提取'}
- 保险产品：{doc.insurance_product or '未提取'}
- 保额：{doc.sum_assured or '未提取'}
- 年缴保费：{doc.annual_premium or '未提取'}
- 缴费期：{doc.payment_years or '未提取'}年
- 保障期：{doc.insurance_period or '未提取'}

计划书完整OCR识别内容：
{doc.content}

请根据用户的要求，基于以上计划书内容进行处理。你的回答应该：
1. 准确、专业、客观
2. 直接针对用户要求给出答案
3. 如果需要引用文档内容，请明确指出
4. 如果文档中没有相关信息，请明确说明
"""

        logger.info("⏳ 开始调用 DeepSeek API")

        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.3,
            max_tokens=8192
        )

        # 获取AI回复
        ai_result = response.choices[0].message.content.strip()

        logger.info(f"✅ DeepSeek API 调用成功")
        logger.info(f"   返回内容长度: {len(ai_result)} 字符")
        logger.info(f"   返回内容预览: {ai_result[:100]}...")
        logger.info("="*80)

        return Response({
            'status': 'success',
            'result': ai_result,
            'document_info': {
                'id': doc.id,
                'file_name': doc.file_name,
                'insured_name': doc.insured_name
            }
        })

    except Exception as e:
        logger.error(f"❌ 处理请求时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_tablesummary(request, document_id):
    """
    更新文档的tablesummary字段
    使用DeepSeek API分析OCR内容，提取表格概要信息

    返回:
    {
        "status": "success",
        "tablesummary": "提取的表格概要内容"
    }
    """
    try:
        # 获取文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'文档 {document_id} 不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        logger.info("="*80)
        logger.info(f"🔄 更新表格概要 (tablesummary)")
        logger.info(f"   文档ID: {document_id}")
        logger.info(f"   文档名称: {doc.file_name}")

        # 检查文档内容
        if not doc.content:
            return Response({
                'status': 'error',
                'message': '文档内容为空，无法生成表格概要'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            logger.error('❌ DEEPSEEK_API_KEY环境变量未设置')
            return Response({
                'status': 'error',
                'message': 'API密钥未配置，请联系管理员'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 构建提示词
        prompt = f"""以保单年度终结为坐标，分析以下保险计划书中的所有表格。

要求：
1. 识别所有以"保单年度终结"为坐标的表格
2. 有些表格可能跨度好几个页面，但只算一张表，请完整识别
3. 对每个表格提取：表详细名称、行数、基本字段

只输出结果，不要有任何解释说明。

输出格式示例：
1.
表名：詳細說明 - 退保價值 (只根據基本計劃計算)
行数：100行
基本字段：保单年度终结,缴付保费总额,退保价值(保证金额(保证现金价值),非保證金額(续期红利),总额),累積已支付非保證入息+總退保價值

2.
表名：身故賠償
行数：50行
基本字段：保单年度终结,身故赔偿(保证金额,非保证金额,总额)

计划书内容：
{doc.content[:120000]}

请直接返回分析结果，不要包含markdown代码块标记。"""

        logger.info("⏳ 开始调用 DeepSeek API 分析表格结构")
        logger.info(f"   OCR内容长度: {len(doc.content)} 字符")
        logger.info(f"   使用内容长度: {min(len(doc.content), 12000)} 字符")

        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档分析助手，擅长识别和分析表格结构。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )

        # 提取结果
        content = response.choices[0].message.content.strip()
        logger.info(f"📦 DeepSeek API返回，长度: {len(content)} 字符")

        # 清理可能的代码块标记
        if content.startswith('```'):
            lines = content.split('\n')
            # 移除第一行（```）和最后一行（```）
            if len(lines) > 2 and lines[-1].strip() == '```':
                content = '\n'.join(lines[1:-1])
            elif len(lines) > 1:
                content = '\n'.join(lines[1:])

        # 最终检查
        if not content or len(content.strip()) == 0:
            logger.error('❌ 处理后内容为空')
            return Response({
                'status': 'error',
                'message': '生成表格概要失败，返回内容为空'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 保存到数据库
        doc.tablesummary = content
        doc.save(update_fields=['tablesummary'])

        logger.info(f"✅ 表格概要已更新到数据库")
        logger.info(f"   概要长度: {len(content)} 字符")
        logger.info(f"   概要预览: {content[:200]}...")
        logger.info("="*80)

        return Response({
            'status': 'success',
            'tablesummary': content,
            'message': '表格概要更新成功'
        })

    except Exception as e:
        logger.error(f"❌ 更新表格概要时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'更新失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def process_surrender_value_table(document_id):
    """
    核心函数：处理文档的退保价值表提取逻辑

    Args:
        document_id: 文档ID

    Returns:
        dict: {
            'success': bool,
            'table1': dict or str,  # 成功时返回dict，未找到时返回''
            'message': str,
            'error': str (if failed)
        }
    """
    try:
        # 获取文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            return {
                'success': False,
                'error': f'文档 {document_id} 不存在'
            }

        logger.info("="*80)
        logger.info(f"🔄 处理退保价值表 (table1字段)")
        logger.info(f"   文档ID: {document_id}")
        logger.info(f"   文档名称: {doc.file_name}")

        # 检查文档内容
        if not doc.content:
            return {
                'success': False,
                'error': '文档内容为空，无法生成退保价值表'
            }

        # 检查tablesummary
        if not doc.tablesummary:
            return {
                'success': False,
                'error': 'tablesummary字段为空，请先更新表格概要'
            }

        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            logger.error('❌ DEEPSEEK_API_KEY环境变量未设置')
            return {
                'success': False,
                'error': 'API密钥未配置'
            }

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 第一步：判断是否存在退保价值表
        check_prompt = f"""根据以下表格概要信息，判断是否存在基本计划的退保价值表（非无忧选、非提取）。

表格概要（tablesummary）：
{doc.tablesummary}

请仔细分析表格概要，判断是否有基本计划的退保价值表。（不包含无忧选、该年非保证入息）
只需要回答：
- 如果存在这样的表格，请返回表格的名称和表格行数以及表格基本字段
- 如果存在两个以上这样的表格，请返回最完整的那个表格的信息，也就是行数最多的那个表
- 如果不存在这样的表格，请返回0

"""

        logger.info("="*80)
        logger.info("⏳ 第一步：调用 DeepSeek API 判断是否存在基本计划退保价值表")
        logger.info(f"   表格概要长度: {len(doc.tablesummary)} 字符")

        # 第一次API调用：判断是否存在相关表格
        check_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档分析助手。请根据表格概要信息，判断是否存在基本计划的退保价值表。"
                },
                {
                    "role": "user",
                    "content": check_prompt
                }
            ],
            temperature=0.1,
            max_tokens=200
        )

        has_surrender_table = check_response.choices[0].message.content.strip()
        logger.info(f"📦 DeepSeek 判断结果: {has_surrender_table}")

        # 如果不存在相关表格，返回空字符串
        if has_surrender_table == '0' or has_surrender_table.lower() in ['0', '不存在', '没有']:
            logger.info("ℹ️  未找到基本计划退保价值表")
            doc.table1 = ''
            doc.save(update_fields=['table1'])

            return {
                'success': True,
                'table1': '',
                'message': '未找到基本计划退保价值表'
            }

        # 第二步：如果存在相关表格，提取数据
        logger.info("="*80)
        logger.info("⏳ 第二步：调用 DeepSeek API 提取基本计划退保价值表数据")
        logger.info(f"   OCR内容长度: {len(doc.content)} 字符")
        logger.info(f"   使用内容长度: {min(len(doc.content), 120000)} 字符")

        extract_prompt = f"""从计划书内容中提取基本计划的退保价值表数据（非无忧选，非提取）。

表格名称：{has_surrender_table}

要求：
1. 根据实际表格基本字段灵活判断，提取以下字段：保单年度终结,退保价值(保证金额,总额)
2. 保单年度终结不一定是纯数字，可以是比如65岁 65歲 等於是投保人年齡+保單年度數字 轉換成數字(第幾年)存儲。
3. 以JSON格式返回，格式如下：

{{
  "years": [
    {{"policy_year": 1, "guaranteed": 1000, "total":1500 }},
    {{"policy_year": 2, "guaranteed": 2000, "total":3000 }}
  ]
}}

计划书内容：
{doc.content[:120000]}

请直接返回JSON格式数据，不要包含任何其他文字或markdown标记。"""

        # logger.info(extract_prompt)
        # 第二次API调用：提取表格数据
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档数据提取助手，擅长从文档中提取结构化的表格数据。你必须返回严格符合要求的JSON格式数据。"
                },
                {
                    "role": "user",
                    "content": extract_prompt
                }
            ],
            temperature=0.1,
            max_tokens=8000
        )

        # 提取结果
        content = response.choices[0].message.content.strip()
        logger.info(f"📦 DeepSeek API返回，长度: {len(content)} 字符")

        # 清理可能的代码块标记
        if content.startswith('```'):
            lines = content.split('\n')
            # 移除第一行（```json 或 ```）和最后一行（```）
            if len(lines) > 2 and lines[-1].strip() == '```':
                content = '\n'.join(lines[1:-1])
            elif len(lines) > 1:
                content = '\n'.join(lines[1:])

        # 尝试解析JSON
        try:
            table_data = json.loads(content)
            logger.info(f"✅ JSON解析成功")
            logger.info(f"   数据条数: {len(table_data.get('years', []))} 条")
        except json.JSONDecodeError as je:
            logger.error(f"❌ JSON解析失败: {je}")
            logger.error(f"   返回内容: {content[:500]}")
            return {
                'success': False,
                'error': f'数据格式错误，JSON解析失败: {str(je)}'
            }

        # 保存到数据库 (使用 table1 字段，保存为JSON字符串)
        doc.table1 = json.dumps(table_data, ensure_ascii=False)
        doc.save(update_fields=['table1'])

        logger.info(f"✅ 退保价值表已更新到数据库 (table1字段)")
        logger.info(f"   数据条数: {len(table_data.get('years', []))} 条")
        logger.info(f"   数据预览: {json.dumps(table_data, ensure_ascii=False)[:200]}...")
        logger.info("="*80)

        return {
            'success': True,
            'table1': table_data,
            'message': '退保价值表更新成功'
        }

    except Exception as e:
        logger.error(f"❌ 处理退保价值表时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': f'处理失败: {str(e)}'
        }


@api_view(['POST'])
def update_surrender_value_table(request, document_id):
    """
    API视图：更新文档的退保价值表 (table1字段)
    使用DeepSeek API根据tablesummary和OCR内容提取退保价值表数据

    返回:
    {
        "status": "success",
        "table1": {...}  # 退保价值表JSON数据
    }
    """
    result = process_surrender_value_table(document_id)

    if result['success']:
        return Response({
            'status': 'success',
            'table1': result.get('table1', ''),
            'message': result.get('message', '退保价值表更新成功')
        })
    else:
        return Response({
            'status': 'error',
            'message': result.get('error', '更新失败')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def process_wellness_table(document_id):
    """
    核心函数：处理文档的无忧选退保价值表提取逻辑

    Args:
        document_id: 文档ID

    Returns:
        dict: {
            'success': bool,
            'table2': dict or str,  # 成功时返回dict，未找到时返回''
            'message': str,
            'error': str (if failed)
        }
    """
    try:
        # 获取文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            return {
                'success': False,
                'error': f'文档 {document_id} 不存在'
            }

        logger.info("="*80)
        logger.info(f"🔄 处理无忧选退保价值表 (table2字段)")
        logger.info(f"   文档ID: {document_id}")
        logger.info(f"   文档名称: {doc.file_name}")

        # 检查文档内容
        if not doc.content:
            return {
                'success': False,
                'error': '文档内容为空，无法生成无忧选退保价值表'
            }

        # 检查tablesummary
        if not doc.tablesummary:
            return {
                'success': False,
                'error': 'tablesummary字段为空，请先更新表格概要'
            }

        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            logger.error('❌ DEEPSEEK_API_KEY环境变量未设置')
            return {
                'success': False,
                'error': 'API密钥未配置'
            }

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 第一步：判断是否存在包含"非保证入息"或"入息"字段的表格
        check_prompt = f"""

表格概要（tablesummary）：
{doc.tablesummary}

请仔细分析表格概要，判断是否有包含与"提取"或"入息"或"无忧选"相关字段的表格。

只需要回答：
- 如果存在这样的表格，请返回表格的名称和表格行数以及表格基本字段
- 如果存在两个以上这样的表格，请返回最完整的那个表格的信息，也就是行数最多的那个表
- 如果不存在这样的表格，请返回0

"""

        logger.info("="*80)
        logger.info("⏳ 第一步：调用 DeepSeek API 判断是否存在包含入息的表格")
        logger.info(f"   表格概要长度: {len(doc.tablesummary)} 字符")

        # 第一次API调用：判断是否存在相关表格
        check_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "请根据以下多个表格的概要信息，判断是否存在包含特定字段的表格。"
                },
                {
                    "role": "user",
                    "content": check_prompt
                }
            ],
            temperature=0.1,
            max_tokens=200
        )

        has_wellness_table = check_response.choices[0].message.content.strip()
        logger.info(f"📦 DeepSeek 判断结果: {has_wellness_table}")

        # 如果不存在相关表格，返回空字符串
        if has_wellness_table == 0 or has_wellness_table.lower() in ['0', '不存在', '没有']:
            logger.info("ℹ️  未找到包含非保证入息或入息的表格")
            doc.table2 = ''
            doc.save(update_fields=['table2'])

            return {
                'success': True,
                'table2': '',
                'message': '未找到无忧选退保价值表（无包含入息的表格）'
            }

        # 第二步：如果存在相关表格，提取数据
        logger.info("="*80)
        logger.info("⏳ 第二步：调用 DeepSeek API 提取无忧选退保价值表数据")
        logger.info(f"   OCR内容长度: {len(doc.content)} 字符")
        logger.info(f"   使用内容长度: {min(len(doc.content), 220000)} 字符")

        extract_prompt = f"""从计划书内容中提取无忧选退保价值表数据（也就是数据字段包含非保证入息或入息的表）。

表格名称：{has_wellness_table}

要求：
1. 根据实际表格基本字段灵活判断，提取以下字段：保单年度终结,该年非保证入息,累计已支付非保证入息,行使无忧选后的退保价值(总额)
2. 以JSON格式返回，格式如下：

{{
  "years": [
    {{"policy_year": 1, "withdraw":1000 ,"withdraw_total": 1000,"total":1500 }},
    {{"policy_year": 2, "withdraw":1000 ,"withdraw_total": 2000,"total":2500 }}
  ]
}}

计划书内容：
{doc.content[:120000]}

请直接返回JSON格式数据，不要包含任何其他文字或markdown标记。"""

        # logger.info(extract_prompt)
        # 第二次API调用：提取表格数据
        extract_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档数据提取助手，擅长从文档中提取结构化的表格数据。你必须返回严格符合要求的JSON格式数据。"
                },
                {
                    "role": "user",
                    "content": extract_prompt
                }
            ],
            temperature=0.1,
            max_tokens=8000
        )

        # 提取结果
        content = extract_response.choices[0].message.content.strip()
        logger.info(f"📦 DeepSeek API返回，长度: {len(content)} 字符")

        # 清理可能的代码块标记
        if content.startswith('```'):
            lines = content.split('\n')
            # 移除第一行（```json 或 ```）和最后一行（```）
            if len(lines) > 2 and lines[-1].strip() == '```':
                content = '\n'.join(lines[1:-1])
            elif len(lines) > 1:
                content = '\n'.join(lines[1:])

        # 尝试解析JSON
        try:
            table_data = json.loads(content)
            logger.info(f"✅ JSON解析成功")
            logger.info(f"   数据条数: {len(table_data.get('years', []))} 条")
        except json.JSONDecodeError as je:
            logger.error(f"❌ JSON解析失败: {je}")
            logger.error(f"   返回内容: {content[:500]}")
            return {
                'success': False,
                'error': f'数据格式错误，JSON解析失败: {str(je)}'
            }

        # 保存到数据库 (使用 table2 字段，保存为JSON字符串)
        doc.table2 = json.dumps(table_data, ensure_ascii=False)
        doc.save(update_fields=['table2'])

        logger.info(f"✅ 无忧选退保价值表已更新到数据库 (table2字段)")
        logger.info(f"   数据条数: {len(table_data.get('years', []))} 条")
        logger.info(f"   数据预览: {json.dumps(table_data, ensure_ascii=False)[:200]}...")
        logger.info("="*80)

        return {
            'success': True,
            'table2': table_data,
            'message': '无忧选退保价值表更新成功'
        }

    except Exception as e:
        logger.error(f"❌ 处理无忧选退保价值表时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': f'处理失败: {str(e)}'
        }


@api_view(['POST'])
def update_wellness_table(request, document_id):
    """
    API视图：更新文档的无忧选退保价值表 (table2字段)
    使用DeepSeek API根据tablesummary和OCR内容提取无忧选退保价值表数据

    返回:
    {
        "status": "success",
        "table2": {...}  # 无忧选退保价值表JSON数据，如果没有则返回空字符串
    }
    """
    result = process_wellness_table(document_id)

    if result['success']:
        return Response({
            'status': 'success',
            'table2': result.get('table2', ''),
            'message': result.get('message', '无忧选退保价值表更新成功')
        })
    else:
        return Response({
            'status': 'error',
            'message': result.get('error', '更新失败')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_plan_summary(request, document_id):
    """
    API视图：更新文档的计划书概要 (summary字段)
    调用DeepSeek API，基于OCR内容、table1和table2数据生成计划书概要

    返回:
    {
        "status": "success",
        "summary": "..."  # Markdown格式的计划书概要
    }
    """
    from api.deepseek_service import extract_plan_summary
    import json

    try:
        # 获取文档
        doc = PlanDocument.objects.get(id=document_id)

        # 解析table1数据
        table1_data = None
        if doc.table1:
            try:
                table1_data = json.loads(doc.table1) if isinstance(doc.table1, str) else doc.table1
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"⚠️ 文档 {document_id} 的table1数据解析失败")

        # 解析table2数据
        table2_data = None
        if doc.table2:
            try:
                table2_data = json.loads(doc.table2) if isinstance(doc.table2, str) else doc.table2
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"⚠️ 文档 {document_id} 的table2数据解析失败")

        # 调用DeepSeek生成概要
        summary_text = extract_plan_summary(
            doc.content,
            table1_data,
            doc.annual_premium,
            doc.payment_years,
            table2_data,
            doc.insured_age
        )

        if summary_text and len(summary_text.strip()) > 0:
            # 保存到数据库
            doc.summary = summary_text
            doc.save(update_fields=['summary'])

            logger.info(f"✅ 文档 {document_id} 计划书概要更新成功，长度: {len(summary_text)}")

            return Response({
                'status': 'success',
                'summary': summary_text,
                'message': '计划书概要更新成功'
            })
        else:
            logger.error(f"❌ 文档 {document_id} 计划书概要生成失败")
            return Response({
                'status': 'error',
                'message': '计划书概要生成失败，DeepSeek返回空内容'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except PlanDocument.DoesNotExist:
        return Response({
            'status': 'error',
            'message': f'文档 {document_id} 不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ 更新计划书概要时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'更新失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
