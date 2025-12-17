# 📖 页面权限管理系统 - README

## 🎯 功能说明

系统现在支持通过 **Django Admin 管理后台**灵活配置页面访问权限。

### 核心特性
✅ **可视化配置**：无需修改代码，在管理后台点点鼠标即可配置
✅ **灵活的权限规则**：支持用户组、管理员、公开访问等多种模式
✅ **即时生效**：用户重新登录后权限立即生效
✅ **命令行工具**：支持批量操作和自动化管理

---

## 🚀 快速开始（5分钟）

### 1. 访问管理后台
```
URL: http://your-domain:8007/admin/
导航: API → 页面访问权限
```

### 2. 查看已配置的权限
系统已自动配置"计划书分步骤分析"页面：
- 只有 `plan_analyzer` 组的成员可以访问
- 管理员始终可以访问

### 3. 授予用户权限
```bash
# 方法1：命令行（推荐）
python3 manage_user_permissions.py add username

# 方法2：Django Admin
进入 Users → 选择用户 → 添加到 plan_analyzer 组
```

### 4. 用户重新登录
⚠️ 用户必须退出并重新登录，权限才会生效！

---

## 📚 文档导航

### 快速入门
- **`PERMISSION_QUICKSTART.md`** - 5分钟快速上手指南（⭐推荐新手阅读）

### 管理员指南
- **`ADMIN_PAGE_PERMISSIONS_GUIDE.md`** - Django Admin 后台详细使用指南
- **`PAGE_PERMISSIONS_COMPLETE_GUIDE.md`** - 完整功能说明和技术实现

### 命令行工具
- **`PLAN_ANALYZER_PERMISSIONS.md`** - 命令行工具详细说明
- **`manage_user_permissions.py`** - 用户权限管理脚本
- **`init_page_permissions.py`** - 初始化配置脚本

---

## 🛠️ 常用命令

### 用户权限管理
```bash
# 查看所有用户及权限状态
python3 manage_user_permissions.py list-all

# 授予用户权限
python3 manage_user_permissions.py add username

# 撤销用户权限
python3 manage_user_permissions.py remove username

# 查看有权限的用户
python3 manage_user_permissions.py list
```

### Django 管理
```bash
# 访问 Admin 后台
http://your-domain:8007/admin/api/pagepermission/

# 创建超级用户（如果没有）
python3 manage.py createsuperuser

# 初始化页面权限配置
python3 init_page_permissions.py
```

---

## 🎨 使用场景

### 场景1：限制高级功能
```
需求：某个高级功能只对付费会员开放

操作：
1. 创建 premium_users 用户组
2. 在 Admin 配置该页面权限，选择 premium_users 组
3. 将付费会员添加到 premium_users 组
```

### 场景2：内测功能
```
需求：新功能先给内测用户试用

操作：
1. 创建 beta_testers 用户组
2. 配置页面权限，选择 beta_testers 组
3. 将内测用户添加到该组
```

### 场景3：管理员专属
```
需求：系统设置页面只允许管理员访问

操作：
1. 配置页面权限
2. 勾选"需要管理员权限"
3. 保存
```

---

## 📋 权限规则

### 优先级（从高到低）
1. **管理员优先**：`is_staff=True` 的用户始终有所有权限
2. **未启用控制**：权限配置未启用时，所有人可访问
3. **需要管理员**：勾选后只有管理员可访问
4. **用户组检查**：用户在允许的组中可访问
5. **无组限制**：未设置组时，所有登录用户可访问

### 配置示例
```
示例1：特定组访问
允许的用户组: plan_analyzer
需要管理员权限: 否
启用: 是
→ 结果：管理员 + plan_analyzer 组成员可访问

示例2：管理员专属
允许的用户组: （空）
需要管理员权限: 是
启用: 是
→ 结果：只有管理员可访问

示例3：所有人可访问
允许的用户组: （空）
需要管理员权限: 否
启用: 是
→ 结果：所有登录用户可访问
```

---

## 🔐 当前配置状态

### 已创建的用户组
- `plan_analyzer` - 计划书分步骤分析功能访问权限

### 已配置的页面权限
| 页面名称 | 页面代码 | 允许的组 | 状态 |
|---------|---------|---------|-----|
| 计划书分步骤分析 | plan-analyzer-2 | plan_analyzer | ✅ 启用 |

### 已授权的用户
```bash
# 查看当前有权限的用户
python3 manage_user_permissions.py list
```

---

## 🆘 故障排查

### 问题：用户看不到权限变化
✅ 让用户退出并重新登录
✅ 或清除浏览器 localStorage

### 问题：所有人都看不到某个页面
检查：
- 权限配置是否启用？
- 是否勾选了"需要管理员权限"？
- 用户是否在允许的组中？

### 问题：API 返回认证错误
检查：
- JWT Token 是否有效？
- 用户是否已登录？
- Token 是否在请求头中？

---

## 📞 技术支持

### 查看日志
```bash
# Django 日志
tail -f /var/log/supervisor/harry-insurance-django-*.log

# 检查数据库
python3 manage.py shell
>>> from api.models import PagePermission
>>> PagePermission.objects.all()
```

### 重启服务
```bash
# 重启 Django
sudo supervisorctl restart harry-insurance:harry-insurance-django

# 重启前端
cd frontend && npm run build
```

---

## 🎓 学习路径

1. **新手**：先阅读 `PERMISSION_QUICKSTART.md`
2. **管理员**：然后阅读 `ADMIN_PAGE_PERMISSIONS_GUIDE.md`
3. **开发者**：最后阅读 `PAGE_PERMISSIONS_COMPLETE_GUIDE.md`

---

## ✅ 系统状态

### 已完成
- ✅ 数据库模型（PagePermission）
- ✅ Django Admin 管理界面
- ✅ API 端点（/api/auth/page-permissions/）
- ✅ 权限检查逻辑
- ✅ 命令行管理工具
- ✅ 初始化脚本
- ✅ 完整文档

### 可选升级
- 🔄 前端从 API 动态获取权限（目前为硬编码）
- 🔄 添加权限变更通知功能
- 🔄 添加权限审计日志

---

**文档版本**：v1.0
**创建日期**：2025-12-14

如有问题，请查阅相关文档或联系系统管理员。
