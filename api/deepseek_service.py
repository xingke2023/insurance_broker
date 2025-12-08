import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

def extract_plan_data_from_text(text_content):
    """
    使用DeepSeek API从PDF文本中提取结构化数据
    """
    # 从环境变量获取API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError('DEEPSEEK_API_KEY环境变量未设置')

    # 初始化DeepSeek客户端（使用OpenAI SDK格式）
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    # 构建提示词
    prompt = f"""
请分析以下保险计划书内容，提取关键信息并以JSON格式返回。

需要提取的字段：
- insured_name: 擬受保人（被保人姓名）
- insured_age: 擬受保人（被保人姓名）年龄（数字）
- insured_gender: 擬受保人（被保人姓名）性别（男/女）
- insurance_product: 保险产品名称（基本計劃）
- insurance_company: 保险公司名称
- sum_assured: 名義金額（保额）（数字）
- annual_premium: 投保時每年保费（数字）
- payment_years: 保費繳付年期（保費繳付期）（如：20年、终身等）
- insurance_period: 保障至年齡、保障年期（如：终身、至70岁等）

请以JSON格式返回，如果某个字段无法从文本中提取，请设置为null。
注意事项：投保時每年總保費可能会有折扣，这只是第一年的折扣，请提取投保時每年保费的原始金额作为annual_premium。

计划书内容：
{text_content[:4000]}  # 限制文本长度

请直接返回JSON，不要包含其他说明文字。
"""

    try:
        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险计划书分析助手，擅长从保险计划书中提取结构化数据。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=1000
        )

        # 获取响应内容
        content = response.choices[0].message.content.strip()

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

        return {
            'success': True,
            'data': extracted_data,
            'raw_response': response.choices[0].message.content
        }

    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'JSON解析失败: {str(e)}',
            'raw_response': response.choices[0].message.content if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'API调用失败: {str(e)}'
        }


def analyze_insurance_table(ocr_content):
    """
    分析保险计划书内容，提取保单年度终结数据

    Args:
        ocr_content: OCR识别的文本内容

    Returns:
        dict: 包含年度价值表的JSON数据，格式如下：
        {
            "years": [
                {
                    "policy_year": 1,
                    "guaranteed_cash_value": 1000.00,
                    "total": 1500.00
                },
                ...
            ]
        }
    """
    try:
        # 从环境变量获取API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        logger.info(f"🔑 API Key检查: {'已配置' if api_key else '未配置'}")

        if not api_key:
            logger.warning('⚠️  DEEPSEEK_API_KEY环境变量未设置，使用模拟数据')
            logger.info('💡 提示：请在.env文件中配置 DEEPSEEK_API_KEY=sk-your-key-here')
            mock_result = mock_analyze_insurance_table(ocr_content)
            logger.info(f"📦 Mock数据返回: {mock_result is not None}, 记录数: {len(mock_result.get('years', [])) if mock_result else 0}")
            return mock_result

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 构建提示词
        prompt = f"""
请分析以下保险计划书的OCR识别内容，提取保单年度终结数据。

要求提取的字段：
1. 保單年度終結 (policy_year) - 文本（可能是数字，也可能是年龄比如65歲）
2. 退保價值（或退保發還金額）下的保證保證金額 (guaranteed_cash_value) - 整数
3. 退保價值（或退保發還金額）下的总额 (total) - 整数

请以JSON格式输出，格式如下：
{{
    "years": [
        {{
            "policy_year": 1,
            "guaranteed_cash_value": 1000.00,
            
            "total": 1500.00
        }},
        {{
            "policy_year": 65歲,
            "guaranteed_cash_value": 2100.00,
            
            "total": 3150.00
        }}
    ]
}}

注意：
- 提取所有table的保單年度終結數據進行匯總，要遍历文档，有可能后面还有相关表格
- 只返回JSON数据，不要其他说明
- 如果某个值不存在或无法识别，使用null
- 按年度顺序排列

OCR识别内容：
{ocr_content}
"""

        logger.info("⏳ 开始调用 DeepSeek API 分析年度价值表")
        logger.info(f"📤 发送内容长度: {len(ocr_content)} 字符")

        # 打印完整的prompt
        logger.info("="*80)
        logger.info("📝 发送给DeepSeek的完整Prompt:")
        logger.info("="*80)
        logger.info(prompt)
        logger.info("="*80)

        import time
        start_time = time.time()

        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险计划书文档分析助手，擅长从保险计划书中提取保单年度终结数据。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=8192,  # 设置为8192以支持更长的年度价值表
            timeout=300  # 设置300秒(5分钟)超时
        )

        elapsed_time = time.time() - start_time
        logger.info(f"⏱️  API调用耗时: {elapsed_time:.2f} 秒")

        # 获取响应内容
        content = response.choices[0].message.content.strip()
        logger.info(f"📥 DeepSeek API 返回内容长度: {len(content)} 字符")
        logger.info(f"📥 返回内容预览: {content[:300]}...")

        # 尝试解析JSON
        # 移除可能的markdown代码块标记
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()

        table_data = json.loads(content)
        logger.info(f"成功解析年度价值表，共 {len(table_data.get('years', []))} 条记录")
        return table_data

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON解析失败: {e}")
        logger.error(f"原始内容长度: {len(content) if 'content' in locals() else 0}")
        logger.error(f"原始内容(最后500字符): ...{content[-500:] if 'content' in locals() else 'N/A'}")
        logger.error("💡 提示：JSON可能被截断，尝试增加max_tokens参数")
        return None
    except Exception as e:
        logger.error(f"❌ 调用DeepSeek API时发生错误:")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def mock_analyze_insurance_table(ocr_content):
    """
    模拟分析函数，用于测试
    返回模拟的年度价值表数据
    """
    logger.info("使用模拟数据进行测试")

    # 返回模拟数据
    return {
        "years": [
            {
                "policy_year": 1,
                "guaranteed_cash_value": 5000.00,
                "terminal_bonus": 1000.00,
                "total": 6000.00
            },
            {
                "policy_year": 2,
                "guaranteed_cash_value": 10500.00,
                "terminal_bonus": 2200.00,
                "total": 12700.00
            },
            {
                "policy_year": 3,
                "guaranteed_cash_value": 16200.00,
                "terminal_bonus": 3500.00,
                "total": 19700.00
            },
            {
                "policy_year": 5,
                "guaranteed_cash_value": 28500.00,
                "terminal_bonus": 6000.00,
                "total": 34500.00
            },
            {
                "policy_year": 10,
                "guaranteed_cash_value": 62000.00,
                "terminal_bonus": 13000.00,
                "total": 75000.00
            }
        ]
    }


