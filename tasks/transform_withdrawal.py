#!/usr/bin/env python3
"""
从md*.json提取款项提取（Withdrawal）场景的数据

输入：md*.json (带Withdrawal选项的projection数据)
输出：简化的行式存储格式

重要说明：
- 提取的是"当前假设情景"（Current/Mid Scenario）数据
- 不是"悲观情景"（Low Scenario）数据
- 使用无Low/High后缀的列（如colAfterWDNotionalAmount）
"""

import json
import sys


def transform_withdrawal_data(md_data):
    """
    提取款项提取场景的数据

    Args:
        md_data: 解析后的md*.json数据

    Returns:
        dict: 提取后的数据结构
    """

    # 找到包含Withdrawal选项的projection
    withdrawal_proj = None
    for proj in md_data['projections']:
        if 'Withdrawal' in proj.get('policyOptions', []):
            withdrawal_proj = proj
            break

    if not withdrawal_proj:
        raise ValueError("未找到包含Withdrawal选项的projection")

    # 提取columns数组
    columns = withdrawal_proj['columns']

    # 建立列名到Values数组的映射
    column_map = {col['Name']: col['Values'] for col in columns}

    # 定义字段映射关系
    column_mappings = {
        'policy_year': 'columnYear',                           # 保单年度
        'premiums_paid': 'colAccumulateAnnualizedPremium',    # 累计已缴保费
        'withdrawal_amount': 'colCurrentTotalWithdrawalAmount',  # 该年提取款项
        'accumulated_withdrawal': 'colAccumulatedTotalWithdrawalAmount',  # 累计提取款项
        'notional_amount': 'colAfterWDNotionalAmount',        # 提取后名义金额
        'guaranteed': 'colGuaranteedCashValue',               # 保证现金价值
        'non_guaranteed': 'colNonGuaranteedSurrender',        # 非保证退保价值
        'total_surrender': 'colTotalSurrender'                # 退保价值
    }

    # 按年度遍历，提取每年的数据
    result = {'withdrawal': []}

    # 获取年度数量
    year_count = len(column_map.get('columnYear', []))

    print(f"处理 {year_count} 个年度的Withdrawal数据...")

    for i in range(year_count):
        year_data = {}

        # 提取每个字段的值
        for output_field, input_column in column_mappings.items():
            if input_column in column_map:
                value = column_map[input_column][i].get('value')
                year_data[output_field] = value
            else:
                print(f"警告: 列 '{input_column}' 不存在，字段 '{output_field}' 设为 0")
                year_data[output_field] = 0

        result['withdrawal'].append(year_data)

    return result


def main():
    # 文件路径
    input_file = 'md4.json'
    output_file = 'md4_withdrawal.json'

    # 支持命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print(f"读取输入文件: {input_file}")

    try:
        # 1. 读取md*.json
        with open(input_file, 'r', encoding='utf-8') as f:
            md_data = json.load(f)

        print(f"✓ 成功读取文件")
        print(f"产品代码: {md_data.get('product', {}).get('code', 'N/A')}")
        print(f"数据类型: 款项提取（Withdrawal）")
        print(f"投资假设: 当前假设情景（非悲观/乐观情景）")

        # 2. 转换数据
        result = transform_withdrawal_data(md_data)

        print(f"✓ 转换完成，共 {len(result['withdrawal'])} 条记录")

        # 3. 输出到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ 已保存到: {output_file}")

        # 4. 显示关键记录作为预览
        print("\n关键年度预览：")
        print()
        print("年度 | 该年提取 | 累计提取 | 名义金额 | 退保价值")
        print("-" * 65)

        # 显示有提取款项的年份（前10次）
        count = 0
        for record in result['withdrawal']:
            if record['withdrawal_amount'] > 0 and count < 10:
                print(f"{record['policy_year']:4d} | "
                      f"{record['withdrawal_amount']:8,} | "
                      f"{record['accumulated_withdrawal']:8,} | "
                      f"{record['notional_amount']:8,} | "
                      f"{record['total_surrender']:12,}")
                count += 1

        # 验证第80年的数据
        print("\n第80年数据验证：")
        year_80 = result['withdrawal'][79]  # 索引79是第80年
        print(f"  该年提取款项总额: {year_80['withdrawal_amount']:,}")
        print(f"  款项提取后的名义金额: {year_80['notional_amount']:,}")
        print(f"  款项提取后的退保价值: {year_80['total_surrender']:,}")

        return 0

    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
        return 1
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}")
        return 1
    except ValueError as e:
        print(f"错误: {e}")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
