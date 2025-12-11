#!/usr/bin/env python3
"""
从md5.json提取款项提取（Withdrawal + Realization）场景的数据

输入：md5.json (带Withdrawal和Realization选项的projection数据)
输出：简化的行式存储格式

重要说明：
- 使用Projection 3（policyOptions: ['Withdrawal', 'Realization']）
- 提取的是"当前假设情景"（Current/Mid Scenario）数据
- 不是"悲观情景"（Low Scenario）数据
- 使用无Low/High后缀的列

字段说明：
- 该年非保证提取款项：colNonGuaranteedWithdraw
- 保证现金价值：colGuaranteedCashValue
- 非保证金额B+C：colNonGuaranteedSurrender
- 总额：colTotalSurrender
"""

import json
import sys


def transform_md5_withdrawal_data(md_data):
    """
    提取md5款项提取场景的数据

    Args:
        md_data: 解析后的md5.json数据

    Returns:
        dict: 提取后的数据结构
    """

    # 使用Projection 3（Withdrawal + Realization）
    # md5的结构不同，需要找到正确的projection
    target_proj = None
    for proj in md_data['projections']:
        options = proj.get('policyOptions', [])
        if 'Withdrawal' in options and 'Realization' in options:
            target_proj = proj
            break

    # 如果没找到，尝试只有Realization的
    if not target_proj:
        for proj in md_data['projections']:
            if 'Realization' in proj.get('policyOptions', []):
                target_proj = proj
                print("警告: 未找到Withdrawal+Realization，使用Realization")
                break

    if not target_proj:
        raise ValueError("未找到包含Withdrawal或Realization选项的projection")

    # 提取columns数组
    columns = target_proj['columns']

    if not columns:
        raise ValueError("找到的projection没有数据列")

    # 建立列名到Values数组的映射
    column_map = {col['Name']: col['Values'] for col in columns}

    # 定义字段映射关系（md5特有）
    column_mappings = {
        'policy_year': 'columnYear',                           # 保单年度
        'premiums_paid': 'colAccumulateAnnualizedPremium',    # 累计已缴保费
        'non_guaranteed_withdrawal': 'colNonGuaranteedWithdraw',  # 该年非保证提取款项
        'accumulated_ng_withdrawal': 'colAccumulatedNonGuaranteedWithdrawal',  # 累计非保证提取
        'guaranteed': 'colGuaranteedCashValue',               # 保证现金价值
        'non_guaranteed_bc': 'colNonGuaranteedSurrender',     # 非保证金额B+C
        'total': 'colTotalSurrender'                          # 总额
    }

    # 按年度遍历，提取每年的数据
    result = {'withdrawal_realization': []}

    # 获取年度数量
    year_count = len(column_map.get('columnYear', []))

    print(f"处理 {year_count} 个年度的Withdrawal+Realization数据...")

    for i in range(year_count):
        year_data = {}

        # 提取每个字段的值
        for output_field, input_column in column_mappings.items():
            if input_column in column_map:
                value = column_map[input_column][i].get('value')
                year_data[output_field] = value if value is not None else 0
            else:
                print(f"警告: 列 '{input_column}' 不存在，字段 '{output_field}' 设为 0")
                year_data[output_field] = 0

        result['withdrawal_realization'].append(year_data)

    return result


def main():
    # 文件路径
    input_file = 'md5.json'
    output_file = 'md5_withdrawal.json'

    # 支持命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print(f"读取输入文件: {input_file}")

    try:
        # 1. 读取md5.json
        with open(input_file, 'r', encoding='utf-8') as f:
            md_data = json.load(f)

        print(f"✓ 成功读取文件")
        print(f"产品代码: {md_data.get('product', {}).get('code', 'N/A')}")
        print(f"数据类型: 款项提取 + Realization")
        print(f"投资假设: 当前假设情景（非悲观/乐观情景）")

        # 2. 转换数据
        result = transform_md5_withdrawal_data(md_data)

        print(f"✓ 转换完成，共 {len(result['withdrawal_realization'])} 条记录")

        # 3. 输出到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✓ 已保存到: {output_file}")

        # 4. 显示关键记录作为预览
        print("\n关键年度预览：")
        print()
        print("年度 | 非保证提取 | 累计非保证 | 保证价值 | 非保证B+C | 总额")
        print("-" * 75)

        # 显示有提取的年份和关键年份
        key_years = [5, 6, 7, 8, 9, 10, 20, 50, 80, 100]

        for year in key_years:
            if year <= len(result['withdrawal_realization']):
                record = result['withdrawal_realization'][year - 1]
                print(f"{record['policy_year']:4d} | "
                      f"{record['non_guaranteed_withdrawal']:10,} | "
                      f"{record['accumulated_ng_withdrawal']:10,} | "
                      f"{record['guaranteed']:8,} | "
                      f"{record['non_guaranteed_bc']:11,} | "
                      f"{record['total']:12,}")

        # 验证第80年的数据
        if len(result['withdrawal_realization']) >= 80:
            print("\n第80年数据详情：")
            year_80 = result['withdrawal_realization'][79]
            print(f"  该年非保证提取款项: {year_80['non_guaranteed_withdrawal']:,}")
            print(f"  累计非保证提取: {year_80['accumulated_ng_withdrawal']:,}")
            print(f"  保证现金价值: {year_80['guaranteed']:,}")
            print(f"  非保证金额B+C: {year_80['non_guaranteed_bc']:,}")
            print(f"  总额: {year_80['total']:,}")

            # 验证关系
            calc_total = year_80['guaranteed'] + year_80['non_guaranteed_bc']
            if abs(calc_total - year_80['total']) <= 1:
                print(f"  ✓ 验证: 保证 + 非保证B+C = 总额")
            else:
                print(f"  ⚠ 差异: {calc_total:,} vs {year_80['total']:,}")

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
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
