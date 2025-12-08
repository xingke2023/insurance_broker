# Admin后台快速开始

## 🎯 访问地址

```
http://your-domain:8007/admin/
```

用管理员账号登录后，在左侧菜单找到 **"API"** 分组下的：
- **保险公司 (Insurance Companies)**
- **保险公司请求配置 (Insurance Company Requests)**

---

## 📋 添加新接口配置的5个步骤

### 1️⃣ 确保保险公司存在
先到"保险公司"页面检查，如果没有则添加。

### 2️⃣ 点击"添加保险公司请求配置"

### 3️⃣ 填写POST URL
```
https://api.example.com/endpoint
```

### 4️⃣ 填写POST Request模板
```json
{
  "premium": "{{premium}}",
  "amount": "{{withdrawal_amount}}"
}
```
**注意：** 使用 `{{变量名}}` 作为占位符

### 5️⃣ 配置字段
**可配置字段列表：**
```json
["premium", "withdrawal_amount", "bearer_token"]
```

**字段描述：**
```json
{
  "premium": {
    "label": "每期保费",
    "type": "number",
    "required": true,
    "default": 10000
  }
}
```

点击"保存"即可！

---

## 🔑 核心概念

| 项目 | 说明 | 示例 |
|------|------|------|
| POST URL | API端点地址 | `https://api.axa.com/calculate` |
| POST Request | 请求体JSON模板 | `{"premium": "{{premium}}"}` |
| 占位符 | 用`{{变量名}}`表示可配置字段 | `{{premium}}`, `{{bearer_token}}` |
| 可配置字段 | 占位符列表 | `["premium", "bearer_token"]` |
| 字段描述 | 每个字段的详细信息 | 标签、类型、是否必填、默认值 |

---

## 📊 当前数据

```
🏢 安盛 (axa)
  ├─ 利益表计算
  └─ 提取金额计算

总计: 1 个保险公司, 2 个API配置
```

---

## 🔍 查看现有配置示例

进入"保险公司请求配置"列表，点击"利益表计算"可以看到完整的配置示例。

---

## 📚 详细文档

查看 `ADMIN_GUIDE.md` 获取完整的使用指南和示例。
