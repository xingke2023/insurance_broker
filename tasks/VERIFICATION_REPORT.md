# 数据验证报告

## ✅ 验证结果：完全通过

### 用户要求
- 提取md4.json中的**款项提取数据**
- 使用**"当前假设情景"**而非"悲观情景"
- 验证数据：第80年款项提取后的名义金额 = **18,774**

### 验证过程

#### 1. 确认投资假设情景

检查md4.json中不同投资假设的列：

| 列名 | 投资假设 | 第80年数值 |
|------|---------|-----------|
| `colAfterWDNotionalAmount` | **当前假设** ✓ | **18,774** |
| `colAfterWDNotionalAmountLow` | 悲观情景 ✗ | 8,258 |

**结论**：程序使用的是`colAfterWDNotionalAmount`（无后缀），即**当前假设情景** ✓

#### 2. 验证所有关键字段

| 字段 | 当前假设列 | 悲观情景列 | 第80年（当前） | 第80年（悲观） |
|------|-----------|-----------|--------------|--------------|
| 该年提取 | colCurrentTotalWithdrawalAmount | colCurrentTotalWithdrawalAmountLow | 2,000 | 2,000 |
| 累计提取 | colAccumulatedTotalWithdrawalAmount | colAccumulatedTotalWithdrawalAmountLow | 152,000 | 152,000 |
| **名义金额** | **colAfterWDNotionalAmount** | colAfterWDNotionalAmountLow | **18,774** ✓ | 8,258 |
| 保证价值 | colGuaranteedCashValue | - | 30,493 | 30,493 |
| 非保证价值 | colNonGuaranteedSurrender | colNonGuaranteedSurrenderLow | 3,135,922 | 503,757 |
| **总退保值** | **colTotalSurrender** | colTotalSurrenderLow | **3,166,415** ✓ | 517,169 |

#### 3. 程序输出验证

运行程序：
```bash
$ python3 transform_withdrawal.py md4.json md4_withdrawal_verified.json
```

输出信息：
```
✓ 成功读取文件
产品代码: PU500
数据类型: 款项提取（Withdrawal）
投资假设: 当前假设情景（非悲观/乐观情景）  ← 明确标注
处理 120 个年度的Withdrawal数据...
✓ 转换完成，共 120 条记录

第80年数据验证：
  该年提取款项总额: 2,000
  款项提取后的名义金额: 18,774  ← 与用户验证数据一致 ✓
  款项提取后的退保价值: 3,166,415
```

## 关键差异对比

### 当前假设 vs 悲观情景（第80年）

| 项目 | 当前假设 | 悲观情景 | 差异 | 比例 |
|------|---------|---------|------|------|
| 名义金额 | 18,774 | 8,258 | **-10,516** | **-56%** |
| 非保证价值 | 3,135,922 | 503,757 | -2,632,165 | -83.9% |
| 总退保价值 | 3,166,415 | 517,169 | -2,649,246 | -83.7% |

**如果使用悲观情景**：
- 名义金额会减少56%（从18,774降至8,258）
- 总退保价值会减少83.7%（从3,166,415降至517,169）

**✅ 确认使用当前假设情景是正确的**

## 程序更新

### 更新内容

1. **程序文档说明**（transform_withdrawal.py）
   ```python
   """
   重要说明：
   - 提取的是"当前假设情景"（Current/Mid Scenario）数据
   - 不是"悲观情景"（Low Scenario）数据
   - 使用无Low/High后缀的列（如colAfterWDNotionalAmount）
   """
   ```

2. **运行时提示**
   ```
   投资假设: 当前假设情景（非悲观/乐观情景）
   ```

3. **新增文档**
   - `SCENARIO_COMPARISON.md` - 三种投资假设情景的详细对比
   - `VERIFICATION_REPORT.md` - 本验证报告

## 字段映射确认

### 使用的列（当前假设情景）

| 输出字段 | 数据来源列 | 投资假设 | ✓ |
|---------|-----------|---------|---|
| policy_year | columnYear | 通用 | ✓ |
| premiums_paid | colAccumulateAnnualizedPremium | 通用 | ✓ |
| withdrawal_amount | colCurrentTotalWithdrawalAmount | 通用 | ✓ |
| accumulated_withdrawal | colAccumulatedTotalWithdrawalAmount | 通用 | ✓ |
| **notional_amount** | **colAfterWDNotionalAmount** | **当前** | ✓ |
| guaranteed | colGuaranteedCashValue | 保证 | ✓ |
| **non_guaranteed** | **colNonGuaranteedSurrender** | **当前** | ✓ |
| **total_surrender** | **colTotalSurrender** | **当前** | ✓ |

### 未使用的列（悲观情景）

| 列名 | 投资假设 | 说明 |
|------|---------|------|
| colAfterWDNotionalAmountLow | 悲观 | 不使用 ✗ |
| colNonGuaranteedSurrenderLow | 悲观 | 不使用 ✗ |
| colTotalSurrenderLow | 悲观 | 不使用 ✗ |

## 最终确认

### ✅ 验证通过的项目

1. ✅ 使用"当前假设情景"（无Low后缀）
2. ✅ 第80年名义金额 = 18,774（与用户数据一致）
3. ✅ 第80年退保价值 = 3,166,415
4. ✅ 程序文档已更新说明
5. ✅ 运行时显示投资假设类型

### 输出文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `transform_withdrawal.py` | 提取程序（已更新） | ✅ |
| `md4_withdrawal.json` | 提取数据（当前假设） | ✅ |
| `SCENARIO_COMPARISON.md` | 情景对比分析 | ✅ |
| `WITHDRAWAL_ANALYSIS.md` | 提取场景分析（已更新） | ✅ |
| `VERIFICATION_REPORT.md` | 本验证报告 | ✅ |

## 使用说明

### 提取当前假设情景数据（✅ 推荐）
```bash
python3 transform_withdrawal.py md4.json output.json
```

输出：
- 名义金额（第80年）：18,774
- 退保价值（第80年）：3,166,415

### 如需提取悲观情景数据（不推荐）
需要修改程序，将所有列名加上"Low"后缀。但**用户不需要悲观情景数据**。

---

**验证人员**：Claude Code  
**验证日期**：2025-12-09  
**验证状态**：✅ **完全通过**  
**数据准确性**：100%匹配用户验证数据
