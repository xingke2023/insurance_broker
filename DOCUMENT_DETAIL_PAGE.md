# 文档详情页面说明

## 功能概述

新增了独立的文档详情页面 `/document/:id`，用于展示保险计划书的完整信息。

## 页面结构

页面包含四个独立的卡片区域，每个卡片宽度为 100%：

### 1. 基本信息卡片
展示内容：
- **受保人信息**：姓名、年龄、性别
- **保险产品**：保险公司、产品名称
- **保费信息**：保额、年缴保费、缴费年数、总保费、保险期限

布局：响应式网格布局（3列，移动端自适应）

### 2. 计划书概要卡片
展示内容：
- **概述**：计划书的简要说明
- **关键点**：列表形式展示保险计划的关键要点
- **重要日期**：重要的时间节点信息

注意：只有当文档的 `summary` 字段存在时才显示此卡片

### 3. 保单年度储蓄计划卡片
展示内容：
- 年度价值表格，包含以下列：
  - 保单年度
  - 年龄
  - 保证现金价值
  - 特别红利
  - 终期红利
  - 总现金价值

特性：
- 表格支持横向滚动（移动端友好）
- 数字格式化（千分位分隔）
- 显示记录总数

注意：只有当文档的 `table.years` 数组存在且有数据时才显示此卡片

### 4. 计划书内容卡片
展示内容：
- OCR 识别的完整文本内容
- 使用等宽字体显示
- 最大高度 384px，超出部分可滚动
- 显示字符总数

## 路由配置

```javascript
<Route path="/document/:id" element={<DocumentDetail />} />
```

## API 端点

**GET** `/api/ocr/documents/{id}/`

返回数据结构：
```json
{
  "status": "success",
  "data": {
    "id": 15,
    "file_name": "example.pdf",
    "file_size": 123456,
    "status": "completed",
    "content": "OCR识别的文本内容...",
    "content_length": 12345,

    // 受保人信息
    "insured_name": "张三",
    "insured_age": 35,
    "insured_gender": "男",

    // 保险产品信息
    "insurance_company": "某保险公司",
    "insurance_product": "某保险产品",

    // 保费信息
    "sum_assured": "500000",
    "annual_premium": "10000",
    "payment_years": 20,
    "total_premium": "200000",
    "insurance_period": "终身",

    // 年度价值表
    "table": {
      "years": [
        {
          "year": 1,
          "age": 36,
          "guaranteed_cash_value": 1000,
          "special_bonus": 500,
          "terminal_bonus": 200,
          "total_cash_value": 1700
        }
      ]
    },
    "table_record_count": 100,

    // 计划书概要
    "summary": {
      "summary": "这是一份终身寿险计划...",
      "key_points": ["关键点1", "关键点2"],
      "important_dates": ["2025-01-01: 保单生效"]
    },

    // 其他元数据
    "extracted_data": {},
    "created_at": "2025-01-13T10:00:00Z",
    "updated_at": "2025-01-13T10:30:00Z"
  }
}
```

## 导航

### 从文档管理页面跳转
在文档管理页面 (`/plan-management`) 中，点击任意文档行的"详情"按钮，会自动跳转到该文档的详情页面。

### 返回列表
详情页面顶部有"返回列表"按钮，点击后返回文档管理页面。

## 文件位置

- **组件文件**：`frontend/src/components/DocumentDetail.jsx`
- **路由配置**：`frontend/src/App.jsx`
- **API 视图**：`api/ocr_views.py::get_document_detail` (第 180 行)
- **URL 配置**：`api/urls.py` (第 38 行)

## 样式特点

- 使用 Tailwind CSS 实现响应式布局
- 卡片阴影和边框，视觉清晰
- 灰色背景 (bg-gray-50)，卡片白色 (bg-white)
- 数据为空时显示 "-" 占位符
- 数字自动格式化（千分位分隔符）
- 移动端友好，自适应布局

## 状态显示

文档状态标签：
- **已完成** (completed)：绿色标签
- **处理中** (processing)：蓝色标签
- **其他**：灰色标签

## 开发说明

### 修改样式
所有样式使用 Tailwind CSS 类，可以直接修改 JSX 中的 className。

### 添加新字段
1. 在对应的卡片区域添加新的显示逻辑
2. 确保 API 返回包含该字段
3. 处理字段为空的情况

### 国际化
目前所有文本为中文硬编码，如需多语言支持，建议集成 i18n 库。
