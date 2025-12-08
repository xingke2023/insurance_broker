"""
保险公司配置文件
定义不同保险公司的数据提取规则和提示词
"""

INSURANCE_COMPANIES = {
    'aia': {
        'name': '友邦保险（AIA）',
        'code': 'aia',
        'logo': '🏢',
        'color': 'blue',
        'table_keywords': [
            '保单年度终结', '保证现金价值', '非保证现金价值', '总现金价值',
            'Policy Year', 'Guaranteed Cash Value', 'Non-Guaranteed Cash Value', 'Total Cash Value'
        ],
        'field_mappings': {
            'policy_year': ['保单年度终结', '保单年度', 'Policy Year End'],
            'guaranteed_value': ['保证现金价值', '保证价值', 'Guaranteed Cash Value'],
            'non_guaranteed_value': ['非保证现金价值', '非保证价值', '红利', 'Non-Guaranteed Cash Value'],
            'total_value': ['总现金价值', '退保价值', '总价值', 'Total Cash Value', 'Surrender Value']
        },
        'extraction_notes': '友邦计划书通常包含详细的年度价值表，注意区分保证和非保证价值'
    },
    'prudential': {
        'name': '保诚保险（Prudential）',
        'code': 'prudential',
        'logo': '🏛️',
        'color': 'red',
        'table_keywords': [
            '保单年度', '保证现金价值', '预期红利', '总现金价值',
            'Year', 'Guaranteed', 'Projected Bonus', 'Total'
        ],
        'field_mappings': {
            'policy_year': ['保单年度', '年度', 'Year'],
            'guaranteed_value': ['保证现金价值', '保证金额', 'Guaranteed'],
            'non_guaranteed_value': ['预期红利', '非保证红利', 'Projected Bonus'],
            'total_value': ['总现金价值', '总价值', 'Total Cash Value']
        },
        'extraction_notes': '保诚计划书的红利称为"预期红利"，需要特别识别'
    },
    'manulife': {
        'name': '宏利保险（Manulife）',
        'code': 'manulife',
        'logo': '🌳',
        'color': 'green',
        'table_keywords': [
            '保单年度终结', '保证现金价值', '非保证终期红利', '总现金价值',
            'End of Policy Year', 'Guaranteed', 'Non-Guaranteed Terminal Bonus', 'Total'
        ],
        'field_mappings': {
            'policy_year': ['保单年度终结', '保单年度', 'End of Policy Year'],
            'guaranteed_value': ['保证现金价值', 'Guaranteed Cash Value'],
            'non_guaranteed_value': ['非保证终期红利', '终期红利', 'Terminal Bonus'],
            'total_value': ['总现金价值', 'Total Cash Value']
        },
        'extraction_notes': '宏利的非保证部分称为"终期红利"'
    },
    'sunlife': {
        'name': '永明金融（Sun Life）',
        'code': 'sunlife',
        'logo': '☀️',
        'color': 'yellow',
        'table_keywords': [
            '保单周年', '保证现金价值', '归原红利', '总现金价值',
            'Policy Anniversary', 'Guaranteed', 'Reversionary Bonus', 'Total'
        ],
        'field_mappings': {
            'policy_year': ['保单周年', '保单年度', 'Policy Anniversary'],
            'guaranteed_value': ['保证现金价值', 'Guaranteed'],
            'non_guaranteed_value': ['归原红利', '周年红利', 'Reversionary Bonus'],
            'total_value': ['总现金价值', 'Total Cash Value']
        },
        'extraction_notes': '永明的红利称为"归原红利"'
    },
    'ftlife': {
        'name': '富通保险（FTLife）',
        'code': 'ftlife',
        'logo': '💎',
        'color': 'purple',
        'table_keywords': [
            '保单年度终结', '保证现金价值', '非保证现金价值', '总现金价值'
        ],
        'field_mappings': {
            'policy_year': ['保单年度终结', '保单年度'],
            'guaranteed_value': ['保证现金价值', '保证金额'],
            'non_guaranteed_value': ['非保证现金价值', '红利'],
            'total_value': ['总现金价值', '退保价值']
        },
        'extraction_notes': '富通计划书格式较为标准，直接提取即可'
    },
    'china_life': {
        'name': '中国人寿（China Life）',
        'code': 'china_life',
        'logo': '🇨🇳',
        'color': 'red',
        'table_keywords': [
            '保单年度', '现金价值', '累计红利', '合计'
        ],
        'field_mappings': {
            'policy_year': ['保单年度', '年度'],
            'guaranteed_value': ['现金价值', '保证现金价值'],
            'non_guaranteed_value': ['累计红利', '红利'],
            'total_value': ['合计', '总现金价值']
        },
        'extraction_notes': '中国人寿的表格通常是纯中文，红利为"累计红利"'
    },
    'ping_an': {
        'name': '中国平安（Ping An）',
        'code': 'ping_an',
        'logo': '🛡️',
        'color': 'orange',
        'table_keywords': [
            '保单年度', '现金价值', '分红', '总额'
        ],
        'field_mappings': {
            'policy_year': ['保单年度', '年度'],
            'guaranteed_value': ['现金价值', '保证现金价值'],
            'non_guaranteed_value': ['分红', '累积分红'],
            'total_value': ['总额', '合计现金价值']
        },
        'extraction_notes': '平安的红利称为"分红"或"累积分红"'
    },
    'other': {
        'name': '其他保险公司',
        'code': 'other',
        'logo': '📋',
        'color': 'gray',
        'table_keywords': [
            '年度', '保证', '非保证', '总'
        ],
        'field_mappings': {
            'policy_year': ['保单年度', '年度', 'Year'],
            'guaranteed_value': ['保证', 'Guaranteed'],
            'non_guaranteed_value': ['非保证', '红利', 'Non-Guaranteed', 'Bonus'],
            'total_value': ['总', '合计', 'Total']
        },
        'extraction_notes': '使用通用规则提取，可能需要人工校验'
    }
}


