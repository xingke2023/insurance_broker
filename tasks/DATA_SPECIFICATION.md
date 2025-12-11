# 数据提取规格说明

## ✓ 确认：提取的数据完全符合要求

### 1. 数据来源：基本计划
```
使用：projections[0]
  - projectionOptions: ['BasePlanWithRiders']
  - policyOptions: [] （空数组 = 基本计划，无附加选项）

不使用其他projections（带Withdrawal/Realization/IPO/Prepayment等附加选项）
```

### 2. 数据类型：退保价值（非身故赔偿）
```
提取的列：
  ✓ colGuaranteedCashValue     - 保证现金价值
  ✓ colNonGuaranteedSurrender  - 非保证退保价值
  ✓ colTotalSurrender          - 总退保价值

不提取的列：
  ✗ colTotalDeathBenefit       - 总身故赔偿
  ✗ colGuaranteedDeathBenefit  - 保证身故赔偿
  ✗ colNonGuaranteedDeathBenefit - 非保证身故赔偿
```

### 3. 投资回报率：基准回报率（非不同回报率场景）
```
提取的列：
  ✓ colTotalSurrender          - 总退保价值（基准）

不提取的列：
  ✗ colTotalSurrenderHigh      - 总退保价值（高回报率）
  ✗ colTotalSurrenderLow       - 总退保价值（低回报率）
  ✗ colNonGuaranteedSurrenderHigh - 非保证退保价值（高）
  ✗ colNonGuaranteedSurrenderLow  - 非保证退保价值（低）
```

## 输出数据结构

### md31.json格式
```json
{
  "standard": [
    {
      "policy_year": 1,        // 保单年度
      "premiums_paid": 10000,  // 累计已缴保费
      "guaranteed": 0,         // 保证现金价值（确定部分）
      "non_guaranteed": 0,     // 非保证退保价值（浮动部分）
      "total": 0               // 总退保价值（guaranteed + non_guaranteed）
    },
    ...
  ]
}
```

### 字段说明

| 字段 | 来源列 | 含义 |
|------|--------|------|
| `policy_year` | `columnYear` | 保单年度（1-120年） |
| `premiums_paid` | `colAccumulateAnnualizedPremium` | 累计已缴保费 |
| `guaranteed` | `colGuaranteedCashValue` | 保证现金价值（保险公司承诺的最低退保价值） |
| `non_guaranteed` | `colNonGuaranteedSurrender` | 非保证退保价值（根据投资表现浮动的部分） |
| `total` | `colTotalSurrender` | 总退保价值（= guaranteed + non_guaranteed） |

## 数据验证

### 前5年数据示例
```
年度 | 已缴保费 | 保证价值 | 非保证价值 | 退保总值
-----|----------|----------|------------|----------
  1  |  10,000  |        0 |          0 |        0
  2  |  20,000  |      500 |      4,000 |    4,500
  3  |  30,000  |    2,500 |      8,368 |   10,868
  4  |  40,000  |    5,000 |     13,137 |   18,137
  5  |  50,000  |   12,500 |     18,094 |   30,594
```

### 数据关系验证
```
✓ total = guaranteed + non_guaranteed（每条记录都验证通过）
✓ premiums_paid 是累计值（逐年递增）
✓ 共120条年度记录（policy_year: 1-120）
```

## 为什么选择这些列？

### 退保价值 vs 身故赔偿
- **退保价值**：投保人主动退保时可获得的金额
- **身故赔偿**：被保人身故时受益人获得的赔偿

**本程序提取的是退保价值**，因为：
1. md31.json中的字段名是 `guaranteed`、`non_guaranteed`、`total`
2. 这些对应md3.json中的 `CashValue`/`Surrender` 列
3. 不是 `DeathBenefit` 列

### 基准回报率 vs 不同回报率场景
- **基准列**（无后缀）：使用标准/预期的投资回报率
- **High列**：假设高投资回报率的场景
- **Low列**：假设低投资回报率的场景

**本程序使用基准列**，因为：
1. md31.json只有一组数据（不是三组High/Mid/Low）
2. 提取的是 `colTotalSurrender`（无后缀）
3. 不是 `colTotalSurrenderHigh` 或 `colTotalSurrenderLow`

### 基本计划 vs 附加选项
md3.json包含16个projections：
- **Projection 0**：基本计划（policyOptions: []）
- **Projection 1-15**：基本计划 + 各种附加选项组合

**本程序使用Projection 0**，因为：
1. policyOptions为空数组，代表纯基本计划
2. 不包含Withdrawal/Realization/IPO/Prepayment等附加功能

## 完整性验证

```bash
$ python3 transform_json.py
✓ 成功读取文件
✓ 产品代码: PU500
✓ 处理 120 个年度的数据
✓ 转换完成，共 120 条记录
✓ 已保存到: md31_generated.json

验证结果：
✓✓✓ 生成数据与原始md31.json完全一致（100%匹配）
```

## 使用场景

此数据适用于：
- ✓ 计算基本计划的退保价值
- ✓ 分析保证与非保证部分的比例
- ✓ 评估不同年度的退保回报率
- ✓ 对比累计保费与退保价值的关系

不适用于：
- ✗ 计算身故赔偿
- ✗ 模拟不同投资回报率场景
- ✗ 分析附加选项的影响
