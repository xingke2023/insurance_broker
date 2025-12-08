# 保险公司API调用系统使用指南

## 🎯 系统概述

这是一个动态的保险公司API调用系统，通过数据库配置驱动前端界面，无需修改代码即可添加新的保险公司和API接口。

## 📋 系统架构

```
用户访问 Dashboard
    ↓
点击"计划书制作"
    ↓
选择保险公司
    ↓
查看该公司的所有API接口按钮
    ↓
点击接口按钮
    ↓
填写参数、执行POST调用、查看响应
```

## 🔧 核心组件

### 1. PlanBuilder（保险公司列表页）
- **路由**: `/plan-builder`
- **功能**: 从数据库动态加载所有保险公司
- **API**: `GET /api/insurance-companies/`
- **显示**: 11家保险公司的卡片网格

### 2. InsuranceCompanyPage（公司API列表页）
- **路由**: `/insurance-company/:companyCode`
- **功能**: 显示指定公司的所有API接口
- **API**: `GET /api/insurance-companies/{companyCode}/requests/`
- **显示**: 该公司所有POST调用的按钮卡片

### 3. ApiCallPage（API调用执行页）
- **路由**: `/api-call/:companyCode/:requestName`
- **功能**: 动态生成表单、执行API调用、显示结果
- **API**: `GET /api/insurance-companies/{companyCode}/requests/{requestName}/`
- **布局**: 左右分栏
  - 左侧：参数输入表单、POST URL、POST Request
  - 右侧：Response响应结果

## 📊 数据流程

### 步骤1：加载保险公司列表
```javascript
GET /api/insurance-companies/
→ 返回11家保险公司的基本信息
→ 前端显示公司卡片
```

### 步骤2：加载公司的API配置
```javascript
GET /api/insurance-companies/axa/requests/
→ 返回安盛的所有API配置（利益表计算、提取金额计算）
→ 前端显示API按钮
```

### 步骤3：获取API详细配置
```javascript
GET /api/insurance-companies/axa/requests/利益表计算/
→ 返回完整配置：
  - request_url: POST URL
  - request_template: 请求体JSON模板
  - configurable_fields: 可配置字段列表
  - field_descriptions: 字段元数据（标签、类型、默认值）
```

### 步骤4：动态生成表单并执行
```javascript
1. 根据 configurable_fields 生成表单字段
2. 根据 field_descriptions 设置字段属性
3. 用户填写表单
4. 替换 request_template 中的 {{占位符}}
5. 发送POST请求到 request_url
6. 显示响应结果
```

## 🎨 前端特性

### 动态表单生成
根据数据库配置自动生成表单：
- **number** 类型 → 数字输入框
- **string** 类型 → 文本输入框
- **sensitive** 字段 → 密码输入框（橙色高亮）
- **required** 字段 → 显示红色星号

### 实时占位符替换
```javascript
// 数据库模板
{
  "premium": "{{premium}}",
  "amount": "{{withdrawal_amount}}"
}

// 用户输入
premium: 10000
withdrawal_amount: 5000

// 最终请求
{
  "premium": "10000",
  "amount": "5000"
}
```

### 三个显示区域
1. **POST URL**: 显示API端点，可复制
2. **POST Request**: 实时显示替换后的完整请求体，可复制
3. **Response**: 显示API返回的响应结果，可复制

## 🔑 关键配置

### 数据库模型

**InsuranceCompany（保险公司）**
```python
- code: 唯一标识（如 'axa'）
- name: 中文名称
- name_en: 英文名称
- icon: Emoji图标
- color_gradient: 颜色渐变
```

**InsuranceCompanyRequest（API配置）**
```python
- request_name: 请求名称
- request_url: API端点
- request_template: JSON模板（含占位符）
- configurable_fields: ["premium", "bearer_token"]
- field_descriptions: 字段元数据
- requires_bearer_token: 是否需要Token
```

### 占位符语法
在 `request_template` 中使用 `{{变量名}}` 表示可配置字段：
```json
{
  "plans": [{
    "premium": "{{premium}}",
    "yearPrem": "{{premium}}"
  }],
  "policyOptions": {
    "wdPayee1PwAmount": ["{{withdrawal_amount}}"]
  }
}
```

## 📱 用户使用流程

### 1. 访问计划书制作
从Dashboard点击"计划书制作"进入保险公司列表页

### 2. 选择保险公司
看到11家保险公司的卡片，选择需要的公司（如安盛）

### 3. 查看可用API
进入后显示该公司的所有API接口按钮
- 利益表计算 🔐 需要Token
- 提取金额计算 🔐 需要Token

### 4. 执行API调用
点击按钮进入调用页面：
- 左侧输入参数（每期保费、提取金额、Bearer Token）
- 点击"开始执行"
- 右侧显示响应结果

### 5. 复制结果
每个区域都有"复制"按钮，可以快速复制：
- POST URL
- POST Request
- Response

## 🔧 管理员操作

### 添加新保险公司
1. 登录 Admin后台：`http://localhost:8017/admin/`
2. 进入"保险公司"页面
3. 点击"添加保险公司"
4. 填写：代码、名称、图标、颜色等
5. 保存

### 添加新API配置
1. 进入"保险公司请求配置"页面
2. 点击"添加保险公司请求配置"
3. 选择保险公司
4. 填写：
   - 请求名称（如"保单查询"）
   - POST URL
   - POST Request模板（JSON格式，使用 `{{占位符}}`）
   - 可配置字段列表
   - 字段描述配置
5. 保存

### 无需重启
所有配置保存后立即生效，前端会自动加载新配置！

## 🎯 当前状态

### 已添加的保险公司（11家）
1. 🏛️ 保诚 (Prudential) - 0个API
2. 🌲 宏利 (Manulife) - 0个API
3. ☀️ 永明 (Sun Life) - 0个API
4. 🏢 安盛 (AXA) - **2个API** ✅
   - 利益表计算
   - 提取金额计算
5. 🏦 中银 (BOC) - 0个API
6. 🐉 国寿 (China Life) - 0个API
7. 💎 周大福 (Chow Tai Fook) - 0个API
8. 🔷 富通 (FTLife) - 0个API
9. 🛡️ 富卫 (FWD) - 0个API
10. 🌉 立桥 (Transamerica) - 0个API
11. 🤝 友邦 (AIA) - 0个API

### 下一步
为其他10家保险公司添加API配置！

## 📄 相关文档

- **Admin使用指南**: `ADMIN_GUIDE.md`
- **快速开始**: `ADMIN_QUICK_START.md`

## 🚀 技术栈

- **后端**: Django + DRF
- **前端**: React + React Router + Axios
- **数据库**: MySQL
- **样式**: Tailwind CSS
- **图标**: Heroicons

## 💡 优势

✅ **配置驱动**: 数据库配置，无需改代码
✅ **动态生成**: 前端根据配置自动生成界面
✅ **灵活扩展**: 随时添加新公司和新接口
✅ **统一界面**: 所有API调用使用相同的交互模式
✅ **实时预览**: 输入参数实时生成请求体
✅ **易于维护**: 集中管理所有API配置

---

**系统已上线并运行！** 🎉
