# Gemini API 调用统计功能

## 功能概述

系统现已实现统一的 Gemini API 调用统计功能，可以追踪所有通过 Gemini API 生成图片的操作，包括：
- **IP形象生成** (ip-image-generator)
- **文案配图生成** (content-image-generator)

## 数据模型

### GeminiUsage 模型

位置：`api/models.py`

```python
class GeminiUsage(models.Model):
    user = models.ForeignKey(User)           # 调用用户
    generation_type = models.CharField()      # 生成类型: 'ip_image' 或 'content_image'
    prompt = models.TextField()               # 使用的提示语
    success = models.BooleanField()           # 是否成功
    error_message = models.TextField()        # 错误信息（如果失败）
    created_at = models.DateTimeField()       # 调用时间
```

**数据库表名**: `gemini_usages`

## API 端点

### 获取 Gemini 调用统计

**端点**: `GET /api/gemini/usage-stats`

**需要认证**: 是（Bearer Token）

**查询参数**:
- `period`: 统计周期（可选）
  - `today` - 今天
  - `week` - 最近7天
  - `month` - 最近30天
  - `all` - 全部（默认）
- `type`: 生成类型过滤（可选）
  - `ip_image` - 仅IP形象生成
  - `content_image` - 仅文案配图生成
  - `all` - 全部类型（默认）

**请求示例**:
```bash
# 获取全部统计
curl -X GET "https://yourdomain.com/api/gemini/usage-stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取今天的IP形象生成统计
curl -X GET "https://yourdomain.com/api/gemini/usage-stats?period=today&type=ip_image" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取最近7天的所有调用统计
curl -X GET "https://yourdomain.com/api/gemini/usage-stats?period=week" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "period": "all",
    "total_count": 45,
    "success_count": 42,
    "failed_count": 3,
    "success_rate": 93.33,
    "by_type": {
      "ip_image_count": 15,
      "content_image_count": 30
    },
    "recent_usage": [
      {
        "id": 45,
        "generation_type": "content_image",
        "prompt": "春天的花园，阳光明媚",
        "success": true,
        "error_message": "",
        "created_at": "2025-01-23T10:30:00Z"
      },
      {
        "id": 44,
        "generation_type": "ip_image",
        "prompt": "专业的商务风格，简约大气",
        "success": true,
        "error_message": "",
        "created_at": "2025-01-23T09:15:00Z"
      }
    ]
  }
}
```

**响应字段说明**:
- `total_count`: 总调用次数
- `success_count`: 成功次数
- `failed_count`: 失败次数
- `success_rate`: 成功率（百分比）
- `by_type.ip_image_count`: IP形象生成次数
- `by_type.content_image_count`: 文案配图生成次数
- `recent_usage`: 最近10条调用记录（按时间倒序）

## 自动记录机制

### IP形象生成

当用户调用 `/api/ip-image/generate` 时：
- ✅ 成功：创建成功记录，包含提示语
- ❌ 失败：创建失败记录，包含错误信息

### 文案配图生成

当用户调用 `/api/content-image/generate` 时：
- ✅ 成功：创建成功记录，包含文案内容（前500字符）
- ❌ 失败：创建失败记录，包含错误信息

**注意**: 每次调用 API 都会自动记录，无需手动操作。

## 使用场景

### 1. 用户个人统计

用户可以查看自己的使用情况：
```bash
GET /api/gemini/usage-stats
```

### 2. 今日使用量查询

查看用户今天使用了多少次：
```bash
GET /api/gemini/usage-stats?period=today
```

### 3. 按类型统计

只查看IP形象生成次数：
```bash
GET /api/gemini/usage-stats?type=ip_image
```

只查看文案配图生成次数：
```bash
GET /api/gemini/usage-stats?type=content_image
```

### 4. 最近使用记录

返回数据中的 `recent_usage` 字段包含最近10条记录，可用于：
- 显示使用历史
- 查看失败原因
- 审计用户行为

## 数据库索引

为了提高查询性能，已创建以下索引：
- `(user, generation_type, created_at)` - 复合索引
- `(user, created_at)` - 复合索引
- `created_at` - 单字段索引

## 管理员功能（可扩展）

管理员可以通过 Django Admin 查看：
1. 所有用户的调用统计
2. 系统级别的调用总量
3. 失败率分析
4. 用户使用趋势

访问：`https://yourdomain.com/admin/api/geminiusage/`

## 实现细节

### 记录时机

