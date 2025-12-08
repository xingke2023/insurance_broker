# Bearer Token 调试指南

## 🔍 问题：Bearer Token被截断

如果您发现Bearer Token在发送时只有部分内容，请按以下步骤排查。

---

## 📋 检查清单

### 1️⃣ 检查输入框中的Token长度

**输入Token后，立即查看：**
- ✅ 输入框右上角显示的字符数
- ✅ 输入框下方的提示（是否显示红色警告）

**标准长度参考：**
- 短Token（如内部测试）：100-300 字符
- 标准JWT Token：200-500 字符
- 长Token（如您提到的）：1000-1200 字符

**如果显示的长度不对**：
- 检查是否完整复制了Token
- 检查是否有多余的空格或换行
- 尝试在文本编辑器中查看Token长度

---

### 2️⃣ 检查HTTP Headers显示区域

**橙色卡片会显示：**
```
📏 Authorization Header 长度: 1062 个字符
```

**如果长度不是1062：**
- 🔴 小于200：肯定被截断了
- 🟡 200-1000：可能被截断了
- 🟢 1000-1100：长度正常

---

### 3️⃣ 打开浏览器Console查看详细日志

**步骤：**
1. 按 `F12` 打开开发者工具
2. 切换到 `Console` 标签
3. 输入Bearer Token
4. 点击"开始执行"按钮

**查看日志输出：**
```
📝 Bearer Token输入变化:
  当前长度: 1055
  前50字符: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl...
  后50字符: ...EkhFjvog

🔑 Bearer Token详细信息:
  原始输入长度: 1055
  Trim后长度: 1055
  处理后长度: 1062
  包含Bearer前缀: false
  前50个字符: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
  中间50个字符: ...中间部分...
  后50个字符: ...EkhFjvog
  完整Token: Bearer eyJhbGci...完整内容...

📨 实际发送的Headers:
  Authorization字段长度: 1062
```

**重点检查：**
- "原始输入长度" 是否等于您复制的Token长度
- "处理后长度" 是否等于 1062
- "完整Token" 是否包含开头、中间、结尾的内容

---

### 4️⃣ 使用浏览器Network面板验证

**步骤：**
1. 按 `F12` 打开开发者工具
2. 切换到 `Network` 标签
3. 点击"开始执行"按钮
4. 在Network列表中找到对应的请求（通常是最新的一条）
5. 点击请求，查看 `Headers` 标签
6. 找到 `Request Headers` 部分
7. 查看 `Authorization` 字段

**应该看到：**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...完整token...
```

**检查：**
- Authorization字段是否存在
- 值是否以 "Bearer " 开头
- 完整长度是否正确

---

## 🐛 常见问题

### Q1: 输入框中的Token看起来完整，但发送时被截断

**可能原因：**
- ❌ textarea有maxLength限制（已设置为5000，应该足够）
- ❌ 浏览器对input值有限制
- ❌ axios截断了header值

**解决方案：**
1. 查看Console日志中的"完整Token"
2. 如果完整Token确实被截断，请联系开发者

---

### Q2: 我输入了1055个字符，为什么变成1062？

**正常现象！**
- 您输入的1055字符是Token本身
- 系统自动添加 "Bearer " 前缀（7个字符）
- 1055 + 7 = 1062 ✅

---

### Q3: Console显示完整，但API返回401

**可能原因：**
1. Token确实被截断（虽然Console显示完整）
2. Token已过期
3. Token权限不足
4. Token格式不正确

**排查步骤：**
1. 在Postman中测试相同的Token
2. 检查Token的过期时间（JWT可以在 jwt.io 解码查看）
3. 确认Token是从正确的来源获取的

---

### Q4: 如何确认Token是否真的被发送了？

**使用Network面板：**
1. F12 → Network
2. 发起请求
3. 点击请求查看Request Headers
4. 手动数一下Authorization字段的字符数

**或者使用代理工具：**
- Charles Proxy
- Fiddler
- Wireshark

---

## 🔧 临时解决方案

### 方案1：分段输入测试

在输入框中分段输入，每次输入200字符后查看长度：
```
输入前200字符 → 查看长度：200
再输入200字符 → 查看长度：400
...
```

如果某个阶段长度不增加，说明达到了限制。

---

### 方案2：使用文件上传

如果Token非常长，可以：
1. 将Token保存到文件
2. 使用文件读取方式加载
3. 避免手动复制粘贴导致的问题

---

### 方案3：联系API提供方

如果Token长度超过1500字符：
- 这可能不是标准的JWT Token
- 联系AXA API提供方确认Token格式
- 可能需要使用其他认证方式

---

## 📊 标准JWT Token结构

一个标准的JWT Token由三部分组成（用`.`分隔）：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9          ← Header (约30-50字符)
.
eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhw...       ← Payload (约100-1000字符)
.
UoYA2HUqAbUQbI9p0dcvpo0YSi-ut2YaFE7EkhFjvog   ← Signature (约40-50字符)
```

**如果您的Token缺少最后一部分（Signature），那就是被截断了！**

---

## 🎯 最终确认方法

**在Console中复制完整Token进行测试：**

```javascript
// 1. 打开Console
// 2. 在"开始执行"后，找到日志中的"完整Token"
// 3. 复制这个值
// 4. 在Console中输入：
console.log('Token长度:', '你复制的完整Token'.length)
console.log('Token内容:', '你复制的完整Token')

// 5. 手动验证字符数
```

---

## 📞 仍然无法解决？

**请提供以下信息：**
1. Console中的完整日志截图
2. Network面板的Request Headers截图
3. 输入框显示的字符数
4. Token的实际长度（在文本编辑器中查看）

**联系开发者，我们会尽快协助解决！**
