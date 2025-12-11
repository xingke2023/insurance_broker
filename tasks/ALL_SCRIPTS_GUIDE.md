# 保险数据提取工具完整指南

## 概述

本项目提供三个独立的数据提取脚本，分别处理不同类型的保险计划数据。

## 三个提取脚本对比

### 1. transform_json.py - 基本计划提取

**用途**：提取基本计划的退保价值数据（无任何附加选项）

**数据来源**：
- Projection 0（policyOptions: []）
- 基本计划，无款项提取，无其他选项

**提取字段**：
- policy_year（保单年度）
- premiums_paid（累计已缴保费）
- guaranteed（保证现金价值）
- non_guaranteed（非保证退保价值）
- total（总退保价值）

**使用方法**：
```bash
python3 transform_json.py md3.json md31.json
python3 transform_json.py md4.json md41.json
```

**输出格式**：
```json
{
  "standard": [
    {
      "policy_year": 80,
      "premiums_paid": 50000,
      "guaranteed": 81211,
      "non_guaranteed": 6741552,
      "total": 6822762
    }
  ]
}
```

**特点**：
- ✓ 最简单的基本计划
- ✓ 无任何提取
- ✓ 适合对比基准

---

### 2. transform_withdrawal.py - 固定提取计划（md4专用）

**用途**：提取带固定款项提取选项的数据

**数据来源**：
- md4.json
- Projection 1（policyOptions: ['Withdrawal']）
- 投资假设：当前假设（无Low/High后缀）

**提取字段**：
- policy_year（保单年度）
- premiums_paid（累计已缴保费）
- withdrawal_amount（该年提取款项）- **固定2,000**
- accumulated_withdrawal（累计提取款项）
- notional_amount（提取后名义金额）
- guaranteed（保证现金价值）
- non_guaranteed（非保证退保价值）
- total_surrender（提取后退保价值）

**使用方法**：
```bash
python3 transform_withdrawal.py md4.json md4_withdrawal.json
```

**输出格式**：
```json
{
  "withdrawal": [
    {
      "policy_year": 80,
      "premiums_paid": 50000,
      "withdrawal_amount": 2000,
      "accumulated_withdrawal": 152000,
      "notional_amount": 18774,
      "guaranteed": 30493,
      "non_guaranteed": 3135922,
      "total_surrender": 3166415
    }
  ]
}
```

**特点**：
- ✓ 每年提取固定金额2,000
- ✓ 从第5年持续到第119年
- ✓ 累计提取230,000
- ✓ 适合稳定现金流需求

**验证数据**（第80年）：
- 名义金额：18,774 ✓
- 退保价值：3,166,415 ✓

---

### 3. transform_md5_withdrawal.py - Realization提取计划（md5专用）

**用途**：提取带Realization选项的浮动提取数据

**数据来源**：
- md5.json
- Projection 3（policyOptions: ['Withdrawal', 'Realization']）
- 投资假设：当前假设（无Low/High后缀）

**提取字段**：
- policy_year（保单年度）
- premiums_paid（累计已缴保费）
- non_guaranteed_withdrawal（该年非保证提取款项）- **金额浮动**
- accumulated_ng_withdrawal（累计非保证提取）
- guaranteed（保证现金价值）
- non_guaranteed_bc（非保证金额B+C）
- total（总额）

**使用方法**：
```bash
python3 transform_md5_withdrawal.py md5.json md5_withdrawal.json
```

**输出格式**：
```json
{
  "withdrawal_realization": [
    {
      "policy_year": 80,
      "premiums_paid": 50000,
      "non_guaranteed_withdrawal": 0,
      "accumulated_ng_withdrawal": 12023,
      "guaranteed": 81211,
      "non_guaranteed_bc": 5556154,
      "total": 5637364
    }
  ]
}
```

**特点**：
- ✓ 提取金额浮动（1,809 - 2,661）
- ✓ 仅从第5年到第9年（5年）
- ✓ 累计提取12,023
- ✓ 第10年开始停止提取
- ✓ 适合长期财富累积

---

## 三种方案第80年对比

### 数据对比表

| 项目 | 基本计划 | md4固定提取 | md5 Realization | 说明 |
|------|---------|------------|----------------|------|
| **累计已缴保费** | 50,000 | 50,000 | 50,000 | 相同 |
| **已提取现金** | 0 | 152,000 | 12,023 | md4提取最多 |
| **保证现金价值** | 81,211 | 30,493 | 81,211 | md5最高 |
| **非保证价值** | 6,741,552 | 3,135,922 | 5,556,154 | 基本计划最高 |
| **退保价值** | 6,822,762 | 3,166,415 | 5,637,364 | 基本计划最高 |
| **总价值** | **6,822,762** | **3,318,415** | **5,649,387** | 已提取+剩余 |

### 总价值排名