**IP形象生成** (`api/ip_image_views.py:92-141`):
```python
# 成功时记录
GeminiUsage.objects.create(
    user=request.user,
    generation_type='ip_image',
    prompt=prompt,
    success=True
)

# 失败时记录
GeminiUsage.objects.create(
    user=request.user,
    generation_type='ip_image',
    prompt=prompt,
    success=False,
    error_message=str(e)
)
```

**文案配图生成** (`api/ip_image_views.py:389-446`):
```python
# 成功时记录
GeminiUsage.objects.create(
    user=request.user,
    generation_type='content_image',
    prompt=content[:500],  # 只存储前500字符
    success=True
)

# 失败时记录
GeminiUsage.objects.create(
    user=request.user,
    generation_type='content_image',
    prompt=content[:500],
    success=False,
    error_message=str(e)
)
```

## 迁移历史

- **迁移文件**: `api/migrations/0020_geminiusage.py`
- **应用时间**: 2025-01-23
- **数据库变更**: 新增 `gemini_usages` 表

## 后续扩展建议

### 1. 限额管理

可以基于统计数据实现使用限额：
```python
# 示例：检查每日限额
daily_count = GeminiUsage.objects.filter(
    user=request.user,
    created_at__date=timezone.now().date()
).count()

if daily_count >= 100:  # 每日限制100次
    return Response({'message': '今日调用次数已达上限'})
```

### 2. 成本追踪

为每条记录添加成本字段：
```python
cost = models.DecimalField()  # 单次调用成本
```

### 3. 全局统计 API

创建管理员专用的全局统计端点：
```python
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_global_gemini_stats(request):
    # 返回系统级别的统计数据
    pass
```

### 4. 数据导出

提供 CSV/Excel 导出功能：
```python
@api_view(['GET'])
def export_usage_stats(request):
    # 导出用户的使用记录
    pass
```

## 测试

### 手动测试步骤

1. **生成IP形象**：
   ```bash
   POST /api/ip-image/generate
   # 上传照片和提示语
   ```

2. **生成文案配图**：
   ```bash
   POST /api/content-image/generate
   # 提交文案内容
   ```

3. **查看统计**：
   ```bash
   GET /api/gemini/usage-stats
   ```

4. **验证记录**：
   - 检查 `total_count` 是否增加
   - 检查 `recent_usage` 是否包含新记录
   - 检查 `by_type` 中的分类统计

### 数据库验证

```bash
python manage.py shell
```

```python
from api.models import GeminiUsage
from django.contrib.auth.models import User

# 查看某用户的统计
user = User.objects.get(username='your_username')
stats = GeminiUsage.objects.filter(user=user)
print(f"总调用次数: {stats.count()}")
print(f"成功次数: {stats.filter(success=True).count()}")
print(f"IP形象生成: {stats.filter(generation_type='ip_image').count()}")
print(f"文案配图生成: {stats.filter(generation_type='content_image').count()}")
```

## 故障排查

### 问题1: 统计不准确

**检查**:
```bash
python manage.py shell -c "
from api.models import GeminiUsage
print('记录总数:', GeminiUsage.objects.count())
print('成功记录:', GeminiUsage.objects.filter(success=True).count())
print('失败记录:', GeminiUsage.objects.filter(success=False).count())
"
```

### 问题2: API返回错误

**查看日志**:
```bash
tail -f /var/www/harry-insurance2/logs/django.log | grep "Gemini"
```

### 问题3: 迁移未应用

**检查迁移状态**:
```bash
python manage.py showmigrations api
```

**重新应用**:
```bash
python manage.py migrate api
```

## 安全考虑

1. **认证要求**: 所有统计 API 都需要用户认证
2. **数据隔离**: 用户只能查看自己的统计数据
3. **敏感信息**: prompt 字段可能包含敏感内容，仅用户本人可见
4. **限额保护**: 建议实现每日/每月调用限额，防止滥用

## 总结

Gemini API 调用统计功能已完全实现并投入使用：

✅ 统一的数据模型（GeminiUsage）
✅ 自动记录所有调用（成功和失败）
✅ 灵活的查询 API（按时间、类型过滤）
✅ 详细的统计信息（总数、成功率、分类统计）
✅ 数据库索引优化
✅ 完整的错误处理和日志记录

用户现在可以实时追踪自己对 `ip-image-generator` 和 `content-image-generator` 的使用情况！

---

**开发者**: Claude
**最后更新**: 2025-01-23
**相关文件**:
- `api/models.py` (GeminiUsage 模型)
- `api/ip_image_views.py` (记录逻辑 + 统计 API)
- `api/urls.py` (路由配置)
- `api/migrations/0020_geminiusage.py` (数据库迁移)
