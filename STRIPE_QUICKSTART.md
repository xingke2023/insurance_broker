# Stripe会员订阅 - 快速入门

## ✅ 已完成的工作

1. **数据库更新** ✅
   - Membership表添加：stripe_customer_id, stripe_subscription_id
   - PaymentOrder表添加：payment_method, stripe_payment_intent_id, stripe_session_id
   - 新增会员类型：Solo计划(¥180/月), Team计划(¥90/月/人，5人起)

2. **后端集成** ✅
   - 安装stripe库
   - 创建`api/stripe_views.py`（支付会话、webhook处理）
   - 添加API路由：`/api/stripe/create-checkout-session`, `/api/stripe/webhook`
   - 数据库迁移已执行

3. **前端集成** ✅
   - 安装@stripe/stripe-js
   - 创建会员计划页面（`/membership-plans`）
   - Dashboard添加"会员计划"按钮
   - Team计划支持自定义人数（5人起）

4. **环境配置** ✅
   - 后端`.env`已添加Stripe配置项
   - 前端`frontend/.env`已创建
   - Django服务已重启

## 🔧 下一步：配置Stripe密钥

### 1. 获取Stripe API密钥

访问 [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)

- **Publishable key** (pk_test_...)：前端使用
- **Secret key** (sk_test_...)：后端使用

### 2. 更新环境变量

**后端** (`/var/www/harry-insurance2/.env`):
```bash
STRIPE_SECRET_KEY=sk_test_你的密钥
STRIPE_PUBLISHABLE_KEY=pk_test_你的密钥
```

**前端** (`/var/www/harry-insurance2/frontend/.env`):
```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_你的密钥
```

### 3. 配置Stripe Webhook

1. 访问 [Stripe Webhooks](https://dashboard.stripe.com/test/webhooks)
2. 点击 "Add endpoint"
3. 填写URL: `https://hongkong.xingke888.com/api/stripe/webhook`
4. 选择事件: `checkout.session.completed`
5. 复制**Signing secret** (whsec_...) 到后端`.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_你的密钥
   ```

### 4. 重启服务

```bash
# 重启Django加载新配置
sudo supervisorctl restart harry-insurance:harry-insurance-django

# 前端会自动热重载（Vite开发服务器）
```

## 🧪 测试流程

### 测试卡号（Stripe提供）
- **支付成功**: 4242 4242 4242 4242
- **需要3D验证**: 4000 0025 0000 3155
- **支付失败**: 4000 0000 0000 9995

其他信息随意填写：
- 过期日期：任何未来日期（如 12/34）
- CVC：任意3位数（如 123）
- 邮编：任意数字（如 12345）

### 测试步骤

1. **访问会员计划页面**
   - 登录后访问 Dashboard
   - 点击"会员计划"按钮
   - 或直接访问 `/membership-plans`

2. **选择计划**
   - Solo计划：¥180/月，个人订阅
   - Team计划：¥90/月/人，5人起订

3. **支付流程**
   - 点击"立即订阅"
   - 跳转到Stripe结账页面
   - 使用测试卡号完成支付

4. **验证结果**
   - 支付成功后跳转回会员计划页面
   - 查看数据库`memberships`表，确认会员记录
   - 检查`end_date`字段是否设置为下个月

## 📊 数据库检查

```sql
-- 查看会员记录
SELECT * FROM memberships ORDER BY created_at DESC LIMIT 5;

-- 查看订单记录
SELECT * FROM payment_orders WHERE payment_method='stripe' ORDER BY created_at DESC LIMIT 5;
```

## 🔍 故障排查

### 问题1：支付跳转失败
**解决方案**：
- 检查前端`.env`的`VITE_STRIPE_PUBLISHABLE_KEY`
- 打开浏览器Console查看错误
- 确认@stripe/stripe-js已安装

### 问题2：Webhook未收到
**解决方案**：
- 确认webhook URL可公网访问
- 检查Stripe Dashboard的webhook日志
- 验证`STRIPE_WEBHOOK_SECRET`正确

### 问题3：会员未激活
**解决方案**：
```bash
# 查看Django日志
tail -f /var/www/harry-insurance2/logs/django.log

# 检查订单状态
mysql -u root -p insurancetools -e "SELECT * FROM payment_orders WHERE order_no='订单号';"

# 检查会员状态
mysql -u root -p insurancetools -e "SELECT * FROM memberships WHERE user_id=用户ID;"
```

## 📁 相关文件

- **后端**
  - `api/models.py` - 数据模型
  - `api/stripe_views.py` - 支付逻辑
  - `api/urls.py` - 路由配置
  - `.env` - 环境变量

- **前端**
  - `frontend/src/components/MembershipPlans.jsx` - 会员计划页面
  - `frontend/src/components/Dashboard.jsx` - Dashboard
  - `frontend/.env` - 前端环境变量

- **文档**
  - `STRIPE_SETUP.md` - 详细设置指南
  - `STRIPE_QUICKSTART.md` - 快速入门（本文件）

## 🚀 生产环境部署

1. 切换到live密钥（去掉`_test`）
2. 更新webhook URL为生产域名
3. 设置`DEBUG=False`
4. 配置HTTPS
5. 备份数据库

## 💡 功能特性

✅ Solo计划：个人订阅，¥180/月
✅ Team计划：团队订阅，¥90/月/人（5人起）
✅ 自动创建/延长会员
✅ 到期时间设置为下个月
✅ 支持网站用户和小程序用户
✅ Webhook自动处理支付回调
✅ 美观的支付页面和确认提示

## 📞 需要帮助？

如有问题，请联系：
- 电话：852 62645180
- 邮箱：client@xingke888.com
