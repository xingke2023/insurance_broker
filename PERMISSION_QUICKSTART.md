# 快速开始：授予用户"计划书分步骤分析"权限

## 🚀 三步快速授权

### 步骤 1：查看所有用户
```bash
cd /var/www/harry-insurance2
python3 manage_user_permissions.py list-all
```

找到您想授权的用户名。

### 步骤 2：授予权限
```bash
python3 manage_user_permissions.py add <用户名>
```

例如：
```bash
python3 manage_user_permissions.py add kelvinleung
```

### 步骤 3：通知用户重新登录
用户需要退出当前账号，重新登录后权限才会生效。

---

## 📋 常用命令速查

| 操作 | 命令 |
|------|------|
| 查看所有用户 | `python3 manage_user_permissions.py list-all` |
| 授予权限 | `python3 manage_user_permissions.py add <用户名>` |
| 撤销权限 | `python3 manage_user_permissions.py remove <用户名>` |
| 查看有权限的用户 | `python3 manage_user_permissions.py list` |

---

## ✅ 验证权限是否生效

### 前端验证：
1. 让用户登录系统
2. 进入 Dashboard 页面
3. **有权限**：能看到"计划书分步骤分析"卡片（绿色渐变）
4. **无权限**：该卡片不会显示

### 后端验证：
```bash
python3 manage_user_permissions.py list
```
查看该用户是否在列表中。

---

## 🔧 当前系统状态

### ✅ 已完成配置
- ✅ 创建了 `plan_analyzer` 用户组
- ✅ 示例用户 `kelvinleung` 已获得权限
- ✅ 管理员用户 `admin` 默认拥有所有权限

### 📊 权限统计
```bash
# 查看当前有多少用户获得了权限
python3 manage_user_permissions.py list

# 查看系统总用户数
python3 manage_user_permissions.py list-all
```

---

## 💡 权限规则说明

系统有两种方式获得访问权限：

1. **方式一：管理员用户**
   - 所有 `is_staff=True` 的管理员自动拥有权限
   - 无需添加到 `plan_analyzer` 组

2. **方式二：普通用户加入组**
   - 使用 `add` 命令将用户添加到 `plan_analyzer` 组
   - 适合需要访问该功能的普通用户

---

## 🎯 实际操作示例

### 场景1：批量授权多个用户
```bash
# 授权用户 alice
python3 manage_user_permissions.py add alice

# 授权用户 bob
python3 manage_user_permissions.py add bob

# 授权用户 charlie
python3 manage_user_permissions.py add charlie

# 查看所有授权用户
python3 manage_user_permissions.py list
```

### 场景2：临时授权后撤销
```bash
# 临时授权
python3 manage_user_permissions.py add testuser

# 验证权限
python3 manage_user_permissions.py list

# 测试完成后撤销
python3 manage_user_permissions.py remove testuser
```

### 场景3：查看某个用户的权限状态
```bash
# 查看所有用户，筛选特定用户
python3 manage_user_permissions.py list-all | grep username
```

---

## ❓ 常见问题

### Q1: 授权后用户仍然看不到功能？
**A:** 用户需要退出并重新登录。或者清除浏览器的 localStorage。

### Q2: 如何批量授权所有用户？
**A:** 目前需要逐个授权。如需批量授权，可以使用循环：
```bash
# 假设用户名列表在 users.txt 中，每行一个用户名
while read username; do
    python3 manage_user_permissions.py add "$username"
done < users.txt
```

### Q3: 管理员和普通用户有什么区别？
**A:**
- 管理员（is_staff=True）：自动拥有所有功能权限
- 普通用户：需要明确添加到对应的用户组才有权限

### Q4: 删除用户组会怎样？
**A:** 不要删除 `plan_analyzer` 组！删除后所有非管理员用户都会失去访问权限。

---

## 📞 需要帮助？

详细文档请查看：`PLAN_ANALYZER_PERMISSIONS.md`