def extract_plan_summary(ocr_content, table1_data=None, annual_premium=None, payment_years=None, table2_data=None, insured_age=None):
    """
    使用DeepSeek提取计划书概要（纯文本Markdown格式）

    Args:
        ocr_content: OCR识别的文本内容
        table1_data: 退保价值表数据（dict），用于计算投资回报里程碑
        annual_premium: 年保费（用于计算成本）
        payment_years: 缴费年期（用于计算总成本）
        table2_data: 无忧选退保价值表（dict），用于收入提取规划
        insured_age: 被保人当前年龄

    Returns:
        str: 计划书概要文本（Markdown格式），失败返回空字符串
    """
    try:
        # 从环境变量获取API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        logger.info(f"🔑 API Key检查: {'已配置' if api_key else '未配置'}")

        if not api_key:
            logger.error('❌ DEEPSEEK_API_KEY环境变量未设置')
            return ''

        if not ocr_content or len(ocr_content.strip()) == 0:
            logger.error('❌ OCR内容为空，无法提取概要')
            return ''

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 准备退保价值表数据用于分析
        import json
        table1_section = ''
        if table1_data and annual_premium and payment_years:
            total_cost = annual_premium * payment_years
            table1_json = json.dumps(table1_data, ensure_ascii=False, indent=2)

            # 添加年龄计算说明
            age_calculation_note = ""
            if insured_age:
                age_calculation_note = f"""
- **被保人投保年龄**: {insured_age}岁
- **年龄计算公式**: 被保人年龄 = 投保年龄 + 保单年度
  - 例如：投保时{insured_age}岁，保单年度1 = {insured_age + 1}岁，保单年度2 = {insured_age + 2}岁
  - 如果要查找45岁时的数据，应查找保单年度{45 - insured_age}的数据
  - 如果要查找65岁时的数据，应查找保单年度{65 - insured_age}的数据
"""

            table1_section = f"""

## 退保价值表数据（用于分析投资回报）
- 年保费: ${annual_premium:,.0f}
- 缴费年期: {payment_years}年
- 总成本: ${total_cost:,.0f}
{age_calculation_note}
**重要提醒**：
- policy_year字段是保单年度（第几年），不是年龄
- 年龄与保单年度的关系：被保人年龄 = 投保年龄 + 保单年度
- 如果policy_year显示为"65岁"或"65歲"等文本，这表示被保人年龄到达65岁时的数据
- 要根据投保年龄反推保单年度：保单年度 = 目标年龄 - 投保年龄

退保价值表JSON数据：
```json
{table1_json}
```
"""
            logger.info(f"📊 已添加退保价值表数据到prompt，数据行数: {len(table1_data.get('years', []))}")

        # 准备无忧选退保价值表数据用于收入规划
        table2_section = ''
        if table2_data and insured_age:
            table2_json = json.dumps(table2_data, ensure_ascii=False, indent=2)
            table2_section = f"""

## 无忧选退保价值表数据（用于收入提取规划）
- **被保人投保年龄**: {insured_age}岁
- **年龄计算公式**: 被保人年龄 = 投保年龄 + 保单年度
  - 例如：投保时{insured_age}岁，保单年度1 = {insured_age + 1}岁，保单年度35 = {insured_age + 35}岁
  - 如果要查找60岁（退休年龄）的数据，应查找保单年度{60 - insured_age}的数据
  - 如果要查找65岁（退休年龄）的数据，应查找保单年度{65 - insured_age}的数据

**重要提醒**：
- policy_year字段是保单年度（第几年），不是年龄
- 要计算特定年龄的数据，使用公式：保单年度 = 目标年龄 - 投保年龄

无忧选退保价值表JSON数据：
```json
{table2_json}
```
"""
            logger.info(f"💰 已添加无忧选表数据到prompt，数据行数: {len(table2_data.get('years', []))}")

        prompt = f"""
请分析以下保险计划书的完整内容，生成一个简洁易懂的计划书概要，概要是客户比较关注的问题，也是可以打动客户的点。

请严格按照以下Markdown格式生成概要，注意美观排版，使用表格、引用块、emoji等增强可读性：

# 📋 保险计划书概要

---

## 1. 💡 计划书概述

用100-200字简洁明了地说明这是什么产品、适合谁、主要功能。语言要通俗易懂，突出核心价值。

---

## 2. 🔑 关键信息

<table>
  <tr>
    <td><strong>💰 保额</strong></td>
    <td>$XXX,XXX</td>
  </tr>
  <tr>
    <td><strong>📅 缴费年期</strong></td>
    <td>XX年</td>
  </tr>
  <tr>
    <td><strong>🛡️ 保障期限</strong></td>
    <td>终身/XX岁</td>
  </tr>
  <tr>
    <td><strong>💵 年保费</strong></td>
    <td>$XXX,XXX</td>
  </tr>
  <tr>
    <td><strong>💳 总保费</strong></td>
    <td>$XXX,XXX</td>
  </tr>
</table>

---

## 3. 📈 投资回报里程碑

根据退保价值表数据计算的关键时间节点：

<table>
  <thead>
    <tr>
      <th align="center">🎯 里程碑</th>
      <th align="center">📅 保单年度</th>
      <th align="right">💰 总价值</th>
      <th align="right">📊 IRR</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>✅ 回本</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">X.X%</td>
    </tr>
    <tr>
      <td align="center"><strong>🎯 2倍回报</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">X.X%</td>
    </tr>
    <tr>
      <td align="center"><strong>🚀 4倍回报</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">X.X%</td>
    </tr>
    <tr>
      <td align="center"><strong>⭐ 8倍回报</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">X.X%</td>
    </tr>
    <tr>
      <td align="center"><strong>💎 16倍回报</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">X.X%</td>
    </tr>
    <tr style="background-color: #f0f8ff;">
      <td align="center"><strong>🏆 80年价值</strong></td>
      <td align="center">第80年</td>
      <td align="right">$XXX,XXX (X.X倍)</td>
      <td align="right">X.X%</td>
    </tr>
  </tbody>
</table>

> 💡 **IRR计算说明**：IRR = (总价值 / 总成本)^(1 / 保单年度) - 1
> ⚠️ **注意**：policy_year可能是数字或"XX岁"格式，请正确解析。如果某个倍数未达到，标注"未达到"。

---

## 4. 💰 收入提取规划

> ⚠️ **极其重要：保单年度≠年龄！**
> - `policy_year` 是保单年度（第几年），不是年龄
> - 计算公式：被保人年龄 = 投保年龄 + policy_year
> - 反向计算：policy_year = 目标年龄 - 投保年龄
>
> 📝 **示例**（投保时30岁）：
> - 查找"65岁退休"数据 → policy_year = 35（第35年）
> - 查找"60岁退休"数据 → policy_year = 30（第30年）

### 📋 提取方案概览

<table>
  <tr>
    <td><strong>📅 提取开始</strong></td>
    <td>第X年（被保人X岁）</td>
  </tr>
  <tr>
    <td><strong>💵 每年提取</strong></td>
    <td>$XXX,XXX</td>
  </tr>
</table>

### 🎯 关键里程碑节点

<table>
  <thead>
    <tr>
      <th align="center">🎂 年龄节点</th>
      <th align="center">📅 保单年度</th>
      <th align="right">💰 已提取累计</th>
      <th align="right">🏦 保单剩余价值</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><strong>🎓 60岁（退休初期）</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">$XXX,XXX</td>
    </tr>
    <tr>
      <td align="center"><strong>🏖️ 65岁（退休中期）</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">$XXX,XXX</td>
    </tr>
    <tr>
      <td align="center"><strong>🌟 其他关键节点</strong></td>
      <td align="center">第X年</td>
      <td align="right">$XXX,XXX</td>
      <td align="right">$XXX,XXX</td>
    </tr>
  </tbody>
</table>

> 💡 **字段说明**：
> - `withdraw`：每年提取金额
> - `withdraw_total`：累计已提取总额
> - `total`：保单剩余价值（扣除提取后）
> - 必须先根据"投保年龄"计算出正确的 policy_year
> - 如果没有 table2 数据，则跳过此部分

---

## 5. ✨ 保障亮点

<div style="padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white;">

### 核心优势

</div>

- 🛡️ **亮点1**：xxx（详细说明产品的独特保障特性）
- 💎 **亮点2**：xxx（强调与竞品的差异化优势）
- 🎁 **亮点3**：xxx（突出客户最关心的价值点）

---

## 6. 📊 收益说明

<div style="padding: 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 8px; color: white;">

### 收益特点

</div>

- 💹 **收益1**：xxx（说明收益的稳定性和保证性）
- 🎯 **收益2**：xxx（解释非保证收益的潜在空间）
- 🌈 **收益3**：xxx（强调长期持有的复利效应）

---

<div style="text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;">
  <p style="color: #6c757d; font-size: 14px;">
    📞 如需详细咨询，请联系您的保险顾问<br/>
    ⏰ 以上数据基于当前计划书，实际收益以保险公司最终核保为准
  </p>
</div>
{table1_section}{table2_section}
计划书内容：
{ocr_content[:8000]}

请直接返回Markdown格式的概要，不要包含```代码块标记。
"""

        logger.info("📝 正在调用DeepSeek API提取计划书概要...")
        logger.info(f"📤 OCR内容长度: {len(ocr_content)} 字符")

        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险计划书分析助手，擅长从保险计划书中提取关键信息并生成简洁易懂的Markdown格式概要。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )

        # 获取响应内容
        content = response.choices[0].message.content.strip()
        logger.info(f"📥 收到DeepSeek响应，长度: {len(content)} 字符")

        # 检查是否为空
        if not content or len(content.strip()) == 0:
            logger.error('❌ DeepSeek返回空内容')
            return ''

        # 移除可能的markdown代码块标记
        if content.startswith('```'):
            lines = content.split('\n')
            if lines[0].strip() in ['```', '```text', '```markdown', '```md']:
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            content = '\n'.join(lines).strip()

        # 最终检查
        if not content or len(content.strip()) == 0:
            logger.error('❌ 处理后内容为空')
            return ''

        logger.info(f"✅ 计划书概要提取成功，最终长度: {len(content)} 字符")
        logger.info(f"📄 概要预览(前100字符): {content[:100]}")
        return content

    except Exception as e:
        logger.error(f'❌ 提取计划书概要时发生异常: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return ''


def extract_table_summary(ocr_content):
    """
    使用DeepSeek分析OCR内容中的表格结构
    提取表格的名称、行数、字段信息

    Args:
        ocr_content: OCR识别的完整文本内容

    Returns:
        str: 表格概要文本，格式化后的多行文本
    """
    # 从环境变量获取API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        logger.error('❌ DEEPSEEK_API_KEY环境变量未设置')
        return ''

    # 初始化DeepSeek客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    # 构建提示词
    prompt = f"""以保单年度终结为坐标，分析以下保险计划书中的所有表格。

要求：
1. 识别所有以"保单年度终结"为坐标的表格
2. 有些表格可能跨度好几个页面，但只算一张表
3. 对每个表格提取：表详细名称、行数、基本字段

只输出结果，不要有任何解释说明。

输出格式示例：
1.
表名：詳細說明 - 退保價值 (只根據基本計劃計算)
行数：100行
基本字段：保单年度终结,缴付保费总额,退保价值(保证金额(保证现金价值),非保證金額(续期红利),总额),累計已支付非保證入息+總退保價值

2.
表名：身故賠償
行数：50行
基本字段：保单年度终结,身故赔偿(保证金额,非保证金额,总额)

计划书内容：
{ocr_content[:12000]}

请直接返回分析结果，不要包含markdown代码块标记。"""

    try:
        logger.info(f"🔍 开始调用DeepSeek API提取表格概要...")
        logger.info(f"📄 OCR内容长度: {len(ocr_content)} 字符")

        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的保险文档分析助手，擅长识别和分析表格结构。"},
                {"role": "user", "content": prompt}
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
            return ''

        logger.info(f"✅ 表格概要提取成功，最终长度: {len(content)} 字符")
        logger.info(f"📄 概要预览(前200字符): {content[:200]}")
        return content

    except Exception as e:
        logger.error(f'❌ 提取表格概要时发生异常: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return ''
