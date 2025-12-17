# Stripe支付集成设置指南

## 已完成的修改

### 1. 数据库模型更新
- ✅ `Membership`模型添加了Stripe字段：
  - `stripe_customer_id`: Stripe客户ID
  - `stripe_subscription_id`: Stripe订阅ID
  - 新增会员类型：`solo`（Solo计划）和`team`（Team计划）

- ✅ `PaymentOrder`模型添加了Stripe字段：
  - `payment_method`: 支付方式（微信/Stripe）
  - `stripe_payment_intent_id`: Stripe支付意图ID
  - `stripe_session_id`: Stripe会话ID
  - 新增套餐类型：`solo`和`team`

### 2. 后端API
- ✅ 创建了`api/stripe_views.py`，包含：
  - `create_checkout_session`: 创建Stripe结账会话
  - `stripe_webhook`: 处理Stripe webhook事件
  - `check_membership_status`: 检查会员状态

- ✅ 路由配置（`api/urls.py`）：
  - `/api/stripe/create-checkout-session` - 创建支付会话
  - `/api/stripe/webhook` - Stripe webhook回调
  - `/api/membership/check` - 检查会员状态

### 3. 前端组件
- ✅ 更新了`MembershipPlans.jsx`：
  - 集成Stripe支付
  - 添加Team人数选择模态框
  - 支付成功/取消后的提示

- ✅ 路由配置（`App.jsx`）：
  - `/membership-plans` - 会员计划页面

- ✅ Dashboard添加了"会员计划"按钮

## 需要执行的步骤

### 1. 安装依赖

#### 后端Python依赖
```bash
pip install stripe
```

#### 前端npm依赖
```bash
cd frontend
npm install @stripe/stripe-js
```

### 2. 配置环境变量

在`.env`文件中添加以下配置：

```bash
# Stripe配置
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

在`frontend/.env`或`frontend/.env.local`中添加：

```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

### 3. 数据库迁移

```bash
# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate
```

### 4. 配置Stripe Webhook

1. 登录[Stripe Dashboard](https://dashboard.stripe.com/)
2. 进入 **Developers → Webhooks**
3. 点击 **Add endpoint**
4. 输入Webhook URL：`https://your-domain.com/api/stripe/webhook`
5. 选择要监听的事件：
   - `checkout.session.completed`
6. 复制**Webhook签名密钥**到`.env`的`STRIPE_WEBHOOK_SECRET`

### 5. 获取Stripe API密钥

1. 登录[Stripe Dashboard](https://dashboard.stripe.com/)
2. 进入 **Developers → API keys**
3. 复制以下密钥：
   - **Publishable key** (pk_test_...) → 前端`.env`
   - **Secret key** (sk_test_...) → 后端`.env`

**注意**：测试环境使用`test`密钥，生产环境使用`live`密钥

### 6. 重启服务

```bash
# 重启Django
sudo supervisorctl restart harry-insurance:harry-insurance-django

# 重启前端（如果需要）
# Vite开发服务器会自动重载
```

### 7. 测试支付流程

#### 测试卡号（Stripe提供）：
- **成功**: 4242 4242 4242 4242
- **需要验证**: 4000 0025 0000 3155
- **失败**: 4000 0000 0000 9995

其他信息可以随意填写：
- **过期日期**: 任何未来日期（如：12/34）
- **CVC**: 任意3位数字（如：123）
- **邮编**: 任意数字（如：12345）

## 会员计划配置

### Solo计划
- 价格：¥180/月
- 单人订阅
- 自动续费

### Team计划
- 价格：¥90/人/月
- 最少5人订阅
- 统一付款

## Webhook处理逻辑

当用户完成支付后：
1. Stripe发送`checkout.session.completed`事件到webhook
2. 系统更新订单状态为`paid`
3. 创建或更新用户会员记录：
   - 新会员：设置开始时间和到期时间（下个月）
   - 现有会员：延长到期时间

## 数据库表结构

### memberships表
- `stripe_customer_id`: Stripe客户ID（新增）
- `stripe_subscription_id`: Stripe订阅ID（新增）
- `plan_type`: solo/team（新增类型）
- `end_date`: 到期时间（支付成功后设置为下个月）

### payment_orders表
- `payment_method`: wechat/stripe（新增）
- `stripe_payment_intent_id`: Stripe支付意图ID（新增）
- `stripe_session_id`: Stripe会话ID（新增）
- `plan_type`: solo/team（新增类型）

## 故障排查

### 1. 支付跳转失败
- 检查`VITE_STRIPE_PUBLISHABLE_KEY`是否正确配置
- 检查前端console是否有错误
- 确认@stripe/stripe-js已安装

### 2. Webhook未接收
- 确认webhook URL可公网访问
- 检查`STRIPE_WEBHOOK_SECRET`是否正确
- 查看Stripe Dashboard的webhook日志

### 3. 会员未激活
- 检查webhook是否成功处理
- 查看Django日志：`tail -f logs/django.log`
- 确认订单状态是否更新为`paid`

## 安全注意事项

1. **生产环境**：
   - 使用`live`密钥替换`test`密钥
   - 启用HTTPS
   - 设置正确的webhook签名验证

2. **密钥保护**：
   - 不要将密钥提交到版本控制
   - 使用环境变量管理敏感信息
   - 定期轮换密钥

3. **金额验证**：
   - 在服务器端验证支付金额
   - 不信任客户端传递的价格

## 相关文件清单

### 后端
- `api/models.py` - 数据模型（已更新）
- `api/stripe_views.py` - Stripe支付视图（新增）
- `api/urls.py` - 路由配置（已更新）
- `.env` - 环境变量（需要配置）

### 前端
- `frontend/src/components/MembershipPlans.jsx` - 会员计划页面（新增）
- `frontend/src/components/Dashboard.jsx` - Dashboard（已更新）
- `frontend/src/App.jsx` - 路由配置（已更新）
- `frontend/.env` - 前端环境变量（需要配置）

## 下一步

1. ✅ 安装Python和npm依赖
2. ✅ 配置环境变量
3. ✅ 执行数据库迁移
4. ✅ 配置Stripe webhook
5. ✅ 测试支付流程
6. 🔄 监控webhook日志
7. 🔄 在生产环境切换到live密钥
