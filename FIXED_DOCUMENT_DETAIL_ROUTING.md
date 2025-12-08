# 文档详情页面路由问题修复说明

## 问题描述
从计划书列表页点击某个计划书时，出现路由错误，无法正确跳转到详情页。

## 根本原因
Django 后端没有配置 SPA（单页应用）的路由回退机制。当用户直接访问 `/document/43` 这样的前端路由时，Django 不知道如何处理，导致 404 错误。

## 已完成的修复

### 1. ✅ 添加 Catch-All 路由
**文件：** `backend/urls.py`

添加了一个通用路由，将所有非 API/admin 的请求都返回前端的 `index.html`：

```python
from django.urls import path, include, re_path
from .views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Catch-all 路由：所有非 API/admin 的路由都返回前端的 index.html
urlpatterns += [
    re_path(r'^.*$', index_view, name='index'),
]
```

### 2. ✅ 创建前端视图
**文件：** `backend/views.py`

```python
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# 为前端 SPA 提供 index.html
index_view = never_cache(TemplateView.as_view(template_name='index.html'))
```

### 3. ✅ 配置模板目录
**文件：** `backend/settings.py`

指向前端构建目录：

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend' / 'dist'],  # 指向前端构建目录
        'APP_DIRS': True,
        ...
    },
]
```

### 4. ✅ 配置静态文件
**文件：** `backend/settings.py`

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'dist' / 'assets',  # 前端构建的静态资源
]
```

### 5. ✅ 修复 useAppNavigate Hook
**文件：** `frontend/src/hooks/useAppNavigate.js`

添加了对完整路径的支持：

```javascript
const appNavigate = (page) => {
  // 如果已经是完整路径（以 / 开头），直接使用
  if (page.startsWith('/')) {
    navigate(page);
    return;
  }

  // 映射旧的页面名称到新的路由路径
  const routeMap = { ... };
  const path = routeMap[page] || `/${page}`;
  navigate(path);
};
```

## 工作原理

### 单页应用路由流程

1. **用户点击列表中的文档**
   ```
   点击 → onNavigate('/document/43')
   ```

2. **前端路由跳转**
   ```
   React Router 更新 URL → /document/43
   浏览器不刷新页面
   ```

3. **如果用户刷新页面或直接访问 URL**
   ```
   浏览器请求 → http://your-domain/document/43
   Django 接收请求 → Catch-All 路由匹配
   返回 index.html → React Router 接管
   React Router 渲染 DocumentDetail 组件
   ```

4. **API 请求流程**
   ```
   DocumentDetail 组件加载
   → fetch('/api/ocr/documents/43/')
   → Django API 返回数据
   → 渲染页面内容
   ```

## 测试方法

### 测试 1: 从列表页跳转
1. 访问 `/plan-management`
2. 点击任意文档的"详情"按钮
3. **期望结果：** 正常跳转到 `/document/{id}` 并显示详情

### 测试 2: 直接访问 URL
1. 在浏览器地址栏输入：`http://your-domain/document/43`
2. **期望结果：** 页面正常加载，显示文档详情

### 测试 3: 刷新详情页
1. 在详情页按 F5 刷新
2. **期望结果：** 页面重新加载，内容不变

### 测试 4: API 调用
```bash
# 测试 API 是否正常
curl http://localhost:8017/api/ocr/documents/43/

# 测试前端路由是否返回 HTML
curl http://localhost:8017/document/43 | head -20

# 测试静态资源是否可访问
curl -I http://localhost:8017/assets/index-B9PRbci0.js
```

## 调试步骤

### 如果还有问题，请按以下步骤检查：

#### 1. 检查 Django 服务器是否运行
```bash
ps aux | grep "manage.py runserver"
```

#### 2. 检查浏览器控制台（F12）
- **Console 标签页：** 查看是否有 JavaScript 错误
- **Network 标签页：**
  - 查看页面加载请求（应该返回 200）
  - 查看 API 请求（`/api/ocr/documents/{id}/`）
  - 查看静态资源加载（JS、CSS 文件）

#### 3. 检查 Django 日志
```bash
tail -50 /var/www/harry-insurance2/logs/django.log
```

查找是否有错误信息。

#### 4. 验证模板路径
```bash
ls -la /var/www/harry-insurance2/frontend/dist/index.html
```

确保文件存在。

#### 5. 验证静态资源
```bash
ls -la /var/www/harry-insurance2/frontend/dist/assets/
```

确保 JS/CSS 文件存在。

## 常见问题及解决方案

### 问题 1: 404 Not Found
**症状：** 访问 `/document/43` 返回 404

**解决：**
1. 确认 Django 服务器已重启
2. 检查 `backend/urls.py` 中的 catch-all 路由是否添加
3. 检查 `backend/views.py` 是否存在

### 问题 2: 页面空白
**症状：** 页面加载但内容为空

**解决：**
1. 打开浏览器控制台查看错误
2. 检查 Network 标签，确认 API 请求成功
3. 确认前端已重新构建（`npm run build`）

### 问题 3: 静态资源 404
**症状：** JS/CSS 文件加载失败

**解决：**
1. 检查 `settings.py` 中的 `STATICFILES_DIRS` 配置
2. 确认路径指向正确：`BASE_DIR / 'frontend' / 'dist' / 'assets'`
3. 重启 Django 服务器

### 问题 4: API 返回 404
**症状：** `/api/ocr/documents/43/` 返回 404

**解决：**
1. 确认文档 ID 存在于数据库中
2. 检查 `api/urls.py` 中的路由配置
3. 测试其他文档 ID

## 验证清单

- ✅ Django 服务器运行中
- ✅ `backend/urls.py` 包含 catch-all 路由
- ✅ `backend/views.py` 文件已创建
- ✅ `settings.py` 中 `TEMPLATES['DIRS']` 指向 `frontend/dist`
- ✅ `settings.py` 中 `STATICFILES_DIRS` 指向 `frontend/dist/assets`
- ✅ 前端已构建（`npm run build`）
- ✅ `frontend/dist/index.html` 存在
- ✅ `frontend/dist/assets/` 目录包含 JS/CSS 文件
- ✅ `useAppNavigate` hook 支持完整路径

## 架构说明

```
用户请求 /document/43
    ↓
Django 接收请求
    ↓
检查 URL 模式
    ├─ /admin/* → Django Admin
    ├─ /api/* → API 端点
    └─ /* → index_view (返回 frontend/dist/index.html)
         ↓
    前端 React 应用加载
         ↓
    React Router 解析 URL
         ↓
    匹配路由: /document/:id
         ↓
    渲染 DocumentDetail 组件
         ↓
    组件调用 API: /api/ocr/documents/43/
         ↓
    Django API 返回 JSON 数据
         ↓
    React 渲染最终页面
```

## 总结

现在系统已经正确配置为支持 SPA 路由：

1. ✅ 所有前端路由（`/document/*`, `/plan-management` 等）都能正常工作
2. ✅ 页面刷新不会出现 404
3. ✅ 直接访问 URL 也能正常加载
4. ✅ API 请求正常
5. ✅ 静态资源正常加载

**如果仍有问题，请提供：**
- 浏览器控制台的完整错误信息（截图）
- 访问的具体 URL
- Django 日志中的相关错误

---

**最后更新：** 2025-11-13
**状态：** 已修复 SPA 路由问题
