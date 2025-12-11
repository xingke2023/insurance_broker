# JSON数据转换工具

## 功能说明

将保险计划书的列式存储格式（md3.json）转换为简化的行式存储格式（md31.json）。

## 数据结构对比

### 输入格式（md3.json）
```json
{
  "product": {"code": "PU500"},
  "projections": [{
    "columns": [
      {
        "Name": "columnYear",
        "Values": [
          {"year": 1, "age": 1, "value": 1},
          {"year": 2, "age": 2, "value": 2}
        ]
      },
      {
        "Name": "colGuaranteedCashValue",
        "Values": [...]
      }
    ]
  }]
}
```

### 输出格式（md31.json）
```json
{
  "standard": [
    {
      "policy_year": 1,
      "premiums_paid": 10000,
      "guaranteed": 0,
      "non_guaranteed": 0,
      "total": 0
    },
    {
      "policy_year": 2,
      "premiums_paid": 20000,
      "guaranteed": 500,
      "non_guaranteed": 4000,
      "total": 4500
    }
  ]
}
```

## 字段映射关系

| 输出字段 | 输入列名 | 说明 |
|---------|---------|------|
| `policy_year` | `columnYear` | 保单年度 |
| `premiums_paid` | `colAccumulateAnnualizedPremium` | 累计已缴保费 |
| `guaranteed` | `colGuaranteedCashValue` | 保证现金价值 |
| `non_guaranteed` | `colNonGuaranteedSurrender` | 非保证退保价值 |
| `total` | `colTotalSurrender` | 总退保价值 |

## 使用方法

### 基本用法
```bash
python3 transform_json.py
```
- 默认读取：`md3.json`
- 默认输出：`md31_generated.json`

### 指定文件
```bash
python3 transform_json.py input.json output.json
```

### 命令行参数
```bash
# 只指定输入文件（输出默认为 md31_generated.json）
python3 transform_json.py my_input.json

# 同时指定输入和输出文件
python3 transform_json.py my_input.json my_output.json
```

## 运行示例

```bash
$ python3 transform_json.py
读取输入文件: md3.json
✓ 成功读取文件
产品代码: PU500
处理 120 个年度的数据...
✓ 转换完成，共 120 条记录
✓ 已保存到: md31_generated.json

前3条记录预览：
  年度 1: 已缴保费=10000, 保证=0, 非保证=0, 总计=0
  年度 2: 已缴保费=20000, 保证=500, 非保证=4000, 总计=4500
  年度 3: 已缴保费=30000, 保证=2500, 非保证=8368, 总计=10868
```

## 核心逻辑

转换过程分为4步：

1. **提取列数组**：从 `projections[0].columns` 获取所有列
2. **建立映射**：创建列名 → Values数组的字典
3. **按年度遍历**：从索引0到119（120年）
4. **提取值**：从 `Values[i]['value']` 获取实际数值

## 文件说明

- `transform_json.py` - 主程序
- `md3.json` - 输入文件（列式存储）
- `md31.json` - 参考输出（行式存储）
- `md31_generated.json` - 程序生成的输出

## 验证结果

✓ 生成的数据与原始 `md31.json` 完全一致（120条记录）

## 依赖

- Python 3.6+
- 标准库：`json`, `sys`（无需额外安装）

## 错误处理

程序会处理以下错误：
- 文件不存在
- JSON格式错误
- 缺少必需字段
- 列名不匹配

## 扩展使用

如果需要提取其他列，可以修改 `column_mappings` 字典：

```python
column_mappings = {
    'policy_year': 'columnYear',
    'premiums_paid': 'colAccumulateAnnualizedPremium',
    'guaranteed': 'colGuaranteedCashValue',
    'non_guaranteed': 'colNonGuaranteedSurrender',
    'total': 'colTotalSurrender',
    # 添加新字段
    'death_benefit': 'colTotalDeathBenefit',
}
```

可用的列名（部分）：
- `colGuaranteedCashValue` - 保证现金价值
- `colNonGuaranteedSurrender` - 非保证退保价值
- `colTotalSurrender` - 总退保价值
- `colTotalDeathBenefit` - 总身故赔偿
- `colAccumulateDividendAndInterest` - 累计红利和利息
- 更多列名可通过取消注释 `print_available_columns(md3_data)` 查看
