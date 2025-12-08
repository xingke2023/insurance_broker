# 文档详情页面测试指南

## 问题修复

已修复数据字段映射问题：
- API 返回字段：`policy_year`, `guaranteed_cash_value`, `total`
- 前端显示字段已对齐

## 测试步骤

### 1. 访问文档管理页面
```
http://your-domain/plan-management
```

### 2. 查看可用文档
当前数据库中的文档（user_id=5）：
- ID: 43 - "3岁 女 盛利2 5w年缴4_compressed.pdf"
- ID: 42 - "3岁 女 盛利2 5w年缴4_compressed.pdf"
- ID: 41 - "3岁 女 盛利2 5w年缴4_compressed.pdf"
- ID: 40 - "3岁 女 盛利2 5w年缴4.pdf"
- ID: 39 - "3岁 女 盛利2 5w年缴4.pdf"

### 3. 直接访问详情页
也可以直接通过 URL 访问：
```
http://your-domain/document/43
http://your-domain/document/42
http://your-domain/document/41
http://your-domain/document/40
http://your-domain/document/39
```

### 4. 测试 API（命令行）
```bash
# 测试文档列表
curl -s "http://localhost:8017/api/ocr/documents/?user_id=5" | python3 -m json.tool

# 测试文档详情
curl -s "http://localhost:8017/api/ocr/documents/43/" | python3 -m json.tool
```

## 页面展示内容

### 卡片 1: 基本信息
- 受保人姓名: CUSTOMER_TT
- 年龄: 3岁
- 性别: 女
- 保险公司: AXA安盛
- 产品名称: 盛利Ⅱ储蓄保险 - 至尊
- 保额: ¥250,000
- 年缴保费: ¥50,000
- 缴费年数: 5年
- 保险期限: 138

### 卡片 2: 计划书概要
如果有 `summary` 字段则显示：
- 概述
- 关键点列表
- 重要日期

### 卡片 3: 保单年度储蓄计划
显示年度价值表：
- 保单年度（1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 65岁, 70岁...）
- 保证现金价值
- 总现金价值

### 卡片 4: 计划书内容
显示完整的 OCR 识别文本

## 注意事项

1. **用户登录**: 确保你使用的账户 ID 与文档的 user_id 匹配
2. **数据字段**: API 返回的表格字段为 `policy_year`, `guaranteed_cash_value`, `total`
3. **空值处理**: 如果字段值为 null 或空，会显示 "-"
4. **数字格式化**: 所有数字自动添加千分位分隔符
5. **响应式设计**: 页面在移动端和桌面端都能正常显示

## 已修复的问题

✅ 字段映射错误（之前使用了不存在的字段如 `year`, `age`, `special_bonus` 等）
✅ 表格列已简化为三列：保单年度、保证现金价值、总现金价值
✅ 前端已重新构建

## 下一步优化建议

1. 如果需要显示更多列（如特别红利、终期红利等），需要修改后端 API 返回更多字段
2. 可以添加数据可视化图表（如现金价值曲线图）
3. 可以添加导出功能（导出为 PDF 或 Excel）
4. 可以添加打印样式优化
