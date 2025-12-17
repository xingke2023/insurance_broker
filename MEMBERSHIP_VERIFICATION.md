# 会员权限验证功能实现

## 📋 功能概述

当用户的会员资格过期或用户没有会员资格时，使用核心功能会收到提示，引导用户前往会员计划页面。

## 🔧 技术实现

### 后端实现

#### 1. 权限类 (`api/permissions.py`)

创建了两种会员权限验证机制：

##### `IsMemberActive` - DRF权限类
用于Django REST Framework的 `@permission_classes` 装饰器。

**特性**：
- 检查用户是否登录
- 检查用户是否有会员记录
- 检查会员是否在有效期内
- 返回详细的错误信息（包含错误类型、消息和跳转路径）

**错误响应格式**：
```json
{
  "error": "membership_expired" | "no_membership",
  "message": "您的会员已过期，请续费以继续使用",
  "redirect": "/membership-plans",
  "end_date": "2025-12-31T23:59:59Z"  // 仅在membership_expired时返回
}
```

##### `@require_active_membership` - 装饰器
用于视图函数的装饰器（备用方案）。

**使用场景**：当不使用 `@permission_classes` 时使用。

#### 2. 受保护的API端点

以下API端点已添加会员权限验证：

| API端点 | 功能 | 文件位置 |
|---------|------|---------|
| `POST /api/ocr/create-pending-document` | 创建待处理文档 | `api/ocr_views.py:1031` |
| `POST /api/ocr/upload-pdf-async` | 异步上传PDF | `api/ocr_views.py:1454` |
| `POST /api/ocr/chat/{document_id}` | 与文档对话 | `api/ocr_views.py:739` |
| `POST /api/poster/analyze` | 海报分析 | `api/poster_views.py:13` |

**实现方式**：
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMemberActive])
def protected_view(request):
    # 只有有效会员才能访问
    pass
```

### 前端实现

#### 1. 辅助工具 (`frontend/src/utils/membershipHelper.js`)

提供了多个辅助函数来处理会员权限错误：

##### `handleMembershipError(error, navigate)`
自动处理会员权限错误，显示确认对话框并导航到会员计划页面。

**使用示例**：
```javascript
try {
  await axios.post('/api/poster/analyze', formData);
} catch (error) {
  // 如果是会员权限错误，自动处理
  if (!handleMembershipError(error, onNavigate)) {
    // 如果不是会员错误，显示其他错误消息
    alert('操作失败，请重试');
  }
}
```

##### `isMembershipError(error)`
检查错误是否为会员权限错误。

##### `getMembershipErrorInfo(error)`
从错误对象中提取会员权限相关信息。

##### `showMembershipAlert(message, navigate)`
显示会员权限提示对话框。

#### 2. 已集成的组件

| 组件 | 功能 | 文件位置 |
|------|------|---------|
| `PosterAnalyzer` | 海报分析工具 | `frontend/src/components/PosterAnalyzer.jsx:129` |

**集成示例** (`PosterAnalyzer.jsx`):
```javascript
import { handleMembershipError } from '../utils/membershipHelper';

const handleAnalyzePoster = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/poster/analyze`, formData);
    // 处理成功响应
  } catch (error) {
    // 检查是否为会员权限错误
    if (!handleMembershipError(error, onNavigate)) {
      // 如果不是会员权限错误，显示普通错误消息
      alert(error.response?.data?.error || '分析失败，请重试');
    }
  }
};
```

## 📱 用户体验流程

### 场景1：会员已过期

1. 用户点击"分析海报"按钮
2. 前端发送请求到 `/api/poster/analyze`
3. 后端检测到会员已过期
4. 返回 `403 Forbidden` 错误：
   ```json
   {
     "error": "membership_expired",
     "message": "您的会员已过期，请续费以继续使用此功能",
     "redirect": "/membership-plans",
     "end_date": "2024-12-01T00:00:00Z"
   }
   ```
5. 前端显示确认对话框：
   ```
   您的会员已过期，请续费以继续使用此功能

   是否前往会员计划页面？
   [取消] [确定]
   ```
6. 用户点击"确定"后跳转到会员计划页面

### 场景2：没有会员资格

