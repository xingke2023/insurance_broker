# 多种支付方式支持指南

## 🎉 已支持的支付方式

系统现在支持以下支付方式：

### 1. 💳 信用卡/借记卡
- ✅ Visa
- ✅ Mastercard
- ✅ American Express
- ✅ 银联卡
- ✅ JCB
- ✅ Discover

### 2. 📱 Google Pay
- ✅ 自动检测支持的设备
- ✅ Android设备优先显示
- ✅ Chrome浏览器自动启用
- ✅ 快速一键支付

### 3. 💬 微信支付
- ✅ 扫码支付
- ✅ 网页版支持
- ✅ 移动端支持
- ✅ 中国大陆用户首选

### 4. 🅰️ 支付宝（额外赠送）
- ✅ 扫码支付
- ✅ 网页版支持
- ✅ 移动端支持
- ✅ 中国用户备选

---

## 🔧 Stripe账户配置

### 必须启用的支付方式

请登录 [Stripe Dashboard](https://dashboard.stripe.com/settings/payment_methods) 确保已启用：

#### 1. 信用卡/借记卡
**默认已启用** ✅

#### 2. Google Pay
**配置方式**：
- Google Pay会在用户使用支持的设备时**自动显示**
- 无需额外配置
- 条件：
  - ✅ 用户使用Chrome浏览器
  - ✅ 用户已在设备上设置Google Pay
  - ✅ 支付方式包含 `card`

#### 3. 微信支付（WeChat Pay）
**配置步骤**：
1. 访问：https://dashboard.stripe.com/settings/payment_methods
2. 找到 "WeChat Pay"
3. 点击 "Enable"（启用）
4. 确认服务条款
5. 等待Stripe审核（通常1-2个工作日）

**注意事项**：
- ⚠️ 需要Stripe审核通过
- ⚠️ 仅支持某些货币（HKD、CNY、USD等）
- ⚠️ 需要实名认证的Stripe账户

#### 4. 支付宝（Alipay）
**配置步骤**：
1. 访问：https://dashboard.stripe.com/settings/payment_methods
2. 找到 "Alipay"
3. 点击 "Enable"（启用）
4. 确认服务条款
5. 等待Stripe审核（通常1-2个工作日）

**注意事项**：
- ⚠️ 需要Stripe审核通过
- ⚠️ 支持多种货币
- ⚠️ 需要实名认证的Stripe账户

---

## 💻 代码实现

### 后端配置（已完成）✅

**文件**: `api/stripe_views.py`

```python
checkout_session = stripe.checkout.Session.create(
    payment_method_types=[
        'card',        # 信用卡/借记卡（包含Google Pay）
        'wechat_pay',  # 微信支付
        'alipay',      # 支付宝
    ],
    # ... 其他配置
    payment_method_options={
        'wechat_pay': {
            'client': 'web',  # 支持网页版微信支付
        },
    },
)
```

### 前端配置（无需修改）✅

前端使用 `window.location.href` 直接跳转到Stripe托管页面，Stripe会自动显示所有可用的支付方式。

---

## 🌍 支付方式显示规则

Stripe会根据以下条件**自动显示**合适的支付方式：

| 支付方式 | 显示条件 |
|---------|---------|
| 💳 信用卡 | 始终显示 |
| 📱 Google Pay | Chrome浏览器 + 已设置Google Pay |
| 💬 微信支付 | Stripe已启用 + 货币支持（HKD/CNY） |
| 🅰️ 支付宝 | Stripe已启用 + 货币支持 |

### 示例场景

#### 场景1: 中国用户，使用Chrome浏览器
显示的支付方式：
- ✅ 信用卡/借记卡
- ✅ Google Pay（如果已设置）
- ✅ 微信支付
- ✅ 支付宝

#### 场景2: 香港用户，使用Safari浏览器
显示的支付方式：
- ✅ 信用卡/借记卡
- ✅ 微信支付（如果启用）
- ✅ 支付宝（如果启用）

#### 场景3: 欧美用户，使用Chrome浏览器
显示的支付方式：
- ✅ 信用卡/借记卡
- ✅ Google Pay（如果已设置）

---

## 📱 支付流程

### 信用卡/借记卡支付
1. 用户选择会员计划
2. 跳转到Stripe支付页面
3. 选择"信用卡"或"借记卡"
4. 输入卡号、有效期、CVV
5. 点击"支付"
6. 支付成功，自动跳转回网站

### Google Pay支付
1. 用户选择会员计划
2. 跳转到Stripe支付页面
3. Stripe自动显示"Google Pay"按钮
4. 点击"Google Pay"
5. 选择已保存的卡片
6. 指纹/人脸识别确认
7. 支付成功，自动跳转回网站

### 微信支付流程
1. 用户选择会员计划
2. 跳转到Stripe支付页面
3. 选择"微信支付"
4. 显示二维码
5. 打开微信扫码
6. 在微信中确认支付
7. 支付成功，自动跳转回网站

### 支付宝支付流程
1. 用户选择会员计划
2. 跳转到Stripe支付页面
3. 选择"支付宝"
4. 跳转到支付宝页面或显示二维码
5. 在支付宝中确认支付
6. 支付成功，自动跳转回网站

---

## 🔍 检查配置状态

### 方法1: 测试支付页面
1. 访问会员计划页面
2. 点击"立即订阅"
3. 查看Stripe支付页面显示的支付方式
4. 如果看到微信支付/支付宝，说明配置成功

### 方法2: Stripe Dashboard
1. 访问：https://dashboard.stripe.com/settings/payment_methods
2. 查看各支付方式的状态：
   - ✅ **Enabled** = 已启用
   - ⏳ **Pending** = 审核中
   - ❌ **Disabled** = 未启用

---

## ⚠️ 注意事项

### 1. 货币限制
- 微信支付：支持 HKD、CNY、USD、EUR等
- 支付宝：支持大多数主要货币
- Google Pay：支持所有货币

### 2. 地区限制
- 微信支付：主要面向中国用户
- 支付宝：主要面向中国用户
- Google Pay：全球可用

### 3. 手续费
不同支付方式的Stripe手续费可能不同：
- 信用卡：通常 3.4% + HKD 2.35
- 微信支付：查看Stripe pricing页面
- 支付宝：查看Stripe pricing页面
- Google Pay：与信用卡相同

参考：https://stripe.com/hk/pricing

### 4. 审核要求
- **微信支付**：需要实名认证的Stripe账户
- **支付宝**：需要实名认证的Stripe账户
- 审核时间：1-2个工作日
- 可能需要提供：
  - 营业执照
  - 公司注册信息
  - 网站域名验证

---

## 🧪 测试

### 测试微信支付
1. 在Stripe Dashboard启用测试模式
2. 创建测试订单
3. 选择微信支付
4. 使用Stripe提供的测试二维码
5. 验证支付成功回调

### 测试支付宝
1. 在Stripe Dashboard启用测试模式
2. 创建测试订单
3. 选择支付宝
4. 使用Stripe提供的测试账号
5. 验证支付成功回调

### 测试Google Pay
需要：
- Chrome浏览器
- 已添加测试卡到Google Pay
- 使用测试模式的Stripe密钥

---

## 📊 支付方式对比

| 特性 | 信用卡 | Google Pay | 微信支付 | 支付宝 |
|-----|--------|-----------|---------|--------|
| 配置难度 | 简单 ⭐ | 简单 ⭐ | 中等 ⭐⭐ | 中等 ⭐⭐ |
| 审核要求 | 无 | 无 | 需要 | 需要 |
| 用户体验 | 好 👍 | 优秀 👍👍👍 | 优秀 👍👍👍 | 优秀 👍👍👍 |
| 覆盖人群 | 全球 🌍 | 全球 🌍 | 中国 🇨🇳 | 中国 🇨🇳 |
| 支付速度 | 快 ⚡ | 极快 ⚡⚡⚡ | 快 ⚡⚡ | 快 ⚡⚡ |

---

## 📞 获取帮助

### Stripe支持
- 文档：https://stripe.com/docs/payments/payment-methods
- 支持：https://support.stripe.com/

### 项目支持
- 电话：852 62645180
- 邮箱：client@xingke888.com

---

## ✅ 检查清单

启用微信支付和支付宝前，请确认：

- [ ] Stripe账户已完成实名认证
- [ ] 已访问 Payment Methods 设置页面
- [ ] 已启用微信支付（WeChat Pay）
- [ ] 已启用支付宝（Alipay）
- [ ] 等待审核通过（1-2个工作日）
- [ ] 在测试模式下测试支付流程
- [ ] 在生产环境测试真实支付

---

**更新时间**: 2025-12-13
**版本**: 1.0
**状态**: ✅ 代码已更新，等待Stripe审核