def get_company_list():
    """获取保险公司列表"""
    return [
        {
            'code': company['code'],
            'name': company['name'],
            'logo': company['logo'],
            'color': company['color']
        }
        for company in INSURANCE_COMPANIES.values()
    ]


def get_company_config(company_code):
    """获取指定保险公司的配置"""
    return INSURANCE_COMPANIES.get(company_code, INSURANCE_COMPANIES['other'])


def generate_prompt_for_company(company_code, text_content):
    """根据保险公司生成定制化的提示词"""
    config = get_company_config(company_code)

    # 构建字段映射说明
    field_hints = []
    for field, keywords in config['field_mappings'].items():
        field_hints.append(f"   - {field}: 可能的列名包括: {', '.join(keywords)}")

    field_hints_text = '\n'.join(field_hints)

    prompt = f"""你正在分析 **{config['name']}** 的保险计划书。

【重要提示】：
{config['extraction_notes']}

【基本信息字段】：
1. customer_name: 客户/受保人姓名
2. customer_age: 客户年龄（数字）
3. customer_gender: 性别（男/女）
4. insurance_product: 保险产品名称
5. insurance_company: 保险公司名称（应为：{config['name']}）
6. insurance_amount: 保额/保险金额（数字，单位：元或美元）
7. premium_amount: 年缴保费（数字，单位：元）
8. payment_years: 缴费年期（数字，如20表示20年）
9. total_premium: 总保费（数字，单位：元）
10. insurance_period: 保险期限（如：终身、至70岁、20年等）

【年度价值表】（重要！）：
11. annual_values: 保单年度价值表数组，格式：
   [
     {{
       "policy_year": 1,
       "guaranteed_value": 1000,
       "non_guaranteed_value": 500,
       "total_value": 1500
     }},
     ...
   ]

【针对{config['name']}的字段映射】：
{field_hints_text}

【表格识别关键词】：
在文档中寻找包含以下关键词的表格：
{', '.join(config['table_keywords'])}

**提取规则**：
1. 必须提取完整的年度价值表，从第1年到最后一年
2. 数字字段返回纯数字（去除逗号、货币符号、单位）
3. 如果字段无法提取，设置为null
4. 年度价值表如果找不到，annual_values设置为空数组[]
5. 特别注意{config['name']}的表格格式和列名

**计划书内容**：
{text_content[:15000]}

请直接返回JSON格式，不要包含任何解释文字。"""

    return prompt
