# Admin管理页面使用指南

## 访问Admin后台

访问地址：`http://your-domain:8007/admin/`

登录后即可看到"保险公司接口配置管理"模块。

---

## 模块说明

### 1. 保险公司 (Insurance Companies)

管理所有保险公司的基本信息。

**主要字段：**
- **代码 (code)**: 保险公司的唯一标识，例如 `axa`, `prudential`
- **名称 (name)**: 中文名称，例如"安盛"
- **英文名称 (name_en)**: 英文名称，例如"AXA"
- **图标 (icon)**: emoji图标，例如 🏢
- **颜色渐变 (color_gradient)**: 用于前端显示，例如 `from-blue-600 to-blue-700`
- **背景颜色 (bg_color)**: 例如 `bg-blue-50`
- **描述 (description)**: 简短描述
- **排序 (sort_order)**: 数字越小越靠前

**特性：**
- 在保险公司详情页可以看到该公司的所有API请求配置
- 支持内联快速查看和编辑请求配置

---

### 2. 保险公司请求配置 (Insurance Company Requests)

管理每个保险公司的API接口调用配置。

#### 基本信息

- **保险公司**: 选择所属的保险公司
- **请求名称**: 例如"利益表计算"、"提取金额计算"
- **保险产品**: 例如"盛利 II 儲蓄保險 – 至尊"

#### API配置

- **请求URL**: 完整的API端点地址
  ```
  https://az-api.axa.com.hk/api/iprotoolkit/b2c/pos/v1/ext/proposals/illustrate
  ```

- **请求方法**: GET/POST/PUT/DELETE（通常是POST）

- **需要Bearer Token**: 是否需要认证token

#### POST Request 模板

这是最核心的配置项。在大文本框中输入完整的POST请求体JSON。

**变量占位符语法：**
使用 `{{变量名}}` 表示可配置的字段。

**示例：**
```json
{
  "prodCode": "HK_WEB",
  "plans": [{
    "premium": "{{premium}}",
    "yearPrem": "{{premium}}",
    "sumInsured": "{{sum_insured}}"
  }],
  "policyOptions": {
    "wdPayee1PwAmount": ["{{withdrawal_amount}}"]
  }
}
```

**占位符说明：**
- `{{premium}}` - 会被实际的保费数值替换
- `{{withdrawal_amount}}` - 会被实际的提取金额替换
- `{{bearer_token}}` - 会被用户输入的token替换

#### 可配置字段列表

JSON数组格式，列出所有可以由用户配置的字段名。

**格式：**
```json
[
  "premium",
  "withdrawal_amount",
  "bearer_token"
]
```

**注意：**
- 这些字段名必须与POST Request模板中的 `{{变量名}}` 一一对应
- 字段名区分大小写

#### 字段描述配置

JSON对象格式，描述每个可配置字段的属性。

**格式：**
```json
{
  "premium": {
    "label": "每期保费",
    "type": "number",
    "required": true,
    "default": 10000
  },
  "withdrawal_amount": {
    "label": "提取金额",
    "type": "number",
    "required": false,
    "default": 10000
  },
  "bearer_token": {
    "label": "安盛API Token",
    "type": "string",
    "required": true,
    "sensitive": true
  }
}
```

**字段属性说明：**
- `label`: 字段的中文标签，用于前端显示
- `type`: 字段类型（`number`/`string`/`boolean`等）
- `required`: 是否必填（`true`/`false`）
- `default`: 默认值
- `sensitive`: 是否敏感字段（如token），会特殊显示

#### Response 模板（可选）

预期的响应格式示例，用于文档说明和前端参考。

**示例：**
```json
{
  "status": "success",
  "data": {
    "policyYear": 1,
    "cashValue": 50000,
    "surrenderValue": 45000
  }
}
```

---

## 完整示例：添加新的接口配置

### 场景：为"宏利保险"添加"保单查询"接口

#### 步骤1：添加保险公司（如果还没有）

