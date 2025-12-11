# Company Comparison 页面更新说明

## 📝 更新内容

### 1. 数据源变更
**从**: `insurance_companies` 表的 `standard_surrender_policy` 字段
**改为**: `insurance_products` 表的 `surrender_value_table` 字段

### 2. 新增功能：按缴费年限筛选
用户可以选择不同的缴费年限查看对应产品的数据：
- ✅ 1年期
- ✅ 2年期
- ✅ 5年期

## 🔧 技术实现

### 后端修改 (api/insurance_company_views.py)

#### 修改的函数：`get_companies_standard_comparison`

**新增查询参数**:
- `payment_period`: 缴费年限（可选，默认5年）
- 示例：`/api/insurance-companies/standard-comparison/?payment_period=2`

**数据查询逻辑**:
```python
# 查询指定缴费年限的产品
product = InsuranceProduct.objects.filter(
    company=company,
    payment_period=payment_period,
    is_active=True
).first()

# 解析 surrender_value_table（JSON字符串）
surrender_table = json.loads(product.surrender_value_table)

# 转换为兼容格式
standard_data = {
    'standard': surrender_table
}
```

**返回数据格式**:
```json
{
  "status": "success",
  "payment_period": 5,
  "data": [
    {
      "id": 1,
      "code": "aia",
      "name": "友邦",
      "icon": "🏢",
      "flagship_product": "环宇盈活储蓄寿险计划",
      "has_data": true,
      "payment_period": 5,
      "standard_data": {
        "standard": [
          {
            "policy_year": 1,
            "guaranteed": 10,
            "non_guaranteed": 0,
            "total": 10,
            "premiums_paid": 10000
          }
        ]
      }
    }
  ]
}
```

### 前端修改 (frontend/src/components/CompanyComparison.jsx)

#### 1. 修改 `fetchCompanies` 函数
```javascript
const fetchCompanies = async (paymentPeriod = paymentYears) => {
  const response = await axios.get('/api/insurance-companies/standard-comparison/', {
    params: {
      payment_period: paymentPeriod
    }
  });
  // ...
};
```

#### 2. 新增 `handlePaymentYearsChange` 函数
```javascript
const handlePaymentYearsChange = (years) => {
  setPaymentYears(years);
  setSelectedIds([]); // 清空已选择的公司
  fetchCompanies(years); // 重新获取数据
};
```

#### 3. 更新缴费年限选择器 UI
- 添加 1年、2年、5年 三个选项
- 选中状态高亮显示（蓝色背景 + 边框）
- 点击时触发 `handlePaymentYearsChange`

## 📊 数据库表结构

### insurance_products 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigInt | 主键 |
| company_id | BigInt | 外键（insurance_companies） |
| product_name | VARCHAR(200) | 产品名称 |
| payment_period | INT | 缴费年期（1, 2, 5等） |
| annual_premium | DECIMAL(15,2) | 年缴金额 |
| surrender_value_table | LONGTEXT | 退保价值表（JSON字符串） |
| death_benefit_table | LONGTEXT | 身故赔偿表（JSON字符串） |
| is_withdrawal | BOOLEAN | 是否支持提取 |
| is_active | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### surrender_value_table 数据格式
```json
[
  {
    "policy_year": 1,
    "guaranteed": 10,
    "non_guaranteed": 0,
    "total": 10,
    "premiums_paid": 10000
  },
  {
    "policy_year": 2,
    "guaranteed": 10,
    "non_guaranteed": 0,
    "total": 10,
    "premiums_paid": 20000
  }
]
```

## 🎯 当前数据状态

### 已有数据
- ✅ **5年期产品**: 9个保险公司的产品（友邦、保诚、宏利、永明、安盛、中银、国寿、富卫、周大福）

### 待添加数据
- ⚠️ **1年期产品**: 0个（需要在 Admin 中添加）
- ⚠️ **2年期产品**: 0个（需要在 Admin 中添加）

## 📝 如何添加新产品数据

### 方法1：通过 Django Admin
1. 访问 `/admin/api/insuranceproduct/add/`
2. 选择保险公司
3. 填写产品信息：
   - 产品名称
   - 缴费年期（输入 1 或 2）
   - 年缴金额
   - 退保价值表（JSON格式）
4. 保存

### 方法2：通过数据迁移脚本
可以创建脚本批量导入1年期和2年期的产品数据。

## 🔍 测试结果

### API 测试
```bash
# 5年期（有数据）
curl "http://localhost:8007/api/insurance-companies/standard-comparison/?payment_period=5"
# 返回: 10个公司，9个有数据

# 1年期（无数据）
curl "http://localhost:8007/api/insurance-companies/standard-comparison/?payment_period=1"
# 返回: 10个公司，0个有数据

# 2年期（无数据）
curl "http://localhost:8007/api/insurance-companies/standard-comparison/?payment_period=2"
# 返回: 10个公司，0个有数据
```

### 前端测试
1. ✅ 访问 `/company-comparison` 页面
2. ✅ 默认显示5年期产品
3. ✅ 点击"1年"按钮 → 重新加载数据（目前无数据）
4. ✅ 点击"2年"按钮 → 重新加载数据（目前无数据）
5. ✅ 点击"5年"按钮 → 显示5年期产品数据
6. ✅ 已选择的公司会在切换年限时自动清空

## 📈 用户体验
- 选中的缴费年限按钮会高亮显示（蓝色背景 + 边框）
- 切换年限时会清空已选择的公司，避免数据混乱
- 加载数据时显示 loading 状态
- 如果某个年限没有数据，公司卡片会显示为灰色（不可选择）

## 🚀 部署状态
- ✅ 后端代码已部署
- ✅ 前端代码已更新
- ✅ Django 服务已重启
- ✅ API 测试通过

## 📌 注意事项
1. 当前只有5年期的产品数据，需要手动添加1年期和2年期的数据
2. 切换缴费年限时，已选择的公司会被清空
3. 产品名称会显示在对比结果中（而不是 flagship_product）
4. 如果某个公司没有对应年期的产品，该公司的 has_data 会返回 false

## 🎉 完成状态
- ✅ 数据源从 insurance_companies 改为 insurance_products
- ✅ 支持按缴费年限筛选（1年、2年、5年）
- ✅ 前端 UI 更新（添加年限选择器）
- ✅ API 测试通过
- ✅ 代码已部署并重启服务
