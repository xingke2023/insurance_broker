# 前端使用统计显示 - 测试文档

## 功能概述

前端页面现已集成 Gemini API 调用次数的实时显示功能，用户可以在以下两个页面中查看自己的使用情况：

1. **IP形象生成器页面** (`/ip-image-generator`)
2. **文案配图生成器页面** (`/content-image-generator`)

## 功能特性

### 1. 实时统计显示

- ✅ 显示该功能的总调用次数
- ✅ 显示成功和失败次数
- ✅ 自动刷新（生成成功后立即更新）
- ✅ 响应式设计（桌面端和移动端不同样式）

### 2. 统计卡片位置

**桌面端（≥768px）**:
- 显示在页面右上角，与标题同一行
- 使用渐变背景卡片，醒目但不突兀

**移动端（<768px）**:
- 显示在标题下方
- 横向布局，节省空间

### 3. 显示内容

#### IP形象生成器
```
┌─────────────────────────┐
│  IP形象生成次数         │
│        15               │  ← 大号数字显示
│  成功 14 / 失败 1      │  ← 小字显示详情
└─────────────────────────┘
```

#### 文案配图生成器
```
┌─────────────────────────┐
│  文案配图生成次数       │
│        32               │  ← 大号数字显示
│  成功 30 / 失败 2      │  ← 小字显示详情
└─────────────────────────┘
```

## 实现细节

### 组件文件

1. **IPImageGenerator.jsx** (frontend/src/components/IPImageGenerator.jsx)
   - 第 26-27 行: 添加状态管理
   - 第 61-80 行: 获取统计数据函数
   - 第 149 行: 生成成功后刷新统计
   - 第 243-265 行: 统计卡片 UI

2. **ContentImageGenerator.jsx** (frontend/src/components/ContentImageGenerator.jsx)
   - 第 34-35 行: 添加状态管理
   - 第 93-116 行: 获取统计数据函数
   - 第 172-183 行: 生成成功后刷新统计
   - 第 240-262 行: 统计卡片 UI

### API 调用

两个页面都会调用统计 API：

```javascript
// IP形象生成器
GET /api/gemini/usage-stats?type=ip_image

// 文案配图生成器
GET /api/gemini/usage-stats?type=content_image
```

## 测试步骤

### 测试前准备

1. **确保服务运行**:
   ```bash
   # 检查 Django 服务
   sudo systemctl status gunicorn

   # 如果需要重启
   sudo systemctl restart gunicorn
   ```

2. **确认前端已构建**:
   ```bash
   ls -la /var/www/harry-insurance2/static/assets/
   # 应该看到最新的 index-*.js 和 index-*.css 文件
   ```

### 测试场景 1: IP形象生成器

1. **访问页面**:
   ```
   https://yourdomain.com/ip-image-generator
   ```

2. **检查统计显示**:
   - ✅ 页面加载后，右上角（桌面）或标题下方（移动）应显示统计卡片
   - ✅ 显示 "IP形象生成次数"
   - ✅ 显示数字（如果是新用户，显示 0）
   - ✅ 显示成功/失败次数

3. **生成IP形象**:
   - 上传照片
   - 输入提示语（如："专业的商务风格"）
   - 点击"生成IP形象"
   - 等待生成完成

4. **验证统计更新**:
   - ✅ 生成成功后，统计数字应自动 +1
   - ✅ 成功次数应增加
   - ✅ 总次数应更新

### 测试场景 2: 文案配图生成器

1. **访问页面**:
   ```
   https://yourdomain.com/content-image-generator
   ```

2. **检查统计显示**:
   - ✅ 页面加载后，右上角（桌面）或标题下方（移动）应显示统计卡片
   - ✅ 显示 "文案配图生成次数"
   - ✅ 使用绿色主题（与IP形象的蓝色区分）
   - ✅ 显示数字和成功/失败次数

3. **生成文案配图**:
   - 输入文案内容（如："春天的花园，阳光明媚"）
   - 点击"生成配图"
   - 等待生成完成

4. **验证统计更新**:
   - ✅ 生成成功后，统计数字应自动增加
   - ✅ 如果生成多张图片，每张都会计数
   - ✅ 成功次数应准确反映

### 测试场景 3: 响应式设计

1. **桌面浏览器**（宽度 ≥ 768px）:
   - ✅ 统计卡片显示在页面右上角
   - ✅ 与标题同一水平线
   - ✅ 完整显示所有信息

2. **移动设备/窄屏**（宽度 < 768px）:
   - ✅ 统计卡片显示在标题下方
   - ✅ 横向布局，左边文字右边数字
   - ✅ 隐藏详细的成功/失败次数（节省空间）

3. **测试方法**:
   - 使用浏览器开发者工具
   - 切换设备模拟
   - 调整窗口宽度

### 测试场景 4: 错误处理

1. **API 失败情况**:
   - 如果统计 API 失败，页面应该：
     - ✅ 不显示统计卡片（优雅降级）
     - ✅ 不影响其他功能
     - ✅ 在控制台记录错误（可以在浏览器 Console 查看）

2. **首次使用用户**:
   - ✅ 显示 "0" 次
   - ✅ 成功 0 / 失败 0

### 测试场景 5: 数据准确性