1. 用户点击"上传PDF"按钮
2. 前端发送请求到 `/api/ocr/upload-pdf-async`
3. 后端检测到用户没有会员记录
4. 返回 `403 Forbidden` 错误：
   ```json
   {
     "error": "no_membership",
     "message": "您还不是会员，请加入会员计划以使用此功能",
     "redirect": "/membership-plans"
   }
   ```
5. 前端显示确认对话框并引导用户注册会员

## 🧪 测试方法

### 测试会员过期场景

1. **创建测试会员**（在Django Admin或数据库中）：
   ```python
   from api.models import Membership
   from django.contrib.auth.models import User
   from django.utils import timezone
   from datetime import timedelta

   user = User.objects.get(username='testuser')
   Membership.objects.create(
       user=user,
       plan_type='solo',
       is_active=True,
       start_date=timezone.now() - timedelta(days=60),
       end_date=timezone.now() - timedelta(days=1)  # 昨天过期
   )
   ```

2. **测试API调用**：
   ```bash
   # 使用该用户的token调用受保护的API
   curl -X POST https://hongkong.xingke888.com/api/poster/analyze \
     -H "Authorization: Bearer <token>" \
     -F "image=@poster.jpg"

   # 预期返回403错误
   ```

3. **前端测试**：
   - 登录该测试用户
   - 尝试使用海报分析功能
   - 应该看到会员过期提示

### 测试无会员场景

1. **创建无会员的测试用户**：
   ```python
   # 只创建User，不创建Membership记录
   User.objects.create_user(
       username='nomember',
       password='test123'
   )
   ```

2. **测试流程同上**，预期返回 `no_membership` 错误

## 🔒 安全考虑

### 已实现的安全措施

1. **双重认证**：
   - 先验证用户是否登录 (`IsAuthenticated`)
   - 再验证会员资格 (`IsMemberActive`)

2. **清晰的错误信息**：
   - 不泄露敏感信息
   - 提供明确的操作指引

3. **服务器端验证**：
   - 所有权限检查在后端执行
   - 前端无法绕过权限检查

### 注意事项

- ⚠️ 前端的会员检查只是用户体验优化，**不应作为安全措施**
- ✅ 所有安全相关的验证都在后端完成
- ✅ Token验证和会员验证同时进行

## 📊 会员模型

### `Membership` 模型关键方法

```python
class Membership(models.Model):
    def is_valid(self):
        """检查会员是否有效"""
        from django.utils import timezone
        return self.is_active and self.end_date > timezone.now()

    def days_remaining(self):
        """剩余天数"""
        from django.utils import timezone
        if not self.is_valid():
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
```

### 数据库字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `user` | ForeignKey | 关联用户 |
| `plan_type` | CharField | 会员类型 (solo/team) |
| `is_active` | BooleanField | 是否激活 |
| `start_date` | DateTimeField | 开始时间 |
| `end_date` | DateTimeField | 到期时间 |
| `stripe_customer_id` | CharField | Stripe客户ID |
| `stripe_subscription_id` | CharField | Stripe订阅ID |

## 🚀 后续改进建议

### 1. 前端组件集成
建议在以下组件中也集成会员权限检查：
- `HomePage.jsx` - PDF上传按钮
- `PlanAnalyzer.jsx` - 计划书分析
- `PlanDocumentManagement.jsx` - 文档管理

### 2. 用户体验优化
- 在Dashboard显示会员到期倒计时
- 会员即将过期时提前7天提醒
- 提供"立即续费"快捷按钮

### 3. 宽限期功能
```python
def is_in_grace_period(self):
    """检查是否在宽限期内（过期后3天）"""
    if self.end_date >= timezone.now():
        return False
    days_expired = (timezone.now() - self.end_date).days
    return days_expired <= 3
```

### 4. 使用配额系统
对于非订阅制会员，可以使用 `UserQuota` 模型：
```python
from api.models import UserQuota

def check_and_consume_quota(user):
    """检查并消耗使用配额"""
    quota = UserQuota.objects.get(user=user)
    if quota.has_quota():
        quota.consume_quota()
        return True
    return False
```

## 📝 更新日志

**2025-12-13** - v1.0
- ✅ 创建会员权限验证系统
- ✅ 实现后端权限类和装饰器
- ✅ 添加4个受保护API端点
- ✅ 创建前端辅助工具
- ✅ 集成到海报分析功能
- ✅ 更新会员计划价格为美元

## 📞 支持

如有问题，请联系：
- 电话：852 62645180
- 邮箱：client@xingke888.com