1. **基本计划**：6,822,762（无提取）
2. **md5 Realization**：5,649,387（-17.2%）
3. **md4固定提取**：3,318,415（-51.4%）

### 关键结论

- **基本计划**价值最高，但无现金流
- **md5方式**比md4高70.2%，适合长期
- **md4方式**现金流最稳定，适合退休

---

## 使用场景推荐

### 场景1：财富最大化
- **选择**：基本计划
- **脚本**：`transform_json.py`
- **特点**：无提取，价值最大
- **适合**：遗产规划、长期储蓄

### 场景2：早期提取+长期增值
- **选择**：md5 Realization
- **脚本**：`transform_md5_withdrawal.py`
- **特点**：早期提取部分，后期继续增值
- **适合**：平衡现金需求与长期收益

### 场景3：稳定现金流
- **选择**：md4固定提取
- **脚本**：`transform_withdrawal.py`
- **特点**：每年固定提取，现金流稳定
- **适合**：退休收入、年金需求

---

## 快速使用指南

### 提取基本计划数据
```bash
python3 transform_json.py input.json output.json
```

### 提取md4固定提取数据
```bash
python3 transform_withdrawal.py md4.json md4_withdrawal.json
```

### 提取md5 Realization数据
```bash
python3 transform_md5_withdrawal.py md5.json md5_withdrawal.json
```

### 批量处理
```bash
# 提取所有类型的数据
python3 transform_json.py md4.json md4_basic.json
python3 transform_withdrawal.py md4.json md4_withdrawal.json
python3 transform_md5_withdrawal.py md5.json md5_withdrawal.json
```

---

## 字段说明对照表

| 含义 | transform_json.py | transform_withdrawal.py | transform_md5_withdrawal.py |
|------|-------------------|------------------------|----------------------------|
| 保单年度 | policy_year | policy_year | policy_year |
| 累计保费 | premiums_paid | premiums_paid | premiums_paid |
| 该年提取 | - | withdrawal_amount | non_guaranteed_withdrawal |
| 累计提取 | - | accumulated_withdrawal | accumulated_ng_withdrawal |
| 名义金额 | - | notional_amount | - |
| 保证价值 | guaranteed | guaranteed | guaranteed |
| 非保证值 | non_guaranteed | non_guaranteed | non_guaranteed_bc |
| 总价值 | total | total_surrender | total |

---

## 技术规格

### 共同特性
- ✅ Python 3.6+
- ✅ 无需额外依赖
- ✅ 支持命令行参数
- ✅ 完整错误处理
- ✅ 数据验证

### 投资假设
所有脚本都使用**当前假设情景**（无Low/High后缀）：
- ✓ 不是悲观情景（Low）
- ✓ 不是乐观情景（High）
- ✓ 代表中等/标准投资回报

---

## 文件清单

### 程序文件
| 文件 | 大小 | 用途 |
|------|------|------|
| `transform_json.py` | 4.5 KB | 基本计划提取 |
| `transform_withdrawal.py` | 5.1 KB | md4固定提取 |
| `transform_md5_withdrawal.py` | 6.6 KB | md5 Realization提取 |

### 数据文件示例
| 文件 | 大小 | 说明 |
|------|------|------|
| `md31.json` | 18 KB | 基本计划输出（120年） |
| `md4_withdrawal.json` | 31 KB | md4提取输出（120年） |
| `md5_withdrawal.json` | 28 KB | md5提取输出（120年） |

### 文档文件
| 文件 | 说明 |
|------|------|
| `README_TRANSFORM.md` | 基本使用说明 |
| `DATA_SPECIFICATION.md` | 数据规格说明 |
| `WITHDRAWAL_ANALYSIS.md` | md4提取分析 |
| `MD5_ANALYSIS.md` | md5提取分析 |
| `SCENARIO_COMPARISON.md` | 投资假设对比 |
| `VERIFICATION_REPORT.md` | 验证报告 |
| `ALL_SCRIPTS_GUIDE.md` | 本完整指南 |

---

## 常见问题

### Q1: 应该使用哪个脚本？
- 看你的数据来源和需求
- md3/md4的基本数据 → `transform_json.py`
- md4的提取数据 → `transform_withdrawal.py`
- md5的提取数据 → `transform_md5_withdrawal.py`

### Q2: 如何验证数据正确性？
- 检查第80年的关键数值
- 验证总额 = 保证 + 非保证
- 对比原始计划书

### Q3: 三种方案哪个最好？
- 没有"最好"，只有"最适合"
- 追求最大价值 → 基本计划
- 追求平衡 → md5 Realization
- 需要现金流 → md4固定提取

### Q4: 可以同时使用多个脚本吗？
- 可以！对同一个数据文件提取不同类型的数据
- 用于对比分析不同方案

---

**更新日期**：2025-12-09
**版本**：1.0
**状态**：✅ 生产就绪
