# 如何在 Django Admin 中修改"主打寿险产品"

## 访问路径

1. 访问 Django Admin 后台：`http://your-domain:8007/admin/`
2. 登录管理员账号
3. 找到 **保险公司 (Insurance Companies)** 模块
4. 点击进入列表页

## 在列表页查看

在列表页中，您可以看到以下列：
- 公司代码 (code)
- 公司名称 (name)
- 英文名称 (name_en)
- **主打寿险产品 (flagship_product)** ⭐ 新增字段
- 图标 (icon_display)
- 颜色 (color_display)
- 接口数量 (request_count)
- 是否启用 (is_active)
- 排序 (sort_order)

## 编辑字段

### 方法 1：直接点击公司名称编辑

1. 在列表页点击任意保险公司的名称
2. 进入编辑页面
3. 在 **基本信息** 部分找到 **主打寿险产品** 字段
4. 输入产品名称，例如：
   - 保诚：`守护健康危疾加护保2`
   - 宏利：`赤霞珠2`
   - 友邦：`充裕未来3`
   - 安盛：`安进储蓄系列`
5. 点击页面底部的 **保存** 或 **保存并继续编辑** 按钮

### 方法 2：使用搜索功能

1. 在列表页右上角的搜索框中输入公司代码、名称或产品名称
2. 系统会实时过滤显示匹配的保险公司
3. 点击进入编辑页面修改

## 字段说明

- **字段名称**：主打寿险产品 (flagship_product)
- **字段类型**：文本字段 (CharField)
- **最大长度**：200 个字符
- **是否必填**：否（可以留空）
- **用途**：记录该保险公司的主打寿险产品名称，可用于前端展示和对比

## API 返回

修改后，该字段会自动包含在以下 API 接口的返回数据中：

1. `GET /api/insurance-companies/` - 返回所有保险公司列表
2. `GET /api/insurance-companies/standard-comparison/` - 返回对比数据

返回格式示例：
```json
{
  "id": 2,
  "code": "prudential",
  "name": "保诚",
  "name_en": "Prudential",
  "icon": "/prudential.jpg",
  "flagship_product": "守护健康危疾加护保2",
  "has_data": true
}
```

## 测试验证

已测试保诚公司的主打产品字段：
✅ 字段可以正常保存
✅ 字段可以正常读取
✅ API 可以正常返回
✅ 列表页可以正常显示
✅ 搜索功能正常工作

---

**创建时间**: 2025-12-09
**系统版本**: Django 5.2.7
