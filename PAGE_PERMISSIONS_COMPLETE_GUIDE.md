# 🎯 页面权限管理完整指南

## 📖 目录
1. [功能概述](#功能概述)
2. [快速开始](#快速开始)
3. [管理后台使用](#管理后台使用)
4. [技术实现](#技术实现)
5. [测试验证](#测试验证)
6. [常见问题](#常见问题)

---

## 功能概述

### ✨ 核心功能
系统现在支持通过 Django Admin 后台灵活配置页面访问权限，实现：

✅ **可视化管理**：无需修改代码，通过管理后台配置权限
✅ **灵活的权限规则**：支持用户组、管理员、公开访问等多种模式
✅ **即时生效**：配置保存后用户重新登录即可生效
✅ **批量管理**：支持命令行工具批量操作

### 🎭 适用场景
- 限制高级功能只对付费用户开放
- VIP功能只对特定用户组开放
- 内测功能只对测试用户组开放
- 敏感功能只对管理员开放

---

## 快速开始

### 第一步：访问管理后台

```bash
URL: http://your-domain:8007/admin/
路径: API → 页面访问权限
```

### 第二步：查看现有配置

系统已自动配置"计划书分步骤分析"页面：
- **页面代码**：`plan-analyzer-2`
- **允许的组**：`plan_analyzer`
- **状态**：已启用

### 第三步：授予用户访问权限

**方法1：使用命令行工具**（推荐）
```bash
# 授予用户权限
python3 manage_user_permissions.py add username

# 查看已授权用户
python3 manage_user_permissions.py list
```

**方法2：通过管理后台**
1. 进入：Users → 点击用户名
2. 找到 Groups 部分
3. 将 `plan_analyzer` 从左边移到右边
4. 保存

### 第四步：通知用户重新登录

⚠️ **重要**：用户必须退出并重新登录，新权限才会生效！

---

## 管理后台使用

### 📋 查看权限列表

访问：http://your-domain:8007/admin/api/pagepermission/

列表显示内容：
| 字段 | 说明 | 示例 |
|------|------|------|
| 页面名称 | 显示名称 | 计划书分步骤分析 |
| 页面代码 | 唯一标识 | plan-analyzer-2 |
| 访问权限 | 权限规则 | 👥 plan_analyzer / 🔒 仅管理员 / 🌍 所有用户 |
| 启用 | 是否生效 | ✓ / ✗ |
| 排序 | 显示顺序 | 10 |

### ➕ 创建新页面权限

点击**增加页面访问权限**：

```
【页面信息】
页面名称：高级数据分析          # 用户看到的名称
页面代码：advanced-analytics    # 前端路由标识
路由路径：/advanced-analytics   # 完整路由
描述：提供高级数据分析和可视化功能

【显示设置】
图标：ChartBarIcon              # 图标类名
颜色：from-purple-600 to-pink-600  # 渐变色

【权限配置】
允许的用户组：
  ☑️ premium_users              # 高级用户组
  ☑️ analysts                   # 分析师组
需要管理员权限：☐              # 不勾选
启用：☑️                        # 勾选启用

【排序】
排序：20                        # 显示优先级
```

保存后，系统会提示：
```
已创建页面权限：高级数据分析
```

### ✏️ 编辑现有权限

1. 点击列表中的页面名称
2. 修改权限配置
3. 点击保存

系统会提示：
```
权限配置已更新：XXX。用户需要重新登录才能看到变化。
```

### 🗑️ 删除权限配置

1. 勾选要删除的记录
2. 操作下拉框选择：**删除所选的页面访问权限**
3. 确认删除

---

## 技术实现

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│                  前端 Dashboard                  │
│  - 获取用户权限 (API)                            │
│  - 动态显示/隐藏页面卡片                          │
└─────────────────┬───────────────────────────────┘
                  │
                  │ GET /api/auth/page-permissions/
                  │
┌─────────────────▼───────────────────────────────┐
│              后端 Django API                     │
│  - get_page_permissions() 视图                   │
│  - 检查用户权限                                   │
│  - 返回可访问的页面列表                           │
└─────────────────┬───────────────────────────────┘
                  │
                  │ PagePermission.check_user_permission()
                  │
┌─────────────────▼───────────────────────────────┐
│           数据库 (page_permissions)              │
│  - page_name: 页面名称                           │
│  - page_code: 页面代码                           │
│  - allowed_groups: 允许的用户组 (M2M)             │
│  - require_staff: 是否需要管理员                  │
│  - is_active: 是否启用                           │
└─────────────────────────────────────────────────┘
```

### 📦 数据库模型

```python
class PagePermission(models.Model):
    """页面访问权限配置"""
    page_name = models.CharField(max_length=100, unique=True)
    page_code = models.CharField(max_length=50, unique=True)
    route_path = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    allowed_groups = models.ManyToManyField(Group, blank=True)
    require_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=100, blank=True)
    sort_order = models.IntegerField(default=0)

    def check_user_permission(self, user):
        """检查用户是否有权限访问"""
        # 1. 未启用 → 所有人可访问
        # 2. 需要管理员 → 只有管理员可访问
        # 3. 无用户组限制 → 所有登录用户可访问
        # 4. 管理员 → 始终有权限
        # 5. 检查用户组 → 用户在允许的组中可访问
```

### 🔌 API 端点

**获取用户可访问的页面列表**

```http
GET /api/auth/page-permissions/
Authorization: Bearer <JWT_TOKEN>
```

**响应示例**：
```json
{
  "status": "success",
  "data": [
    {
      "page_code": "plan-analyzer-2",
      "page_name": "计划书分步骤分析",
      "route_path": "/plan-analyzer-2",
      "icon": "DocumentTextIcon",
      "color": "from-emerald-600 to-teal-600",
      "description": "使用AI分步骤分析保险计划书...",
      "sort_order": 10
    }
  ]
}
```

### 💻 前端集成

**原有实现**（硬编码）：
```javascript
const canAccessPlanAnalyzer = () => {
  if (!user) return false;
  if (user.is_staff) return true;
  if (user.groups && user.groups.includes('plan_analyzer')) {
    return true;
  }
  return false;
};
```

**未来可升级为**（动态）：
```javascript
const [accessiblePages, setAccessiblePages] = useState([]);

useEffect(() => {
  // 登录后获取可访问的页面列表
  fetch('/api/auth/page-permissions/', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(res => res.json())
  .then(data => setAccessiblePages(data.data));
}, [user]);

// 根据 page_code 动态控制显示
const isPageAccessible = (pageCode) => {
  return accessiblePages.some(page => page.page_code === pageCode);
};
```

---

## 测试验证

### 🧪 测试场景

#### 测试1：管理员访问
```bash
1. 以管理员身份登录
2. 进入 Dashboard
3. 应该能看到所有页面（包括受限页面）
```

#### 测试2：授权用户访问
```bash
1. 创建测试用户：testuser
2. 将用户添加到 plan_analyzer 组：
   python3 manage_user_permissions.py add testuser
3. 以 testuser 身份登录
4. 进入 Dashboard
5. 应该能看到"计划书分步骤分析"页面
```

#### 测试3：未授权用户访问
```bash
1. 以普通用户身份登录（不在任何特殊组）
2. 进入 Dashboard
3. 不应该看到"计划书分步骤分析"页面
```

#### 测试4：权限修改后生效
```bash
1. 用户 A 已登录，能看到某个页面
2. 管理员在后台移除用户 A 的权限
3. 用户 A 退出并重新登录
4. 用户 A 应该看不到该页面了
```

### 📊 验证方法

**方法1：前端验证**
- 登录系统
- 查看 Dashboard 显示的页面卡片
- 有权限：显示卡片
- 无权限：不显示卡片

**方法2：API验证**
```bash
# 获取 access token（登录后从浏览器 localStorage 获取）
TOKEN="your_jwt_token_here"

# 调用 API
curl -X GET http://localhost:8007/api/auth/page-permissions/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**方法3：数据库验证**
```bash
# 查看权限配置
python3 manage.py shell
>>> from api.models import PagePermission
>>> PagePermission.objects.all()

# 查看用户组
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='testuser')
>>> user.groups.all()
```

---

## 常见问题

### ❓ Q1: 为什么修改权限后用户看不到变化？

**A**: 用户的权限信息在登录时缓存，需要重新登录才能刷新。

**解决方法**：
1. 让用户退出并重新登录
2. 或清除浏览器 localStorage
3. 或等待 Token 过期自动刷新

---

### ❓ Q2: 如何临时对所有人开放某个页面？

**A**: 有两种方法：

**方法1：禁用权限控制**
```
编辑页面权限 → 取消勾选"启用" → 保存
```

**方法2：移除用户组限制**
```
编辑页面权限 → 清空"允许的用户组" → 保存
```

---

### ❓ Q3: 如何让某个页面只对管理员开放？

**A**:
```
编辑页面权限 → 勾选"需要管理员权限" → 保存
```

---

### ❓ Q4: 可以同时设置多个用户组吗？

**A**: 可以！用户只要在任何一个允许的组中，就能访问该页面。

示例：
```
允许的用户组: [premium_users, vip_members, analysts]
```
用户在以上任何一个组中都可以访问。

---

### ❓ Q5: 管理员是否受用户组限制？

**A**: 不受限制。管理员（is_staff=True）始终拥有所有页面的访问权限，即使没有在用户组中。

---

### ❓ Q6: 如何批量授予多个用户权限？

**A**: 使用命令行脚本批量操作：

```bash
# 方法1：循环授权
for user in alice bob charlie david; do
    python3 manage_user_permissions.py add $user
done

# 方法2：从文件读取
while read username; do
    python3 manage_user_permissions.py add "$username"
done < users.txt
```

---

### ❓ Q7: 如何查看某个用户有哪些权限？

**A**:
```bash
# 查看用户所属的组
python3 manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> user.groups.all()
<QuerySet [<Group: plan_analyzer>, <Group: premium_users>]>
```

---

### ❓ Q8: 前端如何判断用户是否有权限？

**A**: 前端调用 API 获取可访问的页面列表，根据 `page_code` 判断。

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| `ADMIN_PAGE_PERMISSIONS_GUIDE.md` | Django Admin 详细使用指南 |
| `PLAN_ANALYZER_PERMISSIONS.md` | 命令行工具详细说明 |
| `PERMISSION_QUICKSTART.md` | 5分钟快速入门 |
| `manage_user_permissions.py` | 命令行管理脚本 |
| `init_page_permissions.py` | 初始化配置脚本 |

---

## 🎓 总结

### ✅ 已实现的功能
1. ✅ Django 数据库模型（PagePermission）
2. ✅ Admin 后台管理界面
3. ✅ API 端点（/api/auth/page-permissions/）
4. ✅ 权限检查逻辑（check_user_permission）
5. ✅ 命令行管理工具
6. ✅ 初始化脚本
7. ✅ 完整文档

### 🚀 使用流程
```
1. 在 Admin 后台配置页面权限
   ↓
2. 创建或选择用户组
   ↓
3. 将用户添加到组（命令行或后台）
   ↓
4. 用户重新登录
   ↓
5. 前端根据权限动态显示页面
```

### 💡 最佳实践
1. **最小权限原则**：只授予必要的权限
2. **定期审计**：检查权限配置和用户组成员
3. **分组管理**：创建合理的用户组划分
4. **文档记录**：记录各个用户组的用途
5. **测试验证**：修改权限后及时测试

---

## 🆘 需要帮助？

如有问题，请查看：
1. 本文档的"常见问题"部分
2. Django Admin 后台的帮助文本
3. 相关文档和脚本的注释

或联系系统管理员获取支持。

---

**文档版本**：v1.0
**最后更新**：2025-12-14
