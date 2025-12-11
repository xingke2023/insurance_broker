#!/usr/bin/env python3
"""
从md3.json提取数据并转换为md31.json格式

输入：md3.json (列式存储的复杂结构)
输出：md31.json (行式存储的简化结构)
"""

import json
import sys


def transform_md3_to_md31(md3_data):
    """
    将md3.json转换为md31.json格式

    核心逻辑：
    1. 从md3的columns数组中找到目标列
    2. 按年度索引提取对应值
    3. 组装成新的扁平化结构

    Args:
        md3_data: 解析后的md3.json数据

    Returns:
        dict: md31格式的数据结构
    """

    # 1. 提取columns数组
    columns = md3_data['projections'][0]['columns']

    # 2. 构建列名到Values数组的映射
    column_map = {col['Name']: col['Values'] for col in columns}

    # 3. 定义字段映射关系（根据md31.json的字段）
    # 输出字段名 -> 输入列名
    column_mappings = {
        'policy_year': 'columnYear',                    # 保单年度
        'premiums_paid': 'colAccumulateAnnualizedPremium',  # 累计已缴保费
        'guaranteed': 'colGuaranteedCashValue',         # 保证现金价值
        'non_guaranteed': 'colNonGuaranteedSurrender',  # 非保证退保价值
        'total': 'colTotalSurrender'                    # 总退保价值
    }

    # 4. 按年度遍历，提取每年的数据
    result = {'standard': []}

    # 获取年度数量（使用第一列的长度）
    year_count = len(column_map.get('columnYear', []))

    print(f"处理 {year_count} 个年度的数据...")

    for i in range(year_count):
        year_data = {}

        # 提取每个字段的值
        for output_field, input_column in column_mappings.items():
            if input_column in column_map:
                value = column_map[input_column][i].get('value')
                year_data[output_field] = value
            else:
                # 如果列不存在，尝试计算或设为0
                if output_field == 'total' and 'guaranteed' in year_data and 'non_guaranteed' in year_data:
                    # total = guaranteed + non_guaranteed
                    year_data['total'] = year_data['guaranteed'] + year_data['non_guaranteed']
                else:
                    print(f"警告: 列 '{input_column}' 不存在，字段 '{output_field}' 设为 0")
                    year_data[output_field] = 0

        result['standard'].append(year_data)

    return result


def print_available_columns(md3_data):
    """打印md3.json中所有可用的列名"""
    columns = md3_data['projections'][0]['columns']
    print("\n可用的列名：")
    for col in columns:
        print(f"  - {col['Name']}")
    print()


def main():
    # 文件路径
    input_file = 'md3.json'
    output_file = 'md31_generated.json'

    # 支持命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    print(f"读取输入文件: {input_file}")

    try:
        # 1. 读取md3.json
        with open(input_file, 'r', encoding='utf-8') as f:
            md3_data = json.load(f)

        print(f"✓ 成功读取文件")
        print(f"产品代码: {md3_data.get('product', {}).get('code', 'N/A')}")

        # 打印可用列名（可选，用于调试）
        # print_available_columns(md3_data)

        # 2. 转换数据
        md31_data = transform_md3_to_md31(md3_data)

        print(f"✓ 转换完成，共 {len(md31_data['standard'])} 条记录")

        # 3. 输出到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(md31_data, f, indent=2, ensure_ascii=False)

        print(f"✓ 已保存到: {output_file}")

        # 4. 显示前3条记录作为预览
        print("\n前3条记录预览：")
        for record in md31_data['standard'][:3]:
            print(f"  年度 {record['policy_year']}: "
                  f"已缴保费={record['premiums_paid']}, "
                  f"保证={record['guaranteed']}, "
                  f"非保证={record['non_guaranteed']}, "
                  f"总计={record['total']}")

        return 0

    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
        return 1
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}")
        return 1
    except KeyError as e:
        print(f"错误: 缺少必需的字段 - {e}")
        print("\n提示: 请检查md3.json的结构是否正确")
        return 1
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