1. **IP形象生成 3 次**:
   ```bash
   # 使用 Python 脚本验证数据
   python manage.py shell -c "
   from api.models import GeminiUsage
   from django.contrib.auth.models import User

   user = User.objects.get(username='your_username')
   count = GeminiUsage.objects.filter(user=user, generation_type='ip_image').count()
   print(f'数据库中的IP形象生成次数: {count}')
   "
   ```

2. **对比前端显示**:
   - ✅ 前端显示的数字应与数据库一致

3. **文案配图生成 5 张**:
   - 如果一次生成 5 张图片
   - ✅ 统计应增加 5 次（因为调用了 5 次 API）

## 样式说明

### IP形象生成器统计卡片

- **颜色主题**: 蓝色-紫色渐变
  - 背景: `from-blue-50 to-purple-50`
  - 边框: `border-blue-200`
  - 数字颜色: `text-blue-600`

### 文案配图生成器统计卡片

- **颜色主题**: 绿色-蓝色渐变
  - 背景: `from-green-50 to-blue-50`
  - 边框: `border-green-200`
  - 数字颜色: `text-green-600`

### 字体大小

- **大标题**: `text-3xl` (30px)
- **小标题**: `text-sm` (14px)
- **超小文字**: `text-xs` (12px)
- **移动端数字**: `text-xl` (20px)

## 调试技巧

### 1. 检查 API 请求

打开浏览器开发者工具（F12），切换到 Network 标签：

```
GET /api/gemini/usage-stats?type=ip_image
Status: 200 OK

Response:
{
  "status": "success",
  "data": {
    "total_count": 15,
    "success_count": 14,
    "failed_count": 1,
    "by_type": {
      "ip_image_count": 15,
      "content_image_count": 0
    }
  }
}
```

### 2. 检查 Console 日志

如果统计加载失败，会在 Console 看到：
```
获取使用统计失败: Error: ...
```

### 3. 检查 React State

使用 React DevTools 查看组件状态：
- `usageStats`: 应包含统计数据
- `isLoadingStats`: 加载完成后应为 `false`

### 4. 手动触发刷新

在浏览器 Console 中运行：
```javascript
// 获取 token
const token = localStorage.getItem('access_token');

// 手动调用 API
fetch('https://yourdomain.com/api/gemini/usage-stats?type=ip_image', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(r => r.json())
.then(data => console.log('统计数据:', data));
```

## 常见问题

### Q1: 统计卡片不显示？

**检查**:
1. 打开浏览器 Console，查看是否有错误
2. 检查 Network 标签，确认 API 请求成功
3. 确认用户已登录（有 access_token）

**解决**:
```bash
# 检查 Django 日志
tail -f /var/www/harry-insurance2/logs/django.log | grep "usage-stats"
```

### Q2: 统计数字不更新？

**检查**:
1. 确认生成操作确实成功
2. 检查 Network 标签，看是否调用了刷新统计的 API
3. 刷新页面，看是否显示最新数据

**解决**:
- 如果生成成功但统计未更新，检查代码中 `fetchUsageStats()` 是否被调用

### Q3: 数字与实际不符？

**验证**:
```bash
python manage.py shell -c "
from api.models import GeminiUsage
from django.contrib.auth.models import User

user = User.objects.get(username='your_username')
print('IP形象:', GeminiUsage.objects.filter(user=user, generation_type='ip_image').count())
print('文案配图:', GeminiUsage.objects.filter(user=user, generation_type='content_image').count())
"
```

### Q4: 移动端样式问题？

**测试**:
- 使用真实移动设备
- 或使用 Chrome DevTools 的设备模拟器
- 确保窗口宽度 < 768px 时切换到移动端样式

## 性能优化

### 缓存策略

目前统计数据：
- ✅ 页面加载时获取一次
- ✅ 生成成功后刷新一次
- ❌ 不使用轮询（避免频繁请求）

### 未来改进

1. **添加加载骨架屏**:
   ```jsx
   {isLoadingStats && (
     <div className="animate-pulse bg-gray-200 rounded-xl h-20 w-32"></div>
   )}
   ```

2. **添加过渡动画**:
   ```jsx
   <p className="transition-all duration-300">
     {usageStats.by_type.ip_image_count}
   </p>
   ```

3. **添加趋势图**:
   - 显示最近 7 天的使用趋势
   - 使用 Chart.js 或 Recharts

## 总结

✅ **已完成功能**:
- IP形象生成器页面统计显示
- 文案配图生成器页面统计显示
- 响应式设计（桌面/移动）
- 实时更新（生成后自动刷新）
- 优雅降级（API 失败不影响使用）

✅ **用户体验**:
- 清晰展示使用情况
- 实时反馈操作结果
- 不干扰主要功能
- 视觉效果美观

✅ **技术实现**:
- React Hooks 管理状态
- RESTful API 获取数据
- Tailwind CSS 响应式样式
- 错误处理和日志记录

---

**开发者**: Claude
**最后更新**: 2025-01-23
**相关文件**:
- `frontend/src/components/IPImageGenerator.jsx`
- `frontend/src/components/ContentImageGenerator.jsx`
- `api/ip_image_views.py` (get_gemini_usage_stats)
- `GEMINI_USAGE_STATS.md` (后端 API 文档)
