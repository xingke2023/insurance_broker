# 文档详情页面调试指南

## 问题描述
计划书列表页点击某一个计划，详情页无法显示列（表格列）

## 已完成的修复

### 1. ✅ 修正字段映射
- API 返回字段：`policy_year`, `guaranteed_cash_value`, `total`
- 前端已更新为使用正确的字段名

### 2. ✅ 添加调试日志
在浏览器控制台（F12 -> Console）中可以看到：
- `📡 正在获取文档详情，ID: XX`
- `📦 API返回数据:` - 完整的 API 响应
- `✅ 文档数据加载成功`
- `🔍 渲染行数据:` - 每一行的数据

### 3. ✅ 改进表格样式
- 添加了边框线使列更清晰可见
- 表头使用灰色背景
- 添加 hover 效果
- 使用 `border-collapse` 确保边框正确显示

### 4. ✅ 添加空数据提示
如果没有年度储蓄计划数据，会显示提示信息

## 调试步骤

### 方法 1：通过文档管理页面测试

1. 访问 http://your-domain/plan-management
2. 找到任意文档，点击"详情"按钮
3. 打开浏览器开发者工具（F12）
4. 查看 Console 标签页的输出

### 方法 2：直接访问详情页

访问以下 URL（使用实际存在的文档ID）：
```
http://your-domain/document/43
http://your-domain/document/42
http://your-domain/document/41
```

### 方法 3：使用测试页面

访问测试页面：
```
http://your-domain/test_document_detail.html
```

该页面提供：
- 快速访问链接
- API 测试按钮
- 调试步骤说明

## 检查清单

### ✅ 确认路由配置
```javascript
// App.jsx 中应该有这一行
<Route path="/document/:id" element={<DocumentDetail />} />
```

### ✅ 确认 API 返回正确数据
在浏览器中访问：
```
http://your-domain/api/ocr/documents/43/
```

应该返回：
```json
{
  "status": "success",
  "data": {
    "id": 43,
    "table": {
      "years": [
        {
          "policy_year": "1",
          "guaranteed_cash_value": null,
          "total": null
        },
        {
          "policy_year": "3",
          "guaranteed_cash_value": 2250,
          "total": 15410
        },
        ...
      ]
    },
    ...
  }
}
```

### ✅ 确认前端已重新构建
```bash
cd /var/www/harry-insurance2/frontend
npm run build
```

构建文件应该在 `dist` 目录中，并且 Django 应该配置为服务这些静态文件。

### ✅ 检查浏览器控制台
打开开发者工具（F12），查看：

1. **Console 标签页**
   - 是否有 JavaScript 错误？
   - 是否看到调试日志（📡、📦、✅、🔍）？

2. **Network 标签页**
   - 刷新页面
   - 查找对 `/api/ocr/documents/{id}/` 的请求
   - 检查响应状态码（应该是 200）
   - 查看响应内容是否正确

3. **Elements 标签页**
   - 使用元素选择器（左上角箭头图标）
   - 点击表格区域
   - 检查 HTML 结构是否正确渲染

## 可能的问题及解决方案

### 问题 1: 表格列不可见
**症状：** 表格标题显示了，但看不到列的边界

**原因：** CSS 边框样式未生效

**解决：**
已添加明确的边框样式：
```jsx
<table className="w-full text-sm border-collapse">
  <thead>
    <tr className="bg-gray-50 border-b-2 border-gray-200">
      <th className="... border-r border-gray-200">...</th>
    </tr>
  </thead>
  <tbody className="bg-white">
    <tr className="border-b border-gray-100">
      <td className="... border-r border-gray-100">...</td>
    </tr>
  </tbody>
</table>
```

### 问题 2: 数据未加载
**症状：** 页面显示加载中或错误信息

**检查：**
1. 浏览器控制台是否有错误？
2. Network 标签页中 API 请求是否成功？
3. API 返回的数据结构是否正确？

**解决：**
- 确认文档 ID 存在
- 确认用户有权限访问该文档
- 检查后端日志

### 问题 3: 字段显示为 "-"
**症状：** 表格中所有值都显示为 "-"

**原因：** 字段名不匹配或数据为 null

**检查：**
```javascript
// 在控制台查看行数据
console.log('🔍 渲染行数据:', row);
```

确认数据结构是否为：
```javascript
{
  policy_year: "1",
  guaranteed_cash_value: 2250,
  total: 15410
}
```

### 问题 4: 表格不显示
**症状：** 看不到"保单年度储蓄计划"卡片

**原因：** 条件判断失败

**检查：**
在控制台运行：
```javascript
// 假设 document 是当前文档数据
console.log('table:', document.table);
console.log('years:', document.table?.years);
console.log('length:', document.table?.years?.length);
```

**解决：**
确保 `document.table.years` 数组存在且长度大于 0

## 数据字段对照表

| API 字段 | 前端显示 | 类型 | 示例值 |
|---------|---------|------|--------|
| `policy_year` | 保单年度 | string | "1", "3", "65岁" |
| `guaranteed_cash_value` | 保证现金价值 | number | 2250, 60500 |
| `total` | 总现金价值 | number | 15410, 330170 |

## 成功的表现

当页面正常工作时，你应该看到：

1. ✅ 顶部导航栏：显示文件名和状态
2. ✅ 基本信息卡片：显示受保人、保险产品、保费信息（3列网格）
3. ✅ 计划书概要卡片：如有数据则显示
4. ✅ 保单年度储蓄计划卡片：
   - 标题显示记录数量
   - 表格有清晰的表头（3列）
   - 表格有多行数据
   - 列之间有边框线
   - 数字格式化（千分位）
5. ✅ 计划书内容卡片：显示完整 OCR 文本

## 联系开发者

如果以上步骤都无法解决问题，请提供：

1. 浏览器控制台的完整错误信息（截图）
2. Network 标签页中 API 请求的详细信息
3. 访问的具体 URL
4. 使用的浏览器类型和版本

---

**最后更新：** 2025-01-13
**状态：** 已修复字段映射问题，添加调试日志和改进样式