1. 进入 **保险公司** 管理页
2. 点击"添加保险公司"
3. 填写：
   - 代码: `manulife`
   - 名称: 宏利
   - 英文名称: Manulife
   - 图标: 🏛️
   - 颜色渐变: `from-red-600 to-red-700`
   - 背景颜色: `bg-red-50`
   - 排序: 2
4. 保存

#### 步骤2：添加接口配置

1. 进入 **保险公司请求配置** 管理页
2. 点击"添加保险公司请求配置"
3. 填写基本信息：
   - 保险公司: 选择"宏利"
   - 请求名称: 保单查询
   - 保险产品: 宏利储蓄计划

4. 填写API配置：
   - 请求URL: `https://api.manulife.com/policy/query`
   - 请求方法: POST
   - 需要Bearer Token: 是

5. 填写POST Request模板：
```json
{
  "policyNumber": "{{policy_number}}",
  "holderName": "{{holder_name}}",
  "queryType": "detail"
}
```

6. 填写可配置字段列表：
```json
[
  "policy_number",
  "holder_name",
  "bearer_token"
]
```

7. 填写字段描述配置：
```json
{
  "policy_number": {
    "label": "保单号码",
    "type": "string",
    "required": true,
    "default": ""
  },
  "holder_name": {
    "label": "持有人姓名",
    "type": "string",
    "required": true,
    "default": ""
  },
  "bearer_token": {
    "label": "API Token",
    "type": "string",
    "required": true,
    "sensitive": true
  }
}
```

8. 点击"保存"

---

## 列表页功能

### 保险公司列表
- 显示所有保险公司
- 可以看到每个公司有多少个API配置
- 可以按公司代码、名称搜索
- 可以按启用状态筛选

### 请求配置列表
- 显示所有API配置
- 可以看到所属公司、请求方法、URL、是否需要token
- 可以按公司、请求方法、token要求筛选
- 可以搜索请求名称、URL、产品名称

---

## API调用流程

前端通过以下步骤使用这些配置：

1. **获取保险公司列表**
   ```
   GET /api/insurance-companies/
   ```

2. **获取某个公司的所有请求配置**
   ```
   GET /api/insurance-companies/axa/requests/
   ```

3. **获取特定请求的详细配置**
   ```
   GET /api/insurance-companies/axa/requests/利益表计算/
   ```

4. **前端使用配置生成实际请求**
   - 读取 `request_template`
   - 替换所有 `{{变量名}}` 为用户输入的实际值
   - 发送到配置的 `request_url`

---

## 注意事项

### JSON格式验证
- 所有JSON字段都会在保存时进行格式验证
- 如果格式错误，会提示具体的错误位置
- 建议使用JSON格式化工具检查格式

### 占位符命名规范
- 使用小写字母和下划线
- 避免使用特殊字符
- 保持简洁明了
- 例如：`premium`, `withdrawal_amount`, `bearer_token`

### 安全性
- Bearer Token等敏感信息应标记为 `sensitive: true`
- 不要在响应模板中包含真实的敏感数据
- 定期审查和更新API配置

### 测试建议
- 添加新配置后，先在Postman等工具中测试
- 确认请求格式正确、占位符替换成功
- 验证响应格式符合预期

---

## 常见问题

### Q: 如何修改现有配置？
A: 在列表页点击请求名称，进入编辑页面修改即可。

### Q: 可以批量导入配置吗？
A: 目前需要手动添加，或使用Django shell脚本批量导入。

### Q: 如何禁用某个接口？
A: 将"是否启用"字段设置为False即可，不会删除数据。

### Q: POST Request太长怎么办？
A: 文本框支持滚动，可以输入任意长度的JSON。建议使用格式化工具压缩JSON。

### Q: 如何知道前端是否正确使用了配置？
A: 可以查看Django日志和前端network请求，确认占位符被正确替换。

---

## 相关文件

- **模型定义**: `/var/www/harry-insurance2/api/models.py`
- **Admin配置**: `/var/www/harry-insurance2/api/admin.py`
- **API视图**: `/var/www/harry-insurance2/api/insurance_company_views.py`
- **URL路由**: `/var/www/harry-insurance2/api/urls.py`

---

## 技术支持

如有问题，请联系开发团队或查看项目文档。
